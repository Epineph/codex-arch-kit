#!/usr/bin/env python3
"""Behavioural checks for the five supplied disposable examples only.

This runs programs as the current user; it is not a security sandbox.
Review side effects before adapting this suite to real maintenance scripts.
"""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent / 'candidate'


def run(name, *args):
  interpreter = 'bash' if name.endswith('.sh') else sys.executable
  return subprocess.run(
    [interpreter, str(ROOT / name), *map(str, args)],
    capture_output=True, text=True, timeout=5,
  )


class ExampleContracts(unittest.TestCase):
  def test_help(self):
    for path in sorted(ROOT.iterdir()):
      with self.subTest(path=path.name):
        result = run(path.name, '--help')
        self.assertEqual(result.returncode, 0)
        self.assertTrue(result.stdout.strip())

  def test_greeting(self):
    self.assertEqual(run('greet.sh').stdout, 'Hello, world!\n')
    self.assertEqual(run('greet.sh', 'Heini Hansen').stdout,
                     'Hello, Heini Hansen!\n')

  def test_counts(self):
    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / 'input with spaces.txt'
      path.write_bytes(b'alpha\nbeta')
      self.assertEqual(run('line_count.sh', path).stdout.strip(), '1')
      self.assertEqual(run('file_size.sh', path).stdout.strip(), '10')
      path.write_bytes(b'')
      self.assertEqual(run('line_count.sh', path).stdout.strip(), '0')
      self.assertEqual(run('file_size.sh', path).stdout.strip(), '0')
      for name in ['line_count.sh', 'file_size.sh']:
        for args in [[], [path.parent / 'missing'], [path, path]]:
          result = run(name, *args)
          self.assertEqual(result.returncode, 2)
          self.assertEqual(result.stdout, '')
          self.assertTrue(result.stderr)

  def test_sum(self):
    result = run('sum_numbers.py', '1.5', '-2', '3')
    self.assertEqual(result.returncode, 0)
    self.assertEqual(result.stdout, '2.5\n')
    self.assertEqual(run('sum_numbers.py', 'not-a-number').returncode, 2)
    self.assertEqual(run('sum_numbers.py').returncode, 2)

  def test_unique_order(self):
    with tempfile.TemporaryDirectory() as directory:
      path = Path(directory) / 'input with spaces.txt'
      path.write_text('beta\nalpha\nbeta\n\nalpha\n', encoding='utf-8')
      result = run('unique_lines.py', path)
      self.assertEqual(result.returncode, 0)
      self.assertEqual(result.stdout, 'beta\nalpha\n\n')
      path.write_text('', encoding='utf-8')
      self.assertEqual(run('unique_lines.py', path).stdout, '')


if __name__ == '__main__':
  unittest.main(verbosity=2)
