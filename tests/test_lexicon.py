import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.database import init_db, connect
from backend.lexicon import read_lexicon, install_lexicon, lookup, remove_lexicon
from backend.main import app

class LexiconTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.old=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name
        init_db()
    def tearDown(self):
        if self.old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.old
        self.temp.cleanup()
    def demo(self):
        text='lemma\tstrong\tgloss\tdefinition\nλόγος\tG3056\tWort\tGriechisches Demo-Wort\n'
        return read_lexicon(text.encode())
    def test_import_lookup_and_delete(self):
        install_lexicon('lex-test','Testlexikon','grc','CC0','Eigenbeispiel','1',self.demo())
        self.assertEqual(lookup('grc',lemma='λόγος')[0]['gloss'],'Wort')
        self.assertEqual(len(lookup('grc',strong='G3056')),1)
        self.assertEqual(lookup('he',lemma='λόγος'),[])
        self.assertTrue(remove_lexicon('lex-test'))
        self.assertEqual(lookup('grc',lemma='λόγος'),[])
    def test_duplicate_rejected_no_data_loss(self):
        install_lexicon('lex-test','Testlexikon','grc','CC0','Eigenbeispiel','1',self.demo())
        with self.assertRaises(ValueError):install_lexicon('lex-test','Overwrite','grc','CC0','E','1',self.demo())
        self.assertEqual(len(lookup('grc',lemma='λόγος')),1)
    def test_invalid_file_and_atomicity(self):
        with self.assertRaises(ValueError):read_lexicon(b'lemma\tdefinition\nfoo\tbar\nfoo\tbar\n')
        with connect() as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM lexicon_modules').fetchone()[0],0)
    def test_api(self):
        with TestClient(app) as client:
            response=client.post('/api/lexica/import',files={'file':('lex.tsv',b'lemma\tdefinition\nlogos\tword\n','text/tab-separated-values')},data={'module_id':'lex-api','title':'API Lex','language':'grc','license_name':'CC0','provenance':'Test'})
            self.assertEqual(response.status_code,200,response.text)
            self.assertEqual(client.get('/api/lexicon/lookup',params={'language':'grc','lemma':'logos'}).json()['results'][0]['definition'],'word')
            self.assertEqual(client.delete('/api/lexica/lex-api').status_code,200)
    def test_old_data_survives_migration(self):
        with connect() as db:
            db.execute("INSERT INTO modules(id,title,language,kind,license,provenance,version) VALUES ('old','Old','de','bible','PD','Test','1')")
            db.execute("INSERT INTO verses(module_id,book,chapter,verse,text) VALUES ('old','Joh',1,1,'Im Anfang')")
        init_db()
        with connect() as db:
            self.assertEqual(db.execute('SELECT text FROM verses WHERE module_id=?',('old',)).fetchone()[0],'Im Anfang')

if __name__=='__main__':unittest.main()
