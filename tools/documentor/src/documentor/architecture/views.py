"""Generate a project's architecture views from its model (architecture_model.py).

    documentor views [--root DIR] [--model FILE] [--directory DIR]   write the views between markers
    documentor views --check [--root DIR] [--model FILE]              fail on a stale view or bad model
    documentor views --emit DIR                                       also write each view to DIR/<id>.mmd

A view sits between `<!-- architecture-view: <id> -->` and `<!-- /architecture-view -->` in its
document; only the text between the markers is generated, so the prose around it stays hand-written.
Standard library only. Projects that must run this without the HELIX plugin vendor it, with
architecture_model.py beside it, unchanged.
"""

import argparse
import json
import re
from pathlib import Path

if __package__:
    from documentor.architecture.deploy import render_deployment
    from documentor.architecture.field_guide import field_guide_problems
    from documentor.architecture.field_page import render_field_guide
    from documentor.architecture.model import (
        Element,
        Model,
        Relation,
        View,
        declared_facts,
        default_model,
        fact_problems,
        find_root,
        load,
        model_problems,
        shown_relations,
    )
    from documentor.architecture.pages import render_cast, render_dag, render_journey, render_stack
else:  # run as a script: the sibling module is on the path
    from documentor.architecture.deploy import render_deployment
    from documentor.architecture.field_guide import field_guide_problems
    from documentor.architecture.field_page import render_field_guide
    from documentor.architecture.model import (
        Element,
        Model,
        Relation,
        View,
        declared_facts,
        default_model,
        fact_problems,
        find_root,
        load,
        model_problems,
        shown_relations,
    )
    from documentor.architecture.pages import render_cast, render_dag, render_journey, render_stack

_BLOCK = re.compile(
    r"(<!-- architecture-view: ([\w-]+) -->\n)(.*?)(<!-- /architecture-view -->)", re.S
)
_PLATE_GROUP = re.compile(r'<g id="([\w-]+)"')


# --- rendering ----------------------------------------------------------------------------------


def _directive(theme: dict) -> str:
    # Mermaid takes the font from the top-level setting; the theme variable alone is ignored.
    variables = {
        "fontFamily": theme["font"],
        "fontSize": "15px",
        "primaryColor": theme["surface"],
        "primaryBorderColor": theme["border"],
        "primaryTextColor": theme["strong"],
        "textColor": theme["text"],
        "lineColor": theme["muted"],
        "clusterBkg": theme["sunken"],
        "clusterBorder": theme["recessed"],
        "edgeLabelBackground": theme["sunken"],
        "tertiaryColor": theme["sunken"],
    }
    init = {"theme": "base", "fontFamily": theme["font"], "themeVariables": variables}
    return f"%%{{init: {json.dumps(init)}}}%%"


def _classes(model: Model) -> dict[str, tuple[str, str]]:
    """Each class's Mermaid style and legend entry: owner when built, status when not."""
    t, name, dashed = model.theme, model.system.name, "stroke-dasharray:5 4"
    ink = f"color:{t['strong']}"
    return {
        "person": (f"fill:{t['sunken']},stroke:{t['muted']},{ink}", "rounded = a person"),
        model.system.id: (
            f"fill:{t['surface']},stroke:{t['accent']},stroke-width:2px,{ink}",
            f"{t['accent_name']} outline = {name}'s code",
        ),
        "platform": (
            f"fill:{t['ground']},stroke:{t['muted']},{ink}",
            f"{t['ground_name']} = outside {name}",
        ),
        "placeholder": (
            f"fill:{t['surface']},stroke:{t['limited']},{dashed},{ink}",
            "amber dashed = a stand-in",
        ),
        "decided": (
            f"fill:{t['surface']},stroke:{t['purchasing']},{dashed},{ink}",
            "slate dashed = decided, not built",
        ),
        "unknown": (
            f"fill:{t['surface']},stroke:{t['evaluation']},{dashed},{ink}",
            "gray dashed = unknown",
        ),
    }


