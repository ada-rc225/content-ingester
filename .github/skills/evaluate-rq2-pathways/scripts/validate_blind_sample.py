#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from rq2_eval_common import (
    BUNDLE_FILES,
    PROTOCOL_ID,
    EvaluationError,
    has_condition_component,
    load_json,
    sha256,
)

CONDITION_RE = re.compile(r"\bP[012]\b", re.IGNORECASE)
FORBIDDEN_KEYS = {"condition", "selection_authority", "generated_by", "producer"}


def find_leaks(value: Any, location: str = "$") -> list[str]:
    leaks: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_KEYS:
                leaks.append(f"{location}.{key}: forbidden key")
            leaks.extend(find_leaks(item, f"{location}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            leaks.extend(find_leaks(item, f"{location}[{index}]"))
    elif isinstance(value, str) and CONDITION_RE.search(value):
        leaks.append(f"{location}: condition token")
    return leaks


def validate(bundle: Path) -> list[str]:
    errors: list[str] = []
    if not bundle.is_dir():
        return [f"bundle directory does not exist: {bundle}"]
    if has_condition_component(bundle):
        errors.append("bundle path reveals P0/P1/P2")
    for name in BUNDLE_FILES:
        if not (bundle / name).is_file():
            errors.append(f"missing bundle file: {name}")
    if errors:
        return errors

    manifest = load_json(bundle / "evaluation-manifest.json")
    if manifest.get("protocol_id") != PROTOCOL_ID:
        errors.append("unexpected protocol_id")
    policy = manifest.get("independence_policy", {})
    if policy.get("condition_hidden") is not True or policy.get("single_sample_pointwise_evaluation") is not True:
        errors.append("blind independence policy is incomplete")
    records = manifest.get("files")
    if not isinstance(records, dict):
        errors.append("manifest files must be an object")
        records = {}
    for name in BUNDLE_FILES:
        if name == "evaluation-manifest.json":
            continue
        record = records.get(name, {})
        if record.get("sha256") != sha256(bundle / name):
            errors.append(f"stale or missing hash for {name}")

    contract = load_json(bundle / "frozen-reference-contract.json")
    if contract.get("lifecycle_status") != "frozen":
        errors.append("Frozen Reference Contract lifecycle_status is not frozen")
    authority_checks = manifest.get("authority_checks", {})
    if authority_checks.get("frozen_contract_release_verified") is not True:
        errors.append("blind manifest does not attest a verified Contract release")
    pathway = load_json(bundle / "pathway-evidence.json")
    selected = pathway.get("selected_item_ids")
    excluded = pathway.get("excluded_item_ids")
    contract_ids = {
        item.get("item_id") for item in contract.get("contract_items", [])
        if isinstance(item, dict)
    }
    if not isinstance(selected, list) or not selected:
        errors.append("selected_item_ids must be a non-empty array")
        selected = []
    if not isinstance(excluded, list):
        errors.append("excluded_item_ids must be an array")
        excluded = []
    if set(selected) & set(excluded):
        errors.append("selected and excluded items overlap")
    if set(selected) | set(excluded) != contract_ids:
        errors.append("selected/excluded items do not partition the Frozen Contract")
    sequence = pathway.get("instruction_sequence")
    units = pathway.get("learning_units")
    unit_ids = {unit.get("unit_id") for unit in units or [] if isinstance(unit, dict)}
    if not isinstance(sequence, list) or set(sequence) != unit_ids or len(sequence) != len(unit_ids):
        errors.append("instruction sequence does not cover each sanitized unit exactly once")

    structural = load_json(bundle / "structural-validation-evidence.json")
    if structural.get("pathway_valid") is not True or structural.get("lesson_output_valid") is not True:
        errors.append("structural evidence is not valid")
    profile = load_json(bundle / "learner-profile.json")
    request = load_json(bundle / "learning-request.json")
    if not isinstance(profile.get("profile_id"), str):
        errors.append("learner profile has no profile_id")
    if not isinstance(request.get("target_capabilities"), list) or not request["target_capabilities"]:
        errors.append("learning request has no target capabilities")

    for name in ("evaluation-manifest.json", "learner-profile.json", "learning-request.json", "pathway-evidence.json", "structural-validation-evidence.json"):
        value = load_json(bundle / name)
        errors.extend(f"{name}: {leak}" for leak in find_leaks(value))
    lesson = (bundle / "lesson.md").read_text(encoding="utf-8")
    if CONDITION_RE.search(lesson):
        errors.append("lesson.md contains an explicit P0/P1/P2 token")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one blind RQ2 evaluation sample.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    bundle = Path(args.bundle).resolve()
    try:
        errors = validate(bundle)
    except (EvaluationError, OSError, ValueError, json.JSONDecodeError) as exc:
        errors = [str(exc)]
    report = {
        "schema_version": "1.0",
        "validator": "validate-rq2-blind-sample-v1",
        "bundle": str(bundle),
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
    }
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        print(f"FAIL: invalid blind RQ2 sample ({len(errors)} errors)")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: valid blind RQ2 sample")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
