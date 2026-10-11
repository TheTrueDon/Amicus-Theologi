"""Regression tests for Hebrew OSHB / STEPBible word previews (1.0.7)."""
import os
import tempfile
import unittest
from fastapi.testclient import TestClient
from backend.database import init_db
from backend.main import app
from backend.lexicon import install_lexicon, read_lexicon
from backend.library import install_module
from backend.morphology import import_annotations
from backend.morph_display import decode
from backend.lexical_text import best_gloss
from backend.hebrew_display import explain_word, strong_for_lemma


class HebrewPreviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.tmp.name
        init_db()
        install_module('hebrew-realistic','OSHB-Test','he','CC BY 4.0','Open Scriptures','1',
                       [('Gen',1,1,'בְּ רֵאשִׁית בָּרָא אֱלֹהִים')])
        # use the API's existing token schema to simulate an already-installed
        # unmodified OSHB import: numeric lemmas and raw grammar codes.
        from backend.database import connect
        with connect() as db:
            db.executemany('''INSERT INTO tokens(module_id,book,chapter,verse,position,surface,lemma,morph,strong)
                             VALUES(?,?,?,?,?,?,?,?,?)''',[
                ('hebrew-realistic','Gen',1,1,1,'בְּרֵאשִׁית','b/7225','HR/Ncfsa','H7225'),
                ('hebrew-realistic','Gen',1,1,2,'בָּרָא','1254 a','HVqp3ms','H1254'),
                ('hebrew-realistic','Gen',1,1,3,'אֱלֹהִים','430','HNcmpa','H430')])
        lex=('lemma\tstrong\tgloss\tdefinition\n'
             'רֵאשִׁית\tH7225\treshith\treshith · H:N-F · beginning, first\n'
             'ברא\tH1254\tbara\tbara · H:V-Q · create, make\n'
             'אֱלֹהִים\tH430\telohim\telohim · H:N-M · God, gods\n')
        install_lexicon('step-tbesh','STEPBible TBESH','he','CC BY 4.0',
                        'STEPBible TBESH','1',read_lexicon(lex.encode()))
    def tearDown(self):
        os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        self.tmp.cleanup()
    def test_real_os_hb_morphology(self):
        tests=[('HR/Ncfsa','Präposition + Substantiv'),
               ('HC/R/Ncfsa','Konjunktion + Präposition + Substantiv'),
               ('HVqp3ms','Verb'),('HNcmpa','Substantiv'),('HTo','Partikel'),
               ('HC','Konjunktion'),('HSp3ms','Suffix')]
        for code,expected in tests:
            with self.subTest(code=code):
                d=decode(code,'he')
                self.assertTrue(d['recognized'],code)
                self.assertEqual(d['features'][0]['value'],expected)
        invalid=decode('HXYZ??','he')
        self.assertFalse(invalid['recognized'])
    def test_numeric_hebrew_lemma_is_not_headword(self):
        self.assertEqual(strong_for_lemma({'lemma':'b/7225','strong':''}),'H7225')
        self.assertEqual(strong_for_lemma({'lemma':'c/m/6529','strong':''}),'H6529')
        self.assertEqual(strong_for_lemma({'lemma':'1254 a','strong':''}),'H1254')
        self.assertFalse(explain_word({'lemma':'c/m/6529','strong':''},entries=[])['display_lemma'])
        with TestClient(app) as client:
            for pos,display,gloss in [(1,'רֵאשִׁית','beginning, first'),
                                       (2,'ברא','create, make'),(3,'אֱלֹהִים','God, gods')]:
                r=client.get('/api/morphology/preview',params={
                    'module_id':'hebrew-realistic','book':'Gen','chapter':1,'verse':1,'position':pos})
                self.assertEqual(r.status_code,200,r.text)
                d=r.json()
                self.assertEqual(d['display_lemma'],display)
                self.assertEqual(d['gloss'],gloss)
                self.assertTrue(d['grammar']['recognized'])
                self.assertFalse(d['display_lemma'][0].isdigit())
            # Same query used by the right-hand lexicon panel.
            resp=client.get('/api/lexicon/lookup',params={'language':'he','lemma':'b/7225','strong':'H7225'})
            self.assertEqual(resp.status_code,200,resp.text)
            self.assertEqual(resp.json()['results'][0]['lemma'],'רֵאשִׁית')
    def test_bare_word_class_is_not_translation(self):
        self.assertEqual(best_gloss({'module_id':'step-tbesh','gloss':'reshith',
                                      'definition':'reshith · H:N-F · beginning, first'}),'beginning, first')
        self.assertEqual(best_gloss({'module_id':'step-tbesh','gloss':'prefix',
                                      'definition':'prefix · H:R · in, by, with'}),'in, by, with')
        self.assertEqual(best_gloss({'module_id':'step-tbesh','gloss':'prefix',
                                      'definition':'prefix · H:R'}),'')
    def test_frontend_uses_resolved_word_display(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        self.assertIn('data.display_lemma',(root/'frontend/wordtools.js').read_text(encoding='utf-8'))
        self.assertIn('info.display_lemma',(root/'frontend/app.js').read_text(encoding='utf-8'))

if __name__=='__main__':unittest.main()
