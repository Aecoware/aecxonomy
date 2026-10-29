#!/usr/bin/env python3
"""Tools for the Aecoware Open Taxonomy.

Turtle in src/ is the source of truth. Run every command from the repository root.
Needs Python 3.9+, rdflib and pyshacl.

  python3 scripts/taxo.py check
      Runs the SHACL shapes in scripts/shapes.ttl, plus the checks SHACL cannot do:
      sentence length, unique labels, depth limits, children per concept, shared labels.
      Exit code 1 when a blocking check fails.

  python3 scripts/build_site.py
      Builds the explorer and the merged data files in site/.

Maintainer commands. They read proposal files that are kept outside the public repository.

  python3 scripts/taxo.py apply PROPOSALS.csv DECISIONS_DIR
      Applies decided proposals. DECISIONS_DIR holds one JSON file per proposal.
      Approved rows get a code (when new) and go into Turtle. Every decided row gets
      its decision, comment and edits in the CSV, and a log entry. Then runs check.

  python3 scripts/taxo.py page PROPOSALS.csv OUT_DIR
      Writes one JSON file per concept for the review tool: accepted concepts from
      Turtle, open proposals and pending revisions from the CSV.

  python3 scripts/taxo.py relate LINKS.tsv L01 L02:3,7 ...
      Adds approved link groups to src/related.tsv and writes src/related.ttl.
      A group ID alone takes every pair. GROUP:3,7 drops pairs 3 and 7. Then runs check.
      Links are symmetric skos:related. They never join a concept to its own ancestor.

  python3 scripts/taxo.py map MAPPINGS.tsv W01 I02:4 ...
      Adds approved mapping groups to src/mappings-<source>.tsv, one file per source,
      and writes src/mappings-<source>.ttl. GROUP:4 drops pair 4. Then runs check.
"""
import csv
import datetime as dt
import json
import pathlib
import re
import sys

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BRANCHES = SRC / "branches"
RELATED = SRC / "related.tsv"
REL_FIELDS = ["code_a", "label_a", "code_b", "label_b", "group", "session", "added"]
MAP_FIELDS = ["code", "label_en_us", "relation", "target", "target_label", "note", "group", "added"]
MAP_REL = {"exact": "skos:exactMatch", "close": "skos:closeMatch", "broad": "skos:broadMatch", "narrow": "skos:narrowMatch"}
MAP_SOURCES = {
    "wikidata": ("Wikidata", "CC0 1.0", "http://www.wikidata.org/entity/"),
    "ifc": ("IFC 4.3, buildingSMART International", "CC BY-ND 4.0. Class identifiers only, no IFC text", "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/"),
    "brick": ("Brick Schema", "BSD-3-Clause", "https://brickschema.org/schema/Brick#"),
    "rec": ("RealEstateCore", "BSD-3-Clause", "https://w3id.org/rec#"),
    "bot": ("Building Topology Ontology, W3C Linked Building Data Community Group", "CC BY 1.0", "https://w3id.org/bot#"),
    "aat": ("Getty Art & Architecture Thesaurus", "ODC-By 1.0", "http://vocab.getty.edu/aat/"),
    "uniclass": ("Uniclass 2015, NBS", "CC BY-ND 4.0. Codes only, no titles, tables not adapted", "https://uniclass.thenbs.com/taxon/"),
}
NS = "https://w3id.org/aeco/"
AECO = Namespace(NS)
BASE = AECO["base"]
TAGS = ["Who", "What", "Where", "When", "Why", "How"]
STD = {"Shared": "std-shared", "AIA": "std-aia", "ConsensusDocs": "std-consensusdocs", "DBIA": "std-dbia",
       "EJCDC": "std-ejcdc", "ICC I-Codes": "std-icc", "NFPA": "std-nfpa", "OSHA 1926": "std-osha1926", "ADA": "std-ada"}
