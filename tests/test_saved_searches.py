import os
import tempfile
import unittest

from backend.database import factory_reset, init_db
from backend.library import install_module
from backend.saved_searches import create_saved_search, delete_saved_search, list_saved_searches


class SavedSearchStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.old=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name
        init_db()
        install_module('greek','Greek text','grc','demo','test fixture','1',
                       [('Joh',1,1,'λόγος'),('Gen',1,1,'θεός')])

    def tearDown(self):
        if self.old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.old
        self.temp.cleanup()

    def test_save_list_and_delete_preserve_search_scope_and_date(self):
        item=create_saved_search('Johannes-Wort',{
            'module_id':'greek','book':'Joh','surface':'λόγος',
            'distance':3,'order':'any'})
        self.assertEqual(item['criteria']['module_id'],'greek')
        self.assertEqual(item['criteria']['book'],'Joh')
        self.assertEqual(item['criteria']['surface'],'λόγος')
        self.assertTrue(item['created_at'])
        self.assertEqual(list_saved_searches(),[item])
        self.assertTrue(delete_saved_search(item['id']))
        self.assertFalse(delete_saved_search(item['id']))
        self.assertEqual(list_saved_searches(),[])

    def test_invalid_criteria_and_duplicate_names_rejected(self):
        with self.assertRaisesRegex(ValueError,'Mindestens ein Kriterium'):
            create_saved_search('Leer',{'distance':5,'order':'any'})
        with self.assertRaisesRegex(ValueError,'unbekannte Felder'):
            create_saved_search('Unbekannt',{'surface':'λόγος','invented':'x'})
        create_saved_search('Λόγος',{'module_id':'greek','lemma':'λόγος'})
        with self.assertRaisesRegex(ValueError,'diesem Namen'):
            create_saved_search('λόγος',{'module_id':'greek','lemma':'λόγος'})

    def test_factory_reset_clears_saved_searches(self):
        create_saved_search('Bleibt nicht',{'module_id':'greek','surface':'λόγος'})
        factory_reset()
        self.assertEqual(list_saved_searches(),[])

    def test_structured_query_conditions_are_saved(self):
        criteria={'module_id':'greek','book':'Joh','conditions':[{'surface':'λόγος'},{'lemma':'θεός'}],
                  'connector':'all','distance':4,'order':'before'}
        item=create_saved_search('Mehrere Bedingungen',criteria)
        self.assertEqual(item['criteria'],criteria)


if __name__=='__main__':unittest.main()
