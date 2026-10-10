"""Amicus Theologi 0.3 – loopback-only API."""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal
import re
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from .database import APP_VERSION, data_dir, init_db, get_settings, set_settings, connect
from .library import BOOKS, NAMES, parse_reference, installed, chapter_view, chapter_refs, neighbor, read_import, install_module
from .search import search_verses
from .advanced_search import advanced_search
from .lexicon import read_lexicon, install_lexicon, installed_lexica, lookup, remove_lexicon
from .morphology import parse_annotation_file, import_annotations, chapter_tokens, get_word, lemma_concordance
ROOT=Path(__file__).resolve().parent.parent; WEB=ROOT/'frontend'
@asynccontextmanager
async def lifespan(app: FastAPI):
 init_db();yield
app=FastAPI(title='Amicus Theologi',version=APP_VERSION,docs_url=None,redoc_url=None,lifespan=lifespan)
app.mount('/assets',StaticFiles(directory=str(WEB)),name='assets')
class SettingsUpdate(BaseModel):
 model_config=ConfigDict(extra='forbid')
 theme:Literal['dark','light']|None=None
 font_size:int|None=Field(default=None,ge=12,le=28)
 search_width:int|None=Field(default=None,ge=17,le=40)
 analysis_width:int|None=Field(default=None,ge=17,le=40)
 active_reference:str|None=Field(default=None,max_length=64)
 show_greek:bool|None=None
 show_german:bool|None=None
 show_latin:bool|None=None
@app.get('/')
def home():return FileResponse(WEB/'index.html')
@app.get('/api/status')
def status():return {'name':'Amicus Theologi','version':APP_VERSION,'offline':True,'installed_modules':len(installed()),'mode':'local'}
@app.get('/api/settings')
def settings():return get_settings()
@app.patch('/api/settings')
def patch_settings(change:SettingsUpdate):
 data=change.model_dump(exclude_unset=True)
 if any(v is None for v in data.values()):raise HTTPException(422,'Leere Einstellungen sind nicht erlaubt.')
 if 'active_reference' in data:
  try:parse_reference(data['active_reference'])
  except ValueError as e:raise HTTPException(422,str(e))
 return set_settings(data)
@app.get('/api/books')
def books():return [{'id':b[0],'name':b[1]} for b in BOOKS]
@app.get('/api/modules')
def modules():return installed()
@app.get('/api/chapter')
def chapter(book:str,chapter:int=1):
 if book not in NAMES or not 1<=chapter<=200:raise HTTPException(422,'Ungültiges Bibelbuch oder Kapitel.')
 parts=chapter_view(book,chapter)
 return {'book':book,'book_name':NAMES[book],'chapter':chapter,'tokens':chapter_tokens(book,chapter),'modules':parts,'available_verses':chapter_refs(book,chapter),'previous':neighbor(book,chapter,-1),'next':neighbor(book,chapter,1)}
@app.get('/api/reference')
def reference(q:str):
 try:b,c,v=parse_reference(q)
 except ValueError as e:raise HTTPException(422,str(e))
 return {'book':b,'chapter':c,'verse':v,'label':f'{b} {c},{v}'}
@app.get('/api/verses')
def verses(book:str,chapter:int=1,verse:int=1):
 if book not in NAMES or not(1<=chapter<=200 and 1<=verse<=200):raise HTTPException(422,'Ungültige Referenz')
 with connect() as db:
  rows=db.execute('SELECT m.id,m.title,m.language,v.text FROM verses v JOIN modules m ON m.id=v.module_id WHERE v.book=? AND v.chapter=? AND v.verse=? ORDER BY m.title',(book,chapter,verse)).fetchall()
 return {'reference':f'{book} {chapter},{verse}','translations':[dict(r) for r in rows]}
@app.post('/api/modules/import')
async def import_module(file:UploadFile=File(...),module_id:str=Form(...),title:str=Form(...),language:str=Form(...),license_name:str=Form(...),provenance:str=Form(...),version:str=Form('1')):
 module_id=module_id.strip();title=title.strip();language=language.strip();license_name=license_name.strip();provenance=provenance.strip();version=version.strip()
 if not re.fullmatch(r'[a-zA-Z0-9_-]{2,48}',module_id):raise HTTPException(422,'Modul-ID: 2–48 Zeichen, nur Buchstaben, Zahlen, - und _.')
 if any(not v or len(v)>250 for v in (title,language,license_name,provenance,version)):raise HTTPException(422,'Alle Metadatenfelder müssen ausgefüllt werden (max. 250 Zeichen).')
 try:
  raw=await file.read(12_000_001);rows=read_import(raw)
  count=install_module(module_id,title,language,license_name,provenance,version,rows)
 except ValueError as e:raise HTTPException(422,str(e))
 return {'module_id':module_id,'verses':count}
