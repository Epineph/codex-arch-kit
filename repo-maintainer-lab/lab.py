#!/usr/bin/env python3
"""Prepare and inspect a five-file, local Codex maintenance experiment.

This controller never invokes an AI, installs packages, commits, or pushes.
Use the VS Code Codex extension for agent work. Run --help for commands.
"""

import argparse
import ast
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / 'fixtures'
CANDIDATE = ROOT / 'candidate'
STATE = ROOT / '.runs'


def fail(message):
  raise SystemExit(f'Error: {message}')


def inventory(directory):
  """Reject links and record bytes and executable permissions for each file."""
  result = {}
  for path in sorted(directory.rglob('*')):
    if path.is_symlink():
      fail(f'Symbolic links are outside the lab scope: {path}')
    if path.is_file():
      name = path.relative_to(directory).as_posix()
      result[name] = {
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'mode': path.stat().st_mode & 0o777,
      }
  return result


def load_plan():
  if not (STATE / 'plan.json').exists():
    fail('Run prepare first.')
  return json.loads((STATE / 'plan.json').read_text())


def parse_jobs(value):
  jobs = set()
  for part in value.replace(',', ' ').split():
    ends = part.split('-')
    try:
      low, high = int(ends[0]), int(ends[-1])
    except ValueError:
      fail('Jobs must be numbers or ranges, such as 1,3 or 1-3.')
    if len(ends) > 2 or not 1 <= low <= high <= 3:
      fail('This experiment has jobs 1, 2, and 3 only.')
    jobs.update(range(low, high + 1))
  if not jobs:
    fail('Select at least one job.')
  return sorted(jobs)


def prepare(args):
  if CANDIDATE.exists() or STATE.exists():
    fail('Already prepared. Extract a fresh copy for a new experiment.')
  names = sorted(inventory(FIXTURES))
  wanted = names if not args.files else list(dict.fromkeys(args.files))
  if set(wanted) - set(names):
    fail('Every --files entry must be a fixture basename.')
  wanted = sorted(wanted)
  if args.extensions:
    extensions = {'.' + x.lstrip('.') for x in args.extensions.split(',')}
    wanted = [x for x in wanted if Path(x).suffix in extensions]
  selected = wanted[:args.max_files]
  if not selected:
    fail('No files selected.')
  jobs = parse_jobs(args.jobs)
  print(f'{len(wanted)} matched; {len(selected)} selected.')
  print('Targets: ' + ', '.join(selected))
  print('Jobs, in order: ' + ', '.join(map(str, jobs)))
  if not args.yes and input('Prepare this experiment? [y/N] ').lower() != 'y':
    return
  STATE.mkdir()
  shutil.copytree(FIXTURES, STATE / 'baseline')
  shutil.copytree(FIXTURES, CANDIDATE)
  plan = {'files': selected, 'jobs': jobs, 'baseline': inventory(FIXTURES)}
  (STATE / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n')
  print('Prepared. Open START-HERE.md in VS Code.')


def checkpoint(label):
  load_plan()
  if not label or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_'
                      for c in label):
    fail('Use lowercase letters, digits, hyphens, or underscores for labels.')
  inventory(CANDIDATE)
  stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
  destination = STATE / 'snapshots' / f'{stamp}-{label}'
  shutil.copytree(CANDIDATE, destination)
  (destination.parent / (destination.name + '.json')).write_text(
    json.dumps(inventory(destination), indent=2) + '\n'
  )
  print(f'Snapshot: {destination.name}')
  return destination


def diff(args):
  load_plan()
  before = inventory(STATE / 'baseline')
  after = inventory(CANDIDATE)
  for name in sorted(before.keys() | after.keys()):
    a, b = STATE / 'baseline' / name, CANDIDATE / name
    old = a.read_text().splitlines(True) if a.exists() else []
    new = b.read_text().splitlines(True) if b.exists() else []
    sys.stdout.writelines(difflib.unified_diff(
      old, new, fromfile=f'baseline/{name}', tofile=f'candidate/{name}'
    ))
    if name in before and name in after:
      if before[name]['mode'] != after[name]['mode']:
        print(f'Mode changed: {name}')


