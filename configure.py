#!/usr/bin/env python3
"""Preview and apply a personal Codex setup, preserving unrelated TOML keys.

Use setup-codex-arch.sh on Arch Linux. This helper can also render and validate
against an installed CLI on another host. No model inference is requested.
"""

from __future__ import annotations

import argparse
from collections.abc import MutableMapping
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import tomlkit

ROOT = Path(__file__).resolve().parent
BEGIN = "# BEGIN HEINI CODEX SETUP"
END = "# END HEINI CODEX SETUP"


def run(args, *, env=None, timeout=45):
  """Capture diagnostics without invoking a shell or expanding arguments."""
  return subprocess.run(
    args, text=True, capture_output=True, stdin=subprocess.DEVNULL,
    env=env, timeout=timeout, check=False
  )


def merge(target, source):
  """Replace only managed values; retain unrelated keys and TOML comments."""
  for key, value in source.items():
    if isinstance(value, MutableMapping):
      if key not in target:
        target[key] = tomlkit.table()
      if not isinstance(target[key], MutableMapping):
        raise ValueError(f"Cannot merge table into existing scalar: {key}")
      merge(target[key], value)
    else:
      target[key] = value


def marked(text, body):
  """Replace our unique block, or append it while preserving other content."""
  block = f"{BEGIN}\n{body.rstrip()}\n{END}"
  if BEGIN in text or END in text:
    if text.count(BEGIN) != 1 or text.count(END) != 1:
      raise ValueError("Ambiguous managed markers; repair before rerunning.")
    start, stop = text.index(BEGIN), text.index(END)
    if stop < start:
      raise ValueError("Managed block end occurs before its beginning.")
    return text[:start] + block + text[stop + len(END):]
  return text.rstrip() + ("\n\n" if text.strip() else "") + block + "\n"


def read(path):
  return path.read_text() if path.exists() else ""


def advertised_effort(model):
  """Use the refreshed CLI catalogue; bundled entries do not prove access."""
  try:
    result = run(["codex", "debug", "models"])
    if result.returncode:
      raise ValueError("catalogue command failed")
    data = json.loads(result.stdout)
    entries = data if isinstance(data, list) else data.get("models", [])
    for item in entries:
      if item.get("slug", item.get("id")) != model:
        continue
      levels = item.get("supported_reasoning_levels", [])
      values = {
        level if isinstance(level, str) else level.get("effort")
        for level in levels
      }
      for effort in ("ultra", "max", "xhigh", "high", "medium", "low"):
        if effort in values:
          return effort
    raise ValueError("model or supported reasoning levels absent")
  except (ValueError, TypeError, subprocess.TimeoutExpired) as error:
    print(f"Catalogue unavailable ({error}); using documented xhigh.")
    print("Confirm model access and Max/Ultra in /model after signing in.")
    return "xhigh"


def validate(config, effort, auto):
  """Ask the local CLI to parse a temporary candidate, without inference."""
  with tempfile.TemporaryDirectory(prefix="codex-config-check-") as tmp:
    stage = Path(tmp)
    shutil.copytree(ROOT / "agents", stage / "agents")
    env = dict(os.environ, CODEX_HOME=str(stage))
    attempts = [effort]
    if auto and effort in ("ultra", "max"):
      attempts = list(dict.fromkeys([effort, "max", "xhigh"]))
    for attempt in attempts:
      config["model_reasoning_effort"] = attempt
      config["plan_mode_reasoning_effort"] = attempt
      (stage / "config.toml").write_text(tomlkit.dumps(config))
      result = run(["codex", "features", "list"], env=env)
      if result.returncode == 0:
        for flag in ("memories", "multi_agent", "remote_plugin"):
          if not re.search(rf"(?m)^\s*{flag}\s", result.stdout):
            raise ValueError(f"CLI lacks {flag}; update Codex first.")
        if attempt != effort:
          print(f"CLI rejected {effort}; candidate uses {attempt}.")
        return attempt
      diagnostic = result.stderr.strip() or result.stdout.strip()
    raise ValueError(f"Codex rejected candidate configuration:\n{diagnostic}")


def write_atomic(path, content, mode=0o600):
  path.parent.mkdir(parents=True, exist_ok=True)
  descriptor, temporary = tempfile.mkstemp(prefix=".codex-", dir=path.parent)
  try:
    with os.fdopen(descriptor, "w") as stream:
      stream.write(content)
    os.chmod(temporary, mode)
    os.replace(temporary, path)
  finally:
    Path(temporary).unlink(missing_ok=True)


