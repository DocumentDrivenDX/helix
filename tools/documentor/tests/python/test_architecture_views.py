"""The generated architecture views and the checks that keep them true (HELIX's architecture views)."""

from pathlib import Path


from documentor.architecture.model import (
    DEFAULT_THEME,
    MAX_VIEW_ELEMENTS,
    Element,
    Evidence,
    Group,
    Model,
    Relation,
    System,
    View,
    default_owner,
    fact_problems,
    load,
    model_problems,
)
from documentor.architecture.views import plate_problems, render, replace_views, run



def _evidence(path: str = "app.py", contains: str = "APP") -> tuple[Evidence, ...]:
    return (Evidence(path, contains),)


def _element(element_id: str, **fields: object) -> Element:
    values: dict = {"name": element_id.title(), "kind": "container", "status": "built"}
    values |= fields
    values.setdefault("owner", default_owner(values["kind"], "atlas"))
    return Element(id=element_id, evidence=_evidence(), **values)


ATLAS = System(id="atlas", name="atlas", regenerate="just architecture")


def _model(*elements: Element, relations: tuple[Relation, ...] = (), views=()) -> Model:
    theme = dict(DEFAULT_THEME)
    return Model({e.id: e for e in elements}, relations, {v.id: v for v in views}, (), ATLAS, theme)


def _root(tmp_path: Path) -> Path:
    (tmp_path / "app.py").write_text("APP = 1\n")
    return tmp_path




def test_evidence_that_no_longer_holds_is_reported(tmp_path: Path) -> None:
    root = _root(tmp_path)
    gone = Element("db", "Db", "store", "built", (Evidence("missing.py", "x"),))
    moved = Element("api", "Api", "container", "built", (Evidence("app.py", "ROUTER"),))
    bare = Element("ui", "Ui", "container", "built", ())
    problems = model_problems(_model(gone, moved, bare), root)
    assert problems == [
        "element db: evidence file missing.py does not exist",
        "element api: app.py no longer contains 'ROUTER'",
        "element ui: no evidence",
    ]


def test_unknown_kinds_statuses_and_endpoints_are_reported(tmp_path: Path) -> None:
    odd = _element("odd", kind="robot", status="maybe")
    edge = Relation("odd", "nowhere", "calls", "built", _evidence())
    view = View("context", "LR", ("odd", "ghost"))
    problems = model_problems(_model(odd, relations=(edge,), views=(view,)), _root(tmp_path))
    assert "element odd: unknown kind robot" in problems
    assert "element odd: unknown status maybe" in problems
    assert "relation odd -> nowhere: unknown element nowhere" in problems
    assert "view context: unknown element ghost" in problems


def test_a_view_past_the_ceiling_or_a_group_outside_its_view_is_reported(tmp_path: Path) -> None:
    elements = [_element(f"e{n}") for n in range(MAX_VIEW_ELEMENTS + 1)]
    crowded = View("crowded", "LR", tuple(e.id for e in elements))
    stray = View("stray", "LR", ("e0",), (Group("app", "App", ("e0", "e1")),))
    problems = model_problems(_model(*elements, views=(crowded, stray)), _root(tmp_path))
    assert (
        f"view crowded: {MAX_VIEW_ELEMENTS + 1} elements, ceiling {MAX_VIEW_ELEMENTS}" in problems
    )
    assert "view stray: group app holds e1, not in the view" in problems


def test_a_declared_fact_needs_an_element_and_a_claim_needs_a_declaration() -> None:
    model = _model(_element("prebill", facts=("mcp-server:prebill", "mcp-server:retired")))
    assert fact_problems(model, {"mcp-server:prebill", "app-resource:postgres"}) == [
        "fact app-resource:postgres: declared in configuration, on no element",
        "element prebill: claims mcp-server:retired, which no configuration declares",
    ]


