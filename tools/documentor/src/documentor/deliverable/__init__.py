"""documentor's deliverable renderers: HELIX present-mode scripts to .pptx and HTML/PDF, and a toolchain report.

Usage:
    documentor deck render DEL.md OUT.pptx [--theme F] [--patterns F] [--look ID]
                                       render a deck script to .pptx (node; pptxgenjs is installed into
                                       the documentor cache on first use when NODE_PATH cannot resolve it)
    documentor deck qa DECK.pptx [--out DIR] [--format text|json] [--no-raster]
                                       geometry and visual QA of a rendered deck (LibreOffice, pdftoppm)
    documentor doc render DEL.md OUT.html [--kind brief|one-pager] [--pdf OUT.pdf] [--look ID] ...
                                       render a brief or one-pager to HTML, and PDF through Chrome
    documentor doctor                  what this host can do, one line per capability

The renderers live beside this module (render-deck.js, render-doc.js, deck-qa.py, lib/, icons/).
They read theme.yml and slide-patterns.yml from $DOCUMENTOR_CATALOG/deliverables/, else the HELIX
checkout above them, else documentor's packaged catalog.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NO_TOOLCHAIN = ("documentor: {what} needs {needs}; the deliverable script stands; "
                "`## Render` records the {target} was not produced")


def pptxgenjs_version() -> str:
    return json.loads((HERE / "package.json").read_text())["dependencies"]["pptxgenjs"]


def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "documentor" / "node" / pptxgenjs_version()


def resolvable(env: dict) -> bool:
    """Whether node resolves pptxgenjs under this environment's NODE_PATH."""
    done = subprocess.run(["node", "-e", "require.resolve('pptxgenjs')"], env=env, cwd=HERE,
                          capture_output=True, text=True)
    return done.returncode == 0


def with_node_path(env: dict, path: Path) -> dict:
    env = dict(env)
    env["NODE_PATH"] = os.pathsep.join(p for p in (str(path), env.get("NODE_PATH", "")) if p)
    return env


def pptxgenjs_env() -> dict:
    """An environment in which node resolves pptxgenjs, installing it into the cache when needed."""
    env = dict(os.environ)
    if resolvable(env):
        return env
    cache = cache_dir()
    modules = cache / "node_modules"
    if not (modules / "pptxgenjs").is_dir():
        cache.mkdir(parents=True, exist_ok=True)
        shutil.copy2(HERE / "package.json", cache / "package.json")
        lock = HERE / "package-lock.json"
        if lock.is_file():
            shutil.copy2(lock, cache / "package-lock.json")
        cmd = ["npm", "ci"] if lock.is_file() else ["npm", "install", "--no-audit", "--no-fund"]
        print(f"documentor: installing pptxgenjs {pptxgenjs_version()} into {cache}", file=sys.stderr)
        done = subprocess.run(cmd, cwd=cache, stdout=sys.stderr)
        if done.returncode != 0:
            raise RuntimeError(f"`{' '.join(cmd)}` failed in {cache} (exit {done.returncode})")
    return with_node_path(env, modules)


ERASER = ("@eraserlabs/diagrams", "0.2.0")  # the presentation renderer `documentor tour --render` drives


def npm_modules(package: str, version: str) -> Path:
    """A node_modules directory holding `package@version`, installed into the documentor cache on
    first use."""
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    cache = Path(base) / "documentor" / "node" / f"{package.replace('/', '+')}@{version}"
    modules = cache / "node_modules"
    if not (modules / package / "package.json").is_file():
        cache.mkdir(parents=True, exist_ok=True)
        (cache / "package.json").write_text(json.dumps({"private": True, "dependencies": {package: version}}))
        cmd = ["npm", "install", "--no-audit", "--no-fund"]
        print(f"documentor: installing {package} {version} into {cache}", file=sys.stderr)
        done = subprocess.run(cmd, cwd=cache, stdout=sys.stderr)
        if done.returncode != 0:
            raise RuntimeError(f"`{' '.join(cmd)}` failed in {cache} (exit {done.returncode})")
    return modules


