"""Hebrew reading view for historic STEPBible/OSHB annotations.

Crucially, OSHB lemma attributes are often Strong-based IDs such as
`c/m/6529` rather than written Hebrew lemmas. The source fields are never
changed; a DISPLAY headword is resolved from installed lexica when possible.
"""
import re
from .lexicon import lookup, clean_key
from .lexical_text import best_gloss, gloss_priority

HEBREW = re.compile(r'[\u0590-\u05ff]')
NUMERIC_LEMMA = re.compile(r'^(?:(?:[a-z]{1,3}|[GH]\d{1,5})/)*[Hh]?\d{1,5}(?:\s+[a-z])?$',re.I)
STRONG = re.compile(r'(?<![a-z0-9])H0*(\d{1,5})(?:[a-z])?(?![a-z0-9])',re.I)


def strong_for_lemma(word):
    """Return a reliable standard Hebrew Strong key, if given explicitly."""
    direct=str(word.get('strong') or '').strip()
    m=STRONG.search(direct)
    if m:return 'H'+str(int(m[1]))
    raw=str(word.get('lemma') or '').strip()
    if NUMERIC_LEMMA.fullmatch(raw):
        last=raw.rsplit('/',1)[-1]
        m=re.match(r'^H?(\d{1,5})(?:\s+[a-z])?$',last,re.I)
        if m:return 'H'+str(int(m[1]))
    return ''


def _is_written_hebrew(value):
    value=str(value or '').strip()
    return bool(HEBREW.search(value)) and bool(value) and len(value)<=180


def explain_word(word,entries=None):
    """Prepare a word's reading view, without changing imported data.

    Lexical orthography is used only when it is linked by Strong. If no
    confirmed source is available, don't present a numeric ID as a lemma.
    """
    strong=strong_for_lemma(word)
    raw=str(word.get('lemma') or '').strip()
    if entries is None:
        entries=lookup('he',raw if _is_written_hebrew(raw) else '',strong)
    preferred=sorted(entries,key=lambda e:(
        not bool(strong and strong_for_lemma({'strong':e.get('strong')})==strong),
        gloss_priority(e)))
    lemma=raw if _is_written_hebrew(raw) else ''
    headword_source='Annotation' if lemma else ''
    if not lemma:
        for entry in preferred:
            candidate=str(entry.get('lemma') or '').strip()
            if _is_written_hebrew(candidate):
                lemma=candidate
                headword_source=str(entry.get('title') or 'Lexikon')
                break
    gloss=''; gloss_source=''
    for entry in preferred:
        candidate=best_gloss(entry)
        if candidate:
            gloss=candidate[:180]
            gloss_source=str(entry.get('title') or '')
            break
    return {'display_lemma':lemma,'lemma_available':bool(lemma),
            'headword_source':headword_source,'lookup_strong':strong,
            'gloss':gloss,'gloss_source':gloss_source,'raw_lemma':raw}
