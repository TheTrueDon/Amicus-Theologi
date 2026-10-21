#!/usr/bin/env python3
"""Package complete PTA Greek texts with their open BKV German translations."""
import argparse
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend import sources
from backend.sources import WORD, read_tei_annotated
from tools.build_starter_source_packages import package

WORKS = [
    {
        'key': 'origen', 'title': 'Origenes · De oratione', 'author': 'Origenes von Alexandria',
        'id': 'origenes-de-oratione-pta', 'filename': 'amicus-griechisch-origenes-de-oratione.amicus-source',
        'translation_title': 'Vom Gebet (BKV)', 'translation_author': 'Origenes; deutsch von Paul Koetschau',
        'translation_edition': 'Origenes, Schriften vom Gebet und Ermahnung zum Martyrium, BKV',
        'translation_url': 'https://bkv.unifr.ch/de/works/cpg-1477/versions/vom-gebet-bkv',
        'opening': 'PTA file: pta0007/pta008/pta0007.pta008.pta-grc1.xml',
    },
    {
        'key': 'athanas', 'title': 'Athanasius · De incarnatione Verbi', 'author': 'Athanasius von Alexandria',
        'id': 'athanasius-de-incarnatione-pta', 'filename': 'amicus-griechisch-athanasius-de-incarnatione.amicus-source',
        'translation_title': 'Über die Menschwerdung des Logos (BKV)', 'translation_author': 'Athanasius; deutsche BKV-Übersetzung',
        'translation_edition': 'Athanasius, Ausgewählte Schriften, Band 2, BKV',
        'translation_url': 'https://bkv.unifr.ch/de/works/cpg-2091/versions/uber-die-menschwerdung-des-logos-und-dessen-leibliche-erscheinung-unter-uns-bkv',
        'opening': 'PTA file: pta0022/pta002/pta0022.pta002.pta-grc1.xml',
    },
    {
        'key': 'chrysostom', 'title': 'Johannes Chrysostomus · In epistulam ad Colossenses homiliae 1–12',
        'author': 'Johannes Chrysostomus', 'id': 'chrysostomus-colossenses-pta',
        'filename': 'amicus-griechisch-chrysostomus-colossenses.amicus-source',
        'translation_title': 'Kommentar zum Brief an die Kolosser (BKV)',
        'translation_author': 'Johannes Chrysostomus; deutsch von Wenzel Stoderl',
        'translation_edition': 'Kommentar zu den Briefen des hl. Paulus, BKV',
        'translation_url': 'https://bkv.unifr.ch/de/works/cpg-4433/versions/kommentar-zum-briefe-des-hl-paulus-an-die-kolosser-bkv',
        'opening': 'PTA file: pta0002/pta161/pta0002.pta161.pta-grc1.xml',
    },
]


def lname(tag):
    return tag.rsplit('}', 1)[-1]


def edition_metadata(spec, xml):
    root = ET.fromstring(xml)
    title = next((n.text.strip() for n in root.iter() if lname(n.tag) == 'title' and n.text and n.attrib.get('level') != 'm'), spec['title'])
    author = next((n.text.strip() for n in root.iter() if lname(n.tag) == 'author' for n in n.iter() if lname(n.tag) == 'persName' and n.text), spec['author'])
    target = next((n.attrib.get('target', '').rstrip('/') for n in root.iter() if lname(n.tag) == 'licence'), '')
    if '/licenses/by-sa/4.0' in target:
        licence = 'CC BY-SA 4.0'
    elif '/licenses/by/4.0' in target:
        licence = 'CC BY 4.0'
    else:
        licence = 'CC BY-SA 4.0'
    return title, author, licence


def build(spec, source_path, translation_path):
    raw = source_path.read_bytes()
    title, author, licence = edition_metadata(spec, raw)
    rows, annotations, skipped = read_tei_annotated(raw)
    text_by_ref = {ref: text for ref, _ordinal, text in rows}
    word_rows = []
    uncovered = 0
    for ref, items in annotations.items():
        surfaces = [m.group() for m in WORD.finditer(text_by_ref[ref])]
        if len(surfaces) != len(items) or any(not lemma for lemma, _morph, _strong in items):
            uncovered += 1
            continue
        word_rows.extend({'ref': ref, 'position': pos, 'surface': surfaces[pos - 1],
                          'lemma': lemma, 'morph': morph or '', 'strong': strong or ''}
                         for pos, (lemma, morph, strong) in enumerate(items, 1))
    edition = {'id': 'de-bkv', 'language': 'de', 'title': spec['translation_title'],
               'author': spec['translation_author'], 'edition': spec['translation_edition'],
               'license': 'Public Domain (BKV-Angabe)', 'provenance': spec['translation_url']}
    translation = {'ref': '@work', 'translation_id': edition['id'],
                   'text': translation_path.read_text(encoding='utf-8-sig').strip()}
    source = {'id': spec['id'], 'title': spec['title'], 'author': spec['author'], 'language': 'grc',
              'edition': 'Patristic Text Archive · PTA TEI-Edition',
              'license': licence, 'provenance': 'https://github.com/PatristicTextArchive/pta_data',
              'version': 'PTA-Commit 524eb97'}
    package(Path('source_packages') / spec['filename'], source,
        [(ref, text) for ref, _ordinal, text in rows], word_rows, [translation], [edition],
        {'provider': 'Patristic Text Archive / spaCy',
         'method': 'Automatisch erzeugte TEI-Wortanalyse; nicht redaktionell geprüft.',
         'coverage': f'{len(word_rows)} Wortanalysen; {uncovered} Abschnitte ausgelassen; {skipped} Abschnitte nicht zuordenbar.',
         'quality':'automatic','review_status':'Automatische PTA-/Modellanalysen; nicht redaktionell geprüft.',
         'license': licence, 'provenance': 'https://github.com/PatristicTextArchive/pta_data'},
        'PTA-CTS-URN-Abschnitte',
        f"Vollständiger griechischer Text; vollständige BKV-Gesamtübersetzung enthalten. "
        f"Quelle: {spec['opening']}")


def main():
    p = argparse.ArgumentParser()
    for name in ('origen', 'athanas', 'chrysostom'):
        p.add_argument('--' + name, type=Path, required=True)
        p.add_argument('--' + name + '-translation', type=Path, required=True)
    args = p.parse_args()
    for spec in WORKS:
        build(spec, getattr(args, spec['key']), getattr(args, spec['key'] + '_translation'))


if __name__ == '__main__':
    main()
