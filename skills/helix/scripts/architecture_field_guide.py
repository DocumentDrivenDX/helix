"""The architecture field guide: a developer-orientation page drawn from the model.

A field-guide view is a whole page, not a marked block: a takeaway headline; a wide plate with
responsibility lanes (the view's groups, left to right), a shaded region around the lane the
system owns, the request's path as numbered steps, the call that runs throughout, and other
calls drawn quiet; a legend; the walkthrough beside the plate; and the sources and limits.
HELIX's diagram standard names that composition (workflows/references/diagram-design.md,
"Architecture field guide"); the model supplies every fact, and the layout is arithmetic on the
lanes, so a model change redraws the page and `--check` fails when it is stale. This module checks
the view and draws the plate (inline SVG); architecture_field_page.py wraps it in the page.
Standard library only.
"""

from dataclasses import dataclass, field
from html import escape

if __package__:
    from .architecture_deploy import Box
    from .architecture_model import Element, Model, Relation, View
else:  # run as a script: the sibling modules are on the path
    from architecture_deploy import Box
    from architecture_model import Element, Model, Relation, View

PAD, HEAD, LANE_GAP, FAN_GAP, NODE_GAP, RIM, AXIS_H = 50, 64, 104, 130, 26, 20, 104
MIN_W, MAX_W, NAME_PX, DETAIL_PX, LABEL_PX, LABEL_CHARS = 190, 300, 11.5, 7.4, 7.2, 20
TYPE = "field-guide"


@dataclass
class Node:
    element: Element
    box: Box
    name: list[str]
    detail: list[str]


@dataclass
class Lane:
    title: str
    ids: tuple[str, ...]
    x: float = 0
    w: float = 0
    owned: bool = False


@dataclass
class Plate:
    lanes: list[Lane]
    nodes: dict[str, Node]
    width: float
    height: float
    lane_of: dict[str, int] = field(default_factory=dict)
    gaps: list[float] = field(default_factory=list)  # after each lane


@dataclass
class Line:
    relation: Relation
    path: str
    label_at: tuple[float, float]
    anchor: str
    mark_at: tuple[float, float]


# --- checks -------------------------------------------------------------------------------------


def field_guide_problems(model: Model, view: View) -> list[str]:
    """A field guide needs its lanes, every element in one lane, and every numbered step on it."""
    if view.type != TYPE:
        return []
    problems: list[str] = []
    if not view.groups:
        problems.append(f"view {view.id}: a field guide needs groups, one per lane, left to right")
    grouped = [e for g in view.groups for e in g.elements]
    problems += [f"view {view.id}: {e} is in no lane" for e in view.elements if e not in grouped]
    doubled = [e for e in sorted(set(grouped)) if grouped.count(e) > 1]
    problems += [f"view {view.id}: {e} is in two lanes" for e in doubled]
    for r in model.relations:
        if r.step and (r.source not in view.elements or r.target not in view.elements):
            problems.append(
                f"view {view.id}: step {r.step} ({r.source} to {r.target}) is off the plate"
            )
    if not view.document.endswith(".html"):
        problems.append(f"view {view.id}: a field guide's document is the HTML page it writes")
    return problems


# --- layout -------------------------------------------------------------------------------------


