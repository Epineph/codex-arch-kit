#!/usr/bin/env bash
set -euo pipefail
if [[ ${1:-} == --help ]]; then
  printf 'Usage: greet.sh [NAME]\n'
  exit 0
fi
name=${1:-world}
printf 'Hello, %s!\n' "$name"
