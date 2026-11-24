"""Steps the explorer tests share: waiting for the data, searching, reading and clicking the map, and the tree."""
from playwright.sync_api import expect

CANVAS = "#chart canvas"
NARROW_MAP = 520  # Below this width the map works as on a phone.


def expect_loaded(page, taxonomy):
    expect(page.locator("#st-concepts")).to_have_text(f"{len(taxonomy):,}")


def open_concept(page, code, search_for=None):
    page.get_by_role("searchbox").fill(search_for or code)
    page.get_by_role("option").filter(has_text=code).click()


def frame(page):
    """The map's report of its last drawn frame, once the zoom has settled and the web fonts are in."""
    page.wait_for_function("window.explorerMap && !explorerMap.lastFrame().moving")
    return page.evaluate("document.fonts.ready.then(() => explorerMap.lastFrame())")


def cell(page, code):
    """The drawn cell of a concept, by its code."""
    return next(c for c in frame(page)["cells"] if c["code"] == code)


def centre(c):
    """The middle of a drawn cell, as a position on the canvas."""
    return {"x": c["x"] + c["w"] / 2, "y": c["y"] + c["h"] / 2}


def click_cell(page, c):
    page.locator(CANVAS).click(position=centre(c))


def narrow(page):
    return page.locator(CANVAS).bounding_box()["width"] < NARROW_MAP


def children(taxonomy, code):
    """The codes of a concept's children. The branches are the children of ""."""
    return [k for k, c in taxonomy.items() if c["parent"] == code]


def concepts_under(taxonomy, code):
    """How many concepts a concept holds, itself included."""
    return 1 + sum(concepts_under(taxonomy, k) for k in children(taxonomy, code))
