import io, os, tempfile, zipfile, unittest
from fastapi.testclient import TestClient
from backend.database import init_db, connect, get_settings
from backend.catalog import parse_step_lexicon, catalog_list
from backend.main import app

class CatalogTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.tmp.name;init_db()
 def tearDown(self):
  os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None);self.tmp.cleanup()
 def sample(self,name,lines):
  out=io.BytesIO()
  with zipfile.ZipFile(out,'w') as archive:
   archive.writestr('STEPBible-Data-master/Lexicons/'+name+' - Beispiel.txt',lines)
  return out.getvalue()
 def test_lexicon_parser(self):
  raw=self.sample('TBESG','G3056\tλόγος\tword, discourse\tSinn und Rede\nG1510\tεἰμί\tbe\tsein\n')
  items=parse_step_lexicon(raw,'TBESG');self.assertEqual(len(items),2);self.assertEqual(items[0][2],'G3056')
 def test_hebrew_parser(self):
  raw=self.sample('TBESH','H1254\tברא\tcreate\tto form\n')
  self.assertEqual(parse_step_lexicon(raw,'TBESH')[0][2],'H1254')
 def test_catalog(self):
  with TestClient(app) as c:
   self.assertEqual(len(c.get('/api/catalog').json()),6)
   self.assertEqual(c.post('/api/catalog/nonesuch/install').status_code,422)
 def test_reset(self):
  with connect() as db:
   db.execute("INSERT INTO modules(id,title,language,kind,license,provenance,version) VALUES('x','X','de','bible','demo','test','1')")
   db.execute("INSERT INTO verses(module_id,book,chapter,verse,text) VALUES('x','Joh',1,1,'Probe')")
  with TestClient(app) as c:
   url='/api/factory-reset';header={'origin':'http://127.0.0.1:8765','host':'127.0.0.1:8765'}
   self.assertEqual(c.post(url,json={'confirmation':'WERKSRESET'}).status_code,403)
   self.assertEqual(c.post(url,json={'confirmation':'FALSCH'},headers=header).status_code,422)
   self.assertEqual(c.post(url,json={'confirmation':'WERKSRESET'},headers=header).status_code,200)
   self.assertEqual(c.get('/api/modules').json(),[])
   self.assertEqual(get_settings()['theme'],'dark')
   self.assertEqual(c.get('/api/search',params={'q':'Probe'}).json()['total'],0)
