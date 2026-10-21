"""Regression tests for the separate primary-source workspace."""
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from backend import sources
from backend.database import init_db, connect
from backend.lexicon import install_lexicon
from backend.maintenance import diagnostics, make_backup, _validate_db


LATIN = b'ref,text\nI.1,"Amicus bonus venit."\nI.2,"Amicus legit."\n'
LATIN_MORPH = (u'ref\tposition\tsurface\tlemma\tmorph\n'
               u'I.1\t1\tAmicus\tamicus\tCase=Nom|Number=Sing\n'
               u'I.1\t2\tbonus\tbonus\tCase=Nom|Number=Sing\n'
               u'I.1\t3\tvenit\tvenio\tVerbForm=Fin\n').encode('utf-8')
TEI = (u'<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader>'
       u'<fileDesc><titleStmt><title>Ignored heading</title></titleStmt></fileDesc></teiHeader>'
       u'<text><body><div n="I"><div subtype="section" n="1">'
       u'<p>ἄνθρωπος καὶ λόγος.</p><p>ἄλλος λόγος.</p>'
       u'</div><div n="2"><p>εἰρήνη.</p></div></div></body></text></TEI>').encode('utf-8')
PTA_ANNOTATED=(u'<TEI><text><body><div n="I">'
 u'<p><w lemma="λόγος" pos="NOUN" msd="Case=Nom">Λόγος</w> '
 u'<w lemma="εἰμί" pos="VERB" msd="Tense=Pres">ἐστίν</w>'
 u'<w pos="PUNCT">.</w></p>'
 u'<p>ἄλλος <w lemma="λόγος" pos="NOUN">λόγος</w>.</p>'
 u'</div></body></text></TEI>').encode('utf-8')


