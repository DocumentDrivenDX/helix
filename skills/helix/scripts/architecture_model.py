"""A project's architecture model, and the checks that keep it true to the code.

The model is `<helix root>/02-design/architecture-model.toml` (workflows/references/
architecture-model.md): the project's system, its elements and the relations between them, each
citing a file and a string the file must contain, and the views that draw a subset of them.
`architecture_views.py` renders the views. A `[theme]` block sets the colors, and `[system] facts`
names a script whose `declared_facts(root)` lists the external systems the configuration declares,
so one added without a place in the views fails the check. Standard library only; Python 3.11 or
later. Projects that must check this without the HELIX plugin vendor this file unchanged.
"""

import importlib.util
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

KINDS = frozenset({"person", "system", "container", "store", "external"})
STATUSES = frozenset({"built", "placeholder", "decided", "unknown"})
# A view past this many elements is split, not shrunk (diagram-design.md).
MAX_VIEW_ELEMENTS = 15
_HELIX_ROOT = re.compile(r"^\s*root:\s*['\"]?([^'\"\s#]+)", re.M)

# Colors when the model sets no [theme]: a neutral palette, one accent for the project's own code.
DEFAULT_THEME = {
    "ground": "#EEF1F4",
    "sunken": "#F7F8FA",
    "surface": "#FFFFFF",
    "border": "#D9DEE5",
    "recessed": "#CFD6DF",
    "text": "#2E3440",
    "strong": "#111418",
    "muted": "#5E6875",
    "accent": "#2F6F8F",
    "limited": "#986A24",
    "purchasing": "#4A5A7A",
    "evaluation": "#777268",
    "font": "ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
    "accent_name": "blue",
    "ground_name": "gray",
}


def find_root(start: Path) -> Path:
    """The nearest directory at or above `start` with a .helix.yml, else with .git."""
    for marker in (".helix.yml", ".git"):
        for parent in (start.resolve(), *start.resolve().parents):
            if (parent / marker).exists():
                return parent
    return start.resolve()


def default_model(root: Path) -> Path:
    """`<helix root>/02-design/architecture-model.toml`, the HELIX root read from .helix.yml."""
    config = root / ".helix.yml"
    found = _HELIX_ROOT.search(config.read_text(encoding="utf-8")) if config.is_file() else None
    return root / (found[1] if found else "docs/helix") / "02-design" / "architecture-model.toml"


ROOT = find_root(Path.cwd())
MODEL = default_model(ROOT)
DESIGN = MODEL.parent


@dataclass(frozen=True)
class Evidence:
    path: str
    contains: str


@dataclass(frozen=True)
class Element:
    id: str
    name: str
    kind: str
    status: str
    evidence: tuple[Evidence, ...]
    detail: str = ""
    facts: tuple[str, ...] = ()
    owner: str = "platform"
    # Another repository's system, by that repository's [system] id (the estate check).
    system: str = ""
    # For the generated pages: the element's job in one line (cast), its layer (stack), and where
    # it runs: a tier, counted from the top, and the zone that hosts it (deployment).
    job: str = ""
    layer: str = ""
    tier: int = 0
    zone: str = ""


@dataclass(frozen=True)
class Relation:
    source: str
    target: str
    label: str
    status: str
    evidence: tuple[Evidence, ...]
    # A step in the view's numbered reading order (1, 2, ...), with the sentence that explains it.
    step: int = 0
    note: str = ""
    # A call that runs for the whole numbered path, such as the spans: drawn heavy, never numbered.
    throughout: bool = False
    # Why the traffic goes this way, shown beside the label on a deployment view.
    why: str = ""
    # Data flowing between stages (a table feeding the next), not a call: a dag view draws only
    # these, and a deployment view leaves them out, so architecture and lineage stay apart.
    data: bool = False


@dataclass(frozen=True)
class Group:
    id: str
    label: str
    elements: tuple[str, ...]


@dataclass(frozen=True)
class View:
    id: str
    direction: str
    elements: tuple[str, ...]
    groups: tuple[Group, ...] = ()
    title: str = ""
    takeaway: str = ""
    # The document that holds the view's markers, relative to the model's directory.
    document: str = "architecture.md"
    # A hand-drawn presentation of the view, whose element groups must match it.
    plate: str = ""
    # flowchart (the default), stack, cast, deployment, or journey; a journey view draws `journey`.
    type: str = "flowchart"
    journey: str = ""


