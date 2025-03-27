import sys
import os
import pytest

# Přidáme root složku projektu do sys.path, aby fungoval import
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scraper import run_scraper

def test_run_scraper_monkeypatch(monkeypatch):
    # Mock hlavičky výsledků
    class DummyHeader:
        def evaluate(self, js):
            return "https://example.com"
        def inner_text(self):
            return "Example Title"

    # Mock myši
    class DummyMouse:
        def move(self, x, y): pass
        def wheel(self, dx, dy): pass

    # Mock celé stránky
    class DummyPage:
        def goto(self, url, timeout): pass
        def get_by_role(self, role, name): return self
        def click(self, timeout): pass
        @property
        def mouse(self): return DummyMouse()
        def wait_for_selector(self, selector, timeout): pass
        def locator(self, selector): return self
        def all(self): return [DummyHeader()]

    # Mock kontextu a prohlížeče
    class DummyContext:
        def new_page(self): return DummyPage()

    class DummyBrowser:
        def new_context(self, **kwargs): return DummyContext()
        def close(self): pass

    # Mock samotného Playwrightu
    class DummyPlaywright:
        @property
        def chromium(self):
            class Chromium:
                def launch(self, **kwargs): return DummyBrowser()
            return Chromium()
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass

    # Nahrazení Playwrightu v scraper.py
    monkeypatch.setattr("scraper.sync_playwright", lambda: DummyPlaywright())

    # Volání testované funkce
    results = run_scraper("test query")

    # Kontrola výstupu
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["title"] == "Example Title"
    assert results[0]["link"] == "https://example.com"