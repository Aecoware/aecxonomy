# Prototype: explorer layouts (throwaway)

This branch, `prototype/explorer-layouts`, is never merged. It answers one question: **which layout should the new explorer use to show the tree of branches?**

The three layouts sit on the real explorer page, `site/template.html`, behind `?variant=`. A yellow bar at the bottom switches between them with ← and →, and so do the arrow keys when focus is outside a text box, the outline or the columns. Without `?variant=` the page is today's explorer.

| Key | Layout | How the tree shows | Filters | Concept |
|---|---|---|---|---|
| `?variant=A` | Outline | A collapsible ARIA tree beside the concept. A short list of filter matches opens the tree down to each one. | Three rows of chips, as today. One button on a phone. | Beside the tree. On a phone, a full-screen sheet, with a bar at the bottom for a selected branch. |
| `?variant=B` | Columns | Columns as the main layout, with the concept as the last column. On a phone, one column at a time with a back button and a path. | A compact strip of three menus. | The last column. On a phone, its own step. |
| `?variant=C` | Search-first | No tree. The home page lists the branches as cards. Typing shows a results page, with hits grouped by branch. | A side bar of checkboxes. One button on a phone. | Its own in-page page with a breadcrumb. Narrower, siblings and related sit beside it. The hero shows on the home page only. |

**The map stays.** Each layout has two tabs in the header, as today's Map and Columns tabs: the layout's own (Outline, Columns or List) and Map. Map shows today's sunburst, with its zoom path, colour switch and rings. It uses the layout's filters, which dim the arcs outside them, and the layout's concept. A click in the map picks the concept, and picking a concept elsewhere zooms the map to it. Add `&map=1` to the address to open a layout on its Map tab; the yellow bar keeps it.

- A: the map takes the outline's place, with the concept beside it. On a phone, the bar at the bottom or the sheet opens the concept.
- B: the map takes the columns' place, with the concept beside it. On a phone, a card under the map opens the concept as a step.
- C: the map takes the place of the pages, with a card for the concept picked in it. The card opens the concept's page. Typing a search goes back to the pages.

## Run it

```bash
python3 scripts/build_site.py
python3 -m http.server 8781 --bind 127.0.0.1 --directory site
```

Then open <http://127.0.0.1:8781/?variant=A>, or <http://127.0.0.1:8781/?variant=A&map=1> for the Map tab. The build needs `rdflib` and `pyshacl` (`python3 -m pip install --user rdflib pyshacl`).

## The five tasks

Do each on a desktop and at 375 px wide, in each layout. Count the wrong turns.

1. Find "fire compartment".
2. Say what's under Spaces.
3. Find the When concepts that have Uniclass mappings. (8 on this branch.)
4. Copy the IRI of Beam.
5. Name the parent of Notice to proceed. (Milestones, under Events and risks, not under Phases.)

## Choices made in the prototype

- The user wants the sunburst kept (24 November 2026). `docs/adr/0002-search-first-no-chart.md` on `explorer-redesign` says it was dropped, so that ADR needs changing. The map is kept as it is today; its lag is not fixed here.
- The three filters are shared by all layouts. A concept counts under every value it has: any value inside one filter, every filter across them. The count beside a value assumes the other two filters as set.
- Search keeps today's matching. Hits outside the filters are left out, and a line says how many, for example "2 more outside your filters".
- Mappings always show, so the "Plug in linked standards" button and "Exact matches only" are gone. The concept drops "Kind (draft)" and "Places in this view", which belonged to the dropped groupings. It adds siblings.
- ADA is in the standard-set filter, but no concept on this branch applies under it, so it shows 0.

## Verdict

To fill in after the user and two or three practitioners have done the tasks: which layout, why, and which parts come from the others.