def _wrap(text: str, chars: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and len(trial) > chars:
            lines.append(line)
            line = word
        else:
            line = trial
    return [*lines, line] if line else []


def _node(element: Element) -> Node:
    widest = max(len(element.name) * NAME_PX, len(element.detail) * DETAIL_PX) + 40
    w = max(MIN_W, min(MAX_W, widest))
    name = _wrap(element.name, int((w - 40) / NAME_PX))
    detail = _wrap(element.detail, int((w - 40) / DETAIL_PX))
    return Node(element, Box(0, 0, w, 40 + 26 * len(name) + 20 * len(detail)), name, detail)


def _stack(lane: Lane, nodes: dict[str, Node]) -> float:
    return sum(nodes[e].box.h for e in lane.ids) + NODE_GAP * (len(lane.ids) - 1)


def layout(model: Model, view: View) -> Plate:
    """Lanes left to right, each lane's boxes stacked and centered on one shared axis."""
    nodes = {e: _node(model.elements[e]) for e in view.elements}
    lanes = [Lane(g.label, g.elements) for g in view.groups]
    for lane in lanes:
        lane.w = max(nodes[e].box.w for e in lane.ids)
        lane.owned = all(model.elements[e].owner == model.system.id for e in lane.ids)
        for e in lane.ids:
            nodes[e].box.w = lane.w
        if len(lane.ids) == 1:  # a station on the request's path: room for the lines it sends
            nodes[lane.ids[0]].box.h = max(nodes[lane.ids[0]].box.h, AXIS_H)
    tallest = max(_stack(lane, nodes) for lane in lanes)
    lane_of = {e: i for i, lane in enumerate(lanes) for e in lane.ids}
    gaps = _gaps(model, view, lane_of, len(lanes))
    axis, x = HEAD + tallest / 2, float(PAD)
    for i, lane in enumerate(lanes):
        lane.x, y = x, axis - _stack(lane, nodes) / 2
        for e in lane.ids:
            nodes[e].box.x, nodes[e].box.y = x, y
            y += nodes[e].box.h + NODE_GAP
        x += lane.w + gaps[i]
    return Plate(lanes, nodes, x - gaps[-1] + PAD, HEAD + tallest + PAD, lane_of, gaps)


def _label_lines(label: str) -> list[str]:
    """A label on one line, or on two when one line would spill past its gap onto a box."""
    if len(label) <= LABEL_CHARS:
        return [label]
    return _wrap(label, -(-len(label) // 2) + 4) or [label]


def _gaps(model: Model, view: View, lane_of: dict[str, int], count: int) -> list[float]:
    """The gap after each lane: wide enough for the longest label line that crosses it."""
    gaps = [float(LANE_GAP)] * count
    fans: dict[str, int] = {}
    for r in shown(model, view):
        i = lane_of[r.source]
        if lane_of[r.target] == i + 1:
            widest = max(len(line) for line in _label_lines(r.label)) * LABEL_PX
            gaps[i] = max(gaps[i], widest + 30)
            fans[r.source] = fans.get(r.source, 0) + 1
    for source, count_out in fans.items():
        if count_out > 1:  # a fan needs room for its corridors and their labels
            gaps[lane_of[source]] = max(gaps[lane_of[source]], FAN_GAP)
    return gaps


# --- routing ------------------------------------------------------------------------------------


def _over(src: Box, tgt: Box, r: Relation, up: bool) -> Line:
    """A line that leaves by the top (or bottom) of its box for a target wholly above (or below)."""
    y0 = src.y if up else src.y + src.h
    path = f"M{src.cx:.0f} {y0:.0f}V{tgt.cy:.0f}H{tgt.x:.0f}"
    long_run = abs(tgt.cy - y0) >= 90
    mark = (src.cx, (y0 + tgt.cy) / 2) if long_run else ((src.cx + tgt.x) / 2, tgt.cy)
    return Line(r, path, (tgt.x - 10, tgt.cy - 19), "end", mark)


def _fan(plate: Plate, source: str, edges: list[Relation]) -> list[Line]:
    """Lines from one box into the next lane: the topmost target wholly above the box is reached
    from its top and the bottommost wholly below from its bottom; the rest leave by the right
    side, spread in the order of their targets (_side)."""
    src = plate.nodes[source].box
    edges = sorted(edges, key=lambda r: plate.nodes[r.target].box.cy)
    out, side = [], []
    for r in edges:
        tgt = plate.nodes[r.target].box
        if r is edges[0] and tgt.y + tgt.h < src.y:
            out.append(_over(src, tgt, r, up=True))
        elif r is edges[-1] and tgt.y > src.y + src.h:
            out.append(_over(src, tgt, r, up=False))
        else:
            side.append(r)
    return out + _side(plate, source, side)


def _side(plate: Plate, source: str, edges: list[Relation]) -> list[Line]:
    """Exits spread down the box's right side in the order of their targets, each line that
    climbs or drops taking its own corridor, the outermost target on the innermost corridor so
    no two cross; a target level with its exit gets a straight run."""
    src = plate.nodes[source].box
    exits = {r: src.y + src.h * (k + 1) / (len(edges) + 1) for k, r in enumerate(edges)}
    target_y = {r: plate.nodes[r.target].box.cy for r in edges}
    ups = sorted((r for r in edges if target_y[r] < exits[r] - 10), key=lambda r: target_y[r])
    downs = sorted((r for r in edges if target_y[r] > exits[r] + 10), key=lambda r: -target_y[r])
    slots = {r: k for group in (ups, downs) for k, r in enumerate(group)}
    width = max(len(ups), len(downs), 1)
    out = []
    for r in edges:
        tgt, y, right = plate.nodes[r.target].box, exits[r], src.x + src.w
        if r not in slots:
            mid = (right + tgt.x) / 2
            straight = f"M{right:.0f} {y:.0f}H{tgt.x:.0f}"
            out.append(Line(r, straight, (mid, y - 19), "middle", (mid, y)))
            continue
        cx = right + plate.gaps[plate.lane_of[source]] * (slots[r] + 1) / (width + 1)
        path = f"M{right:.0f} {y:.0f}H{cx:.0f}V{tgt.cy:.0f}H{tgt.x:.0f}"
        # The label sits over the entry run, so a mark goes on the climb, or on a long drop, where
        # the label cannot reach; on a short drop it goes on the entry run instead.
        climb = tgt.cy < y or tgt.cy - y >= 90
        mark = (cx, (y + tgt.cy) / 2) if climb else ((cx + tgt.x) / 2, tgt.cy)
        out.append(Line(r, path, (tgt.x - 10, tgt.cy - 19), "end", mark))
    return out


def _vertical(plate: Plate, r: Relation) -> Line:
    """A line between two boxes in one lane: straight down (or up) between them."""
    a, b = plate.nodes[r.source].box, plate.nodes[r.target].box
    if b.y >= a.y + a.h:
        top, bottom = a.y + a.h, b.y
        path = f"M{a.cx:.0f} {top:.0f}V{bottom:.0f}"
    else:
        top, bottom = b.y + b.h, a.y
        path = f"M{a.cx:.0f} {bottom:.0f}V{top:.0f}"
    mid = (top + bottom) / 2
    return Line(r, path, (a.cx + 18, mid + 5), "start", (a.cx, mid))


def _perimeter(plate: Plate, r: Relation, hop: int) -> Line:
    """A line that skips a lane runs over the top; one that goes back runs under the bottom."""
    a, b = plate.nodes[r.source].box, plate.nodes[r.target].box
    if hop > 0:
        y = 22.0
        path = f"M{a.cx:.0f} {a.y:.0f}V{y:.0f}H{b.cx:.0f}V{b.y:.0f}"
    else:
        y = plate.height - 18
        path = f"M{a.cx:.0f} {a.y + a.h:.0f}V{y:.0f}H{b.cx:.0f}V{b.y + b.h:.0f}"
    mid = (a.cx + b.cx) / 2
    return Line(r, path, (mid, y - 9), "middle", (mid, y))


def shown(model: Model, view: View) -> list[Relation]:
    """The relations drawn: both ends on the plate, no self-calls, data flow left to a DAG."""
    on = set(view.elements)
    return [
        r
        for r in model.relations
        if {r.source, r.target} <= on and r.source != r.target and not r.data
    ]


def route(plate: Plate, relations: list[Relation]) -> list[Line]:
    lines: list[Line] = []
    forward: dict[str, list[Relation]] = {}
    for r in relations:
        hop = plate.lane_of[r.target] - plate.lane_of[r.source]
        if hop == 1:
            forward.setdefault(r.source, []).append(r)
        elif hop == 0:
            lines.append(_vertical(plate, r))
        else:
            lines.append(_perimeter(plate, r, hop))
    for source, edges in forward.items():
        lines += _fan(plate, source, edges)
    return lines


# --- the SVG ------------------------------------------------------------------------------------


def _text(at: tuple[float, float], text: str, attrs: str) -> str:
    return f'<text x="{at[0]:.0f}" y="{at[1]:.0f}" {attrs}>{escape(text)}</text>'


def _svg_lanes(plate: Plate) -> list[str]:
    out = []
    for i, lane in enumerate(plate.lanes):
        out.append(_text((lane.x, 50), f"{i + 1:02d} / {lane.title.upper()}", 'class="lane"'))
        if lane.owned or len(lane.ids) > 1:
            kind = "owned" if lane.owned else "platform"
            out.append(
                f'<rect x="{lane.x - RIM:.0f}" y="{HEAD - 12}" width="{lane.w + 2 * RIM:.0f}" '
                f'height="{plate.height - HEAD - PAD / 2 + 12:.0f}" rx="16" class="{kind}"/>'
            )
    return out


def _svg_nodes(plate: Plate, system: str) -> list[str]:
    out = []
    for e, node in plate.nodes.items():
        b, person = node.box, node.element.kind == "person"
        own = "own" if node.element.owner == system else "node"
        out.append(f'<g id="{escape(e)}">')
        out.append(
            f'<rect x="{b.x:.0f}" y="{b.y:.0f}" width="{b.w:.0f}" height="{b.h:.0f}" '
            f'rx="{b.h / 2 if person else 10:.0f}" class="{own}"/>'
        )
        x, y = b.x + (30 if person else 20), b.y + 32
        for line in node.name:
            out.append(_text((x, y), line, 'class="name"'))
            y += 26
        for line in node.detail:
            out.append(_text((x, y - 4), line, 'class="detail"'))
            y += 20
        out.append("</g>")
    return out


def _svg_lines(lines: list[Line]) -> list[str]:
    out = []
    for line in lines:
        r = line.relation
        heavy = r.step or r.throughout
        out.append(f'<path d="{line.path}" class="{"edge" if heavy else "quiet"}"/>')
        texts, (x, y) = (
            [r.label] if line.anchor == "start" else _label_lines(r.label),
            line.label_at,
        )
        for i, text in enumerate(texts):
            dy = 16 * i if line.anchor == "start" else -16 * (len(texts) - 1 - i)
            out.append(_text((x, y + dy), text, f'text-anchor="{line.anchor}" class="edge-label"'))
    for line in lines:
        r, (x, y) = line.relation, line.mark_at
        if r.step:
            out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13" class="badge"/>')
            out.append(_text((x, y + 4), str(r.step), 'text-anchor="middle" class="number"'))
        elif r.throughout:
            pill = f'<rect x="{x - 53:.0f}" y="{y - 12:.0f}" width="106" height="24" rx="12"'
            out.append(pill + ' class="badge"/>')
            out.append(_text((x, y + 4), "THROUGHOUT", 'text-anchor="middle" class="number pill"'))
    return out


def _description(model: Model, lines: list[Line]) -> str:
    steps = sorted((ln.relation for ln in lines if ln.relation.step), key=lambda r: r.step)
    names = model.elements
    told = [f"{r.step}. {names[r.source].name} to {names[r.target].name}: {r.label}" for r in steps]
    return "; ".join(told) + "."


def svg(model: Model, view: View) -> str:
    plate = layout(model, view)
    lines = route(plate, shown(model, view))
    head = [
        f'<svg viewBox="0 0 {plate.width:.0f} {plate.height:.0f}" role="img" '
        'aria-labelledby="title desc">',
        f'<title id="title">{escape(model.system.name)}: {escape(view.title)}</title>',
        f'<desc id="desc">{escape(_description(model, lines))}</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        'markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0 0 L10 5 L0 10Z" fill="context-stroke"/></marker></defs>',
    ]
    body = _svg_lanes(plate) + _svg_nodes(plate, model.system.id) + _svg_lines(lines)
    return "\n".join([*head, *body, "</svg>"])
