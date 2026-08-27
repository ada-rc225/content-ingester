#!/usr/bin/env python3
"""Verify a finalized revision review and emit a bounded dependency-revision receipt."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any

import validate_dependency_model as dependency_validator


ITEM_REVIEW_FIELDS = (
    "hard_dependencies",
    "explanatory_dependencies",
    "implementation_dependencies",
    "co_requisite_item_ids",
    "recommended_neighbours",
    "external_prerequisite_concept_ids",
    "fallback_when_explanatory_dependencies_omitted",
    "rationale_and_confidence",
)
CONCEPT_REVIEW_FIELDS = (
    "need_type",
    "supports_item_ids",
    "bridge_candidate_id",
    "content_boundary_and_rationale",
)
MODEL_ID_RE = re.compile(r"^(?P<prefix>[a-z0-9]+(?:-[a-z0-9]+)*-dependencies)-v(?P<version>[0-9]+)$")


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_recorded_path(root: Path, raw_path: Any) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        return None
    path = Path(raw_path)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def next_model_id(model_id: str) -> str:
    match = MODEL_ID_RE.fullmatch(model_id)
    require(match is not None, "parent candidate model_id is invalid")
    return f"{match.group('prefix')}-v{int(match.group('version')) + 1}"


def verify_parent_candidate(
    root: Path,
    contract_path: Path,
    candidate_path: Path,
    candidate: dict[str, Any],
) -> None:
    errors: list[dict[str, str]] = []
    contract = load_object(contract_path)
    contract_hash = dependency_validator.release_errors(root, contract_path, contract, errors)
    dependency_validator.validate_candidate_shape(candidate, errors)
    dependency_validator.validate_semantics(
        root,
        contract_path,
        contract,
        contract_hash,
        candidate,
        errors,
    )
    if errors:
        detail = "; ".join(f"{entry['code']}: {entry['message']}" for entry in errors)
        raise ValueError(f"parent dependency candidate is invalid: {detail}")


def verify_review_binding(
    root: Path,
    contract_path: Path,
    candidate_path: Path,
    candidate: dict[str, Any],
    review: dict[str, Any],
) -> tuple[Path, dict[str, Any]]:
    binding = review.get("candidate_binding")
    require(isinstance(binding, dict), "review candidate_binding is missing")
    require(binding.get("model_id") == candidate.get("model_id"), "review binds another model_id")
    require(
        resolve_recorded_path(root, binding.get("candidate_file")) == candidate_path,
        "review identifies a different parent candidate file",
    )
    require(binding.get("candidate_sha256") == sha256(candidate_path), "parent candidate hash does not match review")
    require(
        resolve_recorded_path(root, binding.get("source_contract_file")) == contract_path,
        "review identifies a different Frozen Contract",
    )
    require(binding.get("source_contract_sha256") == sha256(contract_path), "Frozen Contract hash does not match review")

    validation_path = resolve_recorded_path(root, binding.get("validation_report_file"))
    require(validation_path is not None and validation_path.is_file(), "parent validation report is missing")
    require(binding.get("validation_report_sha256") == sha256(validation_path), "parent validation report hash does not match review")
    validation = load_object(validation_path)
    require(validation.get("valid") is True and validation.get("error_count") == 0, "parent validation did not pass")
    inputs = validation.get("inputs")
    require(isinstance(inputs, dict), "parent validation inputs are missing")
    require(resolve_recorded_path(root, inputs.get("candidate")) == candidate_path, "parent validation identifies another candidate")
    require(inputs.get("candidate_sha256") == sha256(candidate_path), "parent validation candidate hash is stale")
    require(resolve_recorded_path(root, inputs.get("contract")) == contract_path, "parent validation identifies another Contract")
    require(inputs.get("contract_sha256") == sha256(contract_path), "parent validation Contract hash is stale")
    return validation_path, validation


def validate_record_review(
    record: dict[str, Any],
    identifier_field: str,
    expected_fields: tuple[str, ...],
    location: str,
) -> list[str]:
    identifier = record.get(identifier_field)
    require(isinstance(identifier, str) and identifier, f"{location}.{identifier_field} is missing")
    decisions = record.get("field_decisions")
    require(isinstance(decisions, dict), f"{location}.field_decisions is missing")
    require(set(decisions) == set(expected_fields), f"{location}.field_decisions has the wrong fields")
    allowed = {"approved", "revision_required", "not_applicable"}
    require(all(value in allowed for value in decisions.values()), f"{location} contains pending or invalid field decisions")
    revision_fields = [field for field in expected_fields if decisions[field] == "revision_required"]
    decision = record.get("decision")
    if decision == "approved":
        require(not revision_fields, f"{location} is approved but contains revision-required fields")
    elif decision == "revision_required":
        require(bool(revision_fields), f"{location} requires revision but identifies no revision fields")
        require(isinstance(record.get("comment"), str) and record["comment"].strip(), f"{location} revision requires a comment")
    else:
        raise ValueError(f"{location}.decision must be approved or revision_required")
    return revision_fields


def collect_revision_scope(
    candidate: dict[str, Any], review: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidate_item_ids = [item.get("item_id") for item in candidate.get("items", [])]
    item_reviews = review.get("item_reviews")
    require(isinstance(item_reviews, list), "review item_reviews must be an array")
    review_item_ids = [record.get("item_id") for record in item_reviews if isinstance(record, dict)]
    require(review_item_ids == candidate_item_ids, "review item order and coverage must match the parent candidate")

    candidate_item_map = {
        item.get("item_id"): item for item in candidate.get("items", []) if isinstance(item, dict)
    }
    item_changes: list[dict[str, Any]] = []
    for index, record in enumerate(item_reviews):
        require(isinstance(record, dict), f"item_reviews[{index}] must be an object")
        fields = validate_record_review(record, "item_id", ITEM_REVIEW_FIELDS, f"item_reviews[{index}]")
        source_item = candidate_item_map[record["item_id"]]
        for field, decision in record["field_decisions"].items():
            if decision != "not_applicable":
                continue
            if field == "fallback_when_explanatory_dependencies_omitted":
                require(
                    source_item.get("explanatory_dependencies") == [],
                    f"item_reviews[{index}].{field} may be not_applicable only when explanatory_dependencies is empty",
                )
                continue
            require(
                field in {
                    "hard_dependencies", "explanatory_dependencies",
                    "implementation_dependencies", "co_requisite_item_ids",
                    "recommended_neighbours", "external_prerequisite_concept_ids",
                } and source_item.get(field) == [],
                f"item_reviews[{index}].{field} may be not_applicable only for an empty relationship array",
            )
        if fields:
            item_changes.append({"item_id": record["item_id"], "fields": fields, "comment": record["comment"]})

    candidate_concept_ids = [
        concept.get("concept_id") for concept in candidate.get("external_prerequisite_concepts", [])
    ]
    concept_reviews = review.get("external_prerequisite_reviews")
    require(isinstance(concept_reviews, list), "review external_prerequisite_reviews must be an array")
    review_concept_ids = [record.get("concept_id") for record in concept_reviews if isinstance(record, dict)]
    require(review_concept_ids == candidate_concept_ids, "review concept order and coverage must match the parent candidate")

    concept_changes: list[dict[str, Any]] = []
    for index, record in enumerate(concept_reviews):
        require(isinstance(record, dict), f"external_prerequisite_reviews[{index}] must be an object")
        fields = validate_record_review(
            record,
            "concept_id",
            CONCEPT_REVIEW_FIELDS,
            f"external_prerequisite_reviews[{index}]",
        )
        require(
            all(value != "not_applicable" for value in record["field_decisions"].values()),
            f"external_prerequisite_reviews[{index}] fields cannot be not_applicable for an existing concept",
        )
        if fields:
            concept_changes.append(
                {
                    "concept_id": record["concept_id"],
                    "fields": fields,
                    "record_removal_allowed": set(fields) == set(CONCEPT_REVIEW_FIELDS),
                    "comment": record["comment"],
                }
            )
    require(item_changes or concept_changes, "revision review contains no requested field changes")
    return item_changes, concept_changes


def verify_final_review(review: dict[str, Any]) -> None:
    require(review.get("review_status") == "revision_required", "review_status must be revision_required")
    reviewer = review.get("reviewer")
    require(isinstance(reviewer, dict), "reviewer is missing")
    require(isinstance(reviewer.get("reviewer_id"), str) and reviewer["reviewer_id"].strip(), "reviewer_id is required")
    require(isinstance(reviewer.get("reviewer_role"), str) and reviewer["reviewer_role"].strip(), "reviewer_role is required")
    overall = review.get("overall_review")
    require(isinstance(overall, dict), "overall_review is missing")
    require(overall.get("decision") == "revision_required", "overall review decision must be revision_required")
    require(isinstance(overall.get("comment"), str) and overall["comment"].strip(), "overall revision comment is required")
    reviewed_at = overall.get("reviewed_at")
    try:
        datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ValueError("overall_review.reviewed_at must be an ISO 8601 date-time") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--parent-candidate", type=Path, required=True)
    parser.add_argument("--parent-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    contract_path = args.contract.resolve()
    candidate_path = args.parent_candidate.resolve()
    review_path = args.parent_review.resolve()
    output_path = args.output.resolve()
    if output_path.exists():
        print(f"ERROR: refusing to overwrite existing revision receipt: {output_path}")
        return 1
    if output_path.parent == candidate_path.parent:
        print("ERROR: revision output directory must differ from the parent candidate directory")
        return 1
    if (output_path.parent / "contract-dependencies.json").exists():
        print("ERROR: revision output directory already contains a dependency candidate")
        return 1

    try:
        candidate = load_object(candidate_path)
        review = load_object(review_path)
        verify_parent_candidate(root, contract_path, candidate_path, candidate)
        validation_path, _ = verify_review_binding(root, contract_path, candidate_path, candidate, review)
        verify_final_review(review)
        item_changes, concept_changes = collect_revision_scope(candidate, review)
        receipt = {
            "schema_version": "1.0",
            "mode": "revision",
            "source_contract": {
                "file": display_path(contract_path, root),
                "sha256": sha256(contract_path),
            },
            "parent_candidate": {
                "model_id": candidate["model_id"],
                "next_model_id": next_model_id(candidate["model_id"]),
                "file": display_path(candidate_path, root),
                "sha256": sha256(candidate_path),
                "validation_report_file": display_path(validation_path, root),
                "validation_report_sha256": sha256(validation_path),
            },
            "parent_review": {
                "review_id": review.get("review_id"),
                "file": display_path(review_path, root),
                "sha256": sha256(review_path),
                "decision": "revision_required",
                "reviewer_id": review["reviewer"]["reviewer_id"],
                "reviewer_role": review["reviewer"]["reviewer_role"],
                "reviewed_at": review["overall_review"]["reviewed_at"],
            },
            "revision_scope": {
                "item_changes": item_changes,
                "concept_changes": concept_changes,
                "overall_comment": review["overall_review"]["comment"],
            },
            "constraints": {
                "preserve_unmarked_fields": True,
                "require_next_model_version": True,
                "reset_candidate_review_state": True,
                "allow_new_external_concepts_only_from_revised_item_fields": True,
                "inherit_prior_approvals": False,
            },
            "generated_by": {
                "agent": "grounded-curriculum-dependency-builder",
                "agent_version": "1.1",
                "skill": "build-curriculum-dependencies",
                "skill_version": "1.1",
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            },
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"PASS: revision scope verified; receipt written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
