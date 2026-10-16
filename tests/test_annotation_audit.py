import os
import tempfile
import unittest
from pathlib import Path

from backend.annotation_audit import audit_annotations
from backend.database import connect, init_db
from backend.library import install_module, read_import
from backend.morphology import import_annotations, parse_annotation_file

ROOT=Path(__file__).resolve().parents[1]


class AnnotationAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name
        init_db()
        examples=ROOT/'modules/examples'
        install_module('audit-grc','Greek demo','grc','demo','test fixture','1',
                       read_import((examples/'johannes_1_1_grc.tsv').read_bytes()))
        annotation=parse_annotation_file((examples/'johannes_1_1_grc_morph.tsv').read_bytes())
        import_annotations('audit-grc',annotation)

    def tearDown(self):
        os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        self.temp.cleanup()

    def test_passes_for_matching_import(self):
        result=audit_annotations('audit-grc')
        self.assertEqual(result['status'],'passed')
        self.assertEqual(result['counts']['annotated_verses'],1)
        self.assertEqual(result['counts']['annotated_words'],17)
        self.assertTrue(all(result['checks'].values()))

    def test_detects_surface_position_and_analysis_problems(self):
        with connect() as db:
            db.execute("UPDATE tokens SET surface='λανθ' WHERE module_id='audit-grc' AND position=1")
            db.execute("UPDATE tokens SET position=19 WHERE module_id='audit-grc' AND position=17")
            db.execute("UPDATE tokens SET lemma='' WHERE module_id='audit-grc' AND position=2")
        result=audit_annotations('audit-grc')
        self.assertEqual(result['status'],'failed')
        self.assertFalse(result['checks']['token_surfaces_match_verse_text'])
        self.assertFalse(result['checks']['token_positions_contiguous'])
        self.assertFalse(result['checks']['lemma_and_morphology_present'])
        self.assertIn('Johannes 1,1',result['issues']['surface_mismatch_refs'])
        self.assertEqual(result['issue_counts']['position'],1)

    def test_no_annotations_is_not_reported_as_pass(self):
        with connect() as db:
            db.execute("DELETE FROM tokens WHERE module_id='audit-grc'")
        self.assertEqual(audit_annotations('audit-grc')['status'],'no_annotations')

    def test_unknown_and_non_morphological_modules_rejected(self):
        with self.assertRaisesRegex(ValueError,'nicht gefunden'):
            audit_annotations('missing')
        install_module('plain-de','German demo','de','demo','test fixture','1',
                       [('Joh',1,1,'Im Anfang war das Wort.')])
        with self.assertRaisesRegex(ValueError,'nur für griechische'):
            audit_annotations('plain-de')


if __name__=='__main__':
    unittest.main()
