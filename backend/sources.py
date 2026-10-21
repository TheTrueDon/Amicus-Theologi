"""Independent workspace for citable, non-biblical primary sources.

CSV/TSV, JSON and TEI P5 inputs are supported. Tokens are indexed for
concordances. Imported or model-generated analyses must retain a visible
source and review status; no analysis is inferred from bare text at runtime.
"""
import csv
import html
import io
import json
import re
import sqlite3
import unicodedata
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

from .database import connect
from .lexicon import clean_key, latin_key, install_lexicon, lookup
from .search import normalize_query

LANGUAGES = ('la', 'grc', 'he')
MAX_FILE = 25_000_000
MAX_SECTIONS = 100_000
IDENT = re.compile(r'[A-Za-z0-9_-]{2,48}\Z')
WORD = re.compile(r"(?:(?!_)[\w\u0300-\u036f\u0591-\u05c7])+(?:[’'](?:(?!_)[\w\u0300-\u036f\u0591-\u05c7])+)*", re.UNICODE)
PERSEUS_LAT = 'https://raw.githubusercontent.com/PerseusDL/canonical-latinLit/master/data/phi0474/phi001/phi0474.phi001.perseus-lat2.xml'
PERSEUS_GRC = 'https://raw.githubusercontent.com/PerseusDL/canonical-greekLit/master/data/tlg0059/tlg002/tlg0059.tlg002.perseus-grc2.xml'
SEFARIA_AVOT = 'https://www.sefaria.org/api/v3/texts/Pirkei_Avot.1?version=hebrew&return_format=text_only'
PERSEUS_LS = 'https://raw.githubusercontent.com/PerseusDL/lexica/master/CTS_XML_TEI/perseus/pdllex/lat/ls/lat.ls.perseus-eng1.xml'
CSEL_AUGUSTINE = 'https://raw.githubusercontent.com/OpenGreekAndLatin/csel-dev/master/data/stoa0040/stoa001/stoa0040.stoa001.opp-lat1.xml'
OGL_CLEMENT = 'https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/master/data/tlg1271/tlg001/tlg1271.tlg001.1st1K-grc1.xml'
PTA_SEVERIAN = 'https://raw.githubusercontent.com/PatristicTextArchive/pta_data/public/data/pta0001/pta001/pta0001.pta001.pta-grc1.xml'
SEFARIA_AVOT2 = 'https://www.sefaria.org/api/v3/texts/Pirkei_Avot.2?version=hebrew&return_format=text_only'
SEFARIA_BERAKHOT = 'https://www.sefaria.org/api/v3/texts/Mishnah_Berakhot.1?version=hebrew&return_format=text_only'
SEFARIA_MISHNEH = 'https://www.sefaria.org/api/v3/texts/Mishneh_Torah,_Foundations_of_the_Torah.1?version=hebrew&return_format=text_only'
PTA_LSJ = 'https://raw.githubusercontent.com/PatristicTextArchive/pta_lexika/public/LSJ.json'
PTA_GEORGES = 'https://raw.githubusercontent.com/PatristicTextArchive/pta_lexika/public/georges_lat.json'
UD_AQUINAS = 'https://raw.githubusercontent.com/UniversalDependencies/UD_Latin-ITTB/master/la_ittb-ud-dev.conllu'
UD_GREEK = 'https://raw.githubusercontent.com/UniversalDependencies/UD_Ancient_Greek-Perseus/master/grc_perseus-ud-dev.conllu'
CIRCSE_CONFESSIONS = ('https://raw.githubusercontent.com/CIRCSE/AugustiniConfessiones/'
                      'main/connlu/Confessiones_complete.conllu')
PTA_SEVERIAN_ANALYZED = ('https://raw.githubusercontent.com/PatristicTextArchive/pta_data/'
                         'public/analyzed/pta0001/pta001/pta0001.pta001.pta-grc1.xml')

