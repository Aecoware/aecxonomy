"""The Map switch: which map type opens, how a pick is written to the address and kept, and what a switch keeps."""
from playwright.sync_api import expect

from explorer import code_of, expect_loaded, frame


def switch(page):
    return page.get_by_role("group", name="Map")


def test_the_map_switch_offers_icicle_and_sunburst_and_the_explorer_opens_on_the_icicle(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    expect(switch(page).get_by_role("button")).to_have_text(["Icicle", "Sunburst"])
    expect(switch(page).locator("[aria-pressed=true]")).to_have_text("Icicle")
    assert frame(page)["map"] == "icicle"


def test_a_link_picks_the_map_type_and_an_unknown_one_is_ignored(page, taxonomy):
    page.goto("/?map=sunburst")
    expect_loaded(page, taxonomy)
    assert frame(page)["map"] == "sunburst"
    expect(switch(page).locator("[aria-pressed=true]")).to_have_text("Sunburst")
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
