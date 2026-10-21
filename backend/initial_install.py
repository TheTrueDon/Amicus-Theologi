"""One-click installation of all bundled and catalogued Amicus resources."""
from pathlib import Path
from threading import Lock, Thread
from uuid import uuid4
import json
import sys
import zipfile

from .database import connect
from .bible_catalog import bible_catalog, install_bible_from_catalog
from .catalog import catalog_list, install_catalog_item
from . import sources
from .source_packages import install_package

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
PACKAGE_DIR = ROOT / 'source_packages'
_LOCK = Lock()
_JOB = None


def _source_package_id(path):
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read('manifest.json').decode('utf-8-sig'))
    source = manifest.get('source') or {}
    module_id = source.get('id')
    title = source.get('title') or path.stem
    if not isinstance(module_id, str) or not module_id:
        raise ValueError('Quellenpaket hat keine gültige Modul-ID.')
    return module_id, title


def _installed_source_ids():
    with connect() as db:
        return {row[0] for row in db.execute('SELECT id FROM source_modules')}


def _fail(message):
    raise ValueError(message)


def _build_plan():
    tasks = []
    skipped = 0
    external = []
    seen = set()

    def add(module_id, title, installed, run):
        nonlocal skipped
        if module_id in seen:
            return
        seen.add(module_id)
        if installed:
            skipped += 1
        else:
            tasks.append({'id': module_id, 'title': title, 'run': run})

    # Install local resources first, so a missing network never delays the
    # bundled texts, translations, and annotations.
    package_paths = sorted(PACKAGE_DIR.glob('*.amicus-source')) if PACKAGE_DIR.is_dir() else []
    known_source_ids = _installed_source_ids()
    for path in package_paths:
        try:
            module_id, title = _source_package_id(path)
        except (OSError, ValueError, KeyError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
            key = 'bundled-package-' + path.stem[:32]
            add(key, path.name, False,
                lambda error=str(exc): _fail('Paketmanifest ungültig: ' + error))
            continue
        add(module_id, title, module_id in known_source_ids,
            lambda package_path=path: install_package(package_path.read_bytes()))
    if not package_paths:
        add('bundled-source-packages', 'Mitgelieferte Quellenpakete', False,
            lambda: _fail('Im Programmordner wurden keine .amicus-source-Pakete gefunden.'))

    # Biblical text editions shown under Bibelausgaben.
    for item in bible_catalog():
        add(item['module_id'], item['title'], item['installed'],
            lambda edition_id=item['id']: install_bible_from_catalog(edition_id))

    # Linguistic corpora and lexica from the main program's Textmodule catalog.
    for item in catalog_list():
        add(item['id'], item['title'], item['installed'],
            lambda item_id=item['id']: install_catalog_item(item_id))

    # All installable Sources catalog items. The delegated STEPBible lexica are
    # already covered above. External aids are links, not downloadable modules.
    for item in sources.catalog_list():
        if item.get('delegated'):
            continue
        if item.get('kind') == 'reference':
            external.append(item['title'])
            continue
        if item['kind'] == 'lexicon':
            with connect() as db:
                installed = db.execute('SELECT 1 FROM lexicon_modules WHERE id=?',
                                       (item['id'],)).fetchone() is not None
        else:
            installed = item['installed']
        add(item['id'], item['title'], installed,
            lambda item_id=item['id']: sources.install_catalog(item_id))

    return tasks, skipped, external


def _snapshot():
    with _LOCK:
        return dict(_JOB) if _JOB else None


def _run(job_id, tasks):
    global _JOB
    for task in tasks:
        with _LOCK:
            if not _JOB or _JOB['id'] != job_id:
                return
            _JOB['current_title'] = task['title']
            _JOB['phase'] = 'Quelle wird geladen, geprüft und installiert …'
        try:
            task['run']()
            with _LOCK:
                _JOB['installed'] += 1
        except Exception as exc:  # Continue so one upstream failure does not block the collection.
            with _LOCK:
                _JOB['errors'].append({'title': task['title'], 'message': str(exc)[:700]})
        finally:
            with _LOCK:
                if not _JOB or _JOB['id'] != job_id:
                    return
                _JOB['completed'] += 1
                _JOB['progress'] = int(100 * _JOB['completed'] / max(1, _JOB['total']))
                _JOB['current_title'] = ''
                _JOB['phase'] = 'Nächste Quelle wird vorbereitet …'
    with _LOCK:
        if _JOB and _JOB['id'] == job_id:
            _JOB['done'] = True
            _JOB['phase'] = ('Abgeschlossen – einzelne Quellen konnten nicht installiert werden.'
                             if _JOB['errors'] else 'Alle installierbaren Quellen sind bereit.')
            _JOB['progress'] = 100


def start_installation():
    """Start one background job, or return the already-running job."""
    global _JOB
    with _LOCK:
        if _JOB and not _JOB['done']:
            result = dict(_JOB)
            result['already_running'] = True
            return result
        tasks, skipped, external = _build_plan()
        job_id = str(uuid4())
        _JOB = {
            'id': job_id, 'done': not tasks,
            'phase': ('Alle installierbaren Quellen sind bereits vorhanden.' if not tasks
                      else 'Vorbereitung abgeschlossen.'),
            'current_title': '', 'completed': 0, 'total': len(tasks), 'progress': 100 if not tasks else 0,
            'installed': 0, 'skipped': skipped, 'errors': [],
            'external_count': len(external), 'external_titles': external,
            'already_running': False,
        }
    if tasks:
        with _LOCK:
            if _JOB and _JOB['id'] == job_id:
                _JOB['phase'] = 'Installation wird gestartet …'
        Thread(target=_run, args=(job_id, tasks), name='amicus-install-all', daemon=True).start()
    return _snapshot()


def installation_status(job_id):
    state = _snapshot()
    return state if state and state['id'] == job_id else None
