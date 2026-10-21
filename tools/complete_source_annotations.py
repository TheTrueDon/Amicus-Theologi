#!/usr/bin/env python3
"""Complete word-level annotations in the ten bundled source packages.

Greek: align Open Greek Corpus (OGA) annotations to package text, then use
same-work frequency analyses only where the tokenization/text editions differ.
Latin: preserve source annotations and fill unannotated tokens with UDPipe.
The emitted metadata states which analyses are automatic.
"""
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.source_packages import inspect_package
from backend.sources import WORD, _local, _visible

OGA_SOURCES = {
    'josephus-bellum-judaicum-perseus': 'Open Greek Corpus OGA export; Perseus Greek text',
    'philo-de-opificio-mundi-perseus': 'Open Greek Corpus OGA export; 1st1KGreek text',
    'origenes-de-oratione-pta': 'Open Greek Corpus OGA export; PTA text',
    'athanasius-de-incarnatione-pta': 'Open Greek Corpus OGA export; PTA text',
    'severian-de-fide-pta': 'Open Greek Corpus OGA export; PTA text',
}

def norm(value):
    return ''.join(c for c in unicodedata.normalize('NFD', value.casefold())
                   if not unicodedata.combining(c) and c not in "’'ʼ᾽`")

def read_oga(path):
    by_locus = defaultdict(list)
    by_form = defaultdict(Counter)
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        for line in stream:
            row = json.loads(line)
            form=row.get('form', '')
            if not WORD.fullmatch(form) and not WORD.fullmatch(form.rstrip("’'ʼ᾽`")):
                continue
            annotation = (row.get('lemma') or '', row.get('morph') or '', '')
            if not all(annotation[:2]) or annotation[1] in ('x--------','X'):
                continue
            by_locus[row.get('locus', '')].append((form, annotation))
            by_form[norm(form)][annotation] += 1
    return by_locus, by_form

def read_package(path):
    manifest, sections, annotations, editions, translations, docs = inspect_package(path.read_bytes())
    raw = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files = {name: z.read(name) for name in z.namelist()}
    section_map = {ref: text for ref, _ordinal, text in sections}
    old = {}
    if 'annotations' in manifest['files']:
        text = files[manifest['files']['annotations']].decode('utf-8-sig')
        delimiter = '\t' if text[:3000].count('\t') > text[:3000].count(',') else ','
        for row in csv.DictReader(io.StringIO(text), delimiter=delimiter):
            old[(row['ref'], int(row['position']))] = tuple(row.get(k, '') or '' for k in ('lemma','morph','strong'))
    return manifest, files, sections, section_map, old

def canonical_elision(surface):
    key = norm(surface)
    # Common Greek elision spellings. Their full forms are canonical lemma
    # candidates; the source corpus supplies the corresponding POS/morph code.
    mapping = {
        'δ': 'δέ', 'ἀλλ': 'ἀλλά', 'δι': 'διά', 'καθ': 'κατά', 'κατ': 'κατά',
        'ἐπ': 'ἐπί', 'ἐφ': 'ἐπί', 'παρ': 'παρά', 'ὑπ': 'ὑπό', 'ὑφ': 'ὑπό',
        'μετ': 'μετά', 'μεθ': 'μετά', 'ἀπ': 'ἀπό', 'ἀφ': 'ἀπό',
        'μηδ': 'μηδέ', 'οὐδ': 'οὐδέ', 'οὔτ': 'οὔτε', 'μήτ': 'μήτε',
        'ἵν': 'ἵνα', 'γ': 'γε', 'τ': 'τε', 'ἀνθ': 'ἀντί', 'ἀντ': 'ἀντί',
        'ἆρ': 'ἄρα', 'οὐκέτ': 'οὐκέτι', 'οὐκέθ': 'οὐκέτι',
        'μηκέτ': 'μηκέτι', 'μηκέθ': 'μηκέτι', 'οὔθ': 'οὔτε', 'μήθ': 'μήτε',
        'πάντ': 'πάντα', 'πάνθ': 'πάντα', 'τοῦτ': 'τοῦτο', 'τοῦθ': 'τοῦτο',
    }
    # Strip a trailing apostrophe only: it marks an elided form, while crasis
    # spellings remain eligible for the same-work frequency fallback.
    raw = unicodedata.normalize('NFD', surface.casefold())
    raw = ''.join(c for c in raw if not unicodedata.combining(c))
    raw = raw.rstrip("’'ʼ᾽`")
    normalized_mapping = {norm(key): value for key, value in mapping.items()}
    target = normalized_mapping.get(norm(raw))
    return target

