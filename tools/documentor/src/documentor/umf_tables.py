"""Structural reference for upstream monolithic UMF TableSpec 1.0 sources."""
from pathlib import Path
import json
import re

import yaml


def tables(root: Path) -> list[tuple[str, dict]]:
    from documentor.generate import _tracked

    found = []
    names = set()
    for path in sorted(set(_tracked(root, "**/*.yaml") + _tracked(root, "**/*.yml"))):
        # A non-git source tree may also contain a previous publication. Its
        # content-addressed downloads are outputs, not additional table sources.
        if path.parent.name == "sources" and (path.parent.parent / "manifest.json").is_file():
            continue
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"UMF table must stay inside repository: {path}")
        if path.stat().st_size > 4_000_000:
            raise ValueError(f"UMF table exceeds browser 4 MB limit: {path}")
        text = path.read_text(encoding="utf-8")
        if not re.search(r"^table_name:", text, re.M):
            continue
        value = yaml.safe_load(text)
        if not isinstance(value, dict) or str(value.get("version")) != "1.0" or "columns" not in value:
            continue
        name = value["table_name"]
        if not isinstance(name, str) or not name or not isinstance(value["columns"], list):
            raise ValueError(f"invalid UMF table: {path}")
        if name in names:
            raise ValueError(f"duplicate UMF table name: {name}")
        names.add(name)
        found.append((path.relative_to(root).as_posix(), value))
    return found


def reference(root: Path, page: dict) -> tuple[str, list[str]]:
    entries = tables(root)
    if not entries:
        return "", []

    def cell(value):
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace("|", "&#124;").replace("\n", " ")

    lines = ["Generated from upstream UMF TableSpec sources; the YAML is authoritative.", "",
             "Explore these sources with `@documentdrivendx/umf-schema-browser` in the site's Design schemas section.", ""]
    ids = {t["table_name"]: f"t{i}" for i, (_, t) in enumerate(entries)}
    diagram = ["```mermaid", "flowchart LR"]
    for path, table in entries:
        name = table["table_name"]
        diagram.append(f'  {ids[name]}[{json.dumps(name)}]')
        lines += [f"## {cell(name)}", "", f"Source: `{path}`", "",
                  f"Primary key: {cell(table.get('primary_key', 'not declared'))}", "",
                  f"Unique constraints: {cell(table.get('unique_constraints', 'not declared'))}", "",
                  "| Column | Type | Nullable |", "|---|---|---|"]
        for column in table["columns"]:
            if not isinstance(column, dict) or not column.get("name"):
                raise ValueError(f"invalid UMF column: {path}")
            lines.append(f"| {cell(column['name'])} | {cell(column.get('data_type', column.get('type', 'unspecified')))} | "
                         f"{cell(column.get('nullable', 'unspecified'))} |")
        lines += ["", "### Foreign keys", "", "| Column | Referenced table | Referenced column |", "|---|---|---|"]
        relationships = table.get("relationships") or {}
        if not isinstance(relationships, dict) or not isinstance(relationships.get("foreign_keys", []), list):
            raise ValueError(f"invalid UMF relationships: {path}")
        for fk in relationships.get("foreign_keys") or []:
            if not isinstance(fk, dict):
                raise ValueError(f"invalid UMF foreign key: {path}")
            target = fk.get("references_table", "unspecified")
            lines.append(f"| {cell(fk.get('column', 'unspecified'))} | {cell(target)} | {cell(fk.get('references_column', 'unspecified'))} |")
            if target in ids:
                diagram.append(f"  {ids[name]} --> {ids[target]}")
        lines.append("")
    diagram += ["```", ""]
    return "\n".join(lines + ["## Entity relationships", ""] + diagram), [p for p, _ in entries]
