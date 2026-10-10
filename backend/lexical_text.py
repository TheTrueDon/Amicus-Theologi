"""Source-grounded SHORT meanings for hover previews.

STEPBible's TBESG/TBESH/TFLSJ keep separate transliteration, grammar,
short gloss and full definition fields. Older Amicus versions mistakenly
stored the FIRST field after the lemma (usually a transliteration) as gloss.
For existing installations, interpret the original concatenated definition
at read time. Do not rewrite scholarly material or guess a translation.
"""
from html import unescape
from html.parser import HTMLParser
import re


class _PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = []
    def handle_starttag(self, tag, attrs):
        if self.hidden:
            if tag == self.hidden[-1]:
                self.hidden.append(tag)
        elif tag in ('script', 'style', 'iframe', 'svg', 'math', 'template'):
            self.hidden.append(tag)
        elif tag in ('br', 'p', 'div', 'li'):
            self.parts.append(' ')
    def handle_endtag(self, tag):
        if self.hidden:
            if tag == self.hidden[-1]:
                self.hidden.pop()
        elif tag in ('p', 'div', 'li'):
            self.parts.append(' ')
    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def concise_gloss(value):
    """Remove markup for plaintext UI without evaluating HTML or JS."""
    text = str(value or '')[:8000]
    parser = _PlainText()
    try:
        parser.feed(text)
        text = ' '.join(''.join(parser.parts).split())
    except (ValueError, AssertionError):
        text = unescape(re.sub(r'<[^>]*>', ' ', text))
    return text.strip()


# Codes in the grammar column, not definitions. Accept both Greek and Hebrew.
_MORPH = re.compile(r'^(?:[GH]:)?(?:[NAVPRCITDFSX](?:[-:/][A-Z0-9]+){0,4}|[GH]:[A-Z0-9-]+)$', re.I)
_LABEL = re.compile(r'^(?:gloss|short\s+(?:meaning|definition)|meaning|bedeutung|translation|übersetzung)\s*[:：]\s*(.+)$', re.I)


def _is_meta(s):
    return bool(_MORPH.fullmatch(s) or re.fullmatch(r'(?:G|H)\d+[a-z]?', s, re.I)
                or re.fullmatch(r'(?:noun|verb|adjective|adverb|preposition|particle|pronoun|proper noun|substantiv|adjektiv)', s, re.I))


def _meaning_part(text):
    """Return human-readable words; explicitly labelled data wins."""
    s = concise_gloss(text)
    if not s or _is_meta(s) or s in ('-', '–', '?'):
        return ''
    match = _LABEL.match(s)
    return match.group(1).strip() if match else s


def best_gloss(entry):
    """Select a TRUE lexical gloss from an installed entry, if identifiable.

    For legacy STEPBible imports the stored entry looks like
      gloss='logos', definition='logos · G:N-M · word, speech · ...'
    We must NEVER show `logos` as the translation. The first segment is the
    discarded transliteration, the morphology is also skipped.
    For manually imported TSV files the gloss field remains authoritative.
    """
    module_id = str(entry.get('module_id') or '').lower()
    provenance = str(entry.get('provenance') or '').lower()
    is_step = module_id.startswith('step-') or ('stepbible' in provenance and any(x in provenance for x in ('tbesg', 'tbesh', 'tflsj')))
    raw_gloss = concise_gloss(entry.get('gloss') or '')
    definition = str(entry.get('definition') or '')
    if not is_step:
        return _meaning_part(raw_gloss)

    segments = [_meaning_part(x) for x in re.split(r'\s+·\s+', definition)]
    segments = [x for x in segments if x]

    # For older STEPBible imports the first segment is the transliteration.
    # It equals the value erroneously saved in the gloss column.
    if segments and raw_gloss and segments[0].casefold() == raw_gloss.casefold():
        segments.pop(0)
        # Ignore another phonetic field if labelled explicitly.
        while segments and re.match(r'^(?:transliteration|pronunciation|umschrift|aussprache)\s*:', segments[0], re.I):
            segments.pop(0)
        if segments:
            return segments[0][:240]
        return ''

    # Newer source-specific imports can store a genuine gloss directly.
    if raw_gloss and not _is_meta(raw_gloss):
        return _meaning_part(raw_gloss)[:240]

    # A legacy entry without the usual concatenation has no trustworthy
    # standalone meaning; deliberately show "not available".
    for segment in segments:
        if _LABEL.match(segment):
            return _meaning_part(segment)[:240]
    return ''


def gloss_priority(entry):
    """Prefer German when indicated, then brief STEPBible lexica, then LSJ.

    Display languages are not guessed from a Greek/Hebrew headword.
    """
    name = ' '.join((str(entry.get('title') or ''), str(entry.get('module_id') or ''))).lower()
    german = bool(re.search(r'\b(?:deutsch|german|deutschsprachig|gerstrongs)\b', name))
    brief = 'tbesg' in name or 'tbesh' in name
    long_lex = 'tflsj' in name
    return (0 if german else 1, 0 if brief else 1 if not long_lex else 2, name)