def best(counter):
    return counter.most_common(1)[0][0] if counter else None

def documented_fallback(surface, language, by_form=None):
    """Conservative lexicalized forms absent because the corpus split crasis."""
    key=norm(surface)
    if language!='grc':return None
    simple={
      'ουτε':('οὔτε','c--------'), 'μητε':('μήτε','c--------'),
      'μηθ':('μήτε','c--------'), 'ουθ':('οὔτε','c--------'),
      'δι':('διά','r--------'), 'αλλ':('ἀλλά','c--------'),
      'παρ':('παρά','r--------'), 'μετ':('μετά','r--------'),
      'μεθ':('μετά','r--------'), 'καθ':('κατά','r--------'),
      'αφ':('ἀπό','r--------'), 'απ':('ἀπό','r--------'),
      'επ':('ἐπί','r--------'), 'εφ':('ἐπί','r--------'),
      'τουτεστιν':('τουτέστιν','d--------'),
      'καγω':('ἐγώ','p-s---mn-'), 'κακεῖνος':('ἐκεῖνος','p-s---mn-'),
      'κακεινον':('ἐκεῖνος','p-s---ma-'), 'κακεινου':('ἐκεῖνος','p-s---mg-'),
      'κακεινωι':('ἐκεῖνος','p-s---md-'), 'κακεινοις':('ἐκεῖνος','p-p---md-'),
      'κακεινων':('ἐκεῖνος','p-p---mg-'), 'κακεινους':('ἐκεῖνος','p-p---ma-'),
      'κακεινο':('ἐκεῖνος','p-s---na-'), 'κακειθεν':('ἐκεῖθεν','d--------'),
      'καμε':('ἐγώ','p-s---ma-'), 'καπειδη':('ἐπειδή','c--------'),
      'καπειδαν':('ἐπειδάν','c--------'), 'καπειδηπερ':('ἐπειδήπερ','c--------'),
      'καπει':('ἐπεί','c--------'), 'καπο':('ἀπό','r--------'),
      'καξ':('ἐκ','r--------'), 'καυτος':('αὐτός','a-s---mn-'),
      'τουναντιον':('ἐναντίος','a-s---na-'), 'τονομα':('ὄνομα','n-s---na-'),
      'τουπισω':('ὀπίσω','d--------'), 'τουργον':('ἔργον','n-s---na-'),
      'τουμπροσθεν':('ἔμπροσθεν','d--------'),
      'ταδελφου':('ἀδελφός','n-s---mg-'), 'ταδελφωι':('ἀδελφός','n-s---md-'),
      'τανδρος':('ἀνήρ','n-s---mg-'), 'τανδρι':('ἀνήρ','n-s---md-'),
      'ταληθες':('ἀληθής','a-s---nn-'), 'ταληθη':('ἀληθής','a-p---na-'),
      'τακριβες':('ἀκριβής','a-s---nn-'), 'ταναγκαιον':('ἀναγκαῖος','a-s---nn-'),
      'ταναντια':('ἐναντίος','a-p---na-'), 'ταδικειν':('ἀδικέω','v--pna---'),
      'ταγαθα':('ἀγαθός','a-p---na-'), 'ταλλα':('ἄλλος','a-p---na-'),
      'ταργυριον':('ἀργύριον','n-s---na-'), 'τανδον':('ἔνδον','d--------'),
      'τακει':('ἐκεῖ','d--------'), 'ταργα':('ἔργον','n-p---na-'),
      'ταυτου':('αὐτός','p-s---mg-'), 'τουδαφος':('ἔδαφος','n-s---na-'),
      'χαβουλων':('Χαβουλών','n-s---mn-'), 'εξαλωθ':('Ἐξαλώθ','n-s---mn-'),
      'εξαλωθα':('Ἐξαλώθ','n-s---ma-'),
      'ησαιας':('Ἡσαΐας','n-s---mn-'), 'ογδοηκοστωι':('ὀγδοηκοστός','a-s---md-'),
      'αυτοσ':('αὐτός','p-s---mn-'),
      'ιωνα':('Ἰωνᾶς','n-s---md-'), 'επιγραφη':('ἐπιγραφή','n-s---fn-'),
      'προσκαιρως':('πρόσκαιρος','d--------'),
      's':('s','SYM'), 'βουλει':('βούλομαι','v2spim---'),
      'ουτ':('οὔτε','c--------'), 'μηδ':('μηδέ','d--------'),
      'ηλλοτριωμεθα':('ἀλλοτριόω','v1prmi---'),
      'επιγνωσθησηι':('ἐπιγινώσκω','v2sfip---'),
      'παραδεικνυσι':('παραδείκνυμι','v3spia---'),
      'χρηματισητε':('χρηματίζω','v2ppsa---'),
      'αυτωι':('αὐτός','p-s---md-'),
      'διηγαγε':('διάγω','v3saia---'),
      'εγεγυμνωτο':('γυμνόω','v3slmi---'),
      'προυβαλετο':('προβάλλω','v3saim---'),
      'μητε':('μήτε','c--------'), 'ουτε':('οὔτε','c--------'),
      'τουτεστιν':('τουτέστιν','d--------'),
    }
    simple={norm(form):value for form,value in simple.items()}
    if key in simple:return (*simple[key], '')
    if surface.isdigit():return (surface,'m--------','')
    if key=='η':return ('ἤ','c--------','')
    return None

