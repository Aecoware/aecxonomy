"""The built explorer, used the way a person uses it, at a desktop size and a phone size."""
from playwright.sync_api import expect

from explorer import expect_loaded, open_concept

DATA_REQUEST = "**/explorer-data.json*"


def test_search_finds_a_concept_and_the_side_panel_shows_it_with_its_warnings(page, taxonomy):
    # A Shared concept without a UK label always gets a warning, so it makes a known example.
    code, concept = next((k, c) for k, c in sorted(taxonomy.items()) if c["shared"] and not c["label_gb"])
    page.goto("/")
    open_concept(page, code, search_for=concept["label"])
    panel = page.locator("#panel")
    expect(panel.get_by_role("heading", level=2)).to_have_text(concept["label"])
    expect(panel).to_contain_text("warning")


def test_a_loading_message_shows_while_the_data_loads(page, taxonomy):
    held = []
    page.route(DATA_REQUEST, lambda route: held.append(route))
    page.goto("/", wait_until="domcontentloaded")
    loading = page.get_by_role("status").filter(has_text="Loading")
    expect(loading).to_be_visible()
    while not held:
        page.wait_for_timeout(50)
    held[0].continue_()
    expect_loaded(page, taxonomy)
    expect(loading).to_be_hidden()


def test_a_failed_data_load_says_so_and_offers_a_retry(page, taxonomy):
    page.route(DATA_REQUEST, lambda route: route.abort())
    page.goto("/")
    retry = page.get_by_role("button", name="Try again")
    expect(retry).to_be_visible()
    expect(page.locator("#load").get_by_role("status")).not_to_contain_text("Loading")
    page.unroute(DATA_REQUEST)
    retry.click()
    expect_loaded(page, taxonomy)
    expect(retry).to_be_hidden()


def test_the_turtle_loads_only_when_a_concept_is_opened(page, taxonomy, shapes):
    asked = []
    page.on("request", lambda r: asked.append(r.url) if "explorer-turtle.json" in r.url else None)
    page.goto("/")
    expect_loaded(page, taxonomy)

    # Moving the pointer across the map previews concepts in the side panel. That must not fetch the Turtle.
    page.locator("#chart").scroll_into_view_if_needed()
    box = page.locator("#chart").bounding_box()
    previewed = False
    for i in range(1, 30):
        page.mouse.move(box["x"] + box["width"] * i / 30, box["y"] + box["height"] / 2)
        previewed = previewed or "Click to keep this open" in page.locator("#panel").text_content()
    assert previewed
    assert asked == []

    code, concept = sorted(taxonomy.items())[0]
    page.mouse.move(0, 0)
    open_concept(page, code)
    code_block = page.locator("#panel pre")
    expect(code_block).to_contain_text(f"aeco:{code} ")
    expect(code_block).to_contain_text(f'"{concept["label"]}"@en-US')
    assert len(asked) == 1

    page.locator("#panel").get_by_role("tab", name="Shapes").click()
    expect(code_block).to_contain_text("sh:NodeShape")
    assert code_block.text_content() == shapes
