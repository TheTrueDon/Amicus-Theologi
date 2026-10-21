"""Amicus Theologi – offline-first study API, local loopback only."""
from contextlib import asynccontextmanager
import os
import tempfile
from starlette.background import BackgroundTask
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Literal, Any
import re
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from .database import APP_VERSION, data_dir, init_db, get_settings, set_settings, connect, factory_reset
from . import maintenance
from .annotation_audit import audit_annotations
from .library import BOOKS, NAMES, parse_reference, installed, chapter_view, chapter_refs, neighbor, read_import, install_module
from .search import search_verses
from .advanced_search import advanced_search
from .query_builder import query_search
from .source_import import install_scientific, download_source, MAX_UPLOAD
from .lexicon import read_lexicon, install_lexicon, installed_lexica, lookup, remove_lexicon
from .morphology import parse_annotation_file, import_annotations, chapter_tokens, get_word, lemma_concordance, lemma_concordance_page, lemma_forms_page
from .catalog import catalog_list, install_catalog_item
from .bible_catalog import bible_catalog, install_bible_from_catalog
from .saved_searches import list_saved_searches, create_saved_search, delete_saved_search
from . import sources
from . import initial_install
ROOT=Path(__file__).resolve().parent.parent; WEB=ROOT/'frontend'
@asynccontextmanager
async def lifespan(app: FastAPI):
 maintenance.apply_staged_restore()
 maintenance.automatic_upgrade_backup()
 init_db()
 maintenance.record_release_version()
 yield
app=FastAPI(title='Amicus Theologi',version=APP_VERSION,docs_url=None,redoc_url=None,lifespan=lifespan)
app.mount('/assets',StaticFiles(directory=str(WEB)),name='assets')

@app.middleware('http')
async def local_only_and_guard_writes(request: Request, call_next):
    """Prevent DNS rebinding and cross-origin POSTs against local study data."""
    host = request.headers.get('host','').split(':',1)[0].lower()
    if host not in ('127.0.0.1','localhost','testserver'):
        return JSONResponse({'detail':'Nur lokale Zugriffe sind zulässig.'},status_code=403)
    if request.url.path.startswith('/api/') and request.method not in ('GET','HEAD','OPTIONS'):
        origin = request.headers.get('origin','')
        actual_host = request.headers.get('host','')
        fetch_site = request.headers.get('sec-fetch-site','')
        if (origin and origin != 'http://' + actual_host) or fetch_site == 'cross-site':
            return JSONResponse({'detail':'Schreibzugriff nur aus Amicus Theologi selbst.'},status_code=403)
    if maintenance.pending_restore() and request.url.path.startswith('/api/') and request.url.path not in ('/api/status','/api/diagnostics','/api/backup/restore/cancel'):
        return JSONResponse({'detail':'Eine Wiederherstellung ist vorbereitet. Bitte Amicus Theologi beenden und neu starten.'},status_code=409)
    response = await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='no-referrer'
    return response
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
 welcome_completed:bool|None=None
 display_module_ids:list[str]|None=Field(default=None,max_length=150)
 display_module_order:list[str]|None=Field(default=None,max_length=150)
 text_layout:Literal['verse','edition']|None=None
class SavedSearchPayload(BaseModel):
 model_config=ConfigDict(extra='forbid')
 name:str=Field(min_length=1,max_length=120)
 criteria:dict[str,Any]
class QuerySearchPayload(BaseModel):
 model_config=ConfigDict(extra='forbid')
 criteria:dict[str,Any]
 limit:int=Field(default=50,ge=1,le=100)
 offset:int=Field(default=0,ge=0,le=100000)
