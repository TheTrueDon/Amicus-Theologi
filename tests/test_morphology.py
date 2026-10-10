import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.database import init_db, connect
from backend.library import read_import, install_module
from backend.morphology import parse_annotation_file, import_annotations, lemma_concordance
from backend.main import app
ROOT=Path(__file__).resolve().parents[1]
class MorphologyTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.tmp.name;init_db()
 def tearDown(self):
  os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None);self.tmp.cleanup()
 def example(self,lang):
  if lang=='grc':stem='johannes_1_1_grc'
  else:stem='genesis_1_1_he'
  folder=ROOT/'modules/examples'
  install_module('m-'+lang,'Demo',lang,'ancient text','manual demonstration','1',read_import((folder/(stem+'.tsv')).read_bytes()))
  return (folder/(stem+'_morph.tsv')).read_bytes()
 def test_greek_example(self):
  raw=self.example('grc');parsed=parse_annotation_file(raw)
  result=import_annotations('m-grc',parsed)
  self.assertEqual(result,{'annotated_verses':1,'tokens':17})
  self.assertEqual(len(lemma_concordance('m-grc','λόγος')),3)
 def test_hebrew_example(self):
  raw=self.example('he');self.assertEqual(import_annotations('m-he',parse_annotation_file(raw))['tokens'],7)
 def test_rollback_wrong_text(self):
  raw=self.example('grc');import_annotations('m-grc',parse_annotation_file(raw))
  corrupt=raw.replace('λόγος'.encode(),'λανθ'.encode(),1)
  with self.assertRaises(ValueError):import_annotations('m-grc',parse_annotation_file(corrupt))
  self.assertEqual(len(lemma_concordance('m-grc','λόγος')),3)
 def test_api(self):
  raw=self.example('grc')
  with TestClient(app) as c:
   res=c.post('/api/morphology/import',data={'module_id':'m-grc'},files={'file':('m.tsv',raw,'text/tab-separated-values')})
   self.assertEqual(res.status_code,200,res.text)
   chap=c.get('/api/chapter',params={'book':'Joh','chapter':1}).json()
   self.assertEqual(len(chap['tokens']),17)
   self.assertEqual(c.get('/api/morphology/word',params={'module_id':'m-grc','book':'Joh','chapter':1,'verse':1,'position':5}).json()['lemma'],'λόγος')
   self.assertEqual(len(c.get('/api/morphology/lemma',params={'module_id':'m-grc','lemma':'λόγος'}).json()['results']),3)
   self.assertEqual(c.delete('/api/modules/m-grc').status_code,200)
   self.assertEqual(c.get('/api/morphology/lemma',params={'module_id':'m-grc','lemma':'λόγος'}).json()['results'],[])
if __name__=='__main__':unittest.main()
