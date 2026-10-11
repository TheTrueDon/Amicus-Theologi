"""v1.0.5: curated SWORD library and saved parallel edition selection."""
import os
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.database import init_db, connect, APP_VERSION
from backend.bible_catalog import BIBLES, bible_catalog, install_bible_from_catalog
from backend.main import app
from backend.library import install_module


class EditionInstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ['AMICUS_THEOLOGI_DATA_DIR'] = self.temp.name
        init_db()

    def tearDown(self):
        os.environ.pop('AMICUS_THEOLOGI_DATA_DIR', None)
        self.temp.cleanup()

    def test_version_and_curated_records(self):
        self.assertEqual(APP_VERSION, '1.0.7')
        self.assertEqual(len(BIBLES), 5)
        self.assertTrue(all(x['base'].startswith('https://www.crosswire.org/') for x in BIBLES.values()))
        self.assertIn('GerElb1905', BIBLES)
        self.assertEqual({x['id'] for x in bible_catalog()}, set(BIBLES))

    def test_unknown_source_never_downloaded(self):
        with patch('backend.bible_catalog.download_bible') as dl:
            with self.assertRaisesRegex(ValueError, 'nicht im geprüften Katalog'):
                install_bible_from_catalog('UnknownBible')
            dl.assert_not_called()

    def test_install_preserves_other_content_and_saved_settings(self):
        install_module('example','Ein Beispiel','de','User','User','1',[('Joh',1,1,'Beispiel')])
        with patch('backend.bible_catalog.download_bible', return_value=b'PKfake'), \
             patch('backend.bible_catalog.parse_sword', return_value=({('Joh',1,1):'Im Anfang war das Wort.',('Gen',1,1):'Im Anfang...'} | {('Ps',1,i):'Ein Psalm' for i in range(1,1000)}, [], 'other', 'GerElb1905')) as parser:
            out = install_bible_from_catalog('GerElb1905')
            self.assertEqual(out['module_id'], 'sword-gerelb1905')
            self.assertGreaterEqual(out['verses'], 1000)
            self.assertEqual(parser.call_args.kwargs['selected'], 'GerElb1905')
        with connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM modules').fetchone()[0],2)
            self.assertEqual(db.execute('SELECT text FROM verses WHERE module_id=?',('example',)).fetchone()[0],'Beispiel')
        self.assertTrue(next(x for x in bible_catalog() if x['id']=='GerElb1905')['installed'])
        with patch('backend.bible_catalog.download_bible') as dl:
            with self.assertRaisesRegex(ValueError,'bereits installiert'):
                install_bible_from_catalog('GerElb1905')
            dl.assert_not_called()

    def test_partial_wrong_module_rejected_atomically(self):
        with patch('backend.bible_catalog.download_bible', return_value=b'PKfake'), \
             patch('backend.bible_catalog.parse_sword', return_value=({('Joh',1,1):'Text'}, [],'other','OtherBible')):
            with self.assertRaises(ValueError):install_bible_from_catalog('GerElb1905')
        with connect() as db:self.assertEqual(db.execute('SELECT count(*) FROM modules').fetchone()[0],0)

    def test_settings_validation_and_old_setting_migration(self):
        with TestClient(app) as client:
            s=client.get('/api/settings').json()
            self.assertEqual(s['display_module_ids'],['*'])
            self.assertEqual(s['display_module_order'],[])
            self.assertEqual(client.patch('/api/settings',json={'display_module_ids':[]}).status_code,200)
            self.assertEqual(client.patch('/api/settings',json={'display_module_ids':['not-installed']}).status_code,422)
            self.assertEqual(client.patch('/api/settings',json={'display_module_ids':['*','*']}).status_code,422)
            r=client.patch('/api/settings',json={'display_module_ids':['*']})
            self.assertEqual(r.json()['display_module_ids'],['*'])
            self.assertEqual(len(client.get('/api/bible-catalog').json()),5)
            self.assertEqual(client.post('/api/bible-catalog/invalid/install').status_code,422)

    def test_no_forced_database_migration(self):
        with connect() as db:
            self.assertEqual([c[1] for c in db.execute('PRAGMA table_info(modules)')],
                ['id','title','language','kind','license','provenance','version','installed_at'])


if __name__ == '__main__':
    unittest.main()