def check(args):
  plan = load_plan()
  original = plan['baseline']
  if inventory(STATE / 'baseline') != original:
    fail('Baseline changed since preparation.')
  current = inventory(CANDIDATE)
  changed = {name for name in original.keys() | current.keys()
             if original.get(name) != current.get(name)}
  if changed - set(plan['files']):
    fail('Out-of-scope changes: ' + ', '.join(sorted(changed -
                                                   set(plan['files']))))
  if original.keys() != current.keys():
    fail('Creation, deletion, and renaming are excluded from experiment 1.')
  errors = 0
  for name in plan['files']:
    path = CANDIDATE / name
    source = path.read_text()
    if path.suffix == '.sh':
      result = subprocess.run(['bash', '-n', str(path)], check=False)
      errors += result.returncode != 0
    elif path.suffix == '.py':
      try:
        ast.parse(source, filename=name)
      except SyntaxError as error:
        print(error)
        errors += 1
    for number, line in enumerate(source.splitlines(), 1):
      if len(line) > 81:
        print(f'WIDTH {name}:{number}: {len(line)} characters')
        errors += 1
  if not args.static_only:
    # This executes only the supplied disposable examples; it is not a sandbox.
    result = subprocess.run([sys.executable, str(ROOT / 'verify_examples.py')],
                            check=False)
    errors += result.returncode != 0
  print(f'Changed targets: {len(changed)}; failed checks: {errors}')
  if errors:
    raise SystemExit(1)


def restore(args):
  plan = load_plan()
  if args.snapshot == 'baseline':
    source = STATE / 'baseline'
    expected = plan['baseline']
  else:
    if Path(args.snapshot).name != args.snapshot:
      fail('Supply a snapshot ID, not a path.')
    source = STATE / 'snapshots' / args.snapshot
    metadata = source.parent / (source.name + '.json')
    if not source.is_dir() or not metadata.is_file():
      fail('Snapshot not found.')
    expected = json.loads(metadata.read_text())
  if inventory(source) != expected:
    fail('Snapshot content does not match its recorded hashes and modes.')
  names = args.files or plan['files']
  if set(names) - set(plan['files']):
    fail('Restore only selected target files.')
  print('Restore: ' + ', '.join(names))
  if not args.yes and input('Restore these files? [y/N] ').lower() != 'y':
    return
  checkpoint('before-restore')
  for name in names:
    destination = CANDIDATE / name
    fd, temporary = tempfile.mkstemp(dir=CANDIDATE)
    os.close(fd)
    try:
      shutil.copy2(source / name, temporary)
      os.replace(temporary, destination)
    finally:
      if os.path.exists(temporary):
        os.unlink(temporary)
  print('Restored. Previous content remains in the before-restore snapshot.')


def doctor(args):
  print(f'Python: {sys.version.split()[0]}')
  for name in ['bash', 'git', 'code', 'codex', 'shfmt', 'shellcheck', 'ruff']:
    print(f'{name}: {shutil.which(name) or "not on PATH"}')
  print('Codex CLI is optional here; use the signed-in VS Code extension.')
  print('No tools are installed and no accounts are authenticated by doctor.')


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  commands = parser.add_subparsers(dest='command', required=True)
  p = commands.add_parser('prepare', help='Select files and copy fixtures.')
  p.add_argument('--files', nargs='+', help='Space-separated fixture names.')
  p.add_argument('--extensions', help='Comma-separated suffixes, e.g. sh,py.')
  p.add_argument('--max-files', type=int, default=5)
  p.add_argument('--jobs', default='1-3')
  p.add_argument('--yes', '--noconfirm', action='store_true')
  p.set_defaults(func=prepare)
  p = commands.add_parser('doctor', help='Report available tools.')
  p.set_defaults(func=doctor)
  p = commands.add_parser('status', help='Show selected files and jobs.')
  p.set_defaults(func=lambda _: print(json.dumps(load_plan(), indent=2)))
  p = commands.add_parser('diff', help='Print a unified diff from the baseline.')
  p.set_defaults(func=diff)
  p = commands.add_parser('check', help='Check scope, syntax and examples.')
  p.add_argument('--static-only', action='store_true')
  p.set_defaults(func=check)
  p = commands.add_parser('checkpoint', help='Save a timestamped candidate.')
  p.add_argument('label')
  p.set_defaults(func=lambda args: checkpoint(args.label))
  p = commands.add_parser('snapshots', help='List saved snapshot IDs.')
  p.set_defaults(func=lambda _: print('\n'.join(
    x.name for x in sorted((STATE / 'snapshots').glob('*')) if x.is_dir()
  )))
  p = commands.add_parser('restore', help='Restore selected files with backup.')
  p.add_argument('snapshot', help='Snapshot ID or baseline.')
  p.add_argument('--files', nargs='+')
  p.add_argument('--yes', '--noconfirm', action='store_true')
  p.set_defaults(func=restore)
  args = parser.parse_args()
  if hasattr(args, 'max_files') and args.max_files < 1:
    parser.error('--max-files must be positive.')
  args.func(args)


if __name__ == '__main__':
  main()