CATALOG = {
    'quellen-cicero': dict(title='Cicero · Pro P. Quinctio', author='M. Tullius Cicero',
        language='la', kind='text', category='quellen', format='tei', url=PERSEUS_LAT,
        edition='A. C. Clark, Orationes 4, Oxford 1909',
        license='CC BY-SA 4.0', provenance='Perseus Digital Library, Tufts University'),
    'quellen-platon': dict(title='Platon · Apologie des Sokrates', author='Platon',
        language='grc', kind='text', category='quellen', format='tei', url=PERSEUS_GRC,
        edition='J. Burnet, Platonis Opera I, Oxford 1905',
        license='CC BY-SA 4.0 (Sammlung; Editionshinweise beachten)',
        provenance='Perseus Digital Library, Tufts University'),
    'quellen-avot1': dict(title='Pirkei Avot · Kapitel 1', author='Mischna',
        language='he', kind='text', category='quellen', format='sefaria', url=SEFARIA_AVOT,
        edition='Sefaria · gewählte hebräische Version',
        license='Wird beim Download aus den Versionsmetadaten geprüft',
        provenance='Sefaria.org (Versionslizenz wird geprüft)'),
    'quellen-lewis-short': dict(title='Lewis & Short · Latin Dictionary', author='Lewis / Short',
        language='la', kind='lexicon', category='lexika', format='tei-lexicon', url=PERSEUS_LS,
        edition='Perseus Digital Library, Lewis & Short',
        license='CC BY-SA 4.0 (Repository; Edition prüfen)',
        provenance='PerseusDL/lexica, digitalisierte historische Ausgabe'),
    'quellen-augustinus': dict(title='Augustinus · Confessiones', author='Augustinus von Hippo',
        language='la',kind='text',category='quellen',format='tei',url=CSEL_AUGUSTINE,
        edition='P. Knöll, CSEL 33, 1896 (digitaler Text: Open Greek and Latin)',
        license='CC BY-SA 4.0 (digitale Ausgabe)',provenance='OpenGreekAndLatin/csel-dev'),
    'quellen-clemens': dict(title='Clemens von Rom · 1. Korintherbrief',author='Clemens Romanus',
        language='grc',kind='text',category='quellen',format='tei',url=OGL_CLEMENT,
        edition='Kirsopp Lake, Apostolic Fathers',license='CC BY-SA 4.0',
        provenance='OpenGreekAndLatin/First1KGreek'),
    'quellen-severian': dict(title='Severian von Gabala · De fide et lege naturae',
        author='Severianus Gabalensis',language='grc',kind='text',category='quellen',
        format='pta-tei',url=PTA_SEVERIAN,
        edition='Patrologia Graeca 48, 1081–1088; PTA Bearbeitung Voicu / von Stockhausen',
        license='CC BY-SA 4.0',provenance='Patristic Text Archive, BBAW'),
    'quellen-avot2': dict(title='Pirkei Avot · Kapitel 2',author='Mischna',
        language='he',kind='text',category='quellen',format='sefaria',url=SEFARIA_AVOT2,
        edition='Sefaria · hebräische Version',license='Version bei Download geprüft',
        provenance='Sefaria.org'),
    'quellen-berakhot': dict(title='Mischna Berakhot · Kapitel 1',author='Mischna',
        language='he',kind='text',category='quellen',format='sefaria',url=SEFARIA_BERAKHOT,
        edition='Sefaria · hebräische Version',license='Version bei Download geprüft',
        provenance='Sefaria.org'),
    'quellen-mishneh': dict(title='Maimonides · Mischne Tora, Grundlagen 1',
        author='Moses Maimonides',language='he',kind='text',category='quellen',
        format='sefaria',url=SEFARIA_MISHNEH,edition='Sefaria · hebräische Version',
        license='Version bei Download geprüft',provenance='Sefaria.org'),
    'quellen-lsj': dict(title='Liddell–Scott–Jones · Griechisches Lexikon',
        author='Liddell / Scott / Jones',language='grc',kind='lexicon',
        category='lexika',format='pta-json-lexicon',url=PTA_LSJ,
        edition='LSJ, digitalisierte Datensätze des PTA',
        license='CC BY-SA 4.0 (Perseus-Ausgangsmaterial; Datei prüfen)',
        provenance='PatristicTextArchive/pta_lexika, LSJ.json'),
    'quellen-georges': dict(title='Georges · Lateinisch-deutsches Handwörterbuch',
        author='Karl Ernst Georges',language='la',kind='lexicon',category='lexika',
        format='pta-json-lexicon',url=PTA_GEORGES,
        edition='Digitalisierter Georges, PTA',
        license='Historisches Wörterbuch; digitale Rechte beim Herausgeber prüfen',
        provenance='PatristicTextArchive/pta_lexika, georges_lat.json'),
    'quellen-ittb': dict(title='Thomas von Aquin · annotierte Textproben',
        author='Thomas von Aquin',language='la',kind='treebank',category='sprachen',
        format='conllu',url=UD_AQUINAS,
        edition='Index Thomisticus Treebank, UD dev-Korpus (Auszug)',
        license='CC BY-NC-SA 3.0 (nicht kommerziell)',
        provenance='UniversalDependencies/UD_Latin-ITTB'),
    'quellen-ud-grc': dict(title='Griechische Wortanalysen · Perseus Treebank',
        author='Perseus / Universal Dependencies',language='grc',kind='treebank',
        category='sprachen',format='conllu',url=UD_GREEK,
        edition='UD Ancient Greek Perseus, dev-Korpus (Auszug)',
        license='CC BY-NC-SA 2.5 (nicht kommerziell)',
        provenance='UniversalDependencies/UD_Ancient_Greek-Perseus'),
    'quellen-confessiones-annotiert': dict(title='Augustinus · Confessiones (morphologisch annotiert)',
        author='Augustinus von Hippo',language='la',kind='treebank',category='sprachen',
        format='conllu',url=CIRCSE_CONFESSIONS,
        edition='The Latin Library; CIRCSE / LiLa, linguistisch überprüfte Annotation',
        license='CC BY-SA 4.0',provenance='CIRCSE/Università Cattolica del Sacro Cuore, Milano',
        description='Gesamter Confessiones-Text mit von CIRCSE manuell nachgeprüften Lemmata und Wortarten; eigenständige Textedition.'),
    'quellen-severian-annotiert': dict(title='Severian von Gabala · morphologisch analysierte Edition',
        author='Severianus Gabalensis',language='grc',kind='treebank',category='sprachen',
        format='pta-analyzed-tei',url=PTA_SEVERIAN_ANALYZED,
        edition='Patrologia Graeca 48, 1081–1088; PTA automatisierte Wortanalyse',
        license='Wird aus dem TEI-Dateikopf geprüft',provenance='Patristic Text Archive, BBAW',
        description='Griechische Originaledition mit automatisch erzeugten Lemma-, Wortarten- und Flexionsdaten. Nicht manuell validiert.'),
    'hilfsmittel-corpus': dict(title='Corpus Corporum · Lateinische Forschungsbibliothek',
        author='Universität Zürich',language='la',kind='reference',category='hilfsmittel',
        format='external',url='https://mlat.uzh.ch/',
        edition='Online-Textbibliothek mit TEI-Export je nach Werk',
        license='Nutzungsrechte der einzelnen Texte beachten',
        provenance='Universität Zürich',description='Online-Korpus öffnen und Texte im TEI-Format exportieren; kein Komplettdownload'),
    'hilfsmittel-grammatik': dict(title='Morphologie · Universal Dependencies Referenz',
        author='Universal Dependencies',language='all',kind='reference',category='hilfsmittel',
        format='external',url='https://universaldependencies.org/u/feat/index.html',
        edition='Aktuelle Beschreibung der morphologischen Merkmale',
        license='Dokumentationsseite',provenance='Universal Dependencies',
        description='Grammatikmerkmale und Codes wissenschaftlich nachschlagen'),
}


