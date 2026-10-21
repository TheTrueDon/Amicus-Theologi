#!/usr/bin/env python3
"""Build the first offline ASPK packages from separately obtained open data.

Inputs are deliberately not vendored in this script. Use the matching source
archives listed in source_packages/README.md and pass their local paths.
"""
import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.sources import WORD, read_conllu, read_tei_annotated
from backend.source_import import parse_oshb


def csv_bytes(rows, columns, delimiter=','):
    out=io.StringIO(newline='')
    writer=csv.DictWriter(out,fieldnames=columns,delimiter=delimiter,lineterminator='\n')
    writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf-8')


def package(path, source, sections, annotations, translations, translation_editions,
            annotation_edition, reference_scheme, scope):
    files={'sections.csv':csv_bytes([{'ref':r,'text':t} for r,t in sections],('ref','text')),
           'translations.csv':csv_bytes(translations,('ref','translation_id','text'))}
    if annotations:
        files['annotations.tsv']=csv_bytes(annotations,('ref','position','surface','lemma','morph','strong'), '\t')
    manifest={'format':'amicus-source-package','format_version':1,'source':source,
        'reference_scheme':reference_scheme,'scope':scope,'annotation_edition':annotation_edition,
        'translation_editions':translation_editions,
        'files':{'sections':'sections.csv','translations':'translations.csv',
                 **({'annotations':'annotations.tsv'} if annotations else {})},
        'checksums':{name:'sha256:'+hashlib.sha256(data).hexdigest() for name,data in files.items()}}
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr('manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        for name,data in files.items():z.writestr(name,data)
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(out.getvalue())
    print(f'{path}: {len(sections)} Abschnitte, {len(annotations)} Analysen, {len(translations)} Übersetzungen, {len(out.getvalue()):,} Bytes')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--circse',type=Path,required=True,help='CIRCSE Confessiones_complete.conllu')
    parser.add_argument('--pta',type=Path,required=True,help='PTA analyzed Severian TEI XML')
    parser.add_argument('--oshb-genesis',type=Path,required=True,help='Open Scriptures morphhb/wlc/Gen.xml')
    parser.add_argument('--genesis-translation',type=Path,help='Luther 1912 OSIS XML (full book)')
    parser.add_argument('--confessions-translation',type=Path,help='Vollständige BKV-Übersetzung, als UTF-8-Text')
    parser.add_argument('--out',type=Path,default=Path('source_packages'))
    args=parser.parse_args()
    de={'id':'de-arbeitsuebersetzung','language':'de','title':'Deutsche Arbeitsübersetzung',
        'author':'Amicus Theologi · Arbeitsübersetzung','edition':'Starterpaket 1.0',
        'license':'CC BY 4.0','provenance':'Für dieses Paket neu erstellt; keine Verlagsübersetzung.'}

    rows,annotations,_=read_conllu(args.circse.read_bytes())
    # The complete original work and the CIRCSE/LiLa sentence annotations are
    # included. The new German translation is intentionally limited to the opening.
    translations=[{'ref':rows[0][0],'translation_id':de['id'],'text':'Groß bist du, Herr, und sehr des Lobes würdig.'},
                  {'ref':rows[1][0],'translation_id':de['id'],'text':'Groß ist deine Macht, und deiner Weisheit ist keine Zahl.'}]
    latin_editions=[de]
    if args.confessions_translation:
        bkv={'id':'de-bkv-hofmann','language':'de','title':'Bekenntnisse (BKV)',
             'author':'Augustinus; deutsch von Alfred Hofmann',
             'edition':'Bibliothek der Kirchenväter, München 1914',
             'license':'Public Domain (BKV-Angabe)',
             'provenance':'https://bkv.unifr.ch/de/works/cpl-251/versions/aug-conf-bkv'}
        latin_editions.append(bkv)
        translations.append({'ref':'@work','translation_id':bkv['id'],
                             'text':args.confessions_translation.read_text(encoding='utf-8-sig').strip()})
    text_by_ref={r:t for r,_n,t in rows}
    latin_ann=[]
    for ref,items in annotations.items():
        surfaces=[m.group() for m in WORD.finditer(text_by_ref[ref])]
        if len(surfaces)!=len(items):continue
        latin_ann.extend({'ref':ref,'position':pos,'surface':surfaces[pos-1],'lemma':lemma or '',
            'morph':morph or '', 'strong':strong or ''}
            for pos,(lemma,morph,strong) in enumerate(items,1))
    package(args.out/'amicus-latin-augustinus-confessiones.amicus-source',
        {'id':'augustinus-confessiones-circse','title':'Augustinus · Confessiones',
         'author':'Augustinus von Hippo','language':'la','edition':'CIRCSE · The Latin Library digitaler Text',
         'license':'CC BY-SA 4.0 (CIRCSE-Datensatz; Quellenangaben im Paket)','provenance':'CIRCSE / LiLa, Università Cattolica del Sacro Cuore; https://github.com/CIRCSE/AugustiniConfessiones',
         'version':'CIRCSE-Commit 02fc680'},
        [(r,t) for r,_n,t in rows],latin_ann,translations,latin_editions,
        {'provider':'CIRCSE / LiLa','method':'UDPipe, nachträglich manuell kontrolliert; CoNLL-U lemma + UPOS',
         'coverage':'Lemmata und Wortarten für zuordenbare Worttokens; FEATS sind in diesem Datensatz nicht durchgehend vorhanden.',
         'quality':'mixed','review_status':'CIRCSE/LiLa-Quelle; fehlende FEATS können automatisch ergänzt sein.',
         'license':'CC BY-SA 4.0','provenance':'https://github.com/CIRCSE/AugustiniConfessiones'},
        'CIRCSE sent_id, Bücher und Sätze','Vollständiger lateinischer Text; deutsche Arbeitsübersetzung nur zu den ersten zwei Sätzen.')

    rows,annotations,skipped=read_tei_annotated(args.pta.read_bytes())
    refs={'7.2'}
    greek_sections=[(r,t) for r,_n,t in rows]
    greek_text={r:t for r,_n,t in rows};greek_ann=[]
    for ref,items in annotations.items():
        surfaces=[m.group() for m in WORD.finditer(greek_text[ref])]
        if len(surfaces)!=len(items):continue
        greek_ann.extend({'ref':ref,'position':pos,'surface':surfaces[pos-1],'lemma':lemma or '',
            'morph':morph or '', 'strong':strong or ''}
            for pos,(lemma,morph,strong) in enumerate(items,1))
    package(args.out/'amicus-griechisch-severian.amicus-source',
        {'id':'severian-de-fide-pta','title':'Severian von Gabala · De fide et lege naturae',
         'author':'Severianus Gabalensis','language':'grc','edition':'Patrologia Graeca 48, 1081–1088; PTA TEI-Edition',
         'license':'CC BY-SA 4.0','provenance':'Patristic Text Archive, Berlin-Brandenburgische Akademie der Wissenschaften; https://github.com/PatristicTextArchive/pta_data',
         'version':'PTA-Commit 524eb97'},
        greek_sections,greek_ann,[{'ref':'7.2','translation_id':de['id'],
            'text':'Doch kehren wir wieder zum eigentlichen Gegenstand zurück.'}],[de],
        {'provider':'PTA / spaCy grc_dep_web_lg','method':'Automatische Wortanalyse aus der TEI-Edition; nicht redaktionell geprüft.',
         'coverage':'Positionsgenaue Lemma-, Wortart- und Merkmalsdaten nur für Stellen mit passender Tokenisierung; Gesamtdatei meldet '+str(skipped)+' nicht zuordenbare Abschnitte.',
         'quality':'automatic','review_status':'PTA-Analyse automatisch erzeugt; nicht redaktionell geprüft.',
         'license':'CC BY-SA 4.0','provenance':'https://github.com/PatristicTextArchive/pta_data'},
        'PTA-CTS-URN-Abschnitte','Vollständiger digitaler PTA-Text; deutsche Arbeitsübersetzung für Abschnitt 7.2.')

    # Parse the official OSHB XML through the same importer used by Amicus.
    xml=args.oshb_genesis.read_bytes();mem=io.BytesIO()
    with zipfile.ZipFile(mem,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('morphhb/wlc/Gen.xml',xml)
    verses,tokens,_=parse_oshb(mem.getvalue())
    genesis_tokens={}
    for token in tokens:
        if token[0]=='Gen':genesis_tokens.setdefault(token[:3],[]).append(token)
    hebrew_sections=[];hebrew_ann=[]
    for book,ch,verse in sorted(verses):
        if book!='Gen':continue
        ref=f'Gen.{ch}.{verse}'
        word_rows=genesis_tokens.get((book,ch,verse),[])
        clean=[(t[4].replace('/',''),t[5],t[6],t[7]) for t in word_rows]
        hebrew_sections.append((ref,' '.join(w[0] for w in clean)))
        for pos,(surface,lemma,morph,strong) in enumerate(clean,1):
            hebrew_ann.append({'ref':ref,'position':pos,'surface':surface,'lemma':lemma,
                'morph':morph,'strong':strong})
    hebrew_translations=[]
    if args.genesis_translation:
        root=ET.fromstring(args.genesis_translation.read_bytes())
        for verse in root.iter():
            osis_id=verse.get('osisID','')
            if not re.fullmatch(r'Gen\.\d+\.\d+', osis_id):
                continue
            value=''.join(verse.itertext()).strip()
            value=' '.join(value.split())
            if value:
                hebrew_translations.append({'ref':osis_id,'translation_id':'luther1912','text':value})
    else:
        hebrew_translations=[
            {'ref':'Gen.1.1','translation_id':'luther1912','text':'Am Anfang schuf Gott Himmel und Erde.'},
            {'ref':'Gen.1.2','translation_id':'luther1912','text':'Und die Erde war wüst und leer, und es war finster auf der Tiefe; und der Geist Gottes schwebte auf dem Wasser.'},
            {'ref':'Gen.1.3','translation_id':'luther1912','text':'Und Gott sprach: Es werde Licht! Und es ward Licht.'}]
    luther={'id':'luther1912','language':'de','title':'Lutherbibel 1912','author':'Martin Luther; Revision von 1912',
        'edition':'Lutherbibel 1912','license':'Public Domain','provenance':'eBible.org, deu1912; vollständiges Genesis-Buch' if args.genesis_translation else 'eBible.org, deu1912; hier Gen 1:1–3'}
    package(args.out/'amicus-hebraeisch-genesis-oshb.amicus-source',
        {'id':'genesis-oshb-wlc','title':'Genesis · Hebräischer Text (OSHB/WLC)',
         'author':'Hebräische Bibel','language':'he','edition':'Westminster Leningrad Codex 4.20 / Open Scriptures Hebrew Bible',
         'license':'WLC-Text Public Domain; OSHB-Morphologie CC BY 4.0','provenance':'Open Scriptures Hebrew Bible; https://github.com/openscriptures/morphhb',
         'version':'OSHB-Commit 3d15126; WLC 4.20'},
        hebrew_sections,hebrew_ann,hebrew_translations,[luther],
        {'provider':'Open Scriptures Hebrew Bible (OSHB)','method':'Editionsgebundene Lemma-/Strong- und Morphologiecodes aus dem OSHB-XML.',
         'coverage':'Genesis vollständig; morphologische Codes werden im Originalformat bewahrt und nicht automatisch in UD-Features umgedeutet.',
         'quality':'edition','review_status':'Editionsgebundene OSHB-Codes; keine Modellergaenzung.',
         'license':'Morphologie CC BY 4.0; WLC-Text Public Domain','provenance':'https://github.com/openscriptures/morphhb'},
        'Genesis Kapitel.Vers (OSIS/BHS-Bezug)',
        'Genesis vollständig; '+('vollständige Lutherbibel-1912-Übersetzung enthalten.' if args.genesis_translation else 'Lutherbibel-1912-Übersetzung nur für Gen 1:1–3 im Starterpaket.'))


if __name__=='__main__':main()