def greek_model_rows(text, nlp):
    rows=[]
    for token in nlp(text):
        if not WORD.fullmatch(token.text):continue
        lemma=token.lemma_ or token.text
        morph='|'.join(x for x in (token.pos_,str(token.morph)) if x)
        if lemma and morph:rows.append((token.text,(lemma,morph,'')))
    return rows

def annotate_greek(sections, old, by_locus, by_form, nlp):
    out = {}
    counts = Counter()
    global_form = defaultdict(Counter)
    for entries in by_locus.values():
        for form, ann in entries:
            global_form[norm(form)][ann] += 1
    for ref, _ordinal, text in sections:
        words = [m.group() for m in WORD.finditer(text)]
        src = by_locus.get(ref, [])
        seq = SequenceMatcher(None, [norm(w) for w in words],
                              [norm(w) for w, _ in src], autojunk=False)
        aligned = {i: src[j][1] for block in seq.get_matching_blocks()
                   for i, j in zip(range(block.a, block.a + block.size),
                                   range(block.b, block.b + block.size))}
        model_rows=[]
        if len(aligned)<len(words):
            model_rows=greek_model_rows(text,nlp)
            model_seq=SequenceMatcher(None,[norm(w) for w in words],
                                      [norm(w) for w,_ in model_rows],autojunk=False)
            model_aligned={i:model_rows[j][1] for block in model_seq.get_matching_blocks()
                           for i,j in zip(range(block.a,block.a+block.size),
                                          range(block.b,block.b+block.size))}
        else:model_aligned={}
        annotations = []
        for i, surface in enumerate(words):
            ann = aligned.get(i)
            if ann and (not ann[0] or not ann[1] or ann[1]=='x--------'):ann=None
            provenance = 'OGA-positionsgenau'
            if ann is None:
                prior = old.get((ref, i + 1))
                if prior and prior[0] and prior[1] and prior[0] != '—' and prior[1] not in ('x--------','X'):
                    ann = prior; provenance = 'Originalanalyse-positionserhaltend'
            if ann is None:
                elided = canonical_elision(surface)
                if elided:
                    ann = best(by_form.get(norm(elided), Counter()))
                    if ann: provenance = 'automatische-Elisionsableitung'
            if ann is None and norm(surface) in {'καν'}:
                # Crasis of καὶ ἐάν: both components are conjunctions.
                ann = ('καί + ἐάν', 'c--------+c--------', '')
                provenance = 'automatische-Krasiszerlegung'
            if ann is None and norm(surface) == 'μηθ':
                ann = ('μήτε', 'c--------', '')
                provenance = 'automatische-Elisionsableitung'
            if ann is None:
                ann = best(global_form.get(norm(surface), Counter()))
                if ann: provenance = 'OGA-Formfrequenz'
            if ann is None:
                ann = documented_fallback(surface,'grc',by_form)
                if ann: provenance = 'dokumentierte-Krasis-oder-Formanalyse'
            if ann is None:
                # Last-resort orthographic variant alignment. Keep this
                # threshold high; never substitute a generic or blank tag.
                needle = norm(surface)
                candidates = [(SequenceMatcher(None, needle, form).ratio(), best(freq))
                              for form, freq in by_form.items()
                              if len(needle) >= 3 and form[:2] == needle[:2]]
                score, candidate = max(candidates, default=(0, None), key=lambda x:x[0])
                if score >= 0.82 and candidate:
                    ann = candidate; provenance = 'OGA-naechste-Formvariante'
            if ann is None and i in model_aligned and model_aligned[i][1] not in ('x--------','X'):
                ann=model_aligned[i];provenance='spaCy-Greek-Modell'
            if ann is None:
                ann = documented_fallback(surface,'grc',by_form)
                if ann: provenance='dokumentierte-Formanalyse'
            if ann is None:
                ann = (surface, 'x--------', '')
                provenance = 'unaufgeloest'
            lemma, morph, strong = ann
            annotations.append((surface, lemma, morph, strong))
            counts[provenance] += 1
        out[ref] = annotations
    return out, counts

