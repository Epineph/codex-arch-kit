# Start the VS Code / Codex experiment

This is a prepared first experiment, not the complete repo-maintainer proposed
in the conversation. The agent runs interactively in your own VS Code session.
No agent has already modified these examples.

## 1. Prepare

Extract the ZIP into a new directory outside your existing repositories.
From the extracted repo-maintainer-lab directory, run:

```bash
python3 lab.py doctor
python3 lab.py prepare --max-files 5 --jobs '1-3'
python3 lab.py check
code .
```

Python 3.10+ and Bash are required. Git is optional for this lab. The controller
uses only Python's standard library. For the formatting job install shfmt,
ShellCheck and Ruff using your usual trusted package manager if absent.
On Arch, the packages used by your setup script are shfmt, shellcheck and
python-ruff. No package installation is performed by this lab.

Open the Codex extension and sign in. Its sidebar is the interface for this
experiment; the separate codex CLI is not required. If you cannot find the
extension, check which VS Code distribution you have: a command named code does
not itself establish which extension marketplace is available.

Your setup-vs-config repository is not modified or executed. Workspace settings
here disable automatic saving, formatting and fix actions during the experiment.
They select Ruff for Python when you explicitly request formatting. These
settings do not rewrite your global editor configuration.

## 2. Paste this into Codex

```text
Read AGENTS.md, START-HERE.md and .runs/plan.json.
We are performing experiment 1 on only the listed candidate files.
Read the selected numbered job files. Show the target list, job order,
required tools and expected checks. Do not edit anything yet.
After I approve the plan, perform only the first selected job. Before edits,
run python3 lab.py checkpoint before-job-1. Run the requested validation,
show the diff, and stop for my review. Do not commit, push, install tools,
or change files outside the selected candidate paths.
```

After you approve job 1, inspect its changes with:

```bash
python3 lab.py diff
python3 lab.py check
python3 lab.py checkpoint accepted-job-1
```

Tell Codex to continue with job 2 and stop again after validation. Job 3 must
present alternatives before changing anything. Selected jobs can be omitted:
for example, prepare --jobs '1,3' selects just formatting and simplification.
The prompts are instructions; your Codex permissions and normal human review
remain the access controls. The controller does not force the agent to pause.

## 3. Restore a version

```bash
python3 lab.py snapshots
python3 lab.py restore baseline --files greet.sh
```

Or replace baseline with an exact printed snapshot ID. Restore asks for
confirmation and first saves the current candidate in a before-restore snapshot.
Use --yes only when you intentionally want to skip that confirmation.
Each snapshot preserves all five example files and recorded permissions.
Backups remain until you deliberately remove the lab. No cleanup is automatic.
Restoration is atomic per file, not a transaction spanning all five files.

## 4. What this experiment establishes

- Explicit file selection, extension filtering and a cap.
- Selection of numbered jobs using commas, spaces or ranges.
- Baseline copies, diffs, timestamped snapshots and per-file restoration.
- Candidate-file scope checks, syntax checks and behavioural checks.
- Interactive plan approval and review through VS Code / Codex.

For example, in a freshly extracted copy:

```bash
python3 lab.py prepare --extensions sh --max-files 2 --jobs '1,3'
```

All five fixtures remain available as context, but only the selected files may
change. Sorting is by filename before applying the cap. The three jobs have no
mandatory dependencies; numeric order is the chosen order in this experiment.

The fixture programs are deliberately small, disposable examples. check executes
them unless --static-only is supplied; it is not a secure execution sandbox.
Do not replace them with real system-management scripts and run check blindly.
Scope validation covers candidate files, not all filesystem writes. Baseline
hashes detect accidental changes; an agent with broad write access could alter
both state and evidence, so this is not tamper-proof enforcement.

This version has no automated agent runner, wall-clock limit, scheduling, remote
execution, application to another repository, commit/push commands or automated
approval gate. It tests the human-in-the-loop workflow before those features.
A VS Code conversation's suggested time budget would not be a hard timeout.

The tests cover useful observed contracts, not mathematical proof of equivalence.
Save all edited buffers before checking: checks operate on files on disk.
Missing formatters must be reported separately; lab.py check does not run them.
Width checking counts Unicode code points, not rendered terminal display cells.

## Sources and the inspected setup

- https://github.com/Epineph/setup-vs-config/blob/main/setup-vs-bin.sh
- https://learn.chatgpt.com/docs/codex/ide
- https://code.visualstudio.com/docs/configure/settings
- https://docs.astral.sh/ruff/formatter/

The setup script already includes ShellCheck, shfmt, Ruff and Python extensions.
It chooses Black as the Python formatter, enables format-on-save and generic
save-time fixes, and does not list the Codex extension. It overwrites user
settings/keybindings when executed; rerunning it is unnecessary for this lab.
