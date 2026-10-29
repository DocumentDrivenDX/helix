"""Publish explicitly referenced design schemas through the UMF schema browser.

Sources stay byte-for-byte intact. This module validates publication metadata and
transport, not native schema semantics or instance conformance.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import posixpath
import sys
from pathlib import Path
from urllib.parse import urlencode

import yaml

from documentor.lib import config_of, find_root, helix_root, publish_out
from documentor.record import split_frontmatter

BROWSER_VERSION = "2.0.0"
FORMATS = {"umf", "json-schema", "tablespec", "artifact-collection"}
OWNER = "documentor.schemas/1"
INDEX_MARKER = "<!-- documentor:schemas -->"


def local(root: Path, raw: str) -> Path:
    """References are repository-relative, including after symlink resolution."""
    path = (root / raw).resolve()
    if Path(raw).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError(f"schema path must stay inside the repository: {raw}")
    return path


def references(page: Path, root: Path) -> list[dict]:
    front, _ = split_frontmatter(page.read_text(encoding="utf-8"))
    try:
        data = yaml.safe_load(front) or {}
    except yaml.YAMLError as error:
        raise ValueError(f"{page}: invalid schema-reference frontmatter: {error}") from error
    metadata = (data.get("ddx") or {}) if isinstance(data, dict) else {}
    refs = metadata.get("schemas", []) if isinstance(metadata, dict) else []
    if not isinstance(refs, list):
        raise ValueError(f"{page}: ddx.schemas must be a list")
    checked = []
    for ref in refs:
        if not isinstance(ref, dict):
            raise ValueError(f"{page}: each schema reference must be a mapping")
        for key in ("id", "title", "version", "path", "schemaFormat"):
            if not isinstance(ref.get(key), str) or not ref[key].strip():
                raise ValueError(f"{page}: schema reference needs a nonempty string {key}")
        if ref["schemaFormat"] not in FORMATS:
            raise ValueError(f"{page}: unsupported schemaFormat {ref['schemaFormat']}")
        path = local(root, ref["path"])
        if path.suffix not in (".json", ".yaml", ".yml") or not path.is_file():
            raise ValueError(f"{page}: missing JSON/YAML schema: {ref['path']}")
        if path.stat().st_size > 4_000_000:
            raise ValueError(f"{page}: schema exceeds browser's 4 MB limit: {path}")
        # Parse for a useful build-time failure; retain original bytes for publication.
        text = path.read_text(encoding="utf-8")
        try:
            value = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
        except (ValueError, yaml.YAMLError) as error:
            raise ValueError(f"{page}: invalid schema source {ref['path']}: {error}") from error
        if not isinstance(value, (dict, bool)):
            raise ValueError(f"{page}: schema must be an object or a JSON Schema boolean")
        definition = ref.get("definition")
        if definition is not None:
            if (not isinstance(definition, list) or len(definition) != 2
                    or not all(isinstance(v, str) and v for v in definition)):
                raise ValueError(f"{page}: definition must be [moduleId, elementId]")
            if ref["schemaFormat"] != "umf" or not isinstance(value, dict) or not any(
                m.get("id") == definition[0] and any(e.get("id") == definition[1]
                    for e in m.get("elements", []) if isinstance(e, dict))
                for m in value.get("modules", []) if isinstance(m, dict)
            ):
                raise ValueError(f"{page}: definition does not exist: {definition}")
        checked.append(ref)
    return checked


def discover(root: Path, config: dict) -> list[dict]:
    sources = {local(root, helix_root(config)), local(root, publish_out(config))}
    entries: dict[str, dict] = {}
    from documentor.site import collect

    pages = {page for source in sources for page in source.rglob("*.md")
             if not any(p.startswith(".") for p in page.relative_to(source).parts)}
    pages.update(path for _, _, published in collect(root, config) for _, path, _ in published)
    for page in sorted(pages):
        local(root, page.relative_to(root).as_posix())
        for ref in references(page, root):
            identity = ref["id"] + "@" + ref["version"]
            path = local(root, ref["path"])
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            owner = page.relative_to(root).as_posix()
            entry = {"id": identity, "title": ref["title"], "category": "design",
                     "path": ref["path"], "format": "json" if path.suffix == ".json" else "yaml",
                     "schemaFormat": ref["schemaFormat"], "url": f"sources/{digest}{path.suffix}",
                     "description": f"Version {ref['version']}; source {ref['path']}",
                     "assets": [{"id": "source", "reference": ref["path"],
                                 "url": f"sources/{digest}{path.suffix}", "format": path.suffix[1:],
                                 "dataKind": "schema", "sha256": digest}],
                     "owners": [owner], "version": ref["version"], "sha256": digest}
            if identity in entries:
                previous = entries[identity]
                if any(previous[k] != entry[k] for k in ("path", "sha256", "schemaFormat", "title", "version")):
                    raise ValueError(f"conflicting schema identity {identity}: {owner}")
                if owner not in previous["owners"]:
                    previous["owners"].append(owner)
            else:
                entries[identity] = entry
    if "umf-tablespec" in (config.get("publish") or {}).get("traits", []):
        from documentor.umf_tables import tables

        for path, table in tables(root):
            identity = "tablespec:" + table["table_name"] + "@" + str(table["version"])
            digest = hashlib.sha256(local(root, path).read_bytes()).hexdigest()
            suffix = Path(path).suffix
            entry = {"id": identity, "title": table["table_name"], "category": "tables",
                     "path": path, "format": "yaml", "schemaFormat": "tablespec",
                     "url": f"sources/{digest}{suffix}", "description": f"Source: {path}",
                     "assets": [], "owners": [path], "version": str(table["version"]), "sha256": digest}
            if identity in entries:
                raise ValueError(f"conflicting schema identity {identity}")
            entries[identity] = entry
    if len(entries) > 10_000:
        raise ValueError("schema catalog exceeds browser's 10,000 entry limit")
    return [entries[k] for k in sorted(entries)]


def links(page: Path, root: Path, page_url: str) -> str:
    """Relative links work under both / and deployment prefixes such as /helix/."""
    lines = []
    for ref in references(page, root):
        query = {"schema": ref["id"] + "@" + ref["version"]}
        if ref.get("definition"):
            query["definition"] = json.dumps(ref["definition"], separators=(",", ":"))
        target = posixpath.relpath("schemas/explorer.html", page_url.strip("/"))
        label = html.escape(ref["title"])
        lines.append(f'<li><a href="{target}#{html.escape(urlencode(query), quote=True)}">'
                     f'Explore schema: {label}</a> (version {html.escape(ref["version"])})</li>')
    return '\n<ul class="design-schemas">' + "".join(lines) + "</ul>\n" if lines else ""


def package(root: Path, config: dict) -> Path:
    settings = (config.get("publish") or {}).get("schemas") or {}
    supplied = settings.get("browser_package")
    choices = [local(root, supplied)] if supplied else [
        root / "node_modules/@documentdrivendx/umf-schema-browser",
        root / "website/node_modules/@documentdrivendx/umf-schema-browser"]
    for path in choices:
        if not (path / "package.json").is_file():
            continue
        metadata = json.loads((path / "package.json").read_text())
        if metadata.get("name") != "@documentdrivendx/umf-schema-browser" or metadata.get("version") != BROWSER_VERSION:
            raise ValueError(f"schema browser must be @documentdrivendx/umf-schema-browser@{BROWSER_VERSION}")
        # Verify every released file before copying executable assets.
        manifest = json.loads((path / "release-manifest.json").read_text())
        if manifest.get("version") != 1 or not isinstance(manifest.get("sha256"), dict):
            raise ValueError("unsupported schema browser release manifest")
        declared = set(manifest["sha256"])
        required = {"index.js", "package.json", "assets/index.html", "LICENSE-MIT",
                    "LICENSE-APACHE", "THIRD_PARTY_NOTICES.md", "provenance.json"}
        actual = {p.relative_to(path).as_posix() for p in path.rglob("*") if p.is_file()}
        if not required <= declared or actual != declared | {"release-manifest.json", "SHA256SUMS"}:
            raise ValueError("schema browser integrity mismatch: release inventory")
        for name, digest in manifest["sha256"].items():
            file = local(path, name)
            if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
                raise ValueError(f"schema browser integrity mismatch: {name}")
        return path
    raise ValueError(f"design schemas need @documentdrivendx/umf-schema-browser@{BROWSER_VERSION}; "
                     "install it with your site's package manager, or set publish.schemas.browser_package")


MOUNT = '''import {mountSchemaBrowser} from './browser/index.js';
const base = new URL('./', import.meta.url);
const handle = mountSchemaBrowser(document.getElementById('schema-view'), {
  assetsUrl: new URL('browser/assets/', base).href,
  catalogUrl: new URL('catalog.json', base).href,
  assetBaseUrl: base.href,
  initialRoute: location.hash.slice(1),
  readOnlyLocalFiles: true, theme: 'auto', height: '85vh', onError: failed,
  onCatalogError: failed,
  onSelect: () => { document.getElementById('status').textContent = ''; },
  onNavigate: selection => {
    const params = new URLSearchParams(Object.entries(selection).filter(([, value]) => typeof value === 'string'));
    history.replaceState(null, '', '#' + params);
  }
});
function failed(error) {
  document.getElementById('status').textContent = 'Schema browser failed: ' + error.message;
}
handle.ready.then(() => {
  const query = new URLSearchParams(location.hash.slice(1));
  if (query.has('schema')) return handle.select(Object.fromEntries(query));
}).catch(failed);
window.addEventListener('hashchange', () => {
  const query = new URLSearchParams(location.hash.slice(1));
  if (query.has('schema')) handle.select(Object.fromEntries(query)).catch(failed);
});
'''


def owned_manifest(destination: Path) -> dict | None:
    """Recognize our inventory, never assume a directory named schemas is ours."""
    path = destination / "manifest.json"
    if destination.is_symlink() or path.is_symlink():
        raise ValueError(f"refusing symlinked schema output: {destination}")
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        owned = isinstance(data, dict) and data.get("generator") == OWNER
        # Older versions emitted this exact inventory envelope without an owner.
        legacy = (isinstance(data, dict) and set(data) == {"browserVersion", "schemas", "sha256", "indexSha256"}
                  and data.get("browserVersion") == BROWSER_VERSION
                  and isinstance(data.get("schemas"), list))
        hashes = data.get("sha256") if isinstance(data, dict) else None
        if not (owned or legacy) or not isinstance(hashes, dict) or not {
            "catalog.json", "mount.js", "browser/index.js"
        } <= set(hashes) or not isinstance(data.get("indexSha256"), str):
            raise ValueError("not a documentor schema inventory")
        if "manifest.json" in hashes:
            raise ValueError("recursive schema inventory")
        for name, digest in hashes.items():
            if not isinstance(name, str) or not isinstance(digest, str) or len(digest) != 64:
                raise ValueError("invalid schema inventory")
            output_file(destination, name)
        return data
    except (ValueError, OSError) as error:
        raise ValueError(f"refusing unowned schema output {destination}: {error}") from error


def output_file(destination: Path, name: str) -> Path:
    path = local(destination, name)
    if path != destination.resolve() / name:
        raise ValueError(f"refusing symlinked schema output: {destination / name}")
    return path


def remove_owned(destination: Path, manifest: dict, retained: set[str]) -> None:
    """Retire only unchanged files recorded by our previous publication."""
    obsolete = set(manifest["sha256"]) - retained
    for name in obsolete:
        path = output_file(destination, name)
        if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"][name]:
            raise ValueError(f"refusing to delete modified schema output: {path}")
    for name in obsolete:
        path = output_file(destination, name)
        if path.is_file():
            path.unlink()
    for directory in sorted(destination.rglob("*"), reverse=True):
        if directory.is_dir() and not directory.is_symlink() and not any(directory.iterdir()):
            directory.rmdir()


def publish(root: Path, config: dict, content: Path, static: Path, check: bool = False) -> int:
    """Generate/check a site section and its assets. No references means no dependency."""
    entries = discover(root, config)
    destination = static / "schemas"
    index = content / "schemas/_index.md"
    if not entries:
        try:
            previous = owned_manifest(destination)
        except ValueError:
            return 0  # No references authorize touching an unrelated schema tree.
    else:
        previous = owned_manifest(destination)
    if not entries:
        own_index = index.is_file() and not index.is_symlink() and (
            INDEX_MARKER in index.read_text(encoding="utf-8") or previous is not None and
            hashlib.sha256(index.read_bytes()).hexdigest() == previous["indexSha256"])
        if check and (previous or own_index):
            raise ValueError("stale schema publication: no remaining references")
        if previous:
            remove_owned(destination, previous, set())
            (destination / "manifest.json").unlink()
            if not any(destination.iterdir()):
                destination.rmdir()
        if own_index:
            index.unlink()
        return 0
    browser = package(root, config)
    catalog_entries = [{k: v for k, v in e.items() if k not in ("owners", "version", "sha256")} for e in entries]
    catalog = json.dumps({"version": 1, "entries": catalog_entries}, indent=2, ensure_ascii=False) + "\n"
    if len(catalog.encode()) > 8_000_000:
        raise ValueError("schema catalog exceeds browser's 8 MB limit")
    files: dict[str, bytes] = {"catalog.json": catalog.encode(), "mount.js": MOUNT.encode()}
    files["explorer.html"] = ('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Design schemas</title>
<body><p><a href="./" target="_top">Schema index and provenance</a></p>
<p id="status" role="status"></p><div id="schema-view"></div>
<noscript>Enable JavaScript to explore schemas. Source downloads are available in the schema index.</noscript>
<script type="module" src="./mount.js"></script></body></html>''').encode()
    files["browser/index.js"] = (browser / "index.js").read_bytes()
    for path in sorted((browser / "assets").rglob("*")):
        if path.is_file():
            files["browser/assets/" + path.relative_to(browser / "assets").as_posix()] = path.read_bytes()
    for name in ("LICENSE-MIT", "LICENSE-APACHE", "THIRD_PARTY_NOTICES.md", "provenance.json"):
        files[name] = (browser / name).read_bytes()
    lines = ['---', 'title: Design schemas', 'weight: 8', 'generated: true', '---', '', INDEX_MARKER, '',
             'Explore the schemas referenced by the governed designs. The browser inspects sources; '
             'it does not establish instance validity or semantic compatibility.', '',
             '<p><a href="explorer.html">Open the schema browser in a full window</a></p>', '',
             '<iframe src="explorer.html" title="UMF design schema browser" loading="lazy" '
             'style="width:100%;height:900px;border:0"></iframe>', '', '## Sources and provenance', '']
    for e in entries:
        files[e["url"]] = local(root, e["path"]).read_bytes()
        route = urlencode({"schema": e["id"]})
        lines.extend([f'- <a href="explorer.html#{route}">{html.escape(e["title"])}</a> '
                      f'(version {html.escape(e["version"])}); '
                      f'<a href="{e["url"]}">Download source</a>',
                      f'  Source: <code>{html.escape(e["path"])}</code>; SHA-256: <code>{e["sha256"]}</code>.',
                      '  Referenced by: ' + ', '.join(f'<code>{html.escape(o)}</code>' for o in e["owners"])])
    page = ("\n".join(lines) + "\n").encode()
    manifest = {"generator": OWNER, "browserVersion": BROWSER_VERSION, "schemas": entries,
                "sha256": {k: hashlib.sha256(v).hexdigest() for k, v in sorted(files.items())},
                "indexSha256": hashlib.sha256(page).hexdigest()}
    files["manifest.json"] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode()
    if check:
        if not index.is_file() or index.read_bytes() != page or any(
            not (destination / k).is_file() or (destination / k).read_bytes() != v for k, v in files.items()
        ):
            raise ValueError("stale schema publication; rerun documentor schemas")
        return 0
    if destination.exists() and previous is None and any(destination.iterdir()):
        raise ValueError(f"refusing unowned schema output: {destination}")
    if index.is_symlink() or index.exists() and not (
        INDEX_MARKER in index.read_text(encoding="utf-8") or previous is not None and
        hashlib.sha256(index.read_bytes()).hexdigest() == previous["indexSha256"] or
        index.read_bytes() == page.replace((INDEX_MARKER + "\n\n").encode(), b"")
    ):
        raise ValueError(f"refusing unowned schema index: {index}")
    for name in files:
        path = output_file(destination, name)
        if previous and path.exists() and name != "manifest.json" and name not in previous["sha256"]:
            raise ValueError(f"refusing to overwrite unowned schema file: {path}")
    if previous:
        remove_owned(destination, previous, set(files))
    for name, data in files.items():
        path = output_file(destination, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_bytes(page)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--content", help="content output directory (default: site's Hugo content root)")
    parser.add_argument("--static", help="asset output directory (default: site's static directory)")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    root = find_root(Path(args.root).resolve())
    config = config_of(root)
    from documentor.site import schema_output_dirs
    try:
        content, static = schema_output_dirs(root, config)
        return publish(root, config, Path(args.content).resolve() if args.content else content,
                       Path(args.static).resolve() if args.static else static, args.check)
    except (ValueError, OSError, yaml.YAMLError) as error:
        print(f"documentor schemas: {error}", file=sys.stderr)
        return 1
