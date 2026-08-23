#!/usr/bin/env python3
"""Validate that a revised P2 assessment and pathway stay within reviewed scope."""

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


class RevisionValidator:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors: list[dict[str, str]] = []

    def error(self, code: str, message: str) -> None:
        self.errors.append({"code": code, "message": message})

    def check(self, condition: bool, code: str, message: str) -> None:
        if not condition:
            self.error(code, message)

    def compare_fields(
        self,
        parent: dict[str, Any],
        child: dict[str, Any],
        fields: tuple[str, ...],
        code: str,
    ) -> None:
        for field in fields:
            if parent.get(field) != child.get(field):
                self.error(code, f"unreviewed field changed: {field}")

    @staticmethod
    def scoped_map(records: list[dict[str, Any]], id_field: str) -> dict[Any, set[str]]:
        return {
            record[id_field]: set(record["fields"])
            for record in records
        }

    def validate(
        self,
        receipt_path: Path,
        candidate_path: Path,
        candidate_assessment_path: Path,
        candidate_validation_path: Path,
    ) -> dict[str, Any]:
        receipt = load_object(receipt_path)
        self.check(receipt.get("mode") == "revision", "receipt.mode", "receipt mode must be revision")
        parent_binding = receipt.get("parent_pathway")
        assessment_binding = receipt.get("parent_assessment")
        review_binding = receipt.get("parent_review")
        if not all(isinstance(value, dict) for value in (parent_binding, assessment_binding, review_binding)):
            self.error("receipt.bindings", "revision receipt parent bindings are missing")
            return receipt
        parent_path = resolve_path(self.root, parent_binding.get("file"))
        parent_assessment_path = resolve_path(self.root, assessment_binding.get("file"))
        review_path = resolve_path(self.root, review_binding.get("file"))
        for label, path, expected_hash in (
            ("parent_pathway", parent_path, parent_binding.get("sha256")),
            ("parent_assessment", parent_assessment_path, assessment_binding.get("sha256")),
            ("parent_review", review_path, review_binding.get("sha256")),
        ):
            if path is None or not path.is_file():
                self.error(f"{label}.file", f"{label} is missing")
            elif expected_hash != sha256(path):
                self.error(f"{label}.hash", f"{label} changed after revision authorization")
        if self.errors:
            return receipt

        parent = load_object(parent_path)  # type: ignore[arg-type]
        parent_assessment = load_object(parent_assessment_path)  # type: ignore[arg-type]
        child = load_object(candidate_path)
        child_assessment = load_object(candidate_assessment_path)
        validation = load_object(candidate_validation_path)
        self.check(validation.get("valid") is True and validation.get("error_count") == 0, "candidate.validation", "candidate unified validation did not pass")
        self.check(resolve_path(self.root, validation.get("pathway")) == candidate_path, "candidate.validation_path", "candidate validation identifies another pathway")
        self.check(validation.get("pathway_sha256") == sha256(candidate_path), "candidate.validation_hash", "candidate pathway changed after validation")
        self.check(child.get("pathway_id") == parent_binding.get("next_pathway_id"), "candidate.pathway_id", "candidate pathway_id differs from authorized next ID")
        self.check(child_assessment.get("assessment_id") == assessment_binding.get("next_assessment_id"), "candidate.assessment_id", "candidate assessment_id differs from authorized next ID")
        child_assessment_binding = child.get("profile_concept_assessment_binding")
        self.check(isinstance(child_assessment_binding, dict), "candidate.assessment_binding", "candidate pathway assessment binding is missing")
        if isinstance(child_assessment_binding, dict):
            self.check(resolve_path(self.root, child_assessment_binding.get("file")) == candidate_assessment_path, "candidate.assessment_path", "candidate pathway identifies another assessment")
            self.check(child_assessment_binding.get("sha256") == sha256(candidate_assessment_path), "candidate.assessment_hash", "candidate pathway assessment hash is stale")
            self.check(child_assessment_binding.get("artifact_id") == child_assessment.get("assessment_id"), "candidate.assessment_binding_id", "candidate assessment binding ID differs")

        immutable_plan_fields = (
            "schema_version", "condition", "topic", "source_authorities",
            "profile_binding", "learning_request_binding", "baseline_pathway_binding",
            "selection_authority", "rendering_policy",
        )
        self.compare_fields(parent, child, immutable_plan_fields, "scope.plan_immutable")
        self.check(child.get("generated_by", {}).get("producer") == "adaptive-curriculum-pathway-planner", "candidate.producer", "candidate producer is invalid")
        self.check(child.get("generated_by", {}).get("producer_version") == "1.1", "candidate.producer_version", "revised pathway producer_version must be 1.1")
        self.check(child.get("generated_by", {}).get("method") == "adaptive_pathway_planning", "candidate.method", "revised pathway method is invalid")

        immutable_assessment_fields = (
            "schema_version", "profile_binding",
            "curriculum_model_binding",
        )
        self.compare_fields(parent_assessment, child_assessment, immutable_assessment_fields, "scope.assessment_immutable")
        # A revision creates a new, unreviewed assessment artifact. Its lifecycle
        # status must therefore reset to ``provisional`` even when the parent uses
        # a legacy status such as ``pending`` or ``pilot_candidate``. Treating the
        # status as immutable would make those legacy parents impossible to
        # revise: preserving the status and resetting it could not both pass.
        self.check(child_assessment.get("assessment_status") == "provisional", "candidate.assessment_status", "revision must not claim reviewed assessment status")
        self.check(child_assessment.get("generated_by", {}).get("producer_version") == "1.1", "candidate.assessment_version", "revised assessment producer_version must be 1.1")

        scope = receipt.get("revision_scope")
        if not isinstance(scope, dict):
            self.error("receipt.scope", "revision scope is missing")
            return receipt
        self.validate_selection(parent, child, scope)
        self.validate_assessment(parent_assessment, child_assessment, scope)
        self.validate_goals(parent, child, scope)
        self.validate_structure(parent, child, scope)
        self.validate_bridges(parent, child, scope)
        self.validate_changes(parent, child, scope)
        self.validate_scope_summary(parent, child, scope)
        return receipt

    def validate_selection(self, parent: dict[str, Any], child: dict[str, Any], scope: dict[str, Any]) -> None:
        allowed = self.scoped_map(scope.get("selection_reviews", []), "item_id")
        psel, csel = parent["selection"], child["selection"]
        self.check(psel.get("all_contract_item_ids") == csel.get("all_contract_item_ids"), "scope.selection_all", "all_contract_item_ids changed")
        pmap = {entry["item_id"]: entry for entry in psel["decisions"]}
        cmap = {entry["item_id"]: entry for entry in csel["decisions"]}
        self.check(set(pmap) == set(cmap), "scope.selection_coverage", "selection decision coverage changed")
        for item_id in set(pmap) & set(cmap):
            fields = allowed.get(item_id, set())
            if "decision_and_role" not in fields:
                self.compare_fields(pmap[item_id], cmap[item_id], ("decision", "selected_role"), "scope.selection_decision")
            if "rationale_and_profile_basis" not in fields:
                self.compare_fields(pmap[item_id], cmap[item_id], ("rationale", "profile_basis"), "scope.selection_rationale")
        if not any("decision_and_role" in fields for fields in allowed.values()):
            self.check(psel.get("selected_item_ids") == csel.get("selected_item_ids"), "scope.selected_ids", "selected_item_ids changed without review")
            self.check(psel.get("excluded_item_ids") == csel.get("excluded_item_ids"), "scope.excluded_ids", "excluded_item_ids changed without review")

    def validate_assessment(self, parent: dict[str, Any], child: dict[str, Any], scope: dict[str, Any]) -> None:
        allowed = self.scoped_map(scope.get("concept_reviews", []), "concept_id")
        pmap = {entry["concept_id"]: entry for entry in parent["concept_assessments"]}
        cmap = {entry["concept_id"]: entry for entry in child["concept_assessments"]}
        self.check(set(pmap) == set(cmap), "scope.concept_coverage", "concept-assessment coverage changed")
        for concept_id in set(pmap) & set(cmap):
            self.check(pmap[concept_id].get("concept_name") == cmap[concept_id].get("concept_name"), "scope.concept_name", f"concept name changed for {concept_id}")
            fields = allowed.get(concept_id, set())
            if "mastery_and_confidence" not in fields:
                self.compare_fields(pmap[concept_id], cmap[concept_id], ("mastery", "confidence"), "scope.concept_mastery")
            if "evidence_and_rationale" not in fields:
                self.compare_fields(pmap[concept_id], cmap[concept_id], ("profile_evidence", "rationale"), "scope.concept_evidence")

    def validate_goals(self, parent: dict[str, Any], child: dict[str, Any], scope: dict[str, Any]) -> None:
        allowed = self.scoped_map(scope.get("learning_goal_reviews", []), "capability_id")
        pmap = {entry["capability_id"]: entry for entry in parent["learning_goal_mappings"]}
        cmap = {entry["capability_id"]: entry for entry in child["learning_goal_mappings"]}
        self.check(set(pmap) == set(cmap), "scope.goal_coverage", "learning-goal coverage changed")
        for goal_id in set(pmap) & set(cmap):
            fields = allowed.get(goal_id, set())
            if "coverage_and_support" not in fields:
                self.compare_fields(pmap[goal_id], cmap[goal_id], ("coverage", "supporting_item_ids"), "scope.goal_support")
            if "rationale" not in fields:
                self.compare_fields(pmap[goal_id], cmap[goal_id], ("rationale",), "scope.goal_rationale")

    def validate_structure(self, parent: dict[str, Any], child: dict[str, Any], scope: dict[str, Any]) -> None:
        record = scope.get("structure_review")
        allowed = set(record.get("fields", [])) if isinstance(record, dict) else set()
        p_units, c_units = parent["learning_units"], child["learning_units"]
        pmap = {entry["unit_id"]: entry for entry in p_units}
        cmap = {entry["unit_id"]: entry for entry in c_units}
        if set(pmap) != set(cmap):
            required = {
                "unit_grouping", "instruction_sequence", "prerequisite_relations",
                "unit_purpose_and_learning_goals",
            }
            self.check(required.issubset(allowed), "scope.unit_set", "changing unit IDs requires review of every structure field")
        else:
            for unit_id in pmap:
                if "unit_grouping" not in allowed:
                    self.compare_fields(pmap[unit_id], cmap[unit_id], ("unit_type", "contract_item_ids", "bridge_contract_id"), "scope.unit_grouping")
                if "prerequisite_relations" not in allowed:
                    self.compare_fields(pmap[unit_id], cmap[unit_id], ("prerequisite_unit_ids",), "scope.unit_prerequisites")
                if "unit_purpose_and_learning_goals" not in allowed:
                    self.compare_fields(pmap[unit_id], cmap[unit_id], ("purpose", "learning_goal_ids"), "scope.unit_purpose")
        if "instruction_sequence" not in allowed:
            self.check(parent.get("instruction_sequence") == child.get("instruction_sequence"), "scope.sequence", "instruction sequence changed without review")

    def validate_bridges(self, parent: dict[str, Any], child: dict[str, Any], scope: dict[str, Any]) -> None:
        concept_scope = self.scoped_map(scope.get("concept_reviews", []), "concept_id")
        allowed = {concept_id for concept_id, fields in concept_scope.items() if "bridge_requirement" in fields}
        pmap = {entry["concept_id"]: entry for entry in parent["bridge_requirements"]}
        cmap = {entry["concept_id"]: entry for entry in child["bridge_requirements"]}
        for concept_id in (set(pmap) | set(cmap)) - allowed:
            self.check(pmap.get(concept_id) == cmap.get(concept_id), "scope.bridge", f"bridge requirement changed without review for {concept_id}")

    def validate_changes(self, parent: dict[str, Any], child: dict[str, Any], scope: dict[str, Any]) -> None:
        records = scope.get("pathway_change_reviews", [])
        allowed = self.scoped_map(records, "change_index")
        pchanges, cchanges = parent["pathway_changes"], child["pathway_changes"]
        structural_allowed = any("structural_accuracy" in fields for fields in allowed.values())
        if len(pchanges) != len(cchanges):
            self.check(structural_allowed, "scope.change_count", "pathway-change records added or removed without structural-accuracy review")
            return
        for index, (pchange, cchange) in enumerate(zip(pchanges, cchanges)):
            fields = allowed.get(index, set())
            if "structural_accuracy" not in fields:
                self.compare_fields(pchange, cchange, ("change_type", "affected_ids"), "scope.change_structure")
            if "profile_basis" not in fields:
                self.compare_fields(pchange, cchange, ("profile_basis",), "scope.change_profile")
            if "rationale" not in fields:
                self.compare_fields(pchange, cchange, ("rationale",), "scope.change_rationale")

    def validate_scope_summary(self, parent: dict[str, Any], child: dict[str, Any], scope: dict[str, Any]) -> None:
        psummary, csummary = parent["scope_summary"], child["scope_summary"]
        self.check(psummary.get("estimated_duration_minutes") == csummary.get("estimated_duration_minutes"), "scope.duration", "revision must preserve legacy duration metadata; word-count control is deferred to the Composer")
        selection_changed = any(
            "decision_and_role" in set(record.get("fields", []))
            for record in scope.get("selection_reviews", [])
        )
        bridge_changed = any(
            "bridge_requirement" in set(record.get("fields", []))
            for record in scope.get("concept_reviews", [])
        )
        derived_selection_fields = {
            "selected_contract_item_count", "excluded_contract_item_count",
            "critical_item_count", "formula_count", "algorithm_or_code_item_count",
        }
        for field in derived_selection_fields:
            if not selection_changed and psummary.get(field) != csummary.get(field):
                self.error("scope.summary", f"derived scope field changed without selection review: {field}")
        if not bridge_changed and psummary.get("released_bridge_count") != csummary.get("released_bridge_count"):
            self.error("scope.summary", "released_bridge_count changed without bridge review")


