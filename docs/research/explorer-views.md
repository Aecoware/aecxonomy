# Explorer views: background research

This note collects evidence for a redesign of the taxonomy explorer. It does not choose a design. It feeds a later interview that will decide who the explorer is for and what it should do.

Sites were visited on 23 November 2026. Library versions are the latest on npm on that date.

## The question

The explorer shows about 1,100 concepts as a zoomable D3 sunburst. The owner says it is laggy and not intuitive. Four questions follow:

1. How do established vocabulary browsers show a hierarchy of this size?
2. What does usability research say about hierarchy views for finding and understanding concepts?
3. What does an SVG sunburst of this size cost to render and animate, and what are the alternatives?
4. Which libraries fit a static GitHub Pages site that loads scripts from a CDN, with no build step?

Some numbers about the data, counted from the built `site/index.html` in the working tree:

- 1,118 concepts under 16 top-level branches. The tree has 4 levels: 16, 150, 819 and 133 concepts. 926 concepts are leaves. The largest branch has 15 children.
- The "Kipling 5W1H" view places a concept under every tag it has, and adds faded parents for the path. By the same rule as `buildTree()` in `site/template.html`, that view has about 1,466 arcs.
- The live site still has the older build: 1,073 concepts under 15 branches ([live explorer](https://aecoware.github.io/aecxonomy/)).

## Summary

- **No established vocabulary browser uses a radial or space-filling chart as its main view.** Skosmos, the Getty AAT, Uniclass, bSDD and OntoPortal all use search plus an indented tree, or one page per concept with its path, parent, children and siblings. Graphs appear only as a secondary tab, or in ontology tools such as WebVOWL. See [section 1](#1-how-vocabulary-browsers-show-a-hierarchy).
- **Search is the main way in.** The browsers suggest terms as you type, match synonyms, show each hit with its path, and filter hits by category with counts.
- **Cross-cutting categories are filters with counts, not extra trees.** Uniclass filters by table and status, bSDD by type and dictionary, Skosmos by group.
- **Phone support is mixed.** Skosmos and Uniclass reflow for a phone. Getty, AgroPortal and bSDD keep a desktop layout. On the live explorer at phone width, the sunburst starts about 1,380 px down the page and its label text is about 5 px.
- **No view wins every task.** For finding a named item, indented trees and linear layouts do as well as or better than radial ones ([Kobsa 2004](https://ics.uci.edu/~kobsa/papers/2004-InfoVis-kobsa.pdf), [Fu et al. 2013](https://link.springer.com/content/pdf/10.1007/978-3-642-41335-3_8.pdf), [Plaisant et al. 2002](https://obj.umiacs.umd.edu/spacetree/2002-05.pdf)). A radial node-link tree took about 21 s against 12 s for a top-down tree on a structure task, with the same accuracy ([Burch et al. 2011](https://doi.org/10.1109/TVCG.2011.193)).
- **The sunburst and the icicle did about equally well where both were tested, and people liked the icicle more.** The sunburst beat the treemap and was preferred to it ([Stasko et al. 2000](https://faculty.cc.gatech.edu/~stasko/papers/ijhcs00.pdf)). But users found small slices hard to see, and fewer labels fit ([Woodburn et al. 2019](https://arxiv.org/pdf/1908.01277)).
- **Rotated text is slower to read.** There is almost no cost within 45°. At 90°, single words took about 26% longer and phrases 44–68% longer. Upside-down phrases took about twice as long ([Wigdor & Balakrishnan 2005](https://www.dgp.toronto.edu/public_user/ravin/papers/ecscw2005_textorientation.pdf)).
- **Facets with counts, and search hits grouped by category, have good evidence.** 29 of 32 people preferred a faceted interface overall ([Yee et al. 2003](http://flamenco.berkeley.edu/papers/flamenco-chi03.pdf)). Grouping hits under their category cut search time by about a quarter ([Dumais et al. 2001](https://www.cs.ucdavis.edu/~hchen/paper/chi2001.pdf)). Those studies used images and web pages, not concept vocabularies.
- **The current sunburst does a lot of work for what it shows.** It keeps one `path` and one `text` element per concept in the DOM. The live page has about 2,450 elements, but only 45 of its 1,075 labels show at the start. Each zoom updates every node on every frame. Published guidance puts this size near the point where SVG animation gets heavy: about 1,000 to 2,000 elements ([Lighthouse](https://developer.chrome.com/docs/lighthouse/performance/dom-size), [ECharts](https://echarts.apache.org/handbook/en/best-practices/canvas-vs-svg/), [Woodburn et al. 2019](https://arxiv.org/pdf/1908.01277)). The hotspots named in section 3 are hypotheses from reading the code, not measurements.
- **Several libraries load from a CDN with no build step.** D3, which the page already loads, can draw the same arcs on a canvas. Apache ECharts has a sunburst, a tree and a treemap, drawn on canvas or SVG (about 1.1 MB). Wunderbaum is a virtual, ARIA treegrid (beta). MiniSearch gives in-page search with prefix and fuzzy matching (about 19 KB).

## 1. How vocabulary browsers show a hierarchy

The phone column comes from loading each page in a 375 × 812 px viewport and checking the viewport meta tag and horizontal scrolling.

| Browser | Main view | How the hierarchy shows | Search | Facets or cross-cutting tags | Concept detail | Phone |
|---|---|---|---|---|---|---|
| **Skosmos 3** (UNESCO Thesaurus) | Concept page with a sidebar | Sidebar tabs A–Z, Hierarchy, Groups and New. The Hierarchy tab is a collapsible indented tree. | Suggests terms as you type and highlights the match. A synonym shows with an arrow to its preferred term. | Groups (domains, microthesauri) as a tab and as a search filter | Preferred term, narrower, related, entry terms, groups, other languages, URI, RDF download | Yes. The sidebar folds into a "Browse concepts" button. |
| **Getty AAT** | Search form, then a results list | An indented outline with dotted leaders. An icon on each line opens the hierarchy at that concept. | AND/OR and truncation. Each hit shows its parent path in brackets. | 8 facets are the top level of the one tree. They are not cross-cutting. | Note, terms in many languages, the hierarchy position as an indented path, sources | No. There is no viewport tag, and the layout uses tables. |
| **NBS Uniclass** | Search box plus a list of tables | One page per code. A breadcrumb shows the path, "Contains" lists the children with counts, and the siblings are listed too. | A results table with title, table and code. Sort by relevance, code or title. | Checkboxes by table and by status, each with a count | Parent, status and version, children, siblings, mappings (for example COBie) | Yes. No horizontal scroll at 375 px. |
| **bSDD search** | Search first, with tiles for popular dictionaries | A breadcrumb to the root, plus the parent and child classes on the class page | Name search, with a switch to search descriptions too. A results table with definitions. | Version and status switches, type (classes, properties and more), and dictionary grouped by organisation | Code, URI, definition, parent, children, relations to other dictionaries | No. The page is 1,280 px wide at a 375 px viewport. |
| **OntoPortal** (AgroPortal, AGROVOC) | Ontology page with tabs | A tree with expand arrows in a left pane, a "Jump to" box and a filter | "Jump to" inside the tree, plus site search | A filter on the tree | Tabs: Details, Visualization, Notes, Mappings | No. There is no viewport tag, so a phone gets the desktop layout. |
| **schema.org** full hierarchy | One page | A nested list of about 800 types under Thing, with an open/close control | None on the page | None | A link to each type's page | Not checked |
| **WebVOWL** | Force-directed graph | Classes are nodes and properties are edges, drawn in the VOWL notation | Users in its studies asked for search with highlighting | Filters, such as collapsing classes with few links | A side panel | Not checked |

Notes on each browser:

- **Skosmos.** The UNESCO Thesaurus runs on Skosmos and holds about 4,500 concepts in 7 domains and 88 microthesauri ([UNESCO browser](https://vocabularies.unesco.org/browser/thesaurus/en/)). The concept page, sidebar tabs, suggestions and phone layout above are from the [Cultural heritage concept page](https://vocabularies.unesco.org/unesco/en/page?uri=http%3A%2F%2Fvocabularies.unesco.org%2Fthesaurus%2Fconcept269) and its [search results](https://vocabularies.unesco.org/unesco/en/search?q=cultural+heritage&clang=en&anylang=on). The results page filters by type and group. Each hit lists its narrower and related terms, its group and its translations. Skosmos 3.0 (December 2025) rebuilt the front end, worked on accessibility, and added type labels to the suggestions ([release notes](https://github.com/NatLibFi/Skosmos/releases/tag/v3.0)). The latest release is 3.6 ([releases](https://github.com/NatLibFi/Skosmos/releases)). Finto, the main Skosmos site, asked for a bot check, so I did not use it.
- **Getty AAT.** The [hierarchy display](https://www.getty.edu/vow/AATHierarchy?find=&logic=AND&note=&subjectid=300000000) starts at the facets. The [search results for "beams"](https://www.getty.edu/vow/AATServlet?english=Y&find=beams&logic=AND&page=1&note=) show each hit with its path, which tells apart the 66 concepts that match. The [full record for beams](https://www.getty.edu/vow/AATFullDisplay?find=beams&logic=AND&note=&english=N&prev_page=1&subjectid=300001497) shows the hierarchy position as an indented path. In the AAT, a concept can have more than one parent. One parent is preferred and listed first. The others are marked "[N]". Guide terms, which only group concepts, are shown in angle brackets ([About the AAT](https://www.getty.edu/research/tools/vocabularies/aat/about.html)).
- **Uniclass.** The results for ["beam"](https://uniclass.thenbs.com/search?query=beam&filter=status%3ACurrent) number 67, with a count next to each table filter (Products 38, Systems 25 and so on). A [table page](https://uniclass.thenbs.com/taxon/pr_25) lists each child with "Contains n current codes". A [code page](https://uniclass.thenbs.com/taxon/pr_25_71_33_33) shows the parent, the siblings and a COBie mapping. I checked only the public Uniclass site, not NBS's paid tools.
- **bSDD.** The [results for "beam"](https://search.bsdd.buildingsmart.org/?SearchText=beam&ShowPreview=true) number 320, across many dictionaries. The [IfcBeam page](https://search.bsdd.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcBeam) shows the path from the root to Beam as a breadcrumb.
- **OntoPortal.** BioPortal asked for a bot check, so I used [AgroPortal](https://agroportal.eu/ontologies/AGROVOC?p=classes), an OntoPortal site ([OntoPortal docs](https://ontoportal.github.io/documentation/)). Its Visualization tab showed an error page for AGROVOC, a SKOS vocabulary.
- **schema.org.** The [full hierarchy](https://schema.org/docs/full.html) is a single nested list with no search.
- **WebVOWL.** WebVOWL draws an ontology as a force-directed graph in the VOWL notation ([Lohmann et al. 2016](https://semantic-web-journal.net/system/files/swj1114.pdf), [repo](https://github.com/VisualDataWeb/WebVOWL)). Its authors say large ontologies remain an open problem. They also say the layout starts at random, so it differs each session and users cannot build a stable mental map.
- **PoolParty.** Its help pages describe a visual browser that shows one concept's relations as a graph. The pages would not load in full ([PoolParty help](https://help.poolparty.biz/8.1/en/user-guide-for-knowledge-engineers/basic-features/additional-information-about-the-project-and-its-concepts/visualization-of-a-project.html)), so this is not verified.

What the browsers share:

- **Search comes first.** Every browser puts a search box at the top of every page. Three of them match synonyms and show where a hit sits.
- **The path is always shown.** It appears as a breadcrumb (Uniclass, bSDD), an indented path (Getty) or a tree opened at the concept (Skosmos, OntoPortal).
- **A concept has a page and a URL.** The page lists the parent, children, siblings or related concepts, and the mappings to other schemes.
- **Counts are next to choices.** Uniclass shows them next to children and filters, and bSDD next to results.
- **None shows a whole vocabulary of this size on one screen.**

## 2. What usability research says

### Results by view and task

The studies test different tasks, and the results change with the task. The task types are:

- **Lookup**: find a named item.
- **Structure**: parents, siblings, depth, common ancestor.
- **Comparison**: which is larger.
- **Overview**: size or balance of branches.

| View | Evidence for | Evidence against | Main studies |
|---|---|---|---|
| Indented tree or outline | Fastest overall and easiest to use in a 6-way test on a 5,799-node taxonomy. Fastest to return to a node already visited. Beat a graph on accuracy for ontology work. | Poor at telling which branch is biggest (12 of 18 wrong). Small indents make siblings hard to tell from parents. Repeats a concept under each parent. | [Kobsa 2004](https://ics.uci.edu/~kobsa/papers/2004-InfoVis-kobsa.pdf), [Plaisant 2002](https://obj.umiacs.umd.edu/spacetree/2002-05.pdf), [Fu 2013](https://link.springer.com/content/pdf/10.1007/978-3-642-41335-3_8.pdf), [Fu 2017](https://www.semantic-web-journal.net/system/files/swj861_0.pdf) |
| Columns (multi-pane) | Beat a flat outline on retrieval, and beat expand/collapse on a heavy browsing task (46 s vs 78 s). Preferred to one page per level. | No controlled study of Finder-style Miller columns was found. The nearest study had 3 fixed panes and 3 levels. | [Chimera & Shneiderman 1994](https://doi.org/10.1145/185462.185483), [schraefel et al. 2003](https://eprints.soton.ac.uk/258800/) |
| Icicle (partition) | As fast as the semicircle sunburst and faster than the treemap for navigation and structure. Preferred to the treemap. Fastest for "is the tree balanced". | Little difference from the radial forms on most tasks | [Woodburn 2019](https://arxiv.org/pdf/1908.01277), [Barlow & Neville 2001](https://courses.ischool.berkeley.edu/i247/s02/readings/barlow.pdf) |
| Sunburst | As accurate as or better than the treemap, and preferred to it by 51 of 60. A sunburst-like "tree ring" was fastest for finding a node again from memory. | Small slices hard to see in large trees. Least liked in a 6-person pilot, partly because fewer labels fit. Labels are rotated. | [Stasko 2000](https://faculty.cc.gatech.edu/~stasko/papers/ijhcs00.pdf), [Barlow & Neville 2001](https://courses.ischool.berkeley.edu/i247/s02/readings/barlow.pdf), [Woodburn 2019](https://arxiv.org/pdf/1908.01277) |
| Treemap | Most accurate in one 6-way test. Fastest at "find the largest". | Slowest or least accurate on structure in two studies, and least preferred | [Kobsa 2004](https://ics.uci.edu/~kobsa/papers/2004-InfoVis-kobsa.pdf), [Barlow & Neville 2001](https://courses.ischool.berkeley.edu/i247/s02/readings/barlow.pdf), [Woodburn 2019](https://arxiv.org/pdf/1908.01277) |
| Radial node-link tree | Parent–child links are easy to see. | About 80% slower than a top-down tree for a common-ancestor task, with the same accuracy. Least preferred. Depth is hard to judge. | [Burch 2011](https://doi.org/10.1109/TVCG.2011.193), [Kobsa 2004](https://ics.uci.edu/~kobsa/papers/2004-InfoVis-kobsa.pdf) |
| Force or node-link graph | Novices liked how a graph shows multiple parents. Each glance at a graph was quicker to take in. | Slower to search than a tree, with more fixations and longer scan paths. Clutters above about 200 nodes. | [Fu 2013](https://link.springer.com/content/pdf/10.1007/978-3-642-41335-3_8.pdf), [Fu 2017](https://www.semantic-web-journal.net/system/files/swj861_0.pdf), [Katifori 2007](https://doi.org/10.1145/1287620.1287621) |
| Faceted browse | Preferred overall by 29 of 32. Found more of the relevant items. Far fewer empty result pages. | Preference split evenly for a simple lookup on one facet. Slower in that study, though its prototype was also slower to respond. | [Yee 2003](http://flamenco.berkeley.edu/papers/flamenco-chi03.pdf), [Hearst 2009, ch. 8](https://searchuserinterfaces.com/book/sui_ch8_navigation_and_search.html) |
| Search hits grouped by category | About a quarter faster than a flat list, and preferred. A category label on each hit of a flat list did not help. | Tested on lookup only, with queries chosen to be ambiguous | [Dumais 2001](https://www.cs.ucdavis.edu/~hchen/paper/chi2001.pdf), [Hearst 2009, ch. 8](https://searchuserinterfaces.com/book/sui_ch8_navigation_and_search.html) |

### The studies

| Study | People | Data | Views | Tasks | Key result |
|---|---|---|---|---|---|
| [Stasko et al. 2000](https://faculty.cc.gatech.edu/~stasko/papers/ijhcs00.pdf) | 32 + 28 students | File trees of about 500 and 3,000 nodes | Treemap, sunburst | Lookup by path or name, structure (deepest folder and more), size comparisons | Sunburst as accurate or better. No significant time difference. Treemap trended faster at "find the largest". 51 of 60 preferred the sunburst. |
| [Barlow & Neville 2001](https://courses.ischool.berkeley.edu/i247/s02/readings/barlow.pdf) | 15 + 15 staff | Small decision trees (16–159 nodes) with no text | Org chart, icicle, treemap, tree ring | Structure, balance, largest leaves, finding a node again | Treemap slowest. Icicle and org chart preferred. Tree ring fastest at finding a node again. Icicle faster at describing nodes by level. |
| [Kobsa 2004](https://ics.uci.edu/~kobsa/papers/2004-InfoVis-kobsa.pdf) | 48 students | eBay taxonomy, 5,799 nodes, 5 levels | Treemap, SequoiaView, BeamTrees, Star Tree, Tree Viewer, Windows Explorer | 15 tasks: structure and attributes | Explorer fastest (101 s per task) and easiest to use. Treemap most accurate (73%). The best tool depended on the task. |
| [Plaisant et al. 2002](https://obj.umiacs.umd.edu/spacetree/2002-05.pdf) | 18 students | Taxonomy of over 7,000 nodes | SpaceTree, hyperbolic tree, Explorer | Lookup, return to a node, list ancestors, biggest branch | Explorer fastest to return to a node. SpaceTree best on ancestors and on biggest branch. Hyperbolic labels hard to scan. |
| [Woodburn et al. 2019](https://arxiv.org/pdf/1908.01277) | 12 (plus a pilot of 6) | Taxonomy of 7,548 nodes, 15 levels | Treemap, icicle, semicircle sunburst ("sundown"). The full sunburst was dropped after the pilot. | Navigate to a leaf, compare sizes, relationship of two nodes, common ancestor | Icicle and sundown faster than treemap. No difference between icicle and sundown. Icicle preferred to treemap. People tilted their heads to read. |
| [McGuffin & Robert 2010](http://profs.etsmtl.ca/mmcguffin/research/treeRepEfficiency/treeRepEfficiency.pdf) | None (analysis) | Model trees | 11 layouts | Room for nodes and labels | In deep trees, sunburst leaves get more room than icicle leaves. But sunburst labels cannot all face one way. A static outline has little label room; scrolling and collapsing make up for it. |
| [Burch et al. 2011](https://doi.org/10.1109/TVCG.2011.193) | 36 | Synthetic trees up to 500 nodes, no labels | Traditional, orthogonal and radial node-link trees | Common ancestor | Radial about 21 s, traditional about 12 s. Same accuracy. Radial least preferred. |
| [Goldberg & Helfman 2011](https://doi.org/10.1177/1473871611406623) (abstract only) | 32 | Charts, not trees | Linear vs radial charts | Reading values | Linear was faster. Following the circle was the slow step. |
| [Wigdor & Balakrishnan 2005](https://www.dgp.toronto.edu/public_user/ravin/papers/ecscw2005_textorientation.pdf) | 15 + 9 | Words, phrases and numbers on a tabletop | Text at 8 angles | Read it, or find one word among 24 | See the rotated-text bullet below. Words at mixed angles made the search 18% slower. |
| [Fu et al. 2013](https://link.springer.com/content/pdf/10.1007/978-3-642-41335-3_8.pdf) | 36 novices | Ontologies of 38–181 classes | Protégé indented tree vs D3 force graph | Check and create mappings | Tree more accurate on the harder pair, which had multiple parents. Tree faster, but not significantly. Some users liked the graph for showing multiple parents. |
| [Fu et al. 2017](https://www.semantic-web-journal.net/system/files/swj861_0.pdf) | 31 (eye tracking) | Same | Same | Same | Tree: fewer fixations, shorter scan paths, faster. Graph: shorter fixations. Everyone spent more time searching than reading. |
| [Katifori et al. 2007](https://doi.org/10.1145/1287620.1287621) (survey) | — | — | Six families of ontology views | — | The indented list tends to win tests and works best with other views. Node-link clutters above about 200 nodes. Zoomable views lose track of the level. Space-filling views are weak for structure. Pair any view with search. |
| [Yee et al. 2003](http://flamenco.berkeley.edu/papers/flamenco-chi03.pdf) | 32 art students | About 35,000 images, hierarchical facets | Faceted interface vs keyword search | Explore, find all items of a kind, compare | Faceted interface preferred overall by 29 of 32. Found 77% vs 21% of the items in one task. 26 vs 82 empty result pages. |
| [Dumais et al. 2001](https://www.cs.ucdavis.edu/~hchen/paper/chi2001.pdf) | 76 adults | Top 100 web results per query | Grouped by category vs a list | Lookup | Grouped hits took 70–84 s against 96–105 s for lists. A label on each hit did not help. An item that fits two categories was harder to find. |

Limits of the evidence:

- **Small samples.** Most studies had 12 to 48 people, mostly students.
- **Data unlike a vocabulary.** Many studies used file systems, synthetic trees or images. Only Kobsa, Plaisant, Woodburn and Fu used concept hierarchies.
- **No text in some studies.** Barlow and Burch showed no labels at all, so their radial results are about seeing structure, not reading names.
- **No direct comparison with this explorer.** No study compares search plus an outline with a zoomable sunburst for finding a named concept.

On labels and rotation:

- **Rotated text.** Within 45°, there was almost no cost. At 90°, words took about 26% longer and phrases 44–68% longer. Upside-down phrases took about twice as long. The study used a tabletop screen and common words ([Wigdor & Balakrishnan 2005](https://www.dgp.toronto.edu/public_user/ravin/papers/ecscw2005_textorientation.pdf)). The explorer flips labels on the left half (`labelTransform`, `site/template.html` line 655), so each label is within 90° of horizontal. Labels near the top and bottom of the circle are still close to vertical.
- **Readable or hidden.** The SpaceTree designers dropped an early design that shrank nodes smoothly. Users rejected it because only one level was ever readable ([Plaisant et al. 2002](https://obj.umiacs.umd.edu/spacetree/2002-05.pdf), p. 4).
- **Few readable labels.** In Stasko's sunburst, users zoomed in when slices were too small to read, and asked for names on hover and for search that highlights the hit ([Stasko et al. 2000](https://faculty.cc.gatech.edu/~stasko/papers/ijhcs00.pdf), pp. 686–689).

On multiple parents and cross-cutting tags:

- **Trees repeat concepts.** The Protégé tree repeats a class under each parent, and users found this confusing ([Fu et al. 2013](https://link.springer.com/content/pdf/10.1007/978-3-642-41335-3_8.pdf), p. 131).
- **Show all the parents.** The survey recommends marking concepts that have several parents, and showing all of them ([Katifori et al. 2007](https://doi.org/10.1145/1287620.1287621)). The explorer's 5W1H view repeats concepts in the same way as the Protégé tree. A concept with two tags appears under both, with faded parents for the path.
- **Facets suit several kinds of category.** Hearst argues that one hierarchy cannot hold several kinds of category. Her answer is a hierarchy for each facet, with any number of labels per item. Her guidance for such interfaces ([Hearst 2006](http://flamenco.berkeley.edu/papers/cacm06.pdf), [Hearst 2009, ch. 8](https://searchuserinterfaces.com/book/sui_ch8_navigation_and_search.html)):
  - show a count next to each value;
  - hide choices that would give no results;
  - keep a separate breadcrumb for each facet;
  - show the next level of a facet hierarchy plus the trail above it.

## 3. What the sunburst costs, and the alternatives

### SVG, Canvas and WebGL at 1,000–2,000 marks

- **SVG.** Each arc and each label is a DOM element.
  - Lighthouse warns when a page body has more than about 800 nodes, and flags an error above about 1,400. A large DOM makes style and layout work slower ([Chrome: DOM size](https://developer.chrome.com/docs/lighthouse/performance/dom-size)).
  - Layout cost grows with the size of the DOM. In web.dev's example, a page of 1,618 elements spent over 28 ms on layout per frame. The budget at 60 Hz is about 16 ms ([web.dev: layout](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing)).
  - The page's own code should finish in about 10 ms of each 16.7 ms frame ([web.dev: rendering performance](https://web.dev/articles/rendering-performance)).
- **Canvas.** One element is drawn by script.
  - `d3.arc()` draws to a canvas context with `arc.context(ctx)`. Without a context, it returns an SVG path string. So the same layout code can draw either way ([d3-shape arc](https://d3js.org/d3-shape/arc)).
  - MDN's canvas advice: redraw only what changed, layer several canvases, avoid drawing text where possible, and scale for `devicePixelRatio` ([MDN: optimizing canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas)).
  - A canvas is a bitmap. Screen readers cannot see what is drawn on it, so a canvas view needs an accessible version alongside ([MDN: canvas](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/canvas)).
- **Library thresholds.** ECharts suggests canvas above about 1,000 elements, and SVG for low memory on phones ([ECharts: canvas vs SVG](https://echarts.apache.org/handbook/en/best-practices/canvas-vs-svg/)). It also turns off animation by default above 2,000 graphic elements (`animationThreshold`, [ECharts sunburst options](https://echarts.apache.org/en/llms-documents/option-parts/option.series-sunburst.md)).
- **What researchers found.** Woodburn et al. found D3 animations stopped responding above about 800 to 1,000 elements, so they moved to WebGL. This is their report, not a measured benchmark ([Woodburn et al. 2019](https://arxiv.org/pdf/1908.01277), p. 3).
- **WebGL.** WebGL is fastest when many shapes go in a few batched draw calls ([MDN: WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)). It has no built-in text, so labels need extra work. In Cytoscape.js's own test, a graph of about 1,200 nodes and 16,000 edges ran at about 20 frames a second on canvas and over 100 with WebGL ([Cytoscape.js blog](https://blog.js.cytoscape.org/2025/01/13/webgl-preview/)). That graph has far more marks than a sunburst of 1,100 arcs.

### The cost of animating every mark

- **D3 transitions share one clock.** d3-timer runs all transitions from a single `requestAnimationFrame` loop, in the same frame ([d3-timer](https://d3js.org/d3-timer)). Each `attrTween` runs once per element per frame. So the work in each frame grows with the number of elements in the transition.
- **Only `transform` and `opacity` skip layout and paint**, and only for elements on their own compositor layer ([web.dev: compositor-only properties](https://web.dev/articles/stick-to-compositor-only-properties-and-manage-layer-count)). Changing an SVG path's `d` changes its shape. My inference is that every frame must then repaint the SVG.

### The cost of measuring text during animation

- **Reading layout after a write forces a layout.** If code reads a layout value after it changes styles, the browser must run layout at once. Doing that in a loop runs layout again and again ([web.dev: layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing)).
- **Text measurement depends on the font and the text.** SVG's `getComputedTextLength()` and canvas's `measureText()` both return a measured width ([MDN getComputedTextLength](https://developer.mozilla.org/en-US/docs/Web/API/SVGTextContentElement/getComputedTextLength), [MDN measureText](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/measureText)).
- **The explorer does not measure text.** `fitText` (`site/template.html` lines 659–663) estimates 6.3 units per character. So text measurement is not a cost here. But the estimate can cut a label too early, or let it overflow.

### Likely hotspots in this code

These are hypotheses from reading `site/template.html`, not measurements. The DOM counts come from the live page.

On the live page, at a 1,024 px window, the page has 2,449 elements. The chart holds 1,073 `path` and 1,075 `text` elements. At the start, 940 arcs show, but only 45 labels do.

1. **Every node stays in the DOM** (`bind()`, lines 666–681). There is one `path` and one `text` per node, whether it shows or not. Hidden ones get `fill-opacity` 0. In the 5W1H view, that would be about 1,466 of each.
2. **Every node is interpolated on every frame** of the 640 ms zoom (`applyVisibility()`, lines 721–744).
   - The `tween('data')` at line 735 runs for all nodes, before the visibility filter.
   - The ring width also animates (line 726). So every visible arc changes shape on every frame, and `arc()` rebuilds its path string (line 739).
   - The visible labels get a new `transform` on every frame (line 742).
3. **All labels are rewritten at the start of each zoom.** `label.text(fitText)` (line 740) runs on every label, hidden ones included.
4. **Hover touches every arc.**
   - `pointerenter` (line 670) calls `highlight()`. That sets `opacity` on every path, and walks each path's ancestors (line 799).
   - The CSS `transition: opacity 140ms` on every arc (line 154) then animates up to about 1,000 paths at once.
   - The same hover rebuilds the side panel (`renderPanel`, line 1119), which can change the page layout.
5. **The tooltip may force a layout on each mouse move.** `moveTip()` (lines 825–832) reads `getBoundingClientRect()` and `offsetWidth`. The previous call wrote the tooltip's position.
6. **Selection rewrites every arc.** `markSelected()` (lines 780–783) sets the stroke on every path and moves the selected one in the DOM with `raise()`.
7. **The page itself is heavy.** `site/index.html` is about 1.2 MB, with the data inline. A phone must parse all of it before it can draw.
8. **Labels are tiny on small screens.** Labels are 11.5 units in an 820-unit `viewBox`. At a 1,024 px window, the chart was 551 px wide, so labels were about 7.7 px. At 375 px, the chart was 341 px wide, so labels were about 4.8 px. It started about 1,380 px down the page.

To test these hypotheses, the Chrome DevTools Performance panel can record a zoom and a hover with the CPU slowed 4×. That roughly matches a mobile device. The panel also flags forced reflows ([DevTools: performance](https://developer.chrome.com/docs/devtools/performance)). For clicks and key presses, Google treats an Interaction to Next Paint of 200 ms or less as good ([web.dev: INP](https://web.dev/articles/inp)).

### Techniques

- **Keep only visible nodes in the DOM.** With the default 3 rings, about 940 of 1,073 arcs show, but only 45 labels. Creating text only for labels that show would remove most `text` elements. This is my reading of the counts above.
- **Animate only what moves.** Interpolate only the nodes visible before or after the zoom. The code already filters `attrTween('d')` this way, but not `tween('data')`. Shorter or no animation is also an option: ECharts turns animation off above 2,000 elements ([ECharts options](https://echarts.apache.org/en/llms-documents/option-parts/option.series-sunburst.md)).
- **Draw on canvas and hit-test.**
  - Draw arcs with `d3.arc().context(ctx)` ([d3-shape arc](https://d3js.org/d3-shape/arc)).
  - Find the arc under the pointer with `isPointInPath` and a `Path2D` ([MDN isPointInPath](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/isPointInPath)). For a partition layout, the angle and radius of the pointer also identify the node directly. That is my derivation from the `x0`/`x1`/`y0`/`y1` layout, not a cited claim.
  - Keep an accessible list or tree next to the canvas ([MDN: canvas](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/canvas)).
- **Virtualise lists and trees.**
  - Render only the rows in view ([web.dev: virtualise lists](https://web.dev/articles/virtualize-long-lists-react-window)).
  - Or let the browser skip off-screen parts with `content-visibility: auto`. web.dev reports a 7× faster first render in one example ([web.dev: content-visibility](https://web.dev/articles/content-visibility)).
  - A virtual tree must tell screen readers each row's depth and position with `aria-level`, `aria-setsize` and `aria-posinset` ([WAI-ARIA tree view pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)).
  - At 1,118 concepts, a tree collapsed by default shows 16 rows. Fully open, 1,118 rows of a few elements each would pass the Lighthouse error level. So a full outline needs collapsing or virtualising. This is my estimate, not a measurement.
- **Batch reads before writes**, for the tooltip and the panel ([web.dev: layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing)).

## 4. Libraries that fit a static page with no build step

Sizes are the minified file as served by the CDN, before compression. I measured them on 23 November 2026.

| Library | Version, licence | What it gives | Trade-off | Size |
|---|---|---|---|---|
| [D3](https://d3js.org/d3-shape/arc) (already loaded) | 7.9.0 on cdnjs (7.9.2 on npm), ISC | `d3.partition` gives both icicle and sunburst ([d3-hierarchy partition](https://d3js.org/d3-hierarchy/partition)). `d3.arc` draws to SVG or canvas. | Nothing new to load. But hit-testing, labels, focus and accessibility are all hand-written. | about 280 KB |
| [Apache ECharts](https://echarts.apache.org/handbook/en/best-practices/canvas-vs-svg/) | 6.1.0, Apache-2.0 | Sunburst, tree and treemap series. Canvas or SVG renderer. Click-to-zoom (`nodeClick: 'rootToNode'`). Radial or tangential labels. Highlights a node's ancestors or descendants. | Large file. Its ARIA support writes a description of the chart and adds patterns ([ECharts ARIA](https://echarts.apache.org/handbook/en/best-practices/aria/)); the docs do not say that single arcs can take keyboard focus. Styling goes through its own option system. | about 1.1 MB (full build) |
| [sunburst-chart](https://github.com/vasturiano/sunburst-chart) | 1.21.5, MIT | A ready-made D3 sunburst with click-to-zoom. Labels are hidden or cut when they do not fit, and can be angular or radial. Loads with one script tag. | Still SVG, so the DOM cost stays the same. | not measured |
| [Wunderbaum](https://github.com/mar10/wunderbaum) | 0.15.0, MIT | A tree and treegrid with no dependencies. Only visible rows exist in the DOM. Has ARIA treegrid roles with level, set size and position. Filtering, keyboard use, lazy loading. UMD and ESM builds on jsDelivr ([llms.txt](https://github.com/mar10/wunderbaum/blob/main/docs/llms.txt), [keyboard and ARIA](https://github.com/mar10/wunderbaum/blob/main/docs/tutorial/tutorial_keyboard.md)). | In beta: the API, markup and styles may still change ([docs](https://mar10.github.io/wunderbaum/)). | about 107 KB |
| [Web Awesome tree](https://webawesome.com/docs/components/tree) (successor of [Shoelace](https://shoelace.style/components/tree)) | 3.15.0 | A `<wa-tree>` web component with lazy children and selection modes | Its docs load it from Web Awesome's own CDN, which is not cdnjs, jsDelivr or unpkg. The docs do not say it renders only visible rows. Shoelace is no longer developed. | not measured |
| [MiniSearch](https://github.com/lucaong/minisearch) | 7.2.0, MIT | In-memory full-text search with prefix and fuzzy matching, field boosts (for example labels above definitions), and suggestions. A UMD script on jsDelivr. | The index is built in the browser on load, which takes time on a phone. | about 19 KB |
| [Fuse.js](https://www.fusejs.io/) | 7.5.0, Apache-2.0 | Fuzzy search over fields, with no dependencies | Fuzzy only. It has no full-text index or prefix ranking like MiniSearch. | about 8.6 KB gzip (stated) |
| [Cytoscape.js](https://github.com/cytoscape/cytoscape.js) | 3.35.0, MIT | Graph drawing on canvas, with a WebGL preview since 3.31 ([blog](https://blog.js.cytoscape.org/2025/01/13/webgl-preview/)) | Only useful for a graph view, for example a concept's neighbours, multiple parents or mappings. Large. | about 443 KB |

Not on the list:

- **TanStack Virtual.** Its introduction page lists framework adapters but does not document use without a build step ([TanStack Virtual](https://tanstack.com/virtual/latest/docs/introduction)).
- **A tree with no library.** Plain HTML with the ARIA tree view pattern needs no library at all ([WAI-ARIA tree view](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)).

## Options and trade-offs

Each option is a direction, not a decision. They can be combined.

| Option | What the evidence says for it | What it says against it | Rough cost |
|---|---|---|---|
| **A. Keep the sunburst, make it cheaper.** Draw on canvas with the same `d3.partition` and `d3.arc`. Create labels only where they show. Animate only what moves. | Keeps the overview of 16 branches and the look. Sunburst beat the treemap and was well liked ([Stasko 2000](https://faculty.cc.gatech.edu/~stasko/papers/ijhcs00.pdf)). Canvas is the documented answer above about 1,000 elements. | Radial layouts are slower for structure tasks ([Burch 2011](https://doi.org/10.1109/TVCG.2011.193)). Labels are rotated and few fit. On a phone they are about 5 px. Canvas needs an accessible version alongside. | Medium: rewrite the drawing and hit-testing. The data code stays. |
| **B. Switch the map to an icicle.** Same partition data, laid out in straight rows or columns. | As fast as the radial form, and preferred ([Woodburn 2019](https://arxiv.org/pdf/1908.01277), [Barlow & Neville 2001](https://courses.ischool.berkeley.edu/i247/s02/readings/barlow.pdf)). Labels can all be horizontal ([McGuffin & Robert 2010](http://profs.etsmtl.ca/mmcguffin/research/treeRepEfficiency/treeRepEfficiency.pdf)). | Leaves get less room than in a sunburst. It needs width, or a vertical layout on phones. It still shows few names at once. | Medium. Same data, new geometry. |
| **C. Make search plus a tree or columns the main view, with one page per concept.** | This is what every vocabulary browser checked does. Trees are best for finding a named item ([Kobsa 2004](https://ics.uci.edu/~kobsa/papers/2004-InfoVis-kobsa.pdf), [Fu 2013](https://link.springer.com/content/pdf/10.1007/978-3-642-41335-3_8.pdf)). Multi-pane browsing beat expand/collapse on a heavy browsing task ([Chimera & Shneiderman 1994](https://doi.org/10.1145/185462.185483)). It works on a phone. | Weak for overview and branch size ([Plaisant 2002](https://obj.umiacs.umd.edu/spacetree/2002-05.pdf)). Repeating a concept under each tag can confuse ([Fu 2013](https://link.springer.com/content/pdf/10.1007/978-3-642-41335-3_8.pdf)). It looks like other tools. | Low to medium. The columns view exists already. |
| **D. Make 5W1H and the standards into facets with counts, and group search hits by branch.** | Facets with counts were preferred overall and found more ([Yee 2003](http://flamenco.berkeley.edu/papers/flamenco-chi03.pdf)). Grouped hits were faster ([Dumais 2001](https://www.cs.ucdavis.edu/~hchen/paper/chi2001.pdf)). The browsers checked show categories this way. | Tested on images and web pages, not concepts. Counts for a concept with two tags need a clear rule: primary tag only, or any tag. | Low. Works with A, B or C. |
| **E. Add a local graph as a second view.** One concept with its parents, children, tags and mappings. | Users liked graphs for showing multiple parents ([Fu 2013](https://link.springer.com/content/pdf/10.1007/978-3-642-41335-3_8.pdf)). | Graphs clutter above about 200 nodes ([Katifori 2007](https://doi.org/10.1145/1287620.1287621)), so only a neighbourhood works. A force layout changes each session ([Lohmann 2016](https://semantic-web-journal.net/system/files/swj1114.pdf)). | Medium. Needs a graph library or hand-written code. |

Questions the evidence cannot settle, for the interview:

- **What is the main task?** Is it finding a named concept, getting an overview, or comparing tags and standards? The best view changes with the task.
- **Who are the main users?** Are they people new to the taxonomy, experts who check and edit it, or developers of AI agents?
- **How much do phones matter?**
- **Is the sunburst part of the brand?** If so, is it part of the overview page only, or of the daily tool too?

## Sources

### Vocabulary browsers (visited 23 November 2026)

- UNESCO Thesaurus (Skosmos): [landing page](https://vocabularies.unesco.org/browser/thesaurus/en/), [concept page](https://vocabularies.unesco.org/unesco/en/page?uri=http%3A%2F%2Fvocabularies.unesco.org%2Fthesaurus%2Fconcept269), [search](https://vocabularies.unesco.org/unesco/en/search?q=cultural+heritage&clang=en&anylang=on)
- Skosmos: [repository](https://github.com/NatLibFi/Skosmos), [3.0 release notes](https://github.com/NatLibFi/Skosmos/releases/tag/v3.0), [releases](https://github.com/NatLibFi/Skosmos/releases)
- Getty AAT: [hierarchy display](https://www.getty.edu/vow/AATHierarchy?find=&logic=AND&note=&subjectid=300000000), [search results](https://www.getty.edu/vow/AATServlet?english=Y&find=beams&logic=AND&page=1&note=), [full record](https://www.getty.edu/vow/AATFullDisplay?find=beams&logic=AND&note=&english=N&prev_page=1&subjectid=300001497), [About the AAT](https://www.getty.edu/research/tools/vocabularies/aat/about.html)
- NBS Uniclass: [search](https://uniclass.thenbs.com/search?query=beam&filter=status%3ACurrent), [table page](https://uniclass.thenbs.com/taxon/pr_25), [code page](https://uniclass.thenbs.com/taxon/pr_25_71_33_33)
- buildingSMART Data Dictionary: [search](https://search.bsdd.buildingsmart.org/?SearchText=beam&ShowPreview=true), [IfcBeam](https://search.bsdd.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcBeam)
- OntoPortal: [AgroPortal AGROVOC](https://agroportal.eu/ontologies/AGROVOC?p=classes), [OntoPortal documentation](https://ontoportal.github.io/documentation/)
- schema.org: [full hierarchy](https://schema.org/docs/full.html)
- WebVOWL: [repository](https://github.com/VisualDataWeb/WebVOWL)
- PoolParty: [help page](https://help.poolparty.biz/8.1/en/user-guide-for-knowledge-engineers/basic-features/additional-information-about-the-project-and-its-concepts/visualization-of-a-project.html) (not read in full)
- Aecoware Open Taxonomy: [live explorer](https://aecoware.github.io/aecxonomy/)

### Papers

- Barlow, T. & Neville, P. (2001). A comparison of 2-D visualizations of hierarchies. IEEE InfoVis. [doi:10.1109/INFVIS.2001.963290](https://doi.org/10.1109/INFVIS.2001.963290), [copy read](https://courses.ischool.berkeley.edu/i247/s02/readings/barlow.pdf)
- Burch, M. et al. (2011). Evaluation of traditional, orthogonal, and radial tree diagrams by an eye tracking study. IEEE TVCG 17(12). [doi:10.1109/TVCG.2011.193](https://doi.org/10.1109/TVCG.2011.193)
- Cawthon, N. & Vande Moere, A. (2007). The effect of aesthetic on the usability of data visualization. IV 2007. [doi:10.1109/IV.2007.147](https://doi.org/10.1109/IV.2007.147). Only the abstract was available: 285 people, 11 hierarchy views, and beauty linked to response time. It is not used above.
- Chimera, R. & Shneiderman, B. (1994). An exploratory evaluation of three interfaces for browsing large hierarchical tables of contents. ACM TOIS 12(4). [doi:10.1145/185462.185483](https://doi.org/10.1145/185462.185483)
- Dumais, S., Cutrell, E. & Chen, H. (2001). Optimizing search by showing results in context. CHI 2001. [doi:10.1145/365024.365116](https://doi.org/10.1145/365024.365116), [copy read](https://www.cs.ucdavis.edu/~hchen/paper/chi2001.pdf)
- English, J., Hearst, M. et al. (2002). Hierarchical faceted metadata in site search interfaces. CHI 2002 extended abstracts. [PDF](http://flamenco.berkeley.edu/papers/chi02_short_paper.pdf)
- Fu, B., Noy, N. & Storey, M.-A. (2013). Indented tree or graph? ISWC 2013. [Springer PDF](https://link.springer.com/content/pdf/10.1007/978-3-642-41335-3_8.pdf)
- Fu, B., Noy, N. & Storey, M.-A. (2017). Eye tracking the user experience. Semantic Web 8(1). [Accepted manuscript](https://www.semantic-web-journal.net/system/files/swj861_0.pdf)
- Goldberg, J. & Helfman, J. (2011). Reading values on linear versus radial graphs. Information Visualization 10(3). [doi:10.1177/1473871611406623](https://doi.org/10.1177/1473871611406623) (abstract only)
- Hearst, M. (2006). Clustering versus faceted categories for information exploration. CACM 49(4). [PDF](http://flamenco.berkeley.edu/papers/cacm06.pdf)
- Hearst, M. (2009). Search User Interfaces, chapter 8. [Online](https://searchuserinterfaces.com/book/sui_ch8_navigation_and_search.html)
- Katifori, A. et al. (2006). A comparative study of four ontology visualization techniques in Protégé. IV 2006. [doi:10.1109/IV.2006.3](https://doi.org/10.1109/IV.2006.3). Not read; known only through the 2007 survey.
- Katifori, A. et al. (2007). Ontology visualization methods — a survey. ACM Computing Surveys 39(4). [doi:10.1145/1287620.1287621](https://doi.org/10.1145/1287620.1287621)
- Kobsa, A. (2004). User experiments with tree visualization systems. IEEE InfoVis. [Author copy](https://ics.uci.edu/~kobsa/papers/2004-InfoVis-kobsa.pdf)
- Lohmann, S. et al. (2016). Visualizing ontologies with VOWL. Semantic Web 7(4). [doi:10.3233/SW-150200](https://doi.org/10.3233/SW-150200), [accepted version](https://semantic-web-journal.net/system/files/swj1114.pdf)
- McGuffin, M. & Robert, J.-M. (2010). Quantifying the space-efficiency of 2D graphical representations of trees. Information Visualization 9(2). [Author copy](http://profs.etsmtl.ca/mmcguffin/research/treeRepEfficiency/treeRepEfficiency.pdf)
- Plaisant, C., Grosjean, J. & Bederson, B. (2002). SpaceTree. IEEE InfoVis. [Author copy](https://obj.umiacs.umd.edu/spacetree/2002-05.pdf)
- schraefel, m.c., Karam, M. & Zhao, S. (2003). Listen to the music: audio preview cues for exploration of online music. INTERACT 2003. [Repository record](https://eprints.soton.ac.uk/258800/)
- Stasko, J. et al. (2000). An evaluation of space-filling information visualizations for depicting hierarchical structures. IJHCS 53(5). [doi:10.1006/ijhc.2000.0420](https://doi.org/10.1006/ijhc.2000.0420), [author copy](https://faculty.cc.gatech.edu/~stasko/papers/ijhcs00.pdf)
- Wigdor, D. & Balakrishnan, R. (2005). Empirical investigation into the effect of orientation on text readability in tabletop displays. ECSCW 2005. [Author copy](https://www.dgp.toronto.edu/public_user/ravin/papers/ecscw2005_textorientation.pdf)
- Woodburn, L., Yang, Y. & Marriott, K. (2019). Interactive visualisation of hierarchical quantitative data: an evaluation. IEEE VIS. [arXiv](https://arxiv.org/pdf/1908.01277)
- Zaphiris, P., Shneiderman, B. & Norman, K. (2002). Expandable indexes vs. sequential menus for searching hierarchies on the World Wide Web. Behaviour & Information Technology 21. [doi:10.1080/0144929021000009045](https://doi.org/10.1080/0144929021000009045). It found an expandable index slower than one page per level. It is not used above.

### Rendering and performance

- D3: [d3-shape arc](https://d3js.org/d3-shape/arc), [d3-hierarchy partition](https://d3js.org/d3-hierarchy/partition), [d3-timer](https://d3js.org/d3-timer), [d3-transition](https://d3js.org/d3-transition)
- MDN: [Optimizing canvas](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API/Tutorial/Optimizing_canvas), [canvas element](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/canvas), [isPointInPath](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/isPointInPath), [measureText](https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/measureText), [getComputedTextLength](https://developer.mozilla.org/en-US/docs/Web/API/SVGTextContentElement/getComputedTextLength), [WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- web.dev: [Rendering performance](https://web.dev/articles/rendering-performance), [Avoid large, complex layouts and layout thrashing](https://web.dev/articles/avoid-large-complex-layouts-and-layout-thrashing), [Compositor-only properties](https://web.dev/articles/stick-to-compositor-only-properties-and-manage-layer-count), [INP](https://web.dev/articles/inp), [Virtualize long lists](https://web.dev/articles/virtualize-long-lists-react-window), [content-visibility](https://web.dev/articles/content-visibility)
- Chrome: [Lighthouse DOM size](https://developer.chrome.com/docs/lighthouse/performance/dom-size), [DevTools performance](https://developer.chrome.com/docs/devtools/performance)
- W3C: [WAI-ARIA tree view pattern](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/)

### Libraries

- Apache ECharts: [canvas vs SVG](https://echarts.apache.org/handbook/en/best-practices/canvas-vs-svg/), [ARIA](https://echarts.apache.org/handbook/en/best-practices/aria/), [sunburst options](https://echarts.apache.org/en/llms-documents/option-parts/option.series-sunburst.md)
- [sunburst-chart](https://github.com/vasturiano/sunburst-chart)
- Wunderbaum: [repository](https://github.com/mar10/wunderbaum), [docs](https://mar10.github.io/wunderbaum/)
- [Web Awesome tree](https://webawesome.com/docs/components/tree), [Shoelace tree](https://shoelace.style/components/tree)
- [MiniSearch](https://github.com/lucaong/minisearch)
- [Fuse.js](https://www.fusejs.io/)
- Cytoscape.js: [repository](https://github.com/cytoscape/cytoscape.js), [WebGL preview](https://blog.js.cytoscape.org/2025/01/13/webgl-preview/)
- [TanStack Virtual](https://tanstack.com/virtual/latest/docs/introduction)
