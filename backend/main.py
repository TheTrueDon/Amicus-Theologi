"""Biblewörks 0.1 local API. Loopback-only; no accounts or network dependencies."""
from contextlib import asynccontextmanager
from pathlib import Path
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from .database import APP_VERSION, data_dir, init_db, get_settings, set_settings, connect

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / 'frontend'

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title='Biblewörks', version=APP_VERSION, docs_url=None, redoc_url=None, lifespan=lifespan)
app.mount('/assets',StaticFiles(directory=str(WEB)),name='assets')

class SettingsUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    theme: Literal['dark','light'] | None = None
    font_size: int | None = Field(default=None,ge=12,le=28)
    search_width: int | None = Field(default=None,ge=17,le=40)
    analysis_width: int | None = Field(default=None,ge=17,le=40)
    active_reference: str | None = Field(default=None,max_length=64)
    show_greek: bool | None = None
    show_german: bool | None = None
    show_latin: bool | None = None

@app.get('/')
def home(): return FileResponse(WEB/'index.html')

@app.get('/api/status')
def status():
    with connect() as db:
        count=db.execute('SELECT COUNT(*) FROM modules').fetchone()[0]
    return {'name':'Biblewörks','version':APP_VERSION,'offline':True,'installed_modules':count,'mode':'local'}

@app.get('/api/settings')
def read_settings(): return get_settings()

@app.patch('/api/settings')
def update_settings(change:SettingsUpdate):
    patch=change.model_dump(exclude_unset=True)
    if any(v is None for v in patch.values()):
        raise HTTPException(422,'Einstellungen dürfen nicht null sein')
    if 'active_reference' in patch:
        patch['active_reference']=patch['active_reference'].strip()
        if not patch['active_reference']:raise HTTPException(422,'Leere Referenz')
    return set_settings(patch)

@app.get('/api/modules')
def modules():
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT * FROM modules ORDER BY title')]

@app.get('/api/verses')
def verses(book:str,chapter:int=1,verse:int=1):
    if not (1<=chapter<=200 and 1<=verse<=200): raise HTTPException(422,'Ungültige Versreferenz')
    with connect() as db:
        rows=db.execute("""SELECT m.id, m.title, m.language, v.text FROM verses v
             JOIN modules m ON m.id=v.module_id
             WHERE v.book=? AND v.chapter=? AND v.verse=? ORDER BY m.title""",(book,chapter,verse)).fetchall()
    return {'reference':f'{book} {chapter},{verse}','translations':[dict(r) for r in rows]}

@app.get('/api/info')
def info():
    return {'message':'Biblewörks 0.1: Entwicklungsgrundgerüst. Noch keine Bibeltexte installiert.','data_dir':str(data_dir()),'planned':['Moduleinfuhr','Bibeltextanzeige','Suchmaschine','Morphologie']}
