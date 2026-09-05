# Validation performed while preparing the lab

- All five behavioural test groups passed against the supplied examples.
- An intentionally incorrect greeting was caught by the behavioural suite.
- Unified diff reported the injected change.
- Baseline restoration restored the original file bytes.
- A before-restore snapshot retained the intentionally modified candidate.
- File-selection cap and out-of-scope change detection were exercised.
- Repeated preparation and an invalid snapshot path were rejected.
- Python source compiled successfully.

These checks ran in temporary copies; the supplied lab remains unprepared.
VS Code/Codex interaction was not run here. shfmt, ShellCheck and Ruff were not
available here, so formatter/linter execution remains part of the local job.
This is a functional experiment, not a tested security sandbox.
