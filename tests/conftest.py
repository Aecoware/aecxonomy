"""Shared fixtures for the explorer tests.

The site is built once per test run, served from a local port, and opened in
headless Chromium at a desktop size and a phone size. Expected values come
from the Turtle in src/, read here with rdflib, not from the build's output.
"""
import functools
import http.server
import pathlib
import subprocess
import sys
import threading

import pytest
from playwright.sync_api import sync_playwright
from rdflib import Graph, Namespace
from rdflib.namespace import OWL, SKOS

ROOT = pathlib.Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
AECO = Namespace("https://w3id.org/aeco/")

SIZES = {
    "desktop": {"viewport": {"width": 1366, "height": 860}},
    "phone": {"viewport": {"width": 375, "height": 812}, "is_mobile": True, "has_touch": True, "device_scale_factor": 3},
}


@pytest.fixture(scope="session")
def shapes():
    """The SHACL shapes, as the repo keeps them."""
    return (ROOT / "scripts" / "shapes.ttl").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def taxonomy():
    """Every concept that is not deprecated, read straight from the Turtle in src/."""
    g = Graph()
    for p in sorted((ROOT / "src").glob("*.ttl")) + sorted((ROOT / "src" / "branches").glob("*.ttl")):
        g.parse(p, format="turtle")
    out = {}
    for s in g.subjects(SKOS.inScheme, AECO.base):
        if g.value(s, OWL.deprecated) or g.value(s, SKOS.notation) is None:
            continue
        labels = {l.language: str(l) for l in g.objects(s, SKOS.prefLabel)}
        parent = g.value(s, SKOS.broader)
        out[str(g.value(s, SKOS.notation))] = {
            "label": labels.get("en-US", ""),
            "label_gb": labels.get("en-GB", ""),
            "definition": str(g.value(s, SKOS.definition) or ""),
            "parent": str(parent).rsplit("/", 1)[1] if parent else "",
            "shared": (s, AECO.appliesUnder, AECO["std-shared"]) in g,
        }
    return out


@pytest.fixture(scope="session")
def site():
    """Build the site once, the way CI and contributors do."""
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_site.py")], cwd=ROOT, check=True,
                   stdout=subprocess.DEVNULL)
    return SITE


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def base_url(site):
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}/"
    server.shutdown()


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture(params=list(SIZES))
def page(request, browser, base_url):
    """A fresh browser page at the desktop size and again at the phone size."""
    context = browser.new_context(base_url=base_url, **SIZES[request.param])
    pg = context.new_page()
    yield pg
    context.close()
