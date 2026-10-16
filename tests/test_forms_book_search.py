import os
import tempfile
import unittest
from pathlib import Path

from backend.advanced_search import advanced_search
from backend.database import connect, init_db
from backend.library import install_module, read_import
from backend.morphology import import_annotations, parse_annotation_file

EXAMPLES=Path(__file__).resolve().parents[1]/'modules/examples'


class FormsBookSearchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.old=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name
        init_db()
        install_module('greek-test','Greek test','grc','demo','test fixture','1',
                       read_import((EXAMPLES/'johannes_1_1_grc.tsv').read_bytes()))
        import_annotations('greek-test',parse_annotation_file((EXAMPLES/'johannes_1_1_grc_morph.tsv').read_bytes()))
        with connect() as db:
            db.execute("INSERT INTO verses(module_id,book,chapter,verse,text) VALUES('greek-test','Gen',1,1,'λόγος')")
        import_annotations('greek-test',{('Gen',1,1):[(1,'λόγος','λόγος','Substantiv',None)]})

    def tearDown(self):
        if self.old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.old
        self.temp.cleanup()

    def test_exact_form_search_respects_book_scope(self):
        all_books=advanced_search(module_id='greek-test',surface='λόγος')
        genesis=advanced_search(module_id='greek-test',book='Gen',surface='λόγος')
        self.assertEqual(all_books['total'],2)
        self.assertEqual(genesis['total'],1)
        self.assertEqual(genesis['results'][0]['book'],'Gen')


if __name__=='__main__':unittest.main()
