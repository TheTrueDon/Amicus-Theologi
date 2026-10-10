"""Regression tests: hover preview, paginated lemma concordance, rich lexicon source."""
import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, connect, APP_VERSION
from backend.library import read_import, install_module
from backend.morphology import import_annotations, parse_annotation_file
from backend.lexicon import install_lexicon, read_lexicon
from backend.lexical_text import concise_gloss

ROOT=Path(__file__).resolve().parents[1]
class WordExperienceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.tmp.name
        init_db()
        base=ROOT/'modules/examples'
        install_module('example-grc','Griechisch Demo','grc','Public Domain','Test','1',read_import((base/'johannes_1_1_grc.tsv').read_bytes()))
        import_annotations('example-grc',parse_annotation_file((base/'johannes_1_1_grc_morph.tsv').read_bytes()))

    def tearDown(self):
        os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        self.tmp.cleanup()

    def test_lemma_has_total_and_pagination(self):
        with TestClient(app) as client:
            first=client.get('/api/morphology/lemma',params={'module_id':'example-grc','lemma':'λόγος','limit':2,'offset':0})
            self.assertEqual(first.status_code,200,first.text)
            self.assertEqual(first.json()['total'],3)
            self.assertEqual(len(first.json()['results']),2)
            rest=client.get('/api/morphology/lemma',params={'module_id':'example-grc','lemma':'λόγος','limit':2,'offset':2}).json()
            self.assertEqual(rest['total'],3)
            self.assertEqual(len(rest['results']),1)
            self.assertEqual(rest['offset'],2)

    def test_lemma_pagination_validated(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/api/morphology/lemma',params={'module_id':'example-grc','lemma':'λόγος','offset':-1}).status_code,422)
            self.assertEqual(client.get('/api/morphology/lemma',params={'module_id':'example-grc','lemma':'λόγος','limit':200}).status_code,422)

    def test_hover_gloss_and_grammar_are_source_based(self):
        lex=('lemma\tstrong\tgloss\tdefinition\n'
             'εἰμί\tG1510\t<b>sein</b> &amp; existieren\tEin <em>Verb</em>')
        install_lexicon('grc-check','Demolexikon','grc','Testlizenz','Testquelle','1',read_lexicon(lex.encode()))
        with TestClient(app) as client:
            res=client.get('/api/morphology/preview',params={'module_id':'example-grc','book':'Joh','chapter':1,'verse':1,'position':3})
            self.assertEqual(res.status_code,200,res.text)
            data=res.json()
            # Find the first token with εἰμί independently of its position.
            word=next((x for x in client.get('/api/chapter',params={'book':'Joh','chapter':1}).json()['tokens'] if x['lemma']=='εἰμί'),None)
            self.assertIsNotNone(word)
            res=client.get('/api/morphology/preview',params={'module_id':'example-grc','book':'Joh','chapter':1,'verse':1,'position':word['position']})
            self.assertEqual(res.status_code,200,res.text)
            data=res.json()
            self.assertEqual(data['lemma'],'εἰμί')
            self.assertIn('sein',data['gloss'])
            self.assertIn('existieren',data['gloss'])
            self.assertNotIn('<b>',data['gloss'])
            self.assertIn('Imperfekt', data['morph'])
            # Full categorical decoding applies to a recognized grammar-code scheme.
            from backend.morph_display import decode
            self.assertTrue(decode('V-IAI-3S','grc')['recognized'])

    def test_no_gloss_not_invented(self):
        with TestClient(app) as client:
            word=next(x for x in client.get('/api/chapter',params={'book':'Joh','chapter':1}).json()['tokens'] if x['lemma']=='λόγος')
            data=client.get('/api/morphology/preview',params={'module_id':'example-grc','book':'Joh','chapter':1,'verse':1,'position':word['position']}).json()
            self.assertEqual(data['gloss'],'')

    def test_markup_not_executed_and_source_kept(self):
        self.assertEqual(concise_gloss('<b>redlich</b><script>alert(1)</script> &amp; <i>sicher</i>'),'redlich & sicher')
        lex='lemma\tdefinition\nλόγος\t<b>Wort</b> und <em>Rede</em>\n'
        install_lexicon('grc-html','Quelle','grc','Test','Test','1',read_lexicon(lex.encode()))
        with connect() as db:
            self.assertIn('<em>',db.execute('SELECT definition FROM lexicon_entries').fetchone()['definition'])
        with TestClient(app) as client:
            self.assertEqual(client.get('/assets/wordtools.js').status_code,200)
            self.assertIn('id="lemma-dialog"',client.get('/').text)
            self.assertNotIn('innerHTML',client.get('/assets/wordtools.js').text)

if __name__=='__main__':unittest.main()