def setup(db):
    """Additive schema: original Bible tables, settings and projects are untouched."""
    db.executescript("""
    CREATE TABLE IF NOT EXISTS source_modules (
      id TEXT PRIMARY KEY, title TEXT NOT NULL, author TEXT NOT NULL,
      language TEXT NOT NULL, edition TEXT NOT NULL,
      license TEXT NOT NULL, provenance TEXT NOT NULL, version TEXT NOT NULL,
      installed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS source_sections (
      module_id TEXT NOT NULL REFERENCES source_modules(id) ON DELETE CASCADE,
      ref TEXT NOT NULL, ordinal INTEGER NOT NULL, text TEXT NOT NULL,
      PRIMARY KEY (module_id, ref), UNIQUE(module_id, ordinal)
    );
    CREATE TABLE IF NOT EXISTS source_tokens (
      module_id TEXT NOT NULL, ref TEXT NOT NULL, position INTEGER NOT NULL,
      surface TEXT NOT NULL, start INTEGER NOT NULL, end INTEGER NOT NULL,
      lemma TEXT, morph TEXT, strong TEXT,
      PRIMARY KEY (module_id, ref, position),
      FOREIGN KEY(module_id, ref) REFERENCES source_sections(module_id,ref) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_source_lemma ON source_tokens(module_id,lemma);
    CREATE INDEX IF NOT EXISTS idx_source_surface ON source_tokens(module_id,surface);
    CREATE INDEX IF NOT EXISTS idx_source_annotated_forms ON source_tokens(surface,lemma)
      WHERE lemma IS NOT NULL;
    CREATE INDEX IF NOT EXISTS idx_bible_source_form_candidates ON tokens(surface)
      WHERE lemma IS NOT NULL;
    CREATE TABLE IF NOT EXISTS source_notes (
      module_id TEXT NOT NULL, ref TEXT NOT NULL, content TEXT NOT NULL,
      modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      PRIMARY KEY(module_id,ref),
      FOREIGN KEY(module_id,ref) REFERENCES source_sections(module_id,ref) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS source_translation_editions (
      module_id TEXT NOT NULL REFERENCES source_modules(id) ON DELETE CASCADE,
      translation_id TEXT NOT NULL, language TEXT NOT NULL, title TEXT NOT NULL,
      author TEXT NOT NULL, edition TEXT NOT NULL, license TEXT NOT NULL,
      provenance TEXT NOT NULL, PRIMARY KEY(module_id,translation_id)
    );
    CREATE TABLE IF NOT EXISTS source_package_metadata (
      module_id TEXT NOT NULL REFERENCES source_modules(id) ON DELETE CASCADE,
      key TEXT NOT NULL, value TEXT NOT NULL,
      PRIMARY KEY(module_id,key)
    );
    CREATE TABLE IF NOT EXISTS source_translations (
      module_id TEXT NOT NULL, ref TEXT NOT NULL, translation_id TEXT NOT NULL,
      text TEXT NOT NULL, PRIMARY KEY(module_id,ref,translation_id),
      FOREIGN KEY(module_id,ref) REFERENCES source_sections(module_id,ref) ON DELETE CASCADE,
      FOREIGN KEY(module_id,translation_id) REFERENCES source_translation_editions(module_id,translation_id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS source_translation_documents (
      module_id TEXT NOT NULL REFERENCES source_modules(id) ON DELETE CASCADE,
      translation_id TEXT NOT NULL, text TEXT NOT NULL,
      PRIMARY KEY(module_id,translation_id),
      FOREIGN KEY(module_id,translation_id) REFERENCES source_translation_editions(module_id,translation_id) ON DELETE CASCADE
    );
    CREATE VIRTUAL TABLE IF NOT EXISTS source_fts USING fts5(
      text, content='source_sections', content_rowid='rowid',
      tokenize='unicode61 remove_diacritics 2'
    );
    CREATE TRIGGER IF NOT EXISTS source_fts_insert AFTER INSERT ON source_sections BEGIN
      INSERT INTO source_fts(rowid,text) VALUES(new.rowid,new.text);
    END;
    CREATE TRIGGER IF NOT EXISTS source_fts_delete AFTER DELETE ON source_sections BEGIN
      INSERT INTO source_fts(source_fts,rowid,text) VALUES('delete',old.rowid,old.text);
    END;
    CREATE TRIGGER IF NOT EXISTS source_fts_update AFTER UPDATE ON source_sections BEGIN
      INSERT INTO source_fts(source_fts,rowid,text) VALUES('delete',old.rowid,old.text);
      INSERT INTO source_fts(rowid,text) VALUES(new.rowid,new.text);
    END;
    """)


def _local(tag):
    return tag.rsplit('}', 1)[-1]


def _visible(node):
    """Collect diplomatic reading without notes, metadata or editorial apparatus."""
    def walk(elem):
        if _local(elem.tag) in ('note', 'head', 'teiHeader', 'app', 'fw'):
            return ''
        value = elem.text or ''
        for child in elem:
            value += walk(child) + (child.tail or '')
        return value
    return re.sub(r'\s+', ' ', walk(node)).strip()


def read_tei(raw):
    if len(raw) > MAX_FILE:
        raise ValueError('TEI-Datei ist zu groß (max. 25 MB).')
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise ValueError('XML mit DTD oder externen Entities wird nicht importiert.')
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError(f'XML/TEI kann nicht gelesen werden: {exc}') from exc
    body = next((e for e in root.iter() if _local(e.tag) == 'body'), None)
    if body is None:
        raise ValueError('TEI enthält keinen Textkörper <body>.')
    found = []
    counts = Counter()

    def traverse(node, divisions):
        name = _local(node.tag)
        if name.startswith('div'):
            n = node.get('n') or node.get('{http://www.w3.org/XML/1998/namespace}id') or ''
            if n and not n.startswith('urn:') and len(n) <= 80:
                divisions = [*divisions, n]
        if name in ('p', 'l', 'ab'):
            value = _visible(node)
            if value:
                base = '.'.join(divisions) or 'Text'
                counts[base] += 1
                # Multiple paragraphs in one cited section share the same section root.
                ref = base if counts[base] == 1 else f'{base}.{counts[base]}'
                found.append((ref, value))
            return
        if name in ('note', 'teiHeader', 'app'):
            return
        for child in node:
            traverse(child, divisions)

    traverse(body, [])
    return _validate_sections(found)