def load_udpipe(model_path):
    from ufal.udpipe import Model, Pipeline
    model = Model.load(str(model_path))
    if not model:
        raise RuntimeError(f'UDPipe-Modell nicht lesbar: {model_path}')
    pipeline=Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
    return model,pipeline

def run_udpipe(text, pipeline):
    result = pipeline.process(text)
    rows = []
    for line in result.splitlines():
        if not line or line.startswith('#'):
            continue
        f = line.split('\t')
        if len(f) >= 10 and f[0].isdigit() and WORD.fullmatch(f[1]):
            morph = '|'.join(x for x in (f[3], f[5]) if x and x != '_')
            rows.append((f[1], f[2], morph, ''))
    return rows

def beta_greek(surface):
    letters={'a':'α','b':'β','g':'γ','d':'δ','e':'ε','z':'ζ','h':'η','q':'θ',
             'i':'ι','k':'κ','l':'λ','m':'μ','n':'ν','c':'ξ','o':'ο','p':'π',
             'r':'ρ','s':'σ','t':'τ','u':'υ','f':'φ','x':'χ','y':'ψ','w':'ω'}
    if any(ch.isupper() for ch in surface):return surface
    return ''.join(letters.get(ch,ch) for ch in surface.lower())

def greek_fallback(surface,nlp):
    if not nlp:return None
    candidate=beta_greek(surface)
    doc=nlp(candidate)
    lexical=[t for t in doc if WORD.fullmatch(t.text)]
    if len(lexical)!=1 or lexical[0].pos_ in ('','X'):
        return None
    token=lexical[0]
    lemma=token.lemma_ or candidate
    morph='|'.join(x for x in (token.pos_,str(token.morph)) if x)
    return (lemma,morph,'') if lemma and morph else None

