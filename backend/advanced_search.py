"""Structured and positional searches over imported morphological token annotations.

Exact lemma/surface/Strong matches, and morph substring matches (case-insensitive).
Position distance is the number of intervening tokens, not verse distance.
Only searches within a single module and verse. No AI or inferred morphology.
"""
from .database import connect
from .library import NAMES

MAX_RESULTS = 100

def advanced_search(*, module_id='', book='', lemma='', surface='', strong='', morph='',
                    second_lemma='', second_surface='', second_strong='', second_morph='',
                    distance=5, order='any', limit=50, offset=0):
    if any(len(x)>200 for x in (module_id,book,lemma,surface,strong,morph,second_lemma,second_surface,second_strong,second_morph)):
        raise ValueError('Suchkriterien zu lang (maximal 200 Zeichen).')
    if book and book not in NAMES: raise ValueError('Unbekanntes Bibelbuch.')
    if not 0<=distance<=100: raise ValueError('Wortabstand muss zwischen 0 und 100 liegen.')
    if order not in ('any','before','after'): raise ValueError('Ungültige Wortreihenfolge.')
    if not 1<=limit<=MAX_RESULTS or not 0<=offset<=100000: raise ValueError('Ungültige Seitengröße/Position.')
    first = {'lemma':lemma.strip(),'surface':surface.strip(),'strong':strong.strip(),'morph':morph.strip()}
    second = {'lemma':second_lemma.strip(),'surface':second_surface.strip(),'strong':second_strong.strip(),'morph':second_morph.strip()}
    if not any(first.values()): raise ValueError('Mindestens ein Kriterium für Wort 1 eingeben.')
    if not any(second.values()) and order!='any': raise ValueError('Wort 2 benötigt Kriterien, wenn eine Reihenfolge gewählt wird.')
    has_second=any(second.values())
    if not has_second and distance!=5: pass  # Abstand ohne zweites Wort ist bedeutungslos.
    args=[]
    filters=[]
    if module_id: filters.append('t.module_id=?');args.append(module_id)
    if book: filters.append('t.book=?');args.append(book)
    for col,value in first.items():
        if value:
            if col=='morph': filters.append('instr(lower(t.morph),lower(?))>0')
            else: filters.append(f't.{col}=? COLLATE NOCASE')
            args.append(value)
    join=''
    if has_second:
        join=' JOIN tokens s ON (s.module_id=t.module_id AND s.book=t.book AND s.chapter=t.chapter AND s.verse=t.verse) '
        filters.append('t.position<>s.position')
        # Number of words between positions, e.g. positions 1,3 means one intervening token.
        filters.append('abs(t.position-s.position)-1<=?');args.append(distance)
        if order=='before': filters.append('t.position<s.position')
        elif order=='after': filters.append('t.position>s.position')
        for col,value in second.items():
            if value:
                if col=='morph': filters.append('instr(lower(s.morph),lower(?))>0')
                else: filters.append(f's.{col}=? COLLATE NOCASE')
                args.append(value)
    where=' AND '.join(filters)
    root=("FROM tokens t " + join + "JOIN verses v ON (v.module_id=t.module_id AND v.book=t.book AND v.chapter=t.chapter AND v.verse=t.verse) "
          "JOIN modules m ON m.id=t.module_id WHERE "+where)
    with connect() as db:
        total=db.execute('SELECT COUNT(*) FROM (SELECT DISTINCT t.module_id,t.book,t.chapter,t.verse '+root+')',args).fetchone()[0]
        rows=db.execute('SELECT DISTINCT t.module_id,m.title AS module_title,m.language,t.book,t.chapter,t.verse,v.text '
                        +root+' ORDER BY t.module_id,t.book,t.chapter,t.verse LIMIT ? OFFSET ?',args+[limit,offset]).fetchall()
    return {'total':total,'limit':limit,'offset':offset,'results':[dict(r) for r in rows],
            'criteria':{'word1':first,'word2':second if has_second else None,'distance':distance,'order':order},
            'note':'Morphologie wird als Teilzeichenfolge des importierten Morphologiefeldes geprüft; keine automatische grammatische Interpretation.'}
