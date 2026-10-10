"""Scientific corpus importers. Offline ZIP upload or explicitly requested downloads.
No repository code is executed. Imports are transactional and keep attribution.
"""
import io, re, zipfile, html, urllib.request
from collections import defaultdict
from xml.etree import ElementTree as ET
from .database import connect
from .library import book_id

MAX_UPLOAD=145_000_000
MAX_UNPACKED=280_000_000
MAX_FILES=2500
MAX_STEP_FILES=150
MAX_STEP_UNPACKED=350_000_000
MAX_STEP_FILE=130_000_000
STEP_CODES={'Mat':'Mt','Mrk':'Mk','Luk':'Lk','Jhn':'Joh','Act':'Apg','Rom':'Röm','1Co':'1Kor','2Co':'2Kor','Php':'Phil','Phm':'Phlm','Jas':'Jak','1Pe':'1Petr','2Pe':'2Petr','1Jn':'1Joh','2Jn':'2Joh','3Jn':'3Joh','Rev':'Offb','Gen':'Gen','Exo':'Ex','Lev':'Lev','Num':'Num','Deu':'Dtn','Jdg':'Ri','1Sa':'1Sam','2Sa':'2Sam','1Ki':'1Kön','2Ki':'2Kön','1Ch':'1Chr','2Ch':'2Chr','Ezr':'Esra','Job':'Hiob','Psa':'Ps','Pro':'Spr','Ecc':'Pred','Sng':'Hld','Isa':'Jes','Lam':'Klgl','Ezk':'Hes','Jol':'Joel','Oba':'Obd','Jon':'Jona','Nam':'Nah','Zep':'Zef','Zec':'Sach','Mal':'Mal','Heb':'Hebr','Jud':'Jud'}
for code in ('Jos','Rut','Neh','Est','Jer','Dan','Hos','Amo','Mic','Hab','Hag','Gal','Eph','Col','1Th','2Th','1Ti','2Ti','Tit'):
 STEP_CODES.setdefault(code,{'1Th':'1Thess','2Th':'2Thess','1Ti':'1Tim','2Ti':'2Tim'}.get(code,code))
REF=re.compile(r'(?<!\w)(?:\d\d_)?([1-3]?[A-Za-z]{2,3})\.(\d{1,3})\.(\d{1,3})(?:#\d+)?')

def safe_archive(raw, source=None, corpus=None):
 if len(raw)>MAX_UPLOAD:raise ValueError('Die Datei ist zu groß (maximal 145 MB).')
 try:z=zipfile.ZipFile(io.BytesIO(raw))
 except zipfile.BadZipFile:raise ValueError('Bitte ein gültiges ZIP-Archiv auswählen.')
 infos=z.infolist()
 if source=='step':
  # The STEPBible GitHub archive includes dictionaries, tagged Bibles and historical
  # formats. Only the requested corpus is relevant. Do not reject the archive
  # merely because those unrelated files are numerous or large.
  selected=[x for x in infos if _step_target(x.filename,corpus)]
  if not selected:raise ValueError('Keine passenden TAGNT/TAHOT-Dateien im Archiv gefunden.')
  if (len(selected)>MAX_STEP_FILES or
      any(x.file_size>MAX_STEP_FILE for x in selected) or
      sum(x.file_size for x in selected)>MAX_STEP_UNPACKED):
   raise ValueError('Die ausgewählten STEPBible-Korpusdateien überschreiten die Sicherheitsgrenze.')
 else:
  if len(infos)>MAX_FILES or sum(x.file_size for x in infos)>MAX_UNPACKED:raise ValueError('Archiv enthält zu viele oder zu große Dateien.')
 if any(x.flag_bits & 1 for x in infos):raise ValueError('Verschlüsselte Archive werden nicht unterstützt.')
 return z

def _step_target(name, corpus):
 if corpus not in ('tagnt','tahot'):return False
 parts=name.replace('\\','/').split('/')
 # Exclude historical or duplicate editions; target canonical current datasets.
 if any(x.lower()=='older formats' for x in parts):return False
 return name.lower().endswith('.txt') and corpus.upper() in name.upper().split('/')[-1]

