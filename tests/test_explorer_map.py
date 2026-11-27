"""The map, read through its report of what it drew last and clicked where that report says a concept is."""
import json
import math

import pytest
from playwright.sync_api import expect

from explorer import (CANVAS, MAP_TYPES, cell, children, click_cell, code_of, concepts_under, expect_loaded, frame,
                      narrow, open_concept)


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


@pytest.mark.parametrize("map_type", MAP_TYPES)
def test_clicking_the_focus_goes_up_and_the_zoom_path_jumps_to_any_ancestor(page, taxonomy, map_type):
    # Notice to proceed sits under Milestones, under Events and risks.
    ntp = code_of(taxonomy, "Notice to proceed")
    milestones, events = taxonomy[ntp]["parent"], taxonomy[taxonomy[ntp]["parent"]]["parent"]
    page.goto(f"/?map={map_type}")
    expect_loaded(page, taxonomy)
    click_cell(page, cell(page, events))
    click_cell(page, cell(page, milestones))
    assert frame(page)["focus"] == milestones
    expect(zoom_path(page).get_by_role("button")).to_have_text(["All branches", "Events and risks"])

    click_cell(page, cell(page, milestones))  # the focus
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


@pytest.mark.parametrize("map_type", MAP_TYPES)
def test_clicking_a_concept_without_children_selects_it_outlines_it_and_writes_the_address(page, taxonomy, map_type):
    # Every child of Spaces has children, so take a grandchild: clicking it brings its parent into focus.
    spaces = code_of(taxonomy, "Spaces")
    parent = sorted(children(taxonomy, spaces))[0]
    leaf = next(k for k in sorted(children(taxonomy, parent)) if not children(taxonomy, k))
    page.goto(f"/?map={map_type}")
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


@pytest.mark.parametrize("map_type", MAP_TYPES)
def test_the_rings_set_how_many_levels_the_map_shows(page, taxonomy, map_type):
    page.goto(f"/?map={map_type}")
    expect_loaded(page, taxonomy)
    for rings in (4, 2, 3):
        page.locator("#rings").get_by_role("button", name=str(rings)).click()
        f = frame(page)
        assert f["rings"] == rings
        assert max(depth(taxonomy, c["code"]) for c in f["cells"] if c["code"]) == rings


@pytest.mark.parametrize("map_type", MAP_TYPES)
def test_the_colour_switch_colours_by_primary_tag_and_shows_its_legend(page, taxonomy, map_type):
    page.goto(f"/?map={map_type}")
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


@pytest.mark.parametrize("map_type", MAP_TYPES)
def test_search_finds_a_concept_by_its_uk_label_and_the_map_zooms_to_it(page, taxonomy, map_type):
    code, concept = next((k, c) for k, c in sorted(taxonomy.items())
                         if c["label_gb"] and c["label_gb"] != c["label"] and c["parent"] and not children(taxonomy, k))
    page.goto(f"/?map={map_type}")
    expect_loaded(page, taxonomy)
    open_concept(page, code, search_for=concept["label_gb"])
    f = frame(page)
    assert (f["focus"], f["selected"]) == (concept["parent"], code)


def open_by_address(page, code):
    """Open a concept, or all branches for None, by its address, and return the frame once the map is there."""
    page.evaluate(f"location.hash = '{code or ''}'")
    page.wait_for_function(f"explorerMap.lastFrame().focus === {repr(code) if code else 'null'}")
    return frame(page)


def overlap(a, b):
    return a["x"] < b["x"] + b["w"] and b["x"] < a["x"] + a["w"] and a["y"] < b["y"] + b["h"] and b["y"] < a["y"] + a["h"]


def test_labels_are_readable_and_every_child_of_the_focus_is_tall_enough_to_name_and_tap(page, taxonomy):
    page.emulate_media(reduced_motion="reduce")
    page.goto("/")
    expect_loaded(page, taxonomy)
    small = narrow(page)
    for focus in [None] + sorted(branches(taxonomy)):
        f = open_by_address(page, focus)
        labels = f["labels"]
        assert all(12 <= l["size"] <= 14 for l in labels), focus
        assert [(a["text"], b["text"]) for i, a in enumerate(labels) for b in labels[i + 1:] if overlap(a, b)] == [], focus
        kids = {c["code"]: c for c in f["cells"] if c["code"] in children(taxonomy, focus or "")}
        assert set(kids) == set(children(taxonomy, focus or "")), focus
        assert min(c["h"] for c in kids.values()) >= (30 if small else 20), focus
        if small:
            assert min(min(c["w"], c["h"]) for c in kids.values()) >= 24, focus


def nearest(p, q):
    """The distance from the centre to the nearest point of the segment p-q, both given from the centre."""
    (px, py), (qx, qy) = p, q
    dx, dy = qx - px, qy - py
    t = max(0, min(1, -(px * dx + py * dy) / ((dx * dx + dy * dy) or 1)))
    return math.hypot(px + t * dx, py + t * dy)


def inside_arc(corners, arc, slack=0.5):
    """Whether a label's box lies inside a sunburst cell. The inside edge of a ring curves away from a straight side,
    so the sides are checked against it as well as the corners."""
    pts = [(x - arc["cx"], y - arc["cy"]) for x, y in corners]
    whole = arc["a1"] - arc["a0"] > 2 * math.pi - 1e-3
    for x, y in pts:
        r = math.hypot(x, y)
        if r > arc["r1"] + slack:
            return False
        if not whole and not arc["a0"] - slack / r <= math.atan2(x, -y) % (2 * math.pi) <= arc["a1"] + slack / r:
            return False
    return arc["r0"] == 0 or all(nearest(p, q) >= arc["r0"] - slack for p, q in zip(pts, pts[1:] + pts[:1]))


