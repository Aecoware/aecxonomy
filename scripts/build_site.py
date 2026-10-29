#!/usr/bin/env python3
"""Build the explorer and the merged data files of the Aecoware Open Taxonomy.

  python3 scripts/build_site.py

Reads src/, scripts/shapes.ttl and site/template.html. Writes to site/:

  index.html          the explorer: one page with the data inside
  aeco.ttl            the core taxonomy in one Turtle file: the scheme, the concepts,
                      the 5W1H tags, the standard sets and the related links
  aeco.jsonld         the same core taxonomy in JSON-LD
  aeco-mappings.ttl   every link to an outside standard, in one Turtle file

Needs Python 3.9+, rdflib and pyshacl.
"""
import csv
import datetime as dt
import json
import pathlib
import re
import sys

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SKOS, XSD

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import taxo  # noqa: E402

ROOT = taxo.ROOT
SRC = taxo.SRC
SITE = ROOT / "site"
CORE = ["aeco-base.ttl", "tags.ttl", "standard-sets.ttl", "related.ttl"]
LICENSE_IRI = "https://creativecommons.org/licenses/by/4.0/"
OUT_PREFIX = {"ifc": "ifc", "wikidata": "wd", "uniclass": "uc", "brick": "brick", "rec": "rec", "bot": "bot", "aat": "aat"}
BY_NAME = [("iso", "mappings-iso-12006-2.tsv", "iso_12006_2_class"), ("riba", "mappings-riba-plan-of-work.tsv", "riba_stage")]
SH = Namespace("http://www.w3.org/ns/shacl#")
RULE = {  # rule findings from taxo.check: (path, component) for the explorer's validation report
    "en-GB": ("skos:prefLabel", "EnGbLabel"),
    "Length": ("skos:definition", "SentenceLength"),
    "Depth": ("skos:broader", "DepthLimit"),
    "Children": ("skos:narrower", "ChildCount"),
    "Label": ("skos:prefLabel", "UniqueLabel"),
    "Shared label": ("skos:altLabel", "SharedLabel"),
    "Ambiguous label": ("skos:hiddenLabel", "AmbiguousLabel"),
    "Related": ("skos:related", "RelatedLink"),
    "Mapping": ("skos:mappingRelation", "MappingRule"),
    "Deprecated": ("dct:isReplacedBy", "Deprecated"),
}


def citation(key, default=""):
    for line in (ROOT / "CITATION.cff").read_text(encoding="utf-8").splitlines():
        m = re.match(rf'{key}:\s*"?([^"]*)"?\s*$', line)
        if m:
            return m.group(1).strip()
    return default


def bind(g):
    for prefix, ns in (("aeco", taxo.NS), ("skos", SKOS), ("dct", DCTERMS), ("owl", OWL), ("rdfs", RDFS), ("xsd", XSD)):
        g.bind(prefix, ns, override=True, replace=True)
    for src, (_, _, ns) in taxo.MAP_SOURCES.items():
        g.bind(OUT_PREFIX.get(src, src), ns, override=True, replace=True)
    return g


def core_graph():
    g = Graph()
    for name in CORE:
        g.parse(SRC / name, format="turtle")
    for p in sorted((SRC / "branches").glob("*.ttl")):
        g.parse(p, format="turtle")
    return bind(g)


def write_exports(version):
    g = core_graph()
    base = URIRef(taxo.NS + "base")
    g.add((base, OWL.versionInfo, Literal(version)))
    g.add((base, DCTERMS.license, URIRef(LICENSE_IRI)))
    g.serialize(destination=str(SITE / "aeco.ttl"), format="turtle")
    context = {"aeco": taxo.NS, "skos": str(SKOS), "dct": str(DCTERMS), "owl": str(OWL), "rdfs": str(RDFS), "xsd": str(XSD)}
    g.serialize(destination=str(SITE / "aeco.jsonld"), format="json-ld", context=context, indent=1)
    m = Graph()
    for p in sorted(SRC.glob("mappings-*.ttl")):
        m.parse(p, format="turtle")
    bind(m).serialize(destination=str(SITE / "aeco-mappings.ttl"), format="turtle")
    return len(g), len(m)