def _xml_name(t):return t.rsplit('}',1)[-1]
def parse_oshb(raw):
 """Open Scriptures wlc OSIS .xml files; texts and annotations are imported together."""
 with safe_archive(raw) as z:
  names=[n for n in z.namelist() if re.search(r'(?:^|/)wlc/[^/]+\.xml$',n,re.I)]
  if not names:raise ValueError('Keine OSHB-Dateien gefunden. Erwartet wird ein GitHub-Quellarchiv mit Ordner wlc/*.xml.')
  verses={};tokens=[]
  for name in names:
   with z.open(name) as f:
    try:tree=ET.parse(f)
    except ET.ParseError as e:raise ValueError(f'OSIS-XML fehlerhaft ({name}): {e}')
   for verse in tree.iter():
    if _xml_name(verse.tag)!='verse':continue
    ref=verse.attrib.get('osisID','').split('!')[0]
    m=re.match(r'^([A-Za-z0-9]+)\.(\d+)\.(\d+)$',ref)
    if not m:continue
    book=STEP_CODES.get(m[1],book_id(m[1]));ch=int(m[2]);v=int(m[3])
    if not book or not(1<=ch<=200 and 1<=v<=200):continue
    words=[]
    for w in verse.iter():
     if _xml_name(w.tag)!='w':continue
     surface=''.join(w.itertext()).strip()
     if not surface:continue
     lemma=w.attrib.get('lemma','')[:180];morph=w.attrib.get('morph','')[:180]
     strongmatch=re.search(r'(?:^|[/\s])(?:H)?(\d{1,5})',lemma)
     strong='H'+str(int(strongmatch[1])) if strongmatch else ''
     words.append((surface,lemma or '–',morph or 'unannotiert',strong))
    if not words:continue
    key=(book,ch,v)
    if key in verses:continue
    verses[key]=' '.join(w[0] for w in words)
    for i,w in enumerate(words,1):tokens.append((*key,i,*w))
  if not verses:raise ValueError('OSHB-Archiv enthält keine lesbaren Verse.')
  return verses,tokens,'he'

def parse_step(raw, corpus):
 """STEP TAB-delimited TAGNT/TAHOT. Preserve raw morphology tags.
 Only core textual tagged rows. For TAGNT explicitly retain SBL edition words.
 """
 with safe_archive(raw,source='step',corpus=corpus) as z:
  names=[n for n in z.namelist() if _step_target(n,corpus)]
  if not names:raise ValueError('Keine passenden TAGNT/TAHOT-Textdateien im STEPBible-Archiv gefunden.')
  verses=defaultdict(list)
  for name in names:
   # Stream selected text files instead of unpacking hundreds of MB at once.
   # Never replace invalid UTF-8 silently in scientific text data.
   with z.open(name) as binary:
    reader=io.TextIOWrapper(binary,encoding='utf-8-sig',errors='strict')
    for line in reader:
     line=line.rstrip('\r\n')
     if not line or line.startswith(('#','//')):continue
     cols=line.split('\t')
     lower=[c.lower().strip() for c in cols]
     if any('word & type' in x for x in lower) or ('greek' in lower and 'editions' in lower) or ('hebrew' in lower and 'english' in lower):
      continue
     refmatch=REF.search(cols[0]) if cols else None
     if not refmatch:continue
     cod,ch,v=refmatch.groups();book=STEP_CODES.get(cod,book_id(cod))
     if not book or int(ch)>200 or int(v)>200:continue
     key=(book,int(ch),int(v))
     if corpus=='tagnt':
      editions=' '.join(cols[5:]) if len(cols)>5 else ''
      if not re.search(r'(?<![A-Za-z])SBL(?![A-Za-z])',editions):continue
      surface=cols[1].split(' (')[0].strip() if len(cols)>1 else ''
      dstrong=cols[3].strip() if len(cols)>3 else ''
      morphology=dstrong.split('=',1)[-1] if '=' in dstrong else 'unannotiert'
      strong=re.search(r'G0*(\d+)',dstrong)
      strong='G'+str(int(strong[1])) if strong else ''
      lemma=cols[4].split('=',1)[0].strip() if len(cols)>4 else ''
     else:
      surface=cols[1].split(' (')[0].strip() if len(cols)>1 else ''
      if not re.search(r'[\u0590-\u05ff]',surface):continue
      lemma=cols[4].split('=',1)[0].strip() if len(cols)>4 else ''
      morph=next((x for x in cols[2:7] if re.search(r'\bH[A-Z][A-Za-z0-9/]+',x)), '')
      morphology=morph or 'unannotiert'
      sm=re.search(r'H0*(\d+)', ' '.join(cols[2:7]));strong='H'+str(int(sm[1])) if sm else ''
     if not surface or len(surface)>150:continue
     verses[key].append((surface,lemma or '–',morphology[:180],strong))
     if len(verses)>200000:raise ValueError('Zu viele Verse im Korpus. Die wissenschaftlichen Daten wurden nicht verändert.')
  if not verses:raise ValueError('Keine kompatiblen Wortzeilen erkannt. STEPBible hat ggf. das Tabellenformat geändert; bitte Datei und Format prüfen.')
  output={k:' '.join(w[0] for w in ws) for k,ws in verses.items()}
  tokens=[(*k,i,*w) for k,ws in verses.items() for i,w in enumerate(ws,1)]
  return output,tokens,'grc' if corpus=='tagnt' else 'he'

