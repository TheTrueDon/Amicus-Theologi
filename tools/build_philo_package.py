#!/usr/bin/env python3
"""Build Philo's De opificio mundi from Perseus TEI and the BKV translation."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.sources import read_tei
from tools.build_starter_source_packages import package


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--greek', type=Path, required=True, help='First1KGreek Perseus TEI, grc1')
    parser.add_argument('--english', type=Path, required=True, help='First1KGreek Perseus TEI, eng1')
    parser.add_argument('--german', type=Path, required=True, help='BKV German translation as UTF-8 text')
    parser.add_argument('--out', type=Path, default=Path('source_packages'))
    args = parser.parse_args()

    greek = read_tei(args.greek.read_bytes())
    english = read_tei(args.english.read_bytes())
    editions = [
        {'id': 'de-bkv-philo', 'language': 'de', 'title': 'Über die Weltschöpfung (BKV)',
         'author': 'Philon von Alexandria; deutsch von Leopold Cohn',
         'edition': 'Die Werke Philos von Alexandria, Erster Teil; Schriften der jüdisch-hellenistischen Literatur',
         'license': 'Public Domain (historische Ausgabe)',
         'provenance': 'https://bkv.unifr.ch/de/works/x-5/versions/uber-die-weltschopfung'},
        {'id': 'en-yonge-philo', 'language': 'en', 'title': 'On the Creation (Perseus)',
         'author': 'Philo Judaeus; translated by Charles Duke Yonge',
         'edition': 'The Works of Philo, translated by C. D. Yonge (1854–1890); Perseus/First1KGreek',
         'license': 'CC BY-SA 4.0 (First1KGreek TEI distribution)',
         'provenance': 'https://github.com/OpenGreekAndLatin/First1KGreek'},
    ]
    translations = [
        {'ref': '@work', 'translation_id': 'de-bkv-philo',
         'text': args.german.read_text(encoding='utf-8-sig').strip()},
        {'ref': '@work', 'translation_id': 'en-yonge-philo',
         'text': '\n\n'.join(text for _ref, _ordinal, text in english)},
    ]
    package(args.out / 'amicus-griechisch-philo-de-opificio-mundi.amicus-source',
        {'id': 'philo-de-opificio-mundi-perseus', 'title': 'Philon von Alexandria · De opificio mundi',
         'author': 'Philon von Alexandria', 'language': 'grc',
         'edition': 'Leopold Cohn, Philonis Alexandrini opera quae supersunt, Band 1; Perseus/First1KGreek TEI',
         'license': 'CC BY-SA 4.0 (First1KGreek TEI distribution)',
         'provenance': 'https://github.com/OpenGreekAndLatin/First1KGreek',
         'version': 'First1KGreek GitHub distribution; Greek work urn:cts:greekLit:tlg0018.tlg001'},
        [(ref, text) for ref, _ordinal, text in greek], [], translations, editions,
        {'provider': 'Keine mitgelieferte morphologische Edition',
         'method': 'Keine Lemma- oder Morphologieangaben übernommen; der griechische Quelltext ist vollständig.',
         'coverage': '0 Wortanalysen; keine Morphologie im ausgewählten First1KGreek-TEI-Datensatz.',
         'license': 'Nicht zutreffend', 'provenance': 'https://github.com/OpenGreekAndLatin/First1KGreek'},
        'Philonis De opificio mundi, paragraph sequence (Perseus CTS work)',
        'Vollständiger griechischer Text; vollständige deutsche BKV- und englische Yonge-Gesamtübersetzung. '
        'Keine morphologische Analyse enthalten.')


if __name__ == '__main__':
    main()
