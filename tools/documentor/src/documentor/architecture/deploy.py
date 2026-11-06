"""The deployment view of a project's architecture model, drawn as a static SVG.

Boxes sit where they run: each element names its tier (1 at the top) and the zone that hosts it.
Each relation is one line, tagged with what travels and why it goes that way. Lines between
adjacent tiers each take their own lane in the gap, the lanes ordered so their runs do not cross,
and a box's exits ordered by where each line goes; a line that skips a tier runs down the left
corridor. Labels sit where the fewest lines pass, and zone headers slide clear of the lines. No
layout engine and no browser: the layout is arithmetic on the tiers. Standard library only.
"""

from dataclasses import dataclass, field, replace
from html import escape
from itertools import pairwise

if __package__:
    from documentor.architecture.model import Element, Model, Relation, View
else:  # run as a script: the sibling module is on the path
    from documentor.architecture.model import Element, Model, Relation, View

WIDTH, ZONE_GAP, BOX_GAP, PAD, HEAD, MARGIN, LANE = 960, 14, 10, 10, 30, 20, 22
NAME_PX, DETAIL_PX, LABEL_PX = 7.6, 6.2, 6.5


@dataclass
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def cx(self) -> float:
        return self.x + self.w / 2

    @property
    def cy(self) -> float:
        return self.y + self.h / 2


@dataclass
class Layout:
    boxes: dict[str, Box] = field(default_factory=dict)
    zones: dict[str, Box] = field(default_factory=dict)
    tiers: dict[int, tuple[float, float]] = field(default_factory=dict)  # tier: (top, bottom)
    paths: list[tuple[str, bool]] = field(default_factory=list)  # (d, dashed)
    # Each relation's routed points, by "source>target", for a renderer that draws its own lines.
    routes: dict[str, list[tuple[float, float]]] = field(default_factory=dict)
    labels: list[tuple[float, float, str]] = field(default_factory=list)
    verticals: list[tuple[float, float, float]] = field(default_factory=list)  # (x, y0, y1)
    height: float = 0
    corridors: int = 0


def _wrap(text: str, width: float, px: float) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if line and len(trial) * px > width:
            lines.append(line)
            line = word
        else:
            line = trial
    return [*lines, line] if line else lines


def _lines(element: Element, width: float) -> tuple[list[str], list[str]]:
    """An element's name and detail, wrapped to the box."""
    return _wrap(element.name, width - 12, NAME_PX), _wrap(element.detail, width - 16, DETAIL_PX)


def _zones_of(model: Model, view: View) -> dict[int, dict[str, list[Element]]]:
    tiers: dict[int, dict[str, list[Element]]] = {}
    for element_id in view.elements:
        element = model.elements[element_id]
        tiers.setdefault(element.tier, {}).setdefault(element.zone, []).append(element)
    return dict(sorted(tiers.items()))


def _edges(model: Model, view: View) -> list[Relation]:
    shown = set(view.elements)
    return [r for r in model.relations if not r.data and r.source in shown and r.target in shown]


def _label(r: Relation) -> str:
    return f"{r.label} · {r.why}" if r.why else r.label


def _end(box: str | None, side: str, span: str, corridor: float = 0.0) -> dict:
    """One end of a line in a gap: a box's side, or the left corridor, and which way it runs."""
    return {"box": box, "side": side, "span": span, "x": corridor}


