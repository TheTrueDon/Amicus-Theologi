#!/usr/bin/env python3
"""Build Josephus' Jewish War from the Perseus Greek and Whiston TEI editions."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.sources import read_tei
from tools.build_starter_source_packages import package


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--greek', type=Path, required=True, help='Perseus Greek TEI')
    parser.add_argument('--english', type=Path, required=True, help='Perseus/Whiston English TEI')
    parser.add_argument('--out', type=Path, default=Path('source_packages'))
    args = parser.parse_args()
    greek = read_tei(args.greek.read_bytes())
    english = read_tei(args.english.read_bytes())
    edition = {'id': 'en-whiston-josephus-war', 'language': 'en',
        'title': 'The Jewish War (Perseus)', 'author': 'Flavius Josephus; translated by William Whiston',
        'edition': 'Perseus Digital Library TEI; Whiston translation, 1895 edition',
        'license': 'Public Domain (historical translation)',
        'provenance': 'https://catalog.perseus.org/catalog/urn:cts:greekLit:tlg0526.tlg004.perseus-eng1'}
    package(args.out / 'amicus-griechisch-josephus-bellum-judaicum.amicus-source',
        {'id': 'josephus-bellum-judaicum-perseus', 'title': 'Flavius Josephus · Bellum Judaicum',
         'author': 'Flavius Josephus', 'language': 'grc',
         'edition': 'Benedikt Niese, Flavii Iosephi opera; Perseus Digital Library TEI',
         'license': 'CC BY-SA 4.0 (Perseus TEI distribution)',
         'provenance': 'https://catalog.perseus.org/catalog/urn:cts:greekLit:tlg0526.tlg004',
         'version': 'Perseus canonical-greekLit TEI, work tlg0526.tlg004'},
        [(ref, text) for ref, _ordinal, text in greek], [],
        [{'ref': '@work', 'translation_id': edition['id'],
          'text': '\n\n'.join(text for _ref, _ordinal, text in english)}], [edition],
        {'provider': 'Keine mitgelieferte morphologische Edition',
         'method': 'Keine Lemma- oder Morphologieangaben übernommen.',
         'coverage': 'Vollständiger griechischer Text, keine Wortanalysen in der verwendeten Edition.',
         'license': 'Nicht zutreffend', 'provenance': 'https://catalog.perseus.org/catalog/urn:cts:greekLit:tlg0526.tlg004'},
        'Bellum Judaicum book.chapter.section (Perseus CTS)',
        'Vollständiger griechischer Text in sieben Büchern und vollständige englische Whiston-Gesamtübersetzung; keine Morphologie enthalten.')


if __name__ == '__main__':
    main()
