import io,zipfile,unittest,os,tempfile
from backend.source_import import parse_oshb,parse_step,safe_archive,install_scientific
from backend.database import init_db,connect

def archive(files):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w') as z:
  for name,data in files.items():z.writestr(name,data)
 return b.getvalue()

class SourceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name;init_db()
 def tearDown(self):
  self.temp.cleanup();os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
 def test_oshb_import(self):
  raw=archive({'morphhb-master/wlc/Gen.xml':'<osis xmlns="http://www.bibletechnologies.net/2003/OSIS/namespace"><verse osisID="Gen.1.1"><w lemma="7225" morph="HNcfsa">בְּרֵאשִׁית</w><w lemma="1254" morph="HVqp3ms">בָּרָא</w></verse></osis>'})
  result=install_scientific('oshb',raw)
  self.assertEqual((result['verses'],result['tokens']),(1,2))
  with connect() as c:self.assertEqual(c.execute('SELECT count(*) FROM tokens').fetchone()[0],2)
  with self.assertRaises(ValueError):install_scientific('oshb',raw)
 def test_step_greek_edition_selection(self):
  data='Mat.1.1#01=NKO\tλόγος (logos)\tword\tG3056=N-NSM\tλόγος=word\tSBL+TR\nMat.1.1#02=NKO\tθεός (theos)\tGod\tG2316=N-NSM\tθεός=God\tTR\n'
  raw=archive({'STEPBible-Data-master/Translators Amalgamated OT+NT/TAGNT-example.txt':data})
  verses,tokens,lang=parse_step(raw,'tagnt')
  self.assertEqual(lang,'grc');self.assertEqual(len(tokens),1)
  self.assertEqual(list(verses.values()),['λόγος'])
 def test_zip_limits(self):
  with self.assertRaises(ValueError):safe_archive(b'not zip')

class StepArchiveLimitRegression(unittest.TestCase):
 def test_large_unrelated_members_do_not_block_tagnt(self):
  example='Mat.1.1#01=NKO\tλόγος (logos)\tword\tG3056=N-NSM\tλόγος=word\tSBL+TR\n'
  files={f'STEPBible-Data-master/Lexicons/filler{i}.txt':'a' for i in range(2600)}
  files['STEPBible-Data-master/Translators Amalgamated OT+NT/TAGNT-main.txt']=example
  verses,tokens,lang=parse_step(archive(files),'tagnt')
  self.assertEqual(len(tokens),1)
  self.assertEqual(lang,'grc')
 def test_huge_relevant_entry_still_rejected(self):
  # Check refusal using ZIP's own declared size, without creating a huge test file.
  import unittest.mock as mock
  sample=archive({'STEPBible-Data-master/TAGNT-main.txt':'x'})
  with mock.patch('backend.source_import.MAX_STEP_FILE',0):
   with self.assertRaisesRegex(ValueError,'Sicherheitsgrenze'):
    parse_step(sample,'tagnt')
