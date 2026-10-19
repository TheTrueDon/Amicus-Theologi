"""HTTP/browser API integration for the optional independent source window."""
import os
import tempfile
import unittest
from fastapi.testclient import TestClient

from backend.database import init_db
from backend.main import app


class SourceWindowApiTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(prefix='amicus-sources-api-')
        self.previous=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.folder.name
        init_db()
        self.client=TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None,None,None)
        if self.previous is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.previous
        self.folder.cleanup()

    def test_separate_window_manual_wizard_word_tools_and_notes(self):
        response=self.client.get('/quellenstudium')
        self.assertEqual(response.status_code,200)
        self.assertIn('Quellenstudium',response.text)
        self.assertEqual(self.client.get('/assets/sources.js').status_code,200)
        catalog=self.client.get('/api/sources/catalog')
        self.assertEqual(catalog.status_code,200)
        self.assertEqual({m['category'] for m in catalog.json()},
                         {'quellen','lexika','sprachen','hilfsmittel'})
        self.assertIn('Bibeltext',self.client.get('/').text)
        args=dict(module_id='test-corpus',title='Testquelle',author='Autor',
                  language='la',edition='Test 1900',license_name='CC0',
                  provenance='Eigene Testdaten',version='1')
        response=self.client.post('/api/sources/import',data=args,
            files={'file':('corpus.csv',b'ref,text\nI.1,"Amicus bonus venit."\n','text/csv')})
        self.assertEqual(response.status_code,200,response.text)
        self.assertEqual(response.json()['sections'],1)
        self.assertEqual(len(self.client.get('/api/sources/modules').json()),1)
        self.assertEqual(self.client.get('/api/sources/sections',params={'module_id':'test-corpus'}).json()[0]['ref'],'I.1')
        self.assertEqual(self.client.get('/api/sources/passage',params={'module_id':'test-corpus','ref':'I.1'}).json()['tokens'][0]['surface'],'Amicus')
        result=self.client.get('/api/sources/search',params={'q':'Amicus'}).json()
        self.assertEqual(result['total'],1)
        form=b'ref,position,surface,lemma,morph\nI.1,1,Amicus,amicus,Case=Nom\nI.1,2,bonus,bonus,Case=Nom\nI.1,3,venit,venio,VerbForm=Fin\n'
        response=self.client.post('/api/sources/annotations/import',data={'module_id':'test-corpus'},
                                  files={'file':('tokens.csv',form,'text/csv')})
        self.assertEqual(response.status_code,200,response.text)
        word=self.client.get('/api/sources/word',params={'module_id':'test-corpus','ref':'I.1','position':1}).json()
        self.assertTrue(word['has_annotation'])
        self.assertEqual(word['lemma'],'amicus')
        self.assertEqual(self.client.get('/api/sources/search',params={'lemma':'amicus'}).json()['total'],1)
        response=self.client.put('/api/sources/note',json={'module_id':'test-corpus','ref':'I.1','content':'Meine Übersetzung'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(self.client.get('/api/sources/note',
            params={'module_id':'test-corpus','ref':'I.1'}).json()['content'],'Meine Übersetzung')
        self.assertEqual(self.client.get('/api/books').status_code,200)

    def test_invalid_import_does_not_leave_a_module(self):
        args=dict(module_id='bad-source',title='Bad',author='Autor',
                  language='he',edition='Test',license_name='CC0',provenance='Test')
        response=self.client.post('/api/sources/import',data=args,
          files={'file':('x.csv',b'ref,text\nA,foo\nA,bar\n','text/csv')})
        self.assertEqual(response.status_code,422)
        self.assertEqual(self.client.get('/api/sources/modules').json(),[])


if __name__=='__main__':
    unittest.main()