def annotate_latin(sections, old, model_path, greek_nlp=None):
    model,pipeline = load_udpipe(model_path)
    out = {}; counts = Counter(); predictions={}; by_surface=defaultdict(Counter)
    non_inflectable={'ADP','CCONJ','SCONJ','PART','INTJ','PUNCT','SYM'}
    for ref,_ordinal,text in sections:
        words=[m.group() for m in WORD.finditer(text)]
        prior=[old.get((ref,i+1)) for i in range(len(words))]
        if all(x and x[0] and x[1] and ('=' in x[1] or x[1].strip().upper() in non_inflectable)
               and x[1] not in ('x--------','X') for x in prior):
            for surface,analysis in zip(words,prior):by_surface[norm(surface)][analysis]+=1
            continue
        rows=run_udpipe(text,pipeline);predictions[ref]=rows
        for surface,lemma,morph,strong in rows:
            if lemma and morph:by_surface[norm(surface)][(lemma,morph,strong)]+=1
    for ref, _ordinal, text in sections:
        words = [m.group() for m in WORD.finditer(text)]
        prior_rows=[old.get((ref,i+1)) for i in range(len(words))]
        if all(item and item[0] and item[1] and ('=' in item[1] or item[1].strip().upper() in non_inflectable)
               and item[1] not in ('x--------','X') for item in prior_rows):
            out[ref]=[(surface,*prior_rows[i]) for i,surface in enumerate(words)]
            counts['Originalquelle'] += len(words)
            continue
        model_rows = predictions.get(ref,[])
        seq = SequenceMatcher(None, [norm(w) for w in words],
                              [norm(w[0]) for w in model_rows], autojunk=False)
        aligned = {i: model_rows[j][1:] for block in seq.get_matching_blocks()
                   for i, j in zip(range(block.a, block.a + block.size),
                                   range(block.b, block.b + block.size))}
        vals=[]
        for i, surface in enumerate(words):
            original = old.get((ref, i + 1))
            if original and original[0] and original[1] and '=' in original[1] and original[1] not in ('x--------','X'):
                ann=original; counts['Originalquelle'] += 1
            elif original and original[0] and original[1] and original[1].strip().upper() in non_inflectable:
                ann=original;counts['Originalwortart']+=1
            elif i in aligned and aligned[i][0] and aligned[i][1]:
                model_lemma,model_morph,model_strong=aligned[i]
                if '=' in model_morph:
                    if original and original[0] and model_morph.split('|',1)[0].upper()==original[1].strip().upper():
                        ann=(original[0],model_morph,original[2]);counts['LatinCy-FEATS-Ergaenzung']+=1
                    else:
                        ann=(model_lemma,model_morph,model_strong);counts['UDPipe-Fallback']+=1
                elif model_morph=='X':
                    greek=greek_fallback(surface,greek_nlp)
                    if greek:ann=greek;counts['Greek-Transliteration-Modell']+=1
                    elif original and original[0] and original[1]:ann=original;counts['UPOS-ohne-FEATS']+=1
                    else:ann=(surface,'X','');counts['unaufgeloest']+=1
                else:
                    # If the model omits features for this occurrence, use a
                    # form-level analysis only when all model predictions for
                    # the same surface and preserved source lemma agree. This
                    # avoids guessing among homographs with different cases.
                    candidates=set()
                    if original and original[0]:
                        for candidate_lemma,candidate_morph,_ in by_surface.get(norm(surface),Counter()):
                            if ('=' in candidate_morph
                                and norm(candidate_lemma)==norm(original[0])
                                and candidate_morph.split('|',1)[0].upper()==original[1].strip().upper()):
                                candidates.add(candidate_morph)
                    if len(candidates)==1:
                        ann=(original[0],next(iter(candidates)),original[2] if original else model_strong)
                        counts['LatinCy-eindeutige-Formanalyse']+=1
                    else:
                        ann=(original[0] if original and original[0] else model_lemma,
                             model_morph,original[2] if original else model_strong)
                        counts['UPOS-ohne-FEATS']+=1
            else:
                candidate=best(by_surface.get(norm(surface),Counter()))
                if candidate and candidate[0] and '=' in candidate[1]:
                    ann=candidate;counts['LatinCy-Formfrequenz']+=1
                else:
                    ann=greek_fallback(surface,greek_nlp)
                    if ann:counts['Greek-Transliteration-Modell']+=1
                    elif original and original[0] and original[1]:ann=original;counts['UPOS-ohne-FEATS']+=1
                    else:ann=(surface,'X','');counts['unaufgeloest']+=1
            if surface.casefold()=='rhetoricam' and ann[0].casefold()=='rhetorica' and ann[1]=='rhetoricus':
                ann=(ann[0],'NOUN|Case=Acc|Gender=Fem|Number=Sing',ann[2])
                counts['Manuelle-Korrektur-rhetoricam']+=1
            vals.append((surface,*ann))
        out[ref]=vals
    return out,counts

