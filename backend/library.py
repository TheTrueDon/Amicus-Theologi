"""Importable, locally stored Bible editions. CSV/TSV intentionally explicit (no rights inference)."""
import csv
import io
import re
from .database import connect

BOOKS = [
 ('Gen','Genesis','1Mo','1 Mose','Gen'),('Ex','Exodus','2Mo','2 Mose'),('Lev','Levitikus','3Mo','3 Mose'),('Num','Numeri','4Mo','4 Mose'),('Dtn','Deuteronomium','5Mo','5 Mose'),
 ('Jos','Josua'),('Ri','Richter'),('Rut','Rut'),('1Sam','1 Samuel'),('2Sam','2 Samuel'),('1Kön','1 Könige'),('2Kön','2 Könige'),('1Chr','1 Chronik'),('2Chr','2 Chronik'),('Esra','Esra'),('Neh','Nehemia'),('Est','Ester'),('Hiob','Hiob','Job'),('Ps','Psalmen','Psalm'),('Spr','Sprüche'),('Pred','Prediger'),('Hld','Hohelied'),('Jes','Jesaja'),('Jer','Jeremia'),('Klgl','Klagelieder'),('Hes','Hesekiel','Ez'),('Dan','Daniel'),('Hos','Hosea'),('Joel','Joel'),('Am','Amos'),('Obd','Obadja'),('Jona','Jona'),('Mi','Micha'),('Nah','Nahum'),('Hab','Habakuk'),('Zef','Zefanja'),('Hag','Haggai'),('Sach','Sacharja'),('Mal','Maleachi'),
 ('Mt','Matthäus','Matt'),('Mk','Markus','Mark'),('Lk','Lukas','Luk'),('Joh','Johannes','John'),('Apg','Apostelgeschichte','Acts'),('Röm','Römer','Rom'),('1Kor','1 Korinther'),('2Kor','2 Korinther'),('Gal','Galater'),('Eph','Epheser'),('Phil','Philipper'),('Kol','Kolosser'),('1Thess','1 Thessalonicher'),('2Thess','2 Thessalonicher'),('1Tim','1 Timotheus'),('2Tim','2 Timotheus'),('Tit','Titus'),('Phlm','Philemon'),('Hebr','Hebräer'),('Jak','Jakobus'),('1Petr','1 Petrus'),('2Petr','2 Petrus'),('1Joh','1 Johannes'),('2Joh','2 Johannes'),('3Joh','3 Johannes'),('Jud','Judas'),('Offb','Offenbarung','Rev')]

def norm(s): return re.sub(r'[^a-z0-9]','',s.casefold().replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('ß','ss'))
ALIASES={norm(a):x[0] for x in BOOKS for a in x}; NAMES={x[0]:x[1] for x in BOOKS}

def book_id(name): return ALIASES.get(norm(name))

def parse_reference(value):
 m=re.fullmatch(r'\s*(.+?)\s+(\d{1,3})(?:\s*[,.:]\s*(\d{1,3}))?\s*',value)
 if not m: raise ValueError('Bitte eine Stelle wie „Joh 1,1“ oder „Gen 1“ eingeben.')
 book=book_id(m.group(1));chapter=int(m.group(2));verse=int(m.group(3) or 1)
 if not book: raise ValueError('Unbekanntes Bibelbuch. Benutze z. B. „Joh“ oder „1 Mose“.')
 if not (1<=chapter<=200 and 1<=verse<=200):raise ValueError('Kapitel oder Vers außerhalb des gültigen Bereichs.')
 return book,chapter,verse

def read_import(raw):
 if len(raw)>12_000_000:raise ValueError('Die Datei darf höchstens 12 MB groß sein.')
 try:txt=raw.decode('utf-8-sig')
 except UnicodeDecodeError:raise ValueError('Die Datei muss UTF-8-kodiert sein.')
 dialect='\t' if txt[:3000].count('\t')>txt[:3000].count(',') else ','
 reader=csv.DictReader(io.StringIO(txt),delimiter=dialect)
 if not reader.fieldnames or not {'book','chapter','verse','text'}.issubset(set(reader.fieldnames)):
  raise ValueError('Erforderliche Spalten: book, chapter, verse, text (CSV oder TSV).')
 rows=[]; seen=set()
 for i,r in enumerate(reader,2):
  if i>200005:raise ValueError('Maximal 200.000 Verse pro Modul.')
  b=book_id(r.get('book','')); text=(r.get('text') or '').strip()
  try:c=int(r.get('chapter',''));v=int(r.get('verse',''))
  except (TypeError,ValueError):raise ValueError(f'Zeile {i}: Kapitel und Vers müssen ganze Zahlen sein.')
  if not b or not(1<=c<=200 and 1<=v<=200) or not text or len(text)>10000:raise ValueError(f'Zeile {i}: Buch, Referenz oder Text ungültig.')
  key=(b,c,v)
  if key in seen:raise ValueError(f'Zeile {i}: doppelte Stelle {b} {c},{v}.')
  seen.add(key);rows.append((b,c,v,text))
 if not rows:raise ValueError('Die Datei enthält keine Verse.')
 return rows

def install_module(module_id,title,language,license_name,provenance,version,rows):
 with connect() as db:
  if db.execute('SELECT 1 FROM modules WHERE id=?',(module_id,)).fetchone():raise ValueError('Diese Modul-ID ist bereits installiert. Bitte zuerst das alte Modul entfernen oder eine andere ID verwenden.')
  db.execute('INSERT INTO modules(id,title,language,kind,license,provenance,version) VALUES(?,?,?,?,?,?,?)',(module_id,title,language,'bible',license_name,provenance,version))
  db.executemany('INSERT INTO verses(module_id,book,chapter,verse,text) VALUES(?,?,?,?,?)',[(module_id,*row) for row in rows])
 return len(rows)

def installed():
 with connect() as db:
  return [dict(r) for r in db.execute('SELECT m.*, (SELECT COUNT(*) FROM verses v WHERE v.module_id=m.id) AS verse_count FROM modules m ORDER BY m.title')]

def chapter_view(book,chapter,chosen=None):
 with connect() as db:
  ids=[r[0] for r in db.execute('SELECT id FROM modules ORDER BY title')]
  if chosen is not None: ids=[i for i in ids if i in chosen]
  result=[]
  for mid in ids:
   m=db.execute('SELECT id,title,language,license,provenance FROM modules WHERE id=?',(mid,)).fetchone()
   verses=[dict(x) for x in db.execute('SELECT verse,text FROM verses WHERE module_id=? AND book=? AND chapter=? ORDER BY verse',(mid,book,chapter))]
   if verses:result.append({**dict(m),'verses':verses})
 return result

def chapter_refs(book,chapter):
 with connect() as db:
  v=db.execute('SELECT DISTINCT verse FROM verses WHERE book=? AND chapter=? ORDER BY verse',(book,chapter)).fetchall()
 return [x[0] for x in v]

def neighbor(book,chapter,direction):
 with connect() as db:
  refs=[(r['book'],r['chapter']) for r in db.execute('SELECT DISTINCT book,chapter FROM verses')]
 # Canonical order for the 66 standard books; other can be introduced by a later versification layer.
 order={b[0]:i for i,b in enumerate(BOOKS)}
 refs.sort(key=lambda x:(order.get(x[0],999),x[1]));here=(book,chapter)
 if here not in refs:return None
 idx=refs.index(here)+direction
 return refs[idx] if 0<=idx<len(refs) else None
