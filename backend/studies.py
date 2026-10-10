"""Local user-owned studies, verse notes and highlights. Never modifies imported modules."""
import json
from .database import connect
from .library import NAMES

COLORS={'yellow','green','blue','pink','orange'}

def setup(db):
    db.executescript('''
    CREATE TABLE IF NOT EXISTS study_projects (
      id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS study_notes (
      id INTEGER PRIMARY KEY AUTOINCREMENT, project_id INTEGER NOT NULL REFERENCES study_projects(id) ON DELETE CASCADE,
      book TEXT NOT NULL, chapter INTEGER NOT NULL, verse INTEGER NOT NULL,
      content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE INDEX IF NOT EXISTS idx_study_notes_ref ON study_notes(book,chapter,verse);
    CREATE TABLE IF NOT EXISTS study_highlights (
      project_id INTEGER NOT NULL REFERENCES study_projects(id) ON DELETE CASCADE,
      book TEXT NOT NULL, chapter INTEGER NOT NULL, verse INTEGER NOT NULL,
      color TEXT NOT NULL, PRIMARY KEY(project_id,book,chapter,verse));
    ''')

def check_ref(book,chapter,verse):
    if book not in NAMES or not(1<=chapter<=200 and 1<=verse<=200):raise ValueError('Ungültige Bibelstelle.')

def projects():
    with connect() as db:
        return [dict(r) for r in db.execute('SELECT * FROM study_projects ORDER BY updated_at DESC,id DESC')]

def create_project(title,description=''):
    title=title.strip();description=description.strip()
    if not (1<=len(title)<=160) or len(description)>3000:raise ValueError('Ungültiger Projekttitel oder Beschreibung.')
    with connect() as db:
        cur=db.execute('INSERT INTO study_projects(title,description) VALUES(?,?)',(title,description))
        return {'id':cur.lastrowid,'title':title,'description':description}

def update_project(pid,title,description):
    title=title.strip();description=description.strip()
    if not (1<=len(title)<=160) or len(description)>3000:raise ValueError('Ungültiger Projekttitel oder Beschreibung.')
    with connect() as db:
        result=db.execute('UPDATE study_projects SET title=?,description=?,updated_at=CURRENT_TIMESTAMP WHERE id=?',(title,description,pid))
        if not result.rowcount:raise ValueError('Projekt nicht gefunden.')
    return {'id':pid,'title':title,'description':description}

def delete_project(pid):
    with connect() as db:
        if not db.execute('DELETE FROM study_projects WHERE id=?',(pid,)).rowcount:raise ValueError('Projekt nicht gefunden.')
    return {'deleted':pid}

def annotations(pid,book=None,chapter=None,verse=None):
    params=[pid]
    with connect() as db:
        if not db.execute('SELECT 1 FROM study_projects WHERE id=?',(pid,)).fetchone():raise ValueError('Projekt nicht gefunden.')
        clause=' WHERE project_id=?'
        if book is not None:
            check_ref(book,chapter,verse or 1)
            clause+=' AND book=? AND chapter=?';params.extend([book,chapter])
            if verse is not None:clause+=' AND verse=?';params.append(verse)
        return {'notes':[dict(r) for r in db.execute('SELECT * FROM study_notes'+clause+' ORDER BY book,chapter,verse,id',params)],
                'highlights':[dict(r) for r in db.execute('SELECT * FROM study_highlights'+clause+' ORDER BY book,chapter,verse',params)]}

def add_note(pid,book,chapter,verse,content):
    check_ref(book,chapter,verse);content=content.strip()
    if not (1<=len(content)<=20000):raise ValueError('Notiz muss 1 bis 20.000 Zeichen enthalten.')
    with connect() as db:
        if not db.execute('SELECT 1 FROM study_projects WHERE id=?',(pid,)).fetchone():raise ValueError('Projekt nicht gefunden.')
        cur=db.execute('INSERT INTO study_notes(project_id,book,chapter,verse,content) VALUES (?,?,?,?,?)',(pid,book,chapter,verse,content))
        db.execute('UPDATE study_projects SET updated_at=CURRENT_TIMESTAMP WHERE id=?',(pid,))
        return {'id':cur.lastrowid,'project_id':pid,'book':book,'chapter':chapter,'verse':verse,'content':content}

def edit_note(pid,nid,content):
    content=content.strip()
    if not (1<=len(content)<=20000):raise ValueError('Notiz muss 1 bis 20.000 Zeichen enthalten.')
    with connect() as db:
        if not db.execute('UPDATE study_notes SET content=?,updated_at=CURRENT_TIMESTAMP WHERE id=? AND project_id=?',(content,nid,pid)).rowcount:raise ValueError('Notiz nicht gefunden.')
        db.execute('UPDATE study_projects SET updated_at=CURRENT_TIMESTAMP WHERE id=?',(pid,))
    return {'id':nid,'content':content}

def delete_note(pid,nid):
    with connect() as db:
        if not db.execute('DELETE FROM study_notes WHERE id=? AND project_id=?',(nid,pid)).rowcount:raise ValueError('Notiz nicht gefunden.')
    return {'deleted':nid}

def highlight(pid,book,chapter,verse,color):
    check_ref(book,chapter,verse)
    if color is not None and color not in COLORS:raise ValueError('Unbekannte Markierungsfarbe.')
    with connect() as db:
        if not db.execute('SELECT 1 FROM study_projects WHERE id=?',(pid,)).fetchone():raise ValueError('Projekt nicht gefunden.')
        if color is None:db.execute('DELETE FROM study_highlights WHERE project_id=? AND book=? AND chapter=? AND verse=?',(pid,book,chapter,verse))
        else:db.execute('INSERT INTO study_highlights(project_id,book,chapter,verse,color) VALUES(?,?,?,?,?) ON CONFLICT(project_id,book,chapter,verse) DO UPDATE SET color=excluded.color',(pid,book,chapter,verse,color))
        db.execute('UPDATE study_projects SET updated_at=CURRENT_TIMESTAMP WHERE id=?',(pid,))
    return {'book':book,'chapter':chapter,'verse':verse,'color':color}

def export_project(pid):
    with connect() as db:
        row=db.execute('SELECT * FROM study_projects WHERE id=?',(pid,)).fetchone()
        if not row:raise ValueError('Projekt nicht gefunden.')
    content=annotations(pid)
    return {'format':'amicus-theologi-study','schema_version':1,'project':dict(row),**content}
