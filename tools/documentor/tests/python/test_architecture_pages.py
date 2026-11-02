"""The stack, cast, journey, and deployment views of the architecture model (HELIX's architecture views)."""

from dataclasses import replace
from itertools import pairwise
from pathlib import Path


from documentor.architecture.deploy import LABEL_PX, render_deployment, route
from documentor.architecture.deploy import _label as deploy_label
from documentor.architecture.model import (
    DEFAULT_THEME,
    Element,
    Evidence,
    Journey,
    Model,
    Relation,
    Step,
    System,
    View,
    load,
    model_problems,
)
from documentor.architecture.pages import render_cast, render_dag, render_journey, render_stack
from documentor.architecture.views import render_view, run


EVIDENCE = (Evidence("app.py", "APP"),)
ATLAS = System(id="atlas", name="atlas", regenerate="just architecture")


def _element(element_id: str, **fields: object) -> Element:
    values: dict = {"name": element_id.title(), "kind": "container", "status": "built"}
    values |= {"owner": "atlas"} | fields
    return Element(id=element_id, evidence=EVIDENCE, **values)


def _relation(source: str, target: str, label: str, **fields: object) -> Relation:
    return Relation(source, target, label, fields.pop("status", "built"), EVIDENCE, **fields)


def _model(*elements: Element, relations=(), views=(), journeys=(), zones=None) -> Model:
    return Model(
        {e.id: e for e in elements},
        tuple(relations),
        {v.id: v for v in views},
        (),
        ATLAS,
        dict(DEFAULT_THEME),
        {j.id: j for j in journeys},
        zones or {},
    )


def _root(tmp_path: Path) -> Path:
    (tmp_path / "app.py").write_text("APP = 1\n")
    return tmp_path


def test_a_stack_lists_each_layer_in_reading_order_and_marks_what_is_not_built() -> None:
    people = _element("user", kind="person", layer="People")
    app = _element("app", layer="atlas")
    walls = _element("walls", kind="external", status="unknown", layer="The firm")
    view = View("stack", "LR", ("user", "app", "walls"), type="stack", title="Where", takeaway="T.")
    text = render_stack(_model(people, app, walls, views=(view,)), view)
    assert text.startswith("**Where.** T.\n\n| Layer | What sits there |")
    assert text.index("| People |") < text.index("| atlas |") < text.index("| The firm |")
    assert "**Walls** (unknown)" in text


def test_a_cast_gives_each_piece_its_job_and_names_another_repository() -> None:
    ledger = _element("ledger", job="The ontology | library.", system="ledger")
    stand = _element("stand", job="Answers for now.", status="placeholder")
    view = View("cast", "LR", ("ledger", "stand"), type="cast")
    text = render_cast(_model(ledger, stand, views=(view,)), view)
    assert "| **Ledger** (ledger) | The ontology \\| library. | built |" in text
    assert "| **Stand** | Answers for now. | stand-in |" in text


def test_a_journey_numbers_its_steps_and_draws_a_reply_against_a_relation_dashed() -> None:
    user, proxy, app = _element("user", kind="person"), _element("proxy"), _element("app")
    relations = (_relation("user", "proxy", "HTTPS"), _relation("proxy", "app", "headers"))
    steps = (
        Step("user", "proxy", "opens it; signs in"),
        Step("app", "app", "chooses a workflow"),
        Step("app", "proxy", "the reply"),
    )
    journey = Journey("j", "A review", "Runs as the person.", steps)
    view = View("j", "LR", (), type="journey", journey="j")
    text = render_journey(_model(user, proxy, app, relations=relations, journeys=(journey,)), view)
    assert text.startswith("**A review.** Runs as the person.\n\n```mermaid\n%%{init: ")
    assert "\nsequenceDiagram\n" in text
    assert '"actorBorder": "#D9DEE5"' in text
    assert "participant user as User" in text
    assert "user->>proxy: 1 · opens it, signs in" in text
    assert "app->>app: 2 · chooses a workflow" in text
    assert "app-->>proxy: 3 · the reply" in text


