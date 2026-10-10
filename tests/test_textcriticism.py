import os,tempfile,unittest
from fastapi.testclient import TestClient
from backend.database import init_db,connect,factory_reset
from backend.main import app
from backend.library import install_module

class TextCriticalTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=os.environ.get('AMICUS_THEOLOGI_DATA_DIR');os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.tmp.name;init_db()
  for mid in ('text_a','text_b'):
   install_module(mid,mid,'grc','Testlizenz','Testquelle','1',[('Joh',1,1,'ἐν ἀρχῇ' if mid=='text_a' else 'ἐν ἀρχῇ λόγος'),('Mt',3,13,'Text '+mid),('Mk',1,9,'Text '+mid)])
 def tearDown(self):
  if self.old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
  else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.old
  self.tmp.cleanup()
 def test_compare(self):
  with TestClient(app) as c:
   r=c.get('/api/textcrit/compare?book=Joh&chapter=1&modules=text_a,text_b');self.assertEqual(r.status_code,200,r.text);self.assertEqual(len(r.json()['rows']),1)
   self.assertNotEqual(r.json()['rows'][0]['texts'][0],r.json()['rows'][0]['texts'][1]);self.assertIn('nicht automatisch',r.json()['notice'])
   self.assertEqual(c.get('/api/textcrit/compare?book=Joh&chapter=1&modules=text_a,text_a').status_code,422)
 def test_synoptic(self):
  with TestClient(app) as c:
   self.assertGreater(len(c.get('/api/textcrit/synopsis').json()),3)
   r=c.get('/api/textcrit/synopsis/0?module_id=text_a');self.assertEqual(r.status_code,200,r.text);self.assertEqual(len(r.json()['columns']),3)
   self.assertEqual(r.json()['columns'][0]['verses'][0]['verse'],13)
 def test_variant_import_and_reset(self):
  data=('book\tchapter\tverse\treading\twitness\tsource\tlicense\tnotes\n'
        'Joh\t1\t1\tἐν ἀρχῇ\tZeuge A\tEdition X\tCC BY 4.0\tDemonstration\n').encode()
  with TestClient(app) as c:
   r=c.post('/api/textcrit/variants/import',data={'collection':'Testkorpus'},files={'file':('demo.tsv',data,'text/tab-separated-values')});self.assertEqual(r.status_code,200,r.text)
   self.assertEqual(len(c.get('/api/textcrit/variants?book=Joh&chapter=1&verse=1').json()),1)
   self.assertEqual(len(c.get('/api/textcrit/collections').json()),1)
   factory_reset();self.assertEqual(c.get('/api/textcrit/collections').json(),[])
 def test_reject_unattributed(self):
  raw=b'book\tchapter\tverse\treading\twitness\tsource\tlicense\nJoh\t1\t1\tTest\t\tNone\tCC0\n'
  with TestClient(app) as c:
   self.assertEqual(c.post('/api/textcrit/variants/import',data={'collection':'Oops'},files={'file':('bad.tsv',raw)}).status_code,422)
   self.assertEqual(c.get('/api/textcrit/collections').json(),[])
if __name__=='__main__':unittest.main()
