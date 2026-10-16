"""Read-only integrity checks for imported Greek/Hebrew word annotations.

Passing means that stored tokens match their stored verse text and have
continuous positions and non-empty lemma/morphology fields. It does not certify
the edition's completeness, license, or scholarly correctness.
"""
from .database import connect
from .library import NAMES
from .morphology import normalize_surface

MAX_REPORTED_REFERENCES = 25


def audit_annotations(module_id):
    with connect() as db:
        module = db.execute('SELECT id,title,language,license,provenance,version FROM modules WHERE id=?',
                            (module_id,)).fetchone()
        if module is None:
            raise ValueError('Textmodul nicht gefunden.')
        if module['language'] not in ('grc', 'he'):
            raise ValueError('Die Wortdatenprüfung ist nur für griechische und hebräische Module verfügbar.')
        verse_count = db.execute('SELECT COUNT(*) FROM verses WHERE module_id=?', (module_id,)).fetchone()[0]
        annotated_verses = db.execute('SELECT COUNT(*) FROM (SELECT book,chapter,verse FROM tokens WHERE module_id=? GROUP BY book,chapter,verse)',
                                      (module_id,)).fetchone()[0]
        annotated_words = db.execute('SELECT COUNT(*) FROM tokens WHERE module_id=?', (module_id,)).fetchone()[0]
        verse_rows = db.execute('''SELECT v.book,v.chapter,v.verse,v.text
            FROM verses v WHERE v.module_id=? AND EXISTS (
              SELECT 1 FROM tokens t WHERE t.module_id=v.module_id AND t.book=v.book
                AND t.chapter=v.chapter AND t.verse=v.verse)
            ORDER BY v.book,v.chapter,v.verse''', (module_id,)).fetchall()

    verse_text = {(r['book'],r['chapter'],r['verse']):r['text'] for r in verse_rows}
    sequence_errors=[]
    position_errors=[]
    analysis_errors=[]
    issue_counts={'surface':0,'position':0,'analysis':0}
    truncated=[False]
    current_ref=None
    surfaces=[]
    expected_position=1

    def record(target, ref):
        label=_reference(ref)
        if label in target:return
        if len(target)<MAX_REPORTED_REFERENCES:target.append(label)
        else:truncated[0]=True

    def finish(ref, words):
        if ref is not None and normalize_surface(''.join(words)) != normalize_surface(verse_text[ref]):
            issue_counts['surface']+=1
            record(sequence_errors,ref)

    for row in _module_tokens(module_id):
        ref=(row['book'],row['chapter'],row['verse'])
        if ref!=current_ref:
            finish(current_ref,surfaces)
            current_ref=ref
            surfaces=[]
            expected_position=1
        if row['position']!=expected_position:
            issue_counts['position']+=1
            record(position_errors,ref)
        expected_position=row['position']+1
        surfaces.append(row['surface'])
        if not row['lemma'] or not row['morph']:
            issue_counts['analysis']+=1
            record(analysis_errors,ref)
    finish(current_ref,surfaces)

    coverage=round(100*annotated_verses/verse_count,1) if verse_count else 0.0
    errors=bool(sequence_errors or position_errors or analysis_errors)
    status='failed' if errors else ('no_annotations' if not annotated_words else 'passed')
    return {
        'module':dict(module), 'status':status,
        'counts':{'verses':verse_count,'annotated_verses':annotated_verses,
                  'unannotated_verses':verse_count-annotated_verses,
                  'annotated_words':annotated_words,'annotation_coverage_percent':coverage,
                  'checked_verses':annotated_verses},
        'checks':{'token_surfaces_match_verse_text':not sequence_errors,
                  'token_positions_contiguous':not position_errors,
                  'lemma_and_morphology_present':not analysis_errors},
        'issues':{'surface_mismatch_refs':sequence_errors,
                  'position_error_refs':position_errors,
                  'missing_analysis_refs':analysis_errors},
        'issue_counts':issue_counts,
        'issue_list_truncated':truncated[0],
        'note':'Diese Prüfung vergleicht gespeicherte Annotationen mit dem gespeicherten Vers. Sie bestätigt weder die Vollständigkeit der Ausgabe noch die Lizenz oder wissenschaftliche Richtigkeit der Quelle.'
    }


def _reference(ref):
    book,chapter,verse=ref
    return f'{NAMES.get(book,book)} {chapter},{verse}'


def _module_tokens(module_id):
    with connect() as db:
        cursor=db.execute('''SELECT book,chapter,verse,position,surface,lemma,morph
            FROM tokens WHERE module_id=? ORDER BY book,chapter,verse,position''',(module_id,))
        yield from cursor