def read_mappings():
    out = {}
    for src in taxo.MAP_SOURCES:
        for r in taxo.read_mappings(src):
            label = r.get("target_label", "") if src == "wikidata" else ""  # Wikidata labels are CC0; no other titles ship
            out.setdefault(r["code"], []).append([src, r["relation"], r["target"], label])
    for src, name, col in BY_NAME:
        path = SRC / name
        if not path.exists():
            continue
        with open(path, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader((l for l in fh if not l.startswith("#")), delimiter="\t"):
                rel = {"broader": "broad", "narrower": "narrow"}.get(r["relation"], r["relation"])
                out.setdefault(r["code"], []).append([src, rel, r[col], ""])
    return out


def concept_ttl(c, maps, related):
    lines = []
    for src, rel, target, _ in maps.get(c["code"], []):
        if src not in taxo.MAP_SOURCES:
            continue
        local = target if re.fullmatch(r"[A-Za-z_][\w-]*", target) else None
        obj = f"{OUT_PREFIX[src]}:{local}" if local else f"<{taxo.MAP_SOURCES[src][2]}{target}>"
        lines.append(f"aeco:{c['code']} {taxo.MAP_REL[rel]} {obj} .")
    for other in related.get(c["code"], []):
        lines.append(f"aeco:{c['code']} skos:related aeco:{other} .")
    return taxo.block(c) + ("\n\n" + "\n".join(lines) if lines else "")


def findings():
    from pyshacl import validate
    g = bind(taxo.graph())
    shapes = Graph().parse(ROOT / "scripts" / "shapes.ttl", format="turtle")
    _, rg, _ = validate(g, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    out = {}
    for r in rg.subjects(RDF.type, SH.ValidationResult):
        node = str(rg.value(r, SH.focusNode)).replace(taxo.NS, "")
        sev = str(rg.value(r, SH.resultSeverity)).rsplit("#", 1)[-1]
        path = rg.value(r, SH.resultPath)
        comp = str(rg.value(r, SH.sourceConstraintComponent) or "").rsplit("#", 1)[-1]
        out.setdefault(node, []).append(["shacl", sev, str(rg.value(r, SH.resultMessage) or ""),
                                         g.namespace_manager.normalizeUri(path) if isinstance(path, URIRef) else "", comp])
    for sev, node, kind, msg in taxo.check(verbose=False, all_findings=True):
        if kind == "Shape":
            continue
        path, comp = RULE.get(kind, ("", kind.replace(" ", "")))
        for code in sorted(set(re.findall(r"aeco-\d{5}", node))):
            out.setdefault(code, []).append(["rule", "Violation" if sev == "BLOCK" else "Warning", msg, path, comp])
    return out


def explorer_data(version, repo):
    cs = {k: c for k, c in taxo.load().items() if not c["deprecated"]}
    maps = read_mappings()
    pairs = [[r["code_a"], r["code_b"]] for r in taxo.read_related()]
    related = {}
    for a, b in pairs:
        related.setdefault(a, []).append(b)
        related.setdefault(b, []).append(a)
    tags = Graph().parse(SRC / "tags.ttl", format="turtle")
    tag_defs = {t: str(tags.value(URIRef(taxo.NS + taxo.tag_iri(t)), SKOS.definition) or "") for t in taxo.TAGS}
    rows = []
    for code in sorted(cs):
        c = cs[code]
        rows.append([code, c["parent"], c["label_en_us"], c["label_en_gb"], c["definition"], "|".join(c["alt_en_us"]),
                     "|".join(c["alt_en_gb"]), "|".join(c["hidden"]), "|".join(c["tags"]), c["scope_note"], "|".join(c["std"]),
                     c["created"], c["modified"]])
    return {
        "version": version,
        "built": dt.date.today().isoformat(),
        "repo": repo,
        "c": rows,
        "m": {k: v for k, v in maps.items() if k in cs},
        "r": pairs,
        "ttl": {code: concept_ttl(cs[code], maps, related) for code in cs},
        "v": findings(),
        "shapes": (ROOT / "scripts" / "shapes.ttl").read_text(encoding="utf-8"),
        "tags": tag_defs,
    }


def main():
    blocking = taxo.check(verbose=False)
    if blocking:
        print(f"{len(blocking)} blocking findings. Run scripts/taxo.py check and fix them first.")
        return 1
    SITE.mkdir(exist_ok=True)
    version = citation("version", "0.0.0")
    repo = citation("repository-code", "")
    core, links = write_exports(version)
    data = explorer_data(version, repo)
    template = (SITE / "template.html").read_text(encoding="utf-8")
    if template.count("/*DATA*/null") != 1:
        print("site/template.html must hold the marker /*DATA*/null exactly once.")
        return 1
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    (SITE / "index.html").write_text(template.replace("/*DATA*/null", payload), encoding="utf-8")
    print(f"site/index.html: {len(data['c'])} concepts, version {version}.")
    print(f"site/aeco.ttl and site/aeco.jsonld: {core} triples. site/aeco-mappings.ttl: {links} triples.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