def read_tei_annotated(raw):
    """Import PTA word-level TEI, retaining only strictly aligned annotations.

    The PTA's analyzed edition is *automatically* tagged, not manually verified.
    No form is silently assigned the annotation of another word.
    """
    rows = read_tei(raw)
    root = ET.fromstring(raw)
    body = next(e for e in root.iter() if _local(e.tag) == 'body')
    annotations = {}
    counts = Counter()
    skipped = 0

    def visible_words(node):
        if _local(node.tag) in ('note', 'head', 'teiHeader', 'app', 'fw'):
            return []
        if _local(node.tag) == 'w':
            return [node]
        result = []
        for child in node:
            result.extend(visible_words(child))
        return result

    def traverse(node, divisions):
        nonlocal skipped
        name = _local(node.tag)
        if name.startswith('div'):
            n = node.get('n') or node.get('{http://www.w3.org/XML/1998/namespace}id') or ''
            if n and not n.startswith('urn:') and len(n) <= 80:
                divisions = [*divisions, n]
        if name in ('p', 'l', 'ab'):
            value = _visible(node)
            if not value:
                return
            base = '.'.join(divisions) or 'Text'
            counts[base] += 1
            ref = base if counts[base] == 1 else f'{base}.{counts[base]}'
            source_words = visible_words(node)
            actual = list(WORD.finditer(value))
            tagged = []
            for word in source_words:
                word_text = _visible(word)
                found = list(WORD.finditer(word_text))
                # PTA also wraps punctuation in <w pos="PUNCT"> elements.
                # An apostrophe or punctuation adjoining a lexical item is
                # part of its TEI element but not necessarily our token.
                if not found:
                    continue
                if len(found) != 1:
                    tagged = []
                    break
                tagged.append((found[0].group(),word))
            if actual and len(actual) == len(tagged) and all(
                _normalize_word(m.group()) == _normalize_word(surface)
                for m,(surface,_) in zip(actual,tagged)
            ):
                annotations[ref] = [
                    (word.get('lemma') or None,
                     '|'.join(x for x in (word.get('pos'),word.get('msd')) if x) or None,
                     None)
                    for _,word in tagged]
            else:
                skipped += 1
            return
        if name in ('note', 'teiHeader', 'app'):
            return
        for child in node:
            traverse(child,divisions)

    traverse(body, [])
    if not annotations:
        raise ValueError('Die analysierte TEI-Quelle enthält keine eindeutig zuordenbaren Wortdaten.')
    return rows, annotations, skipped


def _validate_sections(items):
    if not items or len(items) > MAX_SECTIONS:
        raise ValueError('Die Quelle benötigt 1 bis 100.000 Textabschnitte.')
    rows = []
    seen = set()
    for n, (reference, text) in enumerate(items, 1):
        if reference is None or text is None:
            raise ValueError(f'Abschnitt {n}: Referenz oder Text fehlt.')
        reference = str(reference).strip()
        text = str(text).strip()
        if (not reference or not text or len(reference) > 160 or
                len(text) > 20_000 or '\x00' in reference + text):
            raise ValueError(f'Abschnitt {n}: Referenz oder Text fehlt / ist zu lang.')
        if reference in seen:
            raise ValueError(f'Doppelte Referenz: {reference}.')
        seen.add(reference)
        rows.append((reference, n, text))
    return rows


def read_source(raw, fmt='auto'):
    if len(raw) > MAX_FILE:
        raise ValueError('Quelldatei ist zu groß (max. 25 MB).')
    try:
        txt = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError('Bitte UTF-8-kodierte Dateien verwenden.') from exc
    if fmt == 'auto':
        stripped = txt.lstrip()
        fmt = 'tei' if stripped.startswith('<') else 'json' if stripped.startswith(('{','[')) else 'tabular'
    if fmt == 'tei':
        return read_tei(raw)
    if fmt == 'json':
        try:
            obj = json.loads(txt)
        except ValueError as exc:
            raise ValueError('Ungültige JSON-Datei.') from exc
        if isinstance(obj, dict):
            obj = obj.get('sections', [])
        if not isinstance(obj, list):
            raise ValueError('JSON benötigt eine Liste sections mit ref und text.')
        return _validate_sections([(o.get('ref', o.get('reference', '')), o.get('text', ''))
            for o in obj if isinstance(o, dict)])
    if fmt != 'tabular':
        raise ValueError('Unbekanntes Format.')
    delim = '\t' if txt[:3000].count('\t') > txt[:3000].count(',') else ','
    reader = csv.DictReader(io.StringIO(txt), delimiter=delim)
    columns = set(reader.fieldnames or ())
    if not {'ref', 'text'} <= columns and not {'reference', 'text'} <= columns:
        raise ValueError('CSV/TSV benötigt die Spalten ref,text (oder reference,text).')
    return _validate_sections([(r.get('ref') or r.get('reference'), r.get('text'))
        for r in reader])


def read_conllu(raw):
    """UD CoNLL-U -> citable sentence passages and *verified* word annotations.

    Annotate only where the source-provided sentence text and tokens agree.
    A conflicting sentence is kept readable without falsely matched lemmas.
    """
    if len(raw) > MAX_FILE:
        raise ValueError('Treebankdatei ist größer als 25 MB.')
    try:
        content = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc:
        raise ValueError('CoNLL-U muss UTF-8 enthalten.') from exc
    sections = []
    annotations = {}
    references = set()
    skipped = 0
    for number, block in enumerate(re.split(r'\n\s*\n', content), 1):
        metadata = {}
        words = []
        for line in block.splitlines():
            if line.startswith('# ') and ' = ' in line:
                k,v = line[2:].split(' = ',1)
                metadata[k.strip()] = v.strip()
            elif line and not line.startswith('#'):
                fields = line.split('\t')
                while len(fields)>10 and fields[-1]=='':
                    fields.pop()
                # CIRCSE augments some LiLa-linked CoNLL-U records with an
                # 11th column containing a Lemma Bank URI. The first 10
                # columns still follow CoNLL-U and are used unchanged.
                if (len(fields) == 11 and
                        (fields[10] == '_' or fields[10].startswith('http://lila-erc.eu/data/id/'))):
                    fields = fields[:10]
                if len(fields) != 10:
                    raise ValueError(f'CoNLL-U Abschnitt {number}: 10 Spalten erwartet.')
                if fields[0].isdigit():
                    words.append(fields)
        if not words:
            continue
        reference = metadata.get('reference') or metadata.get('sent_id') or f'Satz-{number}'
        if reference in references:
            reference = f'{reference}-{number}'
        references.add(reference)
        raw_text = metadata.get('text')
        if not raw_text:
            chunks = []
            for index, entry in enumerate(words):
                if index and 'SpaceAfter=No' not in words[index-1][9]:
                    chunks.append(' ')
                chunks.append(entry[1])
            raw_text = ''.join(chunks)
        sections.append((reference,raw_text))
        lexical = [w for w in words if WORD.fullmatch(w[1])]
        detected = list(WORD.finditer(raw_text))
        if len(lexical) != len(detected) or not all(
                _normalize_word(w[1]) == _normalize_word(m.group())
                for w,m in zip(lexical,detected)):
            skipped += 1
            continue
        annotations[reference] = [
            (w[2] if w[2] != '_' else None,
             '|'.join(x for x in (w[3],w[5]) if x and x!='_'), '')
            for w in lexical]
    return _validate_sections(sections), annotations, skipped