@dataclass(frozen=True)
class Step:
    """One step of a journey: a relation the model holds, told as this journey tells it."""

    source: str
    target: str
    label: str


@dataclass(frozen=True)
class Journey:
    id: str
    title: str
    takeaway: str
    steps: tuple[Step, ...]


@dataclass(frozen=True)
class System:
    """The project's own system: its id names the class of its own code."""

    id: str = "system"
    name: str = "the system"
    facts: str = ""
    regenerate: str = "architecture_views.py"


@dataclass(frozen=True)
class Model:
    elements: dict[str, Element]
    relations: tuple[Relation, ...]
    views: dict[str, View]
    problems: tuple[str, ...] = field(default=())
    system: System = System()
    theme: dict = field(default_factory=lambda: dict(DEFAULT_THEME))
    journeys: dict[str, Journey] = field(default_factory=dict)
    # A deployment zone's caption, by zone name: what deploys or provisions it, say.
    zones: dict[str, str] = field(default_factory=dict)


def default_owner(kind: str, system: str = "system") -> str:
    """The owner an element of this kind has unless it names one."""
    return {"person": "person", "system": system, "container": system}.get(kind, "platform")


def _evidence(entry: dict) -> tuple[Evidence, ...]:
    return tuple(Evidence(e["path"], e["contains"]) for e in entry.get("evidence", []))


def _element(entry: dict, system: str) -> Element:
    return Element(
        id=entry["id"],
        name=entry["name"],
        kind=entry["kind"],
        status=entry["status"],
        evidence=_evidence(entry),
        detail=entry.get("detail", ""),
        facts=tuple(entry.get("facts", [])),
        owner=entry.get("owner", default_owner(entry["kind"], system)),
        system=entry.get("system", ""),
        job=entry.get("job", ""),
        layer=entry.get("layer", ""),
        tier=entry.get("tier", 0),
        zone=entry.get("zone", ""),
    )


def _relation(entry: dict) -> Relation:
    return Relation(
        source=entry["from"],
        target=entry["to"],
        label=entry["label"],
        status=entry["status"],
        evidence=_evidence(entry),
        step=entry.get("step", 0),
        note=entry.get("note", ""),
        throughout=entry.get("throughout", False),
        why=entry.get("why", ""),
        data=entry.get("data", False),
    )


def _view(entry: dict) -> View:
    groups = tuple(Group(g["id"], g["label"], tuple(g["elements"])) for g in entry.get("group", []))
    return View(
        id=entry["id"],
        direction=entry.get("direction", "LR"),
        elements=tuple(entry["elements"]),
        groups=groups,
        title=entry.get("title", ""),
        takeaway=entry.get("takeaway", ""),
        document=entry.get("document", "architecture.md"),
        plate=entry.get("plate", ""),
        type=entry.get("type", "flowchart"),
        journey=entry.get("journey", ""),
    )


def _journey(entry: dict) -> Journey:
    steps = tuple(Step(s["from"], s["to"], s["label"]) for s in entry.get("step", []))
    return Journey(entry["id"], entry.get("title", ""), entry.get("takeaway", ""), steps)


def _system(raw: dict) -> System:
    block = raw.get("system", {})
    system_id = block.get("id", "system")
    named = next((e for e in raw.get("element", []) if e.get("id") == system_id), {})
    return System(
        id=system_id,
        name=named.get("name", system_id),
        facts=block.get("facts", ""),
        regenerate=block.get("regenerate", System.regenerate),
    )