def _plan(model: Model, view: View, tight: set[tuple[str, str]]) -> dict[int, list[dict]]:
    """Every line's place in the gaps it crosses, before anything is placed (gap n is below tier n).

    A line between adjacent tiers takes one lane; one that skips a tier takes a lane in the gap it
    leaves by and one in the gap it enters by, joined down the left corridor; one between two
    neighbors too close for a label loops through the gap below them.
    """
    gaps: dict[int, list[dict]] = {}
    corridor, last = 0, max(model.elements[e].tier for e in view.elements)
    for r in _edges(model, view):
        ta, tb = model.elements[r.source].tier, model.elements[r.target].tier
        line = {"id": f"{r.source}>{r.target}", "dashed": r.status != "built", "text": _label(r)}
        if ta == tb and (r.source, r.target) in tight:
            # A loop runs through the gap below its tier, or above it on the bottom tier.
            side, span, gap = ("lower", "down", ta - 1) if ta == last else ("upper", "up", ta)
            ends = [_end(r.source, side, span), _end(r.target, side, span)]
            gaps.setdefault(gap, []).append(line | {"ends": ends})
        elif abs(ta - tb) == 1:
            down = tb > ta
            a = _end(r.source, "upper" if down else "lower", "up" if down else "down")
            b = _end(r.target, "lower" if down else "upper", "down" if down else "up")
            gaps.setdefault(min(ta, tb), []).append(line | {"ends": [a, b]})
        elif abs(ta - tb) > 1:
            xc, corridor = -24.0 - 12 * corridor, corridor + 1
            down = tb > ta
            leave, enter = (ta, tb - 1) if down else (ta - 1, tb)
            src = _end(r.source, "upper" if down else "lower", "up" if down else "down")
            dst = _end(r.target, "lower" if down else "upper", "down" if down else "up")
            out = _end(None, src["side"], "down" if down else "up", xc)
            into = _end(None, dst["side"], "up" if down else "down", xc)
            gaps.setdefault(leave, []).append(line | {"ends": [src, out], "stub": "leave"})
            gaps.setdefault(enter, []).append(line | {"ends": [into, dst], "stub": "enter"})
    return gaps


def _tight(model: Model, view: View, layout: Layout) -> set[tuple[str, str]]:
    """Neighbors on one tier with no room between them for their line's label."""
    pairs: set[tuple[str, str]] = set()
    for r in _edges(model, view):
        a, b = layout.boxes[r.source], layout.boxes[r.target]
        room = b.x - (a.x + a.w) if b.x > a.x else a.x - (b.x + b.w)
        same = model.elements[r.source].tier == model.elements[r.target].tier
        left, right = min(a.cx, b.cx), max(a.cx, b.cx)
        between = any(
            left < box.cx < right and abs(box.cy - a.cy) < 1
            for box_id, box in layout.boxes.items()
            if box_id not in (r.source, r.target)
        )
        if same and (between or room < len(_label(r)) * LABEL_PX + 24):
            pairs.add((r.source, r.target))
    return pairs


def _place_tier(layout: Layout, zones: dict[str, list[Element]], top: float, model: Model) -> float:
    weights = {zone: max(1, len(members)) for zone, members in zones.items()}
    inner = WIDTH - ZONE_GAP * (len(zones) - 1)
    x, bottom = 0.0, top
    for zone, members in zones.items():
        zw = inner * weights[zone] / sum(weights.values())
        bw = (zw - 2 * PAD - BOX_GAP * (len(members) - 1)) / len(members)
        lines = [_lines(m, bw) for m in members]
        bh = 16 + max(18 * len(name) + 15 * len(detail) for name, detail in lines)
        caption = 20 if model.zones.get(zone) else 0
        layout.zones[zone] = Box(x, top, zw, HEAD + bh + PAD + caption)
        for index, member in enumerate(members):
            layout.boxes[member.id] = Box(x + PAD + index * (bw + BOX_GAP), top + HEAD, bw, bh)
        bottom = max(bottom, top + HEAD + bh + PAD + caption)
        x += zw + ZONE_GAP
    return bottom


def _place(model: Model, view: View, lanes: dict[int, int]) -> Layout:
    layout, top = Layout(), 0.0
    for tier, zones in _zones_of(model, view).items():
        bottom = _place_tier(layout, zones, top, model)
        layout.tiers[tier] = (top, bottom)
        top = bottom + max(70, 2 * MARGIN + LANE * (lanes.get(tier, 0) + 1))
    layout.height = top
    return layout


