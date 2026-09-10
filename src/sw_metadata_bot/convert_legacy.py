"""Compatibility CLI wrapper for the legacy snapshot converter."""

from __future__ import annotations

from pathlib import Path

import click

from conversion.convert_legacy_outputs import convert_legacy_output_tree


@click.command(name="convert-legacy")
@click.argument("snapshot_root", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--target-root",
    type=click.Path(path_type=Path),
    default=None,
    help="Destination root for the converted repo-centric layout.",
)
def convert_legacy_command(snapshot_root: Path, target_root: Path | None) -> None:
    """Convert a legacy snapshot tree into the repo-centric layout without publishing."""
    convert_legacy_output_tree(snapshot_root, target_root=target_root)


if __name__ == "__main__":
    convert_legacy_command()