def apply_files(files, home):
  """Snapshot every original before mutation; roll back a failed write batch."""
  stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
  backup = home / "setup-backups" / stamp
  backup.mkdir(parents=True, mode=0o700)
  manifest = []
  for index, (path, content) in enumerate(files.items()):
    if path.is_symlink():
      raise ValueError(f"Refusing to replace symlink: {path}")
    exists = path.exists()
    entry = {"path": str(path), "existed": exists, "copy": str(index)}
    if exists:
      shutil.copy2(path, backup / str(index))
    manifest.append(entry)
  (backup / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
  written = []
  try:
    for entry, (path, content) in zip(manifest, files.items()):
      mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
      write_atomic(path, content, mode)
      written.append(entry)
  except BaseException:
    for entry in reversed(written):
      path = Path(entry["path"])
      if entry["existed"]:
        shutil.copy2(backup / entry["copy"], path)
      else:
        path.unlink(missing_ok=True)
    raise
  print(f"Applied {len(files)} files. Original files: {backup}")
  print("manifest.json maps numbered backup files to original paths.")


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--apply", action="store_true")
  parser.add_argument("--model", default="gpt-6-astra")
  parser.add_argument("--effort", default="auto", choices=[
    "auto", "low", "medium", "high", "xhigh", "max", "ultra"
  ])
  parser.add_argument("--experimental-context", action="store_true")
  parser.add_argument("--zsh-file", type=Path)
  parser.add_argument("--output", type=Path, default=Path("codex-preview"))
  args = parser.parse_args()
  os.umask(0o077)
  home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).absolute()
  zroot = Path(os.environ.get("ZDOTDIR", Path.home()))
  zfile = (args.zsh_file or zroot / ".zshrc").expanduser().absolute()
  output = args.output.expanduser().absolute()
  config_path = home / "config.toml"
  existing = read(config_path)
  config = tomlkit.parse(existing)
  if config.get("model_provider", "openai") != "openai":
    raise ValueError("Existing custom model_provider requires manual migration.")
  if config.get("profile"):
    raise ValueError("Existing default profile may override this setup.")
  desired = tomlkit.parse((ROOT / "config.toml").read_text())
  desired["model"] = args.model
  if args.experimental_context:
    desired["features"]["context_management"] = {
      "experimental_mode": True
    }
  merge(config, desired)
  # Remove explicitly conflicting legacy agent defaults under our ownership.
  for key in ("max_threads", "default_subagent_model",
              "default_subagent_reasoning_effort"):
    config["agents"].pop(key, None)
  effort = args.effort
  if effort == "auto":
    effort = advertised_effort(args.model)
  effort = validate(config, effort, args.effort == "auto")
  completion = run(["codex", "completion", "zsh"])
  if completion.returncode or not completion.stdout.strip():
    raise ValueError("Could not generate Zsh completion with installed Codex.")
  with tempfile.TemporaryDirectory(prefix="codex-zsh-check-") as tmp:
    fragment = Path(tmp) / "completion.zsh"
    fragment.write_text(completion.stdout)
    if run(["zsh", "-n", str(fragment)], timeout=10).returncode:
      raise ValueError("Generated Zsh completion has invalid syntax.")
  loader = '''# Load late, after Zinit/your normal completion initialization.
if [[ -o interactive ]]; then
  typeset -U path
  path=("$HOME/.local/bin" $path)
  if (( ! $+functions[compdef] )); then
    autoload -Uz compinit
    compinit
  fi
  if [[ -r "${CODEX_HOME:-$HOME/.codex}/completion.zsh" ]]; then
    source "${CODEX_HOME:-$HOME/.codex}/completion.zsh"
  fi
fi'''
  global_path = home / "AGENTS.md"
  files = {
    config_path: tomlkit.dumps(config),
    global_path: marked(read(global_path),
                        (ROOT / "personal-instructions.md").read_text()),
    home / "completion.zsh": completion.stdout,
    zfile: marked(read(zfile), loader),
  }
  for agent in sorted((ROOT / "agents").glob("*.toml")):
    target = home / "agents" / agent.name
    text = agent.read_text()
    if target.exists() and read(target) != text:
      raise ValueError(f"Agent exists with different text: {target}")
    files[target] = text
  # Never let preview output overwrite a real configuration or package source.
  if output == home or output == ROOT or output in home.parents:
    raise ValueError("Choose a separate preview directory.")
  if output.exists():
    raise ValueError(f"Preview directory already exists: {output}")
  output.mkdir(parents=True)
  for index, (path, content) in enumerate(files.items()):
    (output / f"{index:02d}-{path.name}").write_text(content)
  (output / "destinations.json").write_text(
    json.dumps([str(path) for path in files], indent=2) + "\n"
  )
  print(f"Model: {args.model}; reasoning: {effort}; subagents: up to 4.")
  print(f"Reviewable candidate files: {output}")
  print("Parser validation passed; account/model and MCP access are not tested.")
  if args.apply:
    apply_files(files, home)
    print("Start a fresh interactive Zsh, then codex login and codex.")
    print("Check /model, /status, /mcp, /memories, and /plugins.")
  else:
    print("Preview only. Rerun with --apply and a NEW --output directory.")


if __name__ == "__main__":
  try:
    main()
  except (ValueError, OSError, subprocess.TimeoutExpired) as error:
    raise SystemExit(f"ERROR: {error}") from error