@app.get('/')
def home():return FileResponse(WEB/'index.html')
@app.get('/quellenstudium', include_in_schema=False)
def source_workspace():return FileResponse(WEB/'sources.html')
@app.get('/ANLEITUNG.html', include_in_schema=False)
def help_manual():return FileResponse(ROOT/'ANLEITUNG.html', media_type='text/html')
@app.get('/ANLEITUNG.css', include_in_schema=False)
def help_styles():return FileResponse(ROOT/'ANLEITUNG.css', media_type='text/css')
@app.get('/ANLEITUNG.js', include_in_schema=False)
def help_script():return FileResponse(ROOT/'ANLEITUNG.js', media_type='application/javascript')
@app.get('/api/status')
def status():return {'name':'Amicus Theologi','version':APP_VERSION,'offline':True,'installed_modules':len(installed()),'mode':'local','pending_restore':maintenance.pending_restore()}
@app.get('/api/settings')
def settings():return get_settings()
@app.patch('/api/settings')
def patch_settings(change:SettingsUpdate):
 data=change.model_dump(exclude_unset=True)
 if any(v is None for v in data.values()):raise HTTPException(422,'Leere Einstellungen sind nicht erlaubt.')
 if 'active_reference' in data:
  try:parse_reference(data['active_reference'])
  except ValueError as e:raise HTTPException(422,str(e))
 for key in ('display_module_ids', 'display_module_order'):
  if key in data:
   allowed={m['id'] for m in installed()}
   if key=='display_module_ids':allowed.add('*')
   if any(i not in allowed for i in data[key]) or len(set(data[key]))!=len(data[key]):
    raise HTTPException(422,'Auswahlliste enthält unbekannte oder doppelte Module.')
 return set_settings(data)
@app.get('/api/books')
def books():return [{'id':b[0],'name':b[1]} for b in BOOKS]
@app.get('/api/saved-searches')
def saved_searches_list():return list_saved_searches()
@app.post('/api/saved-searches',status_code=201)
def saved_searches_create(payload:SavedSearchPayload):
 try:return create_saved_search(payload.name,payload.criteria)
 except ValueError as e:raise HTTPException(422,str(e))
@app.delete('/api/saved-searches/{search_id}')
def saved_searches_delete(search_id:int):
 if not delete_saved_search(search_id):raise HTTPException(404,'Gespeicherte Suche nicht gefunden.')
 return {'deleted':search_id}
@app.get('/api/modules')
def modules():return installed()
@app.get('/api/bible-catalog')
def available_bible_editions():
 return bible_catalog()
@app.post('/api/bible-catalog/{edition_id}/install')
def install_bible_edition(edition_id:str):
 try:return install_bible_from_catalog(edition_id)
 except ValueError as exc:raise HTTPException(422,str(exc))

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
@app.get('/api/modules/{module_id}/annotation-audit')
def module_annotation_audit(module_id:str):
 if not re.fullmatch(r'[a-zA-Z0-9_-]{2,48}',module_id):
  raise HTTPException(422,'Ungültige Modul-ID.')
 try:return audit_annotations(module_id)
 except ValueError as e:raise HTTPException(422,str(e))
@app.get('/api/search')
def search(q:str, module_id:str|None=None, book:str|None=None, mode:Literal['all','any','phrase']='all', limit:int=50,offset:int=0):
 try:return search_verses(q,module_id,book,mode,limit,offset)
 except ValueError as e:raise HTTPException(422,str(e))
@app.get('/api/info')
def info():return {'message':'Morphologische und positionsbezogene Suche in importierten Annotationen.','data_dir':str(data_dir())}

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
def morphology_lemma(module_id:str,lemma:str,limit:int=50,offset:int=0,sort_by:Literal['reference','surface']='reference',direction:Literal['asc','desc']='asc'):
 if not re.fullmatch(r'[a-zA-Z0-9_-]{2,48}',module_id):
  raise HTTPException(422,'Ungültige Modul-ID.')
 try:return lemma_concordance_page(module_id,lemma,limit,offset,sort_by,direction)
 except ValueError as e:raise HTTPException(422,str(e))

@app.get('/api/morphology/forms')
def morphology_forms(module_id:str,lemma:str,limit:int=50,offset:int=0):
 if not re.fullmatch(r'[a-zA-Z0-9_-]{2,48}',module_id):
  raise HTTPException(422,'Ungültige Modul-ID.')
 try:return lemma_forms_page(module_id,lemma,limit,offset)
 except ValueError as e:raise HTTPException(422,str(e))

