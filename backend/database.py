"""Local SQLite storage. No user data is ever written inside the application package."""
import json
import os
import sqlite3
from pathlib import Path

APP_VERSION = '0.8.0'
DEFAULT_SETTINGS = {
    'theme': 'dark', 'font_size': 17, 'search_width': 25,
    'analysis_width': 27, 'active_reference': 'Joh 1,1',
    'show_greek': True, 'show_german': True, 'show_latin': True,
}

def data_dir():
    """Maintain the original v0.1 data path to avoid losing settings and modules.

    AMICUS_THEOLOGI_DATA_DIR overrides; old BIBLEWOERKS_DATA_DIR stays supported.
    A future explicit data migration can change this, but not silently.
    """
    custom = os.getenv('AMICUS_THEOLOGI_DATA_DIR') or os.getenv('BIBLEWOERKS_DATA_DIR')
    if custom:
        root = Path(custom).expanduser()
    elif os.name == 'nt':
        root = Path(os.getenv('LOCALAPPDATA', Path.home())) / 'Biblewoerks'
    else:
        root = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local/share')) / 'biblewoerks'
    root.mkdir(parents=True, exist_ok=True)
    return root

def connect():
    con = sqlite3.connect(data_dir() / 'amicus_theologi.sqlite3', timeout=10)
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
        CREATE INDEX IF NOT EXISTS idx_token_reference ON tokens(module_id,book,chapter,verse);
        CREATE TABLE IF NOT EXISTS verse_mapping (
            source_module TEXT NOT NULL, source_ref TEXT NOT NULL,
            target_module TEXT NOT NULL, target_ref TEXT NOT NULL,
            PRIMARY KEY(source_module, source_ref, target_module)
        );""")
        # v0.5 additive migration: independent lexicon modules and their entries.
        # No existing user tables are rewritten, and old verse/token data are retained.
        db.executescript("""
        CREATE TABLE IF NOT EXISTS lexicon_modules (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, language TEXT NOT NULL,
            license TEXT NOT NULL, provenance TEXT NOT NULL, version TEXT NOT NULL,
            installed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS lexicon_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            module_id TEXT NOT NULL REFERENCES lexicon_modules(id) ON DELETE CASCADE,
            lemma TEXT NOT NULL, lemma_key TEXT NOT NULL,
            strong TEXT NOT NULL DEFAULT '', gloss TEXT NOT NULL DEFAULT '',
            definition TEXT NOT NULL, reference TEXT NOT NULL DEFAULT '',
            UNIQUE(module_id,lemma_key,strong)
        );
        CREATE INDEX IF NOT EXISTS idx_lexicon_lookup ON lexicon_entries(lemma_key);
        CREATE INDEX IF NOT EXISTS idx_lexicon_strong ON lexicon_entries(strong);
        """)
        # v0.7: additive, independent tables for user study data.
        from .studies import setup as setup_studies
        setup_studies(db)
        from .textcriticism import setup as setup_textcriticism
        setup_textcriticism(db)
        # v0.3 migration: add an FTS5 virtual table plus maintenance triggers.
        # Existing module IDs, verses and user settings are preserved.
        db.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS verse_fts USING fts5(
            text, content='verses', content_rowid='rowid', tokenize='unicode61 remove_diacritics 2'
        );
        CREATE TRIGGER IF NOT EXISTS verse_fts_insert AFTER INSERT ON verses BEGIN
            INSERT INTO verse_fts(rowid,text) VALUES (new.rowid,new.text);
        END;
        CREATE TRIGGER IF NOT EXISTS verse_fts_delete AFTER DELETE ON verses BEGIN
            INSERT INTO verse_fts(verse_fts,rowid,text) VALUES ('delete',old.rowid,old.text);
        END;
        CREATE TRIGGER IF NOT EXISTS verse_fts_update AFTER UPDATE ON verses BEGIN
            INSERT INTO verse_fts(verse_fts,rowid,text) VALUES ('delete',old.rowid,old.text);
            INSERT INTO verse_fts(rowid,text) VALUES(new.rowid,new.text);
        END;
        """)
        # Rebuild on initial migration only, not on each startup.
        version=db.execute("SELECT value FROM settings WHERE key='fts_schema_version'").fetchone()
        if not version or version[0] != '1':
            db.execute("INSERT INTO verse_fts(verse_fts) VALUES ('rebuild')")
            db.execute("INSERT INTO settings(key,value) VALUES ('fts_schema_version','1') ON CONFLICT(key) DO UPDATE SET value='1'")
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


def factory_reset():
    """Transactional data reset. Retain schema/FTS triggers and recreate defaults."""
    with connect() as db:
        db.execute('DELETE FROM study_projects')
        db.execute('DELETE FROM textual_variants')
        db.execute('DELETE FROM modules')
        db.execute('DELETE FROM lexicon_modules')
        db.execute('DELETE FROM verse_mapping')
        db.execute('DELETE FROM settings')
    init_db()
    return {'reset': True, 'message':'Alle Benutzerdaten und installierten Module wurden gelöscht.'}
