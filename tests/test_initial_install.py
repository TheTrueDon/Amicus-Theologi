import json
import tempfile
import unittest
import zipfile
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

from backend import initial_install


class InitialInstallTests(unittest.TestCase):
    def test_plan_includes_all_installable_catalogs_and_bundled_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            package_dir = Path(tmp)
            package_path = package_dir / 'example.amicus-source'
            with zipfile.ZipFile(package_path, 'w') as archive:
                archive.writestr('manifest.json', json.dumps({
                    'source': {'id': 'package-1', 'title': 'Offlinepaket'},
                }))

            class FakeConnection:
                def __enter__(self):
                    return self

                def __exit__(self, *_):
                    return False

                def execute(self, _query):
                    return [("already-installed-package",)]

            with (
                patch.object(initial_install, 'PACKAGE_DIR', package_dir),
                patch.object(initial_install, 'connect', FakeConnection),
                patch.object(initial_install, 'bible_catalog', return_value=[
                    {'id': 'bible-new', 'module_id': 'bible-new', 'title': 'Bibel neu', 'installed': False},
                    {'id': 'bible-old', 'module_id': 'bible-old', 'title': 'Bibel vorhanden', 'installed': True},
                ]),
                patch.object(initial_install, 'catalog_list', return_value=[
                    {'id': 'lexicon-1', 'title': 'Lexikon', 'installed': False},
                ]),
                patch.object(initial_install.sources, 'catalog_list', return_value=[
                    {'id': 'source-1', 'title': 'Primärquelle', 'kind': 'text', 'installed': False},
                    {'id': 'lexicon-1', 'title': 'Delegiertes Lexikon', 'kind': 'lexicon', 'delegated': True},
                    {'id': 'reference-1', 'title': 'Onlinehilfe', 'kind': 'reference'},
                ]),
            ):
                tasks, skipped, external = initial_install._build_plan()

        self.assertEqual({task['id'] for task in tasks},
                         {'bible-new', 'lexicon-1', 'source-1', 'package-1'})
        self.assertEqual(skipped, 1)
        self.assertEqual(external, ['Onlinehilfe'])

    def test_progress_finishes_and_continues_after_one_failed_source(self):
        job_id = 'test-job'
        initial_install._JOB = {
            'id': job_id, 'done': False, 'phase': '', 'current_title': '',
            'completed': 0, 'total': 2, 'progress': 0, 'installed': 0,
            'skipped': 0, 'errors': [], 'external_count': 0, 'external_titles': [],
        }

        def fail():
            raise ValueError('Netz nicht erreichbar')

        initial_install._run(job_id, [
            {'id': 'first', 'title': 'Fehlerquelle', 'run': fail},
            {'id': 'second', 'title': 'Erfolgsquelle', 'run': lambda: None},
        ])
        result = initial_install.installation_status(job_id)
        self.assertTrue(result['done'])
        self.assertEqual(result['completed'], 2)
        self.assertEqual(result['progress'], 100)
        self.assertEqual(result['installed'], 1)
        self.assertEqual(result['errors'][0]['title'], 'Fehlerquelle')
        self.assertEqual(result['errors'][0]['message'], 'Netz nicht erreichbar')
        initial_install._JOB = None


if __name__ == '__main__':
    unittest.main()
