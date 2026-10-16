import os
import tempfile
import unittest

from fastapi.testclient import TestClient
from backend.database import init_db
from backend.library import install_module
from backend.main import app


class SavedSearchApiTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.old=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name
        init_db()
        install_module('greek','Greek text','grc','demo','test fixture','1',[('Joh',1,1,'λόγος')])

    def tearDown(self):
        if self.old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.old
        self.temp.cleanup()

    def test_create_list_delete_and_validate(self):
        with TestClient(app) as client:
            body={'name':'Johannes-Lemma','criteria':{'module_id':'greek','book':'Joh','lemma':'λόγος','distance':2,'order':'any'}}
            created=client.post('/api/saved-searches',json=body)
            self.assertEqual(created.status_code,201,created.text)
            saved=created.json()
            self.assertEqual(saved['criteria']['book'],'Joh')
            self.assertEqual(client.get('/api/saved-searches').json(),[saved])
            duplicate=client.post('/api/saved-searches',json={**body,'name':'JOHANNES-LEMMA'})
            self.assertEqual(duplicate.status_code,422)
            invalid=client.post('/api/saved-searches',json={'name':'Ungültig','criteria':{'invented':'x'}})
            self.assertEqual(invalid.status_code,422)
            self.assertEqual(client.delete('/api/saved-searches/'+str(saved['id'])).status_code,200)
            self.assertEqual(client.get('/api/saved-searches').json(),[])
            self.assertEqual(client.delete('/api/saved-searches/'+str(saved['id'])).status_code,404)


if __name__=='__main__':unittest.main()
