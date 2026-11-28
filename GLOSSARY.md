# Aecoware Open Taxonomy

An open SKOS taxonomy for architecture, engineering, construction and operations (AECO), and the explorer that shows it to people.

## Language

### The taxonomy

**Concept**:
One entry in the taxonomy. It has a stable code, labels, a definition and one or two 5W1H tags.
_Avoid_: Term, class, entry

**Branch**:
A top-level concept. Every other concept sits under exactly one branch.
_Avoid_: Category, table

**5W1H tag**:
One of six tags (Who, What, Where, When, Why, How) that tells which question a concept answers. Every concept has one or two.
_Avoid_: Kipling tag, question, kind

**Primary tag**:
The first 5W1H tag of a concept.

**Related concept**:
A concept joined to another concept inside the taxonomy, outside the parent and child line.
_Avoid_: Related link, link

**Mapping**:
A SKOS match (exact, close, broad or narrow) from a concept to an entry in an outside standard.
_Avoid_: Link, crosswalk, alignment

**Outside standard**:
A classification or vocabulary outside the taxonomy that concepts have mappings to, for example Uniclass, IFC or Brick.
_Avoid_: Standard (on its own), linked standard

**Standard set**:
A family of contracts, codes or regulations that a concept applies under, for example AIA, OSHA 1926 or NFPA.
_Avoid_: Standard, regime

### The explorer

**Grouping**:
What concepts sit under at the top level of the explorer, for example branches, 5W1H tags or outside standards.
_Avoid_: View, lens

**Layout**:
How the explorer shows a grouping: as the map or as columns.
_Avoid_: View, mode

**Map**:
The explorer's zoomable drawing of a whole grouping.
_Avoid_: Chart, sunburst

**Map type**:
How the map is drawn: as an icicle, a sunburst or a territory map.
_Avoid_: Variant, style

**Region**:
In the territory map, a child of the focus, drawn as one cell of the circle.
_Avoid_: Area, zone

**District**:
In the territory map, a child of a region, drawn as a cell inside it. A click on a district opens its region.
_Avoid_: Subregion

**Filter**:
A 5W1H tag or an outside standard that narrows which concepts the explorer shows. A concept counts under every tag it has.
_Avoid_: Facet

**Concept page**:
The page of one concept, at the address its IRI resolves to in a browser.
_Avoid_: Panel, detail view