def _validate_metadata(module_id, title, author, language, edition, license_name, provenance, version):
    if not IDENT.fullmatch(module_id):
        raise ValueError('ID: 2–48 Zeichen, A–Z, 0–9, _ oder -.')
    if language not in LANGUAGES:
        raise ValueError('Unterstützte Quellsprachen: la, grc, he.')
    if any(not s.strip() or len(s) > 250 for s in (title, author, edition, license_name, provenance, version)):
        raise ValueError('Titel, Autor, Edition, Lizenz, Herkunft und Version sind Pflicht (max. 250 Zeichen).')


def _word_rows(module_id, ref, content):
    return [(module_id, ref, n, m.group(), m.start(), m.end(), None, None, None)
            for n, m in enumerate(WORD.finditer(content), 1)]


def install_source(module_id, title, author, language, edition, license_name, provenance, version,
                   sections, word_annotations=None):
    _validate_metadata(module_id, title, author, language, edition, license_name, provenance, version)
    rows = _validate_sections([(r[0], r[2]) for r in sections])
    with connect() as db:
        if db.execute('SELECT 1 FROM source_modules WHERE id=?', (module_id,)).fetchone():
            raise ValueError('Quellenmodul bereits installiert. Bitte andere ID verwenden.')
        db.execute("""INSERT INTO source_modules
          (id,title,author,language,edition,license,provenance,version)
          VALUES (?,?,?,?,?,?,?,?)""",
          (module_id,title,author,language,edition,license_name,provenance,version))
        db.executemany('INSERT INTO source_sections(module_id,ref,ordinal,text) VALUES(?,?,?,?)',
                       [(module_id,*r) for r in rows])
        for ref, _, value in rows:
            tokens = _word_rows(module_id, ref, value)
            if len(tokens) > 5000:
                raise ValueError(f'{ref}: maximal 5.000 Wörter je Abschnitt.')
            if word_annotations and ref in word_annotations:
                provided = word_annotations[ref]
                if len(provided) != len(tokens):
                    raise ValueError(f'{ref}: Annotationen passen nicht zu den Textwörtern.')
                tokens = [t[:6] + detail for t,detail in zip(tokens,provided)]
            db.executemany("""INSERT INTO source_tokens
              (module_id,ref,position,surface,start,end,lemma,morph,strong)
              VALUES(?,?,?,?,?,?,?,?,?)""", tokens)
    return {'module_id':module_id, 'sections':len(rows),
            'annotated_sections':len(word_annotations or {})}


def modules():
    with connect() as db:
        result = [dict(r) for r in db.execute("""SELECT m.*,
          (SELECT COUNT(*) FROM source_sections s WHERE s.module_id=m.id) AS section_count,
          (SELECT COUNT(*) FROM source_tokens t WHERE t.module_id=m.id AND t.lemma IS NOT NULL) AS annotated_tokens
          FROM source_modules m ORDER BY m.title""")]
        for item in result:
            item['package_metadata'] = {r['key']: json.loads(r['value']) for r in db.execute(
                'SELECT key,value FROM source_package_metadata WHERE module_id=?',(item['id'],))}
        return result


def remove_source(module_id):
    with connect() as db:
        return bool(db.execute('DELETE FROM source_modules WHERE id=?',(module_id,)).rowcount)


def sections_for(module_id):
    with connect() as db:
        return [dict(r) for r in db.execute(
            'SELECT ref,ordinal,substr(text,1,120) AS preview FROM source_sections WHERE module_id=? ORDER BY ordinal',
            (module_id,))]


def passage(module_id, reference):
    with connect() as db:
        current = db.execute('SELECT * FROM source_sections WHERE module_id=? AND ref=?',(module_id,reference)).fetchone()
        if current is None:
            raise ValueError('Diese Quellenstelle wurde nicht gefunden.')
        rows = db.execute("""SELECT position,surface,start,end,lemma,morph,strong
          FROM source_tokens WHERE module_id=? AND ref=? ORDER BY position""",(module_id,reference)).fetchall()
        translations = [dict(r) for r in db.execute("""SELECT t.translation_id,t.text,e.language,
          e.title,e.author,e.edition,e.license,e.provenance
          FROM source_translations t JOIN source_translation_editions e
          USING(module_id,translation_id) WHERE t.module_id=? AND t.ref=?
          ORDER BY e.language,e.title""",(module_id,reference))]
        work_translations = []
        if current['ordinal'] == 1:
            work_translations = [dict(r) for r in db.execute("""SELECT t.translation_id,t.text,e.language,
              e.title,e.author,e.edition,e.license,e.provenance
              FROM source_translation_documents t JOIN source_translation_editions e
              USING(module_id,translation_id) WHERE t.module_id=? ORDER BY e.language,e.title""",(module_id,))]
        package_metadata = {r['key']: json.loads(r['value']) for r in db.execute(
            'SELECT key,value FROM source_package_metadata WHERE module_id=?',(module_id,))}
        prev = db.execute('SELECT ref FROM source_sections WHERE module_id=? AND ordinal<? ORDER BY ordinal DESC LIMIT 1',
                          (module_id,current['ordinal'])).fetchone()
        nxt = db.execute('SELECT ref FROM source_sections WHERE module_id=? AND ordinal>? ORDER BY ordinal LIMIT 1',
                         (module_id,current['ordinal'])).fetchone()
    return {'ref':reference,'text':current['text'],'tokens':[dict(r) for r in rows],
            'translations':translations,
            'work_translations':work_translations,
            'package_metadata':package_metadata,
            'previous':prev[0] if prev else None,'next':nxt[0] if nxt else None}


def _normalize_word(value):
    return ''.join(c.casefold() for c in unicodedata.normalize('NFC', value)
                   if unicodedata.category(c)[0] not in ('P','Z','C','S'))


