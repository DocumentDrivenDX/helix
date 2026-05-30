#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""
Generate website reference pages for HELIX artifacts and cross-cutting
concerns from the upstream source-of-truth in `workflows/`.

Reads:
  workflows/activities/<activity>/artifacts/<slug>/   -> meta.yml, prompt.md,
                                                  template.md, example.md (sometimes)
  workflows/concerns/<slug>/                   -> concern.md, practices.md

Dependencies (requires/enables/informs/referenced_by) come from `meta.yml`
under `dependencies.*` and `relationships.*`. See ADR-004 — there is no
separate `dependencies.yaml` file in the catalog.

Writes:
  docs/website/content/reference/glossary/artifacts/_index.md
  docs/website/content/reference/glossary/artifacts/<slug>.md   (one per artifact)
  docs/website/content/reference/glossary/concerns/_index.md
  docs/website/content/reference/glossary/concerns/<slug>.md    (one per concern)

Idempotent — destination directories are wiped and rebuilt on every run.

Run with:
  uv run scripts/generate-reference.py
"""
from __future__ import annotations

import re
import shutil
import sys
import html
import posixpath
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_SRC = ROOT / "workflows" / "activities"
CONCERNS_SRC = ROOT / "workflows" / "concerns"
CONTENT_ROOT = ROOT / "docs" / "website" / "content"
ARTIFACTS_DEST = CONTENT_ROOT / "artifact-types"
CONCERNS_DEST = CONTENT_ROOT / "concerns"
LEGACY_GLOSSARY = CONTENT_ROOT / "reference" / "glossary"

ACTIVITIES = {
    "00-discover": {
        "num": 0,
        "slug": "discover",
        "label": "Discover",
        "summary": "Validate that an opportunity is worth pursuing before committing to a development cycle.",
    },
    "01-frame": {
        "num": 1,
        "slug": "frame",
        "label": "Frame",
        "summary": "Define what the system should do, for whom, and how success will be measured.",
    },
    "02-design": {
        "num": 2,
        "slug": "design",
        "label": "Design",
        "summary": "Decide how to build it. Capture trade-offs, contracts, and architecture decisions.",
    },
    "03-test": {
        "num": 3,
        "slug": "test",
        "label": "Test",
        "summary": "Define how we know it works. Plans, suites, and procedures that bind specs to implementation.",
    },
    "04-build": {
        "num": 4,
        "slug": "build",
        "label": "Build",
        "summary": "Implement against the specs and tests. Capture the implementation plan that scopes the work.",
    },
    "05-deploy": {
        "num": 5,
        "slug": "deploy",
        "label": "Deploy",
        "summary": "Ship to users with appropriate operational support, monitoring, and rollback plans.",
        "contract": (
            "Deploy artifacts cover four first-class surfaces in the current "
            "HELIX contract: `deployment-checklist`, `monitoring-setup`, "
            "`runbook`, and `release-notes`."
        ),
    },
    "06-iterate": {
        "num": 6,
        "slug": "iterate",
        "label": "Iterate",
        "summary": "Measure, align, and improve. Close the feedback loop back into the planning strand.",
    },
}

CORE_ARTIFACTS = {
    "00-discover": ["product-vision"],
    "01-frame": ["prd", "principles", "concerns", "feature-specification", "user-stories"],
    "02-design": ["architecture", "adr", "contract", "solution-design", "technical-design"],
    "03-test": ["test-plan", "story-test-plan"],
    "04-build": ["implementation-plan"],
    "05-deploy": ["deployment-checklist", "release-notes"],
    "06-iterate": ["metric-definition", "metrics-dashboard", "improvement-backlog"],
}

SUPPORTING_ARTIFACTS = {
    "00-discover": ["business-case", "competitive-analysis", "opportunity-canvas", "resource-summary"],
    "01-frame": [
        "compliance-requirements",
        "feasibility-study",
        "feature-registry",
        "parking-lot",
        "pr-faq",
        "research-plan",
        "risk-register",
        "security-requirements",
        "stakeholder-map",
        "threat-model",
        "validation-checklist",
    ],
    "02-design": ["data-design", "proof-of-concept", "security-architecture", "tech-spike"],
    "03-test": ["security-tests", "test-procedures", "test-suites"],
    "04-build": [],
    "05-deploy": ["monitoring-setup", "runbook"],
    "06-iterate": ["security-metrics"],
}

ARTIFACT_WEIGHTS = {
    slug: activity["num"] * 100 + idx
    for activity_key, activity in ACTIVITIES.items()
    for idx, slug in enumerate(
        CORE_ARTIFACTS.get(activity_key, []) + SUPPORTING_ARTIFACTS.get(activity_key, []),
        start=10,
    )
}

CORE_NAV_ORDER = [
    slug
    for activity_key in ACTIVITIES
    for slug in CORE_ARTIFACTS.get(activity_key, [])
]

CORE_NAV_WEIGHTS = {
    slug: idx * 10 + 10
    for idx, slug in enumerate(CORE_NAV_ORDER)
}

SIDEBAR_TITLES = {
    "adr": "ADR",
    "pr-faq": "PR-FAQ",
    "prd": "PRD",
}


# ---------------------------------------------------------------------------
# HELIX real-example mapping (PR 1: defined but DISABLED)
#
# Each entry maps an artifact slug to the path of HELIX's actual instance of
# that artifact in `docs/helix/`. When the mapping is enabled (PR 2), the
# generator embeds the real document as the artifact's worked example,
# normalized via the helpers below.
#
# This dict is the source-of-truth audit list for the alignment review
# ahead of the PR 2 flip. validate_helix_real_examples() hard-fails the
# generator if any path is missing — drift in docs/helix/ surfaces loudly.

HELIX_REAL_EXAMPLES = {
    # Activity 0 — Discover
    "product-vision":        "docs/helix/00-discover/product-vision.md",
    # Activity 1 — Frame
    "prd":                   "docs/helix/01-frame/prd.md",
    "concerns":              "docs/helix/01-frame/concerns.md",
    "feature-specification": "docs/helix/01-frame/features/FEAT-013-runtime-install-coverage.md",
    # Activity 2 — Design
    "architecture":          "docs/helix/02-design/architecture.md",
    "data-design":           "docs/helix/02-design/data-design.md",
    "security-architecture": "docs/helix/02-design/security-architecture.md",
    # CONTRACT-001 defines the DDx/HELIX boundary — most-cited downstream.
    "contract":              "docs/helix/02-design/contracts/CONTRACT-001-ddx-helix-boundary.md",
    "adr":                   "docs/helix/02-design/adr/ADR-002-tracker-write-safety-model.md",
    "solution-design":       "docs/helix/02-design/solution-designs/SD-002-first-class-principles.md",
    "technical-design":      "docs/helix/02-design/technical-designs/TD-012-artifact-types-navigation.md",
    # Activity 3 — Test
    "test-plan":             "docs/helix/03-test/test-plans/TP-014-helix-workflow-coverage.md",
    # Activity 4 — Build (no current instance; template-only)
    # Activity 5 — Deploy
    "runbook":               "docs/helix/05-deploy/runbook.md",
    "deployment-checklist":  "docs/helix/05-deploy/deployment-checklist.md",
    "release-notes":         "docs/helix/05-deploy/release-notes.md",
    "monitoring-setup":      "docs/helix/05-deploy/monitoring-setup.md",
    # Activity 6 — Iterate
    "improvement-backlog":   "docs/helix/06-iterate/improvement-backlog.md",
    "metrics-dashboard":     "docs/helix/06-iterate/metrics-dashboard.md",
    "security-metrics":      "docs/helix/06-iterate/security-metrics.md",
}

# Toggle the rendering path. Enabled in PR 2 after the alignment audit.
HELIX_REAL_EXAMPLES_ENABLED = True

# Of the slugs in HELIX_REAL_EXAMPLES, only these are publishable per the
# 2026-05-01 alignment review (AR-2026-05-01-public-examples.md).
# Others fall through to the example.md fallback or "no example yet".
HELIX_REAL_EXAMPLES_PUBLISHABLE = {
    "product-vision",
    "prd",
    "concerns",
    "feature-specification",
    "architecture",
    "adr",
    "contract",
    "technical-design",
    "solution-design",
    "test-plan",
    "data-design",
    "security-architecture",
    "implementation-plan",
    "runbook",
    "deployment-checklist",
    "release-notes",
    "monitoring-setup",
    "improvement-backlog",
    "metrics-dashboard",
    "security-metrics",
}

# Branch to pin embedded relative-link rewrites against.
HELIX_REPO_BLOB_BASE = "https://github.com/DocumentDrivenDX/helix/blob/main"


def validate_helix_real_examples() -> None:
    """Hard-fail if any HELIX_REAL_EXAMPLES path is missing.

    Stale mappings are not a recoverable condition: if the generator says X
    is sourced from Y and Y is missing, the site would be semantically
    wrong. Surfacing this loudly is the drift detection we want.
    """
    errors = []
    for slug, rel_path in HELIX_REAL_EXAMPLES.items():
        full = ROOT / rel_path
        if not full.exists():
            errors.append(f"  - '{slug}' → '{rel_path}' (file not found)")
    if errors:
        msg = (
            "ERROR: stale HELIX example mappings:\n"
            + "\n".join(errors)
            + "\n\nFix by either: (a) restoring the missing file, "
            "(b) updating the mapping in scripts/generate-reference.py, "
            "or (c) removing the mapping if the artifact no longer has a real example."
        )
        print(msg, file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Embed normalization (used by the rendering path that flips on in PR 2)


def strip_frontmatter(content: str) -> str:
    """Strip leading YAML frontmatter (between two --- lines) from content."""
    if not content.startswith("---\n"):
        return content
    end = content.find("\n---\n", 4)
    if end == -1:
        return content
    return content[end + 5:].lstrip("\n")


def shift_headings(content: str, by: int = 1) -> str:
    """Shift every ATX heading down by `by` levels (max H6).

    Skips headings inside fenced code blocks. Setext-style headings
    (===/---) are left alone — rare in HELIX docs and risky to rewrite.
    """
    out = []
    in_fence = False
    fence_marker = None
    for line in content.splitlines(keepends=True):
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif stripped.startswith(fence_marker):
                in_fence = False
                fence_marker = None
            out.append(line)
            continue
        if not in_fence and line.startswith("#"):
            # Count existing # marks
            level = len(line) - len(line.lstrip("#"))
            if 1 <= level <= 6 and (len(line) > level and line[level] == " "):
                new_level = min(level + by, 6)
                out.append("#" * new_level + line[level:])
                continue
        out.append(line)
    return "".join(out)


def rewrite_relative_links(content: str, source_path: str, base_url: str = HELIX_REPO_BLOB_BASE) -> str:
    """Rewrite relative markdown links to absolute repo URLs.

    A link `[text](relative/path.md)` in `source_path` becomes
    `[text](<base_url>/<resolved-path>)` so that embedded docs link
    correctly even though they're rendered under a different URL on the site.

    Absolute URLs (http, https), site-absolute paths (/foo), in-page anchors
    (#section), and mailto: links are left alone.
    """
    import os

    source_dir = os.path.dirname(source_path).replace("\\", "/")
    pattern = re.compile(r"\[([^\]]+)\]\(([^)\s]+)(\s+\"[^\"]*\")?\)")

    def rewrite(m: re.Match) -> str:
        text = m.group(1)
        url = m.group(2)
        title = m.group(3) or ""
        if url.startswith(("http://", "https://", "/", "#", "mailto:")):
            return m.group(0)
        # Split off any anchor
        if "#" in url:
            path_part, anchor = url.split("#", 1)
            anchor = "#" + anchor
        else:
            path_part, anchor = url, ""
        if not path_part:
            return m.group(0)
        resolved = os.path.normpath(os.path.join(source_dir, path_part)).replace("\\", "/")
        return f"[{text}]({base_url}/{resolved}{anchor}{title})"

    return pattern.sub(rewrite, content)


def normalize_embedded_doc(content: str, source_path: str) -> str:
    """Apply all embed normalizations: strip frontmatter, shift headings, rewrite links."""
    content = strip_frontmatter(content)
    content = shift_headings(content, by=1)
    content = rewrite_relative_links(content, source_path)
    return content


# ---------------------------------------------------------------------------
# Helpers


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text())
        return data if isinstance(data, dict) else {}
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: failed to parse {path}: {exc}", file=sys.stderr)
        return {}


def load_text(path: Path) -> str:
    return path.read_text() if path.exists() else ""


def humanize(slug: str) -> str:
    return slug.replace("-", " ").replace("_", " ").title()


def sidebar_title(name: str, slug: str) -> str:
    if slug in SIDEBAR_TITLES:
        return SIDEBAR_TITLES[slug]
    words = name.split()
    if len(words) <= 3:
        return name
    return humanize(slug)


def is_core_artifact(art: dict) -> bool:
    return art["slug"] in CORE_ARTIFACTS.get(art["activity_key"], [])


def is_supporting_artifact(art: dict) -> bool:
    return art["slug"] in SUPPORTING_ARTIFACTS.get(art["activity_key"], [])


def artifact_url(slug: str, slug_to_url: dict[str, str]) -> str:
    return slug_to_url.get(slug, f"/artifact-types/{slug}/")


def artifact_page_relurl(abs_url: str) -> str:
    """Relativize a root-absolute site path for use in an artifact-type page.

    Artifact-type pages live three levels deep (/artifact-types/<phase>/<slug>/),
    so a root-relative target becomes relative with three `../` hops. Relative
    links resolve correctly under any baseURL (root locally, /helix/ in
    production); a raw <a href="/..."> would drop the base path and 404 on the
    project site.
    """
    return "../../../" + abs_url.lstrip("/")


def site_relurl(page_url: str, target: str) -> str:
    """Relative link from page_url to target (both root-absolute site paths).

    The hextra `card` shortcode emits its `link` verbatim without applying the
    baseURL, so a root-absolute card link 404s on the /helix/ project site. A
    relative link resolves correctly under any baseURL.
    """
    rel = posixpath.relpath(target, page_url)
    if target.endswith("/") and not rel.endswith("/"):
        rel += "/"
    return rel


def artifact_output_path(art: dict) -> Path:
    return Path(art["activity"]["slug"]) / f"{art['slug']}.md"


def artifact_page_weight(art: dict) -> int:
    slug = art["slug"]
    activity = art["activity"]
    if is_core_artifact(art):
        return ARTIFACT_WEIGHTS.get(slug, activity["num"] * 100 + 10) - activity["num"] * 100
    return ARTIFACT_WEIGHTS.get(slug, activity["num"] * 100 + 90) - activity["num"] * 100


def yaml_quote(value: str) -> str:
    """Safe YAML double-quoted scalar."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def card_subtitle(text: str, limit: int = 160) -> str:
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text.replace('"', "&quot;")


def extract_markdown_section(md: str, heading: str) -> str:
    """Extract a top-level H2 section body from markdown."""
    if not md:
        return ""
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*\n(?P<body>.*?)(?=^##\s+|\Z)",
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(md)
    return match.group("body").strip() if match else ""


def compact_markdown(md: str, max_chars: int = 900) -> str:
    """Keep prompt-derived guidance readable without dumping the full prompt."""
    md = md.strip()
    if len(md) <= max_chars:
        return md
    cut = md[:max_chars].rsplit("\n", 1)[0].rstrip()
    return cut + "\n\n_Additional guidance continues in the full prompt below._"


def render_inline_relationships(items: list, all_slugs: set, slug_to_url: dict[str, str]) -> str:
    if not items:
        return "_None_"
    links = []
    for r in items:
        slug = r["slug"]
        name = sidebar_title(r["name"], slug) if slug in all_slugs else r["name"]
        label = f"[{name}]({artifact_url(slug, slug_to_url)})" if slug in all_slugs else name
        if r.get("required") is False:
            label += " *(optional)*"
        links.append(label)
    return "<br>".join(links)


def render_html_relationships(items: list, all_slugs: set, slug_to_url: dict[str, str]) -> str:
    if not items:
        return "<em>None</em>"
    links = []
    for r in items:
        slug = r["slug"]
        name = html.escape(sidebar_title(r["name"], slug) if slug in all_slugs else r["name"])
        if slug in all_slugs:
            label = f'<a href="{html.escape(artifact_page_relurl(artifact_url(slug, slug_to_url)))}">{name}</a>'
        else:
            label = name
        if r.get("required") is False:
            label += " <em>(optional)</em>"
        links.append(label)
    return "<br>".join(links)


def render_reference_row(label: str, value: str) -> str:
    return (
        "<tr>"
        f"<th>{html.escape(label)}</th>"
        f"<td>{value}</td>"
        "</tr>"
    )


def render_reference_details(summary: str, content: str) -> str:
    # Encode newlines as entities so the whole row stays a single physical line.
    # The reference table is raw HTML embedded in markdown; a blank line inside a
    # <pre><code> cell would terminate goldmark's HTML block and leak the rest of
    # the content as rendered markdown (stray headings, broken code display).
    body = html.escape(content.strip()).replace("\n", "&#10;")
    return (
        "<details>"
        f"<summary>{html.escape(summary)}</summary>"
        f"<pre><code>{body}</code></pre>"
        "</details>"
    )


def render_helix_document_links(slug: str) -> str:
    rel_path = HELIX_REAL_EXAMPLES.get(slug)
    if not rel_path:
        return ""
    full_path = ROOT / rel_path
    if not full_path.exists():
        return ""
    url = f"{HELIX_REPO_BLOB_BASE}/{rel_path}"
    return f'<a href="{html.escape(url)}"><code>{html.escape(rel_path)}</code></a>'


def render_artifact_reference_section(
    art: dict,
    activity: dict,
    output: str,
    rels: dict,
    all_slugs: set,
    slug_to_url: dict[str, str],
) -> list[str]:
    out: list[str] = []
    out.append("## Reference")
    out.append("")
    out.append("<table class=\"helix-reference-table\">")
    out.append("<tbody>")
    out.append(render_reference_row(
        "Activity",
        (
            f'<a href="{artifact_page_relurl("/reference/glossary/activities/")}"><strong>{html.escape(activity["label"])}</strong></a>'
            f" — {html.escape(activity['summary'])}"
        ),
    ))
    if output:
        out.append(render_reference_row("Default location", f"<code>{html.escape(output)}</code>"))
    out.append(render_reference_row("Requires", render_html_relationships(rels["requires"], all_slugs, slug_to_url)))
    out.append(render_reference_row("Enables", render_html_relationships(rels["enables"], all_slugs, slug_to_url)))
    if rels["informs"]:
        out.append(render_reference_row("Informs", render_html_relationships(rels["informs"], all_slugs, slug_to_url)))
    if rels["referenced_by"]:
        out.append(render_reference_row("Referenced by", render_html_relationships(rels["referenced_by"], all_slugs, slug_to_url)))
    helix_docs = render_helix_document_links(art["slug"])
    if helix_docs:
        out.append(render_reference_row("HELIX documents", helix_docs))
    if art["prompt"]:
        out.append(render_reference_row(
            "Generation prompt",
            render_reference_details("Show the full generation prompt", art["prompt"]),
        ))
    if art["template"]:
        out.append(render_reference_row(
            "Template",
            render_reference_details("Show the template structure", art["template"]),
        ))
    out.append("</tbody>")
    out.append("</table>")
    out.append("")
    return out


# ---------------------------------------------------------------------------
# Artifact collection


def collect_artifacts():
    artifacts = []
    for activity_key, activity in ACTIVITIES.items():
        activity_dir = ARTIFACTS_SRC / activity_key / "artifacts"
        if not activity_dir.exists():
            continue
        for art_dir in sorted(p for p in activity_dir.iterdir() if p.is_dir()):
            slug = art_dir.name
            artifacts.append({
                "slug": slug,
                "activity_key": activity_key,
                "activity": activity,
                "src_dir": art_dir,
                "meta": load_yaml(art_dir / "meta.yml"),
                "prompt": load_text(art_dir / "prompt.md"),
                "template": load_text(art_dir / "template.md"),
                "example": load_text(art_dir / "example.md") if (art_dir / "example.md").exists() else None,
            })
    return artifacts


def _safe_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def get_artifact_name(meta: dict, slug: str) -> str:
    return (
        _safe_dict(meta.get("artifact")).get("name")
        or humanize(slug)
    )


def get_artifact_description(meta: dict) -> str:
    desc = (
        meta.get("description")
        or _safe_dict(meta.get("artifact")).get("description")
        or ""
    )
    return desc.strip() if isinstance(desc, str) else ""


def get_relationships(meta: dict) -> dict:
    """Pull requires/enables/informs/referenced_by from meta.yml.

    Per ADR-004, `meta.yml` is the single source of truth for artifact-type
    dependencies — there is no separate `dependencies.yaml` file.
    """
    out = {"requires": [], "enables": [], "informs": [], "referenced_by": []}

    def _bucket_from(source: dict, key: str, name_field: str):
        items = []
        for d in _safe_dict(source.get("dependencies")).get(key, []) or []:
            if not isinstance(d, dict):
                continue
            slug = d.get("path")
            if not slug:
                continue
            items.append({
                "slug": slug,
                "name": d.get(name_field) or humanize(slug),
                "relationship": d.get("relationship", "") or "",
                "required": d.get("required", True),
                "activity": d.get("activity", ""),
            })
        return items

    out["requires"] = _bucket_from(meta, "requires", "input")
    out["enables"] = _bucket_from(meta, "enables", "output")

    rel = _safe_dict(meta.get("relationships"))
    for slug in rel.get("informs", []) or []:
        if isinstance(slug, str):
            out["informs"].append({"slug": slug, "name": humanize(slug)})
    for slug in rel.get("referenced_by", []) or []:
        if isinstance(slug, str):
            out["referenced_by"].append({"slug": slug, "name": humanize(slug)})

    return out


def get_output_location(meta: dict) -> str:
    out = _safe_dict(meta.get("output"))
    return (out.get("location") or "").strip()


def render_relationship_list(items: list, all_slugs: set, slug_to_url: dict[str, str]) -> str:
    if not items:
        return "_None._"
    lines = []
    for r in items:
        slug = r["slug"]
        name = sidebar_title(r["name"], slug) if slug in all_slugs else r["name"]
        rel = r.get("relationship", "")
        required = r.get("required", True)
        link = f"[{name}]({artifact_url(slug, slug_to_url)})" if slug in all_slugs else name
        line = f"- {link}"
        if rel:
            line += f" — {rel}"
        if required is False:
            line += " *(optional)*"
        lines.append(line)
    return "\n".join(lines)


def render_artifact_page(art: dict, all_slugs: set, slug_to_url: dict[str, str]) -> str:
    slug = art["slug"]
    activity = art["activity"]
    name = get_artifact_name(art["meta"], slug)
    desc = get_artifact_description(art["meta"])
    rels = get_relationships(art["meta"])
    output = get_output_location(art["meta"])
    purpose = extract_markdown_section(art["prompt"], "Purpose")
    key_principles = extract_markdown_section(art["prompt"], "Key Principles")
    lane = extract_markdown_section(art["prompt"], "Stay in Your Lane")
    checklist = extract_markdown_section(art["prompt"], "Quality Checklist")

    weight = artifact_page_weight(art)

    out: list[str] = []
    out.append("---")
    out.append(f"title: {yaml_quote(name)}")
    out.append(f"linkTitle: {yaml_quote(sidebar_title(name, slug))}")
    out.append(f"slug: {slug}")
    out.append(f"activity: {yaml_quote(activity['label'])}")
    out.append(f"artifactRole: {yaml_quote('core' if is_core_artifact(art) else 'supporting')}")
    out.append(f"weight: {weight}")
    out.append("generated: true")
    out.append("---")
    out.append("")

    out.append("## Purpose")
    out.append("")
    if purpose:
        out.append(compact_markdown(purpose, 900))
        out.append("")
    else:
        out.append(desc or f"_({slug} — description not yet captured in upstream `meta.yml`.)_")
        out.append("")

    if key_principles:
        out.append("## Authoring guidance")
        out.append("")
        out.append(compact_markdown(key_principles, 1000))
        out.append("")

    if lane:
        out.append("<details>")
        out.append("<summary>Boundaries: what belongs elsewhere</summary>")
        out.append("")
        out.append(lane)
        out.append("")
        out.append("</details>")
        out.append("")

    if checklist:
        out.append("<details>")
        out.append("<summary>Quality checklist from the prompt</summary>")
        out.append("")
        out.append(compact_markdown(checklist, 1200))
        out.append("")
        out.append("</details>")
        out.append("")

    if art["example"]:
        out.append("## Example")
        out.append("")
        out.append("<details open>")
        out.append("<summary>Show a worked example of this artifact</summary>")
        out.append("")
        out.append("``````markdown")
        out.append(art["example"].strip())
        out.append("``````")
        out.append("")
        out.append("</details>")
        out.append("")

    out.extend(render_artifact_reference_section(art, activity, output, rels, all_slugs, slug_to_url))

    return "\n".join(out)


def render_sidebar_separator(title: str, weight: int) -> str:
    out: list[str] = []
    out.append("---")
    out.append(f"title: {yaml_quote(title)}")
    out.append(f"weight: {weight}")
    out.append("generated: true")
    out.append("sidebar:")
    out.append("  separator: true")
    out.append("---")
    out.append("")
    return "\n".join(out)


def append_artifact_cards(
    out: list[str], artifacts: list[dict], slug_to_url: dict[str, str],
    page_url: str | None = None,
) -> None:
    out.append("{{< cards >}}")
    for art in artifacts:
        slug = art["slug"]
        name = get_artifact_name(art["meta"], slug)
        desc = get_artifact_description(art["meta"]) or slug
        target = artifact_url(slug, slug_to_url)
        link = site_relurl(page_url, target) if page_url else target
        out.append(
            f'  {{{{< card link="{link}" '
            f'title="{name}" subtitle="{card_subtitle(desc, 160)}" >}}}}'
        )
    out.append("{{< /cards >}}")
    out.append("")


def render_artifacts_index(artifacts: list, slug_to_url: dict[str, str]) -> str:
    artifact_by_slug = {a["slug"]: a for a in artifacts}
    core_artifacts = [artifact_by_slug[s] for s in CORE_NAV_ORDER if s in artifact_by_slug]

    out: list[str] = []
    out.append("---")
    out.append("title: Artifact Types")
    out.append("linkTitle: Types")
    out.append("weight: 3")
    out.append("generated: true")
    out.append("---")
    out.append("")
    out.append(
        "HELIX defines a catalog of **artifact types** — categories of governing "
        "document, each with a template, an authoring prompt, metadata, and quality "
        "criteria. Every project applying HELIX produces concrete artifacts that "
        "instantiate these types. Artifact types are reusable methodology content; "
        "they are not tied to DDx or any other runtime."
    )
    out.append("")
    out.append("There are two related public landing paths:")
    out.append("")
    out.append("- [/artifact-types/](/artifact-types/) is the reusable catalog: document shapes, prompts, and quality rules.")
    out.append("- [/artifacts/](/artifacts/) is the worked example: HELIX's own governing artifacts, authored from the catalog under `docs/helix/`.")
    out.append("")
    out.append(
        "The [HELIX skill](/skills/) uses this catalog and the artifact "
        "authority hierarchy to find drift between concrete artifacts and "
        "propose a plan for restoring alignment."
    )
    out.append("")
    out.append(
        "Browse by activity. Each activity lists the core artifacts first, then "
        "the supporting artifacts teams use when they need more detail, risk "
        "control, or operational depth."
    )
    out.append("")

    out.append("{{< cards >}}")
    for activity in ACTIVITIES.values():
        out.append(
            f'  {{{{< card link="{activity["slug"]}" title="{activity["label"]}" '
            f'subtitle="{card_subtitle(activity["summary"], 140)}" >}}}}'
        )
    out.append("{{< /cards >}}")
    out.append("")

    return "\n".join(out)


def render_activity_index(artifacts: list, slug_to_url: dict[str, str]) -> str:
    out: list[str] = []
    out.append("---")
    out.append("title: By Activity")
    out.append("linkTitle: By Activity")
    out.append("weight: 500")
    out.append("generated: true")
    out.append("---")
    out.append("")
    out.append(
        "The activity view shows the full artifact catalog in HELIX flow order. "
        "Each activity lists the core artifacts first, followed by supporting "
        "artifacts used when the project needs more evidence or control."
    )
    out.append("")

    by_activity: dict[str, list[dict]] = {}
    for a in artifacts:
        by_activity.setdefault(a["activity_key"], []).append(a)

    for activity_key, activity in ACTIVITIES.items():
        if activity_key not in by_activity:
            continue
        out.append(f"## {activity['label']}")
        out.append("")
        out.append(f"_{activity['summary']}_")
        out.append("")

        activity_artifacts = {a["slug"]: a for a in by_activity[activity_key]}
        core = [activity_artifacts[s] for s in CORE_ARTIFACTS.get(activity_key, []) if s in activity_artifacts]
        supporting = [activity_artifacts[s] for s in SUPPORTING_ARTIFACTS.get(activity_key, []) if s in activity_artifacts]
        supporting.extend(
            a for a in by_activity[activity_key]
            if a["slug"] not in set(CORE_ARTIFACTS.get(activity_key, []) + SUPPORTING_ARTIFACTS.get(activity_key, []))
        )

        if core:
            out.append("### Core Artifacts")
            out.append("")
            append_artifact_cards(out, core, slug_to_url)

        if supporting:
            out.append("### Supporting Artifacts")
            out.append("")
            append_artifact_cards(out, supporting, slug_to_url)

    return "\n".join(out)


def render_activity_index(activity_key: str, activity: dict, artifacts: list, slug_to_url: dict[str, str]) -> str:
    activity_artifacts = {a["slug"]: a for a in artifacts if a["activity_key"] == activity_key}
    core = [activity_artifacts[s] for s in CORE_ARTIFACTS.get(activity_key, []) if s in activity_artifacts]
    supporting = [activity_artifacts[s] for s in SUPPORTING_ARTIFACTS.get(activity_key, []) if s in activity_artifacts]
    supporting.extend(
        a for a in activity_artifacts.values()
        if a["slug"] not in set(CORE_ARTIFACTS.get(activity_key, []) + SUPPORTING_ARTIFACTS.get(activity_key, []))
    )

    out: list[str] = []
    out.append("---")
    out.append(f"title: {yaml_quote(activity['label'])}")
    out.append(f"linkTitle: {yaml_quote(activity['label'])}")
    out.append(f"weight: {activity['num'] * 10 + 10}")
    out.append("generated: true")
    out.append("---")
    out.append("")
    out.append(activity["summary"])
    out.append("")

    if activity.get("contract"):
        out.append(activity["contract"])
        out.append("")

    page_url = f"/artifact-types/{activity['slug']}/"
    if core:
        out.append("## Core Artifacts")
        out.append("")
        append_artifact_cards(out, core, slug_to_url, page_url)

    if supporting:
        out.append("## Supporting Artifacts")
        out.append("")
        append_artifact_cards(out, supporting, slug_to_url, page_url)

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Concerns


CONCERN_HEADING_MAP = [
    ("category", r"^##\s+Category\s*$"),
    ("areas", r"^##\s+Areas?\s*$"),
]


def parse_concern_md(md: str) -> dict:
    """Extract title, category, areas from a concern.md file."""
    out = {"title": "", "category": "", "areas": ""}
    if not md:
        return out

    # Title — first H1
    for line in md.splitlines():
        if line.startswith("# "):
            t = line[2:].strip()
            if t.lower().startswith("concern:"):
                t = t.split(":", 1)[1].strip()
            out["title"] = t
            break

    for key, pattern in CONCERN_HEADING_MAP:
        m = re.search(pattern + r"\n+(.+)", md, re.MULTILINE)
        if m:
            out[key] = m.group(1).strip()

    return out


CATEGORY_LABELS = {
    "tech-stack": "Tech Stack",
    "quality-attribute": "Quality Attributes",
    "testing": "Quality Attributes",
    "accessibility": "Quality Attributes",
    "internationalization": "Quality Attributes",
    "observability": "Quality Attributes",
    "security": "Security & Compliance",
    "infrastructure": "Infrastructure",
    "demo": "Documentation & Demos",
    "microsite": "Documentation & Demos",
}

CATEGORY_ORDER = [
    "Tech Stack",
    "Quality Attributes",
    "Security & Compliance",
    "Infrastructure",
    "Documentation & Demos",
]


def collect_concerns():
    concerns = []
    for cdir in sorted(p for p in CONCERNS_SRC.iterdir() if p.is_dir()):
        slug = cdir.name
        concern_md = load_text(cdir / "concern.md")
        practices_md = load_text(cdir / "practices.md")
        parsed = parse_concern_md(concern_md)
        concerns.append({
            "slug": slug,
            "concern_md": concern_md,
            "practices_md": practices_md,
            "parsed": parsed,
            "src_dir": cdir,
        })
    return concerns


def strip_first_h1(md: str) -> str:
    return re.sub(r"^#\s+.+\n+", "", md, count=1)


def render_concern_page(c: dict) -> str:
    slug = c["slug"]
    title = c["parsed"]["title"] or humanize(slug)
    category_raw = c["parsed"]["category"]
    category_label = CATEGORY_LABELS.get(category_raw.lower(), category_raw.title()) if category_raw else ""
    areas = c["parsed"]["areas"]

    out: list[str] = []
    out.append("---")
    out.append(f"title: {yaml_quote(title)}")
    out.append(f"slug: {slug}")
    out.append("generated: true")
    out.append("aliases:")
    out.append(f"  - /reference/glossary/concerns/{slug}")
    out.append("---")
    out.append("")

    if category_label or areas:
        bits = []
        if category_label:
            bits.append(f"**Category:** {category_label}")
        if areas:
            bits.append(f"**Areas:** {areas}")
        out.append(" · ".join(bits))
        out.append("")

    if c["concern_md"]:
        out.append("## Description")
        out.append("")
        out.append(rewrite_family_readme_links(strip_first_h1(c["concern_md"]).strip()))
        out.append("")

    if c["practices_md"]:
        out.append("## Practices by activity")
        out.append("")
        out.append(
            "Agents working in any of these activities inherit the practices below "
            "via the bead's context digest."
        )
        out.append("")
        out.append(rewrite_family_readme_links(strip_first_h1(c["practices_md"]).strip()))
        out.append("")

    return "\n".join(out)


def rewrite_family_readme_links(md: str) -> str:
    """Rewrite source-tree links like `../README-auth-family.md` to the Hugo URL.

    In `workflows/concerns/<slug>/concern.md`, the family README sits at
    `../README-auth-family.md`. The website mirror flattens concerns to
    `concerns/<slug>.md`, and Hugo serves the README at `/concerns/readme-auth-family/`.
    Rewrite so the published link points at the published page.
    """
    return re.sub(
        r"\]\(\.\./README-([a-z0-9-]+)\.md\)",
        lambda m: f"](../readme-{m.group(1)}/)",
        md,
    )


def render_concerns_index(concerns: list) -> str:
    # Group by display category (consolidated)
    by_display: dict[str, list[dict]] = {}
    for c in concerns:
        raw = c["parsed"]["category"].lower().strip()
        display = CATEGORY_LABELS.get(raw, humanize(raw) if raw else "Other")
        by_display.setdefault(display, []).append(c)

    # Within each category, sort alphabetically by slug
    for display, items in by_display.items():
        items.sort(key=lambda c: c["slug"])

    out: list[str] = []
    out.append("---")
    out.append("title: Concerns")
    out.append("weight: 4")
    out.append("generated: true")
    out.append("aliases:")
    out.append("  - /docs/glossary/concerns")
    out.append("  - /reference/glossary/concerns")
    out.append("---")
    out.append("")
    out.append(
        "**Cross-cutting concerns** are HELIX's mechanism for declaring "
        "shared standards once and propagating them everywhere agents work."
    )
    out.append("")
    out.append(
        "A concern bundles a description, components, constraints, and "
        "drift signals with per-activity practices. When an agent claims a "
        "bead, HELIX synthesizes a *context digest* that includes the "
        "active concerns — so the agent makes consistent technology "
        "choices, follows the project's conventions, and respects "
        "quality requirements without having to re-derive them from "
        "the codebase."
    )
    out.append("")
    out.append(
        "Concerns are how HELIX answers \"every project needs this kind "
        "of consistency\" without forcing any specific tech stack on "
        "the framework itself."
    )
    out.append("")

    seen = set()
    for cat in CATEGORY_ORDER + sorted(set(by_display) - set(CATEGORY_ORDER)):
        if cat in seen or cat not in by_display:
            continue
        seen.add(cat)
        out.append(f"## {cat}")
        out.append("")
        out.append("{{< cards >}}")
        for c in by_display[cat]:
            title = c["parsed"]["title"] or humanize(c["slug"])
            areas = c["parsed"]["areas"]
            sub = areas if areas else c["slug"]
            out.append(
                f'  {{{{< card link="{c["slug"]}" title="{title}" '
                f'subtitle="{card_subtitle(sub, 80)}" >}}}}'
            )
        out.append("{{< /cards >}}")
        out.append("")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# Main


def main() -> None:
    # Validate the HELIX_REAL_EXAMPLES mapping before doing anything else.
    # Hard-fails on stale paths so drift surfaces loudly.
    validate_helix_real_examples()

    artifacts = collect_artifacts()
    concerns = collect_concerns()

    all_slugs = {a["slug"] for a in artifacts}
    slug_to_url = {
        a["slug"]: f"/artifact-types/{artifact_output_path(a).with_suffix('').as_posix()}/"
        for a in artifacts
    }

    # Wipe and recreate destination directories
    if ARTIFACTS_DEST.exists():
        shutil.rmtree(ARTIFACTS_DEST)
    ARTIFACTS_DEST.mkdir(parents=True)

    if CONCERNS_DEST.exists():
        shutil.rmtree(CONCERNS_DEST)
    CONCERNS_DEST.mkdir(parents=True)

    # Activity section pages must live at the same route parent as their leaf
    # artifact pages. Hextra derives open/sidebar state from the content tree;
    # if activity indexes live elsewhere, leaf pages become dead ends.
    for activity_key, activity in ACTIVITIES.items():
        activity_dest = ARTIFACTS_DEST / activity["slug"]
        activity_dest.mkdir(parents=True, exist_ok=True)
        (activity_dest / "_index.md").write_text(
            render_activity_index(activity_key, activity, artifacts, slug_to_url)
        )

    for a in artifacts:
        output_path = ARTIFACTS_DEST / artifact_output_path(a)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_artifact_page(a, all_slugs, slug_to_url))

    # Artifacts index
    (ARTIFACTS_DEST / "_index.md").write_text(render_artifacts_index(artifacts, slug_to_url))

    # Per-concern pages
    for c in concerns:
        (CONCERNS_DEST / f"{c['slug']}.md").write_text(render_concern_page(c))

    # Family-level READMEs (e.g. README-auth-family.md) live alongside the
    # per-concern directories in workflows/concerns/ and are referenced by
    # `../README-auth-family.md` links from concern.md files. Publish them
    # at the same flat level so those links resolve in Hugo.
    for readme in sorted(CONCERNS_SRC.glob("README-*.md")):
        body = load_text(readme)
        title = "Auth family — ownership table"
        # Strip first H1 to avoid duplicate-title leak
        body = strip_first_h1(body)
        frontmatter = (
            "---\n"
            f"title: \"{title}\"\n"
            "generated: true\n"
            "---\n\n"
        )
        (CONCERNS_DEST / readme.name).write_text(frontmatter + body)

    # Concerns index
    (CONCERNS_DEST / "_index.md").write_text(render_concerns_index(concerns))

    # Remove legacy locations under /reference/glossary/ (now at top level)
    for legacy in (
        LEGACY_GLOSSARY / "artifacts.md",
        LEGACY_GLOSSARY / "concerns.md",
        LEGACY_GLOSSARY / "artifacts",
        LEGACY_GLOSSARY / "concerns",
    ):
        if legacy.exists():
            if legacy.is_dir():
                shutil.rmtree(legacy)
            else:
                legacy.unlink()

    print(f"Generated {len(artifacts)} artifact pages → {ARTIFACTS_DEST.relative_to(ROOT)}/")
    print(f"Generated {len(concerns)} concern pages   → {CONCERNS_DEST.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
