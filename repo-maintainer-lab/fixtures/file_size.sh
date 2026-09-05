#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == --help ]]; then
  printf 'Usage: file_size.sh FILE\n'
  exit 0
fi
if [[ $# != 1 || ! -f $1 ]]; then
  printf 'Expected one existing file.\n' >&2
  exit 2
fi
size=$(wc -c < "$1")
printf '%s\n' "$size"
