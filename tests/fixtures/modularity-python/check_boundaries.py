"""Example adopting-project gate: domain must not import service, adapter or SDK.

This deliberately small Python fixture demonstrates the negative-control recipe.
It is not HELIX's universal dependency analyzer: relative/dynamic imports and
cycle/private-access checks require a project's chosen complete checker.
"""
import ast
import sys
from pathlib import Path


def violations(source_root):
    failures = []
    for path in Path(source_root).glob('domain*.py'):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [item.name for item in node.names]
            elif isinstance(node, ast.ImportFrom):
                names = [node.module or '']
            else:
                continue
            for name in names:
                if name.split('.')[0] in {'service', 'adapter', 'vendor_sdk'}:
                    failures.append(f'{path.name}:{node.lineno}: forbidden domain import {name}')
    return failures


if __name__ == '__main__':
    failures = violations(Path(__file__).parent / 'src')
    print('\n'.join(failures) if failures else 'Boundary check passed')
    sys.exit(bool(failures))