@app.delete('/api/modules/{module_id}')
def delete_module(module_id:str):
 with connect() as db:
  cur=db.execute('DELETE FROM modules WHERE id=?',(module_id,))
  if not cur.rowcount:raise HTTPException(404,'Modul nicht gefunden.')
 return {'deleted':module_id}
@app.get('/api/search')
def search(q:str, module_id:str|None=None, book:str|None=None, mode:Literal['all','any','phrase']='all', limit:int=50,offset:int=0):
 try:return search_verses(q,module_id,book,mode,limit,offset)
 except ValueError as e:raise HTTPException(422,str(e))
@app.get('/api/info')
def info():return {'message':'Version 0.6: morphologische und positionsbezogene Suche nach importierten Annotationen.','data_dir':str(data_dir())}

@app.post('/api/morphology/import')
async def morphology_import(file:UploadFile=File(...),module_id:str=Form(...)):
 if not re.fullmatch(r'[a-zA-Z0-9_-]{2,48}',module_id):raise HTTPException(422,'Ungültige Modul-ID.')
 try:
  raw=await file.read(12_000_001)
  return import_annotations(module_id,parse_annotation_file(raw))
 except ValueError as e:raise HTTPException(422,str(e))

@app.get('/api/morphology/word')
def morphology_word(module_id:str,book:str,chapter:int,verse:int,position:int):
 if not re.fullmatch(r'[a-zA-Z0-9_-]{2,48}',module_id) or book not in NAMES or not(1<=chapter<=200 and 1<=verse<=200 and 1<=position<=500):
  raise HTTPException(422,'Ungültiger Wortverweis.')
 result=get_word(module_id,book,chapter,verse,position)
 if result is None:raise HTTPException(404,'Zu diesem Wort liegen keine Annotationen vor.')
 return result

@app.get('/api/morphology/lemma')
def morphology_lemma(module_id:str,lemma:str,limit:int=100):
 if not re.fullmatch(r'[a-zA-Z0-9_-]{2,48}',module_id) or not 1<=limit<=100:
  raise HTTPException(422,'Ungültige Abfrage.')
 try:return {'module_id':module_id,'lemma':lemma,'results':lemma_concordance(module_id,lemma,limit)}
 except ValueError as e:raise HTTPException(422,str(e))

@app.get('/api/lexica')
def lexica():return installed_lexica()

@app.get('/api/lexicon/lookup')
def lexicon_lookup(language:Literal['grc','he'],lemma:str='',strong:str=''):
 try:return {'language':language,'lemma':lemma,'strong':strong,'results':lookup(language,lemma,strong)}
 except ValueError as e:raise HTTPException(422,str(e))

@app.post('/api/lexica/import')
async def lexicon_import(file:UploadFile=File(...),module_id:str=Form(...),title:str=Form(...),language:str=Form(...),license_name:str=Form(...),provenance:str=Form(...),version:str=Form('1')):
 try:
  raw=await file.read(12_000_001)
  return install_lexicon(module_id.strip(),title.strip(),language.strip(),license_name.strip(),provenance.strip(),version.strip(),read_lexicon(raw))
 except ValueError as e:raise HTTPException(422,str(e))

@app.delete('/api/lexica/{module_id}')
def lexicon_delete(module_id:str):
 if not remove_lexicon(module_id):raise HTTPException(404,'Lexikon nicht gefunden.')
 return {'deleted':module_id}

@app.get('/api/search/advanced')
def morphological_search(module_id:str='',book:str='',lemma:str='',surface:str='',strong:str='',morph:str='',
                         second_lemma:str='',second_surface:str='',second_strong:str='',second_morph:str='',
                         distance:int=5,order:Literal['any','before','after']='any',limit:int=50,offset:int=0):
 try:
  return advanced_search(module_id=module_id,book=book,lemma=lemma,surface=surface,strong=strong,morph=morph,
   second_lemma=second_lemma,second_surface=second_surface,second_strong=second_strong,
   second_morph=second_morph,distance=distance,order=order,limit=limit,offset=offset)
 except ValueError as e: raise HTTPException(422,str(e))
