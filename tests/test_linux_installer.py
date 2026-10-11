"""Static and data-safety checks for Amicus Theologi's Ubuntu package."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class UbuntuInstallerTests(unittest.TestCase):
    def test_debian_package_layout_and_desktop_entry(self):
        builder=(ROOT/'linux/build_ubuntu_deb.sh').read_text(encoding='utf-8')
        desktop=(ROOT/'linux/amicus-theologi.desktop').read_text(encoding='utf-8')
        short=(ROOT/'linux/amicus-theologi-shortcut.desktop').read_text(encoding='utf-8')
        self.assertIn('dpkg-deb --root-owner-group --build', builder)
        self.assertIn('frontend:frontend', builder)
        self.assertIn('ANLEITUNG.html:.', builder)
        self.assertIn('/opt/amicus-theologi', builder)
        self.assertIn('/usr/share/applications', builder)
        self.assertIn('Package: amicus-theologi', builder)
        self.assertIn('Architecture: amd64', builder)
        self.assertIn('Exec=/opt/amicus-theologi/AmicusTheologi', desktop)
        self.assertIn('Icon=amicus-theologi', desktop)
        self.assertIn('Terminal=false', desktop)
        self.assertIn('--create-desktop-shortcut', short)
        self.assertTrue((ROOT/'assets/amicus.png').is_file())

    def test_app_data_outside_installed_program(self):
        database=(ROOT/'backend/database.py').read_text(encoding='utf-8')
        self.assertIn("'.local/share'", database)
        self.assertIn("'amicus-theologi'", database)
        self.assertNotIn('biblewoerks', database.lower())
        self.assertIn('DEBIAN/postrm', (ROOT/'linux/build_ubuntu_deb.sh').read_text(encoding='utf-8'))

    def test_linux_workflow_and_version_consistency(self):
        workflow=(ROOT/'.github/workflows/ubuntu-installer.yml').read_text(encoding='utf-8')
        version=(ROOT/'VERSION').read_text(encoding='utf-8').strip()
        self.assertEqual(version, '1.0.9')
        self.assertIn('ubuntu-24.04', workflow)
        self.assertIn('workflow_dispatch', workflow)
        self.assertIn('unittest discover', workflow)
        self.assertIn('linux/build_ubuntu_deb.sh', workflow)
        self.assertIn('upload-artifact@v6', workflow)
        self.assertIn('docs/UBUNTU_INSTALLATION.md', (ROOT/'README.md').read_text(encoding='utf-8'))

    def test_gui_and_server_self_tests_shipped(self):
        launcher=(ROOT/'windows/launcher.py').read_text(encoding='utf-8')
        self.assertIn('--gui-self-test', launcher)
        self.assertIn('--self-test', launcher)
        self.assertIn('--create-desktop-shortcut', launcher)
        self.assertIn("iconphoto(True,", launcher)
        self.assertIn('from windows.launcher import main', (ROOT/'linux/launcher.py').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
