# Job 3: justified simplification

Inspect selected scripts for unnecessary duplication or complexity. First
present at most two concrete alternatives, with tradeoffs and affected paths.
Include "leave unchanged" when abstraction would cost more than it saves.
Do not change code until the user chooses an alternative. Keep changes inside
existing selected files: cross-file helpers, merging files, switching language,
and removing files are beyond experiment 1. Report such ideas for a later run.
Preserve tested behaviour, stderr/stdout separation and exit statuses.
After an approved edit, run python3 lab.py check and present the resulting diff.
A well-justified no-change conclusion counts as a successful job.