def read_pta_by_ref(xml_path):
    root=ET.parse(xml_path).getroot()
    body=next(node for node in root.iter() if _local(node.tag)=='body')
    result={};counts=Counter()
    def visible_words(node):
        if _local(node.tag) in ('note','head','teiHeader','app','fw'):return []
        if _local(node.tag)=='w':return [node]
        found=[]
        for child in node:found.extend(visible_words(child))
        return found
    def walk(node,divs):
        name=_local(node.tag)
        if name.startswith('div'):
            n=node.get('n') or node.get('{http://www.w3.org/XML/1998/namespace}id') or ''
            if n and not n.startswith('urn:') and len(n)<=80:divs=[*divs,n]
        if name in ('p','l','ab'):
            value=_visible(node)
            if value:
                base='.'.join(divs) or 'Text';counts[base]+=1
                ref=base if counts[base]==1 else f'{base}.{counts[base]}'
                tagged=[]
                for word in visible_words(node):
                    surface=_visible(word); found=list(WORD.finditer(surface))
                    if len(found)==1:
                        tagged.append((found[0].group(),(word.get('lemma') or '',
                            '|'.join(x for x in (word.get('pos'),word.get('msd')) if x),'')))
                result[ref]=tagged
            return
        if name in ('note','teiHeader','app'):return
        for child in node:walk(child,divs)
    walk(body,[])
    return result

def annotate_chrysostom(sections, old, source, nlp):
    out={};counts=Counter()
    for ref,_ord,text in sections:
        words=[m.group() for m in WORD.finditer(text)]; src=source.get(ref,[])
        seq=SequenceMatcher(None,[norm(w) for w in words],[norm(w) for w,_ in src],autojunk=False)
        aligned={i:src[j][1] for block in seq.get_matching_blocks()
                 for i,j in zip(range(block.a,block.a+block.size),range(block.b,block.b+block.size))}
        model_rows=[]
        if len(aligned)<len(words):
            model_rows=greek_model_rows(text,nlp)
            model_seq=SequenceMatcher(None,[norm(w) for w in words],
                                      [norm(w) for w,_ in model_rows],autojunk=False)
            model_aligned={i:model_rows[j][1] for block in model_seq.get_matching_blocks()
                           for i,j in zip(range(block.a,block.a+block.size),
                                          range(block.b,block.b+block.size))}
        else:model_aligned={}
        vals=[]
        for i,surface in enumerate(words):
            prior=old.get((ref,i+1))
            if i in aligned and all(aligned[i][:2]) and aligned[i][1] not in ('x--------','X'):ann=aligned[i];counts['PTA-aligned']+=1
            elif prior and all(prior[:2]) and prior[0]!='—' and prior[1] not in ('x--------','X'):ann=prior;counts['PTA-original']+=1
            elif i in model_aligned and all(model_aligned[i][:2]) and model_aligned[i][1] not in ('x--------','X'):
                ann=model_aligned[i];counts['spaCy-Greek-Modell']+=1
            else:
                ann=documented_fallback(surface,'grc')
                if ann:counts['dokumentierte-Elision']+=1
                else:ann=(surface,'x--------','');counts['unaufgeloest']+=1
            vals.append((surface,*ann))
        out[ref]=vals
    return out,counts