def load(path: Path | None = None) -> Model:
    """Read the model; a duplicate id is reported, and the first definition wins."""
    raw = tomllib.loads((path or MODEL).read_text(encoding="utf-8"))
    system = _system(raw)
    elements: dict[str, Element] = {}
    views: dict[str, View] = {}
    problems: list[str] = []
    for element in (_element(entry, system.id) for entry in raw.get("element", [])):
        if element.id in elements:
            problems.append(f"duplicate element id {element.id}")
        elements.setdefault(element.id, element)
    for view in map(_view, raw.get("view", [])):
        if view.id in views:
            problems.append(f"duplicate view id {view.id}")
        views.setdefault(view.id, view)
    relations = tuple(map(_relation, raw.get("relation", [])))
    theme = DEFAULT_THEME | raw.get("theme", {})
    journeys = {j.id: j for j in map(_journey, raw.get("journey", []))}
    zones = {z["name"]: z.get("caption", "") for z in raw.get("zone", [])}
    return Model(elements, relations, views, tuple(problems), system, theme, journeys, zones)


# --- checks -------------------------------------------------------------------------------------


def _flat(text: str) -> str:
    """Whitespace collapsed, so evidence still matches prose that wraps at a different column."""
    return " ".join(text.split())


def _evidence_problems(owner: str, evidence: tuple[Evidence, ...], root: Path) -> list[str]:
    if not evidence:
        return [f"{owner}: no evidence"]
    problems: list[str] = []
    for item in evidence:
        target = root / item.path
        if not target.is_file():
            problems.append(f"{owner}: evidence file {item.path} does not exist")
        elif _flat(item.contains) not in _flat(target.read_text(encoding="utf-8")):
            problems.append(f"{owner}: {item.path} no longer contains {item.contains!r}")
    return problems


def _element_problems(model: Model, root: Path) -> list[str]:
    owners = {"person", "platform", model.system.id}
    problems: list[str] = []
    for element in model.elements.values():
        owner = f"element {element.id}"
        if element.kind not in KINDS:
            problems.append(f"{owner}: unknown kind {element.kind}")
        if element.status not in STATUSES:
            problems.append(f"{owner}: unknown status {element.status}")
        if element.owner not in owners:
            problems.append(f"{owner}: unknown owner {element.owner}")
        problems += _evidence_problems(owner, element.evidence, root)
    return problems


def _relation_problems(model: Model, root: Path) -> list[str]:
    problems: list[str] = []
    for relation in model.relations:
        owner = f"relation {relation.source} -> {relation.target}"
        missing = [end for end in (relation.source, relation.target) if end not in model.elements]
        problems += [f"{owner}: unknown element {end}" for end in missing]
        if relation.status not in STATUSES:
            problems.append(f"{owner}: unknown status {relation.status}")
        problems += _evidence_problems(owner, relation.evidence, root)
    return problems


def _view_problems(model: Model) -> list[str]:
    problems: list[str] = []
    for view in model.views.values():
        owner = f"view {view.id}"
        problems += [
            f"{owner}: unknown element {e}" for e in view.elements if e not in model.elements
        ]
        if len(view.elements) > MAX_VIEW_ELEMENTS:
            problems.append(f"{owner}: {len(view.elements)} elements, ceiling {MAX_VIEW_ELEMENTS}")
        for group in view.groups:
            stray = [e for e in group.elements if e not in view.elements]
            problems += [f"{owner}: group {group.id} holds {e}, not in the view" for e in stray]
    return problems


def shown_relations(model: Model, view: View) -> list[Relation]:
    """The relations a view draws: those with both ends in it, in model order."""
    shown = set(view.elements)
    return [r for r in model.relations if r.source in shown and r.target in shown]


def _step_problems(model: Model) -> list[str]:
    """A view's numbered steps run 1, 2, ... with no gap or repeat, and each one is explained."""
    problems: list[str] = []
    for view in model.views.values():
        if view.type != "flowchart":
            continue  # only a flowchart numbers its arrows; tables and other drawings ignore steps
        edges = shown_relations(model, view)
        stepped = [r for r in edges if r.step]
        steps = sorted(r.step for r in stepped)
        if steps != list(range(1, len(steps) + 1)):
            problems.append(f"view {view.id}: steps {steps} do not run 1 to {len(steps)}")
        problems += [
            f"view {view.id}: step {r.step} ({r.source} -> {r.target}) has no note"
            for r in stepped
            if not r.note
        ]
        problems += [
            f"view {view.id}: {r.source} -> {r.target} runs throughout, so it needs a "
            "note and no step"
            for r in edges
            if r.throughout and (r.step or not r.note)
        ]
    return problems


