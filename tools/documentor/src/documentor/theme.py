"""The project's theme, from DocumentDrivenDX/ux-builder: one set of colors, fonts, and brand artwork
for every renderer (the site, the architecture views, the presentations, the decks).

A project names a theme in `.helix.yml`:

    publish:
      theme:
        name: synaptiq          # a theme in @ux-builder/tokens' manifest.json
        appearance: system      # light, dark, or system (the site follows the reader; drawings use the default)
        tokens: 1.6.0           # optional: another published version, or a path to a local tokens build

The tokens come from the published package `@ux-builder/tokens`, fetched once from the npm registry
into the documentor cache (no Node needed), or from a local path (a checkout's `packages/tokens`, or
its `dist`). Without `publish.theme`, or when the package cannot be fetched, the theme is `plain`,
packaged with documentor (`catalog/ux-builder/`).

The theme's role tokens (`--piq-color-*`, `--piq-font-*`) map onto documentor's drawing roles once,
here. The roles a theme has no token for (the walkthrough focus, a governing path, and the three
statuses a drawing marks) keep documentor's defaults; a model's own `[theme]` still overrides any
role.
"""

from __future__ import annotations

import io
import json
import os
import sys
import tarfile
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from documentor.lib import catalog

TOKENS_VERSION = "1.6.0"  # the @ux-builder/tokens release this documentor is tested against
REGISTRY = "https://registry.npmjs.org/@ux-builder/tokens/-/tokens-{version}.tgz"
DEFAULT_NAME = "plain"

# documentor's drawing role -> the ux-builder token that supplies it.
ROLES = {
    "ground": "piq-color-ground",
    "sunken": "piq-color-surface-sunken",
    "surface": "piq-color-surface",
    "border": "piq-color-border",
    "recessed": "piq-color-ground-recessed",
    "strong": "piq-color-text-strong",
    "text": "piq-color-text",
    "muted": "piq-color-text-muted",
    "accent": "piq-color-accent",
    "on_accent": "piq-color-on-accent",
    "font": "piq-font-body",
    "heading_font": "piq-font-heading",
    "mono_font": "piq-font-mono",
}


@dataclass
class Theme:
    name: str
    appearance: str  # light, dark, or system
    dist: Path  # the tokens' dist directory: manifest.json, themes/, fonts/, resolved/, brand/
    roles: dict = field(default_factory=dict)  # the default appearance's drawing roles
    dark: dict = field(default_factory=dict)  # the dark appearance's roles, when the theme has one
    appearances: tuple = ()
    brand: str = ""

    def css(self) -> list[Path]:
        """The stylesheets a site loads, in order: the theme, then its fonts."""
        return [p for p in (self.dist / "themes" / f"{self.name}.css", self.dist / "fonts" / f"{self.name}.css") if p.is_file()]

    def drawing_appearance(self) -> str:
        return "dark" if self.appearance == "dark" and self.dark else "light"


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "documentor" / "ux-builder-tokens"


def packaged() -> Path:
    return catalog() / "ux-builder"


def _dist(path: Path) -> Path | None:
    """The directory holding manifest.json: the path itself, or its `dist`."""
    for candidate in (path, path / "dist"):
        if (candidate / "manifest.json").is_file():
            return candidate
    return None


def fetch(version: str) -> Path | None:
    """The tokens of a published version, from the cache, downloading them on first use."""
    target = cache_dir() / version
    if (target / "manifest.json").is_file():
        return target
    try:
        with urllib.request.urlopen(REGISTRY.format(version=version), timeout=30) as response:
            data = response.read()
    except OSError as error:
        print(f"documentor: could not fetch @ux-builder/tokens {version} ({error}); using the packaged theme", file=sys.stderr)
        return None
    staging = target.with_name(target.name + ".partial")
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        members = [m for m in archive.getmembers() if m.name.startswith("package/dist/")]
        for member in members:
            member.name = member.name.removeprefix("package/dist/")
        archive.extractall(staging, members=members, filter="data")
    if target.exists():
        import shutil

        shutil.rmtree(target)
    staging.rename(target)
    return target


def _roles(dist: Path, name: str, appearance: str) -> dict:
    path = dist / "resolved" / f"{name}.{appearance}.json"
    if not path.is_file():
        return {}
    tokens = json.loads(path.read_text(encoding="utf-8")).get("tokens", {})
    return {role: tokens[token] for role, token in ROLES.items() if token in tokens}


