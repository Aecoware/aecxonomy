# Notice

Aecoware Open Taxonomy
Copyright © 2026 Roman Makarov, Tomasz Pijanowski and Kamil Grecki, the founders of Aecoware

The founders will assign these rights to Aecoware when the company is incorporated.

This repository contains the Aecoware Open Taxonomy, made by Aecoware (https://aecoware.com).

## Licences

| Part | Licence |
|---|---|
| Taxonomy content: `src/`, documentation | CC BY 4.0, see `LICENSE` |
| Code: `scripts/`, `site/` | Apache License 2.0, see `LICENSES/Apache-2.0.txt` |

If you share or adapt the taxonomy, you must credit it. Use this line or one with the same information:

> Aecoware Open Taxonomy v0.1.0, © 2026 Roman Makarov, Tomasz Pijanowski and Kamil Grecki, licensed under CC BY 4.0, https://w3id.org/aeco/

If you redistribute the code, keep this NOTICE file with it, as the Apache License 2.0 requires.

## What is original work

Aecoware made these parts:

- the selection of concepts and their arrangement into branches and levels
- the definitions and scope notes
- the 5W1H tags, the standard-set tags and the related links
- the choice of each link to an outside standard and its relation type
- the SHACL shapes, the scripts and the explorer

Labels and synonyms are common industry terms. Aecoware does not claim them as its own.

## Outside standards

The taxonomy links to the standards below. A link holds only an identifier, a code or a name, as the table in each section says. We do not copy, change or redistribute the content of these standards. Their owners keep all rights in them. A link is our own judgement of meaning. It is not an official mapping from the owner.

### IFC 4.3, Industry Foundation Classes

- **Owner:** buildingSMART International Limited. Copyright © 1996-2024 buildingSMART International Limited. Some rights reserved.
- **Licence:** Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)
- **What we use:** class identifiers, for example `IfcBeam`, as link targets in `src/mappings-ifc.ttl`
- **Trademarks:** buildingSMART®, openBIM® and IFC™ are trademarks or registered trademarks of buildingSMART International Limited.
- **Source:** https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/

### BOT, Building Topology Ontology

- **Owner:** the W3C Linked Building Data Community Group. Creators: Mads Holten Rasmussen, Pieter Pauwels, Maxime Lefrançois and Georg Ferdinand Schneider, with all contributing members of the group.
- **Licence:** Creative Commons Attribution 1.0 (CC BY 1.0)
- **What we use:** class IRIs, for example `bot:Storey`, as link targets in `src/mappings-bot.ttl`
- **Source:** https://w3id.org/bot

### Brick

- **Owner:** Brick Consortium, Inc. Copyright © 2016-2026 Brick Consortium, Inc.
- **Licence:** BSD 3-Clause
- **What we use:** class IRIs as link targets in `src/mappings-brick.ttl`
- **Source:** https://github.com/BrickSchema/Brick

### RealEstateCore

- **Owner:** RealEstateCore Consortium. Copyright © 2022 RealEstateCore Consortium.
- **Licence:** BSD 3-Clause
- **What we use:** class IRIs as link targets in `src/mappings-rec.ttl`
- **Source:** https://github.com/RealEstateCore/rec

### Uniclass 2015

- **Owner:** Uniclass is maintained by NBS.
- **Licence:** Creative Commons Attribution-NoDerivatives 4.0 International (CC BY-ND 4.0)
- **What we use:** codes only, for example `ss_20_20`, as link targets in `src/mappings-uniclass.ttl`. We do not include Uniclass titles, adapt the tables or add codes.
- **Credit:** Uniclass 2015 codes, maintained by NBS, CC BY-ND 4.0.
- **Source:** https://uniclass.thenbs.com

### Wikidata

- **Owner:** the Wikidata community, hosted by the Wikimedia Foundation
- **Licence:** structured data under Creative Commons CC0 1.0. CC0 asks for no credit. We give it anyway.
- **What we use:** item IDs, for example `Q3705329`, as link targets in `src/mappings-wikidata.ttl`
- **Trademark:** Wikidata is a trademark of the Wikimedia Foundation. We use the name only to identify the source.
- **Source:** https://www.wikidata.org

### ISO 12006-2:2015

- **Title:** Building construction: Organization of information about construction works, Part 2: Framework for classification
- **Owner:** International Organization for Standardization (ISO). All rights reserved by ISO.
- **What we use:** class names only, for example "construction element", in `src/mappings-iso-12006-2.tsv`. We reproduce no ISO text, tables or codes.
- **Source:** buy the standard from ISO (https://www.iso.org) or from your national standards body.

### RIBA Plan of Work 2020

- **Owner:** Royal Institute of British Architects (RIBA)
- **What we use:** stage numbers and stage names only (0 to 7) in `src/mappings-riba-plan-of-work.tsv`. We reproduce no RIBA text.
- **Source:** https://www.architecture.com

## Standard sets

Some concepts carry a tag that names a US family of contract documents, codes or regulations: AIA contract documents, ConsensusDocs, DBIA, EJCDC, ICC International Codes, NFPA codes, OSHA 29 CFR 1926 and the ADA Standards. The tag only says that the concept is used under that set. We reproduce no text from these documents. The names belong to their owners.

## Classification systems we do not use

This repository contains no codes and no titles from MasterFormat, UniFormat or OmniClass. Three scope notes name MasterFormat or UniFormat only to explain how a branch is organized.

## Writing rules

Definitions follow the writing rules of ASD-STE100 Simplified Technical English. ASD-STE100 is a trademark of ASD. This is not a claim of compliance with ASD-STE100, and ASD does not endorse this work.

## W3C standards

The taxonomy is written in SKOS and Turtle, with a JSON-LD export, and checked with SHACL. These are W3C Recommendations.

## Explorer and tools

- The explorer in `site/` loads D3 (ISC licence, Copyright 2010-2023 Mike Bostock) and the IBM Plex fonts (SIL Open Font License 1.1, Copyright IBM Corp.) when it runs. It does not redistribute them.
- `scripts/` uses rdflib (BSD 3-Clause) and pySHACL (Apache License 2.0) as installed dependencies. It does not redistribute them.

## No endorsement

We name standards and organizations only to identify the sources we link to. None of them endorses Aecoware or this taxonomy, and Aecoware has no affiliation with them.

## No warranty

The taxonomy is provided as is, without warranty of any kind. It is not legal, engineering or professional advice. It does not replace building codes, contracts or standards. Check the source standard before you rely on a link.

## Corrections

If you own a standard named here and you want us to change how we credit or link to it, contact roman@aecoware.com. We will correct it.