class SourceImportTests(unittest.TestCase):
    def test_parses_three_standard_formats(self):
        self.assertEqual(sources.read_source(LATIN)[0][0], 'I.1')
        self.assertEqual(sources.read_source(json.dumps({'sections':[
            {'ref':'1.1','text':'שלום עולם'}]}).encode())[0][0], '1.1')
        data = sources.read_source(TEI)
        self.assertEqual([r[0] for r in data], ['I.1','I.1.2','I.2'])
        self.assertNotIn('Ignored heading', data[0][2])

    def test_rejects_duplicates_and_dtd(self):
        with self.assertRaises(ValueError):
            sources.read_source(b'ref,text\nA,foo\nA,bar\n')
        with self.assertRaises(ValueError):
            sources.read_source(b'<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><TEI/>')

    def test_sefaria_requires_explicit_permissive_license(self):
        data = {'versions':[{'language':'he','license':'Public Domain','versionTitle':'Torat Emet',
            'text':['שלום','עולם']}]}
        rows,license_name,edition=sources._sefaria_sections(json.dumps(data).encode())
        self.assertEqual((len(rows),license_name,edition), (2,'Public Domain','Torat Emet'))
        data['versions'][0]['license']='All rights reserved'
        with self.assertRaises(ValueError):
            sources._sefaria_sections(json.dumps(data).encode())

    def test_lexicon_tei_parser(self):
        entries=''.join('<entryFree key="lat%d"><def>meaning%d</def></entryFree>'%(i,i) for i in range(101))
        parsed=sources._parse_large_lexicon(('<TEI>'+entries+'</TEI>').encode())
        self.assertEqual(len(parsed),101)
        self.assertEqual(parsed[0][0],'lat0')

    def test_hebrew_tokenization_preserves_diacritics(self):
        words=sources._word_rows('x','1','שָׁלוֹם עוֹלָם')
        self.assertEqual([w[3] for w in words],['שָׁלוֹם','עוֹלָם'])

    def test_conllu_parses_lemmas_and_refuses_misaligned_tokens(self):
        data=(u'# sent_id = test-1\n# text = Amicus venit.\n'
              u'1\tAmicus\tamicus\tNOUN\t_\tCase=Nom|Number=Sing\t0\troot\t_\t_\n'
              u'2\tvenit\tvenio\tVERB\t_\tTense=Pres\t1\tdep\t_\tSpaceAfter=No\n'
              u'3\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_\n\n'
              u'# sent_id = test-2\n# text = Alius erat.\n'
              u'1\tDifferens\talius\tADJ\t_\tCase=Nom\t0\troot\t_\t_\n'
              u'2\terat\tsum\tVERB\t_\tTense=Past\t1\tdep\t_\tSpaceAfter=No\n'
              u'3\t.\t.\tPUNCT\t_\t_\t1\tpunct\t_\t_\n').encode('utf-8')
        rows,annotations,skipped=sources.read_conllu(data)
        self.assertEqual(len(rows),2)
        self.assertEqual(skipped,1)
        self.assertEqual(annotations['test-1'][0][0],'amicus')
        self.assertIn('Case=Nom',annotations['test-1'][0][1])
        self.assertNotIn('test-2',annotations)

    def test_pta_analyzed_tei_preserves_only_exact_word_matches(self):
        rows,annotations,skipped=sources.read_tei_annotated(PTA_ANNOTATED)
        self.assertEqual(len(rows),2)
        self.assertEqual(skipped,1)
        self.assertEqual([x[0] for x in annotations['I']],['λόγος','εἰμί'])
        self.assertIn('Case=Nom',annotations['I'][0][1])
        self.assertNotIn('I.2',annotations)

    def test_conllu_allows_explicit_lila_lemma_link_column(self):
        raw=(u'# sent_id = c-1\n# text = Amicus venit.\n'
            u'1\tAmicus\tamicus\tNOUN\t_\tCase=Nom\t0\troot\t_\t_\thttp://lila-erc.eu/data/id/lemma/123\t\n'
            u'2\tvenit\tvenio\tVERB\t_\tTense=Pres\t1\tdep\t_\tSpaceAfter=No\n'
            u'3\t.\t.\tPUNCT\t_\t_\t1\tpunct\t_\t_\n').encode()
        rows,annotations,skipped=sources.read_conllu(raw)
        self.assertEqual((len(rows),skipped),(1,0))
        self.assertEqual(annotations['c-1'][0][0],'amicus')

    def test_pta_json_dictionary_strips_html(self):
        rows=[{'w':f'λόγος{i}','d':f'<b>meaning {i}</b> &amp; note'} for i in range(120)]
        result=sources._parse_pta_json_lexicon(json.dumps(rows).encode())
        self.assertEqual(len(result),120)
        self.assertEqual(result[0][4],'meaning 0 & note')
        self.assertNotIn('<b>',result[0][4])


class SourceDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='amicus-source-test-')
        self.old = os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR'] = self.temp.name
        init_db()
        sources.install_source('latin-01','Testquelle','Testautor','la','Edition 1900',
            'CC BY 4.0','lokaler Test','1',sources.read_source(LATIN))

    def tearDown(self):
        if self.old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.old
        self.temp.cleanup()

    def test_word_click_search_stats_and_notes(self):
        result=sources.passage('latin-01','I.1')
        self.assertEqual(result['tokens'][0]['surface'],'Amicus')
        self.assertEqual(result['next'],'I.2')
        self.assertEqual(sources.search_sources('amicus',module_id='latin-01')['total'],2)
        self.assertEqual(sources.stats('latin-01')['tokens'],5)
        self.assertEqual(sources.word_analysis('latin-01','I.1',1)['has_annotation'],False)
        self.assertEqual(sources.save_note('latin-01','I.1','Meine Übersetzung')['content'],'Meine Übersetzung')
        self.assertEqual(sources.get_note('latin-01','I.1')['content'],'Meine Übersetzung')
        self.assertEqual(sources.save_note('latin-01','I.1','')['content'],'')

    def test_annotation_import_is_atomic_and_feeds_lexicon(self):
        modified=LATIN_MORPH.replace(b'bonus\tbonus',b'wrong\tbonus')
        with self.assertRaises(ValueError):sources.import_annotations('latin-01',modified)
        self.assertEqual(sources.stats('latin-01')['annotated'],0)
        self.assertEqual(sources.import_annotations('latin-01',LATIN_MORPH)['tokens'],3)
        self.assertEqual(sources.search_sources(module_id='latin-01',lemma='amicus')['total'],1)
        self.assertEqual(sources.stats('latin-01','amicus')['forms'][0]['count'],1)
        install_lexicon('lex-test','Latein-Testlexikon','la','CC0','lokaler Test','1',
            [('amicus','amicus','','friend','Friend (test entry)','test')])
        word=sources.word_analysis('latin-01','I.1',1)
        self.assertEqual(word['lemma'],'amicus')
        self.assertIn('Case=Nom',word['grammar'])
        self.assertEqual(word['lexica'][0]['title'],'Latein-Testlexikon')

    def test_unannotated_word_offers_corpus_based_candidate_not_claimed_as_verified(self):
        sources.install_source('latin-02','Vergleichstext','Testautor','la',
            'Edition 1900','CC0','lokal','1',
            sources.read_source(b'ref,text\nI.1,"Amicus ambulat."\n'))
        self.assertEqual(sources.import_annotations('latin-02',
            b'ref,position,surface,lemma,morph\nI.1,1,Amicus,amicus,Case=Nom\n'
            b'I.1,2,ambulat,ambulo,Tense=Pres\n')['tokens'],2)
        word=sources.word_analysis('latin-01','I.1',1)
        self.assertFalse(word['has_annotation'])
        self.assertEqual(word['annotation_quality'],'unannotated')
        self.assertEqual(word['candidate_analyses'][0]['lemma'],'amicus')
        self.assertIn('keine wortbezogenen',word['grammar'])

    def test_source_tables_are_isolated_and_backup_includes_them(self):
        with connect() as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM verses').fetchone()[0],0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM source_sections').fetchone()[0],2)
        report=diagnostics()
        self.assertTrue(report['database_ok'])
        self.assertEqual(report['counts']['quellenabschnitte'],2)
        path=make_backup()
        self.assertTrue(path.is_file())
        self.assertTrue(sources.remove_source('latin-01'))
        self.assertEqual(sources.modules(),[])
        self.assertEqual(sources.search_sources('amicus')['total'],0)

    def test_known_catalog_import_without_network(self):
        with patch('backend.sources.fetch_catalog_data',return_value=TEI):
            result=sources.install_catalog('quellen-platon')
        self.assertEqual(result['sections'],3)
        self.assertEqual(sources.passage('quellen-platon','I.1')['tokens'][0]['surface'],'ἄνθρωπος')

    def test_catalog_has_four_categories_and_word_corpus(self):
        entries=sources.catalog_list()
        self.assertEqual({x['category'] for x in entries},
                         {'quellen','lexika','sprachen','hilfsmittel'})
        self.assertTrue(all(x['external_url'].startswith('https://')
             for x in entries if x['kind']=='reference'))
        self.assertTrue(any(x['id']=='quellen-confessiones-annotiert' for x in entries))
        self.assertTrue(any(x['id']=='quellen-severian-annotiert' for x in entries))
        data=(u'# sent_id = latin-s1\n# text = Amicus venit.\n'
              u'1\tAmicus\tamicus\tNOUN\t_\tCase=Nom\t0\troot\t_\t_\n'
              u'2\tvenit\tvenio\tVERB\t_\tTense=Pres\t1\tdep\t_\tSpaceAfter=No\n'
              u'3\t.\t.\tPUNCT\t_\t_\t2\tpunct\t_\t_\n').encode()
        with patch('backend.sources.fetch_catalog_data',return_value=data):
            result=sources.install_catalog('quellen-ittb')
        self.assertEqual(result['annotated_sections'],1)
        self.assertEqual(sources.word_analysis('quellen-ittb','latin-s1',1)['lemma'],'amicus')


if __name__ == '__main__':
    unittest.main()
