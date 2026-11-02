"""The deployment view of a project's architecture model, drawn as a static SVG.

Boxes sit where they run: each element names its tier (1 at the top) and the zone that hosts it;
a zone whose boxes only send lines sits just above the first tier they reach. A tier's zones, and
a zone's boxes, are ordered by where their lines go, and each zone takes the width its boxes need
before the rest is shared. Each relation is one line, tagged with what travels and why it goes that
way. Neighbors a line joins, in one zone or at the facing ends of two zones in a tier, join side to
side with room for the tag. Lines between adjacent tiers each take their own lane in the gap, the
lanes ordered so their runs cross as few legs as possible, and a box's exits ordered by where each
line goes. A line that skips a tier runs down the left corridor, shorter lines inside longer ones;
one into the bottom tier runs under the boxes and rises into its box. A tag slides along its line,
or wraps onto two or three lines, to where no other line or tag passes; zone headers slide clear of
the lines. No layout engine and no browser: the layout is arithmetic on the tiers. Standard library
only.
"""

from dataclasses import dataclass, field, replace
from html import escape
from itertools import pairwise

from documentor.architecture.model import Element, Model, Relation, View

WIDTH, ZONE_GAP, BOX_GAP, PAD, HEAD, MARGIN, LANE, CORRIDOR = 960, 14, 10, 10, 30, 20, 26, 12
NAME_PX, DETAIL_PX, LABEL_PX, HEADER_PX, CAPTION_PX = 7.6, 6.2, 6.5, 7.4, 6.4
SIDE_TEXT, ARROW_ROOM, TAG_LINE = 150, 16, 16


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
    labels: list[tuple[float, float, str]] = field(default_factory=list)  # a tag's centre and text
    label_rows: list[list[str]] = field(default_factory=list)  # each tag's text as drawn, by row
    verticals: list[tuple[float, float, float]] = field(default_factory=list)  # (x, y0, y1)
    height: float = 0
    width: float = WIDTH
    corridors: int = 0


@dataclass
class Tag:
    rows: list[str]
    w: float
    h: float


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


def _tag(rows: list[str]) -> Tag:
    return Tag(rows, max((len(r) for r in rows), default=0) * LABEL_PX + 12, TAG_LINE * len(rows) + 2)


def _rows(text: str, n: int) -> Tag:
    """The text on at most n rows, as even as the words allow."""
    full = len(text) * LABEL_PX
    width = full / n
    while width < full:
        rows = _wrap(text, width, LABEL_PX)
        if len(rows) <= n:
            return _tag(rows)
        width += 8
    return _tag([text])


def _edges(model: Model, view: View) -> list[Relation]:
    shown = set(view.elements)
    return [r for r in model.relations if not r.data and r.source in shown and r.target in shown]


def _label(r: Relation) -> str:
    return f"{r.label} · {r.why}" if r.why else r.label


def _key(r: Relation) -> str:
    return f"{r.source}>{r.target}"


def _end(box: str | None, side: str, span: str, corridor: float = 0.0) -> dict:
    """One end of a line in a gap: the box edge it leaves ("top" or "bottom"), or the corridor,
    and which way its leg runs from the lane ("up" to a box above, "down" to one below)."""
    return {"box": box, "side": side, "span": span, "x": corridor}


def _ranked(model: Model, view: View) -> Model:
    """The model with the view's tiers numbered 1, 2, ... in order, so a view may skip a tier.

    A zone whose boxes only send lines sits in the tier just above the first tier they reach: a
    deploy principal beside what it deploys, not two tiers above it.
    """
    tier = {e: model.elements[e].tier for e in view.elements}
    zone = {e: (tier[e], model.elements[e].zone) for e in view.elements}
    edges = _edges(model, view)
    for place in set(zone.values()):
        ids = {e for e, z in zone.items() if z == place}
        incoming = any(r.target in ids and r.source not in ids for r in edges)
        outgoing = [r.target for r in edges if r.source in ids and r.target not in ids]
        if incoming or not outgoing:
            continue
        nearest = min(tier[t] for t in outgoing)
        if nearest - 1 > place[0]:
            for e in ids:
                tier[e] = nearest - 1
    ranks = {t: rank for rank, t in enumerate(sorted(set(tier.values())), start=1)}
    elements = dict(model.elements)
    for element_id in view.elements:
        elements[element_id] = replace(elements[element_id], tier=ranks[tier[element_id]])
    return replace(model, elements=elements)


