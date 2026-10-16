import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.database import init_db, connect
from backend.library import read_import, install_module
from backend.morphology import parse_annotation_file, import_annotations, lemma_concordance, lemma_forms_page
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
 def test_forms_page_groups_observed_forms_and_counts_books(self):
  raw=self.example('grc');import_annotations('m-grc',parse_annotation_file(raw))
  result=lemma_forms_page('m-grc','ὁ')
  self.assertEqual(result['total_forms'],2)
  self.assertEqual(result['total_occurrences'],4)
  by_surface={form['surface']:form for form in result['forms']}
  self.assertEqual(by_surface['ὁ']['occurrences'],3)
  self.assertEqual(by_surface['ὁ']['books'],[{'book':'Joh','occurrences':3}])
  self.assertEqual(by_surface['τὸν']['occurrences'],1)
  self.assertFalse(by_surface['ὁ']['analyses'][0]['grammar']['recognized'])
  self.assertEqual(by_surface['ὁ']['analyses'][0]['grammar']['raw'],by_surface['ὁ']['analyses'][0]['morph'])
 def test_forms_api_and_validation(self):
  raw=self.example('grc');import_annotations('m-grc',parse_annotation_file(raw))
  with TestClient(app) as c:
   response=c.get('/api/morphology/forms',params={'module_id':'m-grc','lemma':'λόγος'})
   self.assertEqual(response.status_code,200,response.text)
   self.assertEqual(response.json()['total_occurrences'],3)
   self.assertEqual(c.get('/api/morphology/forms',params={'module_id':'missing','lemma':'λόγος'}).status_code,422)
   self.assertEqual(c.get('/api/morphology/forms',params={'module_id':'m-grc','lemma':'λόγος','limit':0}).status_code,422)
   diagnostic=c.get('/api/diagnostics').json()
   module=next(item for item in diagnostic['modules'] if item['id']=='m-grc')
   self.assertEqual(module['annotated_verses'],1)
   self.assertEqual(module['annotation_coverage_percent'],100.0)
   self.assertIn('weder Vollständigkeit',diagnostic['coverage_note'])
 def test_hebrew_example(self):
  raw=self.example('he');self.assertEqual(import_annotations('m-he',parse_annotation_file(raw))['tokens'],7)
 def test_hebrew_chapter_api_exposes_clickable_tokens(self):
  raw=self.example('he');import_annotations('m-he',parse_annotation_file(raw))
  with TestClient(app) as c:
   chapter=c.get('/api/chapter',params={'book':'Gen','chapter':1})
   self.assertEqual(chapter.status_code,200)
   obj=chapter.json()
   hebrew=[t for t in obj['tokens'] if t['module_id']=='m-he' and t['verse']==1]
   self.assertEqual(len(hebrew),7)
   self.assertEqual(hebrew[1]['surface'],'בָּרָא')
   self.assertEqual(hebrew[1]['lemma'],'ברא')
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
