"""What scripts/build_site.py writes to site/, checked without a browser."""
import hashlib
import json
import re

from rdflib import Graph
from rdflib.namespace import SKOS

DATA_FILES = ["explorer-data.json", "explorer-turtle.json"]


def test_the_page_holds_no_taxonomy_data(site, taxonomy):
    html = (site / "index.html").read_text(encoding="utf-8")
    inside = [code for code, c in taxonomy.items() if c["definition"] in html]
    assert inside == []


def test_the_data_file_holds_every_concept_with_what_the_page_shows(site, taxonomy):
    data = json.loads((site / "explorer-data.json").read_text(encoding="utf-8"))
    rows = {r[0]: r for r in data["c"]}
    assert set(rows) == set(taxonomy)
    for code, c in taxonomy.items():
        assert (rows[code][1], rows[code][2], rows[code][3], rows[code][4]) == (c["parent"], c["label"], c["label_gb"], c["definition"])
    assert set(data) >= {"version", "built", "repo", "m", "r", "v", "tags"}


def test_the_turtle_file_holds_each_concepts_turtle_and_the_shapes(site, taxonomy, shapes):
    turtle = json.loads((site / "explorer-turtle.json").read_text(encoding="utf-8"))
    assert set(turtle["ttl"]) == set(taxonomy)
    for code, c in taxonomy.items():
        assert f"aeco:{code} " in turtle["ttl"][code]
        assert f'"{c["label"]}"@en-US' in turtle["ttl"][code]
    assert turtle["shapes"] == shapes


def test_the_page_asks_for_each_data_file_by_a_hash_of_its_content(site):
    html = (site / "index.html").read_text(encoding="utf-8")
    for name in DATA_FILES:
        found = re.findall(re.escape(name) + r"\?v=([0-9a-f]+)", html)
        assert len(found) == 1, name
        assert len(found[0]) >= 8
        assert hashlib.sha256((site / name).read_bytes()).hexdigest().startswith(found[0]), name


def test_the_downloads_are_still_written(site, taxonomy):
    core = Graph().parse(site / "aeco.ttl", format="turtle")
    assert {str(o) for o in core.objects(None, SKOS.notation)} >= set(taxonomy)
    assert len(Graph().parse(site / "aeco.jsonld", format="json-ld")) == len(core)
    assert len(Graph().parse(site / "aeco-mappings.ttl", format="turtle")) > 0
