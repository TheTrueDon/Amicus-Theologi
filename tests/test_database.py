import os
import tempfile
import unittest
from unittest.mock import patch
from backend.database import init_db, get_settings, set_settings, connect

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.env=patch.dict(os.environ,{'AMICUS_THEOLOGI_DATA_DIR':self.tmp.name})
        self.env.start()
        init_db()
    def tearDown(self):
        self.env.stop();self.tmp.cleanup()
    def test_defaults(self):
        self.assertEqual(get_settings()['theme'],'dark')
    def test_persistence(self):
        set_settings({'theme':'light','font_size':20})
        self.assertEqual(get_settings()['font_size'],20)
        init_db()
        self.assertEqual(get_settings()['theme'],'light')
    def test_schema(self):
        with connect() as db:
            names={row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({'settings','modules','verses','tokens','verse_mapping','saved_searches'}<=names)
    def test_saved_search_schema_is_additive(self):
        set_settings({'theme':'light'})
        with connect() as db:db.execute('DROP TABLE saved_searches')
        init_db()
        self.assertEqual(get_settings()['theme'],'light')
        with connect() as db:
            self.assertIsNotNone(db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='saved_searches'").fetchone())
if __name__=='__main__':unittest.main()
