# Changelog

All notable changes to the Aecoware Open Taxonomy are listed here. The format follows Keep a Changelog (https://keepachangelog.com), and versions follow Semantic Versioning (https://semver.org).

## [Unreleased]

### Added

- The Actions branch (`aeco-01074`): 37 actions in 5 groups, such as Submit, Review, Approve, Return, Close and Share. A record of work names one action and the thing it acts on.
- `aeco:actionType` and `aeco:actsOn`: the 25 activity concepts, such as Approve change order, point to their action and the thing it acts on.
- Mechanical completion (`aeco-01117`) and Punch item (`aeco-01118`, "Snag" in UK English).
- `scripts/field-words.tsv` and its check: 49 field words, each with the concepts it must find. Three known gaps (clash, MEP, IFC) warn until they are fixed.
- Checks for deprecated concepts: the replacement must exist and must not be deprecated itself.

### Changed

- Codes are permanent from v0.1.0, not from v1.0.0. A code never changes its meaning, and a concept is never deleted.
- "completion" is now a hidden label on Substantial, Final and Mechanical completion. Substantial completion has the UK label "Practical completion".
- "look-ahead" and "3-week look-ahead" find Look-ahead schedule. "3-week look-ahead" moved there from Look-ahead planning.
- "CE" and "change event" find Potential change order.
- "CO" and "PM" are hidden labels on each of their two candidates, so neither candidate ranks first.
- "submittal" finds Submittals.

## [0.1.0] - 2026-11-01

First public draft.

### Added

- 1,073 concepts in 15 branches, with definitions, US English labels, UK English labels where the term differs, and 2,238 synonyms
- 5W1H routing tags on every concept, with one primary tag, and [docs/5w1h.md](docs/5w1h.md): why the taxonomy uses them, how an agent can route a question with them, and where the six questions come from
- Standard sets: Shared, AIA, ConsensusDocs, DBIA, EJCDC, ICC International Codes, NFPA, OSHA 1926 and ADA
- 378 related links, including the links between elements and products
- Hidden labels for plain words that fit several concepts, such as "wall" and "door"
- Opt-in links to IFC 4.3, BOT, Brick, RealEstateCore, Uniclass 2015 and Wikidata (854 links), and to ISO 12006-2 and the RIBA Plan of Work by name only (23 links)
- SHACL shapes and a check script
- The explorer, with map and column layouts and Branches and 5W1H views

### Known gaps

- 59 shared concepts have no UK English label yet.
- 549 concepts have no link to an outside standard yet.
