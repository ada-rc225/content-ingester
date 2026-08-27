#!/usr/bin/env python3
"""Validate an RQ2 P2 item selection, learning sequence, bridges, and rationale."""

from __future__ import annotations

import argparse
from pathlib import Path

from pathway_validation import (
    duplicate_values,
    flattened_unit_values,
    graph_errors,
    load_json_object,
    source_binding_errors,
    unit_map_and_errors,
    write_report,
)


CHANGE_TYPES = {
    "reorder_learning_units",
    "add_prerequisite_bridge",
    "regroup_contract_items",
    "change_prerequisite_relations",
    "change_item_selection",
}


def edges(unit_map: dict[str, dict]) -> set[tuple[str, str]]:
    return {
        (prerequisite, unit_id)
        for unit_id, unit in unit_map.items()
        for prerequisite in unit.get("prerequisite_unit_ids", [])
    }


def contract_assignments(unit_map: dict[str, dict], unit_ids: set[str]) -> dict[str, tuple[str, ...]]:
    return {
        unit_id: tuple(unit_map[unit_id].get("contract_item_ids", []))
        for unit_id in unit_ids
    }


def validate(
    canonical: dict,
    actual: dict,
    common_core: dict,
    permissions: dict,
    bridge_catalog: dict | None,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    policy = permissions.get("conditions", {}).get("P2")
    if not isinstance(policy, dict):
        errors.append("permission matrix has no P2 policy")
        policy = {}
    if actual.get("condition") != "P2":
        errors.append("actual condition must be P2")
    if not isinstance(actual.get("profile_id"), str) or not actual.get("profile_id"):
        errors.append("P2 must identify exactly one learner profile")
    if policy.get("canonical_sequence") != "mutable_with_rationale":
        errors.append("permission matrix does not permit rationalized P2 sequence changes")

    rendering = actual.get("rendering_policy", {})
    if rendering.get("output_form") != "one_continuous_student_facing_lesson":
        errors.append("P2 rendering_policy must require one continuous student-facing lesson")
    if rendering.get("learning_units_are_pages") is not False:
        errors.append("P2 learning units must be planning units, not pages")

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

    selected_list = actual.get("selected_contract_item_ids", [])
    excluded_list = actual.get("excluded_contract_item_ids", [])
    if not isinstance(selected_list, list) or not isinstance(excluded_list, list):
        errors.append("selected_contract_item_ids and excluded_contract_item_ids must be arrays")
        selected_list, excluded_list = [], []
    for duplicate in duplicate_values(selected_list):
        errors.append(f"duplicate selected Contract item: {duplicate}")
    for duplicate in duplicate_values(excluded_list):
        errors.append(f"duplicate excluded Contract item: {duplicate}")
    selected = set(selected_list)
    excluded = set(excluded_list)
    all_items = set(common_core.get("all_contract_item_ids", []))
    universal = set(common_core.get("universal_core_item_ids", []))
    selectable = set(common_core.get("selectable_item_ids", []))
    if selected & excluded:
        errors.append(f"Contract items are both selected and excluded: {sorted(selected & excluded)}")
    if selected | excluded != all_items:
        errors.append(
            "selected and excluded Contract items must partition all_contract_item_ids; "
            f"missing={sorted(all_items - (selected | excluded))}, "
            f"unknown={sorted((selected | excluded) - all_items)}"
        )
    if not universal.issubset(selected):
        errors.append(f"P2 omits universal core items: {sorted(universal - selected)}")
    if excluded - selectable:
        errors.append(f"P2 excludes non-selectable items: {sorted(excluded - selectable)}")

    decisions = actual.get("selection_decisions", [])
    if not isinstance(decisions, list):
        errors.append("selection_decisions must be an array")
        decisions = []
    decision_map: dict[str, dict] = {}
    for index, decision in enumerate(decisions):
        if not isinstance(decision, dict):
            errors.append(f"selection_decisions[{index}] must be an object")
            continue
        item_id = decision.get("item_id")
        if item_id in decision_map:
            errors.append(f"duplicate selection decision for {item_id}")
        if item_id not in selectable:
            errors.append(f"selection decision references non-selectable item {item_id}")
        if decision.get("decision") not in ("include", "exclude"):
            errors.append(f"selection decision for {item_id} must be include or exclude")
        for field in ("rationale", "profile_attribute"):
            if not isinstance(decision.get(field), str) or not decision.get(field).strip():
                errors.append(f"selection decision for {item_id} needs a non-empty {field}")
        if isinstance(item_id, str):
            decision_map[item_id] = decision
    if set(decision_map) != selectable:
        errors.append(
            f"selection decisions must cover every selectable item; missing={sorted(selectable - set(decision_map))}"
        )
    for item_id, decision in decision_map.items():
        expected_decision = "include" if item_id in selected else "exclude"
        if decision.get("decision") != expected_decision:
            errors.append(f"selection decision for {item_id} conflicts with selected/excluded lists")

    covered_items = flattened_unit_values(actual_units, "contract_item_ids")
    if covered_items != selected:
        if selected - covered_items:
            errors.append(
                f"selected Contract items are not assigned to learning units: {sorted(selected - covered_items)}"
            )
        if covered_items - selected:
            errors.append(
                f"learning units contain unselected Contract items: {sorted(covered_items - selected)}"
            )
    common_outcomes = {
        outcome.get("learning_outcome_id")
        for outcome in common_core.get("common_learning_outcomes", [])
        if isinstance(outcome, dict)
    }
    covered_outcomes = flattened_unit_values(actual_units, "learning_objective_ids")
    if not common_outcomes.issubset(covered_outcomes):
        errors.append(f"P2 omits common learning outcomes: {sorted(common_outcomes - covered_outcomes)}")

    canonical_ids = set(canonical_units)
    actual_ids = set(actual_units)
    added_ids = actual_ids - canonical_ids
    removed_ids = canonical_ids - actual_ids
    approved_bridges: set[str] = set()
    if bridge_catalog is not None:
        approved_bridges = {
            record.get("bridge_contract_id")
            for record in bridge_catalog.get("bridges", [])
            if isinstance(record, dict) and record.get("status") == "released"
        }
    bridge_ids: set[str] = set()
    for unit_id in sorted(added_ids):
        unit = actual_units[unit_id]
        if unit.get("unit_type") == "prerequisite_bridge":
            bridge_ids.add(unit_id)
            bridge_id = unit.get("bridge_contract_id")
            if bridge_catalog is None:
                errors.append(f"prerequisite bridge {unit_id} requires --bridge-catalog")
            elif bridge_id not in approved_bridges:
                errors.append(
                    f"prerequisite bridge {unit_id} uses an unapproved bridge contract: {bridge_id}"
                )
        else:
            origins = unit.get("origin_unit_ids")
            if not isinstance(origins, list) or not origins or not set(origins).issubset(canonical_ids):
                errors.append(
                    f"new contract-content unit {unit_id} requires canonical origin_unit_ids"
                )

    canonical_common_order = [
        unit_id for unit_id in canonical.get("instruction_sequence", []) if unit_id in actual_ids
    ]
    actual_common_order = [
        unit_id for unit_id in actual.get("instruction_sequence", []) if unit_id in canonical_ids
    ]
    detected: set[str] = set()
    if canonical_common_order != actual_common_order:
        detected.add("reorder_learning_units")
    if bridge_ids:
        detected.add("add_prerequisite_bridge")
    if added_ids - bridge_ids or removed_ids:
        detected.add("regroup_contract_items")
    common_ids = canonical_ids & actual_ids
    canonical_common_edges = {
        edge for edge in edges(canonical_units) if edge[0] in common_ids and edge[1] in common_ids
    }
    actual_common_edges = {
        edge for edge in edges(actual_units) if edge[0] in common_ids and edge[1] in common_ids
    }
    if canonical_common_edges != actual_common_edges:
        detected.add("change_prerequisite_relations")
    if contract_assignments(canonical_units, common_ids) != contract_assignments(actual_units, common_ids):
        detected.add("regroup_contract_items")
    if selected != set(canonical.get("selected_contract_item_ids", [])):
        detected.add("change_item_selection")

    permission_fields = {
        "reorder_learning_units": "reorder_learning_units",
        "add_prerequisite_bridge": "add_prerequisite_bridges",
        "regroup_contract_items": "regroup_contract_items",
        "change_prerequisite_relations": "change_prerequisite_relations",
    }
    for change, field in permission_fields.items():
        if change in detected and policy.get(field) is not True:
            errors.append(f"permission matrix forbids detected change: {change}")

    changes = actual.get("pathway_changes", [])
    if not isinstance(changes, list):
        errors.append("pathway_changes must be an array")
        changes = []
    declared_types: set[str] = set()
    for index, change in enumerate(changes):
        if not isinstance(change, dict):
            errors.append(f"pathway_changes[{index}] must be an object")
            continue
        change_type = change.get("change_type")
        if change_type not in CHANGE_TYPES:
            errors.append(f"unsupported pathway change type: {change_type}")
        else:
            declared_types.add(change_type)
        for field in ("profile_attribute", "rationale"):
            if not isinstance(change.get(field), str) or not change.get(field).strip():
                errors.append(f"pathway change {index} needs a non-empty {field}")
    for detected_change in detected:
        if detected_change not in declared_types:
            errors.append(f"detected change lacks a declared rationale: {detected_change}")
    if not detected:
        warnings.append(
            "P2 plan is valid but its selected content, order, prerequisites and bridges do not differ from the canonical sequence; it is not evidence of material pathway adaptation."
        )

    report = {
        "schema_version": "0.2",
        "validator": "rq2-adaptive-pathway-v0.2",
        "condition": "P2",
        "pathway_id": actual.get("pathway_id"),
        "profile_id": actual.get("profile_id"),
        "valid": not errors,
        "treatment_valid": not errors,
        "materially_different": bool(detected),
        "detected_change_types": sorted(detected),
        "errors": errors,
        "warnings": warnings,
        "checks": {
            "canonical_learning_unit_count": len(canonical_units),
            "actual_learning_unit_count": len(actual_units),
            "added_learning_unit_ids": sorted(added_ids),
            "removed_learning_unit_ids": sorted(removed_ids),
            "selected_contract_item_count": len(selected),
            "universal_core_coverage": (
                len(universal & covered_items) / len(universal) if universal else 1.0
            ),
            "selected_item_coverage": (
                len(selected & covered_items) / len(selected) if selected else 1.0
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
    parser.add_argument("--bridge-catalog", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        report = validate(
            load_json_object(args.canonical),
            load_json_object(args.actual),
            load_json_object(args.common_core),
            load_json_object(args.permissions),
            load_json_object(args.bridge_catalog) if args.bridge_catalog else None,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    write_report(args.output, report)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