def write_report(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--revision-receipt", type=Path, required=True)
    parser.add_argument("--candidate-pathway", type=Path, required=True)
    parser.add_argument("--candidate-assessment", type=Path, required=True)
    parser.add_argument("--candidate-validation-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(args.workspace_root).resolve()
    receipt_path = args.revision_receipt.resolve()
    candidate_path = args.candidate_pathway.resolve()
    assessment_path = args.candidate_assessment.resolve()
    validation_path = args.candidate_validation_report.resolve()
    output_path = args.output.resolve()
    validator = RevisionValidator(root)
    try:
        validator.validate(receipt_path, candidate_path, assessment_path, validation_path)
    except (AuthorityError, OSError, KeyError, TypeError, ValueError) as exc:
        code = exc.code if isinstance(exc, AuthorityError) else "revision.exception"
        validator.error(code, str(exc))
    report = {
        "schema_version": "1.0",
        "validator": "validate-pathway-revision-v1",
        "valid": not validator.errors,
        "error_count": len(validator.errors),
        "errors": validator.errors,
        "inputs": {
            "revision_receipt": display_path(receipt_path, root),
            "revision_receipt_sha256": sha256(receipt_path) if receipt_path.is_file() else None,
            "candidate_pathway": display_path(candidate_path, root),
            "candidate_pathway_sha256": sha256(candidate_path) if candidate_path.is_file() else None,
            "candidate_assessment": display_path(assessment_path, root),
            "candidate_assessment_sha256": sha256(assessment_path) if assessment_path.is_file() else None,
            "candidate_validation_report": display_path(validation_path, root),
            "candidate_validation_report_sha256": sha256(validation_path) if validation_path.is_file() else None,
        },
        "validated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    write_report(output_path, report)
    if report["valid"]:
        print(f"PASS: pathway revision stays within reviewed scope: {output_path}")
        return 0
    print(f"FAIL: {len(validator.errors)} pathway revision error(s)")
    for error in validator.errors:
        print(f"ERROR [{error['code']}]: {error['message']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
