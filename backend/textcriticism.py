"""Edition comparison, documented variants and curated synoptic reference groups.

No textual variant is inferred automatically from translation differences.
"""
import csv
import io
from .database import connect
from .library import NAMES

# Carefully selected passage references, not a claim of complete or verse-exact alignment.
SYNOPTIC = [
 ('Taufe Jesu', [('Mt',3,13,17),('Mk',1,9,11),('Lk',3,21,22)]),
 ('Versuchung Jesu', [('Mt',4,1,11),('Mk',1,12,13),('Lk',4,1,13)]),
 ('Berufung des Levi', [('Mt',9,9,13),('Mk',2,13,17),('Lk',5,27,32)]),
 ('Sturmstillung', [('Mt',8,23,27),('Mk',4,35,41),('Lk',8,22,25)]),
 ('Gleichnis vom Sämann', [('Mt',13,1,9),('Mk',4,1,9),('Lk',8,4,8)]),
 ('Speisung der Fünftausend', [('Mt',14,13,21),('Mk',6,30,44),('Lk',9,10,17)]),
 ('Verklärung Jesu', [('Mt',17,1,9),('Mk',9,2,10),('Lk',9,28,36)]),
 ('Einzug in Jerusalem', [('Mt',21,1,11),('Mk',11,1,11),('Lk',19,28,40)]),
 ('Gethsemane', [('Mt',26,36,46),('Mk',14,32,42),('Lk',22,39,46)]),
]

def compare(book, chapter, module_ids):
 if book not in NAMES or not 1<=chapter<=200:raise ValueError('Ungültige Bibelstelle.')
 if not 2<=len(module_ids)<=4 or len(set(module_ids))!=len(module_ids):raise ValueError('Bitte zwei bis vier unterschiedliche Ausgaben wählen.')
 with connect() as db:
  placeholders=','.join('?' for _ in module_ids)
  mods=db.execute(f'SELECT id,title,language,license,provenance FROM modules WHERE id IN ({placeholders})',module_ids).fetchall()
  if len(mods)!=len(module_ids):raise ValueError('Eine ausgewählte Textausgabe ist nicht installiert.')
  rows=db.execute(f'SELECT module_id,verse,text FROM verses WHERE book=? AND chapter=? AND module_id IN ({placeholders}) ORDER BY verse', (book,chapter,*module_ids)).fetchall()
 ordered={m['id']:dict(m) for m in mods}
 verses={}
 for r in rows:verses.setdefault(r['verse'],{})[r['module_id']]=r['text']
 return {'book':book,'chapter':chapter,'modules':[ordered[mid] for mid in module_ids],
         'rows':[{'verse':v,'texts':[verses[v].get(mid) for mid in module_ids]} for v in sorted(verses)],
         'notice':'Ausgabenunterschiede sind nicht automatisch textkritische Handschriftenvarianten.'}

def synopsis_list():
 return [{'id':i,'title':name,'references':[f'{b} {c},{a}–{z}' for b,c,a,z in refs]} for i,(name,refs) in enumerate(SYNOPTIC)]

def synopsis_detail(item_id,module_id):
 if not 0<=item_id<len(SYNOPTIC):raise ValueError('Unbekannter Synopsenabschnitt.')
 with connect() as db:
  mod=db.execute('SELECT id,title,language,license,provenance FROM modules WHERE id=?',(module_id,)).fetchone()
  if not mod:raise ValueError('Textausgabe nicht installiert.')
  name, refs=SYNOPTIC[item_id]
  parts=[]
  for book,chapter,start,end in refs:
   rows=db.execute('SELECT verse,text FROM verses WHERE module_id=? AND book=? AND chapter=? AND verse BETWEEN ? AND ? ORDER BY verse',(module_id,book,chapter,start,end)).fetchall()
   parts.append({'book':book,'chapter':chapter,'start':start,'end':end,'verses':[dict(r) for r in rows]})
  return {'title':name,'module':dict(mod),'columns':parts,'notice':'Thematisch ausgewählte Parallelperikopen, keine wort- oder versgenaue kritische Synopse.'}

