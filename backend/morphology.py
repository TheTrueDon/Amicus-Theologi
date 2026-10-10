"""User-provided morphological annotation imports; deterministic, no AI guesses.

The annotated surface sequence must match the unannotated text after removing
Unicode punctuation and spacing (not letters / accent marks). Any mismatch aborts.
"""
import csv
import io
import re
import unicodedata
from .database import connect
from .library import book_id, BOOKS

MAX_BYTES = 12_000_000
REQUIRED = {'book', 'chapter', 'verse', 'position', 'surface', 'lemma', 'morph'}

def normalize_surface(value):
    return ''.join(c.casefold() for c in unicodedata.normalize('NFC', value)
                   if unicodedata.category(c)[0] not in ('P','Z','C','S'))

def parse_annotation_file(raw):
    if len(raw) > MAX_BYTES: raise ValueError('Annotationsdatei: maximal 12 MB.')
    try: txt = raw.decode('utf-8-sig')
    except UnicodeDecodeError: raise ValueError('Annotationsdatei muss UTF-8 enthalten.')
    delim = '\t' if txt[:3000].count('\t') > txt[:3000].count(',') else ','
    reader = csv.DictReader(io.StringIO(txt), delimiter=delim)
    if not reader.fieldnames or not REQUIRED.issubset(reader.fieldnames):
        raise ValueError('Spalten: book, chapter, verse, position, surface, lemma, morph; optional strong.')
    result = {}; positions=set()
    for n, row in enumerate(reader,2):
        if n>100001:raise ValueError('Maximal 100.000 annotierte Wörter pro Datei.')
        b=book_id(row.get('book') or '')
        try: ch=int(row['chapter']);v=int(row['verse']);pos=int(row['position'])
        except (ValueError,TypeError,KeyError):raise ValueError(f'Zeile {n}: Ungültige Zahlen.')
        surface=(row.get('surface') or '').strip();lemma=(row.get('lemma') or '').strip()
        morph=(row.get('morph') or '').strip();strong=(row.get('strong') or '').strip()
        if not b or not (1<=ch<=200 and 1<=v<=200 and 1<=pos<=500) or not surface or not lemma or not morph or max(map(len,(surface,lemma,morph,strong)))>200:
            raise ValueError(f'Zeile {n}: Ungültiges Wort oder fehlende Merkmale.')
        key=(b,ch,v); ident=(*key,pos)
        if ident in positions:raise ValueError(f'Zeile {n}: doppelte Wortposition.')
        positions.add(ident)
        result.setdefault(key,[]).append((pos,surface,lemma,morph,strong or None))
    if not result:raise ValueError('Keine annotierten Wörter gefunden.')
    for ref, items in result.items():
        items.sort(key=lambda x:x[0])
        if [x[0] for x in items]!=list(range(1,len(items)+1)):
            raise ValueError(f'{ref}: Wortpositionen müssen bei 1 beginnen und lückenlos sein.')
    return result

def import_annotations(module_id, groups):
    """Atomically replace annotations only for listed verses, preserving other verses."""
    with connect() as db:
        module=db.execute('SELECT id,language FROM modules WHERE id=?',(module_id,)).fetchone()
        if module is None:raise ValueError('Textmodul nicht gefunden. Zuerst Bibeltext installieren.')
        if module['language'] not in ('grc','he'):
            raise ValueError('Morphologieimport derzeit nur für griechische/hebräische Module.')
        prepared=[]
        for (book,ch,verse), words in groups.items():
            row=db.execute('SELECT text FROM verses WHERE module_id=? AND book=? AND chapter=? AND verse=?',(module_id,book,ch,verse)).fetchone()
            if row is None:raise ValueError(f'{book} {ch},{verse}: Vers fehlt im Textmodul.')
            original=normalize_surface(row['text'])
            annotated=normalize_surface(''.join(w[1] for w in words))
            if original!=annotated:
                raise ValueError(f'{book} {ch},{verse}: Wortfolge stimmt nicht mit dem Bibeltext überein (einschl. Akzenten/Vokalzeichen).')
            prepared.append((book,ch,verse,words))
        for book,ch,verse,words in prepared:
            db.execute('DELETE FROM tokens WHERE module_id=? AND book=? AND chapter=? AND verse=?',(module_id,book,ch,verse))
            db.executemany('INSERT INTO tokens(module_id,book,chapter,verse,position,surface,lemma,morph,strong) VALUES(?,?,?,?,?,?,?,?,?)',
                           [(module_id,book,ch,verse,*w) for w in words])
    return {'annotated_verses':len(groups),'tokens':sum(len(x) for x in groups.values())}