class _Plan:
    """The view's tiers, zones and boxes in drawing order, and the room each needs."""

    def __init__(self, model: Model, view: View) -> None:
        self.model, self.edges = model, _edges(model, view)
        self.tier = {e: model.elements[e].tier for e in view.elements}
        tiers: dict[int, dict[str, list[Element]]] = {}
        for element_id in view.elements:
            element = model.elements[element_id]
            tiers.setdefault(element.tier, {}).setdefault(element.zone, []).append(element)
        # Each tier: a list of [zone, members], both reordered below.
        self.tiers = [[[z, m] for z, m in zones.items()] for _, zones in sorted(tiers.items())]
        self.width = WIDTH

    def between(self, a: str, b: str) -> list[Relation]:
        return [r for r in self.edges if {r.source, r.target} == {a, b}]

    def side_tag(self, r: Relation) -> Tag:
        return _tag(_wrap(_label(r), SIDE_TEXT, LABEL_PX))

    def side_gap(self, r: Relation) -> float:
        return (self.side_tag(r).w if _label(r) else 0) + 2 * ARROW_ROOM + 8

    def gaps(self, members: list[Element]) -> list[float]:
        """Neighbors a line joins stand apart by that line's tag; others by the usual gap."""
        out = []
        for a, b in pairwise(members):
            joined = self.between(a.id, b.id)
            out.append(max(map(self.side_gap, joined)) if joined else BOX_GAP)
        return out

    def facing(self, left: list, right: list) -> Relation | None:
        joined = self.between(left[1][-1].id, right[1][0].id)
        return joined[0] if joined else None

    def zone_gaps(self, zones: list) -> list[float]:
        out = []
        for left, right in pairwise(zones):
            r = self.facing(left, right)
            out.append(max(ZONE_GAP, self.side_gap(r) - 2 * PAD) if r else ZONE_GAP)
        return out

    def need(self, zone: str, members: list[Element]) -> float:
        def least(e: Element) -> float:
            words = [len(w) * NAME_PX + 28 for w in e.name.split()]
            return max(120, min(240, len(e.name) * NAME_PX + 28), *words)

        caption = self.model.zones.get(zone) or ""
        boxes = len(members) * max(map(least, members)) + 2 * PAD + sum(self.gaps(members))
        return max(len(zone) * HEADER_PX + 2 * PAD, len(caption) * CAPTION_PX + 2 * PAD, boxes)

    def measure(self) -> None:
        self.width = max(
            WIDTH,
            *(sum(self.need(z, m) for z, m in zones) + sum(self.zone_gaps(zones)) for zones in self.tiers),
        )

    def place(self, lanes: dict[int, int]) -> Layout:
        layout, top = Layout(width=self.width), 0.0
        for tier, zones in enumerate(self.tiers, start=1):
            zone_gaps = self.zone_gaps(zones)
            inner = self.width - sum(zone_gaps)
            total = sum(len(m) for _, m in zones)
            needs = [self.need(z, m) for z, m in zones]
            spare = inner - sum(needs)
            x, bottom = 0.0, top
            for index, (zone, members) in enumerate(zones):
                zw = needs[index] + spare * len(members) / total
                gaps = self.gaps(members)
                bw = (zw - 2 * PAD - sum(gaps)) / len(members)
                bh = 16 + max(18 * len(n) + 15 * len(d) for n, d in (_lines(m, bw) for m in members))
                caption = 20 if self.model.zones.get(zone) else 0
                layout.zones[zone] = Box(x, top, zw, HEAD + bh + PAD + caption)
                bx = x + PAD
                for i, member in enumerate(members):
                    layout.boxes[member.id] = Box(bx, top + HEAD, bw, bh)
                    bx += bw + (gaps[i] if i < len(gaps) else 0)
                bottom = max(bottom, top + HEAD + bh + PAD + caption)
                x += zw + (zone_gaps[index] if index < len(zone_gaps) else 0)
            for zone, _ in zones:
                layout.zones[zone].h = bottom - top
            layout.tiers[tier] = (top, bottom)
            top = bottom + max(70, 2 * MARGIN + LANE * (lanes.get(tier, 0) + 1))
        layout.height = top
        return layout

    def order(self) -> None:
        """Zones in a tier, and boxes in a zone, by where their lines go: the mean position of each
        line's other end, a line that skips a tier counting as the left corridor. Twice, as each
        order moves the other. Then a line joining two zones of one tier brings the zones together
        and its boxes to their facing ends, so it can join them side to side."""
        for _ in range(2):
            boxes = self.place({}).boxes

            def pull(e: Element, boxes: dict[str, Box] = boxes) -> float:
                ends = [
                    -self.width if abs(self.tier[o] - self.tier[e.id]) > 1 else boxes[o].cx
                    for r in self.edges
                    if e.id in (r.source, r.target)
                    for o in [r.target if r.source == e.id else r.source]
                ]
                return sum(ends) / len(ends) if ends else boxes[e.id].cx

            for zones in self.tiers:
                for pair in zones:
                    pair[1].sort(key=pull)
                zones.sort(key=lambda pair: sum(map(pull, pair[1])) / len(pair[1]))
        at_end: set[str] = set()
        zone_of = {m.id: (t, z) for t, zones in enumerate(self.tiers) for z, ms in zones for m in ms}
        for r in self.edges:
            (ta, za), (tb, zb) = zone_of[r.source], zone_of[r.target]
            if ta != tb or za == zb or at_end & {r.source, r.target}:
                continue
            zones = self.tiers[ta]
            a = next(p for p in zones if p[0] == za)
            b = next(p for p in zones if p[0] == zb)
            # The right-hand zone of the two stays where the order put it; the other moves beside it.
            left, right = (a, b) if zones.index(a) < zones.index(b) else (b, a)
            lid, rid = (r.source, r.target) if left is a else (r.target, r.source)
            if any(m.id in at_end for m in [*left[1][:-1], *right[1][1:]]):
                continue
            zones.remove(left)
            zones.insert(zones.index(right), left)
            left[1].append(left[1].pop(next(i for i, m in enumerate(left[1]) if m.id == lid)))
            right[1].insert(0, right[1].pop(next(i for i, m in enumerate(right[1]) if m.id == rid)))
            at_end |= {lid, rid}
        self.measure()

    def tight(self, layout: Layout) -> set[str]:
        """Lines between boxes on one tier with no room for their tag: they loop through a gap.
        Neighbors in a zone, and the facing boxes of adjacent zones, always have room made."""
        out = set()
        for r in self.edges:
            if self.tier[r.source] != self.tier[r.target]:
                continue
            zones = self.tiers[self.tier[r.source] - 1]
            if any(r in self.between(a.id, b.id) for _, ms in zones for a, b in pairwise(ms)):
                continue
            if any(self.facing(a, b) == r for a, b in pairwise(zones)):
                continue
            a, b = layout.boxes[r.source], layout.boxes[r.target]
            room = b.x - (a.x + a.w) if b.x > a.x else a.x - (b.x + b.w)
            left, right = min(a.cx, b.cx), max(a.cx, b.cx)
            blocked = any(
                left < box.cx < right and abs(box.y - a.y) < 1
                for box_id, box in layout.boxes.items()
                if box_id not in (r.source, r.target)
            )
            if blocked or room < len(_label(r)) * LABEL_PX + 36:
                out.add(_key(r))
        return out


