import os
import tempfile
import unittest
from fastapi.testclient import TestClient
from backend.database import init_db, get_settings, set_settings
from backend.library import parse_reference, read_import, install_module, chapter_view, neighbor
from backend.main import app
class LibraryTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name;init_db()
 def tearDown(self):
  self.temp.cleanup();os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
 def test_reference(self):
  self.assertEqual(parse_reference('Joh 1,3'),('Joh',1,3));self.assertEqual(parse_reference('1 Mose 1'),('Gen',1,1))
  with self.assertRaises(ValueError):parse_reference('unbekannt 4,3')
 def test_import_parallel(self):
  rows=read_import(b'book\tchapter\tverse\ttext\nJoh\t1\t1\tAlpha\nJoh\t1\t2\tBeta\n')
  install_module('a','Test A','de','demo','test','1',rows)
  install_module('b','Test B','la','demo','test','1',[('Joh',1,1,'Gamma')])
  items=chapter_view('Joh',1)
  self.assertEqual(len(items),2);self.assertEqual(len(items[0]['verses']),2)
  self.assertEqual(neighbor('Joh',1,-1),None)
  with self.assertRaises(ValueError):read_import(b'book,chapter,verse,text\nJoh,1,1,a\nJoh,1,1,b\n')
 def test_api(self):
  with TestClient(app) as c:
   self.assertEqual(c.get('/api/status').json()['version'],'0.9.0')
   r=c.post('/api/modules/import',files={'file':('sample.tsv',b'book\tchapter\tverse\ttext\nJoh\t1\t1\tTest\n','text/tab-separated-values')},data={'module_id':'t1','title':'Test','language':'de','license_name':'Demo','provenance':'Test','version':'1'})
   self.assertEqual(r.status_code,200,r.text)
   self.assertEqual(c.get('/api/chapter',params={'book':'Joh','chapter':1}).json()['modules'][0]['verses'][0]['text'],'Test')
   self.assertEqual(c.delete('/api/modules/t1').status_code,200)
   self.assertEqual(c.get('/api/modules').json(),[])
 def test_existing_settings(self):
  set_settings({'theme':'light'});init_db();self.assertEqual(get_settings()['theme'],'light')
if __name__=='__main__':unittest.main()