def _text(value: str) -> str:
    return value.replace('"', "#quot;")


def _node(element: Element) -> str:
    label = _text(element.name) + (f"<br/>{_text(element.detail)}" if element.detail else "")
    if element.kind == "store":
        return f'{element.id}[("{label}")]'
    if element.kind == "person":
        return f'{element.id}(["{label}"])'
    return f'{element.id}["{label}"]'


def _class_of(element: Element) -> str:
    return element.owner if element.status == "built" else element.status


def _node_lines(model: Model, view: View) -> list[str]:
    grouped = {member for group in view.groups for member in group.elements}
    lines: list[str] = []
    for group in view.groups:
        lines.append(f'    subgraph {group.id}["{_text(group.label)}"]')
        lines += [f"        {_node(model.elements[member])}" for member in group.elements]
        lines.append("    end")
    lines += [f"    {_node(model.elements[e])}" for e in view.elements if e not in grouped]
    return lines


def _edge(relation: Relation) -> str:
    arrow = "-->" if relation.status == "built" else "-.->"
    label = relation.label
    if relation.step:
        label = f"{relation.step} · {label}"
    elif relation.throughout:
        label = f"throughout · {label}"
    return f'    {relation.source} {arrow}|"{_text(label)}"| {relation.target}'


def _style_lines(model: Model, view: View, edges: list[Relation]) -> list[str]:
    classes: dict[str, list[str]] = {}
    for element_id in view.elements:
        classes.setdefault(_class_of(model.elements[element_id]), []).append(element_id)
    styles = _classes(model)
    lines = [f"    classDef {name} {styles[name][0]}" for name in styles if name in classes]
    lines += [f"    class {','.join(members)} {name}" for name, members in classes.items()]
    stepped = [str(i) for i, relation in enumerate(edges) if relation.step or relation.throughout]
    if stepped:
        lines.append(
            f"    linkStyle {','.join(stepped)} stroke:{model.theme['strong']},stroke-width:2.5px"
        )
    return lines


def _legend(model: Model, view: View, edges: list[Relation]) -> str:
    present = {_class_of(model.elements[e]) for e in view.elements}
    keys = [legend for name, (_, legend) in _classes(model).items() if name in present]
    if any(r.status != "built" for r in edges):
        keys.append("dashed arrow = not built or unknown")
    if any(r.step for r in edges):
        keys.append("dark numbered arrows = the request, in order")
    if any(r.throughout for r in edges):
        keys.append("throughout = runs for the whole request")
    return f"*Key: {' · '.join(keys)}. Generated by `{model.system.regenerate}`.*"


def _walkthrough(edges: list[Relation]) -> str:
    steps = sorted((r for r in edges if r.step), key=lambda r: r.step)
    if not steps:
        return ""
    lines = [f"{r.step}. **{r.label[:1].upper() + r.label[1:]}.** {r.note}" for r in steps]
    lines += [f"\n**Throughout: {r.label}.** {r.note}" for r in edges if r.throughout]
    return "\n\n**Follow a request.**\n\n" + "\n".join(lines)


def render(model: Model, view: View) -> str:
    """One view: its title and takeaway, the Mermaid flowchart, its legend and its walkthrough."""
    edges = shown_relations(model, view)
    header = (
        f"%% Generated from architecture-model.toml; edit the model, then run "
        f"`{model.system.regenerate}`."
    )
    body = [_directive(model.theme), header, f"flowchart {view.direction}"]
    body += _node_lines(model, view) + [_edge(r) for r in edges]
    body += _style_lines(model, view, edges)
    lead = f"**{view.title}.** {view.takeaway}\n\n" if view.title else ""
    chart = "```mermaid\n" + "\n".join(body) + "\n```\n\n"
    return lead + chart + _legend(model, view, edges) + _walkthrough(edges) + "\n"


