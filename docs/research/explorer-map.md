# A better map of the taxonomy

The explorer's map is a zoomable SVG sunburst. The owner says it is laggy and hard to use, and wants a better map, not a page without one. This note asks how else to draw the taxonomy, and it goes with a prototype of four maps on the branch `prototype/explorer-map`. It builds on `docs/research/explorer-views.md`, which covers the classic studies, vocabulary browsers and rendering costs. Sources were visited on 24 November 2026.

## What is wrong with today's map

Measured on the built page at a 1,366 × 860 window, on a fast Mac. A phone is several times slower.

- **Too much to draw.** The page has about 2,470 elements. The chart alone has 1,073 arcs and 1,075 labels, all kept in the page whether they show or not.
- **Zooming moves everything.** Each frame of the zoom rebuilds the shape of every visible arc. That costs about 8.6 ms of script and layout per frame, before painting, out of a budget of 16.7 ms.
- **Few names show.** Only 43 of 1,073 labels show at the start. Labels run along the radius, and rotated text is slower to read ([Wigdor & Balakrishnan 2005](https://www.dgp.toronto.edu/public_user/ravin/papers/ecscw2005_textorientation.pdf)).
- **Labels shrink with the chart.** They are drawn in chart units, so they are about 5 px on a phone.
- **The wheel zooms the map.** Scrolling the page over the map zooms it instead.

## What the research says

**The icicle has the best evidence for finding things.**
- In a 14-person study, the icicle was among the most accurate and fastest at finding subtrees. Radial layouts and treemaps were the slowest, and the treemap was the least accurate ([Dang et al. 2017](https://ceur-ws.org/Vol-1947/paper05.pdf)).
- In a 12-person study, the icicle and a half-circle sunburst performed alike. The treemap was about twice as slow on one task (44 s against 20 s). People preferred the icicle, and the full sunburst came last in the pilot ([Woodburn et al. 2019](https://arxiv.org/pdf/1908.01277)).

**A tree that opens one path is best at showing where a concept sits.**
- SpaceTree did best at listing ancestors and at finding the biggest branch ([Plaisant et al. 2002](https://obj.umiacs.umd.edu/spacetree/2002-05.pdf)).
- Degree-of-interest trees keep the open path and hide the rest, and they scale to very large trees ([Card & Nation 2002](https://doi.org/10.1145/1556262.1556300), [Heer & Card 2004](https://homes.cs.washington.edu/~jheer/files/2004-DOITree-AVI.pdf)).
- People traced structure faster in a top-down tree than in a radial one (about 12 s against 21 s, [Burch et al. 2011](https://doi.org/10.1109/TVCG.2011.193)).

**Maps that look like maps are remembered.**
- People recalled map-like designs better, and still did days later ([Saket et al. 2015](https://cns.iu.edu/docs/publications/2015-saket-recall.pdf)).
- They also rated them more enjoyable ([Saket et al. 2016](https://diglib.eg.org/handle/10.1111/cgf12880)).
- But a Voronoi treemap is still a treemap, and treemaps are weak for structure tasks. The only test of Voronoi treemaps is one IBM report ([DVT](https://dominoweb.draco.res.ibm.com/reports/rc25132.pdf)).

**Circle packing has no task studies.**
- It is a containment layout, like the treemaps that did worst in the Dang study.
- D3's own example labels only the focus's children ([zoomable circle packing](https://observablehq.com/@d3/zoomable-circle-packing)).

**Zoom animation helps, if it is short and moves everything together.**
- Animated zoom made people about twice as fast, with fewer errors, and short animations worked as well as long ones ([Shanmugasundaram & Irani 2008](https://hci.cs.umanitoba.ca/publications/details/the-effect-of-animated-transitions-in-zooming-interfaces)).
- Easing in and out beat other pacings ([Dragicevic 2011](https://hal.archives-ouvertes.fr/inria-00556177v2)).
- Starting elements at different times did not help ([Chevalier 2014](https://hal.archives-ouvertes.fr/hal-01054408v1)).

**Labels should be horizontal and shown only where they fit.**
- D3's icicle shows a label only when its band is at least 16 px tall ([zoomable icicle](https://observablehq.com/@d3/zoomable-icicle)).
- A 24 × 24 px tap target ([WCAG 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)) leaves room for about 330 cells on a phone. So no phone map can show all 1,073 concepts at once, and each map has to open by zooming.

Ruled out for this taxonomy:
- **Radial tidy tree.** All 920 leaf labels need a radius of about 1,760 px.
- **Hyperbolic tree.** It was slower when the target was hard to guess ([Pirolli et al. 2003](https://doi.org/10.1145/606658.606660)).
- **Fisheye views.** Distortion likely hurts size judgements and makes targets hard to hit ([Cockburn et al. 2008](https://www.microsoft.com/en-us/research/wp-content/uploads/2008/01/cockburn-ComputingSurveys09.pdf)).

## The four maps first prototyped

All four draw on a canvas. They draw only what shows, keep labels at 12–14 px on every screen, and leave the mouse wheel to the page. The rest of the page stays today's: groupings, colour switch, filters, search, zoom path, side panel and keyboard.

| Key | Map | How it opens | Labels | Why it is here |
|---|---|---|---|---|
| `?variant=A` | **Sunburst, redrawn** | Click to zoom, click the centre to go up, rings 2–4 | Horizontal where the arc is wide enough, along the radius otherwise, measured, never upside down | Today's look, without the lag. The baseline. |
| `?variant=B` | **Icicle** | Click to zoom, click the left column to go up | All horizontal. Every child of the focus gets at least 20 px (30 px on a phone), so all of them are named. | Best evidence for finding things and comparing sizes |
| `?variant=C` | **SpaceTree** | Click to open, click again to close. Only the path to the focus is open; a closed concept shows a wedge as big as what is under it. | All horizontal and full size | Best for "where does this sit" and for parents |
| `?variant=D` | **Territory map** (Voronoi treemap in a circle) | Click a region to zoom in, click outside the circle to go up. Two levels at a time. | Region names wrapped to the cell, district names where they fit | Map-like and memorable: branch size reads as land area |

Measured on the same machine:
- Each canvas map page has about 330 elements, against about 2,470 today.
- A full redraw of a map, plus the side panel, takes 0.6–1.7 ms.
- The territory map loads `d3-voronoi-treemap` 1.1.2 and its two helper libraries from jsDelivr, only when that map is chosen. A Spaces layout took about 17 ms.

## How to judge

Do each task on a desktop and on a phone, in each map. Count the wrong turns, and say which map you would want to look at.

1. Name the three biggest branches.
2. Say what's under Spaces.
3. Show where Fire compartment sits.
4. Name the parent of Notice to proceed. (It is Milestones, under Events and risks, not under Phases.)
5. Say which branch has the most When concepts. Use the 5W1H colour or the When filter.

## Run it

```bash
python3 scripts/build_site.py
python3 -m http.server 8781 --bind 127.0.0.1 --directory site
```

Open <http://127.0.0.1:8781/>. The Map switch above the chart picks Icicle, Sunburst or Territory. `?map=sunburst` or `?map=territory` in a link opens that map. The build needs `rdflib` and `pyshacl`.

The four maps as first built, with `?variant=A` to `D` and a yellow switcher bar, are in commit 5c9596b on this branch.

## Open questions

- **ADR 0002 has to change.** It said the map was dropped. The owner wants it kept and improved. Resolved: `docs/adr/0002-icicle-map.md` now records the icicle map.
- **Accessibility.** A canvas map needs a matching list or tree for screen readers. None of the four has one yet.
- **More to add.** The research also suggests a branch × 5W1H table beside the map, and an UpSet chart for overlaps between standard sets. Neither is built.

## Verdict

The owner chose on 24 November 2026:

- **The icicle is the main map**, and the explorer opens on it. It has the best evidence for finding things and comparing sizes. Every label is horizontal, and every child of the focus is named.
- **The sunburst and the territory map stay as options**, for fun. A Map switch above the chart offers Icicle, then Sunburst, then Territory, and the page remembers the choice. The sunburst is the canvas version, not today's SVG.
- **The SpaceTree is dropped.**

The prototype now works that way. The old SVG sunburst code is still in `site/template.html`, but nothing draws it. A real build should remove it, and should rewrite the three maps properly rather than reuse the prototype code.
