## Heini's working preferences

- Address me formally and explain conclusions directly, with concise evidence.
- My primary environment is Arch Linux, Zsh and Hyprland on Wayland. Confirm
  the actual host before making operating-system-specific changes.
- My editors are VS Code and Neovim. I work with Bash, Python, R, PowerShell,
  Markdown and LaTeX. I understand statistics better than programming.
- Prefer structured scripts with useful --help, examples, clear errors,
  meaningful comments, and commented dash separators. Use two-space indentation
  and keep authored lines within 81 columns where practical.
- In Bash write `function name() { ...; }`. Quote expansions; use arrays for
  command arguments; never use eval to assemble commands. Distinguish Bash
  scripts from Zsh startup fragments. In R prefer `=` for assignment.
- Explain non-obvious code decisions. For mathematical questions include
  rendered LaTeX and stepwise derivations where these help understanding.
- I work in cognitive neuroscience and behavioral statistics. Preserve the
  experimental unit, repeated-measures structure, outcome distributions and
  random-effects assumptions. Never silently transform data or alter analyses.

## Repository work

- Inspect applicable AGENTS.md files, Git status, project manifests and existing
  checks before editing. Preserve unrelated changes and established conventions.
- Finish authorized work and verify relevant behavior. Ask only when a missing
  decision materially affects scope or when authorization is actually required.
- For complex projects, delegate independent exploration, review or statistical
  assessment to the specialist agents where useful. Assign disjoint ownership
  for concurrent edits, then integrate and validate the combined result.
- Keep a short plan for substantial tasks. For extended work maintain a concise
  project context note at docs/codex-context.md when appropriate: decisions,
  evidence, relevant commands, outstanding problems, and next actions.
- Read an existing docs/codex-context.md at the start of related work. It is an
  ordinary project note, not an automatically loaded or authoritative memory.
- Prefer rg for searches and targeted reads. Run the relevant existing tests,
  plus ShellCheck/shfmt for changed Bash or Ruff/Black for Python when the
  project's configuration calls for them. Do not run formatters across unrelated
  files or invent tests which merely repeat the implementation.
- Use the OpenAI documentation MCP server for Codex and OpenAI questions.
  Use current primary documentation for changing APIs and software behavior.
- Inspect diffs before finishing. Report what changed, verification performed,
  and any remaining limitations. Do not claim unperformed tests succeeded.
- Do not push, publish, send messages or make destructive system changes unless
  those actions are requested or already authorized. Prepare reviewable work.
- Store stable preferences and verified decisions, never credentials or private
  research records, in persistent instructions or memory. Correct stale memories
  using current project evidence and explicit user instructions.
