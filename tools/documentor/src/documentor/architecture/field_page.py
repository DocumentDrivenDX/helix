"""The field guide's page around its plate: header, legend, walkthrough, sources and limits.

Every sentence is the model's: the walkthrough is the numbered relations in order, each led by
why the call goes that way; the omissions are the elements the view leaves out, by layer; the
links are the other documents the same model draws. Self-contained HTML: inline SVG, no scripts,
no remote fonts, the project's theme as CSS variables. Standard library only.
"""

import re
from html import escape
from posixpath import dirname, relpath

if __package__:
    from documentor.architecture.field_guide import TYPE, shown, svg
    from documentor.architecture.model import Model, View
else:  # run as a script: the sibling modules are on the path
    from documentor.architecture.field_guide import TYPE, shown, svg
    from documentor.architecture.model import Model, View


def _mix(a: str, b: str, t: float) -> str:
    """The color t of the way from a to b, both #RRGGBB."""
    ca = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb, strict=True))


def _rich(text: str) -> str:
    """Escaped, with `code` spans kept as code."""
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", escape(text))


def _sentence(text: str) -> str:
    text = text.strip().rstrip(".")
    return text[:1].upper() + text[1:] + "."


def _walkthrough(model: Model, view: View) -> str:
    """The numbered steps in order, each led by why it goes that way; then what runs throughout."""
    steps = sorted((r for r in shown(model, view) if r.step), key=lambda r: r.step)
    items = [
        f"<li><strong>{escape(_sentence(r.why or r.label))}</strong> {_rich(r.note)}</li>"
        for r in steps
    ]
    out = ["<h2>Follow a request</h2>", "<ol>", *items, "</ol>"]
    for r in (r for r in shown(model, view) if r.throughout):
        lead = _sentence(f"Throughout: {r.why or r.label}")
        out.append(f'<p class="throughout"><strong>{escape(lead)}</strong> {_rich(r.note)}</p>')
    return "\n".join(out)


def _omissions(model: Model, view: View) -> str:
    """What the plate leaves out, by layer, and what in the model is not real yet."""
    left: dict[str, list[str]] = {}
    for e in model.elements.values():
        if e.id not in view.elements:
            left.setdefault(e.layer or "elsewhere", []).append(e.name)
    by_layer = "; ".join(f"{layer} ({', '.join(names)})" for layer, names in left.items())
    text = "This is a conceptual map, not a deployment topology."
    if by_layer:
        text += f" Left out on purpose, by layer: {by_layer}."
    unreal = [f"{e.name} ({e.status})" for e in model.elements.values() if e.status != "built"]
    if unreal:
        text += f" Not real yet: {', '.join(unreal)}."
    return escape(text)


def _continue(model: Model, view: View) -> str:
    """Links to the other documents the same model draws, relative to this page."""
    here, seen, links = dirname(view.document), set(), []
    for other in model.views.values():
        if other.document in seen or other.document == view.document or other.type == TYPE:
            continue
        seen.add(other.document)
        label = other.title or other.id
        href = escape(relpath(other.document, here or "."))
        links.append(f'<a href="{href}">{escape(label)}</a>')
    if not links:
        return ""
    joined = ", ".join(links)
    return f"Authority: <code>architecture-model.toml</code>, which also draws {joined}."


def _css(theme: dict) -> str:
    t = {k: theme.get(k, v) for k, v in _FALLBACK.items()}
    tint, tint_line = _mix(t["accent"], t["surface"], 0.9), _mix(t["accent"], t["surface"], 0.5)
    display = theme.get("display", 'Georgia, "Iowan Old Style", "Times New Roman", serif')
    return (
        f":root{{--bg:{t['ground']};--paper:{t['surface']};--sunken:{t['sunken']};--ink:{t['strong']};"
        f"--text:{t['text']};--muted:{t['muted']};--line:{t['border']};--rule:{t['recessed']};"
        f"--accent:{t['accent']};--tint:{tint};--tint-line:{tint_line};--link:{t['ok']};"
        f"--font:{t['font']};--display:{display}}}\n" + _STYLE
    )


_FALLBACK = {
    "ground": "#EEF1F4",
    "surface": "#FFFFFF",
    "sunken": "#F7F8FA",
    "strong": "#111418",
    "text": "#2E3440",
    "muted": "#5E6875",
    "border": "#D9DEE5",
    "recessed": "#CFD6DF",
    "accent": "#2F6F8F",
    "ok": "#3F7D58",
    "font": "ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif",
}