def _slots(lines: list[dict], layout: Layout) -> None:
    """Spread the ends on each box side, ordered by where each line's other end is."""
    sides: dict[tuple[str, str], list[tuple[dict, dict]]] = {}
    for line in lines:
        for end, other in ((line["ends"][0], line["ends"][1]), (line["ends"][1], line["ends"][0])):
            if end["box"]:
                sides.setdefault((end["box"], end["side"]), []).append((end, other))
    for (box_id, _), group in sides.items():
        box = layout.boxes[box_id]
        group.sort(key=lambda pair: layout.boxes[pair[1]["box"]].cx if pair[1]["box"] else -1e9)
        for index, (end, _) in enumerate(group):
            end["x"] = box.x + box.w * (index + 1) / (len(group) + 1)


def _order(lines: list[dict]) -> list[dict]:
    """Lanes top to bottom so that, as far as swaps allow, no run crosses another line's end."""

    def crosses(run: dict, end: dict) -> bool:
        return run["lo"] < end["x"] < run["hi"]

    def cost(order: list[dict]) -> int:
        total = 0
        for i, upper in enumerate(order):
            for lower in order[i + 1 :]:
                total += sum(crosses(upper, e) for e in lower["ends"] if e["span"] == "up")
                total += sum(crosses(lower, e) for e in upper["ends"] if e["span"] == "down")
        return total

    order = sorted(lines, key=lambda line: line["hi"] - line["lo"])
    best, improved = cost(order), True
    while improved:
        improved = False
        for i in range(len(order) - 1):
            trial = [*order[:i], order[i + 1], order[i], *order[i + 2 :]]
            if (score := cost(trial)) < best:
                best, order, improved = score, trial, True
    return order


def _points(end: dict, y: float, layout: Layout) -> list[tuple[float, float]]:
    """The end's path from its box (or the corridor) to the lane."""
    if not end["box"]:
        return [(end["x"], y)]
    box = layout.boxes[end["box"]]
    edge = box.y + box.h if end["side"] == "upper" else box.y
    return [(end["x"], edge), (end["x"], y)]


def _route_gap(layout: Layout, lines: list[dict], gap: int, stubs: dict) -> None:
    _slots(lines, layout)
    for line in lines:
        xs = [end["x"] for end in line["ends"]]
        line["lo"], line["hi"] = min(xs), max(xs)
    top, bottom = layout.tiers[gap][1] + MARGIN, layout.tiers[gap + 1][0] - MARGIN
    order = _order(lines)
    for index, line in enumerate(order):
        y = top + (bottom - top) * (index + 1) / (len(order) + 1)
        line["y"] = y
        points = _points(line["ends"][0], y, layout) + _points(line["ends"][1], y, layout)[::-1]
        for (x0, y0), (x1, y1) in pairwise(points):
            if x0 == x1:
                layout.verticals.append((x0, min(y0, y1), max(y0, y1)))
        if "stub" in line:
            stubs.setdefault(line["id"], {})[line["stub"]] = (points, line["dashed"])
        else:
            layout.paths.append((_path(points), line["dashed"]))
            layout.routes[line["id"]] = points
    for line in order:
        if line["text"] and line.get("stub", "enter") == "enter":
            layout.labels.append((_label_x(layout, line), line["y"], line["text"]))


def _path(points: list[tuple[float, float]]) -> str:
    head, *rest = points
    return f"M{head[0]:.1f},{head[1]:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in rest)


def _label_x(layout: Layout, line: dict) -> float:
    half = (len(line["text"]) * LABEL_PX + 14) / 2
    lo = max(line["lo"], half + 4)
    hi = max(lo, line["hi"] - half)
    middle = (line["lo"] + line["hi"]) / 2
    candidates = [lo + step * 12 for step in range(int((hi - lo) / 12) + 1)] or [lo]

    def crossings(x: float) -> tuple[int, float]:
        y = line["y"]
        hits = sum(1 for vx, y0, y1 in layout.verticals if y0 < y < y1 and abs(vx - x) < half)
        return hits, abs(x - middle)

    return min(candidates, key=crossings)


