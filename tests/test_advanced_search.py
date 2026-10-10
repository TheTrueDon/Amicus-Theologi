import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.database import init_db
from backend.library import install_module, read_import
from backend.morphology import import_annotations, parse_annotation_file
from backend.advanced_search import advanced_search
from backend.main import app
ROOT=Path(__file__).resolve().parents[1]/'modules/examples'
class AdvancedTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=os.environ.get('AMICUS_THEOLOGI_DATA_DIR');os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.tmp.name
  init_db()
  for stem,lang in [('johannes_1_1_grc','grc'),('genesis_1_1_he','he')]:
   install_module('demo-'+lang,'Test '+lang,lang,'demo','tests','1',read_import((ROOT/(stem+'.tsv')).read_bytes()))
   import_annotations('demo-'+lang,parse_annotation_file((ROOT/(stem+'_morph.tsv')).read_bytes()))
 def tearDown(self):
  if self.old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
  else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.old
  self.tmp.cleanup()
 def test_lemma(self):
  self.assertEqual(advanced_search(lemma='λόγος',module_id='demo-grc')['total'],1)
  self.assertEqual(advanced_search(lemma='λόγος',module_id='demo-he')['total'],0)
 def test_morph_and_book(self):
  self.assertEqual(advanced_search(morph='Imperfekt',book='Joh')['total'],1)
  self.assertEqual(advanced_search(morph='Imperfekt',book='Gen')['total'],0)
 def test_proximity_and_order(self):
  self.assertEqual(advanced_search(lemma='λόγος',second_lemma='εἰμί',distance=5)['total'],1)
  self.assertEqual(advanced_search(lemma='ἀρχή',second_lemma='λόγος',distance=0)['total'],0)
  self.assertEqual(advanced_search(lemma='λόγος',second_lemma='εἰμί',distance=5,order='after')['total'],1)
  self.assertEqual(advanced_search(lemma='λόγος',second_lemma='εἰμί',distance=5,order='before')['total'],1)
 def test_validation_and_injection(self):
  with self.assertRaises(ValueError):advanced_search(lemma='')
  self.assertEqual(advanced_search(lemma="' OR 1=1 --")['total'],0)
  with self.assertRaises(ValueError):advanced_search(lemma='λόγος',distance=101)
 def test_api(self):
  with TestClient(app) as client:
   r=client.get('/api/search/advanced',params={'lemma':'λόγος','second_lemma':'εἰμί','distance':5})
   self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['total'],1)
   self.assertEqual(client.get('/api/search/advanced',params={'lemma':''}).status_code,422)
if __name__=='__main__':unittest.main()
