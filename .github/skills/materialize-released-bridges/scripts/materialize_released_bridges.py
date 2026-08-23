#!/usr/bin/env python3
"""Materialize released bridge requirements into a new deterministic P2 plan."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from typing import Any


MATERIALIZER = "released-bridge-pathway-materializer-v1"
RULE_ID = "first-consuming-unit-v1"
ID_PATTERN = re.compile(r"^[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)*$")
BRIDGE_REQUIREMENT_ID_PATTERN = re.compile(r"^BRQ-[0-9]{3,}$")
BRIDGE_REQUIREMENT_FIELDS = {
    "requirement_id",
    "concept_id",
    "bridge_candidate_id",
    "required_by_item_ids",
    "learner_mastery",
    "resolution_status",
    "released_bridge_contract_id",
    "rationale",
}
LEGACY_BRIDGE_REQUIREMENT_FIELDS = {
    "bridge_requirement_id",
    "triggering_item_ids",
    "status",
    "reason",
}


class MaterializationError(ValueError):
    """Materialization failure with a stable diagnostic code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise MaterializationError(code, message)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MaterializationError("input.read", f"cannot read {path}: {exc}") from exc
    require(isinstance(value, dict), "input.type", f"JSON root must be an object: {path}")
    return value


def write_object(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_path(root: Path, raw: Any) -> Path | None:
    if not isinstance(raw, str) or not raw:
        return None
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def parse_timestamp(raw: str) -> str:
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise MaterializationError("input.timestamp", "generated-at must be ISO 8601") from exc
    require(parsed.tzinfo is not None, "input.timestamp", "generated-at must include a timezone")
    return raw


def validate_parent_review(
    root: Path,
    pathway_path: Path,
    review_path: Path,
    pathway: dict[str, Any],
    review: dict[str, Any],
) -> None:
    require(review.get("review_status") == "approved", "review.status", "parent review must be approved")
    require(review.get("overall_review", {}).get("decision") == "approved", "review.overall", "parent overall review must be approved")
    binding = review.get("candidate_binding")
    require(isinstance(binding, dict), "review.binding", "parent review binding is missing")
    require(binding.get("pathway_id") == pathway.get("pathway_id"), "review.pathway_id", "review identifies another pathway")
    require(resolve_path(root, binding.get("pathway_file")) == pathway_path, "review.pathway", "review identifies another pathway file")
    require(binding.get("pathway_sha256") == sha256(pathway_path), "review.pathway_hash", "parent pathway changed after review")
    require(review_path.is_file(), "input.missing", f"missing parent review: {review_path}")


def validate_release(
    root: Path,
    parent_path: Path,
    parent_review_path: Path,
    parent: dict[str, Any],
    catalog_path: Path,
    report_path: Path,
    catalog: dict[str, Any],
    report: dict[str, Any],
) -> None:
    require(catalog.get("status") == "released", "catalog.status", "bridge catalog is not released")
    bridges = catalog.get("bridges")
    require(isinstance(bridges, list) and bridges, "catalog.bridges", "released catalog has no bridges")
    require(all(isinstance(item, dict) and item.get("status") == "released" for item in bridges), "catalog.bridge_status", "every catalog bridge must be released")
    require(report.get("status") == "released", "release.status", "bridge release report is not released")
    require(report.get("library_id") == catalog.get("library_id"), "release.library_id", "release report identifies another library")
    outputs = report.get("outputs")
    require(isinstance(outputs, dict), "release.outputs", "bridge release outputs are missing")
    require(resolve_path(root, outputs.get("released_bridge_catalog")) == catalog_path, "release.catalog", "release report identifies another catalog")
    require(outputs.get("released_bridge_catalog_sha256") == sha256(catalog_path), "release.catalog_hash", "released catalog hash is stale")

    bindings = catalog.get("pathway_bindings")
    require(isinstance(bindings, list), "catalog.pathways", "catalog pathway bindings are missing")
    matches = [item for item in bindings if isinstance(item, dict) and item.get("pathway_id") == parent.get("pathway_id")]
    require(len(matches) == 1, "catalog.parent", "catalog must contain exactly one binding for the parent pathway")
    binding = matches[0]
    require(resolve_path(root, binding.get("pathway_file")) == parent_path, "catalog.parent_path", "catalog binds another parent pathway file")
    require(binding.get("pathway_sha256") == sha256(parent_path), "catalog.parent_hash", "catalog parent pathway hash is stale")
    require(resolve_path(root, binding.get("review_file")) == parent_review_path, "catalog.review_path", "catalog binds another parent review file")
    require(binding.get("review_sha256") == sha256(parent_review_path), "catalog.review_hash", "catalog parent review hash is stale")
    require(report_path.is_file(), "input.missing", f"missing bridge release report: {report_path}")


def ordered_goal_union(
    sequence: list[str],
    units: dict[str, dict[str, Any]],
    required_items: set[str],
) -> list[str]:
    result: list[str] = []
    for unit_id in sequence:
        unit = units[unit_id]
        if required_items.intersection(unit.get("contract_item_ids", [])):
            for goal in unit.get("learning_goal_ids", []):
                if goal not in result:
                    result.append(goal)
    return result


def load_bound_concept_assessments(
    root: Path,
    parent: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    binding = parent.get("profile_concept_assessment_binding")
    require(
        isinstance(binding, dict),
        "assessment.binding",
        "parent profile-concept-assessment binding is missing",
    )
    assessment_path = resolve_path(root, binding.get("file"))
    require(
        assessment_path is not None and assessment_path.is_file(),
        "assessment.file",
        "bound profile-concept assessment is missing",
    )
    require(
        binding.get("sha256") == sha256(assessment_path),
        "assessment.hash",
        "bound profile-concept assessment hash is stale",
    )
    assessment = load_object(assessment_path)
    require(
        binding.get("artifact_id") == assessment.get("assessment_id"),
        "assessment.id",
        "bound profile-concept assessment ID differs from the file",
    )
    entries = assessment.get("concept_assessments")
    require(
        isinstance(entries, list),
        "assessment.concepts",
        "bound profile-concept assessment has no concept assessments",
    )
    result: dict[str, dict[str, Any]] = {}
    for entry in entries:
        require(
            isinstance(entry, dict) and isinstance(entry.get("concept_id"), str),
            "assessment.concept",
            "bound profile-concept assessment contains an invalid concept",
        )
        concept_id = entry["concept_id"]
        require(
            concept_id not in result,
            "assessment.concept",
            f"bound profile-concept assessment repeats {concept_id}",
        )
        result[concept_id] = entry
    return result


def normalize_bridge_requirements(
    requirements: list[Any],
    assessments: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    """Normalize known Planner legacy aliases into the canonical child shape."""

    normalized: list[dict[str, Any]] = []
    actions_by_requirement: dict[str, list[str]] = {}
    seen_concepts: set[str] = set()

    for index, raw in enumerate(requirements, start=1):
        require(
            isinstance(raw, dict),
            "parent.requirement_type",
            "every parent bridge requirement must be an object",
        )
        unknown_fields = set(raw) - BRIDGE_REQUIREMENT_FIELDS - LEGACY_BRIDGE_REQUIREMENT_FIELDS
        require(
            not unknown_fields,
            "parent.requirement_fields",
            "unsupported bridge-requirement fields: " + ", ".join(sorted(unknown_fields)),
        )

        actions: list[str] = []
        expected_id = f"BRQ-{index:03d}"
        standard_id = raw.get("requirement_id")
        if standard_id is None:
            requirement_id = expected_id
            actions.append("generated_requirement_id_from_requirement_order")
        else:
            require(
                isinstance(standard_id, str)
                and BRIDGE_REQUIREMENT_ID_PATTERN.fullmatch(standard_id) is not None,
                "parent.requirement_id",
                f"invalid bridge requirement ID at position {index}",
            )
            require(
                standard_id == expected_id,
                "parent.requirement_id",
                f"bridge requirement at position {index} must use {expected_id}",
            )
            requirement_id = standard_id

        concept_id = raw.get("concept_id")
        candidate_id = raw.get("bridge_candidate_id")
        required_items = raw.get("required_by_item_ids")
        mastery = raw.get("learner_mastery")
        resolution_status = raw.get("resolution_status")
        require(
            isinstance(concept_id, str) and concept_id,
            "parent.requirement_concept",
            f"{requirement_id} has no concept_id",
        )
        require(
            concept_id not in seen_concepts,
            "parent.requirement_concept",
            f"duplicate bridge requirement for {concept_id}",
        )
        seen_concepts.add(concept_id)
        require(
            isinstance(candidate_id, str) and candidate_id,
            "parent.requirement_candidate",
            f"{requirement_id} has no bridge_candidate_id",
        )
        require(
            isinstance(required_items, list)
            and bool(required_items)
            and all(isinstance(item, str) and item for item in required_items)
            and len(required_items) == len(set(required_items)),
            "parent.requirement_items",
            f"{requirement_id} has invalid required_by_item_ids",
        )
        require(
            mastery in {"fragile", "missing", "unknown"},
            "parent.requirement_mastery",
            f"{requirement_id} has invalid learner_mastery",
        )
        require(
            resolution_status == "candidate",
            "parent.requirement_status",
            f"{requirement_id} is not an unresolved candidate",
        )

        if "triggering_item_ids" in raw:
            require(
                raw["triggering_item_ids"] == required_items,
                "parent.requirement_legacy_items",
                f"{requirement_id} triggering_item_ids conflict with required_by_item_ids",
            )
        if "status" in raw:
            require(
                raw["status"] == resolution_status,
                "parent.requirement_legacy_status",
                f"{requirement_id} legacy status conflicts with resolution_status",
            )

        rationale = raw.get("rationale")
        legacy_reason = raw.get("reason")
        if isinstance(rationale, str) and rationale.strip():
            rationale = rationale.strip()
            if legacy_reason is not None:
                require(
                    isinstance(legacy_reason, str) and legacy_reason.strip() == rationale,
                    "parent.requirement_legacy_rationale",
                    f"{requirement_id} reason conflicts with rationale",
                )
        elif isinstance(legacy_reason, str) and legacy_reason.strip():
            rationale = legacy_reason.strip()
            actions.append("renamed_legacy_reason_to_rationale")
        else:
            assessment = assessments.get(concept_id)
            require(
                isinstance(assessment, dict),
                "assessment.concept",
                f"no bound concept assessment found for {concept_id}",
            )
            require(
                assessment.get("mastery") == mastery
                or assessment.get("assessment") == mastery,
                "assessment.mastery",
                f"bound concept assessment mastery differs for {concept_id}",
            )
            assessment_rationale = assessment.get("rationale")
            require(
                isinstance(assessment_rationale, str) and assessment_rationale.strip(),
                "assessment.rationale",
                f"bound concept assessment has no rationale for {concept_id}",
            )
            rationale = assessment_rationale.strip()
            actions.append("copied_rationale_from_bound_concept_assessment")

        released_id = raw.get("released_bridge_contract_id")
        require(
            released_id is None,
            "parent.requirement_status",
            f"{requirement_id} already records a released bridge contract",
        )
        if "released_bridge_contract_id" not in raw:
            actions.append("added_null_released_bridge_contract_id")

        removed_legacy = sorted(set(raw) & LEGACY_BRIDGE_REQUIREMENT_FIELDS)
        if removed_legacy:
            actions.append("removed_legacy_fields:" + ",".join(removed_legacy))

        normalized.append({
            "requirement_id": requirement_id,
            "concept_id": concept_id,
            "bridge_candidate_id": candidate_id,
            "required_by_item_ids": list(required_items),
            "learner_mastery": mastery,
            "resolution_status": resolution_status,
            "released_bridge_contract_id": released_id,
            "rationale": rationale,
        })
        actions_by_requirement[requirement_id] = actions

    return normalized, actions_by_requirement


def materialize(
    parent: dict[str, Any],
    catalog: dict[str, Any],
    assessments: dict[str, dict[str, Any]],
    pathway_id: str,
    generated_at: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(parent.get("condition") == "P2", "parent.condition", "parent pathway must be P2")
    require(parent.get("plan_status") == "provisional", "parent.status", "parent pathway must be provisional")
    require(pathway_id != parent.get("pathway_id"), "output.pathway_id", "new pathway ID must differ from parent")
    require(bool(ID_PATTERN.fullmatch(pathway_id)), "output.pathway_id", "new pathway ID has invalid syntax")

    requirements = parent.get("bridge_requirements")
    learning_units = parent.get("learning_units")
    sequence = parent.get("instruction_sequence")
    require(isinstance(requirements, list) and requirements, "parent.requirements", "parent has no bridge requirements")
    require(all(isinstance(item, dict) and item.get("resolution_status") == "candidate" and item.get("released_bridge_contract_id") is None for item in requirements), "parent.requirement_status", "every parent bridge requirement must be unresolved candidate")
    require(isinstance(learning_units, list) and learning_units, "parent.units", "parent learning units are missing")
    require(isinstance(sequence, list) and sequence, "parent.sequence", "parent instruction sequence is missing")
    unit_map = {item.get("unit_id"): item for item in learning_units if isinstance(item, dict)}
    require(len(unit_map) == len(learning_units) and None not in unit_map, "parent.units", "parent units contain invalid or duplicate IDs")
    require(len(sequence) == len(set(sequence)) and set(sequence) == set(unit_map), "parent.sequence", "parent sequence must exactly cover learning units")

    catalog_map = {
        (item.get("concept_id"), item.get("bridge_candidate_id")): item
        for item in catalog["bridges"]
        if isinstance(item, dict)
    }
    plan = deepcopy(parent)
    normalized_requirements, normalization_actions = normalize_bridge_requirements(
        requirements, assessments
    )
    plan["bridge_requirements"] = normalized_requirements
    plan["pathway_id"] = pathway_id
    plan["plan_status"] = "complete"
    plan_units = plan["learning_units"]
    plan_sequence = plan["instruction_sequence"]
    plan_unit_map = {item["unit_id"]: item for item in plan_units}
    original_prerequisites = {
        item["unit_id"]: list(item.get("prerequisite_unit_ids", []))
        for item in plan_units
    }
    resolved: list[dict[str, Any]] = []

    for index, requirement in enumerate(plan["bridge_requirements"], start=1):
        concept_id = requirement.get("concept_id")
        candidate_id = requirement.get("bridge_candidate_id")
        bridge = catalog_map.get((concept_id, candidate_id))
        require(bridge is not None, "catalog.match", f"no released catalog match for {concept_id}/{candidate_id}")
        contract_id = bridge.get("bridge_contract_id")
        require(isinstance(contract_id, str) and contract_id, "catalog.contract_id", f"released contract ID is missing for {concept_id}")
        required_items = set(requirement.get("required_by_item_ids", []))
        consumers = [
            unit_id for unit_id in plan_sequence
            if required_items.intersection(plan_unit_map[unit_id].get("contract_item_ids", []))
        ]
        require(bool(consumers), "placement.consumer", f"no consuming unit found for {concept_id}")
        first_consumer_id = consumers[0]
        first_consumer = plan_unit_map[first_consumer_id]
        bridge_unit_id = f"BRIDGE-{index:03d}"
        require(bridge_unit_id not in plan_unit_map, "placement.unit_id", f"bridge unit ID collision: {bridge_unit_id}")
        bridge_unit = {
            "unit_id": bridge_unit_id,
            "unit_type": "prerequisite_bridge",
            "purpose": f"Prerequisite bridge: {bridge.get('name')}",
            "contract_item_ids": [],
            "bridge_contract_id": contract_id,
            "prerequisite_unit_ids": list(original_prerequisites[first_consumer_id]),
            "learning_goal_ids": ordered_goal_union(plan_sequence, plan_unit_map, required_items),
        }
        unit_position = next(i for i, item in enumerate(plan_units) if item["unit_id"] == first_consumer_id)
        plan_units.insert(unit_position, bridge_unit)
        sequence_position = plan_sequence.index(first_consumer_id)
        plan_sequence.insert(sequence_position, bridge_unit_id)
        plan_unit_map[bridge_unit_id] = bridge_unit
        first_consumer["prerequisite_unit_ids"] = list(first_consumer.get("prerequisite_unit_ids", [])) + [bridge_unit_id]
        requirement["resolution_status"] = "released"
        requirement["released_bridge_contract_id"] = contract_id
        requirement["rationale"] = requirement["rationale"].rstrip() + f" Resolved by released bridge {contract_id} from {catalog['library_id']}."
        resolved_record = {
            "requirement_id": requirement.get("requirement_id"),
            "concept_id": concept_id,
            "bridge_candidate_id": candidate_id,
            "bridge_contract_id": contract_id,
            "bridge_unit_id": bridge_unit_id,
            "first_consumer_unit_id": first_consumer_id,
            "required_by_item_ids": requirement.get("required_by_item_ids"),
        }
        actions = normalization_actions.get(requirement["requirement_id"], [])
        if actions:
            resolved_record["legacy_normalization_actions"] = actions
        resolved.append(resolved_record)

    changes = plan.get("pathway_changes")
    require(isinstance(changes, list), "parent.changes", "parent pathway_changes must be an array")
    require(all(item.get("change_type") != "add_prerequisite_bridge" for item in changes if isinstance(item, dict)), "parent.changes", "parent already declares materialized prerequisite bridges")
    changes.append({
        "change_type": "add_prerequisite_bridge",
        "affected_ids": [item["bridge_contract_id"] for item in resolved],
        "profile_basis": [{
            "profile_field": "missing_or_fragile_prerequisites",
            "evidence": "; ".join(
                f"{item.get('concept_id')}: mastery={item.get('learner_mastery')}"
                for item in parent["bridge_requirements"]
            ),
        }],
        "rationale": "Materialize the previously approved prerequisite requirements from the released bridge catalog before each concept's first consuming Contract unit.",
    })
    summary = plan.get("scope_summary")
    require(isinstance(summary, dict), "parent.summary", "scope_summary is missing")
    summary["released_bridge_count"] = len(resolved)
    plan["generated_by"] = {
        "producer": "released-bridge-pathway-materializer",
        "producer_version": "1.0",
        "method": "released_bridge_materialization",
        "generated_at": generated_at,
    }
    return plan, resolved


def file_binding(path: Path, root: Path) -> dict[str, str]:
    return {"file": display_path(path, root), "sha256": sha256(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--parent-pathway", type=Path, required=True)
    parser.add_argument("--parent-review", type=Path, required=True)
    parser.add_argument("--bridge-catalog", type=Path, required=True)
    parser.add_argument("--bridge-release-report", type=Path, required=True)
    parser.add_argument("--pathway-id", required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    parent_path = args.parent_pathway.resolve()
    review_path = args.parent_review.resolve()
    catalog_path = args.bridge_catalog.resolve()
    release_report_path = args.bridge_release_report.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        print(f"ERROR [output.exists]: refusing to overwrite {output_dir}")
        return 1

    stage: Path | None = None
    try:
        for label, path in (
            ("parent pathway", parent_path),
            ("parent review", review_path),
            ("bridge catalog", catalog_path),
            ("bridge release report", release_report_path),
        ):
            require(path.is_file(), "input.missing", f"missing {label}: {path}")
        generated_at = parse_timestamp(args.generated_at)
        parent = load_object(parent_path)
        review = load_object(review_path)
        catalog = load_object(catalog_path)
        release_report = load_object(release_report_path)
        validate_parent_review(root, parent_path, review_path, parent, review)
        validate_release(root, parent_path, review_path, parent, catalog_path, release_report_path, catalog, release_report)
        assessments = load_bound_concept_assessments(root, parent)
        plan, resolved = materialize(
            parent, catalog, assessments, args.pathway_id, generated_at
        )

        output_dir.parent.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix=".bridge-materialization-stage-", dir=output_dir.parent))
        plan_path = stage / "pathway-plan.json"
        write_object(plan_path, plan)
        final_plan_path = output_dir / "pathway-plan.json"
        receipt = {
            "schema_version": "1.0",
            "materializer": MATERIALIZER,
            "materialized_at": generated_at,
            "rule_id": RULE_ID,
            "parent_pathway": file_binding(parent_path, root),
            "parent_review": file_binding(review_path, root),
            "bridge_catalog": file_binding(catalog_path, root),
            "bridge_release_report": file_binding(release_report_path, root),
            "resolved_bridges": resolved,
            "output_pathway": {
                "file": display_path(final_plan_path, root),
                "sha256": sha256(plan_path),
            },
        }
        write_object(stage / "bridge-resolution-receipt.json", receipt)
        require({path.name for path in stage.iterdir()} == {"pathway-plan.json", "bridge-resolution-receipt.json"}, "output.files", "unexpected staged output")
        os.replace(stage, output_dir)
        stage = None
    except (MaterializationError, OSError, KeyError, TypeError) as exc:
        code = exc.code if isinstance(exc, MaterializationError) else "materialization.io"
        print(f"ERROR [{code}]: {exc}")
        return 1
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)

    print(f"PASS: released bridges materialized to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
