Output storage conventions
=========================

This project stores analysis data in a repo-centric layout instead of a date-centric
snapshot layout. The goal is to keep repository state easy to inspect, easy to
monitor over time, and safe to reuse across repeated runs.

Repository-centric layout
-------------------------

Each repository gets a stable folder under the configured output root. The folder
contains the current state, event history, archived analysis payloads, and any
issue metadata for that repository.

Typical layout::

   outputs/
   └── batch-a/
       ├── run_report.json
       ├── config.json
       └── github_com_example_repo/
           ├── current-state.json
           ├── event-log.jsonl
           ├── somef_output.json
           ├── pitfall.jsonld
           ├── report.json
           ├── issue_report.md
           ├── analyses/
           │   └── <commit_or_timestamp>_analysis.json
           └── issues/
               └── issue_123.json

Important rules
---------------

- The repository directory is the primary unit of storage.
- The run directory remains useful for grouping runs and keeping snapshot metadata.
- Snapshot tags such as ``202603`` are still used for reproducibility and run
  identity, but they should not force a date-centric repository layout.
- Repeated weekly or periodic analyses should append or update the repository
  state in place rather than creating a new repo tree per date.

Legacy snapshot detection
-------------------------

Legacy output trees are still accepted only through an explicit migration step.
Modern commands must reject a legacy snapshot directory and tell the user to run
``convert-legacy`` first.

This protects the project from accidentally running new analysis logic on output
structures that are no longer the canonical format.

The rule is:

- if the input path still looks like a dated snapshot tree, stop and suggest
  conversion;
- if the path already contains repo-centric files such as ``current-state.json``
  or ``event-log.jsonl``, continue normally.

Conversion workflow
------------------

The conversion command accepts one concrete legacy snapshot directory and
migrates its repository entries into the repo-centric layout.

Example::

   uv run sw-metadata-bot convert-legacy outputs/legacy_batch/202603 --target-root outputs/converted

Do not pass a parent folder that contains multiple dated snapshots. The command
expects a single snapshot root.

The converted repository folders keep the repository identity and add the
repo-centric metadata files. The original run report is mirrored to the target
root when present.

Flattened vs nested layout
-------------------------

The config option ``flatten_repo_layout`` controls whether repo directories are
stored directly under the run root or nested under the snapshot directory.

- ``False``: keep repo directories under the snapshot directory;
- ``True``: flatten repo directories under the run root while still retaining run
  metadata and snapshot identity.

This option is a convenience for organizational preferences; it does not change
how the project interprets repository state.

Operational conventions
----------------------

- ``run-analysis`` creates or updates analysis data without publishing live
  issues.
- ``publish`` consumes the recorded decisions and creates or updates issues.
- ``fetch`` checks existing issue status and updates repository state.
- ``query-history`` reads the repository event log for debugging and monitoring.
- ``report-summary`` reads the run report for dashboard-style summaries.

These commands must all operate on repo-centric paths, not on legacy date-based
snapshot trees.

Why this design
---------------

The repo-centric model makes it easier to:

- follow the current state of a repository,
- inspect its event history,
- monitor repeated analyses over time,
- keep archive payloads close to each repository,
- compare run-level metadata without losing repository-level continuity.

The run-level snapshot metadata remains important for reproducibility, but it is
stored as metadata surrounding the repo-centric state rather than as the primary
organization of the data itself.