def test_duplicate_ids_are_reported_and_the_first_wins(tmp_path: Path) -> None:
    source = tmp_path / "model.toml"
    source.write_text(
        '[[element]]\nid = "a"\nname = "First"\nkind = "system"\nstatus = "built"\n'
        '[[element]]\nid = "a"\nname = "Second"\nkind = "system"\nstatus = "built"\n'
        '[[view]]\nid = "v"\nelements = ["a"]\n[[view]]\nid = "v"\nelements = []\n'
    )
    model = load(source)
    assert model.elements["a"].name == "First"
    assert model.problems == ("duplicate element id a", "duplicate view id v")




def test_a_view_draws_status_shapes_and_only_the_edges_inside_it() -> None:
    app = _element("app", kind="system")
    db = _element("db", kind="store", detail='Postgres "main"')
    user = _element("user", kind="person")
    walls = _element("walls", kind="external", status="unknown")
    edges = (
        Relation("user", "app", "HTTPS", "built", _evidence()),
        Relation("app", "db", "sessions", "built", _evidence()),
        Relation("app", "walls", "which matters", "unknown", _evidence()),
        Relation("app", "elsewhere", "hidden", "built", _evidence()),
    )
    view = View("context", "LR", ("user", "app", "db", "walls"))
    text = render(_model(app, db, user, walls, relations=edges, views=(view,)), view)
    assert text.startswith("```mermaid\n")
    assert '    db[("Db<br/>Postgres #quot;main#quot;")]' in text
    assert '    user(["User"])' in text
    assert '    user -->|"HTTPS"| app' in text
    assert '    app -.->|"which matters"| walls' in text
    assert "hidden" not in text
    assert "class walls unknown" in text
    assert "classDef placeholder" not in text
    assert "dashed arrow = not built or unknown" in text
    assert "class app atlas" in text
    assert "class db platform" in text
    assert text.splitlines()[1].startswith("%%{init: ")


def test_numbered_steps_are_drawn_heavier_and_explained_below_the_view() -> None:
    user = _element("user", kind="person")
    app = _element("app", kind="system", name="atlas")
    db = _element("db", kind="store", name="Lakebase")
    edges = (
        Relation(
            "app", "db", "sessions", "built", _evidence(), step=2, note="It loads the session."
        ),
        Relation("user", "app", "HTTPS", "built", _evidence(), step=1, note="They sign in."),
        Relation("app", "user", "reply", "built", _evidence()),
    )
    view = View("context", "LR", ("user", "app", "db"), title="Context", takeaway="One app.")
    text = render(_model(user, app, db, relations=edges, views=(view,)), view)
    assert text.startswith("**Context.** One app.\n\n```mermaid\n")
    assert '    app -->|"2 · sessions"| db' in text
    assert '    app -->|"reply"| user' in text
    assert "    linkStyle 0,1 stroke:#111418" in text
    assert "dark numbered arrows = the request, in order" in text
    assert text.index("1. **HTTPS.** They sign in.") < text.index(
        "2. **Sessions.** It loads the session."
    )


def test_steps_that_skip_repeat_or_go_unexplained_are_reported(tmp_path: Path) -> None:
    a, b, c = _element("a"), _element("b"), _element("c")
    edges = (
        Relation("a", "b", "x", "built", _evidence(), step=1, note="First."),
        Relation("b", "c", "y", "built", _evidence(), step=3),
    )
    view = View("v", "LR", ("a", "b", "c"))
    problems = model_problems(_model(a, b, c, relations=edges, views=(view,)), _root(tmp_path))
    assert "view v: steps [1, 3] do not run 1 to 2" in problems
    assert "view v: step 3 (b -> c) has no note" in problems


def test_an_element_built_by_its_owner_and_one_not_built_take_different_classes() -> None:
    plugins = _element("plugins", kind="store", owner="atlas")
    walls = _element("walls", kind="container", status="placeholder")
    view = View("v", "LR", ("plugins", "walls"))
    text = render(_model(plugins, walls, views=(view,)), view)
    assert "class plugins atlas" in text
    assert "class walls placeholder" in text
    assert "amber dashed = a stand-in" in text


def test_an_unknown_owner_is_reported(tmp_path: Path) -> None:
    odd = _element("odd", owner="vendor")
    assert "element odd: unknown owner vendor" in model_problems(_model(odd), _root(tmp_path))


