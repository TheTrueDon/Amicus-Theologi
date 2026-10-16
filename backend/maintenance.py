"""Local-only, user-owned database backups, staged recovery and first-run diagnostics.

No server/cloud uploads: exports are generated locally and downloaded by the browser.
Recovery takes effect on the *next app start* to avoid swapping an active SQLite DB.
"""
import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from .database import APP_VERSION, connect, data_dir

FORMAT = 'amicus-theologi-backup'
SCHEMA_VERSION = 1
DB_NAME = 'amicus_theologi.sqlite3'
PENDING = 'restore-pending.sqlite3'
MAX_DB_BYTES = 2_000_000_000
MAX_ZIP_BYTES = 750_000_000
NEEDED_TABLES = {'settings', 'modules', 'verses', 'tokens', 'lexicon_modules',
                 'lexicon_entries', 'study_projects', 'study_notes',
                 'study_highlights', 'textual_variants'}


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _checksum(path):
    sha = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def pending_restore():
    return (data_dir() / PENDING).exists()


def cancel_pending_restore():
    """Cancel a prepared recovery without touching the live database."""
    pending=data_dir() / PENDING
    if not pending.exists():
        return {'canceled': False, 'message':'Keine Wiederherstellung vorgemerkt.'}
    pending.unlink()
    return {'canceled': True, 'message':'Vorgemerkte Wiederherstellung verworfen. Die aktuellen Daten bleiben erhalten.'}


def _temp_db():
    fd, name = tempfile.mkstemp(prefix='amicus-backup-', suffix='.sqlite3', dir=data_dir())
    os.close(fd)
    return Path(name)


def _snapshot(destination):
    current = data_dir() / DB_NAME
    if not current.exists():
        raise ValueError('Es gibt noch keine lokale Datenbank.')
    source = sqlite3.connect(f'file:{current}?mode=ro', uri=True, timeout=30)
    dest = sqlite3.connect(destination)
    try:
        source.backup(dest, pages=256, sleep=0.05)
    finally:
        dest.close()
        source.close()
    return destination


def make_backup(destination=None):
    """Consistent point-in-time backup, compressed with provenance & SHA256."""
    temp = _temp_db()
    if destination is None:
        fd, output = tempfile.mkstemp(prefix='amicus-export-', suffix='.zip', dir=data_dir())
        os.close(fd)
        destination = Path(output)
    else:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        _snapshot(temp)
        manifest = {
            'format': FORMAT, 'schema_version': SCHEMA_VERSION,
            'created_at': utc_now(), 'application_version': APP_VERSION,
            'database_file': 'database.sqlite3', 'database_bytes': temp.stat().st_size,
            'sha256': _checksum(temp),
            'content': 'Bibeltexte, Wortannotationen, Lexika, Notizen, Projekte, Markierungen, Einstellungen',
        }
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, compresslevel=5) as z:
            z.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2))
            z.write(temp, 'database.sqlite3')
        return destination
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    finally:
        temp.unlink(missing_ok=True)


def _validate_db(path):
    if path.stat().st_size > MAX_DB_BYTES:
        raise ValueError('Datenbank ist größer als die zugelassene Sicherungsgröße.')
    # Read-only checking prevents a malformed backup from creating any schema.
    db = sqlite3.connect(f'file:{path}?mode=ro', uri=True)
    try:
        db.execute('PRAGMA trusted_schema=OFF')
        quick = db.execute('PRAGMA integrity_check(1)').fetchone()[0]
        if quick != 'ok':
            raise ValueError('Die Datenbankprüfung ist fehlgeschlagen: ' + str(quick))
        fk = db.execute('PRAGMA foreign_key_check').fetchone()
        if fk is not None:
            raise ValueError('Die Sicherung enthält fehlerhafte Datenbankverknüpfungen.')
        tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not NEEDED_TABLES.issubset(tables):
            raise ValueError('Die Sicherung enthält nicht alle benötigten Amicus-Tabellen.')
        # Protect FTS schema too; do not accept arbitrary SQLite file as project backup.
        if 'verse_fts' not in tables:
            raise ValueError('Der Volltextsuchindex fehlt in der Sicherung.')
    except sqlite3.DatabaseError as exc:
        raise ValueError('Die Sicherung ist keine gültige Amicus-Datenbank.') from exc
    finally:
        db.close()


