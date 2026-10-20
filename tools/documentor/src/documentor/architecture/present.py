#!/usr/bin/env python3
"""Draw a model view as a presentation: Eraser geometry, a theme, and a step-by-step walkthrough.

Usage:
    documentor present --root DIR --view ID [--journey ID] [--theme NAME] --out DIR

The diagram review (docs/helix/02-design/diagram-spikes, example 6) found that Eraser's measured
boxes and routed connectors, styled in the Blueprint register with a walkthrough that highlights
one relationship at a time, read best; but every position, color, and caption there was written by
hand. Here they come from the architecture model instead (docs/references/architecture-model.md (documentor)):

  positions    the deployment layout: each element's tier and zone (architecture_deploy.py)
  connections  the view's relations, with ports from the layout and waypoints for a line that
               skips a tier; a relation marked `data = true` is left to the DAG view
  colors       a theme from workflows/publish/themes/, or the model's own [theme]
  walkthrough  a journey's steps, each walking a relation the model holds, with its caption

This writes the renderer's input (`eraser.json`, `walkthrough.json`, `theme.json`); `present/
render.mjs` renders it with Eraser and wraps it. Nothing here is drawn by hand, so a model change
redraws the presentation. Requires PyYAML; the render step needs Node and Chromium.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from documentor.architecture import deploy
from documentor.lib import catalog
from documentor.architecture import model as am
import yaml

LABEL_PX = 8.4  # the presentation label font, 16px Inter, per character
SCALE = 1.45  # the layout's units are sized for documents; a presentation reads from farther away


def theme_for(model: am.Model, name: str | None) -> dict:
    """The named catalog theme, under the model's own overrides; the model's theme without a name."""
    chosen = name or model.theme.get("name")
    if not chosen:
        return dict(model.theme)
    path = catalog() / "themes" / f"{chosen}.yml"
    if path.is_file():
        return am.DEFAULT_THEME | (yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    sys.exit(f"documentor present: no theme named {chosen}")


def _plain(text: str) -> str:
    """Text Eraser shows as written: its markdown characters escaped, links reduced to their words."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text).replace("'", "\u2019")
    return re.sub(r"([*_`\[\]])", r"\\\1", text)


def _s(value: float) -> int:
    return round(value * SCALE)


def _side(a: tuple[float, float], b: tuple[float, float]) -> str:
    """Which side of a box a line leaves by, from its first segment."""
    if abs(a[0] - b[0]) < 0.5:
        return "bottom" if b[1] > a[1] else "top"
    return "right" if b[0] > a[0] else "left"


def _ports(layout: deploy.Layout, r: am.Relation) -> dict:
    """Ports and waypoints from the deployment router: one lane per line, crossings ordered away,
    a corridor for a line that skips a tier, a loop for neighbors too close for a label. Eraser
    then measures and draws the same route the SVG view draws."""
    points = layout.routes.get(f"{r.source}>{r.target}")
    if not points or len(points) < 2:
        return {}
    ports = {"fromPort": _side(points[0], points[1]), "toPort": _side(points[-1], points[-2])}
    inner = [{"x": _s(x) + OFFSET, "y": _s(y) + OFFSET} for x, y in points]
    spot = next(((x, y) for x, y, text in layout.labels if text == deploy._label(r)), None)
    width = round(len(r.label) * LABEL_PX + 16)  # one line: Eraser wraps a label it is not given room for
    placed = {"labelPlacement": {"x": _s(spot[0]) + OFFSET - width // 2, "y": _s(spot[1]) + OFFSET - 12,
                                 "width": width, "height": 24}} if spot else {}
    return ports | {"points": inner} | placed


OFFSET = 120  # room on the left for the corridor, in presentation units


def _border(model: am.Model, element: am.Element, theme: dict) -> tuple[str, str]:
    states = {"placeholder": theme["limited"], "decided": theme["purchasing"], "unknown": theme["evaluation"]}
    if element.status in states:
        return states[element.status], "dashed"
    if element.owner == model.system.id and element.kind in ("system", "container"):
        return theme["accent"], "solid"
    return theme["border"], "solid"


