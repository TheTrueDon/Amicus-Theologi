"""Validated offline Bible edition bundles with word annotations.

The package is data-only: one text edition, optional parallel text, and
position-aligned annotations. ZIP members are never executed.
"""
import csv
import hashlib
import io
import json
import re
import zipfile

from .database import connect
from .library import read_import
from .morphology import parse_annotation_file, normalize_surface

FORMAT = 'amicus-bible-package'
MAX_BYTES = 80_000_000
MAX_UNPACKED = 120_000_000
MAX_MEMBERS = 20
ID = re.compile(r'[A-Za-z0-9_-]{2,48}\Z')


def _read(raw):
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError('Bibelpaket ist leer oder überschreitet 80 MB.')
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except (zipfile.BadZipFile, OSError) as exc:
        raise ValueError('Bibelpaket ist kein gültiges ZIP-Archiv.') from exc
    with archive:
        infos = archive.infolist()
        if len(infos) > MAX_MEMBERS or sum(i.file_size for i in infos) > MAX_UNPACKED:
            raise ValueError('Bibelpaket überschreitet die Archivgrenzen.')
        names = set()
        for info in infos:
            name = info.filename
            if (info.is_dir() or name.startswith(('/', '\\')) or '\\' in name or
                    any(part in ('', '.', '..') for part in name.split('/')) or
                    info.flag_bits & 1 or info.file_size > MAX_UNPACKED):
                raise ValueError('Unsicherer Dateieintrag im Bibelpaket.')
            if name in names:
                raise ValueError('Doppelte Dateinamen im Bibelpaket.')
            names.add(name)
        if 'manifest.json' not in names:
            raise ValueError('manifest.json fehlt im Bibelpaket.')
        files = {name: archive.read(name) for name in names}
    try:
        manifest = json.loads(files['manifest.json'].decode('utf-8-sig'))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError('manifest.json ist kein gültiges UTF-8-JSON.') from exc
    if manifest.get('format') != FORMAT or manifest.get('format_version') != 1:
        raise ValueError('Unbekanntes Bibelpaketformat.')
    return manifest, files


def package_info(path):
    """Read edition identifiers from a bundled package without importing it."""
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read('manifest.json').decode('utf-8-sig'))
    editions = manifest.get('editions')
    if not isinstance(editions, list) or not editions:
        raise ValueError('Bibelpaket enthält keine Editionen.')
    for edition in editions:
        if not isinstance(edition, dict) or not ID.fullmatch(edition.get('id', '')):
            raise ValueError('Bibelpaket enthält eine ungültige Modul-ID.')
    return editions


def inspect_bible_package(raw):
    manifest, files = _read(raw)
    editions = manifest.get('editions')
    if not isinstance(editions, list) or not 1 <= len(editions) <= 5:
        raise ValueError('Ein bis fünf Bibelausgaben sind erforderlich.')
    ids = set()
    for edition in editions:
        for field in ('id', 'title', 'language', 'license', 'provenance', 'version', 'text_file'):
            if not isinstance(edition.get(field), str) or not edition[field].strip() or len(edition[field]) > 250:
                raise ValueError(f'Bibelausgabe: {field} fehlt oder ist zu lang.')
        if not ID.fullmatch(edition['id']) or edition['id'] in ids:
            raise ValueError('Bibelpaket enthält eine ungültige oder doppelte Modul-ID.')
        if edition['language'] not in ('de', 'en', 'la', 'grc', 'he', 'other'):
            raise ValueError('Bibelpaket enthält eine unbekannte Sprache.')
        ids.add(edition['id'])
        if edition['text_file'] not in files:
            raise ValueError('Textdatei einer Bibelausgabe fehlt.')

    checksums = manifest.get('checksums')
    if not isinstance(checksums, dict):
        raise ValueError('Prüfsummen fehlen im Bibelpaket.')
    for name, expected in checksums.items():
        if name not in files or not isinstance(expected, str) or not expected.startswith('sha256:'):
            raise ValueError('Ungültiger Prüfsummeneintrag im Bibelpaket.')
        if hashlib.sha256(files[name]).hexdigest() != expected[7:]:
            raise ValueError(f'Paketdatei {name} stimmt nicht mit der SHA-256-Prüfsumme überein.')

    verse_sets = {}
    for edition in editions:
        verse_sets[edition['id']] = read_import(files[edition['text_file']])
    annotation_file = manifest.get('annotations_file')
    token_groups = {}
    if annotation_file:
        if annotation_file not in files:
            raise ValueError('Annotationsdatei fehlt.')
        for name in manifest.get('annotation_chunks', []):
            if name not in files:
                raise ValueError('Annotationsdatei fehlt.')
            groups = parse_annotation_file(files[name])
            overlap = token_groups.keys() & groups.keys()
            if overlap:
                raise ValueError(f'Doppelte Wortannotation für {next(iter(overlap))}.')
            token_groups.update(groups)
    if annotation_file:
        primary = editions[0]['id']
        text_map = {(b, c, v): text for b, c, v, text in verse_sets[primary]}
        if set(token_groups) != set(text_map):
            raise ValueError('Annotationen müssen jede Stelle der Hauptausgabe vollständig abdecken.')
        for key, words in token_groups.items():
            if normalize_surface(text_map[key]) != normalize_surface(''.join(word[1] for word in words)):
                raise ValueError(f'{key}: Wortfolge passt nicht zum Bibeltext.')
    return manifest, editions, verse_sets, token_groups


def install_bible_package(raw):
    manifest, editions, verse_sets, token_groups = inspect_bible_package(raw)
    with connect() as db:
        present = {row[0] for row in db.execute('SELECT id FROM modules')}
        duplicate = present.intersection(edition['id'] for edition in editions)
        if duplicate:
            if len(duplicate) == len(editions):
                return {'installed': 0, 'skipped': len(editions), 'modules': sorted(duplicate)}
            raise ValueError('Ein Teil des Pakets ist bereits installiert. Vor dem Import die doppelte Ausgabe entfernen.')
        for edition in editions:
            mid = edition['id']
            db.execute('INSERT INTO modules(id,title,language,kind,license,provenance,version) VALUES(?,?,?,?,?,?,?)',
                       (mid, edition['title'], edition['language'], 'bible', edition['license'],
                        edition['provenance'], edition['version']))
            db.executemany('INSERT INTO verses(module_id,book,chapter,verse,text) VALUES(?,?,?,?,?)',
                           [(mid, b, c, v, text) for b, c, v, text in verse_sets[mid]])
        primary_id = editions[0]['id']
        db.executemany('INSERT INTO tokens(module_id,book,chapter,verse,position,surface,lemma,morph,strong) VALUES(?,?,?,?,?,?,?,?,?)',
            [(primary_id, b, c, v, pos, surface, lemma, morph, strong or None)
             for (b, c, v), words in token_groups.items()
             for pos, surface, lemma, morph, strong in words])
    return {'installed': len(editions), 'skipped': 0,
            'modules': [edition['id'] for edition in editions],
            'verses': sum(len(verse_sets[e['id']]) for e in editions),
            'tokens': sum(map(len, token_groups.values()))}