SWORD_BOOKS={
 'Gen':'Genesis','Ex':'Exodus','Lev':'Leviticus','Num':'Numbers','Dtn':'Deuteronomy','Jos':'Joshua','Ri':'Judges','Rut':'Ruth','1Sam':'I Samuel','2Sam':'II Samuel','1Kön':'I Kings','2Kön':'II Kings','1Chr':'I Chronicles','2Chr':'II Chronicles','Esra':'Ezra','Neh':'Nehemiah','Est':'Esther','Hiob':'Job','Ps':'Psalms','Spr':'Proverbs','Pred':'Ecclesiastes','Hld':'Song of Solomon','Jes':'Isaiah','Jer':'Jeremiah','Klgl':'Lamentations','Hes':'Ezekiel','Dan':'Daniel','Hos':'Hosea','Joel':'Joel','Am':'Amos','Obd':'Obadiah','Jona':'Jonah','Mi':'Micah','Nah':'Nahum','Hab':'Habakkuk','Zef':'Zephaniah','Hag':'Haggai','Sach':'Zechariah','Mal':'Malachi','Mt':'Matthew','Mk':'Mark','Lk':'Luke','Joh':'John','Apg':'Acts','Röm':'Romans','1Kor':'I Corinthians','2Kor':'II Corinthians','Gal':'Galatians','Eph':'Ephesians','Phil':'Philippians','Kol':'Colossians','1Thess':'I Thessalonians','2Thess':'II Thessalonians','1Tim':'I Timothy','2Tim':'II Timothy','Tit':'Titus','Phlm':'Philemon','Hebr':'Hebrews','Jak':'James','1Petr':'I Peter','2Petr':'II Peter','1Joh':'I John','2Joh':'II John','3Joh':'III John','Jud':'Jude','Offb':'Revelation'}

def parse_sword(raw, selected=None):
 try:from pysword.modules import SwordModules
 except ImportError:raise ValueError('Für SWORD fehlt die optionale Bibliothek „pysword“. Bitte „pip install pysword“ ausführen und neu starten.')
 with safe_archive(raw) as z:
  if not any('/mods.d/' in '/'+n for n in z.namelist()):raise ValueError('Kein SWORD-Modul gefunden (mods.d/*.conf fehlt).')
 # pysword accepts ZIP bytes only through a filesystem path; tempfile removed afterward.
 import tempfile,os
 with tempfile.NamedTemporaryFile(suffix='.zip',delete=False) as tmp:
  path=tmp.name;tmp.write(raw)
 try:
  sm=SwordModules(path);found=sm.parse_modules()
  if not found:raise ValueError('SWORD-Archiv enthält keine erkannten Textmodule.')
  ident=selected if selected in found else next(iter(found))
  bible=sm.get_bible_from_module(ident)
  verses={}
  for b,english in SWORD_BOOKS.items():
   for ch in range(1,151):
    found_ch=False
    for v in range(1,177):
     try:rawverse=bible.get(books=[english],chapters=[ch],verses=[v])
     except Exception:rawverse=''
     if isinstance(rawverse,(list,tuple)):rawverse=' '.join(map(str,rawverse))
     value=html.unescape(re.sub(r'<[^>]+>',' ',str(rawverse or '')))
     value=re.sub(r'\s+',' ',value).strip()
     if value and value!='None':verses[(b,ch,v)]=value;found_ch=True
     elif v>2:break
    if not found_ch:break
  if not verses:raise ValueError('SWORD-Modul erkannt, aber keine Verse extrahierbar.')
  return verses,[], 'other',ident
 finally:
  os.unlink(path)

