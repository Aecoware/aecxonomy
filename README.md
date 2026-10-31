# Aecoware Open Taxonomy

An open SKOS taxonomy for architecture, engineering, construction and operations (AECO). It gives people and AI agents one shared set of terms for the built environment.

**Status:** draft v0.1.0. Codes stay stable from v1.0.0. Before v1.0.0, a concept can still move or change.

[Explore the taxonomy](https://aecoware.github.io/aecxonomy/) · [Cite it](CITATION.cff) · [Propose a change](CONTRIBUTING.md) · [Licence and credits](NOTICE.md)

## What is inside

| Item | Count |
|---|---|
| Concepts | 1,073 |
| Top branches | 15 |
| Synonyms (alternative labels) | 2,238 |
| Related links between concepts | 378 |
| 5W1H routing tags | 1 or 2 on every concept |
| Links to outside standards | 854, opt-in, plus 23 links by name only |

Each concept has:

- a stable code and IRI, for example `aeco-01008` (Beam) at `https://w3id.org/aeco/aeco-01008`
- a US English label, a UK English label where the term differs, and synonyms
- a definition of one or two short sentences
- one or two 5W1H tags (Who, What, Where, When, Why, How). The first tag is the primary tag.
- the standard sets it applies under, for example Shared or OSHA 1926
- a creation date and a change date

## The 15 branches

| Code | Branch | Concepts |
|---|---|---|
| aeco-00001 | Built assets | 70 |
| aeco-00002 | Spaces | 70 |
| aeco-00003 | Elements and systems | 137 |
| aeco-00004 | Work results | 94 |
| aeco-00005 | Processes and services | 90 |
| aeco-00006 | Phases | 24 |
| aeco-00007 | Roles and organizations | 55 |
| aeco-00008 | Information | 85 |
| aeco-00009 | Properties | 78 |
| aeco-00010 | Regulations and permits | 73 |
| aeco-00011 | Contracts and commercial | 62 |
| aeco-00012 | Requirements and decisions | 40 |
| aeco-00013 | Events and risks | 38 |
| aeco-00014 | Site and environment | 40 |
| aeco-00015 | Products and equipment | 117 |

Counts include the branch concept itself.

## Design rules

- **One concept, one parent.** The tree is at most 3 levels deep. Elements and systems, and Products and equipment, go to 4 levels.
- **Codes are opaque and never reused.** A label can change. The code stays.
- **Plain definitions.** Definitions follow the writing rules of ASD-STE100 Simplified Technical English: short sentences, one meaning for each word, 25 words or fewer in a sentence.
- **Elements and products are two views of one item.** An element is a part in its place and what it does. A product is the same item as something you specify and buy. Related links join the two.
- **Plain words that fit many concepts are flagged.** Words such as "wall" or "door" are hidden labels on each candidate concept. A search for them asks which concept you mean.
- **5W1H tags route questions, they do not build the tree.** An agent sorts a task question by the six tags, then follows only the concepts with the matching tag. [Why 5W1H](docs/5w1h.md) tells why we use the six questions, how an agent can route with them, and where they come from.
- **Every concept passes SHACL checks** before it goes into the files.

## Linked standards (opt-in)

The core taxonomy stands alone. Links to outside vocabularies sit in separate files, so you load them only when you need them. Each link is a SKOS mapping: `exactMatch`, `closeMatch`, `broadMatch` or `narrowMatch`.

| Standard | Published by | Links | What the link holds | File |
|---|---|---|---|---|
| IFC 4.3 | buildingSMART International | 156 | Class identifier | `src/mappings-ifc.ttl` |
| BOT | W3C Linked Building Data Community Group | 8 (6 of 7 classes) | Class IRI | `src/mappings-bot.ttl` |
| Brick | Brick Consortium | 62 | Class IRI | `src/mappings-brick.ttl` |
| RealEstateCore | RealEstateCore Consortium | 39 | Class IRI | `src/mappings-rec.ttl` |
| Uniclass 2015 | NBS | 210 | Code only, no title | `src/mappings-uniclass.ttl` |
| Wikidata | Wikimedia community | 379 | Item ID | `src/mappings-wikidata.ttl` |
| ISO 12006-2:2015 | ISO | 14 | Class name only | `src/mappings-iso-12006-2.tsv` |
| RIBA Plan of Work 2020 | RIBA | 9 (all 8 stages) | Stage number and name only | `src/mappings-riba-plan-of-work.tsv` |

The links are our own judgement of meaning, not official mappings from the publishers. [NOTICE.md](NOTICE.md) gives the licence of each source and what we take from it.

## Repository layout

```
docs/
  5w1h.md                    why the taxonomy uses the 5W1H tags
src/
  aeco-base.ttl              the concept scheme
  branches/*.ttl             the concepts, one file for each branch
  tags.ttl                   the 5W1H tags
  standard-sets.ttl          the standard sets (Shared, AIA, OSHA 1926 and others)
  related.ttl                related links between concepts
  mappings-<source>.ttl      opt-in links to outside standards
  mappings-<source>.tsv      the same links as tables, for review
scripts/
  shapes.ttl                 the SHACL shapes
  taxo.py                    the checks, and maintainer tools
  build_site.py              builds the explorer and the merged data files
site/
  template.html              the explorer source
```

`scripts/build_site.py` writes `site/index.html` (the explorer), `site/aeco.ttl` and `site/aeco.jsonld` (the core taxonomy in one file) and `site/aeco-mappings.ttl` (all links to outside standards). GitHub Actions builds and publishes them on every change to `main`.

## Use it

Load the core files with Python and rdflib, then ask a question with SPARQL:

```python
from glob import glob
from rdflib import Graph

g = Graph()
for path in ["src/aeco-base.ttl", "src/tags.ttl", "src/standard-sets.ttl",
             "src/related.ttl", *sorted(glob("src/branches/*.ttl"))]:
    g.parse(path)

# Every concept whose primary question is "Who"
query = """
PREFIX aeco: <https://w3id.org/aeco/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?concept ?label WHERE {
  ?concept aeco:primaryTag aeco:tag-who ;
           skos:prefLabel ?label .
  FILTER (lang(?label) = "en-US")
}
ORDER BY ?label
"""
for concept, label in g.query(query):
    print(concept, label)
```

Add `src/mappings-ifc.ttl` (or another mapping file) to the list when you want the links to that standard.

You can also take the whole core taxonomy as one file. The permanent address returns Turtle or JSON-LD when you ask for it:

```
curl -L -H "Accept: text/turtle" https://w3id.org/aeco/ -o aeco.ttl
curl -L -H "Accept: application/ld+json" https://w3id.org/aeco/ -o aeco.jsonld
curl -L https://w3id.org/aeco/mappings -o aeco-mappings.ttl
```

Run the checks:

```
pip install rdflib pyshacl
python3 scripts/taxo.py check
python3 scripts/build_site.py
```

## Versions

We use semantic versions. A minor version adds concepts. A patch fixes wording. A major version removes or changes the meaning of a concept. From v1.0.0, a removed concept stays in the files as deprecated, with a link to its replacement. See [CHANGELOG.md](CHANGELOG.md).

## Contributing

Proposals are welcome. Open an issue with the concept proposal form. A maintainer reviews each change before it goes in. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

- Taxonomy content (`src/`, documentation): [Creative Commons Attribution 4.0 International](LICENSE) (CC BY 4.0)
- Code (`scripts/`, `site/`): [Apache License 2.0](LICENSES/Apache-2.0.txt)
- Outside standards keep their own licences. See [NOTICE.md](NOTICE.md).

When you reuse the taxonomy, credit it like this:

> Aecoware Open Taxonomy v0.1.0, © 2026 Roman Makarov, Tomasz Pijanowski and Kamil Grecki, licensed under CC BY 4.0, https://w3id.org/aeco/

## Trademarks

Aecoware and the Aecoware logo are trademarks of the Aecoware founders. The licences above do not give rights to use them. You can say that your work is "based on the Aecoware Open Taxonomy". Do not suggest that Aecoware endorses your product or service.

## No warranty

The taxonomy is provided as is. It is not legal, engineering or professional advice, and it does not replace building codes, contracts or standards.

## Contact

roman@aecoware.com
