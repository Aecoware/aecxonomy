# The explorer leads with search and the branch list, not a chart

The explorer used to open on a zoomable sunburst of every concept. It was slow, and people found it hard to use. We dropped it. The first screen is now a search box and the list of branches with their counts, and the main people we serve are practitioners who look up one concept. The research in `docs/research/explorer-views.md` found that radial layouts are slower for structure tasks, that rotated labels are slower to read, and that no established vocabulary browser leads with a chart.

## Considered options

- **Keep the sunburst and draw it on a canvas.** Rejected for now: it fixes the lag but not the lookup task, and its labels stay rotated and tiny on a phone.
- **An icicle chart as an overview page.** Not in the first version. Add one only if people miss an overview.

## Consequences

- The colour switch and the rings control go with the sunburst.
- Maintainers find gaps with the "No mapping yet" value of the outside-standard filter, instead of the Standards grouping.
