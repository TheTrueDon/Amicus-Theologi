"""Local SQLite storage. No user data is ever written inside the application package."""
import json
import os
import sqlite3
from pathlib import Path

APP_VERSION = '0.1.0'
DEFAULT_SETTINGS = {
    'theme': 'dark', 'font_size': 17, 'search_width': 25,
    'analysis_width': 27, 'active_reference': 'Joh 1,1',
    'show_greek': True, 'show_german': True, 'show_latin': True,
}

def data_dir():
    if os.getenv('BIBLEWOERKS_DATA_DIR'):
        root = Path(os.environ['BIBLEWOERKS_DATA_DIR']).expanduser()
    elif os.name == 'nt':
        root = Path(os.getenv('LOCALAPPDATA', Path.home())) / 'Biblewoerks'
    else:
        root = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local/share')) / 'biblewoerks'
    root.mkdir(parents=True, exist_ok=True)
    return root

def connect():
    con = sqlite3.connect(data_dir() / 'biblewoerks.sqlite3', timeout=10)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con

def init_db():
    with connect() as db:
        db.executescript("""CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS modules (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, language TEXT NOT NULL,
            kind TEXT NOT NULL, license TEXT NOT NULL, provenance TEXT NOT NULL,
            version TEXT NOT NULL, installed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS verses (
            module_id TEXT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
            book TEXT NOT NULL, chapter INTEGER NOT NULL, verse INTEGER NOT NULL,
            text TEXT NOT NULL,
            PRIMARY KEY(module_id,book,chapter,verse)
        );
        CREATE TABLE IF NOT EXISTS tokens (
            module_id TEXT NOT NULL, book TEXT NOT NULL, chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL, position INTEGER NOT NULL, surface TEXT NOT NULL,
            lemma TEXT, morph TEXT, strong TEXT,
            PRIMARY KEY(module_id,book,chapter,verse,position),
            FOREIGN KEY(module_id,book,chapter,verse) REFERENCES verses(module_id,book,chapter,verse) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_token_lemma ON tokens(module_id, lemma);
        CREATE TABLE IF NOT EXISTS verse_mapping (
            source_module TEXT NOT NULL, source_ref TEXT NOT NULL,
            target_module TEXT NOT NULL, target_ref TEXT NOT NULL,
            PRIMARY KEY(source_module, source_ref, target_module)
        );""")
        for key,value in DEFAULT_SETTINGS.items():
            db.execute('INSERT OR IGNORE INTO settings(key,value) VALUES (?,?)',(key,json.dumps(value)))

def get_settings():
    with connect() as db:
        found = {r['key']:json.loads(r['value']) for r in db.execute('SELECT key,value FROM settings')}
    return {**DEFAULT_SETTINGS,**found}

def set_settings(patch):
    with connect() as db:
        for key,val in patch.items():
            db.execute('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(key,json.dumps(val)))
    return get_settings()