def load(root: Path | None, config: dict) -> Theme:
    """The project's theme: `publish.theme`, else the packaged `plain`."""
    settings = ((config or {}).get("publish") or {}).get("theme") or {}
    if isinstance(settings, str):
        settings = {"name": settings}
    name = str(settings.get("name") or DEFAULT_NAME)
    appearance = str(settings.get("appearance") or "system")
    source = str(settings.get("tokens") or TOKENS_VERSION)
    dist = None
    if name != DEFAULT_NAME or settings.get("tokens"):
        local = Path(source) if Path(source).is_absolute() else (root or Path.cwd()) / source
        dist = _dist(local) if local.exists() else fetch(source)
    entry = None
    if dist is not None:
        manifest = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))
        entry = next((t for t in manifest.get("themes", []) if t.get("name") == name), None)
        if entry is None:
            print(f"documentor: @ux-builder/tokens has no theme named {name}; using the packaged theme", file=sys.stderr)
    if entry is None:
        dist, name = packaged(), DEFAULT_NAME
        entry = json.loads((dist / "manifest.json").read_text(encoding="utf-8"))["themes"][0]
    appearances = tuple(entry.get("appearances") or ("light",))
    default = entry.get("default") or appearances[0]
    light = "light" if "light" in appearances else default
    return Theme(
        name=name,
        appearance=appearance,
        dist=dist,
        roles=_roles(dist, name, light),
        dark=_roles(dist, name, "dark") if "dark" in appearances else {},
        appearances=appearances,
        brand=entry.get("brand") or "",
    )


def drawing_roles(theme: Theme) -> dict:
    """The roles a drawing uses: the light appearance, or the dark one when the project asks for dark.
    Each color also gets a plain name for the legend ("the outline on the project's own code: red")."""
    roles = dict(theme.dark if theme.drawing_appearance() == "dark" else theme.roles)
    for role in ("accent", "ground"):
        if role in roles:
            roles[f"{role}_name"] = color_name(roles[role])
    return roles


def color_name(color: str) -> str:
    """A plain word for a hex color, for a legend a reader can say aloud."""
    import colorsys

    value = color.lstrip("#")
    if len(value) != 6:
        return "accent"
    r, g, b = (int(value[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hue, lightness, saturation = colorsys.rgb_to_hls(r, g, b)
    if saturation < 0.15 or lightness > 0.94 or lightness < 0.08:
        return "white" if lightness > 0.94 else "black" if lightness < 0.15 else "gray"
    degrees = hue * 360
    for limit, word in ((15, "red"), (40, "orange"), (65, "yellow"), (160, "green"), (195, "teal"),
                        (255, "blue"), (290, "purple"), (335, "pink"), (360, "red")):
        if degrees < limit:
            return word
    return "accent"


def declared(config: dict) -> bool:
    """Whether the project names a theme (`publish.theme`); without one, renderers keep their own look."""
    return bool(((config or {}).get("publish") or {}).get("theme"))


def copy_assets(theme: Theme, dest: Path) -> dict:
    """Copy what a site needs to wear the theme under `dest`, keeping the tokens' own layout (so the
    CSS's relative URLs to fonts and brand artwork still resolve). Returns the paths, relative to
    `dest`, of the stylesheets and the favicon."""
    import re
    import shutil

    css = []
    for path in theme.css():
        relative = path.relative_to(theme.dist)
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        css.append(relative.as_posix())
        for url in re.findall(r'url\("?\./([^")]+)"?\)', path.read_text(encoding="utf-8")):
            asset = path.parent / url
            if asset.is_file():
                shutil.copy2(asset, target.parent / url)
    favicon = ""
    if theme.brand and (theme.dist / "brand" / theme.brand).is_dir():
        shutil.copytree(theme.dist / "brand" / theme.brand, dest / "brand" / theme.brand, dirs_exist_ok=True)
        mark = dest / "brand" / theme.brand / "mark.svg"
        favicon = mark.relative_to(dest).as_posix() if mark.is_file() else ""
    return {"css": css, "favicon": favicon}


def deck_theme(theme: Theme, base: dict) -> dict:
    """The deck theme (`deliverables/theme.yml`) with the project theme's colors: the accent as the
    primary hue and the neutrals, in light and dark. The typefaces stay the deck theme's: a deck must
    render the same in every presentation program, so it uses fonts every one of them has."""
    def palette(roles: dict) -> dict:
        names = {"primary": "accent", "ink": "text", "muted": "muted", "surface": "surface",
                 "surface_alt": "sunken", "border": "border"}
        return {key: roles[role] for key, role in names.items() if role in roles}

    result = dict(base)
    colors = dict(base.get("palette") or {})
    colors.update(palette(theme.roles))
    if theme.dark:
        colors["dark"] = dict(colors.get("dark") or {}) | palette(theme.dark)
    result["palette"] = colors
    return result