STD_BACK = {v: k for k, v in STD.items()}
CSV_FIELDS = ["temp_id", "code", "parent", "level", "session", "batch", "rev", "label_en_us", "label_en_gb", "definition",
              "alt_labels_en_us", "alt_labels_en_gb", "hidden_labels", "tags", "standard_sets", "scope_note", "iso_term",
              "group", "depth_limit", "change_note", "refs", "decision", "comment", "edits", "decided_at", "applied_rev"]
MAX_WORDS = 25
TODAY = dt.date.today().isoformat()

PREFIXES = """@prefix aeco: <https://w3id.org/aeco/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dct: <http://purl.org/dc/terms/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""


def tag_iri(t):
    return "tag-" + t.lower()


def split_list(s, sep=";"):
    return [x.strip() for x in str(s or "").split(sep) if x.strip()]


def lit(text, lang):
    t = str(text).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    return f'"{t}"@{lang}'


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", str(text or "").strip()) if s.strip()]


# ---------- load and render ----------
def graph():
    g = Graph()
    for p in sorted(SRC.glob("*.ttl")) + sorted(BRANCHES.glob("*.ttl")):
        g.parse(p, format="turtle")
    return g


def load():
    g = graph()
    out = {}
    for s in g.subjects(SKOS.notation, None):
        if (s, SKOS.inScheme, BASE) not in g:
            continue
        code = str(g.value(s, SKOS.notation))
        labels = {l.language: str(l) for l in g.objects(s, SKOS.prefLabel)}
        alts = list(g.objects(s, SKOS.altLabel))
        prim = g.value(s, AECO.primaryTag)
        tags = [str(prim).rsplit("tag-", 1)[1].capitalize()] if prim else []
        for t in sorted(g.objects(s, AECO.tag)):
            name = str(t).rsplit("tag-", 1)[1].capitalize()
            if name not in tags:
                tags.append(name)
        parent = g.value(s, SKOS.broader)
        repl = g.value(s, DCTERMS.isReplacedBy)
        depth = g.value(s, AECO.depthLimit)
        out[code] = {
            "code": code,
            "parent": str(parent).replace(NS, "") if parent else "",
            "label_en_us": labels.get("en-US", ""),
            "label_en_gb": labels.get("en-GB", ""),
            "definition": str(g.value(s, SKOS.definition) or ""),
            "alt_en_us": sorted(str(a) for a in alts if a.language == "en-US"),
            "alt_en_gb": sorted(str(a) for a in alts if a.language == "en-GB"),
            "hidden": sorted(str(h) for h in g.objects(s, SKOS.hiddenLabel)),
            "tags": tags,
            "std": sorted(STD_BACK.get(str(o).replace(NS, ""), str(o)) for o in g.objects(s, AECO.appliesUnder)),
            "scope_note": str(g.value(s, SKOS.scopeNote) or ""),
            "group": str(g.value(s, AECO.group) or ""),
            "depth_limit": int(depth) if depth is not None else None,
            "created": str(g.value(s, DCTERMS.created) or TODAY),
            "modified": str(g.value(s, DCTERMS.modified) or TODAY),
            "deprecated": bool(g.value(s, OWL.deprecated)),
            "replaced_by": str(repl).replace(NS, "") if repl else "",
        }
    return out


def block(c):
    L = [f"aeco:{c['code']} a skos:Concept ;", "    skos:inScheme aeco:base ;"]
    L.append(f"    skos:broader aeco:{c['parent']} ;" if c["parent"] else "    skos:topConceptOf aeco:base ;")
    L.append(f'    skos:notation "{c["code"]}" ;')
    labels = [lit(c["label_en_us"], "en-US")] + ([lit(c["label_en_gb"], "en-GB")] if c["label_en_gb"] else [])
    L.append("    skos:prefLabel " + " , ".join(labels) + " ;")
    alts = [lit(a, "en-US") for a in c["alt_en_us"]] + [lit(a, "en-GB") for a in c["alt_en_gb"]]
    if alts:
        L.append("    skos:altLabel " + " ,\n        ".join(alts) + " ;")
    if c["hidden"]:
        L.append("    skos:hiddenLabel " + " , ".join(lit(h, "en-US") for h in c["hidden"]) + " ;")
    L.append(f"    skos:definition {lit(c['definition'], 'en')} ;")
    if c["scope_note"]:
        L.append(f"    skos:scopeNote {lit(c['scope_note'], 'en')} ;")
    if c["tags"]:
        L.append(f"    aeco:primaryTag aeco:{tag_iri(c['tags'][0])} ;")
        L.append("    aeco:tag " + " , ".join(f"aeco:{tag_iri(t)}" for t in c["tags"]) + " ;")
    if c["std"]:
        L.append("    aeco:appliesUnder " + " , ".join(f"aeco:{STD.get(s, slug(s))}" for s in c["std"]) + " ;")
    if c["group"]:
        L.append(f'    aeco:group "{c["group"]}" ;')
    if c["depth_limit"]:
        L.append(f"    aeco:depthLimit {int(c['depth_limit'])} ;")
    if c["deprecated"]:
        L.append("    owl:deprecated true ;")
        if c["replaced_by"]:
            L.append(f"    dct:isReplacedBy aeco:{c['replaced_by']} ;")
    L.append(f'    dct:created "{c["created"]}"^^xsd:date ;')
    L.append(f'    dct:modified "{c["modified"]}"^^xsd:date .')
    return "\n".join(L)


def descendants(concepts, code):
    kids = sorted(k for k, c in concepts.items() if c["parent"] == code)
    out = []
    for k in kids:
        out.append(k)
        out.extend(descendants(concepts, k))
    return out


def render(concepts):
    BRANCHES.mkdir(parents=True, exist_ok=True)
    tops = sorted(k for k, c in concepts.items() if not c["parent"])
    for t in tops:
        c = concepts[t]
        name = f"{t}-{slug(c['label_en_us'])}.ttl"
        for old in BRANCHES.glob(f"{t}-*.ttl"):
            if old.name != name:
                old.unlink()
        body = [f"# Branch {t}: {c['label_en_us']}", "# Generated by scripts/taxo.py from accepted review decisions. Edit through the review, not by hand.", "", PREFIXES]
        body += [block(concepts[k]) + "\n" for k in [t] + descendants(concepts, t)]
        (BRANCHES / name).write_text("\n".join(body))
    modified = max([c["modified"] for c in concepts.values()] + [TODAY])
    base = [
        "# Aecoware Open Taxonomy: the concept scheme and the vocabulary it uses.",
        "# Top level aligned with the ISO 12006-2 framework. No ISO text is reproduced.",
        "# License: see LICENSE and NOTICE.md. Namespace: https://w3id.org/aeco/",
        "", PREFIXES,
        "aeco:base a skos:ConceptScheme ;",
        '    dct:title "Aecoware Open Taxonomy"@en ;',
        '    dct:description "An open base vocabulary for architecture, engineering, construction and operations. People and agents use it to name, find and link AECO concepts."@en ;',
        '    dct:created "2026-10-24"^^xsd:date ;',
        f'    dct:modified "{modified}"^^xsd:date' + (" ;" if tops else " ."),
    ]
    if tops:
        base.append("    skos:hasTopConcept " + " ,\n        ".join(f"aeco:{t}" for t in tops) + " .")
    base += ["",
             'aeco:primaryTag a owl:ObjectProperty ;\n    rdfs:label "primary 5W1H tag"@en ;\n    rdfs:comment "The first 5W1H tag of a concept. Agents route on it first."@en ;\n    rdfs:range skos:Concept .',
             "",
             'aeco:tag a owl:ObjectProperty ;\n    rdfs:label "5W1H tag"@en ;\n    rdfs:comment "A 5W1H routing tag of a concept. A concept has 1 or 2. The primary tag is one of them."@en ;\n    rdfs:range skos:Concept .',
             "",
             'aeco:appliesUnder a owl:ObjectProperty ;\n    rdfs:label "applies under"@en ;\n    rdfs:comment "The standard set under which a concept applies: Shared, or a named set such as AIA."@en ;\n    rdfs:range skos:Concept .',
             "",
             'aeco:group a owl:DatatypeProperty ;\n    rdfs:label "framework group"@en ;\n    rdfs:comment "For a top branch: Results, Process, Resources or Properties after the ISO 12006-2 framework, or Added for a branch outside it."@en .',
             "",
             'aeco:depthLimit a owl:DatatypeProperty ;\n    rdfs:label "depth limit"@en ;\n    rdfs:comment "For a top branch: the maximum number of levels in the base, the top branch included."@en .',
             ""]
    (SRC / "aeco-base.ttl").write_text("\n".join(base))


# ---------- related links ----------
def read_related():
    if not RELATED.exists():
        return []
    with open(RELATED, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def render_related(rows):
    with open(RELATED, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=REL_FIELDS, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in REL_FIELDS})
    body = ["# Related links between concepts of the Aecoware Open Taxonomy.",
            "# Generated by scripts/taxo.py from src/related.tsv. Each link is written in both directions.",
            "", PREFIXES]
    for r in sorted(rows, key=lambda x: (x["code_a"], x["code_b"])):
        body.append(f"aeco:{r['code_a']} skos:related aeco:{r['code_b']} .  # {r['label_a']} / {r['label_b']}")
        body.append(f"aeco:{r['code_b']} skos:related aeco:{r['code_a']} .")
    (SRC / "related.ttl").write_text("\n".join(body) + "\n")


def relate(tsv_path, specs):
    with open(tsv_path, newline="") as fh:
        props = list(csv.DictReader(fh, delimiter="\t"))
    rows = read_related()
    have = {tuple(sorted((r["code_a"], r["code_b"]))) for r in rows}
    added = 0
    for spec in specs:
        gid, _, drops = spec.partition(":")
        drop = {d.strip() for d in drops.split(",") if d.strip()}
        for p in props:
            if p["group"] != gid or p["n"] in drop:
                continue
            key = tuple(sorted((p["code_a"], p["code_b"])))
            if key in have:
                continue
            have.add(key)
            rows.append({"code_a": p["code_a"], "label_a": p["label_a"], "code_b": p["code_b"], "label_b": p["label_b"],
                         "group": gid, "session": p.get("session", ""), "added": TODAY})
            added += 1
    render_related(rows)
    print(f"{added} links added. {len(rows)} links in total.")
    return check()


def map_path(src):
    return SRC / f"mappings-{src}.tsv"


def read_mappings(src):
    p = map_path(src)
    if not p.exists():
        return []
    with open(p, newline="") as fh:
        return [r for r in csv.DictReader((l for l in fh if not l.startswith("#")), delimiter="\t")]


def render_mappings(src, rows):
    name, lic, ns = MAP_SOURCES[src]
    with open(map_path(src), "w", newline="") as fh:
        fh.write(f"# Mappings from the Aecoware Open Taxonomy to {name}. License of the target: {lic}.\n")
        w = csv.DictWriter(fh, fieldnames=MAP_FIELDS, delimiter="\t")
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in MAP_FIELDS})
    body = [f"# Mappings from the Aecoware Open Taxonomy to {name}.", f"# Target license: {lic}.",
            f"# Generated by scripts/taxo.py from src/mappings-{src}.tsv.", "", PREFIXES]
    for r in sorted(rows, key=lambda x: (x["code"], x["target"])):
        body.append(f"aeco:{r['code']} {MAP_REL[r['relation']]} <{ns}{r['target']}> .")
    (SRC / f"mappings-{src}.ttl").write_text("\n".join(body) + "\n")


def map_apply(tsv_path, specs):
    with open(tsv_path, newline="") as fh:
        props = list(csv.DictReader(fh, delimiter="\t"))
    by_src = {}
    added = 0
    concepts = load()
    temp = {k: r.get("code", "") for k, r in all_rows().items()}
    for spec in specs:
        gid, _, drops = spec.partition(":")
        drop = {d.strip() for d in drops.split(",") if d.strip()}
        for p in props:
            if p["group"] != gid or p["n"] in drop:
                continue
            code = p["code"]
            if not re.fullmatch(r"aeco-\d{5}", code):
                code = temp.get(code, "")
            if code not in concepts:
                print(f"SKIP {gid} {p['n']}: {p['code']} is not an accepted concept.")
                continue
            p = dict(p, code=code, label=concepts[code]["label_en_us"])
            src = p["source"]
            if src not in by_src:
                by_src[src] = read_mappings(src)
            rows = by_src[src]
            if any(r["code"] == p["code"] and r["target"] == p["target"] for r in rows):
                continue
            rows.append({"code": p["code"], "label_en_us": p["label"], "relation": p["relation"], "target": p["target"],
                         "target_label": "" if src == "uniclass" else p.get("target_label", ""), "note": p.get("note", ""), "group": gid, "added": TODAY})
            added += 1
    for src, rows in by_src.items():
        render_mappings(src, rows)
    print(f"{added} mappings added.")
    return check()


def ancestors(concepts, code):
    out, guard = set(), 0
    while concepts.get(code, {}).get("parent") and guard < 10:
        code = concepts[code]["parent"]
        out.add(code)
        guard += 1
    return out


# ---------- checks ----------
def check(verbose=True, all_findings=False):
    """Return the blocking findings, or every finding when all_findings is true."""
    from pyshacl import validate
    g = graph()
    shapes = Graph().parse(ROOT / "scripts" / "shapes.ttl", format="turtle")
    conforms, rg, _ = validate(g, shacl_graph=shapes, inference="none", advanced=True, allow_warnings=True)
    SH = Namespace("http://www.w3.org/ns/shacl#")
    found = []
    for r in rg.subjects(RDF.type, SH.ValidationResult):
        sev = "BLOCK" if rg.value(r, SH.resultSeverity) == SH.Violation else "WARN"
        node = str(rg.value(r, SH.focusNode)).replace(NS, "")
        msg = str(rg.value(r, SH.resultMessage) or "")
        found.append((sev, node, "Shape", msg))
    cs = load()
    lab_index = {}
    for code, c in cs.items():
        if c["deprecated"]:
            if not c["replaced_by"]:
                found.append(("BLOCK", code, "Deprecated", "A deprecated concept points to its replacement."))
            continue
        for i, s in enumerate(sentences(c["definition"]), 1):
            n = len(s.split())
            if n > MAX_WORDS:
                found.append(("BLOCK", code, "Length", f"Definition sentence {i} has {n} words. The limit is {MAX_WORDS}."))
        for lang, key in (("en-US", "label_en_us"), ("en-GB", "label_en_gb")):
            if c[key]:
                lab_index.setdefault((lang, c[key].lower()), []).append(code)
        if not c["label_en_gb"] and "Shared" in c["std"]:
            found.append(("WARN", code, "en-GB", "A Shared concept has no en-GB label."))
        # depth
        depth, cur, top, guard = 1, c, c, 0
        while cur["parent"] and guard < 10:
            cur = cs.get(cur["parent"]) or {"parent": ""}
            if "code" in cur:
                top = cur
            depth += 1
            guard += 1
        limit = top.get("depth_limit")
        if limit and depth > limit:
            found.append(("BLOCK", code, "Depth", f"Level {depth} is past the limit of {limit} for {top['label_en_us']}."))
        kids = [k for k, o in cs.items() if o["parent"] == code and not o["deprecated"]]
        if len(kids) == 1:
            found.append(("WARN", code, "Children", "Only one child. Merge, or add a sibling."))
        if len(kids) > 15:
            found.append(("WARN", code, "Children", f"{len(kids)} children. Add a middle level above 15."))
    for (lang, lab), codes in lab_index.items():
        if len(codes) > 1:
            for code in codes:
                found.append(("BLOCK", code, "Label", f"Preferred label '{lab}' ({lang}) is also used by {', '.join(x for x in codes if x != code)}."))
    alt_index = {}
    for code, c in cs.items():
        for a in c["alt_en_us"] + c["alt_en_gb"]:
            alt_index.setdefault(a.lower(), set()).add(code)
        for key in ("label_en_us", "label_en_gb"):
            if c[key]:
                alt_index.setdefault(c[key].lower(), set()).add(code)
    for a, codes in alt_index.items():
        if len(codes) > 1:
            found.append(("WARN", ", ".join(sorted(codes)), "Shared label", f"'{a}' is used by more than one concept. Check that the definitions tell them apart."))
    # A hidden label shared by several concepts marks an ambiguous plain word.
    # Taggers ask which concept is meant, or tag all candidates. It must not also be a visible label.
    hid_index = {}
    for code, c in cs.items():
        for h in c["hidden"]:
            hid_index.setdefault(h.lower(), set()).add(code)
    for h, codes in hid_index.items():
        clash = alt_index.get(h, set()) - codes
        if clash and len(h) > 3:  # short forms of 3 letters or fewer follow their own rule
            found.append(("WARN", ", ".join(sorted(codes | clash)), "Ambiguous label", f"Hidden label '{h}' is also a visible label of {', '.join(sorted(clash))}."))
    seen = set()
    for r in read_related():
        a, b = r["code_a"], r["code_b"]
        tag = f"{a}, {b}"
        if a not in cs or b not in cs:
            found.append(("BLOCK", tag, "Related", "A related link points to a code that is not in the base."))
            continue
        if cs[a]["deprecated"] or cs[b]["deprecated"]:
            found.append(("WARN", tag, "Related", "A related link points to a deprecated concept. Move it to the replacement."))
        if a == b or a in ancestors(cs, b) or b in ancestors(cs, a):
            found.append(("BLOCK", tag, "Related", "A related link joins a concept to itself or to its ancestor. Use the hierarchy."))
        key = tuple(sorted((a, b)))
        if key in seen:
            found.append(("WARN", tag, "Related", "The same link is listed twice."))
        seen.add(key)
    for src in MAP_SOURCES:
        exact = {}
        for r in read_mappings(src):
            tag = f"{r['code']} -> {src}:{r['target']}"
            if r["code"] not in cs:
                found.append(("BLOCK", tag, "Mapping", "A mapping points from a code that is not in the base."))
            elif cs[r["code"]]["deprecated"]:
                found.append(("WARN", tag, "Mapping", "A mapping starts at a deprecated concept. Move it to the replacement."))
            if r["relation"] not in MAP_REL:
                found.append(("BLOCK", tag, "Mapping", f"Unknown relation '{r['relation']}'. Use exact, close, broad or narrow."))
            if r["relation"] == "exact":
                exact.setdefault(r["target"], []).append(r["code"])
        for t, codes in exact.items():
            if len(set(codes)) > 1:
                found.append(("BLOCK", ", ".join(sorted(set(codes))), "Mapping", f"{src}:{t} is an exact match of more than one concept. Keep one, make the others close."))
    found = sorted(set(found))
    if all_findings:
        return found
    if verbose:
        print(f"{len(cs)} concepts checked.")
        for f in found:
            print("  ".join(f))
        if not found:
            print("All checks pass.")
    return [f for f in found if f[0] == "BLOCK"]


# ---------- csv ----------
def read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def write_csv(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in CSV_FIELDS})


def read_reviews(folder):
    out = {}
    for p in pathlib.Path(folder).rglob("*.json"):
        doc = json.loads(p.read_text())
        data = doc.get("data", doc) if isinstance(doc, dict) else {}
        out[doc.get("id", p.stem)] = data
    return out


def all_rows(current_path=None, current_rows=None):
    """Rows of every review/session-*.csv, keyed by temp_id. Parents are temp ids across sessions."""
    out = {}
    for p in sorted((ROOT / "review").glob("session-*.csv")):
        if current_path and p.resolve() == pathlib.Path(current_path).resolve():
            continue
        for r in read_csv(p):
            out[r["temp_id"]] = r
    for r in current_rows or []:
        out[r["temp_id"]] = r
    return out


# ---------- apply ----------
def apply(csv_path, reviews_dir):
    rows = read_csv(csv_path)
    reviews = read_reviews(reviews_dir)
    concepts = load()
    by_temp = all_rows(csv_path, rows)
    nums = [int(k.split("-")[1]) for k in concepts] or [0]
    next_num = max(nums) + 1
    log = []
    for r in sorted(rows, key=lambda x: int(x["level"] or 1)):
        rv = reviews.get(r["temp_id"])
        if not rv or not rv.get("decision"):
            continue
        rev = int(r["rev"] or 1)
        if int(rv.get("rev") or 0) < rev:
            continue
        if r.get("applied_rev") == str(rev) and r["decision"] == rv["decision"]:
            continue
        edits = rv.get("edits") or {}
        for f, col in (("label_en_us", "label_en_us"), ("label_en_gb", "label_en_gb"), ("definition", "definition"),
                       ("alt_labels", "alt_labels_en_us"), ("tags", "tags")):
            if f in edits:
                r[col] = str(edits[f]).strip()
        r["decision"] = rv["decision"]
        r["comment"] = rv.get("comment", "") or ""
        r["edits"] = "; ".join(f"{k}: {v}" for k, v in edits.items())
        r["decided_at"] = str(rv.get("at", ""))[:10] or TODAY
        r["applied_rev"] = str(rev)
        if rv["decision"] == "approved":
            if not r["code"]:
                r["code"] = f"aeco-{next_num:05d}"
                next_num += 1
            parent = r["parent"]
            if parent and parent in by_temp:
                parent = by_temp[parent]["code"]
            old = concepts.get(r["code"], {})
            concepts[r["code"]] = {
                "code": r["code"], "parent": parent or "",
                "label_en_us": r["label_en_us"], "label_en_gb": r["label_en_gb"], "definition": r["definition"],
                "alt_en_us": split_list(r["alt_labels_en_us"]), "alt_en_gb": split_list(r["alt_labels_en_gb"]),
                "hidden": split_list(r["hidden_labels"]), "tags": split_list(r["tags"], ","),
                "std": split_list(r["standard_sets"]), "scope_note": r["scope_note"], "group": r["group"],
                "depth_limit": int(r["depth_limit"]) if r["depth_limit"] else None,
                "created": old.get("created", TODAY), "modified": TODAY, "deprecated": False, "replaced_by": "",
            }
        log.append(r)
    render(concepts)
    write_csv(csv_path, rows)
    md = pathlib.Path(csv_path).with_suffix(".md")
    head = "" if md.exists() else f"Version: 0.1\nStatus: Living\nLast updated: {TODAY}\n\n# Review log: {pathlib.Path(csv_path).stem}\n\n> Append-only. One block per apply run. Decisions come from the review tool.\n"
    text = md.read_text() if md.exists() else head
    text = re.sub(r"Last updated: \d{4}-\d{2}-\d{2}", f"Last updated: {TODAY}", text, count=1)
    if log:
        text += f"\n## Applied {TODAY}\n\n| Temp ID | Code | Label | Round | Decision | Edits | Comment | Decided |\n|---|---|---|---|---|---|---|---|\n"
        for r in log:
            cell = lambda s: str(s or "").replace("|", "/").replace("\n", " ")
            text += f"| {r['temp_id']} | {cell(r['code'])} | {cell(r['label_en_us'])} | {r['rev']} | {r['decision']} | {cell(r['edits'])} | {cell(r['comment'])} | {r['decided_at']} |\n"
    md.write_text(text)
    print(f"{len(log)} decisions applied.")
    return check()


# ---------- page export ----------
def diff_text(old, r):
    """Plain-language summary of what a round-2 row changes against the accepted concept."""
    parts = []
    def lst(a, b, name):
        b = split_list(b, "," if name == "Tags" else ";")
        rem = [x for x in a if x not in b]
        add = [x for x in b if x not in a]
        bits = (["removed " + ", ".join(rem)] if rem else []) + (["added " + ", ".join(add)] if add else [])
        if bits:
            parts.append(name + ": " + "; ".join(bits))
    def one(a, b, name):
        if (a or "").strip() != (b or "").strip():
            parts.append(f"{name}: was {a or 'empty'}, now {b or 'empty'}")
    one(old["label_en_us"], r["label_en_us"], "Preferred label")
    one(old["label_en_gb"], r["label_en_gb"], "en-GB label")
    lst(old["alt_en_us"], r["alt_labels_en_us"], "Alternatives")
    lst(old["alt_en_gb"], r["alt_labels_en_gb"], "en-GB alternatives")
    lst(old["hidden"], r["hidden_labels"], "Hidden labels")
    if (old["definition"] or "").strip() != (r["definition"] or "").strip():
        parts.append("Definition rewritten")
    if (old["scope_note"] or "").strip() != (r["scope_note"] or "").strip():
        parts.append("Scope note rewritten")
    lst(old["tags"], r["tags"], "Tags")
    return ". ".join(parts)



def page(csv_path, out_dir):
    rows = read_csv(csv_path)
    concepts = load()
    by_temp = all_rows(csv_path, rows)
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    def top_label(r):
        cur, guard = r, 0
        while cur.get("parent") and cur["parent"] in by_temp and guard < 10:
            cur = by_temp[cur["parent"]]
            guard += 1
        return cur["label_en_us"]

    for i, r in enumerate(rows, 1):
        accepted = bool(r["code"]) and r["code"] in concepts
        pending = not r["decision"]
        src = r if (pending or not accepted) else None
        c = concepts.get(r["code"]) if accepted else None
        if c and not pending:
            vals = {"label_en_us": c["label_en_us"], "label_en_gb": c["label_en_gb"], "definition": c["definition"],
                    "alt_labels": c["alt_en_us"], "alt_labels_gb": c["alt_en_gb"], "tags": ", ".join(c["tags"]),
                    "scope_note": c["scope_note"]}
        else:
            vals = {"label_en_us": src["label_en_us"], "label_en_gb": src["label_en_gb"], "definition": src["definition"],
                    "alt_labels": split_list(src["alt_labels_en_us"]), "alt_labels_gb": split_list(src["alt_labels_en_gb"]),
                    "tags": ", ".join(split_list(src["tags"], ",")), "scope_note": src["scope_note"]}
        status = "Accepted" if accepted else ("Rejected" if r["decision"] == "rejected" else "Proposed")
        sess = int(r["session"] or 0)
        doc = dict(order=i if sess <= 1 else sess * 1000 + i, code=r["code"] if accepted else "", group=r["group"], branch=top_label(r), parent=r["parent"],
                   level=int(r["level"] or 1), iso_term=r["iso_term"], hidden_labels=split_list(r["hidden_labels"]),
                   standard_set=", ".join(split_list(r["standard_sets"])), status=status, session=int(r["session"] or 0),
                   batch=r["batch"], rev=int(r["rev"] or 1), checks=[], refs=split_list(r.get("refs", "")), change_note=r["change_note"], note="",
                   **vals)
        if accepted and pending and int(r["rev"] or 1) > 1:
            doc["diff"] = diff_text(concepts[r["code"]], r)
        (out / f"{r['temp_id']}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    print(f"{len(rows)} page documents written to {out}.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in ("check", "apply", "page", "relate", "map"):
        print(__doc__)
        sys.exit(2)
    if args[0] == "check":
        sys.exit(1 if check() else 0)
    if args[0] == "apply":
        sys.exit(1 if apply(args[1], args[2]) else 0)
    if args[0] == "relate":
        sys.exit(1 if relate(args[1], args[2:]) else 0)
    if args[0] == "map":
        sys.exit(1 if map_apply(args[1], args[2:]) else 0)
    page(args[1], args[2])