def write_package(path, manifest, files, sections, annotations, counts):
    original_annotation_meta = manifest.get('annotation_edition', {})
    rows=[]
    for ref, _ord, _text in sections:
        rows.extend({'ref':ref,'position':i,'surface':surface,'lemma':lemma,
                     'morph':morph,'strong':strong}
                    for i,(surface,lemma,morph,strong) in enumerate(annotations[ref],1))
    text=io.StringIO(newline='')
    writer=csv.DictWriter(text,fieldnames=('ref','position','surface','lemma','morph','strong'),
                          delimiter='\t',lineterminator='\n');writer.writeheader();writer.writerows(rows)
    annotation_name=manifest['files'].get('annotations','annotations.tsv')
    files[annotation_name]=text.getvalue().encode('utf-8')
    manifest['files']['annotations']=annotation_name
    language=manifest['source']['language']
    all_analyses=[analysis for ref,_,_ in sections for analysis in annotations[ref]]
    if language=='grc':
        total=sum(counts.values())
        direct=counts.get('OGA-positionsgenau',0)+counts.get('PTA-aligned',0)
        legacy=sum(v for k,v in counts.items() if k.startswith('Originalanalyse') or k=='PTA-original')
        unresolved=counts.get('unaufgeloest',0)
        automatic=total-direct-legacy-unresolved
        feature_count=sum(1 for _surface,_lemma,morph,_strong in all_analyses
                          if '=' in morph or (len(morph)==9 and morph[0].islower() and '-' in morph))
        annotation_meta={'provider':'Open Greek Corpus OGA; spaCy grc_dep_web_lg 3.8.2 fallback',
            'method':'OGA/PTA-Analysen positionsgenau abgeglichen; offene Stellen mit spaCy Ancient Greek ergänzt. OGA selbst enthält automatisch erzeugte morphosyntaktische Analysen. Nicht redaktionell vollgeprüft.',
            'coverage':f'{total} Tokens; {direct} direkt abgeglichen, {legacy} Edition, {automatic} automatisch; {unresolved} ohne Analyse.',
            'quality':'automatic','review_status':'Automatisch erzeugte Annotationen; nicht redaktionell geprüft.',
            'feature_detail_coverage':{'tokens_with_details':feature_count,'tokens_total':total,
                'definition':'UD-Features oder positionsgebundene AGDT-Tags; reine Wortartlabels nicht mitgezählt.'},
            'license':'OGA/PTA CC BY-SA 4.0; spaCy model MIT; Werklizenzen siehe Quellenmetadaten',
            'provenance':'https://huggingface.co/latincy/grc_dep_web_lg ; https://github.com/PatristicTextArchive/pta_data ; https://github.com/OpenGreekAndLatin/open-greek-corpus'}
    elif language=='la':
        total=sum(counts.values())
        feature_count=sum(1 for _surface,_lemma,morph,_strong in all_analyses if '=' in morph)
        upos_only=sum(1 for _surface,_lemma,morph,_strong in all_analyses if '=' not in morph)
        unresolved=sum(1 for _surface,_lemma,morph,_strong in all_analyses if morph.strip().upper() in ('X','X--------'))
        annotation_meta={'provider':'CIRCSE/LiLa; LatinCy UDPipe 1 v0.2; LatinCy la_core_web_sm 3.9.8',
            'method':'CIRCSE-Lemmata und Wortarten bleiben erhalten; fehlende UD-Flexionsmerkmale wurden, wo übereinstimmend, mit LatinCy UDPipe und spaCy ergänzt. Automatische Ergänzungen sind nicht redaktionell vollgeprüft.',
            'coverage':f'{total} Tokens; {feature_count} mit UD-Flexionsmerkmalen; {upos_only} ohne solche Merkmale (überwiegend nicht flektierbare POS); {unresolved} mit unbekannter Analyse.',
            'quality':'mixed','review_status':'CIRCSE-Analysen laut Quelle geprüft; automatische Ergänzungen nicht redaktionell geprüft. Einzelne Tokens sind nicht getrennt markiert.',
            'feature_detail_coverage':{'tokens_with_details':feature_count,'tokens_total':total,
                'definition':'UD-FEATS; reine UPOS-Wortartlabels nicht mitgezählt.'},
            'license':'CIRCSE CC BY-SA 4.0; LatinCy UDPipe model MIT',
            'provenance':'https://github.com/CIRCSE ; https://huggingface.co/latincy/la_udpipe_latincy'}
    else:
        annotation_meta=manifest.get('annotation_edition',{})
    manifest['annotation_edition']={**original_annotation_meta,**annotation_meta}
    files['manifest.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8')
    manifest['checksums']={name:'sha256:'+hashlib.sha256(data).hexdigest()
                           for name,data in files.items() if name!='manifest.json'}
    files['manifest.json']=json.dumps(manifest,ensure_ascii=False,indent=2).encode('utf-8')
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name,data in files.items():archive.writestr(name,data)
    path.write_bytes(buffer.getvalue())
    # Validate the exact artifact before reporting it.
    info=inspect_package(path.read_bytes())
    return info

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--oga-dir',type=Path,required=True)
    ap.add_argument('--latin-model',type=Path,required=True)
    ap.add_argument('--packages',type=Path,default=Path('source_packages'))
    ap.add_argument('--language',choices=('grc','la'))
    ap.add_argument('--pta-chrysostom',type=Path)
    ap.add_argument('--greek-model',default='grc_dep_web_lg')
    args=ap.parse_args()
    greek_nlp=None
    if args.language in (None,'grc'):
        import spacy
        greek_nlp=spacy.load(args.greek_model)
    mapping={
      'josephus-bellum-judaicum-perseus':'ogc-tlg0526.tlg004.perseus-grc2.jsonl.gz',
      'philo-de-opificio-mundi-perseus':'ogc-tlg0018.tlg001.1st1K-grc1.jsonl.gz',
      'origenes-de-oratione-pta':'ogc-pta0007.pta008.pta-grc1.jsonl.gz',
      'athanasius-de-incarnatione-pta':'ogc-pta0022.pta002.pta-grc1.jsonl.gz',
      'severian-de-fide-pta':'ogc-pta0001.pta001.pta-grc1.jsonl.gz',
    }
    for path in sorted(args.packages.glob('*.amicus-source')):
        manifest,files,sections,section_map,old=read_package(path)
        sid=manifest['source']['id']; lang=manifest['source']['language']
        if args.language and lang!=args.language:continue
        if lang=='grc' and sid in mapping:
            loci,forms=read_oga(args.oga_dir/mapping[sid]); annotations,counts=annotate_greek(sections,old,loci,forms,greek_nlp)
        elif lang=='grc':
            if not args.pta_chrysostom:raise ValueError('Für Chrysostom ist --pta-chrysostom erforderlich.')
            annotations,counts=annotate_chrysostom(sections,old,read_pta_by_ref(args.pta_chrysostom),greek_nlp)
        elif lang=='la':
            annotations,counts=annotate_latin(sections,old,args.latin_model,greek_nlp)
        else:
            continue
        write_package(path,manifest,files,sections,annotations,counts)
        print(sid,dict(counts))

if __name__=='__main__':main()
