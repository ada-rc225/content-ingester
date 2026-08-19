#!/usr/bin/env python3
"""Create a fully pending human-review template for one validated P2 pathway plan."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from pathway_authorities import (
    AuthorityError,
    display_path,
    load_object,
    resolve_path,
    sha256,
)


SELECTION_FIELDS = ("decision_and_role", "rationale_and_profile_basis")
CONCEPT_FIELDS = ("mastery_and_confidence", "evidence_and_rationale", "bridge_requirement")
GOAL_FIELDS = ("coverage_and_support", "rationale")
STRUCTURE_FIELDS = (
    "unit_grouping", "instruction_sequence", "prerequisite_relations",
    "unit_purpose_and_learning_goals",
)
CHANGE_FIELDS = ("structural_accuracy", "profile_basis", "rationale")
SCOPE_FIELDS = (
    "selected_content_scope", "failure_and_convergence_scope",
    "profile_appropriateness",
)


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise AuthorityError(code, message)


def pending_fields(fields: tuple[str, ...]) -> dict[str, str]:
    return {field: "pending" for field in fields}


def verify_inputs(
    root: Path,
    pathway_path: Path,
    validation_path: Path,
    assessment_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Path, dict[str, Any]]:
    pathway = load_object(pathway_path)
    validation = load_object(validation_path)
    assessment = load_object(assessment_path)
    require(pathway.get("condition") == "P2", "pathway.condition", "review templates are only for P2 plans")
    require(validation.get("valid") is True and validation.get("error_count") == 0, "validation.status", "pathway validation did not pass")
    require(resolve_path(root, validation.get("pathway")) == pathway_path, "validation.path", "validation report identifies another pathway")
    require(validation.get("pathway_sha256") == sha256(pathway_path), "validation.hash", "pathway changed after validation")

    assessment_binding = pathway.get("profile_concept_assessment_binding")
    require(isinstance(assessment_binding, dict), "pathway.assessment", "pathway concept-assessment binding is missing")
    require(resolve_path(root, assessment_binding.get("file")) == assessment_path, "assessment.path", "pathway identifies another concept assessment")
    require(assessment_binding.get("sha256") == sha256(assessment_path), "assessment.hash", "concept assessment changed after pathway generation")
    require(assessment_binding.get("artifact_id") == assessment.get("assessment_id"), "assessment.id", "concept assessment ID differs from pathway binding")

    profile_binding = pathway.get("profile_binding")
    require(isinstance(profile_binding, dict), "pathway.profile", "pathway profile binding is missing")
    profile_path = resolve_path(root, profile_binding.get("file"))
    require(profile_path is not None and profile_path.is_file(), "profile.file", "bound learner profile is missing")
    profile = load_object(profile_path)
    require(profile_binding.get("sha256") == sha256(profile_path), "profile.hash", "learner profile hash is stale")
    require(profile_binding.get("profile_id") == profile.get("profile_id"), "profile.id", "learner profile ID differs")

    reference = pathway.get("source_authorities", {}).get("reference_contract")
    require(isinstance(reference, dict), "pathway.contract", "pathway reference-Contract binding is missing")
    contract_path = resolve_path(root, reference.get("file"))
    require(contract_path is not None and contract_path.is_file(), "contract.file", "bound Frozen Contract is missing")
    require(reference.get("sha256") == sha256(contract_path), "contract.hash", "Frozen Contract hash is stale")
    contract = load_object(contract_path)
    return pathway, validation, assessment, profile_path, contract


def revision_lineage(
    root: Path,
    pathway_path: Path,
    validation_path: Path,
    receipt_path: Path | None,
    revision_validation_path: Path | None,
) -> dict[str, str] | None:
    require(
        (receipt_path is None) == (revision_validation_path is None),
        "revision.inputs",
        "revision receipt and revision validation report must be supplied together",
    )
    if receipt_path is None or revision_validation_path is None:
        return None
    receipt = load_object(receipt_path)
    revision_validation = load_object(revision_validation_path)
    require(receipt.get("mode") == "revision", "revision.receipt", "revision receipt mode is invalid")
    require(revision_validation.get("valid") is True and revision_validation.get("error_count") == 0, "revision.validation", "revision-scope validation did not pass")
    inputs = revision_validation.get("inputs")
    require(isinstance(inputs, dict), "revision.validation_inputs", "revision validation inputs are missing")
    for field, path in (
        ("revision_receipt", receipt_path),
        ("candidate_pathway", pathway_path),
        ("candidate_validation_report", validation_path),
    ):
        require(resolve_path(root, inputs.get(field)) == path, f"revision.{field}.path", f"revision validation identifies another {field}")
        require(inputs.get(f"{field}_sha256") == sha256(path), f"revision.{field}.hash", f"{field} changed after revision validation")
    return {
        "receipt_file": display_path(receipt_path, root),
        "receipt_sha256": sha256(receipt_path),
        "validation_report_file": display_path(revision_validation_path, root),
        "validation_report_sha256": sha256(revision_validation_path),
        "parent_pathway_sha256": receipt["parent_pathway"]["sha256"],
        "parent_review_sha256": receipt["parent_review"]["sha256"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--pathway", type=Path, required=True)
    parser.add_argument("--validation-report", type=Path, required=True)
    parser.add_argument("--assessment", type=Path, required=True)
    parser.add_argument("--revision-receipt", type=Path)
    parser.add_argument("--revision-validation-report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(args.workspace_root).resolve()
    pathway_path = args.pathway.resolve()
    validation_path = args.validation_report.resolve()
    assessment_path = args.assessment.resolve()
    output_path = args.output.resolve()
    if output_path.exists():
        print(f"ERROR [output.exists]: refusing to overwrite review: {output_path}")
        return 1
    try:
        pathway, _, assessment, profile_path, contract = verify_inputs(
            root, pathway_path, validation_path, assessment_path
        )
        lineage = revision_lineage(
            root,
            pathway_path,
            validation_path,
            args.revision_receipt.resolve() if args.revision_receipt else None,
            args.revision_validation_report.resolve() if args.revision_validation_report else None,
        )
        contract_map = {
            item["item_id"]: item for item in contract["contract_items"]
        }
        decision_map = {
            decision["item_id"]: decision
            for decision in pathway["selection"]["decisions"]
        }
        requirement_map = {
            requirement["concept_id"]: requirement
            for requirement in pathway["bridge_requirements"]
        }
        review = {
            "schema_version": "1.0",
            "review_id": f"{pathway['pathway_id']}-review-v1",
            "review_status": "pending",
            "candidate_binding": {
                "pathway_id": pathway["pathway_id"],
                "pathway_file": display_path(pathway_path, root),
                "pathway_sha256": sha256(pathway_path),
                "validation_report_file": display_path(validation_path, root),
                "validation_report_sha256": sha256(validation_path),
                "assessment_id": assessment["assessment_id"],
                "assessment_file": display_path(assessment_path, root),
                "assessment_sha256": sha256(assessment_path),
                "profile_id": pathway["profile_binding"]["profile_id"],
                "profile_file": display_path(profile_path, root),
                "profile_sha256": sha256(profile_path),
            },
            "template_generator": {
                "agent": "adaptive-curriculum-pathway-planner",
                "agent_version": "1.1",
                "skill": "plan-adaptive-curriculum-pathways",
                "skill_version": "1.1",
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            },
            "revision_binding": lineage,
            "reviewer": {"reviewer_id": None, "reviewer_role": None},
            "selection_reviews": [
                {
                    "item_id": item_id,
                    "item_type": contract_map[item_id]["item_type"],
                    "criticality": contract_map[item_id]["criticality"],
                    "planned_decision": decision_map[item_id]["decision"],
                    "planned_role": decision_map[item_id]["selected_role"],
                    "field_decisions": pending_fields(SELECTION_FIELDS),
                    "decision": "pending",
                    "comment": None,
                }
                for item_id in pathway["selection"]["all_contract_item_ids"]
            ],
            "concept_reviews": [
                {
                    "concept_id": concept["concept_id"],
                    "planned_mastery": concept["mastery"],
                    "planned_bridge_status": requirement_map.get(concept["concept_id"], {}).get("resolution_status"),
                    "field_decisions": pending_fields(CONCEPT_FIELDS),
                    "decision": "pending",
                    "comment": None,
                }
                for concept in assessment["concept_assessments"]
            ],
            "learning_goal_reviews": [
                {
                    "capability_id": goal["capability_id"],
                    "planned_coverage": goal["coverage"],
                    "planned_supporting_item_ids": goal["supporting_item_ids"],
                    "field_decisions": pending_fields(GOAL_FIELDS),
                    "decision": "pending",
                    "comment": None,
                }
                for goal in pathway["learning_goal_mappings"]
            ],
            "structure_review": {
                "instruction_sequence": pathway["instruction_sequence"],
                "unit_summaries": [
                    {
                        "unit_id": unit["unit_id"],
                        "unit_type": unit["unit_type"],
                        "purpose": unit["purpose"],
                        "contract_item_ids": unit["contract_item_ids"],
                        "prerequisite_unit_ids": unit["prerequisite_unit_ids"],
                        "learning_goal_ids": unit["learning_goal_ids"],
                    }
                    for unit in pathway["learning_units"]
                ],
                "field_decisions": pending_fields(STRUCTURE_FIELDS),
                "decision": "pending",
                "comment": None,
            },
            "pathway_change_reviews": [
                {
                    "change_index": index,
                    "change_type": change["change_type"],
                    "affected_ids": change["affected_ids"],
                    "field_decisions": pending_fields(CHANGE_FIELDS),
                    "decision": "pending",
                    "comment": None,
                }
                for index, change in enumerate(pathway["pathway_changes"])
            ],
            "scope_review": {
                "selected_item_ids": pathway["selection"]["selected_item_ids"],
                "excluded_item_ids": pathway["selection"]["excluded_item_ids"],
                "failure_or_convergence_item_ids": [
                    item_id
                    for item_id in pathway["selection"]["selected_item_ids"]
                    if contract_map[item_id]["item_type"] in {
                        "failure_condition", "convergence_result", "assumption"
                    }
                ],
                "field_decisions": pending_fields(SCOPE_FIELDS),
                "decision": "pending",
                "comment": None,
            },
            "overall_review": {
                "decision": "pending",
                "reviewed_at": None,
                "comment": None,
            },
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
    except (AuthorityError, OSError, KeyError, TypeError, ValueError) as exc:
        code = exc.code if isinstance(exc, AuthorityError) else "review.input"
        print(f"ERROR [{code}]: {exc}")
        return 1
    print(f"PASS: pending pathway review written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
