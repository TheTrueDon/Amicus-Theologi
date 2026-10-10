"""Installable curated corpus and STEPBible lexicon modules (no executing archive content)."""
import re
import io
import zipfile
from .database import connect
from .source_import import download_source, install_scientific, MAX_STEP_FILE
from .lexicon import install_lexicon, clean_key
from .lexical_text import best_gloss

SOURCE='https://github.com/STEPBible/STEPBible-Data'
CATALOG={
 'step-tagnt':dict(title='STEPBible · Griechisches NT (TAGNT)',kind='Korpus + Wortannotationen',language='grc',source='step',corpus='tagnt'),
 'step-tahot':dict(title='STEPBible · Hebräisches AT (TAHOT, experimentell)',kind='Korpus + Wortannotationen',language='he',source='step',corpus='tahot'),
 'oshb':dict(title='Open Scriptures · Hebräisches AT',kind='Korpus + Wortannotationen',language='he',source='oshb',corpus=''),
 'step-tbesg':dict(title='STEPBible · TBESG (griechisches Lexikon)',kind='Lexikon',language='grc',code='TBESG'),
 'step-tbesh':dict(title='STEPBible · TBESH (hebräisches Lexikon)',kind='Lexikon',language='he',code='TBESH'),
 'step-tflsj':dict(title='STEPBible · TFLSJ (griechisches LSJ-Lexikon)',kind='Lexikon',language='grc',code='TFLSJ'),
}

STRONG=re.compile(r'(?<![A-Za-z0-9])([GH])0*(\d{1,5})([a-zA-Z]?)')
def parse_step_lexicon(raw,code):
 """Conservative STEP tab-table parser; fail visibly if upstream schema changes."""
 if code not in ('TBESG','TBESH','TFLSJ'):raise ValueError('Unbekanntes Lexikon.')
 with zipfile.ZipFile(io.BytesIO(raw)) as archive:
  relevant=[x for x in archive.infolist() if '/lexicons/' in '/'+x.filename.lower() and x.filename.rsplit('/',1)[-1].upper().startswith(code) and x.filename.lower().endswith('.txt')]
  if not relevant:raise ValueError('STEPBible-Archiv enthält das ausgewählte Lexikon nicht.')
  if len(relevant)>5 or sum(x.file_size for x in relevant)>85_000_000 or any(x.file_size>MAX_STEP_FILE for x in relevant):raise ValueError('Lexikondaten überschreiten die sichere Importgröße.')
  records={}
  for info in sorted(relevant,key=lambda x:x.filename):
   if info.flag_bits & 1:raise ValueError('Verschlüsselte Lexikondaten werden nicht unterstützt.')
   with archive.open(info) as stream:
    data=stream.read(85_000_001)
   if len(data)>85_000_000:raise ValueError('Lexikondatei zu groß.')
   content=data.decode('utf-8-sig')
   header={}
   for rawline in content.splitlines():
    line=rawline.strip()
    if not line or line[0] in '#$/':continue
    cols=[v.strip() for v in rawline.split('\t')]
    if len(cols)<3:continue
    # STEPBible documents separate transliteration and Gloss columns.
    # Preserve the header positions when supplied; never guess that the
    # first post-lemma field is an English translation.
    if ('estrong' in cols[0].casefold() or 'extended strong' in cols[0].casefold()):
     header={re.sub(r'[^a-z]','',x.casefold()):i for i,x in enumerate(cols)}
     continue
    # STEPBible files use extended Strong IDs in the first column(s).
    m=STRONG.search(cols[0])
    if not m:continue
    prefix,num,suffix=m.groups()
    if prefix != ('H' if code=='TBESH' else 'G'):continue
    strong=prefix+str(int(num))
    # Prefer a real-script headword, never an English transliteration as the lemma.
    script=re.compile('[\u0590-\u05ff]' if prefix=='H' else '[\u0370-\u03ff\u1f00-\u1fff]')
    heads=[i for i,x in enumerate(cols[1:7],1) if script.search(x) and len(x)<180]
    if not heads:continue
    lemma=cols[heads[0]].split(' (',1)[0].strip()
    if not lemma:continue
    # Preserve the publisher's remaining structured text, not an invented definition.
    tail=[x for x in cols[heads[0]+1:] if x and x not in ('-', '–')]
    if not tail:continue
    definition=' · '.join(tail)[:8000]
    if not definition:continue
    key=(clean_key(lemma),strong)
    # Multiple dStrong subentries can share a plain Strong number. Keep unique keys only.
    if key in records:continue
    header_gloss=''
    for label in ('gloss','shortgloss','shortmeaning'):
     index=header.get(label)
     if index is not None and index<len(cols) and cols[index]:
      header_gloss=cols[index]
      break
    # Fallback also repairs the old STEPBible data layout, by skipping
    # transliteration/morph fields and selecting only a true meaning.
    safe_gloss=header_gloss or best_gloss({'module_id':'step-'+code.lower(),
        'gloss':tail[0], 'definition':definition})
    records[key]=(lemma,clean_key(lemma),strong,safe_gloss[:500],definition,info.filename.rsplit('/',1)[-1][:400])
    if len(records)>100000:raise ValueError('Zu viele Lexikoneinträge.')
  if len(records)<1:raise ValueError('Keine gültigen Lexikoneinträge erkannt. Das Originalformat muss geprüft werden; es wurden keine Daten gespeichert.')
  return list(records.values())

def catalog_list():
 with connect() as db:
  existing={r[0] for r in db.execute('SELECT id FROM modules')}
  existing_lex={r[0] for r in db.execute('SELECT id FROM lexicon_modules')}
 return [dict(id=k,**v,installed=k in (existing_lex if v['kind']=='Lexikon' else existing),license='CC BY 4.0' if k!='oshb' else 'CC BY 4.0 / WLC-Textlizenz siehe Quelle',provenance=SOURCE if k!='oshb' else 'https://github.com/openscriptures/morphhb') for k,v in CATALOG.items()]

def install_catalog_item(item):
 if item not in CATALOG:raise ValueError('Dieses Modul ist nicht im geprüften Katalog.')
 conf=CATALOG[item]
 with connect() as db:
  table='lexicon_modules' if conf['kind']=='Lexikon' else 'modules'
  if db.execute(f'SELECT 1 FROM {table} WHERE id=?',(item,)).fetchone():
   raise ValueError('Dieses Modul ist bereits installiert.')
 if conf['kind']!='Lexikon':
  return install_scientific(conf['source'],download_source(conf['source']),conf['corpus'],module_id=item)
 raw=download_source('step')
 entries=parse_step_lexicon(raw,conf['code'])
 return install_lexicon(item,conf['title'],conf['language'],'CC BY 4.0',SOURCE+' · '+conf['code'],'STEPBible-Daten, Online-Import',entries)