# When the documents already live in a directory named architecture-views (the guide's), the
# drawings sit beside them instead of one level deeper.
FLAT = False


def svg_path(view: View) -> str:
    """Where a deployment view's SVG is written, relative to the documents' directory."""
    folder = Path(view.document).parent
    return (folder / f"{view.id}.svg").as_posix() if FLAT else (folder / "architecture-views" / f"{view.id}.svg").as_posix()


def render_view(model: Model, view: View) -> str:
    """A view of any type as the Markdown between its markers."""
    if view.type == "stack":
        return render_stack(model, view)
    if view.type == "cast":
        return render_cast(model, view)
    if view.type == "journey":
        return render_journey(model, view)
    if view.type == "dag":
        return render_dag(model, view)
    if view.type == "deployment":
        lead = f"**{view.title}.** {view.takeaway}\n\n" if view.title else ""
        drawing = f"{view.id}.svg" if FLAT else f"architecture-views/{view.id}.svg"
        image = f"[![{view.title or view.id}]({drawing})]({drawing})"
        key = f"*Generated by `{model.system.regenerate}`.*"
        return f"{lead}{image}\n\n{key}\n"
    return render(model, view)


# The views that are files of their own: a deployment view's SVG beside its document, and a
# field guide, which is the whole page its `document` names.
FILE_VIEWS = {"deployment": render_deployment, "field-guide": render_field_guide}


def output_path(view: View) -> str:
    """Where a view that is a file of its own is written, relative to the model's directory."""
    return view.document if view.type == "field-guide" else svg_path(view)


def _files(model: Model, directory: Path, check: bool) -> list[str]:
    """Write each file view, or report it stale; the files are build output too."""
    problems: list[str] = []
    for view in model.views.values():
        draw = FILE_VIEWS.get(view.type)
        if draw is None:
            continue
        target, drawn = directory / output_path(view), draw(model, view)
        current = target.read_text(encoding="utf-8") if target.is_file() else ""
        if check and current != drawn:
            problems.append(f"{output_path(view)}: stale; run `{model.system.regenerate}`")
        elif not check:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(drawn, encoding="utf-8")
    return problems


# --- documents ----------------------------------------------------------------------------------


def replace_views(
    text: str, rendered: dict[str, str], name: str = "architecture.md"
) -> tuple[str, list[str]]:
    """The document with each marked view regenerated, and any marker that names no view."""
    found = [match[2] for match in _BLOCK.finditer(text)]
    problems = [f"{name}: no view named {v} for this document" for v in found if v not in rendered]
    problems += [f"{name}: view {v} has no markers" for v in rendered if v not in found]
    problems += [f"{name}: view {v} is marked twice" for v in set(found) if found.count(v) > 1]

    def fill(match: re.Match[str]) -> str:
        body = rendered.get(match[2])
        return match[0] if body is None else f"{match[1]}\n{body}\n{match[4]}"

    return _BLOCK.sub(fill, text), problems


def _skeleton(rendered: dict[str, str], name: str) -> str:
    """A generated views page: one marker block per view, for `build` to fill under the guide."""
    title = Path(name).stem.replace("-", " ").capitalize()
    blocks = "\n\n".join(f"## {view_id.replace('-', ' ').replace('_', ' ').capitalize()}\n\n"
                         f"<!-- architecture-view: {view_id} -->\n<!-- /architecture-view -->" for view_id in rendered)
    return f"<!-- generated by `documentor views` from the architecture model; do not edit -->\n# {title}\n\n{blocks}\n"