@app.get('/api/morphology/preview')
def morphology_preview(module_id:str,book:str,chapter:int,verse:int,position:int):
 """Short, source-based hover preview. Never invent a translation or grammar."""
 if not re.fullmatch(r'[a-zA-Z0-9_-]{2,48}',module_id) or book not in NAMES or not(1<=chapter<=200 and 1<=verse<=200 and 1<=position<=500):
  raise HTTPException(422,'Ungültiger Wortverweis.')
 word=get_word(module_id,book,chapter,verse,position)
 if word is None:raise HTTPException(404,'Zu diesem Wort liegen keine Annotationen vor.')
 from .morph_display import decode
 from .lexical_text import best_gloss, gloss_priority
 from .hebrew_display import explain_word
 grammar=decode(word['morph'],word['language'])
 if word['language']=='he':
  reading=explain_word(word)
  return {'surface':word['surface'],'lemma':word['lemma'],'strong':word['strong'],
          'morph':word['morph'],'grammar':grammar,**reading}
 entries=lookup(word['language'],word['lemma'],word['strong'] or '')
 from .lexicon import clean_key
 entries.sort(key=lambda entry: (clean_key(entry['lemma']) != clean_key(word['lemma']), gloss_priority(entry)))
 gloss=''; source=''
 for entry in entries:
  candidate=best_gloss(entry)
  if candidate:
   gloss=candidate[:180];source=entry['title'];break
 return {'surface':word['surface'],'lemma':word['lemma'],'display_lemma':word['lemma'],
         'strong':word['strong'],'morph':word['morph'],'grammar':grammar,
         'gloss':gloss,'gloss_source':source}

@app.get('/api/lexica')
def lexica():return installed_lexica()

@app.get('/api/lexicon/lookup')
def lexicon_lookup(language:Literal['la','grc','he'],lemma:str='',strong:str=''):
 try:
  from .lexical_text import best_gloss
  if language=='he':
   from .hebrew_display import strong_for_lemma
   strong=strong_for_lemma({'lemma':lemma,'strong':strong}) or strong
  rows=lookup(language,lemma,strong)
  return {'language':language,'lemma':lemma,'strong':strong,
          'results':[{**entry, 'display_gloss':best_gloss(entry)} for entry in rows]}
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

@app.post('/api/search/query')
def structured_morphological_search(payload:QuerySearchPayload):
 try:return query_search(payload.criteria,limit=payload.limit,offset=payload.offset)
 except ValueError as e:raise HTTPException(422,str(e))

@app.post('/api/scientific/import')
async def scientific_import(source:Literal['step','oshb','sword']=Form(...),corpus:str=Form(''),file:UploadFile=File(...)):
 try:
  raw=await file.read(MAX_UPLOAD+1)
  return install_scientific(source,raw,corpus)
 except ValueError as e:raise HTTPException(422,str(e))

@app.post('/api/scientific/download')
def scientific_download(source:Literal['step','oshb'],corpus:str=''):
 try:return install_scientific(source,download_source(source),corpus)
 except ValueError as e:raise HTTPException(422,str(e))


@app.get('/api/catalog')
def available_catalog():return catalog_list()

@app.post('/api/catalog/{item}/install')
def catalog_install(item:str):
 try:return install_catalog_item(item)
 except ValueError as e:raise HTTPException(422,str(e))

# Optional source-study window. Biblical references and their endpoints are unchanged.
@app.get('/api/sources/modules')
def sources_modules():
 return sources.modules()

@app.post('/api/sources/import')
async def sources_import(file:UploadFile=File(...),module_id:str=Form(...),title:str=Form(...),
 author:str=Form(...),language:Literal['la','grc','he']=Form(...),edition:str=Form(...),
 license_name:str=Form(...),provenance:str=Form(...),version:str=Form('1')):
 try:
  raw=await file.read(sources.MAX_FILE+1)
  return sources.install_source(module_id.strip(),title.strip(),author.strip(),language,
   edition.strip(),license_name.strip(),provenance.strip(),version.strip(),sources.read_source(raw))
 except ValueError as e:raise HTTPException(422,str(e))

@app.delete('/api/sources/modules/{module_id}')
def sources_remove(module_id:str):
 if not sources.remove_source(module_id):raise HTTPException(404,'Quelle nicht gefunden.')
 return {'deleted':module_id}

@app.get('/api/sources/sections')
def sources_sections(module_id:str):
 return sources.sections_for(module_id)

@app.get('/api/sources/passage')
def sources_passage(module_id:str,ref:str):
 try:return sources.passage(module_id,ref)
 except ValueError as e:raise HTTPException(404,str(e))

@app.get('/api/sources/search')
def sources_search(q:str='',module_id:str='',mode:Literal['all','any','phrase']='all',
 lemma:str='',surface:str='',morph:str='',limit:int=50,offset:int=0):
 try:return sources.search_sources(q,module_id,mode,lemma,surface,morph,limit,offset)
 except ValueError as e:raise HTTPException(422,str(e))

@app.get('/api/sources/word')
def sources_word(module_id:str,ref:str,position:int):
 try:return sources.word_analysis(module_id,ref,position)
 except ValueError as e:raise HTTPException(404,str(e))