def setup(db):
 db.execute('''CREATE TABLE IF NOT EXISTS textual_variants (
  id INTEGER PRIMARY KEY AUTOINCREMENT, collection TEXT NOT NULL,
  book TEXT NOT NULL, chapter INTEGER NOT NULL, verse INTEGER NOT NULL,
  reading TEXT NOT NULL, witness TEXT NOT NULL, source TEXT NOT NULL,
  license TEXT NOT NULL, notes TEXT NOT NULL DEFAULT ''
 )''')
 db.execute('CREATE INDEX IF NOT EXISTS idx_variants_ref ON textual_variants(book,chapter,verse)')

def parse_variants(raw):
 if len(raw)>5_000_000:raise ValueError('Maximal 5 MB pro Variantendatei.')
 try: text=raw.decode('utf-8-sig')
 except UnicodeDecodeError:raise ValueError('Datei muss UTF-8-kodiert sein.')
 sample=text[:4000]
 try: dialect=csv.Sniffer().sniff(sample,delimiters=',\t;')
 except csv.Error: dialect=csv.excel_tab if '\t' in text.splitlines()[0] else csv.excel
 reader=csv.DictReader(io.StringIO(text),dialect=dialect)
 required={'book','chapter','verse','reading','witness','source','license'}
 if not required.issubset(reader.fieldnames or []):raise ValueError('Spalten benötigt: book, chapter, verse, reading, witness, source, license; optional notes.')
 result=[]
 for row in reader:
  try:book=row['book'].strip();chapter=int(row['chapter']);verse=int(row['verse'])
  except (ValueError,AttributeError,TypeError):raise ValueError('Ungültige Bibelstellenangabe.')
  if book not in NAMES or not (1<=chapter<=200 and 1<=verse<=200):raise ValueError('Bibelstelle unbekannt oder ungültig.')
  fields=[(row.get(x) or '').strip() for x in ('reading','witness','source','license','notes')]
  if any(not x or len(x)>1000 for x in fields[:4]) or len(fields[4])>3000:raise ValueError('Lesart, Zeuge, Quelle und Lizenz müssen angegeben werden.')
  result.append((book,chapter,verse,*fields))
  if len(result)>15000:raise ValueError('Maximal 15.000 Lesarten je Datei.')
 if not result:raise ValueError('Keine Lesarten in Datei.')
 return result

def import_variants(collection,raw):
 collection=collection.strip()
 if not 2<=len(collection)<=150:raise ValueError('Name der Sammlung: 2–150 Zeichen.')
 rows=parse_variants(raw)
 with connect() as db:
  db.executemany('INSERT INTO textual_variants(collection,book,chapter,verse,reading,witness,source,license,notes) VALUES (?,?,?,?,?,?,?,?,?)',[(collection,*row) for row in rows])
 return {'collection':collection,'imported':len(rows)}

def variants_at(book,chapter,verse):
 if book not in NAMES or not (1<=chapter<=200 and 1<=verse<=200):raise ValueError('Ungültige Bibelstelle.')
 with connect() as db:
  return [dict(r) for r in db.execute('SELECT id,collection,reading,witness,source,license,notes FROM textual_variants WHERE book=? AND chapter=? AND verse=? ORDER BY collection,id',(book,chapter,verse))]

def collections():
 with connect() as db:return [dict(r) for r in db.execute('SELECT collection,COUNT(*) AS count FROM textual_variants GROUP BY collection ORDER BY collection')]

def remove_collection(name):
 with connect() as db:
  cur=db.execute('DELETE FROM textual_variants WHERE collection=?',(name,))
  if not cur.rowcount:raise ValueError('Sammlung nicht gefunden.')
 return {'removed':name}
