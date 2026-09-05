#!/usr/bin/env python3
import argparse


def main():
  p = argparse.ArgumentParser(description="Add numbers.")
  p.add_argument("numbers", nargs="+", type=float)
  args = p.parse_args()
  print(sum(args.numbers))


if __name__ == "__main__":
  main()
