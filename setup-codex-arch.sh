#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# Configure Codex CLI for Arch Linux. Run as your ordinary user, never via sudo.
# Package installation uses sudo only for pacman. See README.md for examples.
# -----------------------------------------------------------------------------
set -euo pipefail

function show_help() {
  cat <<'HELP'
Usage: bash setup-codex-arch.sh [options]

Default: preview the merged configuration; do not apply changes.
  --apply                  Apply with automatic backups.
  --install-packages       Install Python/TOML and scripting tools with pacman.
  --install-cli            Install/update official npm Codex in a user prefix.
  --github-plugin          Install GitHub plugin after applying configuration.
  --model NAME             Default: gpt-6-astra (requires account access).
  --effort auto|LEVEL      auto selects highest advertised level (Ultra first).
  --experimental-context   Opt in to experimental context management.
  --zsh-file PATH          Append loader to this already-sourced file.
  --output DIR             Preview directory (default: ./codex-preview).
  -h, --help               Show help.

Requires: Arch Linux, Codex CLI, Python 3.11+, python-tomlkit, Zsh.
Installation flags require --apply. No login credentials are written.
HELP
}

function die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

apply=false
packages=false
cli=false
github=false
args=()
while (($#)); do
  case "$1" in
    --apply) apply=true; args+=("$1") ;;
    --install-packages) packages=true ;;
    --install-cli) cli=true ;;
    --github-plugin) github=true ;;
    --experimental-context) args+=("$1") ;;
    --model|--effort|--zsh-file|--output)
      (($# >= 2)) || die "Missing value for $1"
      args+=("$1" "$2")
      shift
      ;;
    -h|--help) show_help; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
  shift
done

[[ -f /etc/arch-release ]] || die 'This installer targets Arch Linux.'
((EUID != 0)) || die 'Run as your normal user, not root.'
if $packages || $cli || $github; then
  $apply || die 'Installation flags require --apply.'
fi

if $packages; then
  # Full upgrade avoids an unsupported Arch partial upgrade.
  sudo pacman -Syu --needed python python-tomlkit zsh git github-cli \
    ripgrep fd shellcheck shfmt python-ruff python-black curl
fi

if $cli; then
  command -v npm >/dev/null || die 'Install npm with pacman first; see README.'
  prefix="${XDG_DATA_HOME:-$HOME/.local/share}/codex-cli"
  target="$HOME/.local/bin/codex"
  mkdir -p "$HOME/.local/bin"
  if [[ -e "$target" || -L "$target" ]]; then
    [[ -L "$target" && "$(readlink "$target")" == "$prefix/bin/codex" ]] || \
      die "$target already exists and is not managed by this installer."
  fi
  npm install --global --prefix "$prefix" @openai/codex@latest
  ln -sfn "$prefix/bin/codex" "$target"
fi
export PATH="$HOME/.local/bin:$PATH"
command -v codex >/dev/null || die 'Codex missing; use --apply --install-cli.'
command -v python3 >/dev/null || die 'Python missing; use --install-packages.'
python3 -c 'import tomlkit' 2>/dev/null || \
  die 'Install python-tomlkit with pacman or use --install-packages.'

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
python3 "$script_dir/configure.py" "${args[@]}"

if $github; then
  codex plugin add github@openai-curated-remote
  printf '%s\n' 'Open /plugins in Codex and finish GitHub authorization.'
fi
