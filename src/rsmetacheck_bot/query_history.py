"""CLI command to query per-repository event history (event-log.jsonl)."""

from __future__ import annotations

import json
from pathlib import Path

import click

from . import repo_state


@click.command()
@click.argument("output_root", type=click.Path(exists=True, path_type=Path))
@click.argument("repo_url", type=str)
@click.option("--event", "event_filter", help="Filter by event type", default=None)
def query_history_command(output_root: Path, repo_url: str, event_filter: str | None):
    """Print repository event-log entries for a given `repo_url`.

    `output_root` should be the configured outputs root (or run root when
    applicable). The command resolves the repo paths via `repo_state` and
    streams `event-log.jsonl` lines as JSON.
    """
    repo_paths = repo_state.resolve_repo_state_paths(output_root, repo_url)
    event_log = repo_paths["repo_folder"] / "event-log.jsonl"
    if not event_log.exists():
        # Nothing to show; exit quietly with no output
        return

    with open(event_log, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if event_filter and obj.get("event") != event_filter:
                continue
            click.echo(json.dumps(obj, ensure_ascii=False))