def test_a_view_type_needs_its_field_and_a_journey_must_walk_relations(tmp_path: Path) -> None:
    bare = _element("bare")
    edge = _relation("bare", "other", "calls")
    other = _element("other")
    views = (
        View("s", "LR", ("bare",), type="stack"),
        View("c", "LR", ("bare",), type="cast"),
        View("d", "LR", ("bare",), type="deployment"),
        View("j", "LR", (), type="journey", journey="missing"),
        View("x", "LR", ("bare",), type="radar"),
    )
    lost = Journey("walk", "", "", (Step("other", "bare", "back"), Step("bare", "ghost", "x")))
    stray = Journey("stray", "", "", (Step("other", "other", "thinks"), Step("bare", "x", "y")))
    model = _model(bare, other, relations=(edge,), views=views, journeys=(lost, stray))
    problems = model_problems(model, _root(tmp_path))
    assert "view s: element bare has no layer" in problems
    assert "view c: element bare has no job" in problems
    assert "view d: element bare has no zone" in problems
    assert "view d: element bare has no tier" in problems
    assert "view j: no journey named 'missing'" in problems
    assert "view x: unknown type radar" in problems
    assert "journey walk step 2: unknown element ghost" in problems
    assert "journey stray step 2: unknown element x" in problems
    assert not any("journey walk step 1" in p or "journey stray step 1" in p for p in problems)


def _deployment() -> Model:
    user = _element("user", kind="person", tier=1, zone="Firm")
    ent = _element("ent", kind="external", status="unknown", tier=1, zone="Firm")
    proxy = _element("proxy", kind="external", tier=2, zone="Edge", detail="SSO")
    app = _element("app", kind="system", tier=3, zone="Apps", detail="one process")
    peer = _element("peer", kind="external", tier=3, zone="Apps")
    db = _element("db", kind="store", tier=4, zone="Data")
    log = _element("log", kind="external", tier=4, zone="Data")
    relations = (
        _relation("user", "proxy", "HTTPS", why="SSO signs them in"),
        _relation("proxy", "app", "headers"),
        _relation("app", "peer", "MCP"),
        _relation("app", "db", "sessions", why="state outlives a restart"),
        _relation("app", "log", "spans"),
        _relation("db", "log", "changes"),
        _relation("app", "ent", "which matters", status="unknown"),
    )
    elements = ("user", "ent", "proxy", "app", "peer", "db", "log")
    view = View("deploy", "LR", elements, type="deployment", title="Where it runs", takeaway="T.")
    zones = {"Data": "Provisioned by infra"}
    return _model(
        user, ent, proxy, app, peer, db, log, relations=relations, views=(view,), zones=zones
    )


def test_a_deployment_gives_every_line_its_own_lane_and_sends_a_skip_down_the_corridor() -> None:
    model = _deployment()
    layout = route(model, model.views["deploy"])
    assert len(layout.paths) == 7
    assert layout.corridors == 1
    corridor = next(path for path, dashed in layout.paths if dashed)
    assert " L-24.0," in corridor
    gap_runs = [
        y
        for _, y, text in layout.labels
        if text in ("sessions · state outlives a restart", "spans")
    ]
    assert len(set(gap_runs)) == 2
    tiers = sorted(layout.tiers.values())
    assert all(upper[1] < lower[0] for upper, lower in pairwise(tiers))


def test_neighbors_a_line_joins_stand_apart_and_join_side_to_side() -> None:
    model = _deployment()
    layout = route(model, model.views["deploy"])
    for source, target in (("app", "peer"), ("db", "log")):
        a, b = layout.boxes[source], layout.boxes[target]
        left, right = (a, b) if a.x < b.x else (b, a)
        points = layout.routes[f"{source}>{target}"]
        assert [x for x, _ in points] in ([left.x + left.w, right.x], [right.x, left.x + left.w])
        assert all(a.y < y < a.y + a.h for _, y in points)
    mcp = next(x for x, _, text in layout.labels if text == "MCP")
    app, peer = layout.boxes["app"], layout.boxes["peer"]
    assert min(app.x, peer.x) < mcp < max(app.x + app.w, peer.x + peer.w)


def _segments(layout):
    return [(key, a, b) for key, points in layout.routes.items() for a, b in pairwise(points)]


def _crossings(layout) -> int:
    count = 0
    segments = _segments(layout)
    for i, (k1, a, b) in enumerate(segments):
        for k2, c, d in segments[i + 1 :]:
            if k1 == k2 or (a[1] == b[1]) == (c[1] == d[1]):
                continue
            (h0, h1), (v0, v1) = ((a, b), (c, d)) if a[1] == b[1] else ((c, d), (a, b))
            if min(h0[0], h1[0]) < v0[0] < max(h0[0], h1[0]) and min(v0[1], v1[1]) < h0[1] < max(v0[1], v1[1]):
                count += 1
    return count


def _tags_crossed(model, view, layout) -> list[str]:
    owner = {deploy_label(r): f"{r.source}>{r.target}" for r in model.relations}
    crossed = []
    for (x, y, text), rows in zip(layout.labels, layout.label_rows, strict=True):
        w, h = max(map(len, rows)) * LABEL_PX + 12, 16 * len(rows) + 2
        box = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        for key, a, b in _segments(layout):
            if key != owner[text] and min(a[0], b[0]) < box[2] and box[0] < max(a[0], b[0]) and min(a[1], b[1]) < box[3] and box[1] < max(a[1], b[1]):
                crossed.append(text)
                break
    return crossed


