#!/usr/bin/env python3
"""Validate every marketplace entry without fetching or installing plugins."""
import argparse
import json
from pathlib import Path
import re


def validate(root):
    catalog = json.loads((root / '.claude-plugin/marketplace.json').read_text())
    entries = catalog.get('plugins', [])
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise ValueError('plugins must be an array of entries')
    names = [entry.get('name') for entry in entries]
    if any(not isinstance(name, str) or not re.fullmatch(r'[a-z0-9][a-z0-9._-]*', name) for name in names):
        raise ValueError('every plugin needs a valid name')
    if len(names) != len(set(names)):
        raise ValueError('duplicate marketplace plugin name')
    if names.count('helix') != 1:
        raise ValueError('marketplace must contain exactly one helix plugin')
    for entry in entries:
        name = entry['name']
        source = entry.get('source', {})
        if not isinstance(source, dict) or source.get('source') not in ('url', 'git-subdir'):
            raise ValueError(f'{name}: expected url or git-subdir Git source')
        if not re.fullmatch(r'https://github.com/[^/]+/[^/]+(?:\.git)?', source.get('url', '')):
            raise ValueError(f'{name}: expected HTTPS GitHub repository URL')
        if source['source'] == 'git-subdir':
            path = source.get('path', '')
            if not path.startswith('./') or '..' in Path(path).parts or not Path(path).parts:
                raise ValueError(f'{name}: expected contained ./ plugin subdirectory')
        sha = source.get('sha')
        if sha is not None and not re.fullmatch(r'[0-9a-f]{40}', sha):
            raise ValueError(f'{name}: sha must be a full Git commit ID')
        if name != 'helix' and sha is None:
            raise ValueError(f'{name}: external plugins must pin a tested commit sha')
        if not entry.get('description'):
            raise ValueError(f'{name}: missing marketplace description')
    return catalog


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        catalog = validate(args.root)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(1, f'FAIL: marketplace validation: {error}\n')
    print('ok: marketplace entries: ' + ', '.join(entry['name'] for entry in catalog['plugins']))
