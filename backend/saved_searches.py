"""Local storage for named, reproducible advanced searches."""
import json
import sqlite3
from datetime import datetime, timezone

from .database import connect
from .library import NAMES

FIELDS={'module_id','book','lemma','surface','strong','morph','second_lemma',
        'second_surface','second_strong','second_morph','distance','order'}
TEXT_FIELDS=FIELDS-{'distance','order'}
MAX_NAME=120


def setup(db):
    db.executescript('''CREATE TABLE IF NOT EXISTS saved_searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        name_key TEXT NOT NULL UNIQUE,
        criteria_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );''')


def _timestamp():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clean(name, criteria):
    if not isinstance(name,str) or not name.strip() or len(name.strip())>MAX_NAME:
        raise ValueError(f'Bitte einen Namen mit 1 bis {MAX_NAME} Zeichen eingeben.')
    if not isinstance(criteria,dict) or set(criteria)-FIELDS:
        raise ValueError('Die Suchkriterien enthalten unbekannte Felder.')
    clean={}
    for key in TEXT_FIELDS:
        value=criteria.get(key,'')
        if not isinstance(value,str) or len(value)>200:
            raise ValueError(f'Ungültiger Wert für das Suchfeld {key}.')
        if value.strip():clean[key]=value.strip()
    distance=criteria.get('distance',5)
    if isinstance(distance,bool) or not isinstance(distance,int):
        raise ValueError('Der Wortabstand muss eine ganze Zahl sein.')
    if not 0<=distance<=100:
        raise ValueError('Wortabstand muss zwischen 0 und 100 liegen.')
    order=criteria.get('order','any')
    if order not in ('any','before','after'):
        raise ValueError('Ungültige Wortreihenfolge.')
    clean['distance']=distance
    clean['order']=order
    if clean.get('book') and clean['book'] not in NAMES:
        raise ValueError('Unbekanntes Bibelbuch.')
    if not any(clean.get(key) for key in ('lemma','surface','strong','morph')):
        raise ValueError('Mindestens ein Kriterium für Wort 1 eingeben.')
    if order!='any' and not any(clean.get(key) for key in ('second_lemma','second_surface','second_strong','second_morph')):
        raise ValueError('Wort 2 benötigt Kriterien, wenn eine Reihenfolge gewählt wird.')
    if clean.get('module_id'):
        with connect() as db:
            module=db.execute('SELECT language FROM modules WHERE id=?',(clean['module_id'],)).fetchone()
            if module is None:
                raise ValueError('Das ausgewählte Textmodul ist nicht installiert.')
            if module['language'] not in ('grc','he'):
                raise ValueError('Gespeicherte morphologische Suchen benötigen ein griechisches oder hebräisches Modul.')
    return name.strip(),clean


def _record(row):
    return {'id':row['id'],'name':row['name'],
            'criteria':json.loads(row['criteria_json']),
            'created_at':row['created_at'],'updated_at':row['updated_at']}


def list_saved_searches():
    with connect() as db:
        rows=db.execute('SELECT * FROM saved_searches ORDER BY lower(name),id').fetchall()
    return [_record(row) for row in rows]


def create_saved_search(name,criteria):
    name,criteria=_clean(name,criteria)
    stamp=_timestamp()
    try:
        with connect() as db:
            cur=db.execute('''INSERT INTO saved_searches(name,name_key,criteria_json,created_at,updated_at)
                VALUES(?,?,?,?,?)''',(name,name.casefold(),json.dumps(criteria,ensure_ascii=False),stamp,stamp))
            row=db.execute('SELECT * FROM saved_searches WHERE id=?',(cur.lastrowid,)).fetchone()
    except sqlite3.IntegrityError as exc:
        if 'UNIQUE constraint failed' in str(exc):
            raise ValueError('Eine gespeicherte Suche mit diesem Namen gibt es bereits.') from exc
        raise
    return _record(row)


def delete_saved_search(search_id):
    with connect() as db:
        cur=db.execute('DELETE FROM saved_searches WHERE id=?',(search_id,))
    return cur.rowcount>0
