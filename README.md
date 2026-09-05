# Codex CLI for Arch Linux — Heini's setup

Prepared 5 September 2026. This is a separate CLI setup inspired by
setup-vs-bin.sh. The attached editor script installs language extensions but
contains no Codex installation or configuration. VS Code and the Codex CLI can
share the same local Codex configuration.

## What is included

| File | Purpose |
| --- | --- |
| setup-codex-arch.sh | Arch package and CLI installation; configuration launcher |
| configure.py | Comment-preserving TOML merge, preview, validation and backups |
| config.toml | Complete personal baseline, suitable for a fresh Codex home |
| personal-instructions.md | Editable preferences merged into global AGENTS.md |
| agents/*.toml | Four standalone custom agent definitions |

The installed model is GPT-6 Astra by default. It is OpenAI's strongest current
recommendation for complex work. Availability depends on your account and
rollout; a config file cannot grant access. If Astra is absent in `/model`, use
`--model gpt-5.6-sol` when rerunning the setup. Do not use an obsolete model name
just because an older configuration guide recommends it.
[Model guidance](https://learn.chatgpt.com/docs/models)

## Installation

Clone the repository with its companion repositories:

```bash
git clone --recurse-submodules https://github.com/Epineph/codex-arch-kit.git
cd codex-arch-kit
```

For an existing clone, populate the companions at their recorded commits with
`git submodule update --init --recursive`. The companions are
`codex-session-capture` and `repo-maintainer-lab`.

Run everything as your ordinary user. The installer invokes sudo only for Arch
packages.

If npm is absent, install it using your normal Arch package management:

```bash
sudo pacman -Syu --needed npm
```

Review pacman's transaction if you already use nodejs-lts or a Node version
manager. The setup does not explicitly replace an existing Node runtime.

Install the helper packages, a user-local Codex CLI, configuration and GitHub
plugin:

```bash
bash setup-codex-arch.sh \
  --apply \
  --install-packages \
  --install-cli \
  --github-plugin \
  --output ./initial-candidate
```

`--install-packages` performs a full Arch upgrade and installs Python/TOML,
Zsh, Git, gh, rg, fd, ShellCheck, shfmt, Ruff and Black. It does not install R,
PowerShell, LaTeX or their package ecosystems. Reuse your existing installations.
`--install-cli` installs `@openai/codex@latest` into a separate user prefix and
links its executable in `~/.local/bin`. Omit it when using another Codex package
manager. Repeating it updates this user-local installation. Official CLI
installation and sign-in guidance is available
[here](https://learn.chatgpt.com/docs/codex/cli).

If the prerequisites are already installed, preview first:

```bash
bash setup-codex-arch.sh --output ./preview-one
bash setup-codex-arch.sh --apply --output ./applied-one
```

Each output directory must be new. It contains the full merged candidate files
and their intended destinations. Existing unrelated TOML entries and comments
are retained. Managed keys are updated; existing custom model providers and
active default profiles require manual review. A different custom agent with
one of the supplied names causes a stop rather than an overwrite.

Backups are automatic under `$CODEX_HOME/setup-backups/<timestamp>` (normally
`~/.codex/setup-backups`). `manifest.json` maps each original path to a numbered
copy and records whether it existed. To restore one file, copy its numbered
backup to its recorded path; if it did not exist previously, remove the newly
created file only after reviewing it. File-write failures trigger rollback of
files written by that apply operation. Package/CLI/plugin installations are
separate operations and are not rolled back.

## Sign in and select maximum reasoning

Open a fresh interactive Zsh, then:

```zsh
codex login
codex
```

Use `/model` to verify your accessible model and choose **Ultra** if available
and you want maximum reasoning with automatic delegation. **Max** is the
single-task reasoning choice. These consume more usage and may take longer.
The parent can also use the supplied specialist agents when project guidance
or your prompt asks for delegation.

There is a current documentation mismatch: the model picker documents Max and
Ultra, while the generic TOML reference enumerates reasoning only through
`xhigh`. Therefore the installer reads `codex debug models`, selects the highest
advertised level it recognizes (Ultra, then Max, then Extra High), then tests
that choice using the local config parser. If catalogue discovery fails it
explicitly uses `xhigh`; if the parser rejects the automatic choice, it tries Max and then
`xhigh`. It never labels that fallback as Ultra or Max or silently switches models.
[Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)

Local verification resolved this for npm Codex CLI 0.153.4: its bundled Astra
catalogue includes `max` and `ultra`, and its parser accepts both values for
normal and Plan mode. The supplied baseline therefore uses Ultra. This is parser
and catalogue evidence, not a live inference or account-entitlement test.

After logging in, rerun to refresh the automatic choice:

```zsh
bash setup-codex-arch.sh --apply --output ./after-login
```

Alternatively request a specific value; an unsupported value causes a failure:

```zsh
bash setup-codex-arch.sh --apply --effort max --output ./max-candidate
```

The same selected effort is applied to normal and Plan mode. Use `/status` and
`/model` in a NEW chat to confirm effective settings. A resumed chat, explicit
CLI overrides, project settings or administrator requirements can affect the
active configuration. The installer does not override those policies.

## Features and agents

The baseline enables live web search, native memories, multi-agent support,
remote plugin discovery, shell snapshots and unified command execution. Four
concurrent subagents are allowed in addition to the primary agent. Custom agents
inherit the parent's model/effort rather than selecting cheaper models.

| Agent | Intended use | Filesystem mode |
| --- | --- | --- |
| repo_mapper | Locate architecture, execution paths and tests | Read-only |
| script_engineer | Implement assigned script changes | Workspace write |
| repo_reviewer | Identify concrete bugs and regressions | Read-only |
| statistics_reviewer | Assess analysis code and design assumptions | Read-only |

These are Codex agents, not separate API services. Ask, for example:

> Have repo_mapper inspect the affected execution paths and repo_reviewer check
> likely failure modes in parallel. Then implement the fix using script_engineer
> with explicit file ownership. Validate the integrated result before finishing.

Inspect active agents with `/agent`. Standalone agent TOML files belong in
`~/.codex/agents/`; repository-specific agents may use `.codex/agents/`.
[Subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)

Experimental context management is an additional opt-in for eligible clients,
models and sign-in methods:

```zsh
bash setup-codex-arch.sh --apply --experimental-context \
  --output ./context-candidate
```

It is separate from cross-session memory. Leave model context-window and
compaction limits at their native defaults; setting enormous numbers does not
increase a model's real capacity. We do not enable every experimental switch:
more tools and experimental features are not inherently better for scripting.

The baseline permits workspace writes and requests approval for escalation.
Ordinary sandboxed shell networking remains disabled; approve a needed package
fetch or use a narrowly scoped project configuration. Web search and remote MCP
are separate from shell networking. Read-only agent sandboxes govern local file
writes, not all possible external tool actions.

## Memories and persistent instructions

There are three complementary mechanisms:

1. `~/.codex/AGENTS.md`: curated personal instructions, loaded across projects.
   The supplied preferences are placed in a replaceable marked block.
2. Native Codex memories: generated from eligible local chats and used later.
   Manage chat participation with `/memories`. This setup enables generation and
   use; memory formation is not immediate or guaranteed for every conversation.
3. Repository `AGENTS.md` and `docs/codex-context.md`: project conventions and
   explicit handover notes. The latter is an ordinary file that the supplied
   instructions tell the agent to read, not a native memory ingestion format.

This package seeds relevant preferences from our conversation. It does not
export your entire browser history, synchronize browser memories, or establish
that every browser memory is available to the CLI. Avoid storing credentials or
private raw research data in instructions. Never share your entire Codex home.
[Memories](https://learn.chatgpt.com/docs/customization/memories)

## MCP: what it does and how to try it

An MCP server exposes tools to the agent. Codex is the client. A server can be a
local child process (stdio) or a remote service (HTTP); it need not be a server
you host or administer.

This setup configures OpenAI's public, read-only documentation server:

```toml
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
enabled = true
```

No API key or Docker installation is needed for this documentation service.
It searches documentation; it does not perform OpenAI API calls for you.
[Docs MCP](https://developers.openai.com/learn/docs-mcp)

Check the registration, then actual connectivity in an interactive session:

```zsh
codex mcp list
codex
```

Enter `/mcp`, then ask: “Use openaiDeveloperDocs to verify the current Codex
memory configuration and cite the documentation.” A successful `mcp list` proves
registration, not connectivity; an actual successful tool call is the check.

For another provider that supports OAuth, registration and authentication are
separate: `codex mcp login SERVER_NAME`. Do not run login for the public Docs
server. MCP configuration is shared with the Codex IDE extension on the same
host. VS Code's own Copilot MCP configuration is a different configuration.
[MCP guide](https://learn.chatgpt.com/docs/extend/mcp)

## Plugins worth considering

Use `/plugins` to browse the catalogue and authorize connections. The optional
installer flag adds `github@openai-curated-remote`; complete its authentication
inside Codex. Your GitHub authorization in this browser is not proof that the
local CLI is connected.

Start with GitHub for repositories, issues, PRs and CI. OpenAI documentation is
already covered by the MCP configuration. Consider Codex Security when you need
security-focused review, and Data Analytics when working on research data, if
those plugins are offered to your account. Browser/frontend plugins are useful
only for projects that actually need browser testing. None of these installs
are required for ordinary shell editing or local Git commands.

```zsh
codex plugin marketplace list
codex plugin list --available --json
codex plugin add github@openai-curated-remote
```

Copy other plugin identifiers from the actual catalogue rather than guessing.
Plugins bundle workflows and potentially tools, authentication and dependencies;
they are not VS Code extensions. If the curated marketplace or plugin is absent,
use `/plugins` to inspect what your account offers. Do not add arbitrary substitute
marketplaces. [Plugin CLI](https://learn.chatgpt.com/docs/developer-commands)

## Zsh completion and your loaded files

By default the installer appends a marked loader to `${ZDOTDIR:-$HOME}/.zshrc`.
To use one of your already-loaded files instead:

```zsh
bash setup-codex-arch.sh --apply \
  --zsh-file "$HOME/.config/zsh/YOUR-LOADED-FILE.zsh" \
  --output ./zsh-candidate
```

Replace the example path. The installer does not guess or rewire your custom
startup-file loader. Load this fragment after Zinit's completion initialization.
It initializes compinit only if compdef is absent, and uses a completion file
generated once by the installed CLI. Rerun setup after a Codex upgrade to refresh
that file. Repeating setup replaces its marked block instead of duplicating it.

For a small independent append command, execute this in Zsh, substituting an
existing file that your shell already sources after compinit:

```zsh
codex_zsh_file="$HOME/.config/zsh/YOUR-LOADED-FILE.zsh"
codex_completion_line='(( $+commands[codex] )) && source <(codex completion zsh)'
[[ -f "$codex_zsh_file" ]] && {
  rg -qF -- "$codex_completion_line" "$codex_zsh_file" ||
    printf '\n%s\n' "$codex_completion_line" >> "$codex_zsh_file"
}
```

This independent snippet regenerates completion each time the file is sourced;
the installer uses the cached alternative. Use one approach. Neither provides
AI-generated command suggestions: this is normal Tab completion of CLI options.
[Completion command](https://learn.chatgpt.com/docs/developer-commands#codex-completion)

Zsh automatically reads `.zprofile` for login shells and `.zshrc` for interactive
shells. `.zsh_profile` is not a standard automatic startup filename; it works only
if your existing configuration explicitly sources it.
[Zsh startup files](https://zsh.sourceforge.io/Doc/Release/Files.html)

## First repository experiment

```zsh
cd "$HOME/repos/YOUR-REPOSITORY"
git status --short
codex
```

Ask Codex to inspect project guidance and propose a limited first task. Your
global preferences are already present; create repository-specific `AGENTS.md`
only when it adds useful project facts. For example, identify the actual test
commands, formatter choices, generated files and data that must remain unchanged.
Use `/plan` for design work, then request implementation and a diff review.

Before pushing, inspect `git diff` and the executed checks. Run `codex resume`
to continue a saved session. The installer itself performs no model inference,
repository commits, pushes or changes to your VS Code settings.

## Verification performed

Tested locally with the official npm Codex CLI 0.153.4 and tomlkit 0.15.1:

- Real catalogue selection of Astra Ultra; normal/Plan configuration parsing.
- Preview does not change target files.
- Existing unrelated MCP configuration, comments and guidance survive merging.
- Repeated apply produces identical managed contents without duplicate loaders.
- Original configuration is recoverable from the backup manifest.
- A simulated write failure restores earlier files in the apply operation.
- All supplied TOML parses, Bash syntax passes, and real generated completions
  load successfully in a clean interactive Zsh with compdef and _codex present.

The Arch pacman transaction, the GitHub authorization flow, account model
entitlements, live model inference and an actual documentation MCP query were
not executed on your machine. ShellCheck was not available for local validation.
