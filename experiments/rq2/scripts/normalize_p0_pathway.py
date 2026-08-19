#!/usr/bin/env python3
"""Deterministically normalize the fixed v0.2 canonical pathway into unified P0."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any

from validate_pathway_plan import Validator


REPO_ROOT = Path(__file__).resolve().parents[3]
AUTHORITY_SCRIPTS = REPO_ROOT / ".github/skills/plan-adaptive-curriculum-pathways/scripts"
import sys

sys.path.insert(0, str(AUTHORITY_SCRIPTS))

from pathway_authorities import (  # noqa: E402
    AuthorityError,
    display_path,
    load_object,
    resolve_path,
    sha256,
    verify_learning_request,
    verify_reference_contract_release,
)


PATHWAY_ID_RE = re.compile(r"^[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)*$")


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise AuthorityError(code, message)


def validate_timestamp(value: str) -> None:
    require(value.endswith("Z"), "generated_at.format", "--generated-at must be a UTC ISO-8601 timestamp ending in Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError("generated_at.format", "--generated-at is not a valid ISO-8601 timestamp") from exc


def verify_mapping_binding(
    root: Path,
    mapping: dict[str, Any],
    name: str,
    expected_path: Path,
) -> None:
    bindings = mapping.get("bindings")
    require(isinstance(bindings, dict), "mapping.bindings", "normalization map bindings are missing")
    binding = bindings.get(name)
    require(isinstance(binding, dict), f"mapping.{name}", f"normalization map has no {name} binding")
    require(
        resolve_path(root, binding.get("file")) == expected_path.resolve(),
        f"mapping.{name}.path",
        f"normalization map identifies another {name} file",
    )
    require(
        binding.get("sha256") == sha256(expected_path),
        f"mapping.{name}.hash",
        f"normalization map {name} SHA-256 is stale",
    )


def unique_ids(values: Any, label: str) -> list[str]:
    require(isinstance(values, list), f"{label}.type", f"{label} must be an array")
    require(all(isinstance(value, str) and value for value in values), f"{label}.items", f"{label} must contain non-empty strings")
    require(len(values) == len(set(values)), f"{label}.duplicate", f"{label} contains duplicates")
    return values


def normalized_topic(value: Any) -> str:
    return re.sub(r"[-_\s]+", " ", value.strip().lower()) if isinstance(value, str) else ""


def build_plan(
    root: Path,
    canonical_path: Path,
    common_core_path: Path,
    contract_path: Path,
    request_path: Path,
    mapping_path: Path,
    pathway_id: str,
    generated_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    canonical = load_object(canonical_path)
    common_core = load_object(common_core_path)
    mapping = load_object(mapping_path)
    contract = verify_reference_contract_release(root, contract_path)
    request = verify_learning_request(root, request_path, contract_path, contract)

    require(canonical.get("schema_version") == "0.2", "canonical.schema", "canonical pathway must use schema_version 0.2")
    require(common_core.get("schema_version") == "0.2", "common_core.schema", "common core must use schema_version 0.2")
    require(mapping.get("schema_version") == "1.0", "mapping.schema", "normalization map must use schema_version 1.0")
    require(mapping.get("status") in {"pilot_candidate", "approved"}, "mapping.status", "normalization map status is invalid")
    for name, path in (
        ("canonical_pathway", canonical_path),
        ("common_core", common_core_path),
        ("learning_request", request_path),
    ):
        verify_mapping_binding(root, mapping, name, path)

    topic = request.get("topic")
    topic_values = (
        canonical.get("topic"), common_core.get("topic"),
        mapping.get("topic"), topic,
    )
    require(
        bool(normalized_topic(topic))
        and len({normalized_topic(value) for value in topic_values}) == 1,
        "input.topic",
        "canonical, common core, mapping, and learning request topics differ",
    )
    canonical_source = canonical.get("source_contract")
    core_source = common_core.get("source_contract")
    require(isinstance(canonical_source, dict) and isinstance(core_source, dict), "input.contract", "fixed-baseline Contract bindings are missing")
    for label, binding in (("canonical", canonical_source), ("common_core", core_source)):
        require(binding.get("contract_id") == contract.get("contract_id"), f"{label}.contract_id", f"{label} contract_id differs")
        require(binding.get("contract_version") == contract.get("contract_version"), f"{label}.contract_version", f"{label} contract_version differs")
        require(binding.get("sha256") == sha256(contract_path), f"{label}.contract_hash", f"{label} Contract SHA-256 is stale")

    contract_items = contract.get("contract_items")
    require(isinstance(contract_items, list) and contract_items, "contract.items", "Frozen Contract items are missing")
    item_map = {item["item_id"]: item for item in contract_items}
    contract_ids = list(item_map)
    all_ids = unique_ids(common_core.get("all_contract_item_ids"), "common_core.all_contract_item_ids")
    universal = unique_ids(common_core.get("universal_core_item_ids"), "common_core.universal_core_item_ids")
    selectable = unique_ids(common_core.get("selectable_item_ids"), "common_core.selectable_item_ids")
    require(all_ids == contract_ids, "common_core.contract_order", "common core item IDs must equal Frozen Contract order")
    require(set(universal).isdisjoint(selectable) and set(universal) | set(selectable) == set(contract_ids), "common_core.partition", "universal and selectable IDs must partition the Contract")

    selected = unique_ids(canonical.get("selected_contract_item_ids"), "canonical.selected_contract_item_ids")
    excluded = unique_ids(canonical.get("excluded_contract_item_ids"), "canonical.excluded_contract_item_ids")
    require(set(selected).isdisjoint(excluded) and set(selected) | set(excluded) == set(contract_ids), "canonical.partition", "canonical selected and excluded IDs must partition the Contract")
    require(selected == [item_id for item_id in contract_ids if item_id in set(selected)], "canonical.selected_order", "canonical selected IDs must preserve Frozen Contract order")

    role_policy = mapping.get("selected_role_policy")
    require(isinstance(role_policy, dict), "mapping.roles", "selected-role policy is missing")
    require(role_policy.get("universal_core_item_ids") in {"target", "supporting", "extension"}, "mapping.universal_role", "universal-core role is invalid")
    require(role_policy.get("selectable_item_ids") in {"target", "supporting", "extension"}, "mapping.selectable_role", "selectable-item role is invalid")
    canonical_decisions = canonical.get("selection_decisions")
    require(isinstance(canonical_decisions, list), "canonical.decisions", "canonical selection_decisions must be an array")
    decision_map: dict[str, dict[str, Any]] = {}
    for decision in canonical_decisions:
        require(isinstance(decision, dict), "canonical.decision_type", "canonical decisions must be objects")
        item_id = decision.get("item_id")
        require(item_id in contract_ids and item_id not in decision_map, "canonical.decision_id", f"invalid or duplicate canonical decision for {item_id}")
        expected = "include" if item_id in selected else "exclude"
        require(decision.get("decision") == expected, "canonical.decision_conflict", f"canonical decision for {item_id} conflicts with selection")
        require(isinstance(decision.get("rationale"), str) and decision["rationale"].strip(), "canonical.decision_rationale", f"canonical decision for {item_id} needs a rationale")
        decision_map[item_id] = decision

    normalized_decisions = []
    universal_set = set(universal)
    selected_set = set(selected)
    for item_id in contract_ids:
        source = decision_map.get(item_id)
        included = item_id in selected_set
        if source is not None:
            rationale = source["rationale"]
        elif included:
            rationale = "Included by the fixed canonical P0 baseline as a universal-core item."
        else:
            rationale = "Excluded by the fixed canonical P0 baseline."
        normalized_decisions.append({
            "item_id": item_id,
            "decision": "include" if included else "exclude",
            "selected_role": (
                role_policy["universal_core_item_ids"] if item_id in universal_set
                else role_policy["selectable_item_ids"]
            ) if included else None,
            "rationale": rationale,
            "profile_basis": [],
        })

    capabilities = request.get("target_capabilities")
    require(isinstance(capabilities, list) and capabilities, "request.capabilities", "learning-request capabilities are missing")
    capability_ids = [capability["capability_id"] for capability in capabilities]
    support_map = mapping.get("capability_supporting_item_ids")
    objective_map = mapping.get("learning_objective_to_capability_ids")
    require(isinstance(support_map, dict) and set(support_map) == set(capability_ids), "mapping.capability_coverage", "normalization map must cover every requested capability exactly once")
    require(isinstance(objective_map, dict), "mapping.objectives", "learning-objective mapping is missing")
    goal_mappings = []
    for capability in capabilities:
        capability_id = capability["capability_id"]
        supports = unique_ids(support_map[capability_id], f"mapping.{capability_id}.support")
        require(set(supports).issubset(selected_set), "mapping.unselected_support", f"{capability_id} uses unselected support items")
        require(bool(supports), "mapping.empty_support", f"{capability_id} needs supporting items")
        goal_mappings.append({
            "capability_id": capability_id,
            "supporting_item_ids": supports,
            "coverage": "complete",
            "rationale": "Deterministically migrated from the reviewed P0 normalization map.",
        })

    raw_units = canonical.get("learning_units")
    sequence = unique_ids(canonical.get("instruction_sequence"), "canonical.instruction_sequence")
    require(isinstance(raw_units, list) and raw_units, "canonical.units", "canonical learning units are missing")
    units: list[dict[str, Any]] = []
    unit_ids: list[str] = []
    assigned: list[str] = []
    for raw in raw_units:
        require(isinstance(raw, dict), "canonical.unit_type", "canonical learning units must be objects")
        unit_id = raw.get("unit_id")
        require(isinstance(unit_id, str) and unit_id not in unit_ids, "canonical.unit_id", f"invalid or duplicate unit {unit_id}")
        unit_ids.append(unit_id)
        item_ids = unique_ids(raw.get("contract_item_ids"), f"canonical.{unit_id}.items")
        assigned.extend(item_ids)
        old_objectives = unique_ids(raw.get("learning_objective_ids"), f"canonical.{unit_id}.objectives")
        unknown_objectives = set(old_objectives) - set(objective_map)
        require(not unknown_objectives, "mapping.objective_missing", f"normalization map omits objectives: {sorted(unknown_objectives)}")
        mapped_goals = {
            capability_id
            for objective_id in old_objectives
            for capability_id in objective_map[objective_id]
        }
        require(mapped_goals.issubset(capability_ids), "mapping.objective_target", f"unit {unit_id} maps to unknown capabilities")
        units.append({
            "unit_id": unit_id,
            "unit_type": "contract_content",
            "purpose": raw.get("title"),
            "contract_item_ids": item_ids,
            "bridge_contract_id": None,
            "prerequisite_unit_ids": raw.get("prerequisite_unit_ids"),
            "learning_goal_ids": [capability_id for capability_id in capability_ids if capability_id in mapped_goals],
        })
    require(sequence == unit_ids, "canonical.unit_order", "canonical learning_units must be stored in instruction_sequence order")
    require(len(assigned) == len(set(assigned)) and set(assigned) == selected_set, "canonical.unit_coverage", "canonical units must assign every selected item exactly once")

    delivery = request.get("delivery_constraints")
    require(isinstance(delivery, dict), "request.delivery", "learning-request delivery constraints are missing")
    duration = canonical.get("target_duration_minutes")
    require(duration == delivery.get("target_duration_minutes"), "duration.mismatch", "canonical and learning-request durations differ")
    canonical_rendering = canonical.get("rendering_policy")
    require(isinstance(canonical_rendering, dict), "canonical.rendering", "canonical rendering policy is missing")
    require(canonical_rendering.get("output_form") == delivery.get("output_form"), "rendering.output", "canonical and learning-request output forms differ")
    require(canonical_rendering.get("learning_units_are_pages") is False and delivery.get("learning_units_are_pages") is False, "rendering.pages", "learning units must not be pages")

    selected_items = [item_map[item_id] for item_id in selected]
    plan = {
        "schema_version": "1.0",
        "pathway_id": pathway_id,
        "condition": "P0",
        "plan_status": "complete",
        "topic": topic,
        "source_authorities": {
            "reference_contract": {
                "contract_id": contract["contract_id"],
                "contract_version": contract["contract_version"],
                "file": display_path(contract_path, root),
                "sha256": sha256(contract_path),
            },
            "curriculum_model": None,
        },
        "profile_binding": None,
        "profile_concept_assessment_binding": None,
        "learning_request_binding": {
            "request_id": request["request_id"],
            "request_version": request["request_version"],
            "file": display_path(request_path, root),
            "sha256": sha256(request_path),
        },
        "baseline_pathway_binding": None,
        "selection_authority": "fixed_baseline",
        "selection": {
            "all_contract_item_ids": contract_ids,
            "selected_item_ids": selected,
            "excluded_item_ids": excluded,
            "decisions": normalized_decisions,
        },
        "learning_goal_mappings": goal_mappings,
        "learning_units": units,
        "instruction_sequence": sequence,
        "bridge_requirements": [],
        "pathway_changes": [],
        "scope_summary": {
            "selected_contract_item_count": len(selected),
            "excluded_contract_item_count": len(excluded),
            "critical_item_count": sum(item.get("criticality") == "critical" for item in selected_items),
            "formula_count": len({formula for item in selected_items for formula in item.get("formula_refs", [])}),
            "algorithm_or_code_item_count": sum(item.get("item_type") in {"algorithm_rule", "code_semantics"} for item in selected_items),
            "released_bridge_count": 0,
            "estimated_duration_minutes": duration,
        },
        "rendering_policy": {
            "output_form": delivery["output_form"],
            "learning_units_are_pages": False,
            "target_duration_minutes": duration,
        },
        "generated_by": {
            "producer": "normalize-p0-pathway",
            "producer_version": "1.0",
            "method": "deterministic_baseline_normalization",
            "generated_at": generated_at,
        },
    }
    validator = Validator(root, "pilot", None)
    validator.validate(plan)
    require(not validator.errors, "output.validation", f"normalized P0 failed unified validation: {validator.errors}")
    receipt = {
        "schema_version": "1.0",
        "operation": "deterministic-p0-normalization-v1",
        "inputs": {
            "canonical_pathway": {"file": display_path(canonical_path, root), "sha256": sha256(canonical_path)},
            "common_core": {"file": display_path(common_core_path, root), "sha256": sha256(common_core_path)},
            "normalization_map": {"file": display_path(mapping_path, root), "sha256": sha256(mapping_path)},
            "reference_contract": {"file": display_path(contract_path, root), "sha256": sha256(contract_path)},
            "learning_request": {"file": display_path(request_path, root), "sha256": sha256(request_path)},
        },
        "mapping_id": mapping["mapping_id"],
        "mapping_review_status": mapping["review"]["review_status"],
        "pathway_id": pathway_id,
        "generated_at": generated_at,
    }
    return plan, receipt


def write_pair(output: Path, receipt_path: Path, plan: dict[str, Any], receipt: dict[str, Any], root: Path) -> None:
    require(output != receipt_path, "output.collision", "plan and receipt outputs must differ")
    require(not output.exists(), "output.exists", f"refusing to overwrite {output}")
    require(not receipt_path.exists(), "receipt.exists", f"refusing to overwrite {receipt_path}")
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    receipt["output"] = {
        "file": display_path(output, root),
        "sha256": sha256(output),
    }
    try:
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except Exception:
        output.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--common-core", type=Path, required=True)
    parser.add_argument("--reference-contract", type=Path, required=True)
    parser.add_argument("--learning-request", type=Path, required=True)
    parser.add_argument("--normalization-map", type=Path, required=True)
    parser.add_argument("--pathway-id", required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    root = Path(args.workspace_root).resolve()
    try:
        require(bool(PATHWAY_ID_RE.fullmatch(args.pathway_id)), "pathway_id.format", "--pathway-id has an invalid format")
        validate_timestamp(args.generated_at)
        plan, receipt = build_plan(
            root,
            args.canonical.resolve(),
            args.common_core.resolve(),
            args.reference_contract.resolve(),
            args.learning_request.resolve(),
            args.normalization_map.resolve(),
            args.pathway_id,
            args.generated_at,
        )
        write_pair(args.output.resolve(), args.receipt.resolve(), plan, receipt, root)
    except (AuthorityError, OSError, KeyError, TypeError, ValueError) as exc:
        code = exc.code if isinstance(exc, AuthorityError) else "normalization.input"
        print(f"ERROR [{code}]: {exc}")
        return 1
    print(f"PASS: wrote deterministic unified P0 plan to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
