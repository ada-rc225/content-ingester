#!/usr/bin/env python3
"""Verify a completed P2 review and emit a bounded pathway-revision receipt."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any

from pathway_authorities import (
    AuthorityError,
    display_path,
    load_object,
    resolve_path,
    sha256,
)


FIELD_SETS = {
    "selection_reviews": ("decision_and_role", "rationale_and_profile_basis"),
    "concept_reviews": ("mastery_and_confidence", "evidence_and_rationale", "bridge_requirement"),
    "learning_goal_reviews": ("coverage_and_support", "rationale"),
    "structure_review": (
        "unit_grouping", "instruction_sequence", "prerequisite_relations",
        "unit_purpose_and_learning_goals",
    ),
    "pathway_change_reviews": ("structural_accuracy", "profile_basis", "rationale"),
    "scope_review": (
        "selected_content_scope", "failure_and_convergence_scope",
        "profile_appropriateness",
    ),
}
ID_FIELDS = {
    "selection_reviews": "item_id",
    "concept_reviews": "concept_id",
    "learning_goal_reviews": "capability_id",
    "pathway_change_reviews": "change_index",
}


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise AuthorityError(code, message)


def next_versioned_id(value: str, marker: str) -> str:
    match = re.fullmatch(rf"(.+){re.escape(marker)}([0-9]+)", value)
    return f"{match.group(1)}{marker}{int(match.group(2)) + 1}" if match else f"{value}{marker}1"


def validate_record(
    record: Any,
    fields: tuple[str, ...],
    location: str,
) -> list[str]:
    require(isinstance(record, dict), f"{location}.type", f"{location} must be an object")
    decisions = record.get("field_decisions")
    require(isinstance(decisions, dict) and set(decisions) == set(fields), f"{location}.fields", f"{location} has incorrect field decisions")
    allowed = {"approved", "revision_required", "not_applicable"}
    require(all(value in allowed for value in decisions.values()), f"{location}.pending", f"{location} contains pending or invalid decisions")
    revisions = [field for field in fields if decisions[field] == "revision_required"]
    if record.get("decision") == "approved":
        require(not revisions, f"{location}.decision", f"{location} is approved but contains revision-required fields")
    elif record.get("decision") == "revision_required":
        require(bool(revisions), f"{location}.decision", f"{location} requires revision but marks no fields")
        require(isinstance(record.get("comment"), str) and record["comment"].strip(), f"{location}.comment", f"{location} revision requires an exact change comment")
    else:
        raise AuthorityError(f"{location}.decision", f"{location} decision must be approved or revision_required")
    return revisions


def verify_binding(
    root: Path,
    pathway_path: Path,
    validation_path: Path,
    assessment_path: Path,
    review_path: Path,
    pathway: dict[str, Any],
    assessment: dict[str, Any],
    review: dict[str, Any],
) -> None:
    binding = review.get("candidate_binding")
    require(isinstance(binding, dict), "review.binding", "review candidate binding is missing")
    expected = {
        "pathway_file": pathway_path,
        "validation_report_file": validation_path,
        "assessment_file": assessment_path,
    }
    for field, path in expected.items():
        require(resolve_path(root, binding.get(field)) == path, f"review.{field}.path", f"review identifies another {field}")
        require(binding.get(field.replace("_file", "_sha256")) == sha256(path), f"review.{field}.hash", f"{field} changed after review creation")
    require(binding.get("pathway_id") == pathway.get("pathway_id"), "review.pathway_id", "review binds another pathway ID")
    require(binding.get("assessment_id") == assessment.get("assessment_id"), "review.assessment_id", "review binds another assessment ID")
    profile = pathway.get("profile_binding")
    require(isinstance(profile, dict), "pathway.profile", "pathway profile binding is missing")
    profile_path = resolve_path(root, profile.get("file"))
    require(profile_path is not None and profile_path.is_file(), "pathway.profile_file", "pathway profile is missing")
    require(resolve_path(root, binding.get("profile_file")) == profile_path, "review.profile_path", "review identifies another profile")
    require(binding.get("profile_sha256") == sha256(profile_path), "review.profile_hash", "profile changed after review creation")
    require(binding.get("profile_id") == profile.get("profile_id"), "review.profile_id", "review binds another profile ID")
    validation = load_object(validation_path)
    require(validation.get("valid") is True and validation.get("error_count") == 0, "validation.status", "parent pathway validation did not pass")
    require(resolve_path(root, validation.get("pathway")) == pathway_path, "validation.path", "parent validation identifies another pathway")
    require(validation.get("pathway_sha256") == sha256(pathway_path), "validation.hash", "parent pathway hash is stale")
    require(review_path.is_file(), "review.file", "parent review is missing")


def verify_snapshots(
    pathway: dict[str, Any],
    assessment: dict[str, Any],
    review: dict[str, Any],
) -> None:
    decisions = {entry["item_id"]: entry for entry in pathway["selection"]["decisions"]}
    selection_reviews = review.get("selection_reviews")
    require(isinstance(selection_reviews, list), "review.selection", "selection reviews are missing")
    require([entry.get("item_id") for entry in selection_reviews] == pathway["selection"]["all_contract_item_ids"], "review.selection_coverage", "selection review order or coverage differs from the pathway")
    for entry in selection_reviews:
        source = decisions[entry["item_id"]]
        require(entry.get("planned_decision") == source.get("decision") and entry.get("planned_role") == source.get("selected_role"), "review.selection_snapshot", f"selection snapshot changed for {entry['item_id']}")

    concepts = {entry["concept_id"]: entry for entry in assessment["concept_assessments"]}
    requirements = {entry["concept_id"]: entry for entry in pathway["bridge_requirements"]}
    concept_reviews = review.get("concept_reviews")
    require(isinstance(concept_reviews, list), "review.concepts", "concept reviews are missing")
    require([entry.get("concept_id") for entry in concept_reviews] == list(concepts), "review.concept_coverage", "concept review order or coverage differs from the assessment")
    for entry in concept_reviews:
        concept_id = entry["concept_id"]
        require(entry.get("planned_mastery") == concepts[concept_id]["mastery"], "review.concept_snapshot", f"mastery snapshot changed for {concept_id}")
        require(entry.get("planned_bridge_status") == requirements.get(concept_id, {}).get("resolution_status"), "review.bridge_snapshot", f"bridge snapshot changed for {concept_id}")

    goals = pathway["learning_goal_mappings"]
    goal_reviews = review.get("learning_goal_reviews")
    require(isinstance(goal_reviews, list) and len(goal_reviews) == len(goals), "review.goal_coverage", "learning-goal review coverage differs")
    for source, entry in zip(goals, goal_reviews):
        require(entry.get("capability_id") == source.get("capability_id"), "review.goal_id", "learning-goal review order differs")
        require(entry.get("planned_coverage") == source.get("coverage") and entry.get("planned_supporting_item_ids") == source.get("supporting_item_ids"), "review.goal_snapshot", f"learning-goal snapshot changed for {source['capability_id']}")

    structure = review.get("structure_review")
    require(isinstance(structure, dict), "review.structure", "structure review is missing")
    require(structure.get("instruction_sequence") == pathway.get("instruction_sequence"), "review.sequence_snapshot", "instruction-sequence snapshot changed")
    summaries = structure.get("unit_summaries")
    require(isinstance(summaries, list) and len(summaries) == len(pathway["learning_units"]), "review.unit_snapshot", "unit-summary coverage differs")
    summary_fields = (
        "unit_id", "unit_type", "purpose", "contract_item_ids",
        "prerequisite_unit_ids", "learning_goal_ids",
    )
    for source, summary in zip(pathway["learning_units"], summaries):
        require(all(summary.get(field) == source.get(field) for field in summary_fields), "review.unit_snapshot", f"unit snapshot changed for {source['unit_id']}")

    changes = pathway["pathway_changes"]
    change_reviews = review.get("pathway_change_reviews")
    require(isinstance(change_reviews, list) and len(change_reviews) == len(changes), "review.change_coverage", "pathway-change review coverage differs")
    for index, (source, entry) in enumerate(zip(changes, change_reviews)):
        require(entry.get("change_index") == index and entry.get("change_type") == source.get("change_type") and entry.get("affected_ids") == source.get("affected_ids"), "review.change_snapshot", f"pathway-change snapshot changed at index {index}")

    scope = review.get("scope_review")
    require(isinstance(scope, dict), "review.scope", "scope review is missing")
    require(scope.get("selected_item_ids") == pathway["selection"]["selected_item_ids"], "review.scope_selected", "selected-scope snapshot changed")
    require(scope.get("excluded_item_ids") == pathway["selection"]["excluded_item_ids"], "review.scope_excluded", "excluded-scope snapshot changed")


def collect_scope(review: dict[str, Any]) -> dict[str, Any]:
    scope: dict[str, Any] = {}
    for section in ("selection_reviews", "concept_reviews", "learning_goal_reviews", "pathway_change_reviews"):
        records = review[section]
        collected = []
        for index, record in enumerate(records):
            fields = validate_record(record, FIELD_SETS[section], f"{section}[{index}]")
            if fields:
                collected.append({
                    ID_FIELDS[section]: record[ID_FIELDS[section]],
                    "fields": fields,
                    "comment": record["comment"],
                })
        scope[section] = collected
    for section in ("structure_review", "scope_review"):
        record = review[section]
        fields = validate_record(record, FIELD_SETS[section], section)
        scope[section] = {"fields": fields, "comment": record.get("comment")} if fields else None
    require(
        any(scope[section] for section in scope),
        "review.empty_revision",
        "revision review contains no requested changes",
    )
    return scope


def verify_final_review(review: dict[str, Any]) -> None:
    require(review.get("review_status") == "revision_required", "review.status", "review_status must be revision_required")
    reviewer = review.get("reviewer")
    require(isinstance(reviewer, dict), "review.reviewer", "reviewer is missing")
    require(isinstance(reviewer.get("reviewer_id"), str) and reviewer["reviewer_id"].strip(), "review.reviewer_id", "reviewer_id is required")
    require(isinstance(reviewer.get("reviewer_role"), str) and reviewer["reviewer_role"].strip(), "review.reviewer_role", "reviewer_role is required")
    overall = review.get("overall_review")
    require(isinstance(overall, dict) and overall.get("decision") == "revision_required", "review.overall", "overall decision must be revision_required")
    require(isinstance(overall.get("comment"), str) and overall["comment"].strip(), "review.overall_comment", "overall revision comment is required")
    try:
        datetime.fromisoformat(overall["reviewed_at"].replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise AuthorityError("review.reviewed_at", "overall reviewed_at must be ISO-8601") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--parent-pathway", type=Path, required=True)
    parser.add_argument("--parent-validation-report", type=Path, required=True)
    parser.add_argument("--parent-assessment", type=Path, required=True)
    parser.add_argument("--parent-review", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(args.workspace_root).resolve()
    pathway_path = args.parent_pathway.resolve()
    validation_path = args.parent_validation_report.resolve()
    assessment_path = args.parent_assessment.resolve()
    review_path = args.parent_review.resolve()
    output_path = args.output.resolve()
    if output_path.exists():
        print(f"ERROR [output.exists]: refusing to overwrite revision receipt: {output_path}")
        return 1
    if output_path.parent == pathway_path.parent:
        print("ERROR [output.parent]: revision output directory must differ from the parent directory")
        return 1
    try:
        pathway = load_object(pathway_path)
        assessment = load_object(assessment_path)
        review = load_object(review_path)
        verify_binding(root, pathway_path, validation_path, assessment_path, review_path, pathway, assessment, review)
        verify_snapshots(pathway, assessment, review)
        verify_final_review(review)
        revision_scope = collect_scope(review)
        receipt = {
            "schema_version": "1.0",
            "mode": "revision",
            "parent_pathway": {
                "pathway_id": pathway["pathway_id"],
                "next_pathway_id": next_versioned_id(pathway["pathway_id"], "-revision-v"),
                "file": display_path(pathway_path, root),
                "sha256": sha256(pathway_path),
                "validation_report_file": display_path(validation_path, root),
                "validation_report_sha256": sha256(validation_path),
            },
            "parent_assessment": {
                "assessment_id": assessment["assessment_id"],
                "next_assessment_id": next_versioned_id(assessment["assessment_id"], "-v"),
                "file": display_path(assessment_path, root),
                "sha256": sha256(assessment_path),
            },
            "parent_review": {
                "review_id": review["review_id"],
                "file": display_path(review_path, root),
                "sha256": sha256(review_path),
                "reviewer_id": review["reviewer"]["reviewer_id"],
                "reviewer_role": review["reviewer"]["reviewer_role"],
                "reviewed_at": review["overall_review"]["reviewed_at"],
            },
            "revision_scope": revision_scope,
            "overall_comment": review["overall_review"]["comment"],
            "constraints": {
                "preserve_unmarked_fields": True,
                "require_new_output_directory": True,
                "require_new_pathway_and_assessment_ids": True,
                "do_not_inherit_human_approval": True,
                "do_not_add_time_limits_or_unit_time_fields": True,
                "word_count_control_deferred_to_composer": True,
            },
            "generated_by": {
                "agent": "adaptive-curriculum-pathway-planner",
                "agent_version": "1.1",
                "skill": "plan-adaptive-curriculum-pathways",
                "skill_version": "1.1",
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            },
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except (AuthorityError, OSError, KeyError, TypeError, ValueError) as exc:
        code = exc.code if isinstance(exc, AuthorityError) else "revision.input"
        print(f"ERROR [{code}]: {exc}")
        return 1
    print(f"PASS: bounded pathway revision receipt written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