def _update(document: Path, rendered: dict[str, str], command: str, check: bool, create: bool = False):
    """One document with its views regenerated, and what is wrong with it. With `create`, a
    document that does not exist is a generated views page under the guide."""
    if not document.is_file():
        if not create:
            return "", [f"{document.name}: no such document for views {sorted(rendered)}"]
        if check:
            return "", [f"{document.name}: the generated views page is missing; run `{command}`"]
        document.parent.mkdir(parents=True, exist_ok=True)
        document.write_text(_skeleton(rendered, document.name), encoding="utf-8")
    current = document.read_text(encoding="utf-8")
    updated, problems = replace_views(current, rendered, document.name)
    if check and updated != current:
        problems.append(f"{document.name}: the generated views are stale; run `{command}`")
    return updated, problems


def plate_problems(view: View, directory: Path) -> list[str]:
    """A plate draws exactly the view's elements, by the model's ids, so its meaning stays put."""
    if not view.plate:
        return []
    plate = directory / view.plate
    if not plate.is_file():
        return [f"view {view.id}: plate {view.plate} does not exist"]
    drawn = set(_PLATE_GROUP.findall(plate.read_text(encoding="utf-8")))
    missing = sorted(set(view.elements) - drawn)
    extra = sorted(drawn - set(view.elements))
    return [f"{view.plate}: does not draw {e} from view {view.id}" for e in missing] + [
        f"{view.plate}: draws {e}, which view {view.id} does not hold" for e in extra
    ]


def _emit(by_document: dict[str, dict[str, str]], emit: Path) -> None:
    emit.mkdir(parents=True, exist_ok=True)
    for rendered in by_document.values():
        for view_id, body in rendered.items():
            if "```mermaid" in body:
                (emit / f"{view_id}.mmd").write_text(body.split("```")[1].removeprefix("mermaid\n"))


def run(
    *, check: bool, model_path: Path, directory: Path, emit: Path | None = None, create: bool = False
) -> list[str]:
    """Check the model and its documents, and write the views unless checking; return problems.
    `directory` holds the documents the views go into; with `create`, missing ones are made."""
    global FLAT
    FLAT = directory.name == "architecture-views"
    model = load(model_path)
    root = find_root(model_path.parent)
    problems = model_problems(model, root) + fact_problems(model, declared_facts(model, root))
    if problems:
        return problems
    problems += [p for view in model.views.values() for p in plate_problems(view, directory)]
    problems += [p for view in model.views.values() for p in field_guide_problems(model, view)]
    if problems:
        return problems
    by_document: dict[str, dict[str, str]] = {}
    for view_id, view in model.views.items():
        if view.type == "field-guide":
            continue  # the page itself is the output, written with the files
        by_document.setdefault(view.document, {})[view_id] = render_view(model, view)
    updates = {}
    for name, rendered in by_document.items():
        command = model.system.regenerate
        updates[name], found = _update(directory / name, rendered, command, check, create)
        problems += found
    if not check and not problems:
        for name, text in updates.items():
            (directory / name).write_text(text, encoding="utf-8")
    if check or not problems:
        problems += _files(model, directory, check)
    if emit is not None:
        _emit(by_document, emit)
    return problems


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="documentor views", description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail on drift instead of writing")
    parser.add_argument(
        "--emit", type=Path, help="also write each view's Mermaid to this directory"
    )
    parser.add_argument("--root", type=Path, help="the project root (default: nearest .helix.yml)")
    parser.add_argument("--model", type=Path, help="the model (default: from .helix.yml)")
    parser.add_argument("--directory", type=Path, help="where the view documents live (default: beside the model)")
    parser.add_argument("--create", action="store_true", help="make a views page for a document that does not exist")
    arguments = parser.parse_args(argv)
    model_path = arguments.model or default_model(find_root(arguments.root or Path.cwd()))
    problems = run(
        check=arguments.check,
        emit=arguments.emit,
        directory=arguments.directory or model_path.parent,
        model_path=model_path,
        create=arguments.create,
    )
    for problem in problems:
        print(problem)
    if problems:
        raise SystemExit(1)
    print("Architecture views match the model" if arguments.check else "Architecture views written")


if __name__ == "__main__":
    main()