def test_sunburst_labels_fit_their_arcs_and_read_from_the_left_and_every_child_is_big_enough_to_tap(page, taxonomy):
    page.emulate_media(reduced_motion="reduce")
    page.goto("/?map=sunburst")
    expect_loaded(page, taxonomy)
    floor = 24 if narrow(page) else 20
    along_the_radius = 0
    for focus in [None] + sorted(branches(taxonomy)):
        f = open_by_address(page, focus)
        cells = {c["code"]: c for c in f["cells"]}
        rings = [l for l in f["labels"] if l["code"] != focus]
        assert rings, focus
        for l in f["labels"]:
            assert 12 <= l["size"] <= 14, (focus, l["text"])
            assert inside_arc(l["corners"], cells[l["code"]]["arc"]), (focus, l["text"])
            assert math.cos(l["angle"]) > -1e-3, (focus, l["text"])  # it reads from the left, or down the page
        for l in rings:
            name = cells[l["code"]]["name"]
            assert l["text"] == name or (l["text"].endswith("…") and name.startswith(l["text"][:-1])), (focus, l["text"])
        along_the_radius += sum(l["angle"] != 0 for l in rings)
        kids = [cells[k]["arc"] for k in children(taxonomy, focus or "")]
        assert min(min(a["r1"] - a["r0"], (a["r0"] + a["r1"]) / 2 * (a["a1"] - a["a0"])) for a in kids) >= floor - 0.01, focus  # the report rounds angles
    assert along_the_radius


def test_on_a_touch_screen_a_tap_on_a_thin_cell_counts_for_the_concept_above_it(page, taxonomy):
    page.goto("/")
    expect_loaded(page, taxonomy)
    if not page.evaluate("navigator.maxTouchPoints"):
        pytest.skip("the desktop size has no touch screen")
    thin = next(c for c in frame(page)["cells"] if c["code"] and depth(taxonomy, c["code"]) == 2 and c["h"] < 24)
    page.locator(CANVAS).tap(position=thin["mid"])
    parent = taxonomy[thin["code"]]["parent"]
    f = frame(page)
    assert (f["focus"], f["selected"]) == (parent, parent)


@pytest.mark.parametrize("map_type", MAP_TYPES)
def test_a_wheel_over_the_map_scrolls_the_page_and_leaves_the_focus(page, taxonomy, map_type):
    spaces = code_of(taxonomy, "Spaces")
    page.goto(f"/?map={map_type}#{spaces}")
    expect_loaded(page, taxonomy)
    page.locator(CANVAS).scroll_into_view_if_needed()
    box = page.locator(CANVAS).bounding_box()
    page.mouse.move(box["x"] + box["width"] * 0.6, box["y"] + box["height"] / 2)
    for delta in (300, -150):
        before = page.evaluate("scrollY")
        page.mouse.wheel(0, delta)
        page.wait_for_function(f"scrollY {'>' if delta > 0 else '<'} {before}")
        assert frame(page)["focus"] == spaces


@pytest.mark.parametrize("map_type", MAP_TYPES)
def test_a_zoom_is_one_short_tween_and_reduced_motion_makes_it_instant(page, taxonomy, map_type):
    spaces = code_of(taxonomy, "Spaces")
    page.goto(f"/?map={map_type}")
    expect_loaded(page, taxonomy)
    click_cell(page, cell(page, spaces))
    zoom = frame(page)["zoom"]
    assert zoom["frames"] > 1 and zoom["ms"] < 500

    page.emulate_media(reduced_motion="reduce")
    click_cell(page, cell(page, spaces))  # the focus: up to all branches
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


@pytest.mark.parametrize("map_type", MAP_TYPES)
def test_the_page_stays_under_1400_elements_as_the_map_zooms(page, taxonomy, map_type):
    count = lambda: page.evaluate("document.getElementsByTagName('*').length")
    biggest = max(branches(taxonomy), key=lambda b: concepts_under(taxonomy, b))
    child = max(children(taxonomy, biggest), key=lambda k: concepts_under(taxonomy, k))
    page.goto(f"/?map={map_type}")
    expect_loaded(page, taxonomy)
    assert count() < 1400
    for code in (biggest, child, child, biggest):  # in, in, then up twice by the focus
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


@pytest.mark.parametrize("map_type", MAP_TYPES)
def test_each_frame_of_a_zoom_takes_at_most_16_7_ms_with_the_cpu_slowed_4x(page, browser, taxonomy, map_type):
    biggest = max(branches(taxonomy), key=lambda b: concepts_under(taxonomy, b))
    # Open the branch first, so its Turtle is in and no download lands during the zoom. Then go back to all
    # branches and rest the pointer on the branch, as a person does before clicking: hover previews it.
    page.goto(f"/?map={map_type}#{biggest}")
    expect_loaded(page, taxonomy)
    expect(page.locator("#panel pre")).to_contain_text(f"aeco:{biggest} ")
    zoom_path(page).get_by_role("button", name="All branches").click()
    target = cell(page, biggest)
    page.locator(CANVAS).hover(position=target["mid"])
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