def stage_restore(archive_path):
    """Verify archive contents and metadata, then stage for next app launch."""
    archive_path = Path(archive_path)
    if archive_path.stat().st_size > MAX_ZIP_BYTES:
        raise ValueError('Das Sicherungsarchiv ist zu groß (max. 750 MB).')
    candidate = _temp_db()
    try:
        try:
            with zipfile.ZipFile(archive_path) as z:
                if sorted(z.namelist()) != ['database.sqlite3', 'manifest.json']:
                    raise ValueError('Die Sicherung muss genau manifest.json und database.sqlite3 enthalten.')
                info = z.getinfo('database.sqlite3')
                meta_info = z.getinfo('manifest.json')
                if info.file_size < 1024 or info.file_size > MAX_DB_BYTES or meta_info.file_size > 16384:
                    raise ValueError('Die Sicherung hat eine ungültige Dateigröße.')
                if (info.flag_bits & 1) or (meta_info.flag_bits & 1):
                    raise ValueError('Verschlüsselte Sicherungen sind nicht unterstützt.')
                manifest = json.loads(z.read('manifest.json').decode('utf-8'))
                if not isinstance(manifest, dict) or manifest.get('format') != FORMAT or manifest.get('schema_version') != SCHEMA_VERSION:
                    raise ValueError('Keine unterstützte Amicus-Theologi-Sicherung.')
                if manifest.get('database_bytes') != info.file_size:
                    raise ValueError('Dateigröße und Sicherungsmanifest stimmen nicht überein.')
                with z.open(info) as source, open(candidate, 'wb') as out:
                    shutil.copyfileobj(source, out, 1024 * 1024)
                if _checksum(candidate) != manifest.get('sha256'):
                    raise ValueError('Die Sicherung ist beschädigt (Prüfsumme stimmt nicht).')
        except (zipfile.BadZipFile, zipfile.LargeZipFile, json.JSONDecodeError, UnicodeError) as exc:
            raise ValueError('Die gewählte Datei ist keine gültige Amicus-Sicherung.') from exc
        _validate_db(candidate)
        os.replace(candidate, data_dir() / PENDING)
        return {'restoration_prepared': True,
                'message': 'Sicherung geprüft. Amicus Theologi vollständig beenden und neu starten. Bis dahin sind Änderungen gesperrt.',
                'created_at': manifest.get('created_at'), 'application_version': manifest.get('application_version')}
    finally:
        candidate.unlink(missing_ok=True)


def apply_staged_restore():
    """Call BEFORE init_db, on application start only. Retain emergency pre-restore backup."""
    pending = data_dir() / PENDING
    if not pending.exists():
        return False
    _validate_db(pending)
    live = data_dir() / DB_NAME
    # Make a recoverable last-known-state file (no overwrite) before replacement.
    if live.exists():
        backups = data_dir() / 'backups'
        backups.mkdir(exist_ok=True)
        name = backups / ('vor-wiederherstellung-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.zip')
        make_backup(name)
    os.replace(pending, live)
    # Any stale WAL/SHM files from an old crash must not be replayed on restored DB.
    for extension in ('-wal', '-shm'):
        (data_dir() / (DB_NAME + extension)).unlink(missing_ok=True)
    return True


