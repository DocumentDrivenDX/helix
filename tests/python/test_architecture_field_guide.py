"""The developer field guide, drawn from the architecture model (HELIX's architecture views; praxis ADR-090 adopted them).

A field-guide view is a whole page: lanes from the view's groups, boxes stacked on one axis,
numbered steps and the call that runs throughout, and the notes beside the plate, all from the
model, so nothing on it is placed by hand.
"""

import re
from itertools import pairwise


from architecture_field_guide import (
    LANE_GAP,
    field_guide_problems,
    layout,
    route,
    shown,
    svg,
)
from architecture_field_page import render_field_guide
from architecture_model import (
    DEFAULT_THEME,
    Element,
    Evidence,
    Group,
    Model,
    Relation,
    System,
    View,
    default_owner,
    load,
)


PRAXIS = System(id="praxis", name="praxis", regenerate="just architecture")


def _element(element_id: str, **fields: object) -> Element:
    values: dict = {"name": element_id.title(), "kind": "container", "status": "built"}
    values |= fields
    values.setdefault("owner", default_owner(values["kind"], "praxis"))
    return Element(id=element_id, evidence=(Evidence("app.py", "APP"),), **values)


def _relation(source: str, target: str, label: str, **fields: object) -> Relation:
    return Relation(source, target, label, "built", (Evidence("app.py", "APP"),), **fields)


def _model(*elements: Element, relations: tuple[Relation, ...] = (), views=()) -> Model:
    return Model(
        {e.id: e for e in elements}, relations, {v.id: v for v in views}, (), PRAXIS, dict(DEFAULT_THEME)
    )


LANES = (
    Group("people", "People", ("user",)),
    Group("app", "praxis", ("app",)),
    Group("data", "Databricks platform", ("files", "queue", "db", "log", "cache", "index")),
)
ELEMENTS = (
    _element("user", kind="person", name="A reader", layer="People"),
    _element("app", kind="system", name="praxis", detail="Databricks App", layer="praxis"),
    _element("files", kind="store", name="Files", layer="Platform"),
    _element("queue", kind="store", name="Queue", layer="Platform"),
    _element("db", kind="store", name="Lakebase", layer="Platform"),
    _element("log", kind="external", name="Collector", layer="Platform"),
    _element("cache", kind="store", name="Cache", layer="Platform", status="decided"),
    _element("index", kind="store", name="Index", layer="Platform"),
)
RELATIONS = (
    _relation("user", "app", "HTTPS", step=1, note="They open it.", why="the platform signs in"),
    _relation("app", "files", "reads files"),
    _relation("app", "queue", "enqueues"),
    _relation("app", "index", "indexes"),
    _relation("app", "db", "session", step=2, note="It locks.", why="state outlives a restart"),
    _relation("app", "log", "audit spans, OTLP", throughout=True, note="Every `call()`."),
    _relation("app", "cache", "a label much longer than twenty characters"),
    _relation("log", "cache", "copies"),
)


def _view(**fields: object) -> View:
    values: dict = {
        "groups": LANES,
        "title": "One read.",
        "takeaway": "A reader asks; praxis reads.",
        "document": "../../guide/developer/field-guide.html",
        "type": "field-guide",
    }
    values |= fields
    return View("guide", "LR", ("user", "app", *LANES[2].elements), **values)


def _guide() -> tuple[Model, View]:
    view = _view()
    other = View("ctx", "LR", ("user", "app"), title="Who it talks to", document="../../x/ctx.md")
    return _model(*ELEMENTS, relations=RELATIONS, views=(view, other)), view


def _paths(model: Model, view: View) -> dict[tuple[str, str], str]:
    plate = layout(model, view)
    return {
        (ln.relation.source, ln.relation.target): ln.path for ln in route(plate, shown(model, view))
    }


def _corridor(path: str) -> float:
    return float(re.search(r"H(\d+)V", path)[1])


# --- checks -------------------------------------------------------------------------------------


def test_a_field_guide_needs_lanes_every_element_in_one_and_every_step_on_the_plate() -> None:
    model, view = _guide()
    assert field_guide_problems(model, view) == []
    bare = _view(groups=())
    assert field_guide_problems(model, bare) == [
        "view guide: a field guide needs groups, one per lane, left to right",
        *(f"view guide: {e} is in no lane" for e in bare.elements),
    ]
    twice = _view(groups=(*LANES, Group("again", "Again", ("db",))))
    assert field_guide_problems(model, twice) == ["view guide: db is in two lanes"]
    partial = View(
        "guide", "LR", ("app", "db"), groups=LANES[1:], type="field-guide", document="g.html"
    )
    assert "view guide: step 1 (user to app) is off the plate" in field_guide_problems(
        model, partial
    )
    assert "view guide: files is in no lane" not in field_guide_problems(model, partial)
    markdown = _view(document="guide.md")
    assert field_guide_problems(model, markdown) == [
        "view guide: a field guide's document is the HTML page it writes"
    ]
    assert field_guide_problems(model, View("plain", "LR", ("app",))) == []


# --- layout -------------------------------------------------------------------------------------