def _gaps(plan: _Plan, tight: set[str]) -> tuple[dict[int, list[dict]], list[dict], int]:
    """Every line's place in the gaps it crosses (gap n is below tier n), the lines that run under
    the bottom tier, and the number of corridor tracks."""
    last = len(plan.tiers)
    tier = plan.tier
    skips = [r for r in plan.edges if abs(tier[r.source] - tier[r.target]) > 1]

    # Corridor tracks nest: a line spanning fewer tiers runs inside one spanning more (one that goes
    # on under the bottom tier counts as longer still), so the outer line wraps the inner.
    def reach(r: Relation) -> float:
        under = tier[r.target] == last and tier[r.target] > tier[r.source]
        return abs(tier[r.source] - tier[r.target]) + (0.5 if under else 0)

    ranked = sorted(skips, key=lambda r: (reach(r), _key(r)))
    track = {_key(r): -2 * CORRIDOR - CORRIDOR * i for i, r in enumerate(ranked)}
    gaps: dict[int, list[dict]] = {}
    under: list[dict] = []
    for r in plan.edges:
        ta, tb = tier[r.source], tier[r.target]
        line = {"id": _key(r), "dashed": r.status != "built", "text": _label(r)}
        if ta == tb and _key(r) in tight:
            # A loop runs through the gap below its tier, or above it on the bottom tier.
            side, span, gap = ("top", "down", ta - 1) if ta == last else ("bottom", "up", ta)
            ends = [_end(r.source, side, span), _end(r.target, side, span)]
            gaps.setdefault(gap, []).append(line | {"ends": ends})
        elif abs(ta - tb) == 1:
            down = tb > ta
            a = _end(r.source, "bottom" if down else "top", "up" if down else "down")
            b = _end(r.target, "top" if down else "bottom", "down" if down else "up")
            gaps.setdefault(min(ta, tb), []).append(line | {"ends": [a, b]})
        elif abs(ta - tb) > 1:
            xc, down = track[_key(r)], tb > ta
            src = _end(r.source, "bottom" if down else "top", "up" if down else "down")
            dst = _end(r.target, "top" if down else "bottom", "down" if down else "up")
            out = _end(None, src["side"], "down" if down else "up", xc)
            gaps.setdefault(ta if down else ta - 1, []).append(line | {"ends": [src, out], "stub": "leave"})
            if down and tb == last:
                # Into the bottom tier, it keeps to the corridor and rises into its box from below.
                under.append(line | {"xc": xc, "to": r.target})
            else:
                into = _end(None, dst["side"], "up" if down else "down", xc)
                gaps.setdefault(tb - 1 if down else tb, []).append(line | {"ends": [into, dst], "stub": "enter"})
    return gaps, under, len(skips)


