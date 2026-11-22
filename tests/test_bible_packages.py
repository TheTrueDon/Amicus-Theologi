import hashlib
import io
import json
import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from backend.bible_packages import inspect_bible_package, install_bible_package
from backend.database import init_db
from backend.library import chapter_view
from backend.morphology import get_word


def fixture_package():
    files = {
        'text.csv': 'book,chapter,verse,text\nGen,1,1,ἐν\n'.encode(),
        'parallel.csv': b'book,chapter,verse,text\nGen,1,1,In the beginning\n',
        'words.tsv': 'book\tchapter\tverse\tposition\tsurface\tlemma\tmorph\tstrong\nGen\t1\t1\t1\tἐν\tἐν\tADP\tG1722\n'.encode(),
    }
    manifest = {
        'format': 'amicus-bible-package', 'format_version': 1,
        'editions': [
            {'id':'test-lxx','title':'Test-LXX','language':'grc','license':'CC0',
             'provenance':'Test','version':'1','text_file':'text.csv'},
            {'id':'test-en','title':'Test English','language':'en','license':'CC0',
             'provenance':'Test','version':'1','text_file':'parallel.csv'}],
        'annotations_file':'words.tsv','annotation_chunks':['words.tsv'],
        'checksums': {name:'sha256:'+hashlib.sha256(data).hexdigest() for name,data in files.items()}}
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifest.json',json.dumps(manifest))
        for name,data in files.items():archive.writestr(name,data)
    return out.getvalue()


class BiblePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='amicus-bible-package-test-')
        self.previous=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.temp.name
        init_db()

    def tearDown(self):
        if self.previous is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
        else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=self.previous
        self.temp.cleanup()

    def test_installation_is_atomic_and_idempotent(self):
        raw=fixture_package()
        result=install_bible_package(raw)
        self.assertEqual(result['installed'],2)
        self.assertEqual(result['tokens'],1)
        self.assertEqual(chapter_view('Gen',1,chosen=['test-lxx'])[0]['verses'][0]['text'],'ἐν')
        self.assertEqual(get_word('test-lxx','Gen',1,1,1)['lemma'],'ἐν')
        skipped=install_bible_package(raw)
        self.assertEqual(skipped['skipped'],2)

    def test_bundled_lxx_is_complete_and_word_aligned(self):
        path=Path(__file__).resolve().parents[1]/'bible_packages'/'amicus-lxx-rahlfs.amicus-bible'
        manifest,editions,verses,tokens=inspect_bible_package(path.read_bytes())
        self.assertEqual([edition['id'] for edition in editions],['lxx-rahlfs-os','brenton-lxx-en'])
        self.assertEqual(len(verses['lxx-rahlfs-os']),28279)
        self.assertEqual(len(verses['brenton-lxx-en']),23700)
        self.assertEqual(len(tokens),28279)
        self.assertEqual(sum(map(len,tokens.values())),573039)


if __name__=='__main__':unittest.main()
