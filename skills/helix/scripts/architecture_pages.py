"""The stack, cast, and journey views of a project's architecture model (architecture_model.py).

A flowchart answers where a piece sits only as well as its layout allows. These views each answer
one question in the form that suits it: a stack shows where each piece sits, read top to bottom,
with no arrows; a cast says what each piece does, one line each; a journey shows how the pieces
work together, one request at a time, as a sequence. Each is Markdown or Mermaid, so the repository
host renders it. Standard library only. Projects that must run this without the HELIX plugin vendor
it unchanged.
"""

import json

if __package__:
    from .architecture_model import Element, Journey, Model, View
else:  # run as a script: the sibling module is on the path
    from architecture_model import Element, Journey, Model, View

_STATUS = {
    "placeholder": "stand-in",
    "decided": "decided, not built",
    "unknown": "unknown",
}


def _cell(value: str) -> str:
    escaped = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return escaped.replace("|", "\\|").replace("\n", " ")


def _status(element: Element) -> str:
    return _STATUS.get(element.status, "built")


def _lead(view: View) -> str:
    return f"**{view.title}.** {view.takeaway}\n\n" if view.title else ""


def render_stack(model: Model, view: View) -> str:
    """Each layer, top to bottom, with the pieces it holds; the order is the reading order."""
    layers: dict[str, list[Element]] = {}
    for element_id in view.elements:
        element = model.elements[element_id]
        layers.setdefault(element.layer, []).append(element)
    rows = ["| Layer | What sits there |", "|---|---|"]
    for layer, members in layers.items():
        pieces = []
        for element in members:
            note = "" if element.status == "built" else f" ({_status(element)})"
            pieces.append(f"**{_cell(element.name)}**{note}")
        rows.append(f"| {_cell(layer)} | {' · '.join(pieces)} |")
    return _lead(view) + "\n".join(rows) + "\n"


def render_cast(model: Model, view: View) -> str:
    """One row per piece: its job in one line, and how far it is built."""
    rows = ["| Piece | Its job | Status |", "|---|---|---|"]
    for element_id in view.elements:
        element = model.elements[element_id]
        name = f"**{_cell(element.name)}**"
        if element.system:
            name += f" ({element.system})"
        rows.append(f"| {name} | {_cell(element.job)} | {_status(element)} |")
    return _lead(view) + "\n".join(rows) + "\n"


def _participants(model: Model, journey: Journey) -> list[str]:
    seen: list[str] = []
    for step in journey.steps:
        for end in (step.source, step.target):
            if end not in seen:
                seen.append(end)
    return seen


def _sequence_theme(theme: dict) -> str:
    """The model's colors for a Mermaid sequence: participants, lifelines, arrows, and notes."""
    variables = {
        "fontFamily": theme["font"],
        "actorBkg": theme["surface"],
        "actorBorder": theme["border"],
        "actorTextColor": theme["strong"],
        "actorLineColor": theme["recessed"],
        "signalColor": theme["muted"],
        "signalTextColor": theme["strong"],
        "sequenceNumberColor": theme["surface"],
        "noteBkgColor": theme["sunken"],
        "noteBorderColor": theme["border"],
    }
    init = {"theme": "base", "fontFamily": theme["font"], "themeVariables": variables}
    return f"%%{{init: {json.dumps(init)}}}%%"


def render_journey(model: Model, view: View) -> str:
    """One journey as a Mermaid sequence: participants in order of appearance, steps numbered."""
    journey = model.journeys[view.journey]
    forward = {(r.source, r.target) for r in model.relations}
    lines = [_sequence_theme(model.theme), "sequenceDiagram"]
    for element_id in _participants(model, journey):
        lines.append(f"    participant {element_id} as {model.elements[element_id].name}")
    for number, step in enumerate(journey.steps, start=1):
        reply = (step.source, step.target) not in forward and step.source != step.target
        arrow = "-->>" if reply else "->>"
        label = step.label.replace(";", ",").replace("#", "")
        lines.append(f"    {step.source}{arrow}{step.target}: {number} · {label}")
    title = journey.title or view.title
    lead = f"**{title}.** {journey.takeaway or view.takeaway}\n\n" if title else ""
    return lead + "```mermaid\n" + "\n".join(lines) + "\n```\n"


def _flow_theme(theme: dict) -> str:
    """The model's colors for a Mermaid flowchart: stages, layers, and arrows."""
    variables = {
        "fontFamily": theme["font"],
        "primaryColor": theme["surface"],
        "primaryBorderColor": theme["border"],
        "primaryTextColor": theme["strong"],
        "lineColor": theme["muted"],
        "clusterBkg": theme["sunken"],
        "clusterBorder": theme["recessed"],
    }
    init = {"theme": "base", "fontFamily": theme["font"], "themeVariables": variables}
    return f"%%{{init: {json.dumps(init)}}}%%"


def render_dag(model: Model, view: View) -> str:
    """Data flow as a left-to-right DAG, the way a job graph is drawn: each stage sits one column
    after what feeds it, so the columns are the dependency order.

    Only relations marked `data = true` are drawn, and they carry no labels: in a pipeline the
    arrow already says "feeds". Architecture (where each piece runs, and what it calls and why)
    belongs in a deployment view, which leaves data relations out.
    """
    shown = set(view.elements)
    lines = [_flow_theme(model.theme), "flowchart LR"]
    for element_id in view.elements:
        element = model.elements[element_id]
        detail = f"<br/><small>{_cell(element.detail)}</small>" if element.detail else ""
        lines.append(f'    {element.id}(["{_cell(element.name)}{detail}"])')
    for r in model.relations:
        if r.data and r.source in shown and r.target in shown:
            lines.append(f"    {r.source} {'-->' if r.status == 'built' else '-.->'} {r.target}")
    return _lead(view) + "```mermaid\n" + "\n".join(lines) + "\n```\n"
