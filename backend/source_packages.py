"""Offline, self-describing Amicus source packages (ASPK v1).

Packages contain UTF-8 sections, optional position-aligned morphology, and one
or more explicitly attributed translations. No archive code is executed.
"""
import csv
import hashlib
import io
import json
import re
import zipfile

from .database import connect
from . import sources

MAX_PACKAGE = 145_000_000
MAX_UNPACKED = 280_000_000
MAX_MEMBERS = 8
PACKAGE_FORMAT = 'amicus-source-package'
TRANSLATION_ID = re.compile(r'[A-Za-z0-9_-]{2,48}\Z')
csv.field_size_limit(4_000_000)


def _required(obj, fields, label):
    if not isinstance(obj, dict):
        raise ValueError(f'{label}: Metadaten fehlen.')
    for field in fields:
        value = obj.get(field)
        if not isinstance(value, str) or not value.strip() or len(value) > 250:
            raise ValueError(f'{label}: {field} ist erforderlich (max. 250 Zeichen).')


def _csv_rows(raw, required, label, maximum=1_500_000):
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError(f'{label}: UTF-8 wird benötigt.') from exc
    delimiter = '\t' if text[:3000].count('\t') > text[:3000].count(',') else ','
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not set(required) <= set(reader.fieldnames or ()):
        raise ValueError(f'{label}: Benötigte Spalten: {", ".join(required)}.')
    rows = list(reader)
    if not rows or len(rows) > maximum:
        raise ValueError(f'{label}: Datei ist leer oder enthält zu viele Zeilen.')
    return rows


def _read_package(raw):
    if not raw or len(raw) > MAX_PACKAGE:
        raise ValueError('Quellenpaket maximal 145 MB.')
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except (zipfile.BadZipFile, OSError) as exc:
        raise ValueError('Datei ist kein gültiges Amicus-Quellenpaket (ZIP).') from exc
    with archive:
        infos = archive.infolist()
        if len(infos) > MAX_MEMBERS or sum(i.file_size for i in infos) > MAX_UNPACKED:
            raise ValueError('Quellenpaket überschreitet die sicheren Archivgrenzen.')
        names = set()
        for info in infos:
            name = info.filename
            if (info.is_dir() or name.startswith(('/', '\\')) or '\\' in name or
                    any(part in ('', '.', '..') for part in name.split('/')) or
                    info.flag_bits & 1 or info.file_size > MAX_UNPACKED):
                raise ValueError('Unsicherer oder nicht unterstützter Dateieintrag im Paket.')
            if name in names:
                raise ValueError('Doppelte Dateinamen im Paket.')
            names.add(name)
        if 'manifest.json' not in names:
            raise ValueError('manifest.json fehlt im Quellenpaket.')
        files = {name: archive.read(name) for name in names}
    try:
        manifest = json.loads(files['manifest.json'].decode('utf-8-sig'))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError('manifest.json ist kein gültiges UTF-8-JSON.') from exc
    if manifest.get('format') != PACKAGE_FORMAT or manifest.get('format_version') != 1:
        raise ValueError('Unbekanntes Quellenpaketformat; unterstützt wird ASPK v1.')
    return manifest, files


