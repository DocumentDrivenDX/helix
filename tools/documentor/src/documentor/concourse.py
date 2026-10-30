"""Install an explicitly selected Concourse distribution into a Hugo microsite."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import yaml

FILES = {"concourse.js": "static/concourse/concourse.js",
         "concourse.css": "static/concourse/concourse.css",
         "concourse.html": "layouts/_partials/concourse.html"}


def install(root: Path, config: dict, site: Path) -> None:
    settings = ((config.get("publish") or {}).get("site") or {}).get("concourse")
    if not settings:
        return
    if not isinstance(settings, dict) or set(settings) - {"enabled", "site", "api", "package"}:
        raise ValueError("invalid publish.site.concourse settings")
    if not isinstance(settings.get("enabled", False), bool):
        raise ValueError("Concourse enabled must be boolean")
    name = settings.get("site")
    api = settings.get("api", "/__concourse/")
    if not isinstance(name, str) or not name.strip() or api != "/__concourse/":
        raise ValueError("Concourse requires a site identity and same-origin /__concourse/ API")
    package = settings.get("package") or os.environ.get("CONCOURSE_PACKAGE")
    if not package:
        raise ValueError("Concourse requires an explicitly pinned local package distribution")
    distribution = (root / package).resolve() / "dist"
    manifest = json.loads((distribution / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != "0.1.0" or set(manifest.get("files", {})) != set(FILES):
        raise ValueError("unsupported Concourse release inventory")
    verified = {}
    for source, destination in FILES.items():
        data = (distribution / source).read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest["files"][source]:
            raise ValueError(f"Concourse asset integrity mismatch: {source}")
        verified[site / destination] = data
    # Verify the complete inventory before writing any assets.
    for target, data in verified.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    hook = site / "layouts/_partials/custom/footer.html"
    hook.parent.mkdir(parents=True, exist_ok=True)
    # Existing host hooks are never overwritten; Hextra sites should call the
    # installed partial from their own hook/base template when one already exists.
    bases = [site / "layouts/baseof.html", site / "layouts/_default/baseof.html"]
    direct = any(p.is_file() and 'partial "concourse.html"' in p.read_text(encoding="utf-8") for p in bases)
    if not direct and not hook.exists():
        hook.write_text('{{ if site.Params.concourse.enabled }}{{ partial "concourse.html" . }}{{ end }}\n', encoding="utf-8")
    overlay = site / "config/_default/concourse.yaml"
    overlay.parent.mkdir(parents=True, exist_ok=True)
    overlay.write_text(yaml.safe_dump({"params": {"concourse": {
        "enabled": settings.get("enabled", False), "site": name, "api": api}}}, sort_keys=False), encoding="utf-8")
