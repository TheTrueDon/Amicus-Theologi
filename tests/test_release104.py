"""Version 1.0.4 - study note input has contrast in both themes."""
from pathlib import Path
import unittest
from backend.database import APP_VERSION

ROOT = Path(__file__).resolve().parents[1]

class StudyFieldContrastTests(unittest.TestCase):
    def test_release_version(self):
        self.assertGreaterEqual(tuple(map(int, APP_VERSION.split('.'))), (1,0,4))
        self.assertEqual((ROOT / 'VERSION').read_text(encoding='utf-8').strip(), APP_VERSION)

    def test_study_note_uses_theme_tokens_not_missing_panel_token(self):
        css = (ROOT / 'frontend/style.css').read_text(encoding='utf-8')
        self.assertIn('.study-note-form textarea{', css)
        self.assertIn('background:var(--surface2);color:var(--txt);caret-color:var(--txt)', css)
        self.assertNotIn('.study-note-form textarea{width:100%;box-sizing:border-box;min-height:95px;padding:10px;border:1px solid var(--line,#555);border-radius:6px;background:var(--panel', css)
        self.assertIn('body[data-theme="dark"] { color-scheme: dark; }', css)
        self.assertIn('body[data-theme="light"] { color-scheme: light; }', css)
        self.assertIn('.study-note-form textarea:focus-visible', css)
        self.assertIn('.study-note-form textarea::placeholder', css)

    def test_study_note_keeps_dynamic_field_and_save(self):
        js = (ROOT / 'frontend/app.js').read_text(encoding='utf-8')
        self.assertIn("el('form','study-note-form')", js)
        self.assertIn("el('textarea')", js)
        self.assertIn("'Notiz speichern'", js)