def test_a_busy_box_sends_each_line_on_its_own_track_with_no_crossing_and_no_line_under_a_tag() -> None:
    # One box with lines to every box in the tier below, two tiers up, and one under the bottom
    # tier: the shape that drew a bundle of crossed lines with tags over them.
    people = [_element("person", tier=1, zone="People"), _element("installer", tier=1, zone="People")]
    app = _element("app", kind="system", tier=2, zone="Apps")
    below = [_element(f"store{i}", kind="store", tier=3, zone="Data") for i in range(5)]
    relations = (
        _relation("person", "app", "HTTPS", why="signs the person in"),
        _relation("app", "person", "notifies", why="when a job finishes"),
        *(_relation("app", e.id, f"writes {e.id}", why="state outlives a restart") for e in below),
        _relation("installer", "store4", "copies a plug-in", why="reviewed, with no deploy"),
    )
    ids = tuple(e.id for e in (*people, app, *below))
    view = View("d", "LR", ids, type="deployment")
    model = _model(*people, app, *below, relations=relations, views=(view,))
    layout = route(model, view)
    assert _crossings(layout) == 0
    assert _tags_crossed(model, view, layout) == []
    # The installer's line skips a tier and runs under the bottom tier, rising into its box.
    installer = layout.routes["installer>store4"]
    store = layout.boxes["store4"]
    assert installer[-1] == (installer[-1][0], store.y + store.h)
    assert min(x for x, _ in installer) < 0


def test_corridor_tracks_nest_the_shorter_line_inside() -> None:
    top = _element("top", tier=1, zone="Top")
    side = _element("side", tier=1, zone="Top")
    middle = _element("middle", tier=2, zone="Middle")
    app = _element("app", kind="system", tier=3, zone="Apps")
    bottom = _element("bottom", tier=4, zone="Bottom")
    relations = (
        _relation("top", "middle", "reaches"),
        _relation("middle", "app", "calls"),
        _relation("app", "bottom", "stores"),
        _relation("top", "bottom", "copies"),
        _relation("app", "side", "asks", status="unknown"),
    )
    view = View("d", "LR", ("top", "side", "middle", "app", "bottom"), type="deployment")
    model = _model(top, side, middle, app, bottom, relations=relations, views=(view,))
    layout = route(model, view)
    track = {key: min(x for x, _ in points) for key, points in layout.routes.items() if min(x for x, _ in points) < 0}
    # The line spanning two tiers runs inside the one that goes on under the bottom tier.
    assert track["app>side"] > track["top>bottom"]


def test_a_zone_that_only_sends_sits_just_above_what_it_reaches() -> None:
    ci = _element("ci", tier=1, zone="CI")
    user = _element("user", kind="person", tier=1, zone="People")
    proxy = _element("proxy", tier=2, zone="Edge")
    app = _element("app", kind="system", tier=3, zone="Apps")
    relations = (_relation("user", "proxy", "HTTPS"), _relation("proxy", "app", "headers"), _relation("ci", "app", "deploys"))
    view = View("d", "LR", ("ci", "user", "proxy", "app"), type="deployment")
    model = _model(ci, user, proxy, app, relations=relations, views=(view,))
    layout = route(model, view)
    assert layout.boxes["ci"].y == layout.boxes["proxy"].y
    assert layout.corridors == 0


def test_a_deployment_draws_the_svg_in_the_theme_and_the_page_links_it() -> None:
    model = _deployment()
    view = model.views["deploy"]
    svg = render_deployment(model, view)
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert ">EDGE</text>" in svg
    assert "Provisioned by infra" in svg
    assert f'stroke="{model.theme["accent"]}" stroke-width="2"' in svg
    assert 'stroke-dasharray="5 4"' in svg
    assert "sessions · state outlives a restart" in svg
    markdown = render_view(model, view)
    link = "[![Where it runs](architecture-views/deploy.svg)](architecture-views/deploy.svg)"
    assert markdown.startswith(f"**Where it runs.** T.\n\n{link}")


