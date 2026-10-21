"""Locally imported lexical datasets. Exact, source-preserving lexical lookups."""
import csv
import io
import re
import unicodedata
from .database import connect

MAX_BYTES = 12_000_000
ID = re.compile(r'[a-zA-Z0-9_-]{2,48}\Z')

def clean_key(value):
    return unicodedata.normalize('NFC', value.strip()).casefold()

def latin_key(value):
    """Macron-insensitive Latin lookup; preserves the printed headword."""
    value=re.sub(r'\((\d+)\)$',r'\1',value.strip())
    return ''.join(char for char in unicodedata.normalize('NFD', value.casefold())
                   if unicodedata.category(char) != 'Mn')

def read_lexicon(raw):
    if len(raw)>MAX_BYTES:
        raise ValueError('Lexikondatei darf maximal 12 MB enthalten.')
    try: txt=raw.decode('utf-8-sig')
    except UnicodeDecodeError: raise ValueError('Lexikondatei muss UTF-8 enthalten.')
    delimiter='\t' if txt[:3000].count('\t')>txt[:3000].count(',') else ','
    reader=csv.DictReader(io.StringIO(txt),delimiter=delimiter)
    if not reader.fieldnames or not {'lemma','definition'}.issubset(set(reader.fieldnames)):
        raise ValueError('Erforderliche Spalten: lemma, definition; optional strong, gloss, reference.')
    entries=[];keys=set()
    for n,row in enumerate(reader,2):
        if n>100001: raise ValueError('Maximal 100.000 Lexikoneinträge.')
        lemma=(row.get('lemma') or '').strip();definition=(row.get('definition') or '').strip()
        strong=(row.get('strong') or '').strip();gloss=(row.get('gloss') or '').strip();reference=(row.get('reference') or '').strip()
        if not lemma or not definition or len(lemma)>200 or len(definition)>8000 or len(strong)>80 or len(gloss)>500 or len(reference)>500:
            raise ValueError(f'Zeile {n}: Lemma/Definition fehlt oder Feld ist zu lang.')
        if '\x00' in ''.join((lemma,definition,strong,gloss,reference)):
            raise ValueError(f'Zeile {n}: NUL-Zeichen sind nicht erlaubt.')
        key=(clean_key(lemma),strong.upper())
        if key in keys:raise ValueError(f'Zeile {n}: doppelter Eintrag für Lemma und Strong.')
        keys.add(key);entries.append((lemma,clean_key(lemma),strong.upper(),gloss,definition,reference))
    if not entries:raise ValueError('Lexikon enthält keine Einträge.')
    return entries

def install_lexicon(module_id,title,language,license_name,provenance,version,entries):
    if not ID.fullmatch(module_id):raise ValueError('Lexikon-ID: 2–48 Zeichen, Buchstaben, Zahlen, - oder _.')
    if language not in ('la','grc','he'):raise ValueError('Lexikon-Sprache muss la, grc oder he sein.')
    if any(not s or len(s)>250 for s in (title,license_name,provenance,version)):
        raise ValueError('Titel, Lizenz, Quelle und Version sind Pflichtfelder (max. 250 Zeichen).')
    with connect() as db:
        if db.execute('SELECT 1 FROM lexicon_modules WHERE id=?',(module_id,)).fetchone():
            raise ValueError('Diese Lexikon-ID ist bereits vergeben.')
        db.execute('INSERT INTO lexicon_modules(id,title,language,license,provenance,version) VALUES(?,?,?,?,?,?)',
                   (module_id,title,language,license_name,provenance,version))
        db.executemany('INSERT INTO lexicon_entries(module_id,lemma,lemma_key,strong,gloss,definition,reference) VALUES(?,?,?,?,?,?,?)',
                       [(module_id,e[0],latin_key(e[0]) if language=='la' else e[1],*e[2:]) for e in entries])
    return {'module_id':module_id,'entries':len(entries)}

def installed_lexica():
    with connect() as db:
        return [dict(row) for row in db.execute('''SELECT l.*,COUNT(e.id) AS entry_count FROM lexicon_modules l
          LEFT JOIN lexicon_entries e ON e.module_id=l.id GROUP BY l.id ORDER BY l.title''')]

def lookup(language,lemma='',strong=''):
    if language not in ('la','grc','he') or len(lemma)>200 or len(strong)>80:
        raise ValueError('Ungültige Sprache oder Wortschlüssel.')
    lemma_key=latin_key(lemma) if language=='la' else clean_key(lemma)
    strong=strong.strip().upper()
    if not lemma_key and not strong: return []
    with connect() as db:
        # Strong numbers are supplementary identifiers; only exact lemma matches
        # when a lemma is provided, avoiding misleading lexical cross-links.
        # Lewis & Short suffixes homographs with digits (amicus1, amicus2).
        keys=[lemma_key]+[lemma_key+str(n) for n in range(1,10)] if language=='la' else [lemma_key]
        placeholders=','.join('?' for _ in keys)
        rows=db.execute('''SELECT e.lemma,e.strong,e.gloss,e.definition,e.reference,
               l.id AS module_id,l.title,l.language,l.license,l.provenance,l.version
               FROM lexicon_entries e JOIN lexicon_modules l ON l.id=e.module_id
               WHERE l.language=? AND ((? <> '' AND e.lemma_key IN ('''+placeholders+'''))
                  OR (? <> '' AND e.strong=?))
               ORDER BY l.title,e.lemma LIMIT 100''',
            (language,lemma_key,*keys,strong,strong)).fetchall()
    return [dict(r) for r in rows]

def remove_lexicon(module_id):
    with connect() as db:
        row=db.execute('DELETE FROM lexicon_modules WHERE id=?',(module_id,))
        return bool(row.rowcount)