@app.get('/api/sources/stats')
def sources_stats(module_id:str,lemma:str=''):
 return sources.stats(module_id,lemma)

@app.post('/api/sources/annotations/import')
async def sources_annotations(file:UploadFile=File(...),module_id:str=Form(...)):
 try:return sources.import_annotations(module_id,await file.read(sources.MAX_FILE+1))
 except ValueError as e:raise HTTPException(422,str(e))

@app.get('/api/sources/note')
def sources_get_note(module_id:str,ref:str):
 return sources.get_note(module_id,ref)

class SourceNoteUpdate(BaseModel):
 module_id:str=Field(max_length=48)
 ref:str=Field(max_length=160)
 content:str=Field(max_length=20000)

@app.put('/api/sources/note')
def sources_put_note(note:SourceNoteUpdate):
 try:return sources.save_note(note.module_id,note.ref,note.content)
 except ValueError as e:raise HTTPException(422,str(e))

@app.get('/api/sources/catalog')
def sources_catalog():
 return sources.catalog_list()

@app.post('/api/sources/catalog/{item}/install')
def sources_install_catalog(item:str):
 try:return sources.install_catalog(item)
 except ValueError as e:raise HTTPException(422,str(e))
 except (OSError, TimeoutError) as e:raise HTTPException(502,'Download nicht möglich: '+str(e))

@app.post('/api/sources/packages/install')
async def sources_install_package(file:UploadFile=File(...)):
 try:
  from .source_packages import install_package,MAX_PACKAGE
  raw=await file.read(MAX_PACKAGE+1)
  return install_package(raw)
 except ValueError as e:raise HTTPException(422,str(e))

@app.post('/api/initial-install/start')
def initial_install_start():
 try:return initial_install.start_installation()
 except (OSError, ValueError) as exc:raise HTTPException(500,'Quelleninstallation konnte nicht vorbereitet werden: '+str(exc))

@app.get('/api/initial-install/{job_id}')
def initial_install_get_status(job_id:str):
 if not re.fullmatch(r'[a-f0-9-]{36}',job_id):raise HTTPException(422,'Ungültige Installations-ID.')
 state=initial_install.installation_status(job_id)
 if state is None:raise HTTPException(404,'Installationsauftrag nicht gefunden. Bitte neu starten.')
 return state

# Version 1.0: self-check, portable complete backups, staged recovery and offline demo setup.
@app.get('/api/diagnostics')
def get_diagnostics():
    try: return maintenance.diagnostics()
    except Exception as exc: raise HTTPException(500, f'Diagnose konnte nicht ausgeführt werden: {exc}')

@app.get('/api/backup/download')
def backup_download():
    try: path = maintenance.make_backup()
    except ValueError as exc: raise HTTPException(422,str(exc))
    return FileResponse(path, media_type='application/zip',
                        filename='Amicus-Theologi-Sicherung.zip',
                        background=BackgroundTask(path.unlink, missing_ok=True))

@app.post('/api/backup/restore')
async def backup_restore(file:UploadFile=File(...)):
    # A staged restore intentionally requires manual app restart.
    fd, pathname = tempfile.mkstemp(prefix='amicus-upload-',suffix='.zip',dir=data_dir())
    os.close(fd)
    path = Path(pathname)
    try:
        received = 0
        with path.open('wb') as dest:
            while chunk := await file.read(1024*1024):
                received += len(chunk)
                if received > maintenance.MAX_ZIP_BYTES:
                    raise HTTPException(413,'Sicherungsarchiv ist zu groß.')
                dest.write(chunk)
        try: return maintenance.stage_restore(path)
        except ValueError as exc: raise HTTPException(422,str(exc))
    finally: path.unlink(missing_ok=True)

@app.post('/api/backup/restore/cancel')
def backup_restore_cancel():
    return maintenance.cancel_pending_restore()

@app.post('/api/demo/install')
def demo_install():
    try:return maintenance.install_demo_bundle()
    except ValueError as exc:raise HTTPException(422,str(exc))

class ResetRequest(BaseModel):
 confirmation:Literal['WERKSRESET']

@app.post('/api/factory-reset')
def reset_everything(payload:ResetRequest,request:Request):
 # The app is bound to loopback. Also require a same-origin browser request.
 origin=request.headers.get('origin','')
 host=request.headers.get('host','')
 if not (host.startswith(('127.0.0.1:','localhost:')) and origin == 'http://' + host):
  raise HTTPException(403,'Werksreset nur aus der lokalen Programmoberfläche erlaubt.')
 return factory_reset()