def inspect_package(raw):
    """Validate a package without changing the database; used by tests/tools."""
    manifest, files = _read_package(raw)
    source = manifest.get('source')
    _required(source, ('id','title','author','language','edition','license','provenance','version'), 'Quelle')
    if source['language'] not in sources.LANGUAGES:
        raise ValueError('Sprache muss la, grc oder he sein.')
    if not sources.IDENT.fullmatch(source['id']):
        raise ValueError('Ungültige Quellen-ID.')
    file_map = manifest.get('files')
    if not isinstance(file_map, dict) or not {'sections','translations'} <= set(file_map):
        raise ValueError('Paketdateien sections und translations sind erforderlich.')
    if set(file_map) - {'sections','annotations','translations'}:
        raise ValueError('Unbekannter Dateityp im Paketmanifest.')
    if any(not isinstance(name, str) or name not in files for name in file_map.values()):
        raise ValueError('Eine im Manifest genannte Datei fehlt im Paket.')
    checksums=manifest.get('checksums',{})
    expected_files=set(file_map.values())
    if not isinstance(checksums,dict) or not expected_files <= set(checksums):
        raise ValueError('Paketprüfsummen sind ungültig.')
    for name,digest in checksums.items():
        if name not in files or not isinstance(digest,str) or not digest.startswith('sha256:'):
            raise ValueError('Ungültige SHA-256-Prüfsumme im Paketmanifest.')
        if hashlib.sha256(files[name]).hexdigest()!=digest[7:]:
            raise ValueError(f'Paketdatei {name} stimmt nicht mit der SHA-256-Prüfsumme überein.')
    sections = sources.read_source(files[file_map['sections']])
    section_map = {ref: text for ref, _ordinal, text in sections}

    editions = manifest.get('translation_editions')
    if not isinstance(editions, list) or not editions or len(editions) > 20:
        raise ValueError('Mindestens eine Übersetzung mit Editionsmetadaten ist erforderlich.')
    edition_map = {}
    for edition in editions:
        _required(edition, ('id','language','title','author','edition','license','provenance'), 'Übersetzung')
        if not TRANSLATION_ID.fullmatch(edition['id']) or edition['id'] in edition_map:
            raise ValueError('Übersetzungs-IDs müssen eindeutig und gültig sein.')
        edition_map[edition['id']] = edition
    translations = _csv_rows(files[file_map['translations']], ('ref','translation_id','text'), 'Übersetzungen', 300_000)
    seen_translations = set()
    translation_data = []
    translation_documents = []
    for row in translations:
        ref, tid, text = tuple((row.get(k) or '').strip() for k in ('ref','translation_id','text'))
        if tid not in edition_map or not text:
            raise ValueError('Übersetzung verweist auf eine unbekannte Stelle/Ausgabe oder ist leer.')
        if ref == '@work':
            if len(text) > 3_000_000:
                raise ValueError('Gesamtübersetzung überschreitet 3 MB.')
            translation_documents.append((tid, text))
            continue
        if ref not in section_map or len(text) > 20_000:
            raise ValueError('Übersetzung verweist auf eine unbekannte Stelle/Ausgabe oder ist leer.')
        key = (ref, tid)
        if key in seen_translations:
            raise ValueError(f'Doppelte Übersetzung für {ref} ({tid}).')
        seen_translations.add(key)
        translation_data.append((ref, tid, text))

    annotations = {}
    if 'annotations' in file_map:
        annotation_meta=manifest.get('annotation_edition')
        _required(annotation_meta,('provider','method','coverage','license','provenance'),'Morphologie-Edition')
        rows = _csv_rows(files[file_map['annotations']], ('ref','position','surface','lemma','morph'), 'Wortanalysen', 1_500_000)
        grouped = {}
        for row in rows:
            ref = (row.get('ref') or '').strip()
            if ref not in section_map:
                raise ValueError('Wortanalyse verweist auf eine unbekannte Stelle.')
            try:
                position = int(row['position'])
            except (TypeError, ValueError) as exc:
                raise ValueError('Wortanalyse enthält eine ungültige Position.') from exc
            vals = tuple((row.get(key) or '').strip() for key in ('surface','lemma','morph','strong'))
            if position < 1 or not vals[0] or not vals[1] or any(len(v) > 200 for v in vals):
                raise ValueError('Wortanalyse enthält fehlende oder zu lange Werte.')
            grouped.setdefault(ref, []).append((position, *vals))
        for ref, entries in grouped.items():
            entries.sort(key=lambda item: item[0])
            expected = sources._word_rows(source['id'], ref, section_map[ref])
            if len(entries) != len(expected):
                raise ValueError(f'{ref}: Wortanalysen stimmen nicht vollständig mit dem Text überein.')
            if any(pos != token[2] or sources._normalize_word(surface) != sources._normalize_word(token[3])
                   for (pos,surface,*_),token in zip(entries,expected)):
                raise ValueError(f'{ref}: Wortpositionen/Oberflächenformen passen nicht zum Text.')
            annotations[ref] = [entry[2:] for entry in entries]
    return manifest, sections, annotations, edition_map, translation_data, translation_documents


