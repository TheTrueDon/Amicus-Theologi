"""Smoke checks for the version 0.9 keyboard UX and retained API."""
from pathlib import Path
import os
import tempfile
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db

ROOT=Path(__file__).resolve().parent.parent

def test_command_palette_shipped():
    html=(ROOT/'frontend/index.html').read_text(encoding='utf-8')
    js=(ROOT/'frontend/workflow.js').read_text(encoding='utf-8')
    assert '<title>Amicus Theologi</title>' in html
    assert 'id="command-dialog"' in html
    assert 'id="palette-button"' in html
    assert 'id="recent-references"' in html
    assert '/assets/workflow.js' in html
    for shortcut in ['Ctrl','ArrowLeft','ArrowRight','ArrowDown','F1','Alt']:
        assert shortcut in js
    assert 'localStorage.setItem' in js

def test_frontend_routes_and_schema_unchanged():
    with tempfile.TemporaryDirectory() as d:
        old=os.environ.get('AMICUS_THEOLOGI_DATA_DIR')
        os.environ['AMICUS_THEOLOGI_DATA_DIR']=d
        try:
            init_db()
            with TestClient(app) as client:
                assert client.get('/api/status').json()['version']=='1.0.8'
                page=client.get('/')
                assert page.status_code==200
                assert '<title>Amicus Theologi</title>' in page.text
                assert client.get('/assets/workflow.js').status_code==200
                assert client.get('/api/projects').status_code==200
        finally:
            if old is None:os.environ.pop('AMICUS_THEOLOGI_DATA_DIR',None)
            else:os.environ['AMICUS_THEOLOGI_DATA_DIR']=old
