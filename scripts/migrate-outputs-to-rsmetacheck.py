#!/usr/bin/env python3
"""Migration utility to normalize legacy bot-version keys in output JSON files.

Usage:
  scripts/migrate-outputs-to-rsmetacheck.py --root outputs/example_run --dry-run
  scripts/migrate-outputs-to-rsmetacheck.py --root outputs/example_run --apply

The script looks for `run_report.json` files and per-repo `report.json` files and,
if a record contains a legacy bot-version key but not the canonical
`rsmetacheck_bot_version`, it will add the canonical key with the legacy value.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rsmetacheck_bot import reporting, constants


def migrate_payload(path: Path, apply: bool) -> int:
    changed = 0
    with open(path, encoding="utf-8") as fh:
        payload = json.load(fh)

    records = payload.get("records", [])
    for rec in records:
        if not isinstance(rec, dict):
            continue
        # If canonical key missing but legacy present, set canonical key
        canonical = rec.get(constants.VERSION_FIELD_BOT)
        if canonical:
            continue
        val = reporting.extract_bot_version(rec)
        if val:
            print(f"Would set {constants.VERSION_FIELD_BOT}={val} in {path}")
            changed += 1
            if apply:
                rec[constants.VERSION_FIELD_BOT] = val
    if apply and changed:
        backup = path.with_suffix(path.suffix + ".bak")
        path.replace(backup)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"Applied migration and created backup: {backup}")
    return changed


def find_and_migrate(root: Path, apply: bool) -> int:
    total = 0
    for run_report in root.rglob("run_report.json"):
        total += migrate_payload(run_report, apply)
    # also look for per-repo report.json files
    for report in root.rglob("**/report.json"):
        total += migrate_payload(report, apply)
    return total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", required=True, help="Root outputs directory or snapshot"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Apply changes (default: dry-run)"
    )
    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"Path not found: {root}")
        raise SystemExit(2)

    changed = find_and_migrate(root, args.apply)
    print(f"Total records to change: {changed}")


if __name__ == "__main__":
    main()