def install_package(raw):
    manifest, sections, annotations, editions, translations, translation_documents = inspect_package(raw)
    meta = manifest['source']
    sources._validate_metadata(meta['id'],meta['title'],meta['author'],meta['language'],
        meta['edition'],meta['license'],meta['provenance'],meta['version'])
    with connect() as db:
        existing = db.execute('SELECT * FROM source_modules WHERE id=?',(meta['id'],)).fetchone()
        updated = existing is not None
        if updated:
            old_sections = db.execute(
                'SELECT ref,ordinal,text FROM source_sections WHERE module_id=? ORDER BY ordinal',
                (meta['id'],)).fetchall()
            if [(row['ref'],row['ordinal'],row['text']) for row in old_sections] != sections:
                raise ValueError('Das installierte Werk hat abweichende Stellen oder Text; ein sicheres Paketupdate ist nicht möglich.')
            db.execute('UPDATE source_modules SET title=?,author=?,language=?,edition=?,license=?,provenance=?,version=? WHERE id=?',
                (meta['title'],meta['author'],meta['language'],meta['edition'],meta['license'],meta['provenance'],meta['version'],meta['id']))
            # Replace package-owned analysis and translations in place. Sections and
            # user notes remain untouched because the imported text was verified above.
            db.execute('DELETE FROM source_tokens WHERE module_id=?',(meta['id'],))
            db.execute('DELETE FROM source_translations WHERE module_id=?',(meta['id'],))
            db.execute('DELETE FROM source_translation_documents WHERE module_id=?',(meta['id'],))
            db.execute('DELETE FROM source_translation_editions WHERE module_id=?',(meta['id'],))
            db.execute('DELETE FROM source_package_metadata WHERE module_id=?',(meta['id'],))
        else:
            db.execute('INSERT INTO source_modules(id,title,author,language,edition,license,provenance,version) VALUES(?,?,?,?,?,?,?,?)',
                (meta['id'],meta['title'],meta['author'],meta['language'],meta['edition'],meta['license'],meta['provenance'],meta['version']))
            db.executemany('INSERT INTO source_sections(module_id,ref,ordinal,text) VALUES(?,?,?,?)',
                [(meta['id'],ref,ordinal,text) for ref,ordinal,text in sections])
        for ref,ordinal,text in sections:
            tokens=sources._word_rows(meta['id'],ref,text)
            if ref in annotations:
                tokens=[token[:6]+detail for token,detail in zip(tokens,annotations[ref])]
            db.executemany('INSERT INTO source_tokens(module_id,ref,position,surface,start,end,lemma,morph,strong) VALUES(?,?,?,?,?,?,?,?,?)',tokens)
        db.executemany('INSERT INTO source_translation_editions(module_id,translation_id,language,title,author,edition,license,provenance) VALUES(?,?,?,?,?,?,?,?)',
            [(meta['id'],e['id'],e['language'],e['title'],e['author'],e['edition'],e['license'],e['provenance']) for e in editions.values()])
        db.executemany('INSERT INTO source_translations(module_id,ref,translation_id,text) VALUES(?,?,?,?)',
            [(meta['id'],ref,tid,text) for ref,tid,text in translations])
        db.executemany('INSERT INTO source_translation_documents(module_id,translation_id,text) VALUES(?,?,?)',
            [(meta['id'],tid,text) for tid,text in translation_documents])
        metadata={key:manifest[key] for key in ('reference_scheme','scope','annotation_edition') if key in manifest}
        db.executemany('INSERT INTO source_package_metadata(module_id,key,value) VALUES(?,?,?)',
            [(meta['id'],key,json.dumps(value,ensure_ascii=False)) for key,value in metadata.items()])
    return {'module_id':meta['id'],'sections':len(sections),'annotated_sections':len(annotations),
            'translations':len(translations)+len(translation_documents),
            'work_translations':len(translation_documents),
            'updated':updated,
            'package_sha256':hashlib.sha256(raw).hexdigest()}
