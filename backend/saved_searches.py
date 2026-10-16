"""Local storage for named, reproducible advanced searches."""
import json
import sqlite3
from datetime import datetime, timezone

from .database import connect
from .library import NAMES

FIELDS={'module_id','book','lemma','surface','strong','morph','second_lemma',
        'second_surface','second_strong','second_morph','distance','order',
        'conditions','connector'}
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
    # 1.3 structured criteria coexist with legacy two-word searches from 1.2.
    if 'conditions' in criteria:
        if set(criteria)-{'module_id','book','conditions','connector','distance','order'}:
            raise ValueError('Die strukturierte Suchabfrage enthält unbekannte Felder.')
        module_id=criteria.get('module_id','')
        book=criteria.get('book','')
        conditions=criteria.get('conditions')
        if not isinstance(module_id,str) or len(module_id)>48:
            raise ValueError('Ungültige Modul-ID.')
        if not isinstance(book,str) or (book and book not in NAMES):
            raise ValueError('Unbekanntes Bibelbuch.')
        if not isinstance(conditions,list) or not 1<=len(conditions)<=5:
            raise ValueError('Bitte 1 bis 5 Wortbedingungen speichern.')
        cleaned_conditions=[]
        for condition in conditions:
            if not isinstance(condition,dict) or set(condition)-{'lemma','surface','strong','morph','position_from','position_to'}:
                raise ValueError('Eine Wortbedingung enthält unbekannte Felder.')
            item={}
            for key,value in condition.items():
                if key in ('position_from','position_to'):
                    if value is None or value=='':continue
                    if isinstance(value,bool) or not isinstance(value,int) or not 1<=value<=500:
                        raise ValueError('Tokenpositionen müssen ganze Zahlen zwischen 1 und 500 sein.')
                    item[key]=value
                else:
                    if not isinstance(value,str) or len(value)>200:
                        raise ValueError(f'Ungültiger Wert für {key}.')
                    if value.strip():item[key]=value.strip()
            if not any(item.get(key) for key in ('lemma','surface','strong','morph')):
                raise ValueError('Jede Wortbedingung benötigt ein Suchfeld.')
            if ('position_from' in item and 'position_to' in item and item['position_from']>item['position_to']):
                raise ValueError('Die erste Tokenposition darf nicht hinter der letzten liegen.')
            cleaned_conditions.append(item)
        connector=criteria.get('connector','all')
        if connector not in ('all','any'):raise ValueError('Verknüpfung muss UND oder ODER sein.')
        distance=criteria.get('distance',5)
        if isinstance(distance,bool) or not isinstance(distance,int) or not 0<=distance<=100:
            raise ValueError('Wortabstand muss zwischen 0 und 100 liegen.')
        order=criteria.get('order','any')
        if order not in ('any','before','after') or (connector=='any' and order!='any'):
            raise ValueError('Ungültige Reihenfolge für diese Verknüpfung.')
        if len(cleaned_conditions)<2 and order!='any':
            raise ValueError('Eine Reihenfolge benötigt mindestens zwei Wortbedingungen.')
        clean={'conditions':cleaned_conditions,'connector':connector,'distance':distance,'order':order}
        if module_id:clean['module_id']=module_id
        if book:clean['book']=book
        if module_id:
            with connect() as db:
                module=db.execute('SELECT language FROM modules WHERE id=?',(module_id,)).fetchone()
                if module is None:raise ValueError('Das ausgewählte Textmodul ist nicht installiert.')
                if module['language'] not in ('grc','he'):
                    raise ValueError('Morphologische Suchen benötigen griechische oder hebräische Module.')
        return name.strip(),clean
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
