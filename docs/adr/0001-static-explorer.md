# The explorer is a static site, with a page for each concept

The explorer is plain files that `scripts/build_site.py` writes from the taxonomy and GitHub Pages serves. Scripts load from a CDN. There is no npm, bundler or server, so anyone can fork the open data and rebuild the site with Python alone. The build also writes one small HTML page for each concept, and a concept's w3id IRI sends a browser to that page. A link then opens one concept quickly, on a phone, for search engines, and for agents that do not run JavaScript.

## Considered options

- **A JavaScript framework with a build step.** Rejected: it adds a second toolchain to a data project, for a page that a static build can make.
- **IRIs keep resolving to the explorer** (`#aeco-01008`). Rejected: a browser loads every concept to show one.

## Consequences

- The w3id redirect rule for browsers must change from the explorer's `#code` address to the concept page. This needs a pull request to the w3id repository.
- Each build writes about 1,100 more files.
