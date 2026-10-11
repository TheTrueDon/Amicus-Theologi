"""Curated German Bible editions from official CrossWire SWORD packages.

The published URLs refer to RAW SWORD module ZIPs, not web pages or EXE files.
Only allowlisted identifiers may be fetched; texts are never bundled with Amicus.
"""
import urllib.error
import urllib.request
from .database import connect
from .source_import import parse_sword, MAX_UPLOAD

CROSSWIRE = 'https://www.crosswire.org'
RAW = CROSSWIRE + '/ftpmirror/pub/sword/packages/rawzip/'
BETA = CROSSWIRE + '/ftpmirror/pub/sword/betapackages/rawzip/'

BIBLES = {
    'GerElb1905': {
        'title': 'Elberfelder Bibel 1905', 'detail': 'Unrevidierte Elberfelder', 'language': 'de',
        'license': 'Public Domain laut CrossWire', 'base': RAW, 'status': 'Veröffentlichte Ausgabe',
    },
    'GerElb1871': {
        'title': 'Elberfelder Bibel 1871', 'detail': 'Historische Elberfelder Ausgabe', 'language': 'de',
        'license': 'Public Domain laut CrossWire', 'base': RAW, 'status': 'Veröffentlichte Ausgabe',
    },
    'GerMenge': {
        'title': 'Menge-Bibel 1939', 'detail': 'Textfassung Hermann Menge', 'language': 'de',
        'license': 'Public Domain laut CrossWire', 'base': RAW, 'status': 'Veröffentlichte Ausgabe',
    },
    'GerTextbibel': {
        'title': 'Textbibel 1906', 'detail': 'Kautzsch / Weizsäcker', 'language': 'de',
        'license': 'Public Domain laut CrossWire', 'base': RAW, 'status': 'Veröffentlichte Ausgabe',
    },
    'GerLut1912': {
        'title': 'Lutherbibel 1912', 'detail': 'Historische Lutherbibel; CrossWire-Betarepository', 'language': 'de',
        'license': 'Public Domain laut CrossWire', 'base': BETA, 'status': 'CrossWire Beta',
    },
}


def bible_catalog():
    with connect() as db:
        installed = {r[0] for r in db.execute('SELECT id FROM modules')}
    return [{
        'id': code, 'module_id': 'sword-' + code.lower(), 'installed': 'sword-' + code.lower() in installed,
        'title': entry['title'], 'detail': entry['detail'], 'language': entry['language'],
        'license': entry['license'], 'status': entry['status'],
        'source_url': CROSSWIRE + '/sword/modules/ModInfo.jsp?modName=' + code,
    } for code, entry in BIBLES.items()]


def download_bible(code):
    if code not in BIBLES:
        raise ValueError('Diese Bibelausgabe ist nicht im geprüften Katalog.')
    url = BIBLES[code]['base'] + code + '.zip'
    req = urllib.request.Request(url, headers={'User-Agent': 'AmicusTheologi/1.0.8'})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            chunks = []
            total = 0
            while True:
                part = response.read(256 * 1024)
                if not part:
                    break
                total += len(part)
                if total > min(MAX_UPLOAD, 20_000_000):
                    raise ValueError('Das SWORD-Modul überschreitet 20 MB. Import abgebrochen.')
                chunks.append(part)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ValueError('CrossWire-Download fehlgeschlagen. Internetverbindung prüfen oder ' +
                         'die ZIP-Datei auf der Originalseite herunterladen. Details: ' + str(exc)) from exc
    raw = b''.join(chunks)
    if not raw.startswith(b'PK'):
        raise ValueError('CrossWire hat keine gültige ZIP-Datei geliefert. Bitte Originalquelle kontrollieren.')
    return raw


def install_bible_from_catalog(code):
    if code not in BIBLES:
        raise ValueError('Diese Bibelausgabe ist nicht im geprüften Katalog.')
    module_id = 'sword-' + code.lower()
    with connect() as db:
        if db.execute('SELECT 1 FROM modules WHERE id=?', (module_id,)).fetchone():
            raise ValueError('Die Bibelausgabe ist bereits installiert.')
    raw = download_bible(code)
    # Require the exact source module rather than falling back to an arbitrary
    # member of an archive. This keeps the provenance and license accurate.
    verses, tokens, language, ident = parse_sword(raw, selected=code)
    if ident != code or language not in ('other', 'de'):
        raise ValueError('Das Archiv enthält nicht das erwartete CrossWire-Modul.')
    if len(verses) < 1000:
        raise ValueError('Das Modul lieferte zu wenige Verse; unvollständiger Import verhindert.')
    source = (CROSSWIRE + '/sword/modules/ModInfo.jsp?modName=' + code)
    metadata = BIBLES[code]
    with connect() as db:
        if db.execute('SELECT 1 FROM modules WHERE id=?', (module_id,)).fetchone():
            raise ValueError('Die Bibelausgabe ist bereits installiert.')
        db.execute('INSERT INTO modules(id,title,language,kind,license,provenance,version) '
                   'VALUES(?,?,?,?,?,?,?)',
                   (module_id, metadata['title'], 'de', 'bible', metadata['license'],
                    source + ' · CrossWire SWORD ' + code, 'CrossWire'))
        db.executemany('INSERT INTO verses(module_id,book,chapter,verse,text) VALUES(?,?,?,?,?)',
                       [(module_id, *k, text) for k, text in verses.items()])
    return {'module_id': module_id, 'title': metadata['title'], 'verses': len(verses),
            'language': 'de', 'source': source, 'license': metadata['license']}
