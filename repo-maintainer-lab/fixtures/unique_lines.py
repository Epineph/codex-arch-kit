#!/usr/bin/env python3
import argparse
from pathlib import Path


def main():
  p = argparse.ArgumentParser(description="Print unique lines in input order.")
  p.add_argument("file", type=Path)
  args = p.parse_args()
  lines = args.file.read_text(encoding="utf-8").splitlines()
  seen = set()
  for line in lines:
    if line not in seen:
      print(line)
      seen.add(line)


if __name__ == "__main__":
  main()
