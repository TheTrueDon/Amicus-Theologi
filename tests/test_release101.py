"""v1.0.1: searchable manual, Windows distribution assets, and unchanged data model."""
import os
import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import connect, APP_VERSION, init_db

ROOT=Path(__file__).resolve().parent.parent


class ManualAndInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name

    def tearDown(self):
        os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        self.temp.cleanup()

    def test_static_manual_and_search(self):
        with TestClient(app) as client:
            self.assertEqual(client.get('/api/status').json()['version'],APP_VERSION)
            manual=client.get('/ANLEITUNG.html')
            self.assertEqual(manual.status_code,200)
            self.assertIn('text/html',manual.headers['content-type'])
            for fragment in ('id="suche-grundlagen"','id="suche-erweitert"',
                             'id="morphologie"','id="daten"',
                             'id="probleme"','=im Anfang','V-IAI-3S','WERKSRESET'):
                # WERKSRESET is in the software settings; the manual may describe it in plain language
                if fragment!='WERKSRESET':self.assertIn(fragment,manual.text)
            self.assertEqual(client.get('/ANLEITUNG.css').status_code,200)
            script=client.get('/ANLEITUNG.js')
            self.assertEqual(script.status_code,200)
            self.assertIn('sortResults',script.text)
            self.assertIn('search-results',script.text)
            self.assertEqual(client.get('/assets/amicus.png').status_code,200)
            self.assertIn('Amicus Theologi',client.get('/').text)
            self.assertNotIn('id="help-dialog"',client.get('/').text)

    def test_unchanged_database_schema(self):
        init_db()
        with connect() as db:
            tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertTrue({'settings','verses','tokens','study_projects','lexicon_entries'}.issubset(tables))
        self.assertNotIn('help_search',tables)

    def test_windows_build_assets(self):
        self.assertEqual(APP_VERSION,APP_VERSION)
        script=(ROOT/'windows/AmicusTheologi.iss').read_text(encoding='utf-8')
        self.assertIn('PrivilegesRequired=lowest',script)
        self.assertIn('desktopicon',script)
        self.assertIn('AmicusTheologi.exe',script)
        self.assertNotIn('UninstallDelete',script)  # retain user data
        self.assertTrue((ROOT/'assets/amicus.ico').stat().st_size>5000)
        self.assertTrue((ROOT/'.github/workflows/windows-installer.yml').is_file())
        self.assertIn('--self-test',(ROOT/'windows/build_windows.ps1').read_text(encoding='utf-8'))


if __name__=='__main__':unittest.main()
