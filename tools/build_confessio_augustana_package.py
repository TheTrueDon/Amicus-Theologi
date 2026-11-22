#!/usr/bin/env python3
"""Build the offline Amicus source package from the CA generator's exports."""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.sources import read_source
from tools.build_starter_source_packages import package


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--exports', type=Path, required=True,
                        help='Generatorordner EXPORT_28_ARTIKEL')
    parser.add_argument('--out', type=Path,
                        default=Path('source_packages/amicus-latein-confessio-augustana.amicus-source'))
    args = parser.parse_args()
    sections = read_source((args.exports / 'CA_VOLLSTAENDIG_28_Artikel_TEXT.csv').read_bytes())
    with (args.exports / 'CA_VOLLSTAENDIG_28_Artikel_WORTDATEN.tsv').open(
            encoding='utf-8-sig', newline='') as stream:
        annotations = list(csv.DictReader(stream, delimiter='\t'))
    with (args.exports / 'CA_ABDECKUNG_UND_QUELLEN.json').open(encoding='utf-8') as stream:
        summary = __import__('json').load(stream)
    source = {
        'id': 'confessio-augustana-latin',
        'title': 'Confessio Augustana · Latein, 28 Artikel',
        'author': 'Philipp Melanchthon', 'language': 'la',
        'edition': 'Concordia, Lipsiae 1584; Wikisource-Transkription',
        'license': 'Wikisource CC BY-SA 4.0; historischer Wortlaut gemeinfrei',
        'provenance': 'https://la.wikisource.org/wiki/Confessio_Augustana',
        'version': 'Wikisource-Transkription 2026-11-22; Stanza-Modellanalyse',
    }
    annotation_edition = {
        'provider': 'Stanza 1.8.2 · Latin pipeline',
        'method': 'Automatisch vorhergesagte Lemmata und Universal-Dependencies-Merkmale; nicht fachwissenschaftlich geprüft.',
        'coverage': (f"{summary['word_positions']} von {summary['word_positions']} Wortpositionen annotiert. "
                     f"Deutsche Wörterbuchbedeutungen für {summary['german_gloss_covered_positions']} Wortvorkommen; "
                     'die Bedeutungen sind keine kontextgeprüfte Satzübersetzung.'),
        'license': 'Stanza Apache-2.0; Wikisource-Text CC BY-SA 4.0; siehe Quellenhinweise im Projekt.',
        'provenance': 'https://la.wikisource.org/wiki/Confessio_Augustana; https://github.com/stanfordnlp/stanza',
        'quality': 'automatic',
        'review_status': 'Automatische Modellvorhersage; nicht vollständig fachwissenschaftlich geprüft.',
        'codes_recognized_by_decoder': {'tokens': summary['word_positions'],
                                        'tokens_total': summary['word_positions']},
        'feature_detail_coverage': {'tokens': summary['word_positions'],
                                    'tokens_total': summary['word_positions'], 'percent': 100.0},
    }
    package(args.out, source, [(ref, text) for ref, _ordinal, text in sections],
            annotations, [], [], annotation_edition,
            'Artikel und nummerierte Abschnitte I.1–XXVIII.',
            (f"Volltext aller 28 Artikel; {len(sections)} Abschnitte, "
             f"{summary['word_positions']} automatisch analysierte Wortpositionen."))


if __name__ == '__main__':
    main()