def import_annotations(module_id, raw):
    if len(raw) > MAX_FILE:
        raise ValueError('Annotationsdatei maximal 25 MB.')
    try: txt = raw.decode('utf-8-sig')
    except UnicodeDecodeError as exc: raise ValueError('UTF-8 benötigt.') from exc
    delim = '\t' if txt[:3000].count('\t') > txt[:3000].count(',') else ','
    reader = csv.DictReader(io.StringIO(txt), delimiter=delim)
    if not {'ref','position','surface','lemma','morph'} <= set(reader.fieldnames or ()):
        raise ValueError('Annotationsspalten: ref,position,surface,lemma,morph; optional strong.')
    data = {}
    for index, row in enumerate(reader, 2):
        if index > 300_000: raise ValueError('Zu viele Annotationen.')
        ref = (row.get('ref') or '').strip()
        try: pos = int(row['position'])
        except (ValueError,TypeError): raise ValueError(f'Zeile {index}: Position ungültig.')
        values = tuple((row.get(key) or '').strip() for key in ('surface','lemma','morph','strong'))
        if not ref or pos < 1 or pos > 5000 or not values[0] or not values[1] or any(len(v)>200 for v in values):
            raise ValueError(f'Zeile {index}: fehlende oder ungültige Annotation.')
        data.setdefault(ref, []).append((pos, *values))
    if not data: raise ValueError('Annotationsdatei ist leer.')
    with connect() as db:
        if not db.execute('SELECT 1 FROM source_modules WHERE id=?',(module_id,)).fetchone():
            raise ValueError('Quellentext muss zuerst installiert sein.')
        for ref, entries in data.items():
            existing = db.execute("""SELECT position,surface FROM source_tokens
                WHERE module_id=? AND ref=? ORDER BY position""",(module_id,ref)).fetchall()
            entries.sort(key=lambda r:r[0])
            if not existing or len(entries) != len(existing):
                raise ValueError(f'{ref}: Wortanzahl stimmt nicht mit dem Text überein.')
            if any(p != original['position'] or _normalize_word(surface) != _normalize_word(original['surface'])
                   for (p,surface,*_), original in zip(entries,existing)):
                raise ValueError(f'{ref}: Wortposition oder Oberfläche weicht von der Quelle ab.')
        for ref, entries in data.items():
            db.executemany("""UPDATE source_tokens SET lemma=?,morph=?,strong=?
                WHERE module_id=? AND ref=? AND position=?""",
                [(lemma, morph or None, strong or None, module_id, ref, p)
                 for p,surface,lemma,morph,strong in entries])
    return {'annotated_sections':len(data),'tokens':sum(map(len,data.values()))}


def word_analysis(module_id, reference, position):
    with connect() as db:
        row = db.execute("""SELECT t.*,m.title,m.language,m.edition,m.license,m.provenance
            FROM source_tokens t JOIN source_modules m ON m.id=t.module_id
            WHERE t.module_id=? AND t.ref=? AND t.position=?""",(module_id,reference,position)).fetchone()
        if row is None: raise ValueError('Wortposition nicht gefunden.')
        obj = dict(row)
        annotation_row=db.execute("SELECT value FROM source_package_metadata WHERE module_id=? AND key='annotation_edition'",
                                  (module_id,)).fetchone()
        annotation_meta=json.loads(annotation_row['value']) if annotation_row else {}
        options = list(dict.fromkeys((obj['surface'],obj['surface'].lower(),
                                     obj['surface'].capitalize())))
        placeholders = ','.join('?' for _ in options)
        candidates = []
        if not obj['lemma']:
            # Evidence from independent, annotated passages is useful, but does
            # not prove the correct reading in the passage currently displayed.
            candidates.extend(dict(r) for r in db.execute("""
              SELECT t.lemma, t.morph, COUNT(*) AS attestations,
                MIN(m.title) AS source_title FROM source_tokens t
                JOIN source_modules m ON m.id=t.module_id
              WHERE m.language=? AND t.lemma IS NOT NULL
                AND t.surface IN ("""+placeholders+""")
              GROUP BY t.lemma,t.morph ORDER BY attestations DESC LIMIT 8
            """,[obj['language'],*options]))
            candidates.extend(dict(r) for r in db.execute("""
              SELECT t.lemma, t.morph, COUNT(*) AS attestations,
                MIN(m.title) AS source_title FROM tokens t
                JOIN modules m ON m.id=t.module_id
              WHERE m.language=? AND t.lemma IS NOT NULL
                AND t.surface IN ("""+placeholders+""")
              GROUP BY t.lemma,t.morph ORDER BY attestations DESC LIMIT 8
            """,[obj['language'],*options]))
    lemma = obj['lemma'] or obj['surface']
    from .morph_display import decode
    morph = obj['morph'] or ''
    decoded=decode(morph,obj['language']) if morph else {'recognized':False,'features':[]}
    features=decoded.get('features',[])
    grammar=' · '.join(f"{item['name']}: {item['value']}" for item in features)
    obj['morphology_detail_missing']=(decoded.get('scheme')=='Universal Dependencies' and len(features)<=1)
    if obj['morphology_detail_missing'] and grammar:
        grammar+=' · Quelle enthält keine weiteren Flexionsmerkmale'
    if not grammar:
        grammar=decoded.get('notice') or morph or 'Für diese Textstelle liegen keine wortbezogenen Morphologiedaten vor.'
        if morph and not decoded.get('recognized'):
            grammar=f"Unbekannter Morphologiecode {morph}; Originalcode bleibt erhalten."
    obj['morphology_decoded']=bool(decoded.get('recognized'))
    obj['grammar'] = grammar
    distinct = {}
    for item in candidates:
        key = (item['lemma'],item['morph'])
        if key not in distinct:
            distinct[key] = item
        else:
            distinct[key]['attestations'] += item['attestations']
    obj['candidate_analyses'] = [
        {**c,'grammar':c['morph'].replace('|',' · ') if c['morph'] and '=' in c['morph']
         else c['morph'] or 'Keine Flexionsangaben'}
        for c in sorted(distinct.values(),key=lambda c:-c['attestations'])[:8]]
    quality=annotation_meta.get('quality','provided')
    obj['annotation_quality'] = quality if obj['lemma'] else 'unannotated'
    obj['annotation_status'] = annotation_meta.get('review_status','')
    from .lexical_text import best_gloss
    entries = lookup(obj['language'], lemma, obj['strong'] or '')
    if not entries and not obj['lemma']:
        # A dictionary headword derived from another corpus is only a *hint*.
        for candidate in obj['candidate_analyses'][:4]:
            entries = lookup(obj['language'],candidate['lemma'],'')
            if entries:
                obj['lexicon_candidate_lemma'] = candidate['lemma']
                break
    obj['lexica'] = [{**entry, 'display_gloss':best_gloss(entry)} for entry in entries]
    obj['has_annotation'] = bool(obj['lemma'])
    return obj


