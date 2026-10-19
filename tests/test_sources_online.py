"""Optional real-network checks; disabled in normal offline CI runs."""
import os
import tempfile
import unittest

from backend.database import init_db
from backend.sources import install_catalog, modules, passage
from backend.lexicon import lookup


@unittest.skipUnless(os.environ.get('AMICUS_TEST_SOURCE_NETWORK') == '1',
                     'Online-Katalogtests sind standardmäßig deaktiviert.')
class RealSourceCatalogTests(unittest.TestCase):
    def test_full_annotated_augustine_and_patristic_greek(self):
        with tempfile.TemporaryDirectory(prefix='amicus-online-morph-fix-') as temp:
            previous=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
            os.environ['AMICUS_THEOLOGI_DATA_DIR']=temp
            try:
                init_db()
                for item,expected in (('quellen-confessiones-annotiert',3000),
                                      ('quellen-severian-annotiert',8)):
                    result=install_catalog(item)
                    self.assertGreater(result['annotated_sections'],expected,item)
                    module=next(m for m in modules() if m['id']==item)
                    self.assertGreater(module['annotated_tokens'],100,item)
                    from backend.sources import sections_for,word_analysis
                    first=sections_for(item)[0]['ref']
                    self.assertTrue(word_analysis(item,first,1)['lemma'],item)
                    print(item,result['annotated_sections'],'Abschnitte mit Annotationen',flush=True)
            finally:
                if previous is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
                else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=previous

    def test_three_original_language_sources(self):
        with tempfile.TemporaryDirectory(prefix='amicus-online-catalog-') as temp:
            previous=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
            os.environ['AMICUS_THEOLOGI_DATA_DIR']=temp
            try:
                init_db()
                for entry in ('quellen-cicero','quellen-platon','quellen-avot1'):
                    result=install_catalog(entry)
                    self.assertGreater(result['sections'],1)
                    module=next(m for m in modules() if m['id']==entry)
                    self.assertGreater(module['section_count'],1)
                    from backend.sources import sections_for
                    first=sections_for(entry)[0]['ref']
                    self.assertGreater(len(passage(entry,first)['tokens']),0)
                    print(entry, 'Abschnitte:',result['sections'], 'erste Stelle:',first)
            finally:
                if previous is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
                else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=previous

    def test_extended_patristic_and_hebrew_sources(self):
        with tempfile.TemporaryDirectory(prefix='amicus-online-patristic-') as temp:
            previous=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
            os.environ['AMICUS_THEOLOGI_DATA_DIR']=temp
            try:
                init_db()
                for item in ('quellen-augustinus','quellen-clemens','quellen-severian',
                             'quellen-avot2','quellen-berakhot','quellen-mishneh'):
                    result=install_catalog(item)
                    self.assertGreater(result['sections'],1,item)
                    print(item,result['sections'],'Abschnitte',flush=True)
            finally:
                if previous is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
                else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=previous

    def test_annotated_latin_and_greek_treebanks(self):
        with tempfile.TemporaryDirectory(prefix='amicus-online-treebank-') as temp:
            previous=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
            os.environ['AMICUS_THEOLOGI_DATA_DIR']=temp
            try:
                init_db()
                for item in ('quellen-ittb','quellen-ud-grc'):
                    result=install_catalog(item)
                    self.assertGreater(result['sections'],10,item)
                    self.assertGreater(result['annotated_sections'],10,item)
                    print(item,result,flush=True)
            finally:
                if previous is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
                else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=previous

    @unittest.skipUnless(os.environ.get('AMICUS_TEST_LARGE_LEXICON') == '1',
                         'Großer Wörterbuchdownload wird nur auf ausdrücklichen Testwunsch ausgeführt.')
    def test_large_latin_dictionary(self):
        with tempfile.TemporaryDirectory(prefix='amicus-latin-lexicon-') as temp:
            previous=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
            os.environ['AMICUS_THEOLOGI_DATA_DIR']=temp
            try:
                init_db()
                result=install_catalog('quellen-lewis-short')
                self.assertGreater(result['entries'],10000)
                self.assertGreater(len(lookup('la','amicus')),0)
                print('Lewis & Short:',result['entries'],'Einträge; amicus erfolgreich gefunden')
            finally:
                if previous is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
                else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=previous

    @unittest.skipUnless(os.environ.get('AMICUS_TEST_LARGE_LEXICON') == '1',
                         'Große Wörterbücher nur in separatem Integrationstest.')
    def test_pta_lsj_and_german_georges(self):
        with tempfile.TemporaryDirectory(prefix='amicus-online-lexica-') as temp:
            previous=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
            os.environ['AMICUS_THEOLOGI_DATA_DIR']=temp
            try:
                init_db()
                for item in ('quellen-lsj','quellen-georges'):
                    result=install_catalog(item)
                    self.assertGreater(result['entries'],10000,item)
                    print(item,result['entries'],'Stichwörter',flush=True)
                self.assertTrue(lookup('grc','λόγος'))
                self.assertTrue(lookup('la','amicus'))
            finally:
                if previous is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
                else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=previous


if __name__ == '__main__':
    unittest.main()