def automatic_upgrade_backup():
    """Save once on first 1.0 start for existing installs, before schema initialization."""
    dbpath = data_dir() / DB_NAME
    if not dbpath.exists() or dbpath.stat().st_size == 0:
        return False
    # Marked versions won't be snapshotted repeatedly. Older builds have no key.
    db = sqlite3.connect(f'file:{dbpath}?mode=ro', uri=True)
    try:
        version = db.execute("SELECT value FROM settings WHERE key='application_release_version'").fetchone()
    except sqlite3.DatabaseError:
        version = None
    finally:
        db.close()
    if version and version[0] == json.dumps(APP_VERSION):
        return False
    backups = data_dir() / 'backups'
    backups.mkdir(exist_ok=True)
    dest = backups / ('vor-update-1.0-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '.zip')
    make_backup(dest)
    return True


def record_release_version():
    with connect() as db:
        db.execute("INSERT INTO settings(key,value) VALUES ('application_release_version',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (json.dumps(APP_VERSION),))


def diagnostics():
    with connect() as db:
        integrity = db.execute('PRAGMA quick_check').fetchone()[0]
        foreign_keys = db.execute('PRAGMA foreign_key_check').fetchall()
        quantities = {}
        for key, table in [('bibeltexte', 'modules'), ('verse', 'verses'),
                           ('annotierte_woerter','tokens'), ('lexika','lexicon_modules'),
                           ('lexikoneintraege','lexicon_entries'), ('projekte','study_projects'),
                           ('notizen','study_notes'), ('markierungen','study_highlights'),
                           ('textvarianten','textual_variants')]:
            quantities[key] = db.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        modules = [dict(r) for r in db.execute('''SELECT m.id,m.title,m.language,m.license,m.provenance,
          COUNT(DISTINCT v.rowid) AS verse_count,
          (SELECT COUNT(*) FROM tokens t WHERE t.module_id=m.id) AS annotated_words,
          (SELECT COUNT(DISTINCT t.book || ':' || t.chapter || ':' || t.verse)
             FROM tokens t WHERE t.module_id=m.id) AS annotated_verses
          FROM modules m LEFT JOIN verses v ON v.module_id=m.id
          GROUP BY m.id ORDER BY m.title''')]
        for module in modules:
            total=module['verse_count']
            module['annotation_coverage_percent']=round(100*module['annotated_verses']/total,1) if total else 0.0
    return {'version': APP_VERSION, 'database_ok':integrity=='ok' and not foreign_keys,
            'database_message': integrity if not foreign_keys else 'Fehlerhafte Fremdschlüssel',
            'pending_restore': pending_restore(), 'counts': quantities, 'modules':modules,
            'storage':str(data_dir()), 'data_size_mb':round((data_dir() / DB_NAME).stat().st_size / (1024*1024), 2),
            'coverage_note':'Die Abdeckung zählt Verse mit importierten Wortannotationen. Sie belegt weder Vollständigkeit der Ausgabe noch Korrektheit der Annotationen.'}


def install_demo_bundle():
    """Install small offline examples only; never silently overwrite user's modules."""
    from .library import read_import, install_module
    from .morphology import parse_annotation_file, import_annotations
    from .lexicon import read_lexicon, install_lexicon
    examples = Path(__file__).resolve().parent.parent / 'modules' / 'examples'
    texts = [
        ('demo-jn-de', 'Johannes 1,1–5 · Deutsch (Demo)', 'de', 'johannes_demo_de.tsv'),
        ('demo-jn-la', 'Johannes 1,1–5 · Vulgata (Demo)', 'la', 'johannes_demo_la.tsv'),
        ('demo-jn-grc', 'Johannes 1,1 · Griechisch (Demo)', 'grc', 'johannes_1_1_grc.tsv'),
        ('demo-gen-he', 'Genesis 1,1 · Hebräisch (Demo)', 'he', 'genesis_1_1_he.tsv'),
    ]
    lexica = [
        ('demo-lexicon-grc', 'Griechisches Mini-Lexikon (Demo)', 'grc', 'demo_lexikon_grc.tsv'),
        ('demo-lexicon-he', 'Hebräisches Mini-Lexikon (Demo)', 'he', 'demo_lexikon_he.tsv'),
    ]
    present = set()
    with connect() as db:
        present = {r[0] for r in db.execute('SELECT id FROM modules')}
        existing_lex = {r[0] for r in db.execute('SELECT id FROM lexicon_modules')}
    installed = []
    for mid, title, lang, fname in texts:
        if mid not in present:
            install_module(mid, title, lang, 'Demonstrationsdaten – nicht für Zitate verwenden',
                           'Amicus Theologi / modules/examples', '1', read_import((examples/fname).read_bytes()))
            installed.append(mid)
    for mid, fname in [('demo-jn-grc','johannes_1_1_grc_morph.tsv'),
                       ('demo-gen-he','genesis_1_1_he_morph.tsv')]:
        with connect() as db:
            annotated = db.execute('SELECT COUNT(*) FROM tokens WHERE module_id=?', (mid,)).fetchone()[0]
        if not annotated:
            import_annotations(mid, parse_annotation_file((examples/fname).read_bytes()))
    for lid, title, lang, fname in lexica:
        if lid not in existing_lex:
            install_lexicon(lid, title, lang, 'Demo – selbst erstellte Kurzdefinitionen',
                            'Amicus Theologi / modules/examples', '1', read_lexicon((examples/fname).read_bytes()))
            installed.append(lid)
    return {'installed': installed, 'message': 'Demo-Daten bereit. Diese enthalten keine vollständige Bibelausgabe.'}
