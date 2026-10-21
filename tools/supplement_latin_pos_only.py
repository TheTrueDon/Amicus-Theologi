#!/usr/bin/env python3
"""Supplement edition Latin analyses that contain only an inflectable UPOS."""
from collections import Counter
from pathlib import Path
from difflib import SequenceMatcher
import spacy

from complete_source_annotations import norm, read_package, write_package
from backend.sources import WORD


def supplement(path: Path, nlp):
    manifest, files, sections, _section_map, old = read_package(path)
    if manifest['source']['language'] != 'la':
        return 0
    inflectable = {'NOUN', 'PROPN', 'ADJ', 'PRON', 'DET', 'VERB', 'AUX', 'NUM'}
    result = {}
    changed = 0
    for ref, _ordinal, text in sections:
        words = [m.group() for m in WORD.finditer(text)]
        rows = [old.get((ref, i + 1), ('', '', '')) for i in range(len(words))]
        needs_model = any(
            len(row) >= 2 and row[0] and row[1].strip().upper() in inflectable
            and '=' not in row[1] and row[1] not in ('X', 'x--------')
            for row in rows
        )
        model_rows = []
        if needs_model:
            for token in nlp(text):
                if not WORD.fullmatch(token.text):
                    continue
                morph = '|'.join(x for x in (token.pos_, str(token.morph)) if x)
                model_rows.append((token.text, token.lemma_ or token.text, morph))
        seq = SequenceMatcher(None, [norm(w) for w in words],
                              [norm(row[0]) for row in model_rows], autojunk=False)
        aligned = {i: model_rows[j][1:] for block in seq.get_matching_blocks()
                   for i, j in zip(range(block.a, block.a + block.size),
                                   range(block.b, block.b + block.size))}
        vals = []
        for i, surface in enumerate(words):
            lemma, morph, strong = rows[i]
            if (lemma and morph.strip().upper() in inflectable and '=' not in morph
                    and i in aligned):
                model_lemma, model_morph = aligned[i]
                model_upos = model_morph.split('|', 1)[0].upper()
                same_lemma = norm(model_lemma) == norm(lemma)
                if ('=' in model_morph
                        and (model_upos == morph.strip().upper() or same_lemma)):
                    morph = model_morph
                    changed += 1
            vals.append((surface, lemma or surface, morph or 'X', strong))
        result[ref] = vals
    if changed:
        total = sum(len(rows) for rows in result.values())
        write_package(path, manifest, files, sections, result,
                      Counter({'Originalquelle': total - changed,
                               'LatinCy-spaCy-FEATS-Ergaenzung': changed}))
    return changed


if __name__ == '__main__':
    model = spacy.load('la_core_web_sm')
    root = Path(__file__).resolve().parents[1] / 'source_packages'
    for package in sorted(root.glob('*.amicus-source')):
        count = supplement(package, model)
        if count:
            print(package.name, count)