def _spread(lines: list[dict], layout: Layout) -> None:
    """Spread the ends on each box side, ordered by where each line's other end is: first the
    other box's centre, then the other end's own spot."""
    sides: dict[tuple[str, str], list[tuple[dict, dict]]] = {}
    for line in lines:
        for end, other in ((line["ends"][0], line["ends"][1]), (line["ends"][1], line["ends"][0])):
            if end["box"]:
                sides.setdefault((end["box"], end["side"]), []).append((end, other))
    for where in (lambda o: layout.boxes[o["box"]].cx, lambda o: o["x"]):
        for (box_id, _), group in sides.items():
            box = layout.boxes[box_id]
            group.sort(key=lambda pair: (where(pair[1]) if pair[1]["box"] else pair[1]["x"] - 1e6, pair[1]["box"] or ""))
            for index, (end, _) in enumerate(group):
                end["x"] = box.x + box.w * (index + 1) / (len(group) + 1)


def _order(lines: list[dict]) -> list[dict]:
    """Lanes top to bottom in one gap. First, as few crossings as possible: a lane's run crossing a
    leg of a line in a lower lane that rises to a box above, or of a line in a higher lane that
    drops to a box below. Then, among the best: lines leaving one box the same way nest (heading
    right, the rightmost exit on top; heading left, the leftmost), and a loop between neighbors sits
    in the lane nearest its boxes. Every order is tried for a small gap, pruned by the best so far;
    a large gap takes adjacent swaps from the shortest runs up."""

    def crossings(upper: dict, lower: dict) -> int:
        rising = sum(upper["lo"] < e["x"] < upper["hi"] for e in lower["ends"] if e["span"] == "up")
        dropping = sum(lower["lo"] < e["x"] < lower["hi"] for e in upper["ends"] if e["span"] == "down")
        return rising + dropping

    def loop(line: dict) -> bool:
        a, b = line["ends"]
        return bool(a["box"] and b["box"]) and a["side"] == b["side"] and a["span"] == b["span"]

    def heading(line: dict) -> int:
        delta = line["ends"][1]["x"] - line["ends"][0]["x"]
        return (delta > 0) - (delta < 0)

    def preference(upper: dict, lower: dict) -> int:
        cost = 0
        a, b = upper["ends"][0], lower["ends"][0]
        shared = a["box"] and a["box"] == b["box"] and a["side"] == b["side"]
        if shared and not loop(upper) and not loop(lower) and heading(upper) == heading(lower) != 0:
            cost += (a["x"] < b["x"]) if heading(upper) > 0 else (a["x"] > b["x"])
        if loop(upper) and not loop(lower) and upper["ends"][0]["span"] == "down":
            cost += 1
        if loop(lower) and not loop(upper) and lower["ends"][0]["span"] == "up":
            cost += 1
        return cost

    n = len(lines)
    pair = [[0 if i == j else 1000 * crossings(u, l) + preference(u, l) for j, l in enumerate(lines)] for i, u in enumerate(lines)]
    first = sorted(range(n), key=lambda i: (lines[i]["hi"] - lines[i]["lo"], lines[i]["id"]))

    def total(order: list[int]) -> int:
        return sum(pair[u][l] for i, u in enumerate(order) for l in order[i + 1 :])

    best, best_order = total(first), first
    if n <= 8:
        used, current = [False] * n, []

        def search(cost: int) -> None:
            nonlocal best, best_order
            if cost >= best:
                return
            if len(current) == n:
                best, best_order = cost, list(current)
                return
            for i in first:
                if used[i]:
                    continue
                # Placing i next puts it above every line not yet placed.
                added = sum(pair[i][j] for j in first if not used[j] and j != i)
                used[i] = True
                current.append(i)
                search(cost + added)
                current.pop()
                used[i] = False

        search(0)
        return [lines[i] for i in best_order]
    order, improved = first, True
    while improved:
        improved = False
        for i in range(n - 1):
            trial = [*order[:i], order[i + 1], order[i], *order[i + 2 :]]
            if (score := total(trial)) < best:
                best, order, improved = score, trial, True
    return [lines[i] for i in order]