def eraser_env() -> dict:
    """An environment in which `architecture/js/render.mjs` finds Eraser and a Chromium."""
    env = dict(os.environ)
    modules = env.get("ERASER_MODULES")
    if not (modules and (Path(modules) / ERASER[0]).is_dir()):
        env["ERASER_MODULES"] = str(npm_modules(*ERASER))
    if not env.get("CHROMIUM_PATH"):
        chrome = find_chrome()
        if not chrome:
            raise RuntimeError("no Chromium or Chrome found; set CHROMIUM_PATH")
        env["CHROMIUM_PATH"] = chrome
    return env


def run_node(script: str, args: list[str], env: dict | None = None) -> int:
    return subprocess.run(["node", str(HERE / script), *args], env=env).returncode


def usage(stream=sys.stdout) -> None:
    print(__doc__.strip(), file=stream)


def project_deck_theme(args: list[str]) -> list[str]:
    """`--theme <file>` for the project's ux-builder theme (`publish.theme`), when it names one and the
    call names no theme of its own."""
    if "--theme" in args:
        return []
    import tempfile

    import yaml

    from documentor import theme
    from documentor.lib import config_of, find_root, helix_catalog

    try:
        root = find_root(Path.cwd())
        config = config_of(root)
    except (OSError, SystemExit, ValueError):
        return []
    if not theme.declared(config):
        return []
    base = yaml.safe_load((helix_catalog() / "deliverables" / "theme.yml").read_text(encoding="utf-8")) or {}
    merged = theme.deck_theme(theme.load(root, config), base)
    handle = tempfile.NamedTemporaryFile("w", suffix=".yml", prefix="documentor-theme-", delete=False, encoding="utf-8")
    with handle:
        yaml.safe_dump(merged, handle, sort_keys=False)
    return ["--theme", handle.name]


def deck_main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        usage()
        return 0 if argv else 2
    sub, rest = argv[0], argv[1:]
    if sub == "render":
        if not (shutil.which("node") and shutil.which("npm")):
            print(NO_TOOLCHAIN.format(what="deck render", needs="node and npm", target=".pptx"), file=sys.stderr)
            return 3
        try:
            env = pptxgenjs_env()
        except (RuntimeError, OSError) as err:
            print(f"documentor: deck render could not install pptxgenjs: {err}", file=sys.stderr)
            print(NO_TOOLCHAIN.format(what="deck render", needs="pptxgenjs", target=".pptx"), file=sys.stderr)
            return 3
        return run_node("render-deck.js", rest + project_deck_theme(rest), env)
    if sub == "qa":
        return subprocess.run([sys.executable, str(HERE / "deck-qa.py"), *rest]).returncode
    print(f"documentor deck: unknown subcommand {sub!r} (render, qa)", file=sys.stderr)
    return 2


def doc_main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        usage()
        return 0 if argv else 2
    sub, rest = argv[0], argv[1:]
    if sub == "render":
        if not shutil.which("node"):
            print(NO_TOOLCHAIN.format(what="doc render", needs="node", target="HTML"), file=sys.stderr)
            return 3
        return run_node("render-doc.js", rest)
    print(f"documentor doc: unknown subcommand {sub!r} (render)", file=sys.stderr)
    return 2


CHROMES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable", "/usr/bin/chromium", "/usr/bin/chromium-browser",
)


def find_chrome() -> str:
    env = os.environ.get("CHROMIUM_PATH")
    if env and Path(env).exists():
        return env
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        if shutil.which(name):
            return shutil.which(name)
    return next((p for p in CHROMES if Path(p).exists()), "")


def agent_command() -> str:
    from documentor.write import COMMAND

    configured = ""
    config_file = Path.cwd() / ".helix.yml"
    if config_file.is_file():
        try:
            import yaml

            config = yaml.safe_load(config_file.read_text()) or {}
            configured = ((config.get("publish") or {}).get("agent") or {}).get("command") or ""
        except Exception:
            configured = ""
    return (os.environ.get("DOCUMENTOR_AGENT") or configured or COMMAND).split()[0]