def search_sources(query='', module_id='', mode='all', lemma='', surface='', morph='', limit=50, offset=0):
    if not 1 <= limit <= 100 or not 0 <= offset <= 100000:
        raise ValueError('Seitengröße oder Startposition ungültig.')
    if not any((query.strip(),lemma.strip(),surface.strip(),morph.strip())):
        raise ValueError('Suchbegriff oder Wortbedingung erforderlich.')
    where = [];args=[]
    if query.strip():
        expression,_ = normalize_query(query, mode)
        where.append('source_fts MATCH ?');args.append(expression)
    if module_id:
        where.append('s.module_id=?');args.append(module_id)
    if lemma or surface or morph:
        parts=['t.module_id=s.module_id','t.ref=s.ref']
        if lemma:parts.append('t.lemma=?');args.append(lemma)
        if surface:parts.append('t.surface=?');args.append(surface)
        if morph:
            parts.append("t.morph LIKE ? ESCAPE '\\'")
            args.append('%'+morph.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')
        where.append('EXISTS (SELECT 1 FROM source_tokens t WHERE ' + ' AND '.join(parts) + ')')
    clauses=' AND '.join(where)
    base='FROM source_sections s JOIN source_modules m ON m.id=s.module_id'
    if query.strip():base+=' JOIN source_fts ON source_fts.rowid=s.rowid'
    try:
        with connect() as db:
            total=db.execute('SELECT COUNT(*) '+base+' WHERE '+clauses,args).fetchone()[0]
            rows=db.execute("""SELECT s.module_id,m.title,s.ref,s.ordinal,s.text
                """+base+' WHERE '+clauses+' ORDER BY m.title,s.ordinal LIMIT ? OFFSET ?',
                args+[limit,offset]).fetchall()
    except sqlite3.OperationalError as exc:
        raise ValueError('Quellensuche nicht ausführbar: '+str(exc)) from exc
    return {'total':total,'limit':limit,'offset':offset,'results':[dict(r) for r in rows]}


def stats(module_id, lemma=''):
    with connect() as db:
        counts=db.execute("""SELECT COUNT(*) AS tokens,
            SUM(CASE WHEN lemma IS NOT NULL THEN 1 ELSE 0 END) AS annotated
            FROM source_tokens WHERE module_id=?""",(module_id,)).fetchone()
        key='lemma' if lemma else 'surface'
        if lemma:
            forms=db.execute("""SELECT surface AS form, COUNT(*) AS count FROM source_tokens
               WHERE module_id=? AND lemma=? GROUP BY surface ORDER BY count DESC,surface LIMIT 150""",
               (module_id,lemma)).fetchall()
            refs=db.execute("""SELECT ref, COUNT(*) AS count FROM source_tokens WHERE module_id=?
               AND lemma=? GROUP BY ref ORDER BY count DESC,ref LIMIT 150""",(module_id,lemma)).fetchall()
        else:
            forms=db.execute("""SELECT surface AS form, COUNT(*) AS count FROM source_tokens
               WHERE module_id=? GROUP BY surface ORDER BY count DESC,surface LIMIT 150""",(module_id,)).fetchall()
            refs=[]
    return {'tokens':counts['tokens'], 'annotated':counts['annotated'] or 0,
            'lemma':lemma,'forms':[dict(r) for r in forms],'references':[dict(r) for r in refs],
            'basis':'importierte Lemmata' if lemma else 'gezählte Schreibweisen, keine Lemmaschätzung'}


def get_note(module_id, reference):
    with connect() as db:
        r=db.execute('SELECT content,modified_at FROM source_notes WHERE module_id=? AND ref=?',
                     (module_id,reference)).fetchone()
    return dict(r) if r else {'content':'','modified_at':None}


def save_note(module_id, reference, content):
    if len(content) > 20_000:raise ValueError('Notiz zu lang (max. 20.000 Zeichen).')
    with connect() as db:
        if not db.execute('SELECT 1 FROM source_sections WHERE module_id=? AND ref=?',
                          (module_id,reference)).fetchone():
            raise ValueError('Quellenstelle fehlt.')
        if not content.strip():
            db.execute('DELETE FROM source_notes WHERE module_id=? AND ref=?',(module_id,reference))
        else:
            db.execute("""INSERT INTO source_notes(module_id,ref,content) VALUES(?,?,?)
              ON CONFLICT(module_id,ref) DO UPDATE SET content=excluded.content,modified_at=CURRENT_TIMESTAMP""",
              (module_id,reference,content))
    return get_note(module_id,reference)


def fetch_catalog_data(url, cap=MAX_FILE):
    """Fixed catalog allowlist only; no user-controlled fetch URL or local file schemes."""
    approved={item['url'] for item in CATALOG.values()}
    if url not in approved:
        raise ValueError('Nicht katalogisierte Downloadadresse.')
    with urlopen(Request(url, headers={'User-Agent':'Amicus-Theologi/1.3.2 Quellenstudium'}),
                 timeout=45) as response:
        host=urlparse(response.geturl()).hostname
        if host not in ('raw.githubusercontent.com','www.sefaria.org'):
            raise ValueError('Download wurde zu einer nicht erlaubten Adresse umgeleitet.')
        raw=response.read(cap+1)
    if len(raw)>cap:raise ValueError('Download überschreitet die sichere Dateigröße.')
    return raw


def _sefaria_sections(raw, chapter='1'):
    try:data=json.loads(raw)
    except ValueError as exc:raise ValueError('Sefaria lieferte kein gültiges JSON.') from exc
    versions=data.get('versions') or []
    selected=next((v for v in versions if v.get('language') in ('he','hebrew')),None)
    if not selected:raise ValueError('Keine hebräische Textversion von Sefaria erhalten.')
    license_name=(selected.get('license') or '').strip()
    if license_name.casefold() not in ('public domain','cc0','cc by 4.0','cc by-sa 4.0'):
        raise ValueError('Sefaria-Version ohne eindeutig freie Lizenz: '+(license_name or 'unbekannt'))
    values=selected.get('text')
    if not isinstance(values,list):raise ValueError('Sefaria lieferte keine Abschnittsliste.')
    rows=[(f'{chapter}.{i}', str(item)) for i,item in enumerate(values,1)
          if isinstance(item,str) and item.strip()]
    return _validate_sections(rows), license_name, selected.get('versionTitle','Unbenannte Sefaria-Version')


class _HTMLToText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in ('br','p','li','div'):
            self.parts.append(' ')


def _parse_pta_json_lexicon(raw, language='grc'):
    """Import PTA's w/d dictionaries as plain (not executable HTML) definitions."""
    try:
        items=json.loads(raw)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError('Lexikondatei enthält kein gültiges UTF-8-JSON.') from exc
    if not isinstance(items,list):
        raise ValueError('Das PTA-Lexikon ist keine Eintragsliste.')
    if len(items)>250_000:
        raise ValueError('Lexikon mit mehr als 250.000 Einträgen nicht unterstützt.')
    entries=[]
    positions={}
    for item in items:
        if not isinstance(item,dict):
            continue
        lemma=str(item.get('w') or '').strip()[:200]
        definition=item.get('d')
        if not lemma or not isinstance(definition,str) or not definition:
            continue
        parser=_HTMLToText()
        parser.feed(definition)
        clean=re.sub(r'\s+',' ',html.unescape(''.join(parser.parts))).strip()[:8000]
        if not clean:
            continue
        key=latin_key(lemma) if language=='la' else clean_key(lemma)
        if key in positions:
            index=positions[key]
            old=entries[index]
            if clean not in old[4] and len(old[4])<7400:
                entries[index]=(*old[:4],(old[4]+' | '+clean)[:8000],old[5])
            continue
        positions[key]=len(entries)
        entries.append((lemma,key,'','',clean,'PTA-Lexikondaten'))
    if len(entries)<100:
        raise ValueError('PTA-Lexikon enthält zu wenige gültige Einträge.')
    return entries


def _pta_license(raw):
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise ValueError('PTA-XML enthält eine unerlaubte DTD.')
    try:
        root=ET.fromstring(raw)
    except ET.ParseError as exc:
        raise ValueError('PTA-XML ist ungültig.') from exc
    for node in root.iter():
        if _local(node.tag) in ('licence','license'):
            target=node.get('target','')
            if target.startswith('https://creativecommons.org/licenses/by-sa/4.0'):
                return 'CC BY-SA 4.0'
            if target.startswith('https://creativecommons.org/licenses/by/4.0'):
                return 'CC BY 4.0'
    raise ValueError('Keine passende offene Lizenz im PTA-Dateikopf gefunden.')


def _parse_large_lexicon(raw):
    """Streaming TEI dictionary reader; no speculative meaning synthesis."""
    entries=[]
    seen=set()
    for _,el in ET.iterparse(io.BytesIO(raw),events=('end',)):
        if _local(el.tag) not in ('entry','entryFree'):
            continue
        lemma=(el.get('key') or el.get('n') or '').strip()
        if not lemma:
            orth=next((c for c in el.iter() if _local(c.tag) == 'orth'),None)
            lemma=''.join(orth.itertext()).strip() if orth is not None else ''
        lemma=lemma[:200]
        raw_definition=re.sub(r'\s+',' ',' '.join(el.itertext())).strip()[:8000]
        key=latin_key(lemma)
        if lemma and raw_definition and key not in seen:
            sense=next((e for e in el.iter() if _local(e.tag) in ('def','gloss')),None)
            gloss=re.sub(r'\s+',' ',' '.join(sense.itertext())).strip()[:500] if sense is not None else ''
            entries.append((lemma,key,'',gloss,raw_definition,'Lewis & Short (Perseus)'))
            seen.add(key)
        el.clear()
        if len(entries)>100000:raise ValueError('Lexikon überschreitet 100.000 Einträge.')
    if len(entries)<100:raise ValueError('Kein unterstütztes TEI-Lexikonformat erkannt.')
    return entries


def catalog_list():
    existing={m['id'] for m in modules()}
    with connect() as db:
        existing_lex={r[0] for r in db.execute('SELECT id FROM lexicon_modules')}
    result=[{'id':name,**{k:v for k,v in item.items() if k!='url'},
             'external_url':item['url'] if item['kind']=='reference' else '',
             'installed':name in (existing_lex if item['kind']=='lexicon' else existing),
             'download_size_hint':('ca. 77 MB' if name=='quellen-lewis-short'
               else 'ca. 40 MB' if item['format']=='pta-json-lexicon'
               else 'ca. 7 MB' if name=='quellen-confessiones-annotiert' else '')}
            for name,item in CATALOG.items()]
    from .catalog import catalog_list as existing_catalog
    for entry in existing_catalog():
        if entry['kind']=='Lexikon' and entry['language'] in ('grc','he'):
            result.append({'id':entry['id'],'kind':'lexicon','title':entry['title'],
                           'category':'lexika','language':entry['language'],
                           'author':'','edition':entry['code'],
                           'license':entry['license'],'provenance':entry['provenance'],
                           'installed':entry['installed'],'delegated':True})
    return result


def install_catalog(item_id):
    if item_id not in CATALOG:
        from .catalog import CATALOG as original, install_catalog_item
        if item_id in original and original[item_id]['kind']=='Lexikon':
            return install_catalog_item(item_id)
        raise ValueError('Unbekanntes Quellenmodul.')
    item=CATALOG[item_id]
    if item['kind']=='reference':
        raise ValueError('Diese Hilfsquelle ist extern verfügbar und kein installierbares Datenmodul.')
    raw=fetch_catalog_data(item['url'],90_000_000 if item['kind']=='lexicon' else MAX_FILE)
    if item['kind']=='lexicon':
        entries=(_parse_pta_json_lexicon(raw,item['language']) if item['format']=='pta-json-lexicon'
                 else _parse_large_lexicon(raw))
        return install_lexicon(item_id,item['title'],item['language'],item['license'],
                               item['provenance'],item['edition'],entries)
    if item['format']=='conllu':
        rows,annotations,skipped=read_conllu(raw)
        result=install_source(item_id,item['title'],item['author'],item['language'],
                              item['edition'],item['license'],
                              item['provenance']+' · '+item['url'],'1',rows,annotations)
        result['annotation_skipped_sections']=skipped
        return result
    if item['format']=='pta-analyzed-tei':
        license_name=_pta_license(raw)
        rows,annotations,skipped=read_tei_annotated(raw)
        result=install_source(item_id,item['title'],item['author'],item['language'],
                              item['edition'],license_name,
                              item['provenance']+' · '+item['url'],'1',rows,annotations)
        result['annotation_skipped_sections']=skipped
        return result
    if item['format']=='sefaria':
        chapter='2' if item_id=='quellen-avot2' else '1'
        rows,license_name,edition=_sefaria_sections(raw,chapter)
    elif item['format']=='pta-tei':
        license_name=_pta_license(raw)
        rows=read_tei(raw)
        edition=item['edition']
    else:
        rows=read_tei(raw)
        license_name=item['license'];edition=item['edition']
    return install_source(item_id,item['title'],item['author'],item['language'],edition,
                          license_name,item['provenance']+' · '+item['url'], '1',rows)
