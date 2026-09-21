"""Wrapper for rsmetacheck CLI to integrate with rsmetacheck-bot."""

import sys
from pathlib import Path

import click
from rsmetacheck import cli as rsmetacheck_cli


def _default_non_failing_rsmetacheck_config() -> Path:
    """Return the packaged rsmetacheck config that disables CI exit-on-findings."""
    return Path(__file__).resolve().parent / "config" / "rsmetacheck_non_failing.toml"


def run_rsmetacheck(
    *,
    input_source: str,
    skip_somef: bool = False,
    somef_output: str = "somef_outputs",
    pitfalls_output: str = "pitfalls_outputs",
    analysis_output: str = "analysis_results.json",
    threshold: float = 0.8,
    generate_codemeta: bool = False,
    config_file: str | None = None,
    config_profile: str | None = None,
) -> None:
    """Run rsmetacheck CLI by constructing and forwarding argv."""
    argv = ["rsmetacheck"]
    config_path = _default_non_failing_rsmetacheck_config()

    argv.extend(["--input", input_source.strip()])
    argv.extend(["--somef-output", somef_output])
    argv.extend(["--pitfalls-output", pitfalls_output])
    argv.extend(["--analysis-output", analysis_output])
    argv.extend(["--threshold", str(threshold)])

    argv.extend(["--config", str(config_path)])
    if config_profile:
        argv.extend(["--config-profile", config_profile])

    if skip_somef:
        argv.append("--skip-somef")
    if generate_codemeta:
        argv.append("--generate-codemeta")

    # jsonld output also includes non-detected checks when verbose is enabled.
    argv.append("--verbose")

    original_argv = sys.argv
    try:
        sys.argv = argv
        click.echo(f"[rsmetacheck] running: {' '.join(argv)}")
        rsmetacheck_cli()
    except SystemExit as exc:
        # Print a helpful message when rsmetacheck exits with a non-zero code
        if exc.code not in {0, None}:
            click.echo(
                f"[rsmetacheck] exited with code {exc.code} for input {input_source}",
                err=True,
            )
            return
        raise
    except Exception as exc:  # pragma: no cover - defensive
        click.echo(f"[rsmetacheck] unexpected error: {exc}", err=True)
        raise
    finally:
        sys.argv = original_argv