VIEW_TYPES = {
    "flowchart": "",
    "stack": "layer",
    "cast": "job",
    "deployment": "zone",
    "journey": "",
    "dag": "",
    "field-guide": "",  # lanes are the view's groups; architecture_field_guide.py checks them
}


def _cycle(model: Model, view: View) -> list[str]:
    """A cycle among the view's relations, as element ids, or nothing when it is a DAG."""
    shown = set(view.elements)
    after: dict[str, list[str]] = {e: [] for e in shown}
    for r in model.relations:
        if r.data and r.source in shown and r.target in shown:
            after[r.source].append(r.target)
    state: dict[str, int] = {}
    path: list[str] = []

    def visit(node: str) -> list[str]:
        state[node] = 1
        path.append(node)
        for nxt in after[node]:
            if state.get(nxt) == 1:
                return [*path[path.index(nxt) :], nxt]
            if nxt not in state and (found := visit(nxt)):
                return found
        state[node] = 2
        path.pop()
        return []

    for node in view.elements:
        if node in shown and node not in state and (found := visit(node)):
            return found
    return []


def _page_problems(model: Model) -> list[str]:
    """Each view's type is known, and its elements carry the field that type draws from."""
    problems: list[str] = []
    for view in model.views.values():
        if view.type not in VIEW_TYPES:
            problems.append(f"view {view.id}: unknown type {view.type}")
            continue
        needed = VIEW_TYPES[view.type]
        bare = [e for e in view.elements if e in model.elements and not _has(model, e, needed)]
        problems += [f"view {view.id}: element {e} has no {needed}" for e in bare]
        if view.type == "deployment":
            problems += [
                f"view {view.id}: element {e} has no tier"
                for e in view.elements
                if e in model.elements and model.elements[e].tier < 1
            ]
        if view.type == "dag" and (cycle := _cycle(model, view)):
            problems.append(f"view {view.id}: not a DAG, {' -> '.join(cycle)}")
        if view.type == "journey" and view.journey not in model.journeys:
            problems.append(f"view {view.id}: no journey named {view.journey!r}")
    return problems


def _has(model: Model, element_id: str, name: str) -> bool:
    return not name or bool(getattr(model.elements[element_id], name))


def _journey_problems(model: Model) -> list[str]:
    """A journey's steps walk relations the model holds, in either direction, or stay on one."""
    pairs = {(r.source, r.target) for r in model.relations}
    problems: list[str] = []
    for journey in model.journeys.values():
        for number, step in enumerate(journey.steps, start=1):
            owner = f"journey {journey.id} step {number}"
            missing = [e for e in (step.source, step.target) if e not in model.elements]
            problems += [f"{owner}: unknown element {e}" for e in missing]
            walked = (step.source, step.target) in pairs or (step.target, step.source) in pairs
            if not missing and step.source != step.target and not walked:
                problems.append(f"{owner}: no relation {step.source} -> {step.target}")
    return problems


def fact_problems(model: Model, declared: set[str]) -> list[str]:
    """Each declared fact is claimed by an element, and each claim is still declared."""
    claimed = {fact: e.id for e in model.elements.values() for fact in e.facts}
    unclaimed = sorted(declared - claimed.keys())
    stale = sorted(claimed.keys() - declared)
    return [f"fact {fact}: declared in configuration, on no element" for fact in unclaimed] + [
        f"element {claimed[fact]}: claims {fact}, which no configuration declares" for fact in stale
    ]


def declared_facts(model: Model, root: Path) -> set[str]:
    """What the project's facts script (`[system] facts`) finds; nothing when it names none."""
    if not model.system.facts:
        return set()
    spec = importlib.util.spec_from_file_location("architecture_facts", root / model.system.facts)
    if spec is None or spec.loader is None:
        raise SystemExit(f"cannot load the facts script {model.system.facts}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return set(module.declared_facts(root))


def model_problems(model: Model, root: Path = ROOT) -> list[str]:
    """Everything wrong with the model itself, before any view is rendered."""
    return [
        *model.problems,
        *_element_problems(model, root),
        *_relation_problems(model, root),
        *_view_problems(model),
        *_step_problems(model),
        *_page_problems(model),
        *_journey_problems(model),
    ]
