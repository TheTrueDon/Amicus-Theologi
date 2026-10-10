"""v1.0.3: genuine STEP glosses and stable sortable lemma concordance."""
import io
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, connect
from backend.lexical_text import best_gloss
from backend.catalog import parse_step_lexicon
from backend.library import read_import, install_module
from backend.morphology import import_annotations, parse_annotation_file
from backend.lexicon import install_lexicon, read_lexicon

ROOT = Path(__file__).resolve().parents[1]


class V103Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ['AMICUS_THEOLOGI_DATA_DIR'] = self.temp.name
        init_db()
        base = ROOT/'modules/examples'
        install_module('greek-example','Griechisch','grc','Test','Demo','1',
                       read_import((base/'johannes_1_1_grc.tsv').read_bytes()))
        import_annotations('greek-example',parse_annotation_file(
            (base/'johannes_1_1_grc_morph.tsv').read_bytes()))

    def tearDown(self):
        os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        self.temp.cleanup()

    def test_old_step_transliteration_is_not_translation(self):
        # The previous importer stored tail[0]='logos' as the gloss.
        data=('lemma\tstrong\tgloss\tdefinition\n'
              'λόγος\tG3056\tlogos\tlogos · G:N-M · <b>word, speech</b> · utterance\n'
              'εἰμί\tG1510\teimi\teimi · G:V · to be, exist · being\n')
        install_lexicon('step-tbesg','STEPBible TBESG','grc','CC BY 4.0',
                        'STEPBible TBESG','1',read_lexicon(data.encode('utf-8')))
        with TestClient(app) as client:
            tokens=client.get('/api/chapter',params={'book':'Joh','chapter':1}).json()['tokens']
            logos=next(t for t in tokens if t['lemma']=='λόγος')
            res=client.get('/api/morphology/preview',params={'module_id':'greek-example','book':'Joh','chapter':1,'verse':1,'position':logos['position']})
            self.assertEqual(res.status_code,200,res.text)
            self.assertEqual(res.json()['gloss'],'word, speech')
            lex=client.get('/api/lexicon/lookup',params={'language':'grc','lemma':'λόγος'}).json()['results'][0]
            self.assertEqual(lex['display_gloss'],'word, speech')
            self.assertEqual(lex['gloss'],'logos')  # Original remains intact

    def test_old_step_hebrew_and_empty_translation(self):
        self.assertEqual(best_gloss({'module_id':'step-tbesh','gloss':'bara',
                                     'definition':'bara · H:V-Q · create, make · ...'}), 'create, make')
        self.assertEqual(best_gloss({'module_id':'step-tbesh','gloss':'bara',
                                     'definition':'bara · H:V-Q'}), '')
        self.assertEqual(best_gloss({'module_id':'custom','gloss':'Wort',
                                     'definition':'eine Rede'}),'Wort')
        self.assertEqual(best_gloss({'module_id':'step-tbesg','gloss':'λόγος',
                                     'definition':'λόγος · G:N · speech'}),'speech')

    def test_step_lexicon_header_extracts_real_gloss(self):
        text=('EStrong#\tGreek\tTransliteration\tGloss\tMorph\tMeaning\n'
              'G3056\tλόγος\tlogos\tword, speech\tG:N\tword, speech, statement\n')
        stream=io.BytesIO()
        with zipfile.ZipFile(stream,'w') as z:
            z.writestr('STEPBible-Data-master/Lexicons/TBESG - test.txt',text)
        entries=parse_step_lexicon(stream.getvalue(),'TBESG')
        self.assertEqual(len(entries),1)
        self.assertEqual(entries[0][3],'word, speech')

    def test_lemma_sorting_and_pagination_applied_in_sql(self):
        with connect() as db:
            db.execute("UPDATE tokens SET surface='λόγου' WHERE module_id='greek-example' AND lemma='λόγος' AND position=4")
            db.execute("UPDATE tokens SET surface='λόγῳ' WHERE module_id='greek-example' AND lemma='λόγος' AND position=7")
        with TestClient(app) as client:
            q={'module_id':'greek-example','lemma':'λόγος','sort_by':'surface','direction':'asc','limit':2}
            a=client.get('/api/morphology/lemma',params=q)
            self.assertEqual(a.status_code,200,a.text)
            r=a.json()
            self.assertEqual(r['total'],3)
            b=client.get('/api/morphology/lemma',params={**q,'offset':2}).json()
            combined=[x['surface'] for x in r['results']+b['results']]
            self.assertEqual(combined,sorted(combined))
            rev=client.get('/api/morphology/lemma',params={**q,'direction':'desc','limit':50}).json()
            self.assertEqual([x['surface'] for x in rev['results']],list(reversed(combined)))
            reference=client.get('/api/morphology/lemma',params={**q,'sort_by':'reference','limit':50}).json()
            self.assertEqual([x['position'] for x in reference['results']],sorted(x['position'] for x in reference['results']))
            self.assertEqual(client.get('/api/morphology/lemma',params={**q,'sort_by':'unknown'}).status_code,422)

    def test_frontend_controls_exist(self):
        with TestClient(app) as client:
            page=client.get('/').text
            code=client.get('/assets/wordtools.js').text
            self.assertIn('id="lemma-dialog-sort"',page)
            self.assertIn('id="lemma-dialog-direction"',page)
            self.assertIn('sort_by:sortBy',code)


if __name__=='__main__':
    unittest.main()
