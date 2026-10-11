"""1.0.9 regression checks: first-run migration and uninstall packaging."""
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend import database


class StorageMigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.original_env = dict(os.environ)
        os.environ.pop('AMICUS_THEOLOGI_DATA_DIR', None)
        os.environ['XDG_DATA_HOME'] = str(self.root)

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.original_env)
        self.tmp.cleanup()

    @unittest.skipIf(os.name == 'nt', 'Uses Linux XDG paths in CI')
    def test_old_database_and_backups_are_migrated_without_data_loss(self):
        previous = database._previous_data_dir()
        previous.mkdir(parents=True)
        with sqlite3.connect(previous / 'amicus_theologi.sqlite3') as con:
            con.execute('CREATE TABLE old_data (value TEXT)')
            con.execute('INSERT INTO old_data VALUES (?)', ('persoenliche-notiz',))
        (previous / 'backups').mkdir()
        (previous / 'backups' / 'safe.zip').write_bytes(b'saved')
        current = database.data_dir()
        self.assertEqual(current, self.root / 'amicus-theologi')
        self.assertFalse(previous.exists())
        self.assertEqual((current / 'backups' / 'safe.zip').read_bytes(), b'saved')
        with sqlite3.connect(current / 'amicus_theologi.sqlite3') as con:
            self.assertEqual(con.execute('SELECT value FROM old_data').fetchone()[0], 'persoenliche-notiz')

    @unittest.skipIf(os.name == 'nt', 'Uses Linux XDG paths in CI')
    def test_collision_fails_closed_without_overwriting_user_data(self):
        previous = database._previous_data_dir()
        previous.mkdir(parents=True)
        (previous / 'old.txt').write_text('old', encoding='utf-8')
        new = self.root / 'amicus-theologi'
        new.mkdir()
        (new / 'new.txt').write_text('new', encoding='utf-8')
        with self.assertRaises(RuntimeError):
            database.data_dir()
        self.assertEqual((previous / 'old.txt').read_text(), 'old')
        self.assertEqual((new / 'new.txt').read_text(), 'new')

    @unittest.skipIf(os.name == 'nt', 'Uses Linux XDG paths in CI')
    def test_explicit_data_location_stays_unchanged(self):
        chosen = self.root / 'chosen'
        with patch.dict(os.environ, {'AMICUS_THEOLOGI_DATA_DIR': str(chosen)}):
            self.assertEqual(database.data_dir(), chosen)
            self.assertTrue(chosen.is_dir())


class InstallerCleanupTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]

    def test_windows_uninstaller_removes_local_app_data(self):
        script = (self.ROOT / 'windows/AmicusTheologi.iss').read_text(encoding='utf-8')
        self.assertIn('[UninstallDelete]', script)
        self.assertIn('Type: filesandordirs; Name: "{localappdata}\\AmicusTheologi"', script)

    def test_ubuntu_removes_data_only_on_uninstall(self):
        script = (self.ROOT / 'linux/build_ubuntu_deb.sh').read_text(encoding='utf-8')
        self.assertIn('DEBIAN/postrm', script)
        self.assertIn('remove|purge)', script)
        self.assertIn('upgrade|failed-upgrade|abort-install', script)
        self.assertIn('rm -rf -- "$data"', script)
        self.assertIn('[ ! -L "$data" ]', script)

    def test_no_previous_branding_in_program_sources(self):
        prior = bytes((98, 105, 98, 108, 101, 119, 111, 101, 114, 107, 115)).decode('ascii')
        for folder in ('backend', 'frontend', 'windows', 'linux'):
            for p in (self.ROOT / folder).rglob('*'):
                if p.is_file() and p.suffix in {'.py', '.js', '.html', '.css', '.iss', '.sh', '.desktop', '.xml'}:
                    self.assertNotIn(prior, p.read_text(encoding='utf-8').lower(), str(p))


if __name__ == '__main__':
    unittest.main()