def _points(end: dict, y: float, layout: Layout) -> list[tuple[float, float]]:
    """The end's path from its box (or the corridor) to the lane."""
    if not end["box"]:
        return [(end["x"], y)]
    box = layout.boxes[end["box"]]
    edge = box.y + box.h if end["side"] == "bottom" else box.y
    return [(end["x"], edge), (end["x"], y)]


def _route_gap(layout: Layout, lines: list[dict], gap: int, stubs: dict, lanes: dict) -> None:
    _spread(lines, layout)
    for line in lines:
        xs = [end["x"] for end in line["ends"]]
        line["lo"], line["hi"] = min(xs), max(xs)
    top, bottom = layout.tiers[gap][1] + MARGIN, layout.tiers[gap + 1][0] - MARGIN
    order = _order(lines)
    for index, line in enumerate(order):
        y = top + (bottom - top) * (index + 1) / (len(order) + 1)
        points = _points(line["ends"][0], y, layout) + _points(line["ends"][1], y, layout)[::-1]
        for (x0, y0), (x1, y1) in pairwise(points):
            if x0 == x1:
                layout.verticals.append((x0, min(y0, y1), max(y0, y1)))
        if "stub" in line:
            stubs.setdefault(line["id"], {})[line["stub"]] = points
        else:
            layout.routes[line["id"]] = points
        if line["text"] and line.get("stub") != "leave":
            lanes[line["id"]] = (line["text"], y, line["lo"], line["hi"])


