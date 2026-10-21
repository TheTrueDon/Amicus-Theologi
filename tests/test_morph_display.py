import unittest

from backend.morph_display import decode


class MorphDisplayTests(unittest.TestCase):
    def test_open_greek_corpus_agdt_code_is_readable(self):
        result = decode('v1saoa---', 'grc')
        self.assertTrue(result['recognized'])
        self.assertEqual(result['scheme'], 'AGDT/Perseus positional morphology')
        self.assertIn({'name': 'Tempus', 'value': 'Aorist'}, result['features'])

    def test_ud_features_are_readable_for_latin_and_greek(self):
        for language in ('la', 'grc'):
            result = decode('NOUN|Case=Gen|Gender=Fem|Number=Sing', language)
            self.assertTrue(result['recognized'])
            self.assertIn({'name': 'Kasus', 'value': 'Genitiv'}, result['features'])

    def test_unknown_tag_is_explicitly_marked(self):
        result = decode('X', 'la')
        self.assertTrue(result['recognized'])
        self.assertEqual(result['features'][0]['value'], 'nicht bestimmbar')

    def test_oshb_pronoun_placeholder_keeps_gender_and_number(self):
        result=decode('HPdxcp','he')
        self.assertTrue(result['recognized'])
        self.assertIn({'name':'Genus','value':'Gemeinsames Genus'},result['features'])
        self.assertIn({'name':'Numerus','value':'Plural'},result['features'])

    def test_oshb_extended_verb_stems_decode(self):
        result=decode('HVvj3mp','he')
        self.assertTrue(result['recognized'])
        self.assertIn({'name':'Stamm','value':'Hishtaphel'},result['features'])
        self.assertIn({'name':'Form','value':'Jussiv'},result['features'])


if __name__ == '__main__':
    unittest.main()
