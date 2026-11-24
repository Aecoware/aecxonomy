"""The map, read through its report of what it drew last and clicked where that report says a concept is."""
import json

import pytest
from playwright.sync_api import expect

from explorer import (CANVAS, cell, centre, children, click_cell, concepts_under, expect_loaded, frame, narrow,
                      open_concept)


def branches(taxonomy):
    return children(taxonomy, "")


def test_the_explorer_opens_on_the_icicle_with_every_branch_named_and_sized_by_its_concepts(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    f = frame(page)
    assert f["map"] == "icicle"
    assert f["focus"] is None
    cells = {c["code"]: c for c in f["cells"] if c["code"] in branches(taxonomy)}
    assert set(cells) == set(branches(taxonomy))
    assert {l["code"] for l in f["labels"]} >= set(branches(taxonomy))
    # Judging task 1: the three biggest branches can be read off the map.
    biggest = sorted(branches(taxonomy), key=lambda b: -concepts_under(taxonomy, b))[:3]
    tallest = sorted(cells, key=lambda b: -cells[b]["h"])[:3]
    assert tallest == biggest


def code_of(taxonomy, label):
    return next(k for k, c in taxonomy.items() if c["label"] == label)


def zoom_path(page):
    return page.locator("#crumbs")


def test_clicking_a_concept_with_children_zooms_to_it_and_names_every_child(page, taxonomy):
    # Judging task 2: after zooming to Spaces, every child of Spaces can be read.
    spaces = code_of(taxonomy, "Spaces")
    page.goto("/")
    expect_loaded(page, taxonomy)
    click_cell(page, cell(page, spaces))
    f = frame(page)
    assert f["focus"] == spaces
    assert {l["code"] for l in f["labels"]} >= set(children(taxonomy, spaces))
    expect(zoom_path(page).locator(".here")).to_have_text("Spaces")


def test_clicking_the_focus_column_goes_up_and_the_zoom_path_jumps_to_any_ancestor(page, taxonomy):
    # Notice to proceed sits under Milestones, under Events and risks.
    ntp = code_of(taxonomy, "Notice to proceed")
    milestones, events = taxonomy[ntp]["parent"], taxonomy[taxonomy[ntp]["parent"]]["parent"]
    page.goto("/")
    expect_loaded(page, taxonomy)
    click_cell(page, cell(page, events))
    click_cell(page, cell(page, milestones))
    assert frame(page)["focus"] == milestones
    expect(zoom_path(page).get_by_role("button")).to_have_text(["All branches", "Events and risks"])

    click_cell(page, cell(page, milestones))  # the focus column
    assert frame(page)["focus"] == events
    click_cell(page, cell(page, milestones))
    zoom_path(page).get_by_role("button", name="All branches").click()
    assert frame(page)["focus"] is None
    expect(zoom_path(page).locator(".here")).to_have_text("All branches")


def test_a_link_to_a_concept_opens_it_under_its_parent(page, taxonomy):
    # Judging task 4: Notice to proceed has Milestones as its parent, under Events and risks.
    ntp = code_of(taxonomy, "Notice to proceed")
    page.goto(f"/#{ntp}")
    expect_loaded(page, taxonomy)
    f = frame(page)
    assert f["focus"] == taxonomy[ntp]["parent"]
    assert f["selected"] == ntp
    expect(zoom_path(page)).to_have_text("All branches›Events and risks›Milestones")
    expect(page.locator("#panel h2")).to_have_text("Notice to proceed")


def test_clicking_a_concept_without_children_selects_it_outlines_it_and_writes_the_address(page, taxonomy):
    # Every child of Spaces has children, so take a grandchild: clicking it brings its parent into focus.
    spaces = code_of(taxonomy, "Spaces")
    parent = sorted(children(taxonomy, spaces))[0]
    leaf = next(k for k in sorted(children(taxonomy, parent)) if not children(taxonomy, k))
    page.goto("/")
    expect_loaded(page, taxonomy)
    click_cell(page, cell(page, spaces))
    click_cell(page, cell(page, leaf))
    f = frame(page)
    assert (f["focus"], f["selected"]) == (parent, leaf)
    expect(page.locator("#panel h2")).to_have_text(taxonomy[leaf]["label"])
    assert page.evaluate("location.hash") == f"#{leaf}"


def test_grouping_links_open_the_right_place_and_back_and_forward_move_the_map(page, taxonomy):
    spaces = code_of(taxonomy, "Spaces")
    ntp = code_of(taxonomy, "Notice to proceed")
    page.goto(f"/#kipling/{spaces}")
    expect_loaded(page, taxonomy)
    f = frame(page)
    assert (f["focus"], f["selected"]) == (spaces, spaces)
    expect(page.locator("#vseg [aria-pressed=true]")).to_have_text("Kipling 5W1H")
    expect(zoom_path(page).get_by_role("button").first).to_have_text("All 5W1H tags")

    page.evaluate("location.hash = 'kipling'")
    page.wait_for_function("explorerMap.lastFrame().focus === null")
    assert frame(page)["selected"] is None

    page.evaluate(f"location.hash = '{ntp}'")
    page.wait_for_function(f"explorerMap.lastFrame().selected === '{ntp}'")
    expect(page.locator("#vseg [aria-pressed=true]")).to_have_text("Branches")
    page.go_back()
    page.wait_for_function("explorerMap.lastFrame().selected === null")
    expect(page.locator("#vseg [aria-pressed=true]")).to_have_text("Kipling 5W1H")
    page.go_forward()
    page.wait_for_function(f"explorerMap.lastFrame().selected === '{ntp}'")
    assert frame(page)["focus"] == taxonomy[ntp]["parent"]


def depth(taxonomy, code):
    return 1 if not taxonomy[code]["parent"] else 1 + depth(taxonomy, taxonomy[code]["parent"])


def test_the_rings_set_how_many_levels_the_map_shows(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    for rings in (4, 2, 3):
        page.locator("#rings").get_by_role("button", name=str(rings)).click()
        f = frame(page)
        assert f["rings"] == rings
        assert max(depth(taxonomy, c["code"]) for c in f["cells"] if c["code"]) == rings


def test_the_colour_switch_colours_by_primary_tag_and_shows_its_legend(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    legend = page.locator("#legend")
    expect(legend).to_be_hidden()
    level_one = lambda f: {c["code"]: c["fill"] for c in f["cells"] if c["code"] in branches(taxonomy)}
    assert len(set(level_one(frame(page)).values())) == len(branches(taxonomy))

    page.locator("#colormode").get_by_role("button", name="5W1H").click()
    expect(legend).to_be_visible()
    for tag in ("Who", "What", "Where", "When", "Why", "How"):
        expect(legend).to_contain_text(f"{tag}:")
    for code, fill in level_one(frame(page)).items():
        tag = taxonomy[code]["primary_tag"]
        assert fill == page.evaluate(f"getComputedStyle(document.documentElement).getPropertyValue('--q-{tag}').trim()")


def test_switching_the_grouping_keeps_the_selection(page, taxonomy):
    ntp = code_of(taxonomy, "Notice to proceed")
    page.goto(f"/#{ntp}")
    expect_loaded(page, taxonomy)
    page.locator("#vseg").get_by_role("button", name="Kipling 5W1H").click()
    f = frame(page)
    assert (f["focus"], f["focusName"]) == (None, "All 5W1H tags")
    expect(page.locator("#panel h2")).to_have_text("Notice to proceed")
    assert page.evaluate("location.hash") == f"#kipling/{ntp}"
    assert {c["name"] for c in f["cells"] if c["code"] is None} >= {"All 5W1H tags", "Who", "When"}


def test_switching_the_grouping_with_nothing_selected_writes_it_to_the_address(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    page.locator("#vseg").get_by_role("button", name="Kipling 5W1H").click()
    page.wait_for_function("location.hash === '#kipling'")
    page.locator("#vseg").get_by_role("button", name="Branches").click()
    page.wait_for_function("location.hash === ''")


def test_the_columns_layout_shares_the_selection_with_the_map(page, taxonomy):
    spaces = code_of(taxonomy, "Spaces")
    first = sorted(children(taxonomy, spaces), key=lambda k: taxonomy[k]["label"])[0]
    page.goto(f"/#{spaces}")
    expect_loaded(page, taxonomy)
    page.get_by_role("tab", name="Columns").click()
    columns = page.locator("#cols")
    expect(columns.get_by_role("option", selected=True)).to_contain_text("Spaces")
    columns.get_by_role("option").filter(has_text=taxonomy[first]["label"]).click()
    page.get_by_role("tab", name="Map").click()
    f = frame(page)
    assert (f["focus"], f["selected"]) == (first, first)


def test_search_finds_a_concept_by_its_uk_label_and_the_map_zooms_to_it(page, taxonomy):
    code, concept = next((k, c) for k, c in sorted(taxonomy.items())
                         if c["label_gb"] and c["label_gb"] != c["label"] and c["parent"] and not children(taxonomy, k))
    page.goto("/")
    expect_loaded(page, taxonomy)
    open_concept(page, code, search_for=concept["label_gb"])
    f = frame(page)
    assert (f["focus"], f["selected"]) == (concept["parent"], code)


def overlap(a, b):
    return a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]


def test_labels_are_readable_and_every_child_of_the_focus_is_tall_enough_to_name_and_tap(page, taxonomy):
    page.emulate_media(reduced_motion="reduce")
    page.goto("/")
    expect_loaded(page, taxonomy)
    small = narrow(page)
    for focus in [None] + sorted(branches(taxonomy)):
        page.evaluate(f"location.hash = '{focus or ''}'")
        page.wait_for_function(f"explorerMap.lastFrame().focus === {repr(focus) if focus else 'null'}")
        f = frame(page)
        labels = f["labels"]
        assert all(12 <= l["size"] <= 14 for l in labels), focus
        assert [(a["text"], b["text"]) for i, a in enumerate(labels) for b in labels[i + 1:] if overlap(a, b)] == [], focus
        kids = {c["code"]: c for c in f["cells"] if c["code"] in children(taxonomy, focus or "")}
        assert set(kids) == set(children(taxonomy, focus or "")), focus
        assert min(c["h"] for c in kids.values()) >= (30 if small else 20), focus
        if small:
            assert min(min(c["w"], c["h"]) for c in kids.values()) >= 24, focus


def test_on_a_touch_screen_a_tap_on_a_thin_cell_counts_for_the_concept_above_it(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    if not page.evaluate("navigator.maxTouchPoints"):
        pytest.skip("the desktop size has no touch screen")
    thin = next(c for c in frame(page)["cells"] if c["code"] and depth(taxonomy, c["code"]) == 2 and c["h"] < 24)
    page.locator(CANVAS).tap(position=centre(thin))
    parent = taxonomy[thin["code"]]["parent"]
    f = frame(page)
    assert (f["focus"], f["selected"]) == (parent, parent)


def test_a_wheel_over_the_map_scrolls_the_page_and_leaves_the_focus(page, taxonomy):
    spaces = code_of(taxonomy, "Spaces")
    page.goto(f"/#{spaces}")
    expect_loaded(page, taxonomy)
    page.locator(CANVAS).scroll_into_view_if_needed()
    box = page.locator(CANVAS).bounding_box()
    page.mouse.move(box["x"] + box["width"] * 0.6, box["y"] + box["height"] / 2)
    for delta in (300, -150):
        before = page.evaluate("scrollY")
        page.mouse.wheel(0, delta)
        page.wait_for_function(f"scrollY {'>' if delta > 0 else '<'} {before}")
        assert frame(page)["focus"] == spaces


def test_a_zoom_is_one_short_tween_and_reduced_motion_makes_it_instant(page, taxonomy):
    spaces = code_of(taxonomy, "Spaces")
    page.goto("/")
    expect_loaded(page, taxonomy)
    click_cell(page, cell(page, spaces))
    zoom = frame(page)["zoom"]
    assert zoom["frames"] > 1 and zoom["ms"] < 500

    page.emulate_media(reduced_motion="reduce")
    click_cell(page, cell(page, spaces))  # the focus column: up to all branches
    f = page.evaluate("explorerMap.lastFrame()")
    assert (f["focus"], f["moving"], f["zoom"]) == (None, False, {"ms": 0, "frames": 1})


def canvas_size(page):
    return page.evaluate(f"(() => {{ const c = document.querySelector('{CANVAS}'), r = c.getBoundingClientRect();"
                         " return { width: c.width, height: c.height, css: [r.width, r.height], ratio: devicePixelRatio }; })()")


def test_the_canvas_matches_the_pixel_ratio_and_a_resize_redraws_and_keeps_the_focus(page, taxonomy):
    spaces = code_of(taxonomy, "Spaces")
    page.goto(f"/#{spaces}")
    expect_loaded(page, taxonomy)
    small = narrow(page)
    assert frame(page)["rings"] == (2 if small else 3)
    expect(page.locator("#rings [aria-pressed=true]")).to_have_text("2" if small else "3")
    before = canvas_size(page)
    assert (before["width"], before["height"]) == tuple(round(v * before["ratio"]) for v in before["css"])

    page.set_viewport_size({"width": 700 if small else 1100, "height": 860})
    page.wait_for_function(f"document.querySelector('{CANVAS}').width !== {before['width']}")
    after = canvas_size(page)
    assert (after["width"], after["height"]) == tuple(round(v * after["ratio"]) for v in after["css"])
    f = frame(page)
    assert f["focus"] == spaces
    assert max(c["x"] + c["w"] for c in f["cells"]) == round(after["css"][0], 2)
    assert {l["code"] for l in f["labels"]} >= set(children(taxonomy, spaces))


def test_the_page_stays_under_1400_elements_as_the_map_zooms(page, taxonomy):
    count = lambda: page.evaluate("document.getElementsByTagName('*').length")
    biggest = max(branches(taxonomy), key=lambda b: concepts_under(taxonomy, b))
    child = max(children(taxonomy, biggest), key=lambda k: concepts_under(taxonomy, k))
    page.goto("/")
    expect_loaded(page, taxonomy)
    assert count() < 1400
    for code in (biggest, child, child, biggest):  # in, in, then up twice by the focus column
        click_cell(page, cell(page, code))
        frame(page)
        assert count() < 1400


def test_the_map_is_a_canvas_with_no_application_role_and_the_hint_describes_it(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    assert page.locator("#chart svg").count() == 0
    assert page.locator("[role=application]").count() == 0
    expect(page.locator(".hint")).to_contain_text("Click the left column to go up")


def frame_tasks(trace):
    """How long each main-thread task that ran a frame's animation callback took, in ms."""
    events = [e for e in trace if e.get("ph") == "X" and "dur" in e]
    callbacks = [e for e in events if e["name"] == "FireAnimationFrame"]
    main = {e["tid"] for e in callbacks}
    tasks = [e for e in events if e["name"] == "ThreadControllerImpl::RunTask" and e["tid"] in main]
    holding = [t for t in tasks if any(t["ts"] <= c["ts"] and c["ts"] + c["dur"] <= t["ts"] + t["dur"] for c in callbacks)]
    return [t["dur"] / 1000 for t in holding]


def test_each_frame_of_a_zoom_takes_at_most_16_7_ms_with_the_cpu_slowed_4x(page, browser, taxonomy):
    biggest = max(branches(taxonomy), key=lambda b: concepts_under(taxonomy, b))
    # Open the branch first, so its Turtle is in and no download lands during the zoom. Then go back to all
    # branches and rest the pointer on the branch, as a person does before clicking: hover previews it.
    page.goto(f"/#{biggest}")
    expect_loaded(page, taxonomy)
    expect(page.locator("#panel pre")).to_contain_text(f"aeco:{biggest} ")
    zoom_path(page).get_by_role("button", name="All branches").click()
    target = cell(page, biggest)
    page.locator(CANVAS).hover(position=centre(target))
    cdp = page.context.new_cdp_session(page)
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
    browser.start_tracing(page=page, categories=["devtools.timeline", "toplevel"])
    click_cell(page, target)
    page.wait_for_function("!explorerMap.lastFrame().moving", polling=100)
    trace = json.loads(browser.stop_tracing())["traceEvents"]
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 1})
    zoom = frame(page)["zoom"]
    times = frame_tasks(trace)
    assert len(times) >= zoom["frames"] > 1
    assert max(times) <= 16.7, [round(t, 1) for t in times]
