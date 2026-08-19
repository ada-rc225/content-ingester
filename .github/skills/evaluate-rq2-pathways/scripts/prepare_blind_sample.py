#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from rq2_eval_common import (
    BUNDLE_FILES,
    PROTOCOL_ID,
    EvaluationError,
    binding,
    has_condition_component,
    load_json,
    relative,
    resolve,
    sha256,
    verify_binding,
    write_json,
)


def parse_time(value: str) -> str:
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def redact_conditions(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(r"\bP[012]\b", "[condition-redacted]", value, flags=re.IGNORECASE)
    if isinstance(value, list):
        return [redact_conditions(item) for item in value]
    if isinstance(value, dict):
        return {key: redact_conditions(item) for key, item in value.items()}
    return value


def sanitize_pathway(pathway: dict[str, Any], bridge_catalog: dict[str, Any] | None) -> dict[str, Any]:
    raw_units = [unit for unit in pathway.get("learning_units", []) if isinstance(unit, dict)]
    raw_sequence = pathway.get("instruction_sequence", [])
    sequence = [unit_id for unit_id in raw_sequence if isinstance(unit_id, str)]
    unit_map = {unit_id: f"U-{index:03d}" for index, unit_id in enumerate(sequence, 1)}
    for unit in raw_units:
        unit_id = unit.get("unit_id")
        if isinstance(unit_id, str) and unit_id not in unit_map:
            unit_map[unit_id] = f"U-{len(unit_map) + 1:03d}"

    units = []
    selected_bridge_ids: set[str] = set()
    raw_by_id = {unit.get("unit_id"): unit for unit in raw_units}
    for old_id in sequence:
        unit = raw_by_id.get(old_id, {})
        bridge_id = unit.get("bridge_contract_id")
        if isinstance(bridge_id, str):
            selected_bridge_ids.add(bridge_id)
        units.append({
            "unit_id": unit_map[old_id],
            "unit_type": unit.get("unit_type"),
            "purpose": unit.get("purpose"),
            "contract_item_ids": unit.get("contract_item_ids", []),
            "bridge_contract_id": bridge_id,
            "prerequisite_unit_ids": [unit_map[item] for item in unit.get("prerequisite_unit_ids", []) if item in unit_map],
            "learning_goal_ids": unit.get("learning_goal_ids", []),
        })

    released_bridges: list[dict[str, Any]] = []
    if bridge_catalog:
        released_bridges = [
            bridge for bridge in bridge_catalog.get("bridges", [])
            if isinstance(bridge, dict)
            and bridge.get("status") == "released"
            and bridge.get("bridge_contract_id") in selected_bridge_ids
        ]

    selection = pathway.get("selection", {})
    return redact_conditions({
        "schema_version": "1.0",
        "topic": pathway.get("topic"),
        "selected_item_ids": selection.get("selected_item_ids", []),
        "excluded_item_ids": selection.get("excluded_item_ids", []),
        "selection_decisions": selection.get("decisions", []),
        "learning_goal_mappings": pathway.get("learning_goal_mappings", []),
        "learning_units": units,
        "instruction_sequence": [unit_map[item] for item in sequence],
        "bridge_requirements": pathway.get("bridge_requirements", []),
        "released_bridges": released_bridges,
        "pathway_changes": pathway.get("pathway_changes", []),
        "scope_summary": pathway.get("scope_summary", {}),
    })


def sanitize_request(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": request.get("schema_version"),
        "request_id": request.get("request_id"),
        "request_version": request.get("request_version"),
        "topic": request.get("topic"),
        "audience_scope": request.get("audience_scope"),
        "learning_goal": request.get("learning_goal"),
        "target_capabilities": request.get("target_capabilities", []),
        "delivery_constraints": request.get("delivery_constraints", {}),
    }


def ensure_empty_target(path: Path, label: str) -> None:
    if path.exists():
        raise EvaluationError(f"{label} already exists; refusing to overwrite: {path}")
    if has_condition_component(path):
        raise EvaluationError(f"{label} path reveals an experimental condition: {path}")


def copy(path: Path, target: Path) -> None:
    shutil.copyfile(path, target)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create one condition-blind RQ2 evaluation sample.")
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--lesson-run", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--sample-id", required=True)
    parser.add_argument("--bundle-dir", required=True)
    parser.add_argument("--mapping-output", required=True)
    parser.add_argument("--generated-at", required=True, type=parse_time)
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    run_dir = resolve(root, args.lesson_run)
    profile_path = resolve(root, args.profile)
    bundle_dir = resolve(root, args.bundle_dir)
    mapping_output = resolve(root, args.mapping_output)
    stage: Path | None = None
    try:
        ensure_empty_target(bundle_dir, "bundle directory")
        ensure_empty_target(mapping_output, "mapping output")
        if bundle_dir in mapping_output.parents or mapping_output in bundle_dir.parents:
            raise EvaluationError("condition mapping must be stored outside the blind bundle tree")
        if not run_dir.is_dir() or not profile_path.is_file():
            raise EvaluationError("lesson run or learner profile is missing")

        manifest_path = run_dir / "lesson-manifest.json"
        validation_path = run_dir / "lesson-validation-report.json"
        lesson_path = run_dir / "lesson.md"
        manifest = load_json(manifest_path)
        validation = load_json(validation_path)
        profile = load_json(profile_path)
        if validation.get("valid") is not True:
            raise EvaluationError("lesson output did not pass composer validation")
        if manifest.get("outputs", {}).get("lesson", {}).get("sha256") != sha256(lesson_path):
            raise EvaluationError("lesson differs from its composer manifest")

        inputs = manifest.get("inputs", {})
        if not isinstance(inputs, dict):
            raise EvaluationError("lesson manifest inputs are invalid")
        contract_path = verify_binding(root, inputs.get("reference_contract", {}), "reference contract")
        request_path = verify_binding(root, inputs.get("learning_request", {}), "learning request")
        pathway_path = verify_binding(root, inputs.get("pathway", {}), "pathway")
        pathway_validation_path = verify_binding(root, inputs.get("pathway_validation_report", {}), "pathway validation")
        pathway_validation = load_json(pathway_validation_path)
        if pathway_validation.get("valid") is not True:
            raise EvaluationError("pathway did not pass deterministic validation")

        supplied_profile_hash = sha256(profile_path)
        bound_profile = inputs.get("profile")
        if isinstance(bound_profile, dict) and bound_profile:
            bound_profile_path = verify_binding(root, bound_profile, "profile")
            if sha256(bound_profile_path) != supplied_profile_hash:
                raise EvaluationError("supplied learner profile differs from the lesson's bound profile")

        contract = load_json(contract_path)
        if contract.get("lifecycle_status") != "frozen":
            raise EvaluationError("reference contract lifecycle_status is not frozen")
        release_report_path = contract_path.parent / "release_gate_report.json"
        release_report = load_json(release_report_path)
        if release_report.get("status") != "released":
            raise EvaluationError("reference contract has no successful release-gate report")
        release_outputs = release_report.get("outputs", {})
        if release_outputs.get("frozen_contract_sha256") != sha256(contract_path):
            raise EvaluationError("release-gate report does not bind the supplied Frozen Contract")
        request = load_json(request_path)
        pathway = load_json(pathway_path)

        bridge_catalog = None
        bridge_binding = inputs.get("bridge_catalog")
        if isinstance(bridge_binding, dict) and bridge_binding:
            bridge_catalog_path = verify_binding(root, bridge_binding, "bridge catalog")
            bridge_catalog = load_json(bridge_catalog_path)

        bundle_dir.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=".rq2-blind-stage-", dir=bundle_dir.parent))
        copy(lesson_path, stage / "lesson.md")
        copy(profile_path, stage / "learner-profile.json")
        write_json(stage / "learning-request.json", sanitize_request(request))
        copy(contract_path, stage / "frozen-reference-contract.json")
        write_json(stage / "pathway-evidence.json", sanitize_pathway(pathway, bridge_catalog))
        structural = {
            "schema_version": "1.0",
            "pathway_valid": True,
            "lesson_output_valid": True,
            "pathway_metrics": pathway_validation.get("metrics", {}),
            "lesson_metrics": validation.get("metrics", {}),
            "validation_scope": validation.get("validation_scope", {}),
        }
        write_json(stage / "structural-validation-evidence.json", structural)
        manifest_files = {
            name: {"sha256": sha256(stage / name)}
            for name in BUNDLE_FILES if name != "evaluation-manifest.json"
        }
        blind_manifest = {
            "schema_version": "1.0",
            "protocol_id": PROTOCOL_ID,
            "sample_id": args.sample_id,
            "created_at": args.generated_at,
            "files": manifest_files,
            "independence_policy": {
                "condition_hidden": True,
                "profile_visible_for_fit_judgement": True,
                "single_sample_pointwise_evaluation": True,
                "other_samples_excluded": True,
            },
            "authority_checks": {
                "frozen_contract_release_verified": True,
                "pathway_validation_verified": True,
                "lesson_output_validation_verified": True
            },
        }
        write_json(stage / "evaluation-manifest.json", blind_manifest)
        stage.rename(bundle_dir)
        stage = None

        condition = manifest.get("condition")
        run_id = manifest.get("run_id")
        mapping = {
            "schema_version": "1.0",
            "protocol_id": PROTOCOL_ID,
            "sample_id": args.sample_id,
            "condition": condition,
            "topic": manifest.get("topic"),
            "profile_id": profile.get("profile_id"),
            "run_id": run_id,
            "source_lesson_run": relative(root, run_dir),
            "source_pathway": relative(root, pathway_path),
            "blind_bundle": relative(root, bundle_dir),
            "blind_manifest_sha256": sha256(bundle_dir / "evaluation-manifest.json"),
            "created_at": args.generated_at,
        }
        write_json(mapping_output, mapping)
        print(f"PASS: blind RQ2 sample {args.sample_id} created at {bundle_dir}")
        return 0
    except (EvaluationError, OSError, ValueError) as exc:
        if stage and stage.exists():
            shutil.rmtree(stage)
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
