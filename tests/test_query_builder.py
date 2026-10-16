import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.advanced_search import advanced_search
from backend.database import init_db
from backend.library import install_module, read_import
from backend.morphology import import_annotations, parse_annotation_file
from backend.query_builder import query_search

ROOT=Path(__file__).resolve().parents[1]/'modules/examples'


class QueryBuilderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.env=patch.dict(os.environ,{'AMICUS_THEOLOGI_DATA_DIR':self.tmp.name})
        self.env.start()
        init_db()
        install_module('demo-grc','Greek demo','grc','demo','test fixture','1',
                       read_import((ROOT/'johannes_1_1_grc.tsv').read_bytes()))
        import_annotations('demo-grc',parse_annotation_file((ROOT/'johannes_1_1_grc_morph.tsv').read_bytes()))

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_three_conditions_and_order_are_reproducible(self):
        criteria={
            'module_id':'demo-grc','book':'Joh','connector':'all','distance':20,'order':'before',
            'conditions':[{'surface':'Ἐν'},{'lemma':'θεός'},{'lemma':'λόγος'}],
        }
        result=query_search(criteria)
        self.assertEqual(result['total'],1)
        self.assertEqual(result['criteria'],criteria)
        self.assertEqual(result['results'][0]['book'],'Joh')

    def test_distance_order_and_boolean_connector(self):
        pair={'conditions':[{'lemma':'θεός'},{'lemma':'εἰμί'}],
              'connector':'all','distance':0,'order':'before','module_id':'demo-grc'}
        self.assertEqual(query_search(pair)['total'],1)
        pair.update({'order':'after','distance':2})
        self.assertEqual(query_search(pair)['total'],1)
        pair.update({'connector':'any','order':'any','distance':5,
                     'conditions':[{'surface':'Ἐν'},{'lemma':'θεός'}]})
        self.assertEqual(query_search(pair)['total'],1)

    def test_single_clause_matches_existing_search_and_invalid_query_is_rejected(self):
        result=query_search({'conditions':[{'lemma':'λόγος'}],'module_id':'demo-grc'})
        old=advanced_search(lemma='λόγος',module_id='demo-grc')
        self.assertEqual(result['total'],old['total'])
        self.assertEqual(result['total'],1)
        for criteria in (
            {'conditions':[{}]},
            {'conditions':[{'lemma':'λόγος'}]*6},
            {'conditions':[{'lemma':'λόγος'}],'connector':'any','order':'before'},
        ):
            with self.subTest(criteria=criteria),self.assertRaises(ValueError):
                query_search(criteria)
        self.assertEqual(query_search({'conditions':[{'lemma':"' OR 1=1 --"}]})['total'],0)


if __name__=='__main__':unittest.main()
