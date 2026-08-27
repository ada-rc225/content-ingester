#!/usr/bin/env python3
"""Validate that an RQ2 P0/P1 output preserves the canonical learning sequence."""

from __future__ import annotations

import argparse
from pathlib import Path

from pathway_validation import (
    flattened_unit_values,
    graph_errors,
    load_json_object,
    unit_map_and_errors,
    simplified_decisions,
    source_binding_errors,
    write_report,
)


IMMUTABLE_UNIT_FIELDS = (
    "unit_type",
    "prerequisite_unit_ids",
    "learning_objective_ids",
    "contract_item_ids",
)


def validate(
    canonical: dict,
    actual: dict,
    common_core: dict,
    permissions: dict,
    condition: str,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    condition_policy = permissions.get("conditions", {}).get(condition)
    if condition not in ("P0", "P1") or not isinstance(condition_policy, dict):
        errors.append("condition must be P0 or P1 and exist in the permission matrix")
        condition_policy = {}
    if condition_policy.get("canonical_sequence") != "exact":
        errors.append(f"permission matrix does not freeze the canonical sequence for {condition}")
    if condition_policy.get("contract_item_selection") != "canonical_exact":
        errors.append(f"permission matrix does not freeze Contract selection for {condition}")

    if actual.get("condition") != condition:
        errors.append(f"actual condition must be {condition}")
    profile_id = actual.get("profile_id")
    if condition == "P0" and profile_id not in (None, ""):
        errors.append("P0 must not contain a learner profile ID")
    if condition == "P1" and (not isinstance(profile_id, str) or not profile_id):
        errors.append("P1 must identify exactly one learner profile")
    rendering = actual.get("rendering_policy", {})
    if rendering.get("output_form") != "one_continuous_student_facing_lesson":
        errors.append(f"{condition} must render as one continuous student-facing lesson")
    if rendering.get("learning_units_are_pages") is not False:
        errors.append(f"{condition} learning units must be planning units, not pages")

    expected_source = common_core.get("source_contract", {})
    errors.extend(source_binding_errors(expected_source, canonical.get("source_contract", {}), "canonical"))
    errors.extend(source_binding_errors(expected_source, actual.get("source_contract", {}), "actual"))
    if actual.get("topic") != common_core.get("topic"):
        errors.append("actual topic does not match common-core topic")

    canonical_units, canonical_unit_errors = unit_map_and_errors(canonical)
    actual_units, actual_unit_errors = unit_map_and_errors(actual)
    errors.extend(f"canonical: {error}" for error in canonical_unit_errors)
    errors.extend(f"actual: {error}" for error in actual_unit_errors)
    errors.extend(f"canonical: {error}" for error in graph_errors(canonical, canonical_units))
    errors.extend(f"actual: {error}" for error in graph_errors(actual, actual_units))

    if actual.get("instruction_sequence") != canonical.get("instruction_sequence"):
        errors.append("fixed condition changed instruction_sequence")
    if set(actual_units) != set(canonical_units):
        errors.append("fixed condition changed the canonical learning-unit set")
    for unit_id in sorted(set(actual_units) & set(canonical_units)):
        for field in IMMUTABLE_UNIT_FIELDS:
            if actual_units[unit_id].get(field) != canonical_units[unit_id].get(field):
                errors.append(f"fixed condition changed {unit_id}.{field}")

    canonical_selected = canonical.get("selected_contract_item_ids", [])
    canonical_excluded = canonical.get("excluded_contract_item_ids", [])
    if actual.get("selected_contract_item_ids") != canonical_selected:
        errors.append("fixed condition changed selected_contract_item_ids")
    if actual.get("excluded_contract_item_ids") != canonical_excluded:
        errors.append("fixed condition changed excluded_contract_item_ids")
    if simplified_decisions(actual) != simplified_decisions(canonical):
        errors.append("fixed condition changed canonical selection decisions")

    covered_items = flattened_unit_values(actual_units, "contract_item_ids")
    selected_items = set(actual.get("selected_contract_item_ids", []))
    if covered_items != selected_items:
        missing = sorted(selected_items - covered_items)
        unselected = sorted(covered_items - selected_items)
        if missing:
            errors.append(f"selected Contract items are not assigned to learning units: {missing}")
        if unselected:
            errors.append(f"learning units contain unselected Contract items: {unselected}")
    core_items = set(common_core.get("universal_core_item_ids", []))
    if not core_items.issubset(selected_items):
        errors.append(f"fixed pathway omits universal core items: {sorted(core_items - selected_items)}")

    common_outcomes = {
        outcome.get("learning_outcome_id")
        for outcome in common_core.get("common_learning_outcomes", [])
        if isinstance(outcome, dict)
    }
    covered_outcomes = flattened_unit_values(actual_units, "learning_objective_ids")
    if not common_outcomes.issubset(covered_outcomes):
        errors.append(
            f"fixed pathway omits common learning outcomes: {sorted(common_outcomes - covered_outcomes)}"
        )

    report = {
        "schema_version": "0.2",
        "validator": "rq2-fixed-pathway-v0.2",
        "condition": condition,
        "pathway_id": actual.get("pathway_id"),
        "valid": not errors,
        "treatment_valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "canonical_learning_unit_count": len(canonical_units),
            "actual_learning_unit_count": len(actual_units),
            "selected_contract_item_count": len(selected_items),
            "covered_contract_item_count": len(covered_items),
            "universal_core_coverage": (
                len(core_items & covered_items) / len(core_items) if core_items else 1.0
            ),
            "canonical_sequence_exact": not any(
                "fixed condition changed" in error for error in errors
            ),
        },
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--common-core", type=Path, required=True)
    parser.add_argument("--permissions", type=Path, required=True)
    parser.add_argument("--condition", choices=("P0", "P1"), required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = validate(
            load_json_object(args.canonical),
            load_json_object(args.actual),
            load_json_object(args.common_core),
            load_json_object(args.permissions),
            args.condition,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    write_report(args.output, report)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
