"""Validated multi-condition searches for annotated Bible tokens."""
from .database import connect
from .library import NAMES

MAX_RESULTS = 100
MAX_CONDITIONS = 5
FIELDS = ('lemma', 'surface', 'strong', 'morph')


def _condition_sql(alias, condition):
    parts = []
    args = []
    for field in FIELDS:
        value = condition.get(field, '').strip()
        if value:
            if field == 'morph':
                parts.append(f'instr(lower({alias}.morph),lower(?))>0')
            else:
                parts.append(f'{alias}.{field}=? COLLATE NOCASE')
            args.append(value)
    return ' AND '.join(parts), args


def _validate(criteria):
    if not isinstance(criteria, dict):
        raise ValueError('Die Suchabfrage muss als Kriterienliste übergeben werden.')
    allowed = {'module_id', 'book', 'conditions', 'connector', 'distance', 'order'}
    if set(criteria) - allowed:
        raise ValueError('Die Suchabfrage enthält unbekannte Felder.')
    module_id = criteria.get('module_id', '') or ''
    book = criteria.get('book', '') or ''
    if not isinstance(module_id, str) or len(module_id) > 48:
        raise ValueError('Ungültige Modul-ID.')
    if book and book not in NAMES:
        raise ValueError('Unbekanntes Bibelbuch.')
    conditions = criteria.get('conditions')
    if not isinstance(conditions, list) or not 1 <= len(conditions) <= MAX_CONDITIONS:
        raise ValueError(f'Bitte 1 bis {MAX_CONDITIONS} Wortbedingungen angeben.')
    cleaned = []
    for condition in conditions:
        if not isinstance(condition, dict) or set(condition) - set(FIELDS):
            raise ValueError('Eine Wortbedingung enthält unbekannte Felder.')
        item = {}
        for field in FIELDS:
            value = condition.get(field, '')
            if not isinstance(value, str) or len(value) > 200:
                raise ValueError(f'Ungültiger Wert für {field}.')
            if value.strip():
                item[field] = value.strip()
        if not item:
            raise ValueError('Jede Wortbedingung benötigt mindestens ein Suchfeld.')
        cleaned.append(item)
    connector = criteria.get('connector', 'all')
    if connector not in ('all', 'any'):
        raise ValueError('Verknüpfung muss UND oder ODER sein.')
    distance = criteria.get('distance', 5)
    if isinstance(distance, bool) or not isinstance(distance, int) or not 0 <= distance <= 100:
        raise ValueError('Wortabstand muss eine ganze Zahl zwischen 0 und 100 sein.')
    order = criteria.get('order', 'any')
    if order not in ('any', 'before', 'after'):
        raise ValueError('Ungültige Reihenfolge.')
    if connector == 'any' and order != 'any':
        raise ValueError('Reihenfolge und Wortabstand gelten nur bei UND-Verknüpfung.')
    if len(cleaned) == 1 and order != 'any':
        raise ValueError('Eine Reihenfolge benötigt mindestens zwei Wortbedingungen.')
    if module_id:
        with connect() as db:
            module = db.execute('SELECT language FROM modules WHERE id=?', (module_id,)).fetchone()
        if module is None:
            raise ValueError('Das ausgewählte Textmodul ist nicht installiert.')
        if module['language'] not in ('grc', 'he'):
            raise ValueError('Morphologische Suchen benötigen griechische oder hebräische Module.')
    return {
        'module_id': module_id, 'book': book, 'conditions': cleaned,
        'connector': connector, 'distance': distance, 'order': order,
    }


def query_search(criteria, *, limit=50, offset=0):
    """Search verses where structured token conditions occur.

    For AND, each condition matches a distinct token in the same verse. The
    maximum distance is checked between adjacent conditions in their displayed
    order. ODER searches each condition independently and ignores position.
    """
    criteria = _validate(criteria)
    if not 1 <= limit <= MAX_RESULTS or not 0 <= offset <= 100000:
        raise ValueError('Ungültige Seitengröße/Position.')
    conditions = criteria['conditions']
    args = []
    scope = []
    if criteria['module_id']:
        scope.append('v.module_id=?')
        args.append(criteria['module_id'])
    if criteria['book']:
        scope.append('v.book=?')
        args.append(criteria['book'])

    if criteria['connector'] == 'any':
        alternatives = []
        for index, condition in enumerate(conditions):
            sql, condition_args = _condition_sql(f'o{index}', condition)
            alternatives.append(
                f"EXISTS (SELECT 1 FROM tokens o{index} WHERE o{index}.module_id=v.module_id "
                f"AND o{index}.book=v.book AND o{index}.chapter=v.chapter AND o{index}.verse=v.verse AND {sql})"
            )
            args.extend(condition_args)
        where = ' AND '.join(scope + ['(' + ' OR '.join(alternatives) + ')'])
        from_sql = 'FROM verses v JOIN modules m ON m.id=v.module_id WHERE ' + where
    else:
        joins = []
        predicates = list(scope)
        for index, condition in enumerate(conditions):
            alias = f't{index}'
            if index == 0:
                joins.append(f'JOIN tokens {alias} ON {alias}.module_id=v.module_id AND {alias}.book=v.book AND {alias}.chapter=v.chapter AND {alias}.verse=v.verse')
            else:
                joins.append(f'JOIN tokens {alias} ON {alias}.module_id=t0.module_id AND {alias}.book=t0.book AND {alias}.chapter=t0.chapter AND {alias}.verse=t0.verse')
                predicates.append(f'{alias}.position<>t0.position')
                for previous in range(1, index):
                    predicates.append(f'{alias}.position<>t{previous}.position')
                previous = index - 1
                predicates.append(f'abs(t{index}.position-t{previous}.position)-1<=?')
                args.append(criteria['distance'])
                if criteria['order'] == 'before':
                    predicates.append(f't{previous}.position<t{index}.position')
                elif criteria['order'] == 'after':
                    predicates.append(f't{previous}.position>t{index}.position')
            sql, condition_args = _condition_sql(alias, condition)
            predicates.append(sql)
            args.extend(condition_args)
        from_sql = 'FROM verses v JOIN modules m ON m.id=v.module_id ' + ' '.join(joins) + ' WHERE ' + ' AND '.join(predicates)

    with connect() as db:
        total = db.execute('SELECT COUNT(*) FROM (SELECT DISTINCT v.module_id,v.book,v.chapter,v.verse ' + from_sql + ')', args).fetchone()[0]
        rows = db.execute('''SELECT DISTINCT v.module_id,m.title AS module_title,m.language,v.book,v.chapter,v.verse,v.text '''
                          + from_sql + ' ORDER BY v.module_id,v.book,v.chapter,v.verse LIMIT ? OFFSET ?',
                          args + [limit, offset]).fetchall()
    return {
        'total': total, 'limit': limit, 'offset': offset,
        'results': [dict(row) for row in rows], 'criteria': criteria,
        'note': 'Morphologie wird als Teilzeichenfolge des importierten Codes geprüft. UND verlangt alle Wortbedingungen im selben Vers; der Abstand gilt zwischen benachbarten Bedingungen.',
    }
