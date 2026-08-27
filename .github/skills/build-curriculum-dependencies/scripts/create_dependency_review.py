#!/usr/bin/env python3
"""Create a pending human-review template bound to a validated dependency candidate."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


ITEM_FIELDS = (
    "hard_dependencies",
    "explanatory_dependencies",
    "implementation_dependencies",
    "co_requisite_item_ids",
    "recommended_neighbours",
    "external_prerequisite_concept_ids",
    "fallback_when_explanatory_dependencies_omitted",
    "rationale_and_confidence",
)
CONCEPT_FIELDS = (
    "need_type",
    "supports_item_ids",
    "bridge_candidate_id",
    "content_boundary_and_rationale",
)


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


def validate_inputs(
    root: Path,
    candidate_path: Path,
    validation_path: Path,
    candidate: dict[str, Any],
    validation: dict[str, Any],
) -> None:
    require(candidate.get("lifecycle_status") == "candidate", "dependency model must be a candidate")
    require(candidate.get("review_status") == "unreviewed", "dependency candidate must be unreviewed")
    require(candidate.get("approval") is None, "dependency candidate must not contain approval")
    require(isinstance(candidate.get("model_id"), str), "candidate model_id is missing")
    require(validation.get("valid") is True, "dependency validation report is not valid")
    require(validation.get("error_count") == 0, "dependency validation report contains errors")

    inputs = validation.get("inputs")
    require(isinstance(inputs, dict), "dependency validation report inputs are missing")
    require(
        resolve_recorded_path(root, inputs.get("candidate")) == candidate_path,
        "validation report identifies a different candidate file",
    )
    candidate_hash = sha256(candidate_path)
    require(
        inputs.get("candidate_sha256") == candidate_hash,
        "candidate changed after deterministic validation; rerun validation",
    )
    source_contract = candidate.get("source_contract")
    require(isinstance(source_contract, dict), "candidate source_contract binding is missing")
    require(
        inputs.get("contract_sha256") == source_contract.get("sha256"),
        "validation report and candidate bind different Frozen Contract hashes",
    )

    items = candidate.get("items")
    require(isinstance(items, list) and items, "candidate must contain dependency items")
    item_ids = [item.get("item_id") for item in items if isinstance(item, dict)]
    require(len(item_ids) == len(items), "candidate contains an invalid item record")
    require(len(item_ids) == len(set(item_ids)), "candidate contains duplicate item IDs")
    concepts = candidate.get("external_prerequisite_concepts")
    require(isinstance(concepts, list), "candidate external prerequisites must be an array")
    concept_ids = [concept.get("concept_id") for concept in concepts if isinstance(concept, dict)]
    require(len(concept_ids) == len(concepts), "candidate contains an invalid concept record")
    require(len(concept_ids) == len(set(concept_ids)), "candidate contains duplicate concept IDs")


def revision_binding(
    root: Path,
    candidate_path: Path,
    validation_path: Path,
    receipt_path: Path | None,
    revision_validation_path: Path | None,
) -> dict[str, str] | None:
    require(
        (receipt_path is None) == (revision_validation_path is None),
        "revision receipt and revision validation report must be supplied together",
    )
    if receipt_path is None or revision_validation_path is None:
        return None
    receipt = load_object(receipt_path)
    revision_validation = load_object(revision_validation_path)
    require(receipt.get("mode") == "revision", "revision receipt mode must be revision")
    require(revision_validation.get("valid") is True, "revision validation report is not valid")
    require(revision_validation.get("error_count") == 0, "revision validation report contains errors")
    inputs = revision_validation.get("inputs")
    require(isinstance(inputs, dict), "revision validation report inputs are missing")
    expected_paths = {
        "revision_receipt": receipt_path,
        "candidate": candidate_path,
        "dependency_validation_report": validation_path,
    }
    for field, expected_path in expected_paths.items():
        require(
            resolve_recorded_path(root, inputs.get(field)) == expected_path,
            f"revision validation report identifies a different {field}",
        )
        require(
            inputs.get(f"{field}_sha256") == sha256(expected_path),
            f"{field} changed after revision validation",
        )
    parent_candidate = receipt.get("parent_candidate")
    parent_review = receipt.get("parent_review")
    require(isinstance(parent_candidate, dict), "revision receipt parent_candidate is missing")
    require(isinstance(parent_review, dict), "revision receipt parent_review is missing")
    return {
        "receipt_file": display_path(receipt_path, root),
        "receipt_sha256": sha256(receipt_path),
        "validation_report_file": display_path(revision_validation_path, root),
        "validation_report_sha256": sha256(revision_validation_path),
        "parent_candidate_sha256": parent_candidate["sha256"],
        "parent_review_sha256": parent_review["sha256"],
    }


def pending_item_review(item_id: str) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "field_decisions": {field: "pending" for field in ITEM_FIELDS},
        "decision": "pending",
        "comment": None,
    }


def pending_concept_review(concept_id: str) -> dict[str, Any]:
    return {
        "concept_id": concept_id,
        "field_decisions": {field: "pending" for field in CONCEPT_FIELDS},
        "decision": "pending",
        "comment": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--validation-report", type=Path, required=True)
    parser.add_argument("--revision-receipt", type=Path)
    parser.add_argument("--revision-validation-report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    candidate_path = args.candidate.resolve()
    validation_path = args.validation_report.resolve()
    receipt_path = args.revision_receipt.resolve() if args.revision_receipt else None
    revision_validation_path = (
        args.revision_validation_report.resolve() if args.revision_validation_report else None
    )
    output_path = args.output.resolve()
    if output_path.exists():
        print(f"ERROR: refusing to overwrite existing review file: {output_path}")
        return 1

    try:
        candidate = load_object(candidate_path)
        validation = load_object(validation_path)
        validate_inputs(root, candidate_path, validation_path, candidate, validation)
        lineage = revision_binding(
            root,
            candidate_path,
            validation_path,
            receipt_path,
            revision_validation_path,
        )
        source_contract = candidate["source_contract"]
        review = {
            "schema_version": "1.0",
            "review_id": f"{candidate['model_id']}-review-v1",
            "review_status": "pending",
            "candidate_binding": {
                "model_id": candidate["model_id"],
                "candidate_file": display_path(candidate_path, root),
                "candidate_sha256": sha256(candidate_path),
                "validation_report_file": display_path(validation_path, root),
                "validation_report_sha256": sha256(validation_path),
                "source_contract_file": source_contract["file"],
                "source_contract_sha256": source_contract["sha256"],
            },
            "template_generator": {
                "agent": "grounded-curriculum-dependency-builder",
                "agent_version": "1.1",
                "skill": "build-curriculum-dependencies",
                "skill_version": "1.1",
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            },
            "revision_binding": lineage,
            "reviewer": {"reviewer_id": None, "reviewer_role": None},
            "item_reviews": [pending_item_review(item["item_id"]) for item in candidate["items"]],
            "external_prerequisite_reviews": [
                pending_concept_review(concept["concept_id"])
                for concept in candidate["external_prerequisite_concepts"]
            ],
            "overall_review": {"decision": "pending", "reviewed_at": None, "comment": None},
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1

    print(f"PASS: pending dependency review template written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