def test_lanes_run_left_to_right_and_a_lane_stacks_its_boxes_on_the_shared_axis() -> None:
    model, view = _guide()
    plate = layout(model, view)
    assert [lane.title for lane in plate.lanes] == ["People", "praxis", "Databricks platform"]
    assert plate.lanes[0].x < plate.lanes[1].x < plate.lanes[2].x
    boxes = plate.nodes
    stack = [boxes[e].box for e in LANES[2].elements]
    assert all(a.y + a.h < b.y for a, b in pairwise(stack))
    assert len({b.w for b in stack}) == 1, "boxes in a lane share the lane's width"
    axis = (stack[0].y + stack[-1].y + stack[-1].h) / 2
    assert abs(boxes["app"].box.cy - axis) < 1
    assert abs(boxes["user"].box.cy - axis) < 1
    assert plate.lanes[1].owned
    assert not plate.lanes[2].owned
    assert plate.width > plate.lanes[2].x + plate.lanes[2].w


def test_a_gap_widens_for_the_longest_label_line_that_crosses_it() -> None:
    model, view = _guide()
    plate = layout(model, view)
    assert plate.gaps[0] == LANE_GAP, "HTTPS fits in the standard gap"
    longest = max(len(line) for line in ("a label much longer", "than twenty characters"))
    assert plate.gaps[1] >= longest * 7.2 + 30


# --- routing ------------------------------------------------------------------------------------


def test_a_fan_leaves_by_the_top_and_bottom_for_the_outer_targets_and_nests_the_rest() -> None:
    model, view = _guide()
    plate = layout(model, view)
    app = plate.nodes["app"].box
    assert app.h >= 104, "a station on the path is tall enough for the lines it sends"
    paths = _paths(model, view)
    assert paths["app", "files"].startswith(f"M{app.cx:.0f} {app.y:.0f}V"), "out of the top"
    assert paths["app", "index"].startswith(f"M{app.cx:.0f} {app.y + app.h:.0f}V"), "the bottom"
    queue, db, log, cache = (paths["app", t] for t in ("queue", "db", "log", "cache"))
    assert all("V" in p for p in (queue, db, log, cache)), "the rest climb or drop by corridor"
    assert _corridor(queue) < _corridor(db), "the higher target takes the corridor nearest the box"
    assert _corridor(cache) < _corridor(log), "and so does the lower one, mirrored"
    assert _corridor(queue) == _corridor(cache)
    assert plate.gaps[1] >= 130, "a fan's gap has room for its corridors"
    three = Group("data", "Data", ("files", "log", "cache"))
    level = View("guide", "LR", ("user", "app", *three.elements), groups=(*LANES[:2], three))
    assert "V" not in _paths(model, level)["app", "log"], "level with its exit: a straight run"


def test_same_lane_lines_run_straight_between_boxes_and_a_skip_or_return_takes_the_perimeter() -> (
    None
):
    model, view = _guide()
    plate = layout(model, view)
    copies = route(plate, [_relation("log", "cache", "copies")])[0]
    assert re.fullmatch(r"M\d+ \d+V\d+", copies.path)
    assert copies.anchor == "start"
    skip = route(plate, [_relation("user", "db", "direct")])[0]
    assert skip.path.startswith("M")
    assert "V22H" in skip.path, "over the top"
    back = route(plate, [_relation("db", "user", "reply")])[0]
    assert f"V{plate.height - 18:.0f}H" in back.path, "under the bottom"


# --- the SVG and the page -----------------------------------------------------------------------


def test_the_plate_draws_every_element_by_id_numbers_the_steps_and_marks_what_runs_throughout() -> (
    None
):
    model, view = _guide()
    drawing = svg(model, view)
    assert all(f'<g id="{e}">' in drawing for e in view.elements)
    assert drawing.count('class="badge"') == 3, "two numbered steps and one pill"
    assert ">THROUGHOUT<" in drawing
    assert ">1<" in drawing
    assert ">2<" in drawing
    assert drawing.count('class="edge"') == 3
    assert drawing.count('class="quiet"') == 5
    assert '<rect x="' in drawing
    assert 'class="own"' in drawing
    assert 'class="owned"' in drawing
    assert "01 / PEOPLE" in drawing
    assert "03 / DATABRICKS PLATFORM" in drawing
    assert ">a label much longer than<" in drawing
    assert ">twenty characters<" in drawing
    assert ">audit spans, OTLP<" in drawing, "a short label stays on one line"
    assert (
        '<desc id="desc">1. A reader to praxis: HTTPS; 2. praxis to Lakebase: session.</desc>'
        in drawing
    )


def test_the_page_tells_the_walkthrough_the_omissions_and_where_else_the_model_is_drawn() -> None:
    model, view = _guide()
    page = render_field_guide(model, view)
    assert "<h1>One read.</h1>" in page
    assert "<p>A reader asks; praxis reads.</p>" in page
    assert "<li><strong>The platform signs in.</strong> They open it.</li>" in page
    assert "<li><strong>State outlives a restart.</strong> It locks.</li>" in page
    assert "<strong>Throughout: audit spans, OTLP.</strong> Every <code>call()</code>." in page
    assert "This is a conceptual map, not a deployment topology." in page
    assert "Not real yet: Cache (decided)." in page
    assert 'href="../../x/ctx.md">Who it talks to</a>' in page
    assert "8 of 8 elements" in page
    assert "--accent:#2F6F8F" in page, "the model's theme becomes the page's variables"
    assert "<script" not in page
    assert "http" not in page.split("<body>")[1]


def test_what_the_plate_leaves_out_is_listed_by_layer() -> None:
    model, _ = _guide()
    view = View(
        "guide",
        "LR",
        ("user", "app", "db"),
        groups=(LANES[0], LANES[1], Group("d", "Data", ("db",))),
        type="field-guide",
        document="g.html",
    )
    page = render_field_guide(model, view)
    assert (
        "Left out on purpose, by layer: Platform (Files, Queue, Collector, Cache, Index)." in page
    )
    assert "3 of 8 elements" in page