def _route_under(layout: Layout, under: list[dict], stubs: dict, lanes: dict) -> None:
    """The bottom channel: a lane per line below the bottom tier, ends spread along each box's bottom."""
    channel = layout.tiers[max(layout.tiers)][1] + MARGIN
    by_box: dict[str, list[dict]] = {}
    for line in under:
        by_box.setdefault(line["to"], []).append(line)
    for box_id, group in by_box.items():
        box = layout.boxes[box_id]
        for index, line in enumerate(sorted(group, key=lambda line: line["xc"])):
            line["x"] = box.x + box.w * (index + 1) / (len(group) + 1)
    for index, line in enumerate(sorted(under, key=lambda line: -line["xc"])):
        box, y = layout.boxes[line["to"]], channel + LANE * (index + 0.5)
        leave = stubs.pop(line["id"])["leave"]
        layout.routes[line["id"]] = [*leave, (line["xc"], y), (line["x"], y), (line["x"], box.y + box.h)]
        layout.verticals += [(line["xc"], leave[-1][1], y), (line["x"], box.y + box.h, y)]
        if line["text"]:
            lanes[line["id"]] = (line["text"], y, line["xc"], line["x"])


def _place_tags(layout: Layout, sides: dict, lanes: dict) -> dict[str, tuple[float, float, Tag]]:
    """A side tag sits in the middle of its line. A lane's tag slides along its run to where no other
    line passes it; failing that it wraps onto two rows, then three, and slides again; failing all
    it takes the spot fewest lines pass. Tags keep clear of each other and of the lanes beside."""
    horizontals = [
        (key, a[1], min(a[0], b[0]), max(a[0], b[0]))
        for key, points in layout.routes.items()
        for a, b in pairwise(points)
        if a[1] == b[1]
    ]
    placed: dict[str, tuple[float, float, Tag]] = dict(sides)
    boxes = [(x - t.w / 2, y - t.h / 2, t.w, t.h) for x, y, t in sides.values()]
    reach = CORRIDOR * (layout.corridors + 2)
    for key, (text, y, lo_run, hi_run) in lanes.items():
        middle, best = (lo_run + hi_run) / 2, None

        def own(vx: float, lo_run: float = lo_run, hi_run: float = hi_run) -> bool:
            return lo_run - 0.5 <= vx <= hi_run + 0.5

        for tag in (_tag([text]), _rows(text, 2), _rows(text, 3)):
            half = tag.w / 2
            # A tag stays out of the corridor unless its own line runs along it.
            lo = max(lo_run, half + 4 - reach if lo_run < 0 else half + 4)
            hi = max(lo, hi_run - half)
            x = lo
            while x <= hi + 0.01:
                bx, by = x - half, y - tag.h / 2
                lines = sum(
                    1
                    for vx, y0, y1 in layout.verticals
                    if y0 < by + tag.h and by < y1 and bx - 2 < vx < bx + tag.w + 2
                    and not (own(vx) and (abs(y1 - y) < 0.5 or abs(y0 - y) < 0.5))
                ) + sum(
                    1
                    for other, hy, x0, x1 in horizontals
                    if other != key and abs(hy - y) > 0.5 and by - 2 < hy < by + tag.h + 2
                    and x0 < bx + tag.w and bx < x1
                )
                tags = sum(
                    1
                    for ox, oy, ow, oh in boxes
                    if ox < bx + tag.w + 4 and bx < ox + ow + 4 and oy < by + tag.h + 2 and by < oy + oh + 2
                )
                # Fewest lines and tags, then one row before two, then nearest the middle of the run.
                score = (lines + 10 * tags, len(tag.rows), abs(x - middle))
                if best is None or score < best[0]:
                    best = (score, x, tag)
                x += 6
        _, x, tag = best
        boxes.append((x - tag.w / 2, y - tag.h / 2, tag.w, tag.h))
        placed[key] = (x, y, tag)
    return placed


