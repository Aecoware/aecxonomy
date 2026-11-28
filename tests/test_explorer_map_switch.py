"""The Map switch: which map type opens, how a pick is written to the address and kept, and what a switch keeps."""
from playwright.sync_api import expect

from explorer import code_of, expect_loaded, frame, open_map, wait_for_map_type


def switch(page):
    return page.get_by_role("group", name="Map")


def test_the_map_switch_offers_icicle_sunburst_and_territory_and_the_explorer_opens_on_the_icicle(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    expect(switch(page).get_by_role("button")).to_have_text(["Icicle", "Sunburst", "Territory"])
    expect(switch(page).locator("[aria-pressed=true]")).to_have_text("Icicle")
    assert frame(page)["map"] == "icicle"


def test_a_link_picks_the_map_type_and_an_unknown_one_is_ignored(page, taxonomy):
    page.goto("/?map=sunburst")
    expect_loaded(page, taxonomy)
    assert frame(page)["map"] == "sunburst"
    expect(switch(page).locator("[aria-pressed=true]")).to_have_text("Sunburst")
    open_map(page, taxonomy, "territory")
    page.goto("/?map=treemap")
    expect_loaded(page, taxonomy)
    assert frame(page)["map"] == "icicle"
    expect(switch(page).locator("[aria-pressed=true]")).to_have_text("Icicle")


def pick(page, map_type):
    switch(page).get_by_role("button", name=map_type).click()


def test_the_last_map_type_picked_is_remembered_and_a_link_wins_over_it(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    pick(page, "Sunburst")
    page.goto("/")
    expect_loaded(page, taxonomy)
    assert frame(page)["map"] == "sunburst"
    assert page.evaluate("location.search") == "?map=sunburst"  # so a link copied from the page opens the sunburst
    page.goto("/?map=icicle")
    expect_loaded(page, taxonomy)
    assert frame(page)["map"] == "icicle"


def test_picking_a_map_type_updates_the_address_in_place_and_the_hint(page, taxonomy):
    spaces = code_of(taxonomy, "Spaces")
    page.goto(f"/#{spaces}")
    expect_loaded(page, taxonomy)
    entries = page.evaluate("history.length")
    pick(page, "Sunburst")
    assert page.evaluate("[location.search, location.hash, history.length]") == ["?map=sunburst", f"#{spaces}", entries]
    expect(page.locator(".hint")).to_contain_text("Click the centre to go up")
    pick(page, "Icicle")
    assert page.evaluate("[location.search, location.hash, history.length]") == ["", f"#{spaces}", entries]
    expect(page.locator(".hint")).to_contain_text("Click the left column to go up")


def test_switching_the_map_type_keeps_the_focus_and_the_selection(page, taxonomy):
    ntp = code_of(taxonomy, "Notice to proceed")
    page.goto(f"/#{ntp}")
    expect_loaded(page, taxonomy)
    for map_type in ("Sunburst", "Icicle"):
        pick(page, map_type)
        f = frame(page)
        assert (f["map"], f["focus"], f["selected"]) == (map_type.lower(), taxonomy[ntp]["parent"], ntp)
        expect(page.locator("#panel h2")).to_have_text("Notice to proceed")


def test_back_and_forward_bring_back_the_map_type_of_each_address(page, taxonomy):
    spaces, ntp = code_of(taxonomy, "Spaces"), code_of(taxonomy, "Notice to proceed")
    page.goto(f"/#{spaces}")
    expect_loaded(page, taxonomy)
    page.evaluate(f"location.hash = '{ntp}'")
    page.wait_for_function(f"explorerMap.lastFrame().selected === '{ntp}'")
    pick(page, "Sunburst")
    page.go_back()
    page.wait_for_function(f"explorerMap.lastFrame().selected === '{spaces}'")
    assert (frame(page)["map"], page.evaluate("location.search")) == ("icicle", "")
    expect(switch(page).locator("[aria-pressed=true]")).to_have_text("Icicle")
    page.go_forward()
    page.wait_for_function(f"explorerMap.lastFrame().selected === '{ntp}'")
    assert (frame(page)["map"], page.evaluate("location.search")) == ("sunburst", "?map=sunburst")


TERRITORY_LIBRARIES = [
    "https://cdn.jsdelivr.net/npm/d3-weighted-voronoi@1.1.3/",
    "https://cdn.jsdelivr.net/npm/d3-voronoi-map@2.1.1/",
    "https://cdn.jsdelivr.net/npm/d3-voronoi-treemap@1.1.2/",
]


def test_the_territory_libraries_load_only_when_territory_is_picked_and_are_pinned(page, taxonomy):
    asked = []
    page.on("request", lambda r: asked.append(r.url))
    page.goto("/")
    expect_loaded(page, taxonomy)
    frame(page)  # the map has drawn, and the page has asked for all it asks for before a pick
    assert [u for u in asked if "jsdelivr" in u] == []
    pick(page, "Territory")
    wait_for_map_type(page, "territory")
    assert [next(u for u in asked if u.startswith(lib)) for lib in TERRITORY_LIBRARIES]
    scripts = page.evaluate("[...document.querySelectorAll('script[src*=jsdelivr]')].map(s => [s.src, s.integrity, s.crossOrigin])")
    assert [src for src, _, _ in scripts if not any(src.startswith(lib) for lib in TERRITORY_LIBRARIES)] == []
    assert len(scripts) == 3 and all(sri.startswith("sha384-") and cors == "anonymous" for _, sri, cors in scripts)


def test_when_the_territory_libraries_do_not_load_the_icicle_shows_with_a_short_message(page, taxonomy):
    page.route("https://cdn.jsdelivr.net/**", lambda route: route.abort())
    page.goto("/?map=sunburst")
    expect_loaded(page, taxonomy)
    pick(page, "Territory")
    expect(page.locator("#map-note")).to_contain_text("did not load")
    assert frame(page)["map"] == "icicle"
    expect(switch(page).locator("[aria-pressed=true]")).to_have_text("Icicle")
    assert page.evaluate("location.search") == ""


def test_rings_is_hidden_in_the_territory_map_and_shown_in_the_others(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    rings = page.get_by_role("group", name="Rings")
    for map_type, shown in (("Territory", False), ("Sunburst", True), ("Territory", False), ("Icicle", True)):
        pick(page, map_type)
        wait_for_map_type(page, map_type.lower())
        expect(rings).to_be_visible() if shown else expect(rings).to_be_hidden()


def test_a_failed_territory_load_does_not_undo_a_later_pick(page, taxonomy):
    held = []
    page.route("https://cdn.jsdelivr.net/**", lambda route: held.append(route))
    page.goto("/")
    expect_loaded(page, taxonomy)
    with page.expect_request(lambda r: "jsdelivr" in r.url):
        pick(page, "Territory")
    pick(page, "Sunburst")
    wait_for_map_type(page, "sunburst")
    held[0].abort()
    page.wait_for_function("!document.querySelector('script[src*=jsdelivr]')")
    expect(page.locator("#map-note")).to_be_hidden()
    assert frame(page)["map"] == "sunburst"
    expect(switch(page).locator("[aria-pressed=true]")).to_have_text("Sunburst")