def _route_side(layout: Layout, r: Relation) -> None:
    a, b = layout.boxes[r.source], layout.boxes[r.target]
    x1, x2 = (a.x + a.w, b.x) if b.x > a.x else (a.x, b.x + b.w)
    layout.paths.append((f"M{x1:.1f},{a.cy:.1f} L{x2:.1f},{a.cy:.1f}", r.status != "built"))
    layout.routes[f"{r.source}>{r.target}"] = [(x1, a.cy), (x2, a.cy)]
    layout.labels.append(((x1 + x2) / 2, a.cy - 12, _label(r)))


def _ranked(model: Model, view: View) -> Model:
    """The model with the view's tiers numbered 1, 2, ... in order, so a view may skip a tier."""
    ranks = {
        tier: rank
        for rank, tier in enumerate(
            sorted({model.elements[e].tier for e in view.elements}), start=1
        )
    }
    elements = dict(model.elements)
    for element_id in view.elements:
        element = elements[element_id]
        elements[element_id] = replace(element, tier=ranks[element.tier])
    return replace(model, elements=elements)


def route(model: Model, view: View) -> Layout:
    """Place the boxes, then route every line through the gaps and the left corridor."""
    model = _ranked(model, view)
    draft = _place(model, view, {})
    tight = _tight(model, view, draft)
    gaps = _plan(model, view, tight)
    layout = _place(model, view, {gap: len(lines) for gap, lines in gaps.items()})
    for r in _edges(model, view):
        same = model.elements[r.source].tier == model.elements[r.target].tier
        if same and (r.source, r.target) not in tight:
            _route_side(layout, r)
    stubs: dict[str, dict] = {}
    for gap, lines in sorted(gaps.items()):
        _route_gap(layout, lines, gap, stubs)
    for key, parts in stubs.items():
        (leave, dashed), (enter, _) = parts["leave"], parts["enter"]
        layout.paths.append((_path(leave + enter), dashed))
        layout.routes[key] = leave + enter
        layout.verticals.append(
            (leave[-1][0], min(leave[-1][1], enter[0][1]), max(leave[-1][1], enter[0][1]))
        )
    layout.corridors = sum(1 for parts in stubs.values() if parts)
    return layout


# --- drawing ------------------------------------------------------------------------------------


def _stroke(model: Model, element: Element) -> tuple[str, str, str]:
    """An element's outline (color, width, dash): the accent on its own code, dashed if unbuilt."""
    t = model.theme
    states = {"placeholder": t["limited"], "decided": t["purchasing"], "unknown": t["evaluation"]}
    if element.status in states:
        return states[element.status], "1.5", "5 4"
    if element.owner == model.system.id and element.kind in ("system", "container"):
        return t["accent"], "2", ""
    return t["border"], "1.5", ""


def _clear_x(layout: Layout, zone: Box, width: float, band: tuple, right: bool = False) -> float:
    """A label's left edge in its zone: the nearest spot to its home with no line crossing it."""
    lo, hi = zone.x + PAD, zone.x + zone.w - width - PAD
    spots = (
        [hi - step for step in range(0, int(hi - lo) + 1, 6)]
        if right
        else [lo + step for step in range(0, int(hi - lo) + 1, 6)]
    )
    for x in spots:
        if not any(
            band[0] < y1 and y0 < band[1] and x - 12 < vx < x + width + 12
            for vx, y0, y1 in layout.verticals
        ):
            return x
    return hi if right else lo


def _text(at: tuple[float, float], text: str, style: str) -> str:
    return f'<text x="{at[0]:.1f}" y="{at[1]:.1f}" {style}>{escape(text)}</text>'


