"""FTS5 full-text retrieval with an intentionally small documented query language.

No user-provided SQL or raw FTS expression is executed. Query tokens are quoted.
Morphological queries require annotated texts and are reserved for v0.4+.
"""
import re
import sqlite3
from .database import connect
from .library import NAMES, BOOKS

MAX_RESULTS = 100
MAX_QUERY = 180


def normalize_query(raw: str, mode: str = 'all'):
    raw = raw.strip()
    if not raw or len(raw) > MAX_QUERY:
        raise ValueError('Suchbegriff erforderlich (maximal 180 Zeichen).')
    # Small set of BibleWorks-inspired commands; these are Amicus commands, not BW compatibility.
    if raw.startswith('='):
        mode, raw = 'phrase', raw[1:].strip()
    elif raw.startswith('+'):
        mode, raw = 'all', raw[1:].strip()
    elif raw.startswith('?'):
        mode, raw = 'any', raw[1:].strip()
    if mode not in ('all', 'any', 'phrase'):
        raise ValueError('Unbekannter Suchmodus.')
    if not raw:
        raise ValueError('Suchbegriff fehlt.')
    words = re.findall(r'[^\W_]+(?:\*|\b)', raw, re.UNICODE)
    # The actual FTS expression is generated from word-only atoms; trailing * is permitted.
    tokens = []
    for item in words:
        prefix = item.endswith('*')
        word = item.rstrip('*')
        if not word:
            continue
        tokens.append('"' + word.replace('"', '') + '"' + ('*' if prefix else ''))
    if not tokens or len(tokens) > 16:
        raise ValueError('Bitte 1 bis 16 Suchwörter eingeben.')
    if mode == 'phrase':
        # Avoid treating punctuation / separators as operators.
        if any(t.endswith('*') for t in tokens):
            raise ValueError('Platzhalter * sind in der Phrasensuche nicht möglich.')
        expression = '"' + ' '.join(t[1:-1] for t in tokens) + '"'
    else:
        expression = (' OR ' if mode == 'any' else ' AND ').join(tokens)
    return expression, mode


def search_verses(query, module_id=None, book=None, mode='all', limit=50, offset=0):
    expression, mode = normalize_query(query, mode)
    if module_id is not None and (len(module_id) > 48 or not re.fullmatch(r'[A-Za-z0-9_-]{2,48}', module_id)):
        raise ValueError('Ungültige Modul-ID.')
    if book and book not in NAMES:
        raise ValueError('Unbekanntes Bibelbuch.')
    if not (1 <= limit <= MAX_RESULTS and 0 <= offset <= 100000):
        raise ValueError('Ungültige Seitengröße oder Position.')
    where = ['verse_fts MATCH ?']
    args = [expression]
    if module_id:
        where.append('v.module_id=?')
        args.append(module_id)
    if book:
        where.append('v.book=?')
        args.append(book)
    w = ' AND '.join(where)
    # Rank by canonical order rather than relevance to provide predictable exegetical listings.
    order = {b[0]: i for i, b in enumerate(BOOKS)}
    cases = 'CASE v.book ' + ' '.join('WHEN ? THEN '+str(i) for i in range(len(order))) + ' ELSE 999 END'
    order_args = list(order)
    with connect() as db:
        try:
            total = db.execute('SELECT COUNT(*) FROM verse_fts JOIN verses v ON v.rowid=verse_fts.rowid WHERE '+w, args).fetchone()[0]
            rows = db.execute('''SELECT v.module_id,m.title AS module_title,m.language,v.book,v.chapter,v.verse,v.text
              FROM verse_fts JOIN verses v ON v.rowid=verse_fts.rowid
              JOIN modules m ON m.id=v.module_id
              WHERE '''+w+' ORDER BY '+cases+', v.chapter, v.verse, m.title LIMIT ? OFFSET ?',args+order_args+[limit,offset]).fetchall()
        except sqlite3.OperationalError as exc:
            raise ValueError('Suchausdruck nicht ausführbar: '+str(exc)) from exc
    return {'query':query,'mode':mode,'total':total,'limit':limit,'offset':offset,
            'results':[dict(row) for row in rows]}