def chapter_tokens(book,chapter):
    with connect() as db:
        rows=db.execute("""SELECT t.module_id,t.book,t.chapter,t.verse,t.position,t.surface,t.lemma,t.morph,t.strong
            FROM tokens t JOIN modules m ON m.id=t.module_id
            WHERE t.book=? AND t.chapter=? AND m.language IN ('grc','he')
            ORDER BY t.module_id,t.verse,t.position""",(book,chapter)).fetchall()
    return [dict(x) for x in rows]

def get_word(module_id,book,chapter,verse,position):
    with connect() as db:
        row=db.execute("""SELECT t.*,m.title AS module_title,m.language,m.provenance,m.license
            FROM tokens t JOIN modules m ON m.id=t.module_id
            WHERE t.module_id=? AND t.book=? AND t.chapter=? AND t.verse=? AND t.position=?""",
            (module_id,book,chapter,verse,position)).fetchone()
    return dict(row) if row else None

def lemma_concordance(module_id, lemma, limit=100):
    if not lemma or len(lemma)>200:raise ValueError('Lemma fehlt oder ist zu lang.')
    with connect() as db:
        rows=db.execute("""SELECT t.book,t.chapter,t.verse,t.position,t.surface,t.lemma,t.morph,v.text
            FROM tokens t JOIN verses v ON (v.module_id=t.module_id AND v.book=t.book AND v.chapter=t.chapter AND v.verse=t.verse)
            WHERE t.module_id=? AND t.lemma=? ORDER BY t.book,t.chapter,t.verse,t.position LIMIT ?""",(module_id,lemma,limit)).fetchall()
    return [dict(x) for x in rows]


def lemma_concordance_page(module_id, lemma, limit=50, offset=0,
                            sort_by='reference', direction='asc'):
    """Paginated results sorted across the WHOLE edition before LIMIT.

    Reference order is biblical canon, not lexicographic book abbreviations.
    Sorting by word form uses SQLite text collation, with canonical reference
    order as a deterministic tie-breaker.
    """
    if not lemma or len(lemma)>200 or not (1<=limit<=100) or not (0<=offset<=1_000_000):
        raise ValueError('Ungültiges Lemma oder Seitenlimit.')
    if sort_by not in ('reference', 'surface') or direction not in ('asc', 'desc'):
        raise ValueError('Unbekannte Sortierung.')
    book_cases=' '.join(f"WHEN '{record[0]}' THEN {index}" for index,record in enumerate(BOOKS))
    book_sort=f'(CASE t.book {book_cases} ELSE 999 END)'
    ref_order=f'{book_sort} ASC,t.chapter ASC,t.verse ASC,t.position ASC'
    if sort_by=='reference':
        sort_sql=ref_order if direction=='asc' else f'{book_sort} DESC,t.chapter DESC,t.verse DESC,t.position DESC'
    else:
        # Deterministic order even when two tokens have identical spellings.
        sort_sql=f't.surface COLLATE NOCASE {direction.upper()},{ref_order}'
    with connect() as db:
        total=db.execute('SELECT COUNT(*) FROM tokens WHERE module_id=? AND lemma=?',
                         (module_id,lemma)).fetchone()[0]
        rows=db.execute(f"""SELECT t.book,t.chapter,t.verse,t.position,t.surface,t.lemma,t.morph,v.text
            FROM tokens t JOIN verses v ON (v.module_id=t.module_id AND v.book=t.book AND v.chapter=t.chapter AND v.verse=t.verse)
            WHERE t.module_id=? AND t.lemma=?
            ORDER BY {sort_sql} LIMIT ? OFFSET ?""",
            (module_id,lemma,limit,offset)).fetchall()
    return {'module_id':module_id,'lemma':lemma,'total':total,'limit':limit,'offset':offset,
            'sort_by':sort_by,'direction':direction,'results':[dict(x) for x in rows]}
