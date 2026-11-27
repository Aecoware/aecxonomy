# The explorer opens on an icicle map drawn on a canvas

The explorer's map was a zoomable SVG sunburst. It kept every arc and label in the page and reshaped them all on every frame of a zoom, so it was slow, and its rotated labels were hard to read and tiny on a phone. We keep a map and make it better. The explorer opens on an icicle: every label is horizontal and every child of the focus is named, and the icicle has the best evidence for finding concepts and comparing branch sizes. A Map switch also offers the sunburst and a territory map (a Voronoi treemap in a circle). All three draw on a canvas and draw only what shows. The evidence and the measurements are in `docs/research/explorer-map.md` and `docs/research/explorer-views.md`.

## Considered options

- **Search first, with no map.** Rejected: the map is the point of the explorer. Search and concept pages serve lookup beside it.
- **Tune the SVG sunburst.** Rejected: it would still keep about 2,150 elements in the page, and its labels would still be rotated.
- **SpaceTree**, a tree that opens one path at a time. Prototyped and not kept.

## Consequences

- The old SVG sunburst code goes. The three maps are written new, not copied from the prototype on `prototype/explorer-map`.
- A canvas is invisible to screen readers, so an ARIA tree beside it mirrors the map's focus, and arrow keys move through it.
- The territory map loads `d3-voronoi-treemap` 1.1.2, `d3-voronoi-map` 2.1.1 and `d3-weighted-voronoi` 1.1.3 from jsDelivr, pinned, and only when it is chosen. It is optional, so it can go if they break.
