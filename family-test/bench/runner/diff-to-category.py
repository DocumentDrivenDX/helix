#!/usr/bin/env python3
"""Map a PR file-diff to the bench categories that must run (plan §15c P14).

Usage:
  diff-to-category.py [--config PATH] [--diff PATH | --files FILE...] [--json]

Inputs:
  --diff PATH    file containing newline-separated repo-relative paths (one
                 per line). Convention: `git diff --name-only base...HEAD`.
  --files PATH   pass individual paths on the CLI; repeatable.
  --config PATH  override bench-categories.yml (defaults to sibling of repo).
  --json         emit JSON (default: newline-separated category names on
                 stdout, suitable for `xargs` / GitHub Actions matrix).

Exit codes:
  0  — success; categories printed
  2  — config invalid (rule references unknown category, glob malformed, …)
  3  — no diff provided (caller forgot --diff / --files)

Design notes:
  - EVERY matching rule contributes; we do not short-circuit on first match.
    A PR that edits SKILL.md AND stop-at-triggers.yml runs BOTH conversation,
    routing, AND stop_at — the union of contributions.
  - If no rule matches, return the `unmatched_fallback` (default `full`).
    The fallback prevents silently skipping coverage on an unanticipated
    refactor (per plan §19.2: "any unmatched path → full bench").
  - `**` in globs matches any number of path components (POSIX-style). We do
    NOT use fnmatch directly because fnmatch's `*` already matches `/`. We
    translate to a regex with explicit semantics.
  - The script has zero non-stdlib dependencies so it runs in a vanilla
    ubuntu-latest CI image without `pip install`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Minimal YAML loader — stdlib has no yaml. The categories file is hand-
# authored and stays small + simple (mapping, list, scalars). We avoid pulling
# in PyYAML because CI environments may not have it and we want this script
# to be portable. The loader handles the exact shape of bench-categories.yml
# and rejects anything more exotic (so we fail loudly if the file grows
# beyond what the loader supports).


class YamlParseError(Exception):
    pass


def _strip_comment(line: str) -> str:
    # respect '#' only when not inside quotes; the categories file uses no
    # quoted '#' so a simple scan is sufficient.
    in_q = False
    quote = ""
    out = []
    for ch in line:
        if in_q:
            out.append(ch)
            if ch == quote:
                in_q = False
        elif ch in ("'", '"'):
            in_q = True
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def _unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        return s[1:-1]
    return s


def _parse_inline_list(s: str) -> list[str]:
    s = s.strip()
    if not (s.startswith("[") and s.endswith("]")):
        raise YamlParseError(f"expected inline list, got: {s!r}")
    body = s[1:-1].strip()
    if not body:
        return []
    return [_unquote(p.strip()) for p in body.split(",")]


def load_yaml(path: Path) -> dict:
    """Tiny YAML subset loader scoped to bench-categories.yml.

    Supports: top-level scalar k: v, top-level list k: [a, b], nested
    mappings, lists of strings, lists of mappings. Indentation is 2 spaces.
    Comment lines (#…) and blank lines ignored.
    """
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    lines: list[tuple[int, str]] = []
    for ln in raw_lines:
        stripped = _strip_comment(ln)
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped))
    value, consumed = _parse_block(lines, 0, indent=0)
    if consumed != len(lines):
        raise YamlParseError(
            f"trailing content at line {consumed}: {lines[consumed][1]!r}"
        )
    if not isinstance(value, dict):
        raise YamlParseError("expected top-level mapping")
    return value


def _coerce_scalar(s: str):
    s = s.strip()
    if s.lower() in ("true", "false"):
        return s.lower() == "true"
    try:
        return int(s)
    except ValueError:
        pass
    return _unquote(s)


def _coerce_inline(v: str):
    v = v.strip()
    if v.startswith("["):
        return _parse_inline_list(v)
    return _coerce_scalar(v)


def _parse_block(lines: list[tuple[int, str]], start: int, indent: int):
    """Parse a block of lines starting at `start` at the given `indent`.

    Returns (parsed_value, next_index). The block ends at the first line whose
    indent is less than `indent` (or EOF).
    """
    if start >= len(lines) or lines[start][0] < indent:
        return {}, start
    first = lines[start][1].lstrip(" ")
    if first.startswith("- "):
        return _parse_list(lines, start, indent)
    return _parse_mapping(lines, start, indent)


def _parse_list(lines: list[tuple[int, str]], start: int, indent: int):
    items = []
    i = start
    n = len(lines)
    while i < n and lines[i][0] == indent:
        body = lines[i][1].lstrip(" ")
        if not body.startswith("- "):
            break
        item_body = body[2:].strip()
        i += 1
        if ":" in item_body and not item_body.startswith("["):
            # `- key: value` introducing a mapping item; subsequent sibling
            # keys live at indent+2 (one space + dash + space = 2 columns,
            # but YAML allows children of a list-item mapping at indent+2
            # relative to the dash's own column).
            k, _, v = item_body.partition(":")
            k = k.strip()
            v = v.strip()
            item: dict = {}
            child_indent = indent + 2
            if v == "":
                child_val, i = _parse_block(lines, i, child_indent + 2)
                item[k] = child_val
            else:
                item[k] = _coerce_inline(v)
            # consume sibling keys at child_indent
            while i < n and lines[i][0] == child_indent:
                sib = lines[i][1].lstrip(" ")
                if sib.startswith("- "):
                    break
                if ":" not in sib:
                    raise YamlParseError(f"expected key: at indent {child_indent}: {sib!r}")
                sk, _, sv = sib.partition(":")
                sk = sk.strip()
                sv = sv.strip()
                i += 1
                if sv == "":
                    sv_val, i = _parse_block(lines, i, child_indent + 2)
                    item[sk] = sv_val
                else:
                    item[sk] = _coerce_inline(sv)
            items.append(item)
        else:
            items.append(_coerce_inline(item_body))
    return items, i


def _parse_mapping(lines: list[tuple[int, str]], start: int, indent: int):
    out: dict = {}
    i = start
    n = len(lines)
    while i < n and lines[i][0] == indent:
        body = lines[i][1].lstrip(" ")
        if body.startswith("- "):
            break
        if ":" not in body:
            raise YamlParseError(f"expected key: at indent {indent}: {body!r}")
        k, _, v = body.partition(":")
        k = k.strip()
        v = v.strip()
        i += 1
        if v == "":
            child_val, i = _parse_block(lines, i, indent + 2)
            out[k] = child_val
        else:
            out[k] = _coerce_inline(v)
    return out, i


# ---------------------------------------------------------------------------
# Glob → regex
# ---------------------------------------------------------------------------


def glob_to_regex(glob: str) -> re.Pattern:
    """Translate a path glob to a regex.

    Semantics:
      `**` matches any number of path components (including zero)
      `*`  matches anything EXCEPT `/`
      `?`  matches any single char except `/`
      Other characters are escaped literally.
    """
    out = []
    i = 0
    n = len(glob)
    while i < n:
        c = glob[i]
        if c == "*":
            if i + 1 < n and glob[i + 1] == "*":
                # `**` — possibly `**/` or `/**`
                # consume two stars
                i += 2
                # consume a trailing `/` if any
                if i < n and glob[i] == "/":
                    out.append(r"(?:.*/)?")
                    i += 1
                else:
                    out.append(r".*")
            else:
                out.append(r"[^/]*")
                i += 1
        elif c == "?":
            out.append(r"[^/]")
            i += 1
        else:
            out.append(re.escape(c))
            i += 1
    return re.compile("^" + "".join(out) + "$")


# ---------------------------------------------------------------------------
# Mapper
# ---------------------------------------------------------------------------


def validate_config(cfg: dict) -> None:
    if "categories" not in cfg or not isinstance(cfg["categories"], list):
        raise SystemExit("config: missing or malformed `categories:` list")
    if "rules" not in cfg or not isinstance(cfg["rules"], list):
        raise SystemExit("config: missing or malformed `rules:` list")
    fallback = cfg.get("unmatched_fallback", "full")
    if fallback not in cfg["categories"]:
        raise SystemExit(
            f"config: unmatched_fallback={fallback!r} not in `categories:` list"
        )
    seen_ids = set()
    for r in cfg["rules"]:
        rid = r.get("id")
        if not rid:
            raise SystemExit(f"config: rule missing `id`: {r}")
        if rid in seen_ids:
            raise SystemExit(f"config: duplicate rule id {rid!r}")
        seen_ids.add(rid)
        cats = r.get("categories", [])
        if not isinstance(cats, list) or not cats:
            raise SystemExit(f"config: rule {rid!r} has empty `categories:`")
        for c in cats:
            if c not in cfg["categories"]:
                raise SystemExit(
                    f"config: rule {rid!r} references unknown category {c!r}"
                )
        globs = r.get("globs", [])
        if not isinstance(globs, list) or not globs:
            raise SystemExit(f"config: rule {rid!r} has empty `globs:`")


def map_paths(paths: list[str], cfg: dict) -> dict:
    """Return {'categories': [...sorted...], 'matched_rules': [...],
    'unmatched_paths': [...]}.

    Categories accumulate as a set (union of every matching rule). Order in
    the returned list is by `cfg['categories']` to give the CI matrix a
    stable order across runs.
    """
    matched_rules: list[str] = []
    matched_categories: set[str] = set()
    matched_any_path: set[str] = set()

    compiled: list[tuple[str, list[re.Pattern], list[str]]] = []
    for r in cfg["rules"]:
        pats = [glob_to_regex(g) for g in r["globs"]]
        compiled.append((r["id"], pats, r["categories"]))

    for p in paths:
        norm = p.replace("\\", "/").lstrip("./").strip()
        if not norm:
            continue
        for rid, pats, cats in compiled:
            if any(pat.match(norm) for pat in pats):
                matched_rules.append(f"{rid}<-{norm}")
                matched_categories.update(cats)
                matched_any_path.add(norm)
                # do NOT break — multiple rules can claim the same path

    unmatched = [p for p in paths if p.replace("\\", "/").lstrip("./").strip()
                 and p.replace("\\", "/").lstrip("./").strip() not in matched_any_path]

    if not matched_categories and not unmatched:
        # empty diff — run self-test only
        out_cats = ["self_test"]
    elif unmatched:
        # fallback: any unmatched path forces escalation per plan §19.2
        fallback = cfg.get("unmatched_fallback", "full")
        matched_categories.add(fallback)
        out_cats = [c for c in cfg["categories"] if c in matched_categories]
    else:
        out_cats = [c for c in cfg["categories"] if c in matched_categories]

    # If `full` is selected it implies all categories; expand for the CI
    # matrix consumer so downstream code does not need to special-case it.
    if "full" in out_cats:
        out_cats = [c for c in cfg["categories"] if c not in ("full",)]
        if "self_test" not in out_cats:
            out_cats.insert(0, "self_test")

    return {
        "categories": out_cats,
        "matched_rules": matched_rules,
        "unmatched_paths": sorted(set(unmatched)),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = REPO_ROOT / "family-test" / "bench" / "bench-categories.yml"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--diff", type=Path, default=None,
                    help="file with one repo-relative path per line")
    ap.add_argument("--files", action="append", default=[],
                    help="repo-relative path (repeatable)")
    ap.add_argument("--json", action="store_true",
                    help="emit JSON summary on stdout")
    args = ap.parse_args(argv)

    if not args.config.exists():
        print(f"config not found: {args.config}", file=sys.stderr)
        return 2
    cfg = load_yaml(args.config)
    validate_config(cfg)

    paths: list[str] = []
    if args.diff:
        if not args.diff.exists():
            print(f"diff file not found: {args.diff}", file=sys.stderr)
            return 3
        paths.extend(
            ln.strip() for ln in args.diff.read_text(encoding="utf-8").splitlines()
            if ln.strip()
        )
    paths.extend(args.files)

    if not paths and not args.diff:
        # No input at all — that's a usage bug, not "empty diff".
        print("no paths supplied (use --diff or --files)", file=sys.stderr)
        return 3

    result = map_paths(paths, cfg)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for c in result["categories"]:
            print(c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