_STYLE = """\
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 var(--font)}
main{max-width:1440px;margin:auto;padding:54px 48px}p{margin:0 0 14px}strong{color:var(--ink)}
header{display:flex;justify-content:space-between;align-items:start;gap:40px;margin-bottom:30px}
header p{max-width:760px;font-size:19px;color:var(--muted);margin:0}
.eyebrow{font:600 12px/1.5 ui-monospace,Menlo,monospace;letter-spacing:2px;text-transform:uppercase;
  color:var(--accent)}
h1{font-family:var(--display);font-weight:600;color:var(--ink);font-size:46px;line-height:1.12;
  letter-spacing:-1px;margin:14px 0 18px}
h2{font-family:var(--display);color:var(--ink);font-size:22px;margin:6px 0 16px}
.stamp{border-left:2px solid var(--rule);padding-left:20px;min-width:200px;font-size:13px;
  color:var(--muted)}
.plate{background:var(--paper);border:1px solid var(--rule);border-radius:16px;overflow:auto;
  padding:16px}
svg{display:block;width:100%;min-width:940px;height:auto}
svg text{font-family:var(--font);fill:var(--ink)}
.lane{font:600 12px ui-monospace,Menlo,monospace;letter-spacing:1.5px;fill:var(--muted)}
.name{font-size:22px;font-weight:650}.detail{font-size:14.5px;fill:var(--muted)}
.node{fill:var(--sunken);stroke:var(--line);stroke-width:1.5}
.own{fill:var(--paper);stroke:var(--accent);stroke-width:2.5}
.owned{fill:var(--tint);stroke:var(--tint-line);stroke-dasharray:6 5}
.platform{fill:none;stroke:var(--rule);stroke-width:1.5}
.edge{fill:none;stroke:var(--ink);stroke-width:2.5;marker-end:url(#arrow)}
.quiet{fill:none;stroke:var(--muted);stroke-width:1.5;marker-end:url(#arrow)}
.edge-label{font-size:14px;fill:var(--muted);paint-order:stroke;stroke:var(--paper);stroke-width:8px;
  stroke-linejoin:round}
.badge{fill:var(--ink);stroke:var(--paper);stroke-width:3}
.number{fill:var(--paper);font-size:12px;font-weight:700}.pill{font-size:10.5px;letter-spacing:.8px}
.legend{display:flex;gap:28px;flex-wrap:wrap;margin:16px 6px 30px;color:var(--muted);font-size:13px}
.legend span:before{content:"";display:inline-block;width:27px;border-top:2.5px solid var(--ink);
  vertical-align:middle;margin-right:9px}
.legend .quiet-key:before{border-top:1.5px solid var(--muted)}
.legend .region:before{height:13px;border:1px dashed var(--tint-line);background:var(--tint)}
.legend .own-key:before{height:13px;border:2px solid var(--accent);background:var(--paper)}
.notes{display:grid;grid-template-columns:1.6fr 1fr;gap:44px}ol{padding-left:23px;margin:0}
li{padding:0 0 12px 9px;color:var(--muted)}.throughout{margin-top:14px}
aside{border-left:1px solid var(--rule);padding-left:30px}aside p{color:var(--muted);font-size:14px}
a{color:var(--link);text-underline-offset:3px}code{font:13px ui-monospace,Menlo,monospace}
footer{border-top:1px solid var(--rule);margin-top:30px;padding-top:16px;font-size:12px;
  color:var(--muted)}
@media(max-width:800px){main{padding:28px 16px}header{display:block}h1{font-size:34px}
  .stamp{margin-top:24px}.notes{grid-template-columns:1fr;gap:22px}aside{padding-left:0;border:0}}
@media print{@page{size:A3 landscape;margin:12mm}body{background:white}
  main{padding:0;max-width:none}header{margin-bottom:18px}h1{font-size:32px}header p{font-size:15px}
  .plate{break-inside:avoid;padding:4px}svg{min-width:0;height:140mm}.legend{margin:8px 4px 14px}
  .notes{font-size:11px;gap:30px}h2{font-size:17px}li{padding-bottom:5px}aside p{font-size:11px}
  a{color:inherit}footer{margin-top:15px}}"""


def render_field_guide(model: Model, view: View) -> str:
    """The whole page: header, plate, legend, walkthrough, sources and limits, footer."""
    name, own = escape(model.system.name), escape(model.system.id)
    continue_with = _continue(model, view)
    count = f"{len(view.elements)} of {len(model.elements)} elements"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name}: architecture field guide</title>
<!-- Generated from architecture-model.toml by {escape(model.system.regenerate)}: every box, line,
  number, and note is an element or relation of the model, each citing the code that shows it.
  Edit the model, not this file. Composition: HELIX's architecture field guide profile. -->
<style>
{_css(model.theme)}
</style>
</head>
<body>
<main>
<header>
<div>
<div class="eyebrow">{name} / architecture field guide</div>
<h1>{escape(view.title)}</h1>
<p>{escape(view.takeaway)}</p>
</div>
<div class="stamp">Developer orientation<br>Generated from the model<br>{count}</div>
</header>

<section class="plate" aria-label="Architecture map">
{svg(model, view)}
</section>
<div class="legend">
<span>The request's path: numbered steps in order, and the call that runs throughout</span>
<span class="quiet-key">Other calls</span>
<span class="own-key">{own}'s own code</span>
<span class="region">Shaded lane: what {own} owns and deploys</span>
</div>

<section class="notes">
<div>
{_walkthrough(model, view)}
</div>
<aside>
<h2>Sources and limits</h2>
<p>{_omissions(model, view)}</p>
<p>{continue_with}</p>
<p>Visual approach: HELIX's architecture field guide profile (responsibility lanes, numbered
reading order, notes beside the plate), in the project's theme.</p>
</aside>
</section>
<footer>Self-contained HTML, no remote fonts, libraries, or scripts. Generated from
<code>architecture-model.toml</code>; nothing is placed by hand.</footer>
</main>
</body>
</html>
"""