def test_a_deployment_svg_is_written_beside_its_document_and_a_changed_one_is_stale(
    tmp_path: Path,
) -> None:
    (tmp_path / ".helix.yml").write_text("flows:\n  - root: .\n")
    (tmp_path / "app.py").write_text("APP = 1\n")
    (tmp_path / "architecture.md").write_text(
        "<!-- architecture-view: where -->\n<!-- /architecture-view -->\n"
    )
    model = tmp_path / "architecture-model.toml"
    element = (
        'kind = "{}"\nstatus = "built"\nevidence = [{{ path = "app.py", contains = "APP" }}]\n'
    )
    model.write_text(
        '[system]\nid = "app"\n'
        '[[element]]\nid = "app"\nname = "App"\ntier = 1\nzone = "Apps"\n'
        + element.format("system")
        + '[[element]]\nid = "db"\nname = "Db"\ntier = 2\nzone = "Data"\n'
        + element.format("store")
        + '[[relation]]\nfrom = "app"\nto = "db"\nlabel = "rows"\nstatus = "built"\n'
        'evidence = [{ path = "app.py", contains = "APP" }]\n'
        '[[view]]\nid = "where"\ntype = "deployment"\nelements = ["app", "db"]\n'
    )
    assert run(check=False, directory=tmp_path, model_path=model) == []
    drawn = tmp_path / "architecture-views" / "where.svg"
    assert ">rows</text>" in drawn.read_text(encoding="utf-8")
    assert run(check=True, directory=tmp_path, model_path=model) == []
    drawn.write_text("<svg/>\n", encoding="utf-8")
    assert run(check=True, directory=tmp_path, model_path=model) == [
        "architecture-views/where.svg: stale; run `documentor views`"
    ]


def test_a_view_may_skip_a_tier_and_a_line_past_a_box_loops_around_it(tmp_path: Path) -> None:
    # Found on a pilot: a view holding tiers 1 and 3 crashed, and a same-tier line
    # between non-adjacent boxes ran through the box between them.
    jobs = _element("jobs", tier=1, zone="Jobs")
    left = _element("left", tier=3, zone="Data")
    middle = _element("middle", tier=3, zone="Data")
    right = _element("right", tier=3, zone="Data")
    relations = (_relation("jobs", "left", "writes"), _relation("left", "right", "feeds"))
    view = View("d", "LR", ("jobs", "left", "middle", "right"), type="deployment")
    model = _model(jobs, left, middle, right, relations=relations, views=(view,))
    layout = route(model, view)
    assert sorted(layout.tiers) == [1, 2]
    feeds = next(y for _, y, text in layout.labels if text == "feeds")
    middle_box = layout.boxes["middle"]
    assert not middle_box.y <= feeds <= middle_box.y + middle_box.h


def test_a_table_cell_keeps_angle_brackets_and_evidence_matches_across_wrapped_lines(
    tmp_path: Path,
) -> None:
    catalog = _element("catalog", layer="Unity Catalog: pipeline_<env>", job="Holds <env> tables.")
    view = View("s", "LR", ("catalog",), type="stack")
    assert "pipeline_&lt;env&gt;" in render_stack(_model(catalog, views=(view,)), view)
    (tmp_path / "notes.md").write_text("The jobs run\nnightly at two.\n")
    wrapped = Element("j", "J", "container", "built", (Evidence("notes.md", "run nightly at"),))
    problems = model_problems(_model(wrapped), tmp_path)
    assert not any("no longer contains" in p for p in problems)


def test_a_dag_draws_only_data_relations_without_labels_and_rejects_a_cycle(
    tmp_path: Path,
) -> None:
    raw = _element("raw", kind="store", layer="Bronze")
    clean = _element("clean", kind="store", layer="Silver", detail="one row per claim")
    gold = _element("gold", kind="store", layer="Gold")
    flow = (
        _relation("raw", "clean", "feeds", data=True),
        _relation("clean", "gold", "feeds", data=True),
        _relation("gold", "raw", "audited by"),
    )
    view = View("dag", "LR", ("raw", "clean", "gold"), type="dag")
    text = render_dag(_model(raw, clean, gold, relations=flow, views=(view,)), view)
    assert "flowchart LR" in text
    assert 'clean(["Clean<br/><small>one row per claim</small>"])' in text
    assert "    raw --> clean" in text
    assert "feeds" not in text
    assert "gold --> raw" not in text
    looped = (*flow, _relation("gold", "raw", "back", data=True))
    model = _model(raw, clean, gold, relations=looped, views=(view,))
    assert "view dag: not a DAG, raw -> clean -> gold -> raw" in model_problems(
        model, _root(tmp_path)
    )


def test_a_deployment_leaves_data_relations_to_the_dag() -> None:
    base = _deployment()
    lineage = _relation("db", "log", "copies", data=True)
    model = replace(base, relations=(*base.relations, lineage))
    labels = [text for _, _, text in route(model, model.views["deploy"]).labels]
    assert "copies" not in labels
    assert "changes" in labels
