import os,tempfile,unittest
from fastapi.testclient import TestClient
from backend.database import init_db,connect,factory_reset
from backend.main import app
from backend.morph_display import decode

class StudiesTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=os.environ.get('AMICUS_THEOLOGI_DATA_DIR');os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.tmp.name;init_db()
 def tearDown(self):
  if self.old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
  else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.old
  self.tmp.cleanup()
 def test_project_notes_highlights_export(self):
  with TestClient(app) as c:
   p=c.post('/api/projects',json={'title':'Exegese Joh 1','description':'Studie'});self.assertEqual(p.status_code,201,p.text);pid=p.json()['id']
   self.assertEqual(len(c.get('/api/projects').json()),1)
   self.assertEqual(c.post(f'/api/projects/{pid}/notes',json={'book':'Joh','chapter':1,'verse':1,'content':'Erste Notiz'}).status_code,201)
   note=c.get(f'/api/projects/{pid}/annotations?book=Joh&chapter=1').json()['notes'][0]
   self.assertEqual(c.patch(f'/api/projects/{pid}/notes/{note["id"]}',json={'content':'Neu'}).status_code,200)
   self.assertEqual(c.put(f'/api/projects/{pid}/highlight',json={'book':'Joh','chapter':1,'verse':1,'color':'green'}).status_code,200)
   exp=c.get(f'/api/projects/{pid}/export').json();self.assertEqual(exp['schema_version'],1)
   self.assertEqual(exp['highlights'][0]['color'],'green')
   self.assertEqual(exp['notes'][0]['content'],'Neu')
   self.assertEqual(c.delete(f'/api/projects/{pid}/notes/{note["id"]}').status_code,200)
   self.assertEqual(c.delete(f'/api/projects/{pid}').status_code,200)
 def test_validation_and_reset(self):
  with TestClient(app) as c:
   pid=c.post('/api/projects',json={'title':'Probe'}).json()['id']
   self.assertEqual(c.post(f'/api/projects/{pid}/notes',json={'book':'FAKE','chapter':1,'verse':1,'content':'test'}).status_code,422)
   factory_reset()
   self.assertEqual(c.get('/api/projects').json(),[])
 def test_morphology_translations(self):
  a=decode('V-IAI-3S','grc');self.assertTrue(a['recognized']);self.assertIn({'name':'Tempus','value':'Imperfekt'},a['features'])
  n=decode('N-NSM','grc');self.assertTrue(n['recognized']);self.assertIn({'name':'Kasus','value':'Nominativ'},n['features'])
  h=decode('HVqp3ms','he');self.assertTrue(h['recognized']);self.assertIn({'name':'Stamm','value':'Qal'},h['features'])
  self.assertFalse(decode('X-UNKNOWN','grc')['recognized'])
if __name__=='__main__':unittest.main()
