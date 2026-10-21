#!/usr/bin/env python3
"""Build complete annotated CIRCSE packages for Augustine's major Latin works."""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend import sources
from backend.sources import WORD, read_conllu
from tools.build_starter_source_packages import package


WORKS = [
    {
        'arg': 'civitate', 'file': 'Augustinus_Civitate.conllu',
        'id': 'augustinus-de-civitate-dei-circse',
        'filename': 'amicus-latein-augustinus-de-civitate-dei.amicus-source',
        'title': 'Augustinus · De civitate Dei', 'edition': 'CIRCSE · The Latin Library digitaler Text',
        'url': 'https://github.com/CIRCSE/AugustiniDeCiuitateDei', 'version': 'CIRCSE-Commit (Quellstand 2026-10)',
        'opening': 'Die glorreiche Stadt Gottes, die in diesem Lauf der Zeiten als Glaubende unter den Gottlosen pilgert …',
        'translation_id': 'de-bkv-schroeder',
        'translation_language': 'de',
        'translation_title': 'Zweiundzwanzig Bücher über den Gottesstaat (BKV)',
        'translation_author': 'Augustinus; deutsch von Alfred Schröder',
        'translation_edition': 'Bibliothek der Kirchenväter, Kempten/München 1911–1916',
        'translation_provenance': 'https://bkv.unifr.ch/de/works/cpl-313/versions/zweiundzwanzig-bucher-uber-den-gottesstaat-bkv',
    },
    {
        'arg': 'trinitate', 'file': 'Augustinus_Trinitate_complete.conll',
        'id': 'augustinus-de-trinitate-circse',
        'filename': 'amicus-latein-augustinus-de-trinitate.amicus-source',
        'title': 'Augustinus · De Trinitate', 'edition': 'CIRCSE · The Latin Library digitaler Text',
        'url': 'https://github.com/CIRCSE/AugustiniDeTrinitate', 'version': 'CIRCSE-Commit (Quellstand 2026-10)',
        'opening': 'Augustinus grüßt im Herrn den seligen, durch aufrichtige Liebe verehrten heiligen Bruder und Mitbischof Papst Aurelius.',
        'translation_id': 'en-npnf-haddan',
        'translation_language': 'en',
        'translation_title': 'The Fifteen Books of Aurelius Augustinus on the Trinity',
        'translation_author': 'Augustine; translated by Arthur West Haddan',
        'translation_edition': 'Nicene and Post-Nicene Fathers, First Series, vol. 3 (1890)',
        'translation_provenance': 'https://www.ccel.org/ccel/schaff/npnf103.html',
    },
]


def build(spec, source_path, translation_path=None):
    # The package validator has the larger, explicit 145 MB limit; here the
    # curated CIRCSE source exceeds the ordinary ad-hoc upload limit.
    sources.MAX_FILE = 60_000_000
    rows, annotations, skipped = read_conllu(source_path.read_bytes())
    text_by_ref = {ref: text for ref, _ordinal, text in rows}
    words = []
    incomplete = 0
    for ref, items in annotations.items():
        surfaces = [m.group() for m in WORD.finditer(text_by_ref[ref])]
        if len(surfaces) != len(items) or any(not lemma for lemma, _morph, _strong in items):
            incomplete += 1
            continue
        words.extend({'ref': ref, 'position': pos, 'surface': surfaces[pos - 1],
                      'lemma': lemma or '', 'morph': morph or '', 'strong': strong or ''}
                     for pos, (lemma, morph, strong) in enumerate(items, 1))
    if not rows:
        raise SystemExit(f"Keine Textabschnitte in {spec['arg']}/{spec['file']}")
    de = {'id': 'de-arbeitsuebersetzung', 'language': 'de',
          'title': 'Deutsche Arbeitsübersetzung (Auszug)', 'author': 'Amicus Theologi · Arbeitsübersetzung',
          'edition': 'Arbeitsübersetzung 1.0', 'license': 'CC BY 4.0',
          'provenance': 'Für dieses Paket neu erstellt; nur der erste Abschnitt ist übersetzt.'}
    first_ref = rows[0][0]
    translations = [{'ref': first_ref, 'translation_id': de['id'], 'text': spec['opening']}]
    editions = [de]
    if translation_path:
        edition = {'id': spec['translation_id'], 'language': spec['translation_language'], 'title': spec['translation_title'],
                   'author': spec['translation_author'], 'edition': spec['translation_edition'],
                   'license': 'Public Domain (BKV-Angabe)', 'provenance': spec['translation_provenance']}
        editions.append(edition)
        translations.append({'ref': '@work', 'translation_id': edition['id'],
                             'text': translation_path.read_text(encoding='utf-8-sig').strip()})
    package(Path('source_packages') / spec['filename'],
        {'id': spec['id'], 'title': spec['title'], 'author': 'Augustinus von Hippo', 'language': 'la',
         'edition': spec['edition'], 'license': 'CC BY-SA 4.0', 'provenance': spec['url'],
         'version': spec['version']},
        [(ref, text) for ref, _ordinal, text in rows], words, translations, editions,
        {'provider': 'CIRCSE / LiLa', 'method': 'UDPipe; manuell nachkontrollierte CoNLL-U-Annotationen.',
         'coverage': f'{len(words)} Wortanalysen; {incomplete} Sätze ohne importierbare Analyse; FEATS lückenhaft; {skipped} weitere Sätze nicht positionsgenau zuordenbar.',
         'quality':'mixed','review_status':'CIRCSE/LiLa-Quelle; fehlende FEATS werden im Quellenpaket modellbasiert ergänzt und sind nicht redaktionell geprüft.',
         'license': 'CC BY-SA 4.0', 'provenance': spec['url']},
        'CIRCSE sent_id; Satzabschnitte der Quelldatei',
        f"Vollständiger lateinischer Text; Übersetzungsauszug nur zum ersten Abschnitt ({first_ref}).")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--civitate', type=Path, required=True)
    parser.add_argument('--trinitate', type=Path, required=True)
    parser.add_argument('--civitate-translation', type=Path)
    parser.add_argument('--trinitate-translation', type=Path)
    args = parser.parse_args()
    build(WORKS[0], args.civitate, args.civitate_translation)
    build(WORKS[1], args.trinitate, args.trinitate_translation)


if __name__ == '__main__':
    main()