def install_scientific(source, raw, corpus='', module_id=''):
 if source=='oshb':verses,tokens,language=parse_oshb(raw);id='oshb';name='Open Scriptures Hebrew Bible (WLC/OSHB)';lic='CC BY 4.0 (Morphologie), gemeinfreier WLC-Text';src='https://github.com/openscriptures/morphhb'
 elif source=='step':
  if corpus not in ('tagnt','tahot'):raise ValueError('Bitte TAGNT oder TAHOT wählen.')
  verses,tokens,language=parse_step(raw,corpus);id='step-'+corpus;name='STEP Bible '+corpus.upper();lic='CC BY 4.0';src='https://github.com/STEPBible/STEPBible-Data'
 elif source=='sword':
  verses,tokens,language,ident=parse_sword(raw);id='sword-'+re.sub('[^a-zA-Z0-9_-]','-',ident)[:35];name='SWORD '+ident;lic='Lizenz des Originalmoduls separat prüfen';src='CrossWire / lokal geliefertes SWORD-Modul'
 else:raise ValueError('Unbekannte Datenquelle.')
 if len(verses)>200000 or len(tokens)>1500000:raise ValueError('Datensatz übersteigt die lokalen Importgrenzen.')
 if module_id:
  if not re.fullmatch(r'[A-Za-z0-9_-]{2,48}',module_id):raise ValueError('Ungültige Modul-ID.')
  id=module_id
 with connect() as db:
  if db.execute('SELECT 1 FROM modules WHERE id=?',(id,)).fetchone():raise ValueError('Dieses Modul ist bereits installiert. Bestehende Module werden nicht überschrieben.')
  db.execute('INSERT INTO modules(id,title,language,kind,license,provenance,version) VALUES(?,?,?,?,?,?,?)',(id,name,language,'bible',lic,src,'Import 0.6.3'))
  db.executemany('INSERT INTO verses(module_id,book,chapter,verse,text) VALUES(?,?,?,?,?)',[(id,*k,v) for k,v in verses.items()])
  if tokens:
   db.executemany('INSERT INTO tokens(module_id,book,chapter,verse,position,surface,lemma,morph,strong) VALUES(?,?,?,?,?,?,?,?,?)',[(id,*t) for t in tokens])
 return {'module_id':id,'verses':len(verses),'tokens':len(tokens),'source':src,'license':lic}

DOWNLOADS={'oshb':'https://github.com/openscriptures/morphhb/archive/refs/heads/master.zip','step':'https://github.com/STEPBible/STEPBible-Data/archive/refs/heads/master.zip'}
def download_source(source):
 url=DOWNLOADS.get(source)
 if not url:raise ValueError('Für diese Quelle ist nur der ZIP-Import verfügbar.')
 req=urllib.request.Request(url,headers={'User-Agent':'AmicusTheologi/0.6.3'})
 try:
  with urllib.request.urlopen(req,timeout=75) as response:
   pieces=[];size=0
   while True:
    piece=response.read(1024*1024)
    if not piece:break
    size+=len(piece)
    if size>MAX_UPLOAD:raise ValueError('Heruntergeladenes Archiv überschreitet 145 MB. Bitte die gewünschte Teildatei manuell importieren.')
    pieces.append(piece)
   return b''.join(pieces)
 except (OSError,TimeoutError) as e:raise ValueError(f'Download nicht möglich: {e}. Alternativ ZIP von der Projektwebsite herunterladen und hier auswählen.')
