import os
import tempfile
import unittest
from pathlib import Path

class SearchTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory()
  self.old=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
  os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.t.name
  from backend.database import init_db
  from backend.library import install_module
  init_db()
  install_module('test-de','Testausgabe','de','Test','Eigene Testdaten','1',[
   ('Joh',1,1,'Im Anfang war das Wort und das Wort war bei Gott.'),
   ('Joh',1,2,'Dasselbe war im Anfang bei Gott.'),
   ('Gen',1,1,'Am Anfang schuf Gott Himmel und Erde.')])
 def tearDown(self):
  if self.old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
  else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.old
  self.t.cleanup()
 def test_all(self):
  from backend.search import search_verses
  self.assertEqual(search_verses('Anfang Gott')['total'],3)
 def test_phrase(self):
  from backend.search import search_verses
  self.assertEqual(search_verses('=im Anfang')['total'],2)
 def test_any(self):
  from backend.search import search_verses
  self.assertEqual(search_verses('?Erde Wort')['total'],2)
 def test_prefix(self):
  from backend.search import search_verses
  self.assertEqual(search_verses('Anfan*')['total'],3)
 def test_filter(self):
  from backend.search import search_verses
  self.assertEqual(search_verses('Gott',book='Gen')['total'],1)
 def test_delete(self):
  from backend.database import connect
  from backend.search import search_verses
  with connect() as db:db.execute('DELETE FROM modules WHERE id=?',('test-de',))
  self.assertEqual(search_verses('Gott')['total'],0)
 def test_legacy_rebuild(self):
  from backend.database import connect,init_db
  from backend.search import search_verses
  with connect() as db:
   db.execute("DELETE FROM settings WHERE key='fts_schema_version'")
   db.execute("INSERT INTO verse_fts(verse_fts) VALUES('delete-all')")
  init_db()
  self.assertEqual(search_verses('Anfang')['total'],3)
 def test_injection(self):
  from backend.search import search_verses
  self.assertEqual(search_verses('Gott OR Erde')['total'],0)

if __name__=='__main__':unittest.main()
