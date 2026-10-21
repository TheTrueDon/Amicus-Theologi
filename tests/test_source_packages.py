import io
import hashlib
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from backend.database import init_db
from backend.source_packages import install_package, inspect_package
from backend.sources import modules, passage, get_note, save_note, word_analysis


def package_bytes(*, bad_surface=False, version='1.0', lemma='principium', text='In principio', quality='reviewed'):
    manifest = {
        'format': 'amicus-source-package', 'format_version': 1,
        'source': {'id':'pkg-augustine-test','title':'Augustinus · Testausgabe',
            'author':'Augustinus','language':'la','edition':'Testedition 2026',
            'license':'CC BY-SA 4.0','provenance':'Lokale Testquelle','version':version},
        'files': {'sections':'sections.csv','annotations':'words.tsv','translations':'translations.csv'},
        'annotation_edition': {'provider':'Fixture','method':'Manuell geprüft','coverage':'Alle Wörter des Testabschnitts',
            'license':'CC0','provenance':'Test','quality':quality,
            'review_status':'Prüfung laut Fixture'},
        'translation_editions': [{'id':'de-test','language':'de','title':'Deutsche Arbeitsübersetzung',
            'author':'Testübersetzung','edition':'Teststand 2026','license':'CC0',
            'provenance':'Für den Test erstellt'}]
    }
    words='ref\tposition\tsurface\tlemma\tmorph\tstrong\nI.1\t1\t'+('alio' if bad_surface else 'in')+'\tin\tADP\t\nI.1\t2\tprincipio\t'+lemma+'\tNOUN|Case=Abl|Number=Sing\t\n'
    files={'manifest.json':json.dumps(manifest,ensure_ascii=False),
        'sections.csv':'ref,text\nI.1,"'+text+'"\n',
        'words.tsv':words,
        'translations.csv':'ref,translation_id,text\nI.1,de-test,"Am Anfang"\n@work,de-test,"Gesamtübersetzung"\n'}
    manifest['checksums']={name:'sha256:'+hashlib.sha256(value.encode('utf-8')).hexdigest()
                           for name,value in files.items() if name!='manifest.json'}
    files['manifest.json']=json.dumps(manifest,ensure_ascii=False)
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,value in files.items():archive.writestr(name,value)
    return out.getvalue()


class SourcePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='amicus-package-test-')
        self.previous=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name
        init_db()

    def tearDown(self):
        if self.previous is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.previous
        self.temp.cleanup()

    def test_installs_text_annotations_and_attributed_parallel_translation(self):
        result=install_package(package_bytes())
        self.assertEqual(result['sections'],1)
        self.assertEqual(result['annotated_sections'],1)
        self.assertEqual(result['translations'],2)
        self.assertEqual(result['work_translations'],1)
        content=passage('pkg-augustine-test','I.1')
        self.assertEqual(content['text'],'In principio')
        self.assertEqual(content['tokens'][1]['lemma'],'principium')
        self.assertEqual(content['tokens'][1]['morph'],'NOUN|Case=Abl|Number=Sing')
        detailed=word_analysis('pkg-augustine-test','I.1',2)
        self.assertEqual(detailed['grammar'],'Wortart: Substantiv · Kasus: Ablativ · Numerus: Singular')
        sparse=word_analysis('pkg-augustine-test','I.1',1)
        self.assertTrue(sparse['morphology_detail_missing'])
        self.assertIn('keine weiteren Flexionsmerkmale',sparse['grammar'])
        self.assertEqual(content['translations'][0]['text'],'Am Anfang')
        self.assertEqual(content['translations'][0]['license'],'CC0')
        self.assertEqual(content['work_translations'][0]['text'],'Gesamtübersetzung')

    def test_bad_token_alignment_fails_before_any_data_is_installed(self):
        with self.assertRaisesRegex(ValueError,'passen nicht'):
            install_package(package_bytes(bad_surface=True))
        self.assertNotIn('pkg-augustine-test',[m['id'] for m in modules()])

    def test_reinstall_updates_analysis_and_keeps_notes(self):
        install_package(package_bytes())
        save_note('pkg-augustine-test','I.1','Meine Notiz')
        result=install_package(package_bytes(version='2.0',lemma='principium-novum'))
        self.assertTrue(result['updated'])
        content=passage('pkg-augustine-test','I.1')
        self.assertEqual(content['tokens'][1]['lemma'],'principium-novum')
        self.assertEqual(get_note('pkg-augustine-test','I.1')['content'],'Meine Notiz')

    def test_word_analysis_exposes_package_review_status(self):
        install_package(package_bytes(quality='automatic'))
        analysis=word_analysis('pkg-augustine-test','I.1',1)
        self.assertEqual(analysis['annotation_quality'],'automatic')
        self.assertEqual(analysis['annotation_status'],'Prüfung laut Fixture')

    def test_update_refuses_changed_text_without_touching_installed_data(self):
        install_package(package_bytes())
        with self.assertRaisesRegex(ValueError,'abweichende Stellen oder Text'):
            install_package(package_bytes(version='2.0',text='IN principio'))
        self.assertEqual(passage('pkg-augustine-test','I.1')['text'],'In principio')

    def test_rejects_path_traversal(self):
        data=package_bytes()
        with zipfile.ZipFile(io.BytesIO(data)) as original:
            entries=[(i.filename,original.read(i.filename)) for i in original.infolist()]
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as archive:
            for name,value in entries:archive.writestr('../'+name if name=='words.tsv' else name,value)
        with self.assertRaisesRegex(ValueError,'Unsicher'):
            inspect_package(out.getvalue())

    def test_all_bundled_packages_validate_and_install_offline(self):
        root=Path(__file__).resolve().parents[1]/'source_packages'
        expected={'amicus-latin-augustinus-confessiones.amicus-source':(4051,'la'),
                  'amicus-latein-augustinus-de-civitate-dei.amicus-source':(12125,'la'),
                  'amicus-latein-augustinus-de-trinitate.amicus-source':(4366,'la'),
                  'amicus-griechisch-origenes-de-oratione.amicus-source':(157,'grc'),
                  'amicus-griechisch-athanasius-de-incarnatione.amicus-source':(57,'grc'),
                  'amicus-griechisch-chrysostomus-colossenses.amicus-source':(91,'grc'),
                  'amicus-griechisch-philo-de-opificio-mundi.amicus-source':(172,'grc'),
                  'amicus-griechisch-josephus-bellum-judaicum.amicus-source':(4001,'grc'),
                  'amicus-griechisch-severian.amicus-source':(13,'grc'),
                  'amicus-hebraeisch-genesis-oshb.amicus-source':(1533,'he')}
        for filename,(count,language) in expected.items():
            with self.subTest(filename=filename):
                manifest,sections,annotations,editions,translations,work_translations=inspect_package((root/filename).read_bytes())
                self.assertEqual(len(sections),count)
                self.assertEqual(manifest['source']['language'],language)
                self.assertTrue(all(lemma.strip() and morph.strip()
                                    for rows in annotations.values()
                                    for lemma,morph,_strong in rows),
                                'Jedes Wort braucht mindestens Lemma und Morphologie-/Wortartcode.')
                expected_quality={'la':'mixed','grc':'automatic','he':'edition'}[language]
                self.assertEqual(manifest['annotation_edition']['quality'],expected_quality)
                self.assertEqual(manifest['annotation_edition']['codes_recognized_by_decoder']['tokens'],
                                 manifest['annotation_edition']['codes_recognized_by_decoder']['tokens_total'])
                self.assertIn('feature_detail_coverage',manifest['annotation_edition'])
                if filename not in ('amicus-griechisch-philo-de-opificio-mundi.amicus-source',
                                    'amicus-griechisch-josephus-bellum-judaicum.amicus-source'):
                    self.assertTrue(annotations)
                self.assertTrue(editions)
                self.assertTrue(translations or work_translations)
                result=install_package((root/filename).read_bytes())
                self.assertEqual(result['sections'],count)
                first=sections[0][0]
                content=passage(result['module_id'],first)
                self.assertEqual(content['text'],sections[0][2])
                if filename in ('amicus-latin-augustinus-confessiones.amicus-source',
                                'amicus-latein-augustinus-de-civitate-dei.amicus-source',
                                'amicus-latein-augustinus-de-trinitate.amicus-source',
                                'amicus-griechisch-origenes-de-oratione.amicus-source',
                                'amicus-griechisch-athanasius-de-incarnatione.amicus-source',
                                'amicus-griechisch-chrysostomus-colossenses.amicus-source'):
                    self.assertTrue(content['work_translations'])
                if filename == 'amicus-griechisch-philo-de-opificio-mundi.amicus-source':
                    self.assertEqual(len(content['work_translations']), 2)
                if filename == 'amicus-griechisch-josephus-bellum-judaicum.amicus-source':
                    self.assertEqual(len(content['work_translations']), 1)
                if filename == 'amicus-hebraeisch-genesis-oshb.amicus-source':
                    self.assertEqual(len(translations), count)


if __name__=='__main__':unittest.main()
