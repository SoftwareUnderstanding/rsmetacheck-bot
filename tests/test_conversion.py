import json

from click.testing import CliRunner

from conversion.convert_legacy_outputs import convert_legacy_output_tree
from sw_metadata_bot.main import cli
from sw_metadata_bot.pipeline import run_analysis_command
from sw_metadata_bot.publish import publish_command, simulate_publish_command


def test_convert_legacy_output_tree_creates_repo_state_layout(tmp_path):
    legacy_snapshot = tmp_path / "outputs" / "batch-a" / "202603"
    repo_dir = legacy_snapshot / "github_com_example_repo"
    repo_dir.mkdir(parents=True)

    (repo_dir / "pitfall.jsonld").write_text('{"@type": "Pitfall"}', encoding="utf-8")
    (repo_dir / "somef_output.json").write_text(
        '{"somef_provenance": "legacy"}', encoding="utf-8"
    )
    (repo_dir / "report.json").write_text(
        json.dumps(
            {
                "records": [
                    {
                        "repo_url": "https://github.com/example/repo",
                        "action": "simulated_created",
                        "current_commit_id": "abc123",
                        "codemeta_status": "present",
                        "file": "202603/github_com_example_repo/pitfall.jsonld",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (legacy_snapshot / "run_report.json").write_text(
        json.dumps({"records": [], "run_metadata": {}}),
        encoding="utf-8",
    )

    converted = convert_legacy_output_tree(
        legacy_snapshot, target_root=tmp_path / "outputs" / "batch-a"
    )

    assert converted == [legacy_snapshot]

    converted_repo = tmp_path / "outputs" / "batch-a" / "github_com_example_repo"
    assert converted_repo.exists()
    assert (converted_repo / "pitfall.jsonld").exists()
    assert (converted_repo / "somef_output.json").exists()
    assert (converted_repo / "report.json").exists()
    assert (converted_repo / "current-state.json").exists()
    assert (converted_repo / "event-log.jsonl").exists()
    assert not any(
        path.name.startswith("example_invalid_")
        for path in (tmp_path / "outputs" / "batch-a").iterdir()
    )
    assert (tmp_path / "outputs" / "batch-a" / "run_report.json").exists()


def test_convert_legacy_snapshot_and_simulate_publish_work_together(tmp_path):
    """Scenario 1: old snapshot conversion should remain usable by the modern CLI flow."""
    legacy_root = tmp_path / "legacy" / "202603"
    repo_dir = legacy_root / "github_com_example_repo"
    repo_dir.mkdir(parents=True)

    (repo_dir / "pitfall.jsonld").write_text('{"@type": "Pitfall"}', encoding="utf-8")
    (repo_dir / "somef_output.json").write_text(
        '{"somef_provenance": "legacy"}', encoding="utf-8"
    )
    (repo_dir / "report.json").write_text(
        json.dumps(
            {
                "records": [
                    {
                        "repo_url": "https://github.com/example/repo",
                        "action": "simulated_created",
                        "current_commit_id": "abc123",
                        "codemeta_status": "present",
                        "file": "202603/github_com_example_repo/pitfall.jsonld",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (legacy_root / "run_report.json").write_text(
        json.dumps({"records": [], "run_metadata": {}}), encoding="utf-8"
    )

    target_root = tmp_path / "converted"
    convert_legacy_output_tree(legacy_root, target_root=target_root)

    runner = CliRunner()
    result = runner.invoke(
        simulate_publish_command,
        ["--analysis-root", str(target_root)],
    )

    assert result.exit_code == 0, result.output
    assert (target_root / "run_report.json").exists()


def test_run_analysis_cli_creates_fresh_dry_run_outputs_without_publishing(tmp_path):
    """Scenario 3: fresh analysis works from scratch and stays dry-run only."""
    config_path = tmp_path / "config.json"
    output_root = tmp_path / "outputs"
    config_path.write_text(
        json.dumps(
            {
                "analysis": {"repositories": ["https://github.com/example/repo"]},
                "issues": {"custom_issue_message": None, "opt_outs": []},
                "outputs": {
                    "output_root_dir": str(output_root),
                    "run_name": "batch-a",
                    "snapshot_tag_format": "%Y%m%d",
                },
            }
        ),
        encoding="utf-8",
    )

    runner = CliRunner()
    result = runner.invoke(
        run_analysis_command,
        ["--config-file", str(config_path), "--snapshot-tag", "202603"],
    )

    assert result.exit_code == 0, result.output
    assert (output_root / "batch-a" / "202603" / "run_report.json").exists()


def test_convert_legacy_cli_is_registered_and_usable(tmp_path):
    """Compatibility: the legacy converter is exposed through the CLI group."""
    legacy_root = tmp_path / "legacy"
    legacy_root.mkdir()
    target_root = tmp_path / "converted"

    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["convert-legacy", str(legacy_root), "--target-root", str(target_root)],
    )

    assert result.exit_code == 0, result.output
    assert target_root.exists()


def test_publish_command_rejects_legacy_snapshot_dir(tmp_path):
    """Legacy snapshot roots must be migrated before publish can run."""
    legacy_root = tmp_path / "legacy" / "202603"
    repo_dir = legacy_root / "github_com_example_repo"
    repo_dir.mkdir(parents=True)
    (repo_dir / "pitfall.jsonld").write_text('{"@type": "Pitfall"}', encoding="utf-8")
    (legacy_root / "run_report.json").write_text(
        json.dumps({"records": [], "run_metadata": {}}), encoding="utf-8"
    )

    runner = CliRunner()
    result = runner.invoke(publish_command, ["--analysis-root", str(legacy_root)])

    assert result.exit_code != 0
    assert "convert-legacy" in result.output
    assert "Legacy snapshot layout detected" in result.output