def route(model: Model, view: View) -> Layout:
    """Place the boxes, then route every line: side to side, through the gaps, down the corridor."""
    plan = _Plan(_ranked(model, view), view)
    plan.measure()
    plan.order()
    tight = plan.tight(plan.place({}))
    gaps, under, corridors = _gaps(plan, tight)
    counts = {gap: len(lines) for gap, lines in gaps.items()} | {len(plan.tiers): len(under)}
    layout = plan.place(counts)
    layout.corridors = corridors
    sides: dict[str, tuple[float, float, Tag]] = {}
    straight = [
        r for r in plan.edges if plan.tier[r.source] == plan.tier[r.target] and _key(r) not in tight
    ]
    for r in straight:
        a, b = layout.boxes[r.source], layout.boxes[r.target]
        # A call and its return between the same boxes: the rightward line above the middle, the
        # other below, so their tags stack instead of overlapping.
        paired = any(o is not r and {o.source, o.target} == {r.source, r.target} for o in straight)
        tag = plan.side_tag(r)
        y = a.cy + ((-1 if b.x > a.x else 1) * (tag.h / 2 + 3) if paired else 0)
        x1, x2 = (a.x + a.w, b.x) if b.x > a.x else (a.x, b.x + b.w)
        layout.routes[_key(r)] = [(x1, y), (x2, y)]
        if _label(r):
            sides[_key(r)] = ((x1 + x2) / 2, y, tag)
    stubs: dict[str, dict] = {}
    lanes: dict[str, tuple[str, float, float, float]] = {}
    for gap, lines in sorted(gaps.items()):
        _route_gap(layout, lines, gap, stubs, lanes)
    _route_under(layout, under, stubs, lanes)
    for key, parts in stubs.items():
        leave, enter = parts["leave"], parts["enter"]
        layout.routes[key] = leave + enter
        layout.verticals.append(
            (leave[-1][0], min(leave[-1][1], enter[0][1]), max(leave[-1][1], enter[0][1]))
        )
    tags = _place_tags(layout, sides, lanes)
    for r in plan.edges:
        key = _key(r)
        layout.paths.append((_path(layout.routes[key]), r.status != "built"))
        if key in tags:
            x, y, tag = tags[key]
            layout.labels.append((x, y, _label(r)))
            layout.label_rows.append(tag.rows)
    return layout


def _path(points: list[tuple[float, float]]) -> str:
    head, *rest = points
    return f"M{head[0]:.1f},{head[1]:.1f} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in rest)


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
    for (x, y, _), rows in zip(layout.labels, layout.label_rows, strict=True):
        tag = _tag(rows)
        top = y - tag.h / 2
        out.append(
            f'<rect x="{x - tag.w / 2:.1f}" y="{top:.1f}" width="{tag.w:.1f}" '
            f'height="{tag.h:.1f}" rx="3" fill="{t["sunken"]}" stroke="{t["border"]}"/>'
        )
        for index, row in enumerate(rows):
            style = f'font-size="12" fill="{t["strong"]}" text-anchor="middle"'
            out.append(_text((x, top + 13 + TAG_LINE * index), row, style))


def render_deployment(model: Model, view: View) -> str:
    """The view as one standalone SVG, in the model's theme."""
    layout = route(model, view)
    left = CORRIDOR * (layout.corridors + 2) + 24 if layout.corridors else 24
    width = layout.width + left + 10
    t = model.theme
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-left} -10 {width:.0f} '
        f'{layout.height + 10:.0f}" font-family="{escape(t["font"])}">',
        f'<rect x="{-left}" y="-10" width="{width:.0f}" height="{layout.height + 10:.0f}" '
        f'fill="{t["sunken"]}"/>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" '
        f'orient="auto"><path d="M0,0 L8,3 L0,6 z" fill="{t["accent"]}"/></marker></defs>',
    ]
    _draw_zones(model, layout, out)
    _draw_lines(model, layout, out)
    _draw_boxes(model, layout, out)
    return "\n".join([*out, "</svg>"]) + "\n"
