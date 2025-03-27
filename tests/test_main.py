import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from main import app
import subprocess
import json

client = TestClient(app)

def test_root_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Vyhledávač" in response.text

def test_search_success(monkeypatch):
    def dummy_run(*args, **kwargs):
        class DummyResult:
            returncode = 0
            stdout = json.dumps([{"title": "Mock title", "link": "https://example.com"}])
            stderr = ""
        return DummyResult()
    
    monkeypatch.setattr(subprocess, "run", dummy_run)

    response = client.get("/search?query=test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["title"] == "Mock title"
    assert data[0]["link"] == "https://example.com"