def test_a_group_becomes_a_subgraph_and_its_members_are_drawn_once() -> None:
    model = _model(_element("spa"), _element("api"), _element("db", kind="store"))
    view = View(
        "containers", "TB", ("spa", "api", "db"), (Group("app", "One process", ("spa", "api")),)
    )
    text = render(model, view)
    assert 'subgraph app["One process"]' in text
    assert text.count('spa["Spa"]') == 1
    assert "flowchart TB" in text


def test_only_the_text_between_markers_is_regenerated() -> None:
    end = "<!-- /architecture-view -->\n"
    document = (
        f"Intro prose.\n<!-- architecture-view: context -->\nold drawing\n{end}"
        f"Table prose.\n<!-- architecture-view: retired -->\nx\n{end}"
    )
    updated, problems = replace_views(document, {"context": "NEW\n", "containers": "C\n"})
    assert "<!-- architecture-view: context -->\n\nNEW\n\n<!-- /architecture-view -->" in updated
    assert updated.startswith("Intro prose.\n")
    assert "Table prose.\n" in updated
    assert "old drawing" not in updated
    assert problems == [
        "architecture.md: no view named retired for this document",
        "architecture.md: view containers has no markers",
    ]


def test_a_view_marked_twice_is_reported() -> None:
    block = "<!-- architecture-view: context -->\nx\n<!-- /architecture-view -->\n"
    _, problems = replace_views(block * 2, {"context": "y\n"})
    assert problems == ["architecture.md: view context is marked twice"]



def test_a_view_whose_document_is_missing_is_reported(tmp_path: Path) -> None:
    _root(tmp_path)
    model = tmp_path / "architecture-model.toml"
    model.write_text(
        '[[element]]\nid = "app"\nname = "App"\nkind = "system"\nstatus = "built"\n'
        'evidence = [{ path = "app.py", contains = "APP" }]\n'
        '[[view]]\nid = "context"\nelements = ["app"]\n'
    )
    problems = run(check=True, directory=tmp_path, model_path=model)
    assert any(p.startswith("architecture.md: no such document for views") for p in problems)


def test_a_plate_must_draw_exactly_the_elements_of_its_view(tmp_path: Path) -> None:
    (tmp_path / "plate.html").write_text('<svg><g id="app"></g><g id="legacy"></g></svg>')
    view = View("overview", "LR", ("app", "db"), plate="plate.html")
    assert plate_problems(view, tmp_path) == [
        "plate.html: does not draw db from view overview",
        "plate.html: draws legacy, which view overview does not hold",
    ]
    missing = View("overview", "LR", ("app",), plate="gone.html")
    assert plate_problems(missing, tmp_path) == ["view overview: plate gone.html does not exist"]
    assert plate_problems(View("plain", "LR", ("app",)), tmp_path) == []


def test_a_call_that_runs_throughout_is_drawn_heavy_unnumbered_and_explained_last() -> None:
    app = _element("app", kind="system", name="atlas")
    db = _element("db", kind="store", name="Lakebase")
    log = _element("log", kind="external", name="Collector")
    edges = (
        Relation(
            "app", "db", "session", "built", _evidence(), step=1, note="It locks the session."
        ),
        Relation("app", "log", "spans", "built", _evidence(), throughout=True, note="Every call."),
    )
    view = View("context", "LR", ("app", "db", "log"))
    text = render(_model(app, db, log, relations=edges, views=(view,)), view)
    assert '    app -->|"throughout · spans"| log' in text
    assert "    linkStyle 0,1 stroke:#111418" in text
    assert "throughout = runs for the whole request" in text
    assert text.index("1. **Session.**") < text.index("**Throughout: spans.** Every call.")


def test_a_call_that_runs_throughout_needs_a_note_and_no_step(tmp_path: Path) -> None:
    a, b = _element("a"), _element("b")
    both = Relation("a", "b", "x", "built", _evidence(), step=1, note="n", throughout=True)
    view = View("v", "LR", ("a", "b"))
    problems = model_problems(_model(a, b, relations=(both,), views=(view,)), _root(tmp_path))
    assert "view v: a -> b runs throughout, so it needs a note and no step" in problems