def theme_line() -> tuple[bool, str]:
    """The theme `publish.theme` resolves to, or the packaged one."""
    from documentor import theme
    from documentor.lib import config_of, find_root

    try:
        root = find_root(Path.cwd())
        config = config_of(root)
    except (OSError, SystemExit, ValueError):
        root, config = Path.cwd(), {}
    if not theme.declared(config):
        return True, "theme: none named (publish.theme); the packaged neutral look"
    chosen = theme.load(root, config)
    wanted = (config.get("publish") or {}).get("theme")
    name = wanted.get("name") if isinstance(wanted, dict) else wanted
    ok = chosen.name == (name or theme.DEFAULT_NAME)
    return ok, f"theme {chosen.name} from {chosen.dist}" + ("" if ok else f" (wanted {name}; not found)")


def doctor_main(argv: list[str]) -> int:
    if argv and argv[0] in ("-h", "--help"):
        print("documentor doctor: what this host can do, one line per capability (always exits 0)")
        return 0
    lines: list[tuple[bool, str, str]] = []

    def have(name: str) -> str:
        return shutil.which(name) or ""

    def add(ok: bool, what: str, enables: str) -> None:
        lines.append((ok, what, enables))

    add(True, f"python {sys.version.split()[0]} ({sys.executable})", "documentor itself")
    add(bool(have("hugo")), f"hugo {have('hugo') or ''}".strip(), "site build")
    add(*theme_line(), "the look of the site, views, presentations, and decks")
    add(bool(have("go")), f"go {have('go') or ''}".strip(), "hextra theme (Hugo modules)")
    node, npm = have("node"), have("npm")
    add(bool(node), f"node {node}".strip(), "deck render, doc render")
    add(bool(npm), f"npm {npm}".strip(), "deck render (installs pptxgenjs into the cache)")
    if node and resolvable(dict(os.environ)):
        add(True, "pptxgenjs resolvable on NODE_PATH", "deck render")
    elif (cache_dir() / "node_modules" / "pptxgenjs").is_dir():
        add(True, f"pptxgenjs cached at {cache_dir() / 'node_modules'}", "deck render")
    else:
        add(bool(node and npm), f"pptxgenjs {pptxgenjs_version()} " + ("cacheable (npm installs it on first deck render)"
            if node and npm else "not resolvable and not cacheable"), "deck render")
    chrome = find_chrome()
    add(bool(chrome), f"Chrome/Chromium {chrome}".strip(), "doc render --pdf, tour render")
    add(bool(have("soffice")), f"LibreOffice soffice {have('soffice')}".strip(), "deck qa raster")
    add(bool(have("pdftoppm")), f"pdftoppm {have('pdftoppm')}".strip(), "deck qa raster, PDF inspection")
    raster = have("rsvg-convert") or have("magick") or have("convert")
    add(bool(raster), f"icon rasterizer {raster}".strip(), "deck icons (else badges show numbers)")
    agent = agent_command()
    add(bool(have(agent)), f"agent CLI {agent} {have(agent)}".strip(), "documentor write")
    base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    cached = Path(base) / "documentor" / "node" / f"{ERASER[0].replace('/', '+')}@{ERASER[1]}" / "node_modules"
    modules = Path(os.environ["ERASER_MODULES"]) if os.environ.get("ERASER_MODULES") else cached
    if (modules / ERASER[0]).is_dir():
        add(True, f"{ERASER[0]} in {modules}", "presentations (tour --render, site)")
    else:
        add(bool(node and npm), f"{ERASER[0]} {ERASER[1]} " + ("cacheable (npm installs it on first render)"
            if node and npm else "not installed and not cacheable"), "presentations (tour --render, site)")
    for ok, what, enables in lines:
        print(f"{'ok     ' if ok else 'missing'}  {what}: {enables}")
    return 0
