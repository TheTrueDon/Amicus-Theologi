"""1.0.9: test the persisted verse/edition display preference and existing data model."""
import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.database import APP_VERSION, init_db, get_settings, connect
from backend.main import app
from backend.library import install_module


class VerseComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        os.environ['AMICUS_THEOLOGI_DATA_DIR'] = self.temp.name
        init_db()

    def tearDown(self):
        os.environ.pop('AMICUS_THEOLOGI_DATA_DIR', None)
        self.temp.cleanup()

    def test_new_install_is_versewise_and_edition_mode_persists(self):
        self.assertEqual(APP_VERSION, '1.0.9')
        with TestClient(app) as client:
            self.assertEqual(client.get('/api/settings').json()['text_layout'], 'verse')
            self.assertEqual(client.patch('/api/settings', json={'text_layout':'edition'}).status_code, 200)
            self.assertEqual(client.get('/api/settings').json()['text_layout'],'edition')
            self.assertEqual(client.patch('/api/settings', json={'text_layout':'verse'}).status_code, 200)
            self.assertEqual(client.patch('/api/settings', json={'text_layout':'invalid'}).status_code, 422)
        # Equivalent to a normal application restart/update.
        init_db()
        self.assertEqual(get_settings()['text_layout'],'verse')

    def test_older_settings_and_bible_content_untouched(self):
        install_module('lut','Luther','de','PD','Source','1',[('Joh',1,1,'Im Anfang'),('Joh',1,2,'Das Wort')])
        install_module('elb','Elberfelder','de','PD','Source','1',[('Joh',1,1,'Im Anfang war')])
        install_module('lxx','Septuaginta','grc','PD','Source','1',[('Gen',1,1,'ἐν ἀρχῇ')])
        with connect() as db:
            db.execute('DELETE FROM settings WHERE key=?',('text_layout',))  # Simulate v1.0.5.
            db.execute('INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)',('active_reference','"Joh 1,1"'))
        init_db()
        with TestClient(app) as client:
            self.assertEqual(client.get('/api/settings').json()['text_layout'],'verse')
            data=client.get('/api/chapter',params={'book':'Joh','chapter':1}).json()
            self.assertEqual({x['id'] for x in data['modules']},{'lut','elb'})
            self.assertEqual(data['available_verses'],[1,2])
            self.assertEqual([v['verse'] for v in next(x for x in data['modules'] if x['id']=='elb')['verses']],[1])
            self.assertEqual(len(client.get('/api/modules').json()),3)
        with connect() as db:
            self.assertEqual(db.execute('SELECT count(*) FROM verses').fetchone()[0],4)
            self.assertEqual(db.execute('SELECT count(*) FROM modules').fetchone()[0],3)
            self.assertEqual(db.execute('SELECT count(*) FROM study_projects').fetchone()[0],0)

    def test_user_interface_help_and_installer_consistent(self):
        root=Path(__file__).resolve().parents[1]
        html=(root/'frontend/index.html').read_text(encoding='utf-8')
        js=(root/'frontend/app.js').read_text(encoding='utf-8')
        self.assertIn('id="text-layout"',html)
        self.assertIn('Versweise vergleichen',html)
        self.assertIn('Nach Ausgabe anzeigen',html)
        self.assertIn('verse-group',js)
        self.assertIn('if(layout===\'verse\')',js)
        self.assertIn('Kein Text für diesen Vers',js)
        self.assertIn('window.amicusWordTools.enableHover',js)
        self.assertIn('paintHighlights();refreshStudyPane();',js)
        manual=(root/'ANLEITUNG.html').read_text(encoding='utf-8')
        portable=(root/'HANDBUCH_OFFLINE.html').read_text(encoding='utf-8')
        self.assertIn('Paralleltexte versweise vergleichen',manual)
        self.assertIn('Paralleltexte versweise vergleichen',portable)
        self.assertIn('Amicus Theologi',portable)
        self.assertIn('1.0.9',(root/'windows/AmicusTheologi.iss').read_text(encoding='utf-8'))
        self.assertEqual((root/'VERSION').read_text(encoding='utf-8').strip(),'1.0.9')

if __name__=='__main__': unittest.main()