def eraser(model: am.Model, view: am.View, theme: dict) -> dict:
    layout = deploy.route(model, view)
    shapes, groups = [], []
    for name, zone in layout.zones.items():
        groups.append({
            "tag": "Group", "id": "zone-" + "".join(c if c.isalnum() else "-" for c in name.lower()),
            "x": _s(zone.x) + OFFSET, "y": _s(zone.y) + OFFSET, "width": _s(zone.w), "height": _s(zone.h),
            "title": {"text": name, "fontSize": 18, "typeface": "clean", "border": False,
                      "color": theme["muted"], "bgColor": theme["sunken"]},
            "color": "gray", "bgColor": theme["sunken"], "styleMode": "plain",
            "borderStyle": "solid", "borderColor": theme["recessed"], "borderWidth": 1.2})
    zone_of = {e: "zone-" + "".join(c if c.isalnum() else "-" for c in model.elements[e].zone.lower())
               for e in view.elements}
    for element_id, box in layout.boxes.items():
        element = model.elements[element_id]
        color, style = _border(model, element, theme)
        texts = [{"text": f"**{_plain(element.name)}**", "fontSize": 22, "typeface": "clean", "color": theme["strong"]}]
        if element.detail:
            texts.append({"text": _plain(element.detail), "fontSize": 16, "typeface": "clean", "color": theme["muted"]})
        shapes.append({
            "tag": "Shape", "id": element_id, "x": _s(box.x) + OFFSET, "y": _s(box.y) + OFFSET,
            "width": _s(box.w), "height": _s(box.h), "shape": "rectangle", "color": "gray",
            "styleMode": "plain", "cornerRadius": "round", "texts": texts, "containerId": zone_of[element_id],
            "bgColor": theme["surface"], "borderColor": color, "borderWidth": 2.2 if color == theme["accent"] else 1.6,
            **({"borderStyle": "dashed"} if style == "dashed" else {})})
    connections = []
    for r in deploy._edges(model, view):
        connections.append({
            "id": f"{r.source}--{r.target}", "from": r.source, "to": r.target, "label": _plain(r.label),
            "fontSize": 16, "typeface": "clean", "connectorStyle": "elbow", "endArrowhead": "arrow",
            "color": theme["muted"], "labelColor": theme["muted"], "lineWidth": 1.8,
            **({"lineStyle": "dashed"} if r.status != "built" else {}),
            **_ports(layout, r)})
    return {"entities": [*groups, *shapes], "connections": connections}


def walkthrough(model: am.Model, view: am.View, journey_id: str | None) -> dict:
    """The steps a presenter clicks through: a journey's, else the view's relations in model order."""
    shown = {f"{r.source}--{r.target}": r for r in deploy._edges(model, view)}
    steps = []
    if journey_id:
        journey = model.journeys[journey_id]
        for step in journey.steps:
            key = next((k for k in (f"{step.source}--{step.target}", f"{step.target}--{step.source}") if k in shown), "")
            relation = shown.get(key)
            caption = step.label[:1].upper() + step.label[1:]
            if relation and relation.why and relation.why.lower() not in caption.lower():
                caption += f": {relation.why}."
            elif not caption.endswith("."):
                caption += "."
            steps.append({"nodes": sorted({step.source, step.target} & set(view.elements)),
                          "edge": key, "caption": caption})
        title, lead = journey.title, journey.takeaway
    else:
        for key, r in shown.items():
            steps.append({"nodes": [r.source, r.target], "edge": key,
                          "caption": f"{r.label[:1].upper() + r.label[1:]}" + (f": {r.why}." if r.why else ".")})
        title, lead = view.title, view.takeaway
    lead = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", lead or "")
    return {"title": title or view.id, "lead": lead, "eyebrow": f"{model.system.name} / architecture",
            "steps": steps, "source": "architecture-model.toml"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="documentor present", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--model", type=Path)
    parser.add_argument("--view", required=True)
    parser.add_argument("--journey")
    parser.add_argument("--theme")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    model = am.load(args.model or am.default_model(root))
    if args.view not in model.views:
        parser.error(f"no view named {args.view}")
    view = model.views[args.view]
    if any(model.elements[e].tier < 1 for e in view.elements):
        parser.error(f"view {args.view}: every element needs a tier and zone (a deployment view)")
    theme = theme_for(model, args.theme)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "eraser.json").write_text(json.dumps(eraser(model, view, theme), indent=1), encoding="utf-8")
    (args.out / "walkthrough.json").write_text(json.dumps(walkthrough(model, view, args.journey), indent=1), encoding="utf-8")
    (args.out / "theme.json").write_text(json.dumps(theme, indent=1), encoding="utf-8")
    print(f"wrote {args.out} ({len(view.elements)} elements, theme {theme.get('id', 'model')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
