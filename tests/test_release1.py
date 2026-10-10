"""1.0 critical workflows: first install, backup integrity, guided recovery, migration."""
import hashlib
import io
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, connect, get_settings, set_settings
from backend.maintenance import (
    make_backup, stage_restore, apply_staged_restore, diagnostics,
    install_demo_bundle, automatic_upgrade_backup, record_release_version,
    pending_restore,
)


class Release1Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ['AMICUS_THEOLOGI_DATA_DIR'] = self.tmp.name
        init_db()

    def tearDown(self):
        os.environ.pop('AMICUS_THEOLOGI_DATA_DIR', None)
        self.tmp.cleanup()

    def test_first_run_demo_and_diagnostics(self):
        with TestClient(app) as client:
            self.assertFalse(client.get('/api/settings').json()['welcome_completed'])
            self.assertEqual(client.get('/api/diagnostics').json()['counts']['bibeltexte'],0)
            self.assertEqual(client.post('/api/demo/install').status_code,200)
            self.assertEqual(client.get('/api/diagnostics').json()['counts']['bibeltexte'],4)
            self.assertEqual(len(client.get('/api/lexica').json()),2)
            greek=client.get('/api/chapter',params={'book':'Joh','chapter':1}).json()
            self.assertIn('demo-jn-grc', [m['id'] for m in greek['modules']])
            self.assertTrue(any(x['module_id']=='demo-jn-grc' for x in greek['tokens']))
            self.assertEqual(client.post('/api/demo/install').json()['installed'],[])
            self.assertEqual(client.patch('/api/settings',json={'welcome_completed':True}).status_code,200)
            self.assertTrue(get_settings()['welcome_completed'])

    def test_full_backup_restore_after_mutations(self):
        install_demo_bundle()
        with connect() as db:
            pid = db.execute("INSERT INTO study_projects(title,description) VALUES ('Archiv','Test')").lastrowid
            db.execute('INSERT INTO study_notes(project_id,book,chapter,verse,content) VALUES (?,?,?,?,?)',
                       (pid,'Joh',1,1,'Wertvolle Notiz'))
        set_settings({'theme':'light'})
        archive=make_backup()
        self.assertTrue(zipfile.is_zipfile(archive))
        with zipfile.ZipFile(archive) as z:
            manifest=json.loads(z.read('manifest.json'))
            self.assertEqual(manifest['format'],'amicus-theologi-backup')
            self.assertEqual(hashlib.sha256(z.read('database.sqlite3')).hexdigest(),manifest['sha256'])
        with connect() as db:
            db.execute('DELETE FROM study_notes')
            db.execute('DELETE FROM lexicon_modules')
        set_settings({'theme':'dark'})
        result=stage_restore(archive)
        self.assertTrue(result['restoration_prepared'])
        self.assertTrue(pending_restore())
        self.assertTrue(apply_staged_restore())
        self.assertFalse(pending_restore())
        self.assertEqual(get_settings()['theme'],'light')
        with connect() as db:
            self.assertEqual(db.execute('SELECT content FROM study_notes').fetchone()[0],'Wertvolle Notiz')
            self.assertEqual(db.execute('SELECT COUNT(*) FROM lexicon_modules').fetchone()[0],2)
        self.assertTrue(list((Path(self.tmp.name)/'backups').glob('vor-wiederherstellung-*')))

    def test_reject_checksum_tampering(self):
        archive=make_backup()
        with zipfile.ZipFile(archive) as original:
            meta=json.loads(original.read('manifest.json'))
            meta['sha256']='0'*64
            data=original.read('database.sqlite3')
        manipulated=Path(self.tmp.name)/'manipulated.zip'
        with zipfile.ZipFile(manipulated,'w') as z:
            z.writestr('manifest.json',json.dumps(meta))
            z.writestr('database.sqlite3',data)
        with self.assertRaisesRegex(ValueError,'Prüfsumme'):
            stage_restore(manipulated)
        self.assertFalse(pending_restore())
        self.assertTrue(diagnostics()['database_ok'])

    def test_reject_arbitrary_database_and_zip_members(self):
        bad=Path(self.tmp.name)/'bad.zip'
        with zipfile.ZipFile(bad,'w') as z:
            z.writestr('manifest.json','{}')
            z.writestr('database.sqlite3',b'wrong')
            z.writestr('../evil.txt','x')
        with self.assertRaisesRegex(ValueError,'genau'):
            stage_restore(bad)
        self.assertFalse((Path(self.tmp.name)/'evil.txt').exists())

    def test_api_origin_and_maintenance_mode(self):
        with TestClient(app) as client:
            self.assertEqual(client.post('/api/demo/install',headers={'origin':'https://evil.example'}).status_code,403)
            self.assertEqual(client.get('/api/status',headers={'host':'some.external.example'}).status_code,403)
            self.assertEqual(client.post('/api/demo/install').status_code,200)
            backup=client.get('/api/backup/download')
            self.assertEqual(backup.status_code,200)
            self.assertTrue(backup.content[:2]==b'PK')
            restored=client.post('/api/backup/restore',files={'file':('save.zip',backup.content,'application/zip')})
            self.assertEqual(restored.status_code,200,restored.text)
            self.assertEqual(client.post('/api/demo/install').status_code,409)
            self.assertEqual(client.get('/api/diagnostics').json()['pending_restore'],True)
            response=client.post('/api/backup/restore/cancel')
            self.assertEqual(response.status_code,200)
            self.assertTrue(response.json()['canceled'])
            self.assertEqual(client.post('/api/demo/install').status_code,200)
        self.assertFalse(pending_restore())

    def test_upgrade_backup_only_once(self):
        install_demo_bundle()
        self.assertTrue(automatic_upgrade_backup())
        backups=list((Path(self.tmp.name)/'backups').glob('vor-update-1.0-*'))
        self.assertEqual(len(backups),1)
        record_release_version()
        self.assertFalse(automatic_upgrade_backup())
        self.assertEqual(len(list((Path(self.tmp.name)/'backups').glob('vor-update-1.0-*'))),1)


if __name__=='__main__':unittest.main()
