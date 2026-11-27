#!/usr/bin/env python3
"""Two rules for Python in HELIX.

1. Python and its dependencies are managed with uv: standalone scripts declare their dependencies
   inline and are locked, and nothing launches a bare interpreter or installs with pip.
2. Using HELIX never requires running code: every script beside the skill has a by-hand route.

These are text and metadata checks. They show that a route is written down, not that following it
gives the script's result.
"""
import ast
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_SCRIPTS = ROOT / 'skills/helix/scripts'
FALLBACKS = ROOT / 'workflows/references/without-scripts.md'
PROJECTS = ('tools/documentor/',)
DISTRIBUTIONS = {'yaml': 'pyyaml', 'databricks': 'databricks-sdk', 'playwright': 'playwright'}
HEADER = re.compile(r'^# /// script\n(.*?)^# ///$', re.S | re.M)

# Records, examples for adopters' own projects, and test data are not how HELIX runs its Python.
NOT_SCANNED = (
    '.ddx/', 'docs/archive/', 'docs/examples/', 'docs/resources/', 'docs/helix/', 'docs/website/',
    'workflows/concerns/', 'tests/fixtures/', 'evals/results/', 'website/',
    'tests/test_python_policy.py',
    # Assert on fixture text that names an adopting project's own command.
    'tests/test_modularity.py',
)
# A Databricks notebook installs into its own kernel, which uv does not manage.
NOTEBOOK_PIP = ('docs/install/databricks-genie.md', 'README.md')

BARE_PYTHON = re.compile(
    r'(?<![\w./-])python3?\s+(?:-[cm]\b|-\s|"?\$|[\w./<>-]+\.py\b)'
)
PIP = re.compile(r'(?<![\w-])(?:pip3?|pipx)\s+install\b|"-m",\s*"pip"|actions/setup-python|python3-yaml')
UV_PYTHON = re.compile(r'uv run\b[^|;&\n]*?\bpython3?\b')


def tracked():
    out = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others', '--exclude-standard'],
                         capture_output=True, text=True, check=True).stdout
    return [name for name in out.splitlines() if (ROOT / name).is_file()]


def text_of(name):
    try:
        return (ROOT / name).read_text(encoding='utf-8')
    except UnicodeDecodeError:
        return ''


def has_header(name):
    return name != 'tests/test_python_policy.py' and bool(HEADER.search(text_of(name)))


def imports(path):
    found = set()
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        if isinstance(node, ast.Import):
            found |= {alias.name.split('.')[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split('.')[0])
    return found


def third_party(path, seen=None):
    """Third-party modules a script needs, following imports of its sibling modules."""
    seen = set() if seen is None else seen
    seen.add(path)
    needed = set()
    for module in imports(path):
        sibling = path.parent / f'{module}.py'
        if sibling.is_file():
            if sibling not in seen:
                needed |= third_party(sibling, seen)
        elif module not in sys.stdlib_module_names:
            needed.add(module)
    return needed


def entry_scripts():
    return [p for p in sorted(SKILL_SCRIPTS.glob('*.py'))
            if re.search(r'^if __name__ == .__main__.:', p.read_text(encoding='utf-8'), re.M)]


class UvManagesPython(unittest.TestCase):
    def test_every_skill_script_declares_its_dependencies(self):
        self.assertTrue(entry_scripts())
        for path in entry_scripts():
            with self.subTest(script=path.name):
                header = HEADER.search(path.read_text(encoding='utf-8'))
                self.assertIsNotNone(header, 'needs inline script metadata')
                declared = header[1].lower()
                for module in third_party(path):
                    self.assertIn(DISTRIBUTIONS.get(module, module), declared, f'imports {module}')

    def test_inline_metadata_is_locked(self):
        scripts = [n for n in tracked() if not n.startswith(NOT_SCANNED) and not n.endswith('.lock')
                   and has_header(n)]
        self.assertTrue(scripts)
        for name in scripts:
            with self.subTest(script=name):
                self.assertTrue((ROOT / f'{name}.lock').is_file(), f'run: uv lock --script {name}')
                result = subprocess.run(['uv', 'lock', '--check', '--script', str(ROOT / name)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_other_third_party_imports_come_from_a_uv_environment(self):
        root_project = (ROOT / 'pyproject.toml').read_text(encoding='utf-8').lower()
        local = {Path(n).stem for n in tracked() if n.endswith('.py')} | {'scripts', 'documentor'}
        for name in tracked():
            if (not name.endswith('.py') or name.startswith(NOT_SCANNED + PROJECTS) or has_header(name)
                    or (ROOT / name).parent == SKILL_SCRIPTS):
                continue
            for module in imports(ROOT / name) - local - set(sys.stdlib_module_names):
                with self.subTest(file=name, module=module):
                    self.assertIn(DISTRIBUTIONS.get(module, module), root_project)

    def test_no_command_wraps_uv_run_in_uv_run(self):
        doubled = [f'{name}:{number}' for name in tracked() if not name.startswith(NOT_SCANNED)
                   for number, line in enumerate(text_of(name).splitlines(), 1)
                   if re.search(r'uv run [^|;&`"\']*?(?<!-- )uv run ', line)]
        self.assertEqual(doubled, [])

    def test_script_mode_is_used_only_where_dependencies_are_inline(self):
        # `uv run --script` ignores the project, so a file without metadata gets no dependencies.
        wrong = [f'{name}: {target}' for name in tracked() if not name.startswith(NOT_SCANNED)
                 for target in re.findall(r'uv run (?:--quiet )?(?:--script )((?:scripts|tests|workflows)/[\w./-]+)', text_of(name))
                 if (ROOT / target).is_file() and not has_header(target)]
        self.assertEqual(wrong, [])

    def test_nothing_launches_bare_python_or_pip(self):
        found = []
        for name in tracked():
            if name.startswith(NOT_SCANNED) or name.endswith('.lock'):
                continue
            for number, line in enumerate(text_of(name).splitlines(), 1):
                rest = UV_PYTHON.sub('uv-managed', line)
                pip = PIP.search(rest) and not (name in NOTEBOOK_PIP and '%pip install' in rest)
                if pip or BARE_PYTHON.search(rest):
                    found.append(f'{name}:{number}: {line.strip()[:120]}')
        self.assertEqual(found, [], 'run Python through uv:\n' + '\n'.join(found))


class CodeIsOptional(unittest.TestCase):
    def test_every_skill_script_has_a_by_hand_route(self):
        sections = set(re.findall(r'^## ([\w-]+\.py)$', FALLBACKS.read_text(encoding='utf-8'), re.M))
        self.assertEqual(sections, {p.name for p in entry_scripts()})

    def test_workflows_that_name_a_script_point_to_the_by_hand_routes(self):
        names = '|'.join(re.escape(p.name) for p in entry_scripts())
        # The mode and action contracts and the generation prompts are what an agent follows.
        followed = [*(ROOT / 'workflows/modes').glob('*.md'), *(ROOT / 'workflows/actions').glob('*.md'),
                    *(ROOT / 'workflows/activities').glob('*/artifacts/*/prompt.md'), ROOT / 'skills/helix/SKILL.md']
        for path in followed:
            text = path.read_text(encoding='utf-8')
            if re.search(names, text):
                with self.subTest(file=str(path.relative_to(ROOT))):
                    self.assertRegex(text, r'without-scripts\.md|modes/validate\.md')


if __name__ == '__main__':
    unittest.main()
