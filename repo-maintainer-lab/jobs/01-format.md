# Job 1: deterministic formatting

Format selected Bash scripts with shfmt -i 2 -ci -bn -w and selected Python
scripts with ruff format. Pass explicit paths, never the whole project.
Use the root pyproject.toml for Ruff's two-space indentation and 81-column
line-length target. Do not run Ruff's automatic fixes in this job.
Run ShellCheck on selected Bash files and Ruff check on selected Python files.
Report findings without unrelated behavioural changes.
Run python3 lab.py check. Stop and show the diff for review.
If a required tool is missing, report it and stop this job; do not install it.