# Version 0.7: personal projects, notes and color highlights.
from . import studies
from fastapi.responses import JSONResponse

class ProjectPayload(BaseModel):
 title:str=Field(min_length=1,max_length=160)
 description:str=Field(default='',max_length=3000)
class NotePayload(BaseModel):
 book:str
 chapter:int
 verse:int
 content:str=Field(min_length=1,max_length=20000)
class NoteEdit(BaseModel):
 content:str=Field(min_length=1,max_length=20000)
class HighlightPayload(BaseModel):
 book:str
 chapter:int
 verse:int
 color:Literal['yellow','green','blue','pink','orange']|None=None

def study_error(e):
 raise HTTPException(422,str(e))

@app.get('/api/projects')
def projects_list():return studies.projects()
@app.post('/api/projects',status_code=201)
def projects_create(data:ProjectPayload):
 try:return studies.create_project(data.title,data.description)
 except ValueError as e:study_error(e)
@app.patch('/api/projects/{pid}')
def projects_update(pid:int,data:ProjectPayload):
 try:return studies.update_project(pid,data.title,data.description)
 except ValueError as e:study_error(e)
@app.delete('/api/projects/{pid}')
def projects_delete(pid:int):
 try:return studies.delete_project(pid)
 except ValueError as e:study_error(e)
@app.get('/api/projects/{pid}/annotations')
def projects_annotations(pid:int,book:str|None=None,chapter:int|None=None,verse:int|None=None):
 try:return studies.annotations(pid,book,chapter,verse)
 except ValueError as e:study_error(e)
@app.post('/api/projects/{pid}/notes',status_code=201)
def projects_add_note(pid:int,data:NotePayload):
 try:return studies.add_note(pid,data.book,data.chapter,data.verse,data.content)
 except ValueError as e:study_error(e)
@app.patch('/api/projects/{pid}/notes/{nid}')
def projects_edit_note(pid:int,nid:int,data:NoteEdit):
 try:return studies.edit_note(pid,nid,data.content)
 except ValueError as e:study_error(e)
@app.delete('/api/projects/{pid}/notes/{nid}')
def projects_delete_note(pid:int,nid:int):
 try:return studies.delete_note(pid,nid)
 except ValueError as e:study_error(e)
@app.put('/api/projects/{pid}/highlight')
def projects_highlight(pid:int,data:HighlightPayload):
 try:return studies.highlight(pid,data.book,data.chapter,data.verse,data.color)
 except ValueError as e:study_error(e)
@app.get('/api/projects/{pid}/export')
def projects_export(pid:int):
 try:return JSONResponse(studies.export_project(pid),headers={'Content-Disposition':f'attachment; filename="amicus-projekt-{pid}.json"'})
 except ValueError as e:study_error(e)

from .morph_display import decode as decode_morph
@app.get('/api/morphology/decode')
def morph_decode(morph:str,language:Literal['grc','he']):
 return decode_morph(morph,language)


# v0.8: edition comparison, synoptic passages and documented textual readings.
from . import textcriticism as tc
@app.get('/api/textcrit/compare')
def compare_editions(book:str,chapter:int,modules:str):
 try:return tc.compare(book,chapter,[m.strip() for m in modules.split(',') if m.strip()])
 except ValueError as e:raise HTTPException(422,str(e))
@app.get('/api/textcrit/synopsis')
def synoptic_index():return tc.synopsis_list()
@app.get('/api/textcrit/synopsis/{item_id}')
def synoptic_passage(item_id:int,module_id:str):
 try:return tc.synopsis_detail(item_id,module_id)
 except ValueError as e:raise HTTPException(422,str(e))
@app.get('/api/textcrit/variants')
def textual_readings(book:str,chapter:int,verse:int):
 try:return tc.variants_at(book,chapter,verse)
 except ValueError as e:raise HTTPException(422,str(e))
@app.get('/api/textcrit/collections')
def textual_collections():return tc.collections()
@app.post('/api/textcrit/variants/import')
async def import_textual_readings(collection:str=Form(...),file:UploadFile=File(...)):
 try:return tc.import_variants(collection,await file.read(5_000_001))
 except ValueError as e:raise HTTPException(422,str(e))
@app.delete('/api/textcrit/collections/{name}')
def delete_textual_collection(name:str):
 try:return tc.remove_collection(name)
 except ValueError as e:raise HTTPException(404,str(e))