def _draw_zones(model: Model, layout: Layout, out: list[str]) -> None:
    t = model.theme
    for name, zone in layout.zones.items():
        out.append(
            f'<rect x="{zone.x:.1f}" y="{zone.y:.1f}" width="{zone.w:.1f}" '
            f'height="{zone.h:.1f}" rx="5" fill="{t["ground"]}" stroke="{t["border"]}"/>'
        )
        label = name.upper()
        width = len(label) * 7.4
        x = _clear_x(layout, zone, width, (zone.y + 6, zone.y + 24))
        out.append(
            f'<rect x="{x - 4:.1f}" y="{zone.y + 7:.1f}" width="{width + 8:.1f}" '
            f'height="17" fill="{t["ground"]}"/>'
        )
        heading = f'font-size="11.5" fill="{t["muted"]}" font-weight="600" letter-spacing="0.06em"'
        out.append(_text((x, zone.y + 20), label, heading))
        caption = model.zones.get(name)
        if caption:
            width = len(caption) * 6.4
            x = _clear_x(layout, zone, width, (zone.y + zone.h - 20, zone.y + zone.h - 4), True)
            out.append(
                f'<rect x="{x - 4:.1f}" y="{zone.y + zone.h - 20:.1f}" '
                f'width="{width + 8:.1f}" height="16" fill="{t["ground"]}"/>'
            )
            out.append(
                _text((x, zone.y + zone.h - 8), caption, f'font-size="11.5" fill="{t["muted"]}"')
            )


def _draw_boxes(model: Model, layout: Layout, out: list[str]) -> None:
    t = model.theme
    for element_id, box in layout.boxes.items():
        element = model.elements[element_id]
        color, width, dash = _stroke(model, element)
        dashing = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(
            f'<rect x="{box.x:.1f}" y="{box.y:.1f}" width="{box.w:.1f}" '
            f'height="{box.h:.1f}" rx="4" fill="{t["surface"]}" stroke="{color}" '
            f'stroke-width="{width}"{dashing}/>'
        )
        name = f'font-size="13.5" fill="{t["strong"]}" text-anchor="middle" font-weight="600"'
        names, details = _lines(element, box.w)
        for index, line in enumerate(names):
            out.append(_text((box.cx, box.y + 20 + 18 * index), line, name))
        below = box.y + 20 + 18 * (len(names) - 1)
        detail = f'font-size="11.5" fill="{t["muted"]}" text-anchor="middle"'
        for index, line in enumerate(details):
            out.append(_text((box.cx, below + 17 + 15 * index), line, detail))


def _draw_lines(model: Model, layout: Layout, out: list[str]) -> None:
    t = model.theme
    for path, dashed in layout.paths:
        dashing = ' stroke-dasharray="5 4"' if dashed else ""
        out.append(
            f'<path d="{path}" fill="none" stroke="{t["muted"]}" stroke-width="1.3"'
            f'{dashing} marker-end="url(#arrow)"/>'
        )
    for x, y, text in layout.labels:
        width = len(text) * LABEL_PX + 12
        out.append(
            f'<rect x="{x - width / 2:.1f}" y="{y - 9:.1f}" width="{width:.1f}" '
            f'height="18" rx="3" fill="{t["sunken"]}" stroke="{t["border"]}"/>'
        )
        out.append(
            _text((x, y + 4), text, f'font-size="12" fill="{t["strong"]}" text-anchor="middle"')
        )


def render_deployment(model: Model, view: View) -> str:
    """The view as one standalone SVG, in the model's theme."""
    layout = route(model, view)
    left = 40 + 12 * layout.corridors
    t = model.theme
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-left} -10 {WIDTH + left + 10} '
        f'{layout.height + 10:.0f}" font-family="{escape(t["font"])}">',
        f'<rect x="{-left}" y="-10" width="{WIDTH + left + 10}" height="{layout.height + 10:.0f}" '
        f'fill="{t["sunken"]}"/>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" '
        f'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="{t["accent"]}"/></marker></defs>',
    ]
    _draw_zones(model, layout, out)
    _draw_lines(model, layout, out)
    _draw_boxes(model, layout, out)
    return "\n".join([*out, "</svg>"]) + "\n"
