#!/usr/bin/env python3
"""Deterministically validate a unified RQ2 P0, P1, or P2 pathway plan."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
AUTHORITY_SCRIPTS = (
    REPO_ROOT / ".github/skills/plan-adaptive-curriculum-pathways/scripts"
)
sys.path.insert(0, str(AUTHORITY_SCRIPTS))

from pathway_authorities import (  # noqa: E402
    AuthorityError,
    display_path,
    load_object,
    resolve_path,
    sha256,
    verify_curriculum_model_release,
    verify_file_binding,
    verify_learning_request,
    verify_p0_baseline,
    verify_profile,
    verify_reference_contract_release,
)


ROOT_REQUIRED = {
    "schema_version", "pathway_id", "condition", "plan_status", "topic",
    "source_authorities", "profile_binding",
    "profile_concept_assessment_binding", "learning_request_binding",
    "baseline_pathway_binding", "selection_authority", "selection",
    "learning_goal_mappings", "learning_units", "instruction_sequence",
    "bridge_requirements", "pathway_changes", "scope_summary",
    "rendering_policy", "generated_by",
}
CONDITIONS = {"P0", "P1", "P2"}
MASTERY_VALUES = {"mastered", "fragile", "missing", "unknown"}
CHANGE_TYPES = {
    "change_item_selection", "reorder_learning_units",
    "add_prerequisite_bridge", "regroup_contract_items",
    "change_theory_implementation_application_depth",
}
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
BRIDGE_REQUIREMENT_ID_PATTERN = re.compile(r"^BRQ-[0-9]{3,}$")


class Validator:
    def __init__(
        self,
        root: Path,
        phase: str,
        bridge_catalog_path: Path | None,
        pathway_path: Path | None = None,
    ) -> None:
        self.root = root
        self.phase = phase
        self.bridge_catalog_path = bridge_catalog_path
        self.pathway_path = pathway_path
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []
        self.metrics: dict[str, Any] = {}

    def error(self, code: str, message: str) -> None:
        self.errors.append({"code": code, "message": message})

    def warning(self, code: str, message: str) -> None:
        self.warnings.append({"code": code, "message": message})

    def check(self, condition: bool, code: str, message: str) -> bool:
        if not condition:
            self.error(code, message)
        return condition

    def verify_bound_path(
        self,
        binding: Any,
        *,
        label: str,
        id_field: str,
    ) -> Path | None:
        if not isinstance(binding, dict):
            self.error(f"{label}.binding", f"{label} binding must be an object")
            return None
        path = resolve_path(self.root, binding.get("file"))
        if path is None or not path.is_file():
            self.error(f"{label}.file", f"{label} binding does not identify a file")
            return None
        if binding.get(id_field) in (None, ""):
            self.error(f"{label}.id", f"{label} binding is missing {id_field}")
        if binding.get("sha256") != sha256(path):
            self.error(f"{label}.hash", f"{label} binding SHA-256 is stale")
        return path

    def validate(self, plan: dict[str, Any]) -> None:
        self.validate_root(plan)
        condition = plan.get("condition")
        authorities = plan.get("source_authorities")
        if not isinstance(authorities, dict):
            self.error("plan.authorities", "source_authorities must be an object")
            return

        contract_path = self.verify_bound_path(
            authorities.get("reference_contract"),
            label="reference_contract",
            id_field="contract_id",
        )
        if contract_path is None:
            return
        try:
            contract = verify_reference_contract_release(self.root, contract_path)
        except AuthorityError as exc:
            self.error(exc.code, str(exc))
            return
        reference_binding = authorities["reference_contract"]
        self.check(
            reference_binding.get("contract_id") == contract.get("contract_id"),
            "reference_contract.id", "reference contract_id differs from the file",
        )
        self.check(
            reference_binding.get("contract_version") == contract.get("contract_version"),
            "reference_contract.version", "reference contract_version differs from the file",
        )

        request_path = self.verify_bound_path(
            plan.get("learning_request_binding"),
            label="learning_request", id_field="request_id",
        )
        if request_path is None:
            return
        try:
            request = verify_learning_request(
                self.root, request_path, contract_path, contract
            )
        except AuthorityError as exc:
            self.error(exc.code, str(exc))
            return
        request_binding = plan["learning_request_binding"]
        self.check(
            request_binding.get("request_id") == request.get("request_id"),
            "learning_request.id", "learning request ID differs from the file",
        )
        self.check(
            request_binding.get("request_version") == request.get("request_version"),
            "learning_request.version", "learning request version differs from the file",
        )
        self.check(
            plan.get("topic") == request.get("topic"),
            "plan.topic", "plan topic must equal the shared learning-request topic",
        )

        profile: dict[str, Any] | None = None
        profile_path: Path | None = None
        if condition == "P0":
            self.check(plan.get("profile_binding") is None, "P0.profile", "P0 must not bind a learner profile")
        else:
            profile_path = self.verify_bound_path(
                plan.get("profile_binding"), label="profile", id_field="profile_id"
            )
            if profile_path is not None:
                try:
                    profile = verify_profile(self.root, profile_path, request)
                except AuthorityError as exc:
                    self.error(exc.code, str(exc))
                else:
                    self.check(
                        plan["profile_binding"].get("profile_id") == profile.get("profile_id"),
                        "profile.id", "profile binding ID differs from the file",
                    )

        baseline: dict[str, Any] | None = None
        baseline_path: Path | None = None
        if condition == "P0":
            self.check(plan.get("baseline_pathway_binding") is None, "P0.baseline", "P0 must not bind a baseline")
        else:
            baseline_path = self.verify_bound_path(
                plan.get("baseline_pathway_binding"),
                label="baseline", id_field="pathway_id",
            )
            if baseline_path is not None:
                try:
                    baseline = verify_p0_baseline(
                        self.root, baseline_path, contract_path, request_path
                    )
                except AuthorityError as exc:
                    self.error(exc.code, str(exc))
                else:
                    self.check(
                        plan["baseline_pathway_binding"].get("pathway_id")
                        == baseline.get("pathway_id"),
                        "baseline.id", "baseline pathway ID differs from the file",
                    )

        model: dict[str, Any] | None = None
        model_path: Path | None = None
        if condition in {"P0", "P1"}:
            self.check(
                authorities.get("curriculum_model") is None,
                f"{condition}.curriculum_model",
                f"{condition} must not bind the Frozen Curriculum Model",
            )
        elif condition == "P2":
            model_binding = authorities.get("curriculum_model")
            model_path = self.verify_bound_path(
                model_binding, label="curriculum_model", id_field="model_id"
            )
            if model_path is not None and isinstance(model_binding, dict):
                try:
                    model, release = verify_curriculum_model_release(
                        self.root, model_path, contract_path
                    )
                except AuthorityError as exc:
                    self.error(exc.code, str(exc))
                else:
                    self.check(
                        model_binding.get("model_id") == model.get("model_id"),
                        "curriculum_model.id", "curriculum model ID differs from the file",
                    )
                    report_path = model_path.with_name("curriculum-release-report.json")
                    self.check(
                        resolve_path(self.root, model_binding.get("release_report_file"))
                        == report_path.resolve(),
                        "curriculum_model.release_path",
                        "curriculum model binding identifies another release report",
                    )
                    self.check(
                        model_binding.get("release_report_sha256") == sha256(report_path),
                        "curriculum_model.release_hash",
                        "curriculum model release-report SHA-256 is stale",
                    )
                    self.metrics["curriculum_release_status"] = release.get("status")

        item_map = {
            item.get("item_id"): item
            for item in contract.get("contract_items", [])
            if isinstance(item, dict) and isinstance(item.get("item_id"), str)
        }
        selection = self.validate_selection(plan, item_map, condition)
        self.validate_learning_goals(plan, request, selection)
        units, item_units = self.validate_units(plan, selection, request)
        self.validate_scope(plan, request, item_map, selection)

        if condition == "P0":
            self.validate_p0(plan)
        elif condition == "P1" and baseline is not None:
            self.validate_p1(plan, baseline)
        elif condition == "P2" and model is not None and profile is not None and baseline is not None:
            assessment = self.validate_assessment(plan, profile_path, profile, model_path, model)
            self.validate_p2(
                plan, model, assessment, selection, units, item_units, baseline
            )

        if self.phase == "confirmatory":
            self.validate_confirmatory(request, profile, plan)

    def validate_root(self, plan: dict[str, Any]) -> None:
        missing = sorted(ROOT_REQUIRED - set(plan))
        extra = sorted(set(plan) - ROOT_REQUIRED)
        if missing:
            self.error("schema.root_missing", f"missing root fields: {missing}")
        if extra:
            self.error("schema.root_extra", f"unsupported root fields: {extra}")
        self.check(plan.get("schema_version") == "1.0", "schema.version", "schema_version must be 1.0")
        self.check(plan.get("condition") in CONDITIONS, "plan.condition", "condition must be P0, P1, or P2")
        self.check(plan.get("plan_status") in {"provisional", "complete"}, "plan.status", "plan_status must be provisional or complete")
        self.check(isinstance(plan.get("pathway_id"), str) and bool(plan.get("pathway_id")), "plan.id", "pathway_id is required")

    def validate_selection(
        self,
        plan: dict[str, Any],
        item_map: dict[str, dict[str, Any]],
        condition: Any,
    ) -> set[str]:
        selection = plan.get("selection")
        if not isinstance(selection, dict):
            self.error("selection.type", "selection must be an object")
            return set()
        all_list = selection.get("all_contract_item_ids")
        selected_list = selection.get("selected_item_ids")
        excluded_list = selection.get("excluded_item_ids")
        if not all(isinstance(value, list) for value in (all_list, selected_list, excluded_list)):
            self.error("selection.arrays", "selection item fields must be arrays")
            return set()
        all_ids, selected, excluded = set(all_list), set(selected_list), set(excluded_list)
        contract_ids = set(item_map)
        for label, values, unique in (
            ("all", all_list, all_ids), ("selected", selected_list, selected),
            ("excluded", excluded_list, excluded),
        ):
            if len(values) != len(unique):
                self.error(f"selection.{label}_duplicate", f"{label} item IDs contain duplicates")
        self.check(all_ids == contract_ids, "selection.contract_coverage", "all_contract_item_ids must equal the Frozen Contract items")
        self.check(not (selected & excluded), "selection.overlap", "selected and excluded items overlap")
        self.check(selected | excluded == contract_ids, "selection.partition", "selected and excluded items must partition the Frozen Contract")
        self.check(bool(selected), "selection.empty", "at least one Contract item must be selected")

        decisions = selection.get("decisions")
        decision_map: dict[str, dict[str, Any]] = {}
        if not isinstance(decisions, list):
            self.error("selection.decisions", "selection decisions must be an array")
        else:
            for index, decision in enumerate(decisions):
                if not isinstance(decision, dict):
                    self.error("selection.decision_type", f"decision {index} must be an object")
                    continue
                item_id = decision.get("item_id")
                if item_id in decision_map:
                    self.error("selection.decision_duplicate", f"duplicate decision for {item_id}")
                if isinstance(item_id, str):
                    decision_map[item_id] = decision
                expected = "include" if item_id in selected else "exclude"
                if decision.get("decision") != expected:
                    self.error("selection.decision_conflict", f"decision for {item_id} must be {expected}")
                role = decision.get("selected_role")
                if expected == "include" and role not in {"target", "supporting", "extension"}:
                    self.error("selection.role", f"selected item {item_id} needs a selected_role")
                if expected == "exclude" and role is not None:
                    self.error("selection.role", f"excluded item {item_id} must have null selected_role")
                if not isinstance(decision.get("rationale"), str) or not decision["rationale"].strip():
                    self.error("selection.rationale", f"decision for {item_id} needs a rationale")
                basis = decision.get("profile_basis")
                if not isinstance(basis, list):
                    self.error("selection.profile_basis", f"decision for {item_id} needs a profile_basis array")
                elif condition == "P2" and not basis:
                    self.error("selection.profile_basis", f"P2 decision for {item_id} needs profile evidence")
            self.check(set(decision_map) == contract_ids, "selection.decision_coverage", "decisions must cover every Frozen Contract item exactly once")
        self.metrics["contract_item_count"] = len(contract_ids)
        self.metrics["selected_item_count"] = len(selected)
        self.metrics["excluded_item_count"] = len(excluded)
        return selected

    def validate_learning_goals(
        self, plan: dict[str, Any], request: dict[str, Any], selected: set[str]
    ) -> None:
        mappings = plan.get("learning_goal_mappings")
        if not isinstance(mappings, list):
            self.error("goals.type", "learning_goal_mappings must be an array")
            return
        requested = {
            item.get("capability_id"): item
            for item in request.get("target_capabilities", [])
            if isinstance(item, dict)
        }
        mapped: dict[str, dict[str, Any]] = {}
        for mapping in mappings:
            if not isinstance(mapping, dict):
                self.error("goals.mapping_type", "each learning-goal mapping must be an object")
                continue
            capability_id = mapping.get("capability_id")
            if capability_id in mapped:
                self.error("goals.duplicate", f"duplicate learning-goal mapping for {capability_id}")
            if isinstance(capability_id, str):
                mapped[capability_id] = mapping
            support = mapping.get("supporting_item_ids")
            if not isinstance(support, list):
                self.error("goals.support", f"{capability_id} supporting_item_ids must be an array")
                support = []
            if not set(support).issubset(selected):
                self.error("goals.unselected_support", f"{capability_id} is supported by unselected items")
            if mapping.get("coverage") == "complete" and not support:
                self.error("goals.empty_support", f"complete capability {capability_id} needs supporting items")
        self.check(set(mapped) == set(requested), "goals.coverage", "goal mappings must cover every requested capability exactly once")
        for capability_id, capability in requested.items():
            if capability.get("priority") == "required" and mapped.get(capability_id, {}).get("coverage") != "complete":
                self.error("goals.required", f"required capability {capability_id} must have complete coverage")

    def validate_units(
        self, plan: dict[str, Any], selected: set[str], request: dict[str, Any]
    ) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
        raw_units = plan.get("learning_units")
        sequence = plan.get("instruction_sequence")
        if not isinstance(raw_units, list) or not isinstance(sequence, list):
            self.error("units.type", "learning_units and instruction_sequence must be arrays")
            return {}, {}
        units: dict[str, dict[str, Any]] = {}
        item_units: dict[str, str] = {}
        bridge_ids: list[str] = []
        requested_goals = {
            item.get("capability_id") for item in request.get("target_capabilities", [])
            if isinstance(item, dict)
        }
        for index, unit in enumerate(raw_units):
            if not isinstance(unit, dict):
                self.error("units.unit_type", f"learning unit {index} must be an object")
                continue
            unit_id = unit.get("unit_id")
            if not isinstance(unit_id, str) or not unit_id:
                self.error("units.id", f"learning unit {index} needs a unit_id")
                continue
            if unit_id in units:
                self.error("units.duplicate", f"duplicate learning unit {unit_id}")
            units[unit_id] = unit
            unit_type = unit.get("unit_type")
            item_ids = unit.get("contract_item_ids")
            if not isinstance(item_ids, list):
                self.error("units.items", f"unit {unit_id} contract_item_ids must be an array")
                item_ids = []
            if unit_type == "contract_content":
                if not item_ids or unit.get("bridge_contract_id") is not None:
                    self.error("units.contract_shape", f"contract unit {unit_id} needs items and a null bridge_contract_id")
                for item_id in item_ids:
                    if item_id in item_units:
                        self.error("units.item_duplicate", f"Contract item {item_id} appears in multiple units")
                    item_units[item_id] = unit_id
            elif unit_type == "prerequisite_bridge":
                if item_ids or not isinstance(unit.get("bridge_contract_id"), str) or not unit.get("bridge_contract_id"):
                    self.error("units.bridge_shape", f"bridge unit {unit_id} must contain only a bridge_contract_id")
                else:
                    bridge_ids.append(unit["bridge_contract_id"])
            else:
                self.error("units.unit_kind", f"unit {unit_id} has unsupported unit_type")
            unit_goals = unit.get("learning_goal_ids")
            if not isinstance(unit_goals, list) or not set(unit_goals).issubset(requested_goals):
                self.error("units.goals", f"unit {unit_id} has invalid learning_goal_ids")
            if not isinstance(unit.get("prerequisite_unit_ids"), list):
                self.error("units.prerequisites", f"unit {unit_id} prerequisite_unit_ids must be an array")

        self.check(len(sequence) == len(set(sequence)), "sequence.duplicate", "instruction_sequence contains duplicates")
        self.check(set(sequence) == set(units), "sequence.coverage", "instruction_sequence must contain every learning unit exactly once")
        self.check(set(item_units) == selected, "units.selection_coverage", "selected items must occur in exactly one contract-content unit and excluded items in none")
        positions = {unit_id: index for index, unit_id in enumerate(sequence)}
        for unit_id, unit in units.items():
            prerequisites = unit.get("prerequisite_unit_ids", [])
            if isinstance(prerequisites, list):
                if len(prerequisites) != len(set(prerequisites)):
                    self.error("units.prerequisite_duplicate", f"unit {unit_id} repeats a prerequisite")
                for prerequisite in prerequisites:
                    if prerequisite not in units:
                        self.error("units.prerequisite_unknown", f"unit {unit_id} references unknown prerequisite {prerequisite}")
                    elif positions.get(prerequisite, len(sequence)) >= positions.get(unit_id, -1):
                        self.error("sequence.prerequisite_order", f"unit {unit_id} occurs before prerequisite {prerequisite}")
        self.metrics["learning_unit_count"] = len(units)
        self.metrics["bridge_unit_count"] = len(bridge_ids)
        return units, item_units

    def validate_scope(
        self,
        plan: dict[str, Any],
        request: dict[str, Any],
        item_map: dict[str, dict[str, Any]],
        selected: set[str],
    ) -> None:
        summary = plan.get("scope_summary")
        if not isinstance(summary, dict):
            self.error("scope.type", "scope_summary must be an object")
            return
        expected = {
            "selected_contract_item_count": len(selected),
            "excluded_contract_item_count": len(item_map) - len(selected),
            "critical_item_count": sum(item_map[item].get("criticality") == "critical" for item in selected),
            "formula_count": len({ref for item in selected for ref in item_map[item].get("formula_refs", [])}),
            "algorithm_or_code_item_count": sum(item_map[item].get("item_type") in {"algorithm_rule", "code_semantics"} for item in selected),
            "released_bridge_count": sum(
                isinstance(requirement, dict) and requirement.get("resolution_status") == "released"
                for requirement in plan.get("bridge_requirements", [])
                if isinstance(plan.get("bridge_requirements"), list)
            ),
        }
        for field, value in expected.items():
            if summary.get(field) != value:
                self.error("scope.recomputed", f"scope_summary.{field} must be {value}")
        target = request.get("delivery_constraints", {}).get("target_duration_minutes")
        rendering = plan.get("rendering_policy")
        if not isinstance(rendering, dict):
            self.error("rendering.type", "rendering_policy must be an object")
            return
        self.check(rendering.get("output_form") == request.get("delivery_constraints", {}).get("output_form"), "rendering.output", "output form differs from the learning request")
        self.check(rendering.get("learning_units_are_pages") is False, "rendering.pages", "learning units are not pages")
        self.check(rendering.get("target_duration_minutes") == target, "rendering.duration", "target duration differs from the learning request")
        estimate = summary.get("estimated_duration_minutes")
        if not isinstance(estimate, int) or estimate < 1 or (isinstance(target, int) and estimate > target):
            self.error("scope.duration", "estimated duration must be positive and no greater than the requested target")

    def validate_p0(self, plan: dict[str, Any]) -> None:
        self.check(plan.get("plan_status") == "complete", "P0.status", "P0 must be complete")
        self.check(plan.get("selection_authority") == "fixed_baseline", "P0.authority", "P0 selection authority must be fixed_baseline")
        self.check(plan.get("profile_concept_assessment_binding") is None, "P0.assessment", "P0 must not bind a concept assessment")
        self.check(plan.get("bridge_requirements") == [], "P0.bridges", "P0 cannot declare bridges")
        self.check(plan.get("pathway_changes") == [], "P0.changes", "P0 cannot declare pathway changes")
        self.check(plan.get("generated_by", {}).get("method") == "deterministic_baseline_normalization", "P0.method", "P0 must use deterministic baseline normalization")

    def validate_p1(self, plan: dict[str, Any], baseline: dict[str, Any]) -> None:
        self.check(plan.get("plan_status") == "complete", "P1.status", "P1 must be complete")
        self.check(plan.get("selection_authority") == "fixed_baseline", "P1.authority", "P1 selection authority must be fixed_baseline")
        self.check(plan.get("profile_concept_assessment_binding") is None, "P1.assessment", "P1 must not bind a concept assessment")
        self.check(plan.get("bridge_requirements") == [], "P1.bridges", "P1 cannot declare bridges")
        self.check(plan.get("pathway_changes") == [], "P1.changes", "P1 cannot declare pathway changes")
        self.check(plan.get("generated_by", {}).get("method") == "deterministic_P0_copy", "P1.method", "P1 must use deterministic_P0_copy")
        exact_fields = (
            "topic", "selection", "learning_goal_mappings", "learning_units",
            "instruction_sequence", "scope_summary", "rendering_policy",
        )
        for field in exact_fields:
            if plan.get(field) != baseline.get(field):
                self.error("P1.exact_copy", f"P1 field {field} must exactly equal P0")

    def validate_assessment(
        self,
        plan: dict[str, Any],
        profile_path: Path | None,
        profile: dict[str, Any],
        model_path: Path | None,
        model: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        binding = plan.get("profile_concept_assessment_binding")
        path = self.verify_bound_path(binding, label="concept_assessment", id_field="artifact_id")
        if path is None:
            return {}
        assessment = load_object(path)
        self.check(binding.get("artifact_id") == assessment.get("assessment_id"), "assessment.id", "assessment binding ID differs from the file")
        self.check(assessment.get("schema_version") == "1.0", "assessment.schema", "assessment schema_version must be 1.0")
        profile_binding = assessment.get("profile_binding")
        if not isinstance(profile_binding, dict) or profile_path is None:
            self.error("assessment.profile", "assessment profile binding is missing")
        else:
            try:
                verify_file_binding(self.root, profile_binding, profile_path, "file", "sha256", "assessment.profile")
            except AuthorityError as exc:
                self.error(exc.code, str(exc))
            self.check(profile_binding.get("profile_id") == profile.get("profile_id"), "assessment.profile_id", "assessment profile ID differs")
        model_binding = assessment.get("curriculum_model_binding")
        if not isinstance(model_binding, dict) or model_path is None:
            self.error("assessment.model", "assessment curriculum-model binding is missing")
        else:
            try:
                verify_file_binding(self.root, model_binding, model_path, "file", "sha256", "assessment.model")
            except AuthorityError as exc:
                self.error(exc.code, str(exc))
            self.check(model_binding.get("model_id") == model.get("model_id"), "assessment.model_id", "assessment model ID differs")
        expected = {
            concept.get("concept_id"): concept
            for concept in model.get("external_prerequisite_concepts", [])
            if isinstance(concept, dict)
        }
        actual: dict[str, dict[str, Any]] = {}
        entries = assessment.get("concept_assessments")
        if not isinstance(entries, list):
            self.error("assessment.concepts", "concept_assessments must be an array")
            return actual
        for entry in entries:
            if not isinstance(entry, dict):
                self.error("assessment.concept_type", "each concept assessment must be an object")
                continue
            concept_id = entry.get("concept_id")
            if concept_id in actual:
                self.error("assessment.concept_duplicate", f"duplicate concept assessment for {concept_id}")
            if isinstance(concept_id, str):
                actual[concept_id] = entry
            if concept_id in expected and entry.get("concept_name") != expected[concept_id].get("name"):
                self.error("assessment.concept_name", f"concept name for {concept_id} differs from the Frozen Curriculum Model")
            if entry.get("mastery") not in MASTERY_VALUES:
                self.error("assessment.mastery", f"invalid mastery for {concept_id}")
            if not isinstance(entry.get("profile_evidence"), list) or not entry["profile_evidence"]:
                self.error("assessment.evidence", f"concept {concept_id} needs explicit profile evidence")
            if not isinstance(entry.get("rationale"), str) or not entry["rationale"].strip():
                self.error("assessment.rationale", f"concept {concept_id} needs a rationale")
        self.check(set(actual) == set(expected), "assessment.coverage", "assessment must cover every external concept exactly once")
        return actual

    def validate_materialization_receipt(self, plan: dict[str, Any]) -> None:
        if self.pathway_path is None:
            self.error("materialization.pathway", "materialized P2 validation requires its pathway file path")
            return
        receipt_path = self.pathway_path.parent / "bridge-resolution-receipt.json"
        if not receipt_path.is_file():
            self.error("materialization.receipt", "materialized P2 is missing bridge-resolution-receipt.json")
            return
        try:
            receipt = load_object(receipt_path)
        except (AuthorityError, OSError, ValueError) as exc:
            code = exc.code if isinstance(exc, AuthorityError) else "materialization.receipt"
            self.error(code, str(exc))
            return
        self.check(receipt.get("materializer") == "released-bridge-pathway-materializer-v1", "materialization.identity", "unexpected bridge materializer identity")
        self.check(receipt.get("rule_id") == "first-consuming-unit-v1", "materialization.rule", "unexpected bridge placement rule")
        output = receipt.get("output_pathway", {})
        self.check(resolve_path(self.root, output.get("file")) == self.pathway_path, "materialization.output_path", "receipt identifies another output pathway")
        self.check(output.get("sha256") == sha256(self.pathway_path), "materialization.output_hash", "materialized pathway changed after receipt generation")
        for field in ("parent_pathway", "parent_review", "bridge_release_report"):
            binding = receipt.get(field, {})
            path = resolve_path(self.root, binding.get("file"))
            self.check(path is not None and path.is_file(), f"materialization.{field}_path", f"receipt {field} file is missing")
            if path is not None and path.is_file():
                self.check(binding.get("sha256") == sha256(path), f"materialization.{field}_hash", f"receipt {field} hash is stale")
        catalog_binding = receipt.get("bridge_catalog", {})
        catalog_path = resolve_path(self.root, catalog_binding.get("file"))
        self.check(self.bridge_catalog_path is not None, "materialization.catalog_required", "materialized P2 validation requires --bridge-catalog")
        self.check(catalog_path == self.bridge_catalog_path, "materialization.catalog_path", "receipt and validator use different bridge catalogs")
        if catalog_path is not None and catalog_path.is_file():
            self.check(catalog_binding.get("sha256") == sha256(catalog_path), "materialization.catalog_hash", "receipt bridge catalog hash is stale")
        resolved = receipt.get("resolved_bridges")
        self.check(isinstance(resolved, list) and bool(resolved), "materialization.resolved", "receipt has no resolved bridges")

    def validate_p2(
        self,
        plan: dict[str, Any],
        model: dict[str, Any],
        assessment: dict[str, dict[str, Any]],
        selected: set[str],
        units: dict[str, dict[str, Any]],
        item_units: dict[str, str],
        baseline: dict[str, Any],
    ) -> None:
        self.check(plan.get("selection_authority") == "dependency_aware_planner", "P2.authority", "P2 selection authority must be dependency_aware_planner")
        generated = plan.get("generated_by", {})
        producer = generated.get("producer")
        if producer == "adaptive-curriculum-pathway-planner":
            self.check(generated.get("method") == "adaptive_pathway_planning", "P2.method", "Planner P2 must use adaptive_pathway_planning")
            self.check(generated.get("producer_version") in {"1.0", "1.1"}, "P2.producer_version", "Planner producer_version must be 1.0 or 1.1")
        elif producer == "released-bridge-pathway-materializer":
            self.check(generated.get("method") == "released_bridge_materialization", "P2.method", "materialized P2 must use released_bridge_materialization")
            self.check(generated.get("producer_version") == "1.0", "P2.producer_version", "materializer producer_version must be 1.0")
            self.validate_materialization_receipt(plan)
        else:
            self.error("P2.producer", "P2 producer must be the adaptive Planner or released-bridge materializer")
        model_items = {
            item.get("item_id"): item for item in model.get("items", [])
            if isinstance(item, dict)
        }
        order = {unit_id: index for index, unit_id in enumerate(plan.get("instruction_sequence", []))}
        decisions = {
            decision.get("item_id"): decision
            for decision in plan.get("selection", {}).get("decisions", [])
            if isinstance(decision, dict)
        }
        for item_id in selected:
            dependency = model_items.get(item_id)
            if dependency is None:
                self.error("dependency.item", f"selected item {item_id} is absent from the curriculum model")
                continue
            for dependency_type in ("hard_dependencies", "implementation_dependencies"):
                for prerequisite in dependency.get(dependency_type, []):
                    if prerequisite not in selected:
                        self.error(f"dependency.{dependency_type}", f"selected {item_id} omits {prerequisite}")
                    elif prerequisite in item_units and item_id in item_units:
                        prerequisite_unit, item_unit = item_units[prerequisite], item_units[item_id]
                        if prerequisite_unit == item_unit or order.get(prerequisite_unit, 10**6) >= order.get(item_unit, -1):
                            self.error("dependency.order", f"{prerequisite} must be in an earlier unit than {item_id}")
            for prerequisite in dependency.get("co_requisite_item_ids", []):
                if prerequisite not in selected:
                    self.error("dependency.co_requisite", f"selected {item_id} omits co-requisite {prerequisite}")
            omitted_explanatory = set(dependency.get("explanatory_dependencies", [])) - selected
            if omitted_explanatory:
                fallback = dependency.get("fallback_when_explanatory_dependencies_omitted", {})
                if fallback.get("allowed") is not True or not fallback.get("instruction"):
                    self.error("dependency.explanatory", f"selected {item_id} omits explanatory dependencies without an allowed fallback")
                else:
                    unit = units.get(item_units.get(item_id, ""), {})
                    searchable = " ".join([
                        str(unit.get("purpose", "")),
                        str(decisions.get(item_id, {}).get("rationale", "")),
                    ])
                    if fallback["instruction"] not in searchable:
                        self.error("dependency.fallback", f"selected {item_id} must record the exact explanatory fallback instruction")

        concept_map = {
            concept.get("concept_id"): concept
            for concept in model.get("external_prerequisite_concepts", [])
            if isinstance(concept, dict)
        }
        required_concepts: dict[str, set[str]] = {}
        for concept_id, concept in concept_map.items():
            supporting = set(concept.get("supports_item_ids", [])) & selected
            assessed = assessment.get(concept_id)
            if supporting and assessed and assessed.get("mastery") in {"fragile", "missing", "unknown"}:
                required_concepts[concept_id] = supporting
        raw_requirements = plan.get("bridge_requirements")
        if not isinstance(raw_requirements, list):
            self.error("bridges.type", "bridge_requirements must be an array")
            raw_requirements = []
        requirements: dict[str, dict[str, Any]] = {}
        for position, requirement in enumerate(raw_requirements, start=1):
            if not isinstance(requirement, dict):
                self.error("bridges.requirement_type", "each bridge requirement must be an object")
                continue
            missing_fields = BRIDGE_REQUIREMENT_FIELDS - set(requirement)
            extra_fields = set(requirement) - BRIDGE_REQUIREMENT_FIELDS
            if missing_fields:
                self.error(
                    "bridges.requirement_fields",
                    "bridge requirement is missing canonical fields: "
                    + ", ".join(sorted(missing_fields)),
                )
            if extra_fields:
                self.error(
                    "bridges.requirement_extra_fields",
                    "bridge requirement contains non-canonical fields: "
                    + ", ".join(sorted(extra_fields)),
                )
            requirement_id = requirement.get("requirement_id")
            expected_requirement_id = f"BRQ-{position:03d}"
            if (
                not isinstance(requirement_id, str)
                or BRIDGE_REQUIREMENT_ID_PATTERN.fullmatch(requirement_id) is None
                or requirement_id != expected_requirement_id
            ):
                self.error(
                    "bridges.requirement_id",
                    f"bridge requirement at position {position} must use {expected_requirement_id}",
                )
            rationale = requirement.get("rationale")
            if not isinstance(rationale, str) or not rationale.strip():
                self.error(
                    "bridges.rationale",
                    f"{expected_requirement_id} must have a non-empty rationale",
                )
            concept_id = requirement.get("concept_id")
            if concept_id in requirements:
                self.error("bridges.duplicate", f"duplicate bridge requirement for {concept_id}")
            if isinstance(concept_id, str):
                requirements[concept_id] = requirement
            concept = concept_map.get(concept_id, {})
            assessed = assessment.get(concept_id, {})
            if requirement.get("bridge_candidate_id") != concept.get("bridge_candidate_id"):
                self.error("bridges.candidate_id", f"bridge candidate for {concept_id} differs from the curriculum model")
            if set(requirement.get("required_by_item_ids", [])) != required_concepts.get(concept_id, set()):
                self.error("bridges.required_by", f"bridge requirement {concept_id} has incorrect required_by_item_ids")
            if requirement.get("learner_mastery") != assessed.get("mastery"):
                self.error("bridges.mastery", f"bridge requirement {concept_id} differs from the assessment")
        self.check(set(requirements) == set(required_concepts), "bridges.coverage", "bridge requirements must exactly cover selected items' unmet external prerequisites")

        released_catalog = self.load_released_bridges()
        released_contracts: set[str] = set()
        unresolved = False
        for concept_id, requirement in requirements.items():
            status = requirement.get("resolution_status")
            released_id = requirement.get("released_bridge_contract_id")
            if status == "released":
                if not isinstance(released_id, str) or not released_id:
                    self.error("bridges.released_id", f"released bridge {concept_id} needs a contract ID")
                elif (concept_id, requirement.get("bridge_candidate_id"), released_id) not in released_catalog:
                    self.error("bridges.release_evidence", f"bridge {released_id} is not released in the supplied catalog")
                else:
                    released_contracts.add(released_id)
            elif status in {"missing", "candidate"}:
                unresolved = True
                if released_id is not None:
                    self.error("bridges.unreleased_id", f"unreleased bridge {concept_id} must have null released_bridge_contract_id")
            else:
                self.error("bridges.status", f"bridge requirement {concept_id} has invalid resolution_status")
        bridge_units = [
            unit.get("bridge_contract_id") for unit in units.values()
            if unit.get("unit_type") == "prerequisite_bridge"
        ]
        self.check(set(bridge_units) == released_contracts and len(bridge_units) == len(released_contracts), "bridges.units", "bridge learning units must exactly match released required bridges")
        expected_status = "provisional" if unresolved else "complete"
        self.check(plan.get("plan_status") == expected_status, "P2.status", f"P2 plan_status must be {expected_status}")
        self.metrics["unresolved_bridge_count"] = sum(
            requirement.get("resolution_status") in {"missing", "candidate"}
            for requirement in requirements.values()
        )

        detected = self.detect_changes(plan, baseline, selected, item_units, units)
        raw_changes = plan.get("pathway_changes")
        if not isinstance(raw_changes, list):
            self.error("changes.type", "pathway_changes must be an array")
            return
        declared: set[str] = set()
        for change in raw_changes:
            if not isinstance(change, dict):
                self.error("changes.change_type", "each pathway change must be an object")
                continue
            change_type = change.get("change_type")
            if change_type not in CHANGE_TYPES:
                self.error("changes.unsupported", f"unsupported pathway change {change_type}")
                continue
            declared.add(change_type)
            if not isinstance(change.get("affected_ids"), list) or not change["affected_ids"]:
                self.error("changes.affected", f"change {change_type} needs affected_ids")
            if not isinstance(change.get("profile_basis"), list) or not change["profile_basis"]:
                self.error("changes.profile_basis", f"change {change_type} needs learner-profile evidence")
            if not isinstance(change.get("rationale"), str) or not change["rationale"].strip():
                self.error("changes.rationale", f"change {change_type} needs a rationale")
        for change_type in detected:
            if change_type not in declared:
                self.error("changes.undeclared", f"detected change is not declared: {change_type}")
        for change_type in declared - {"change_theory_implementation_application_depth"}:
            if change_type not in detected:
                self.error("changes.not_detected", f"declared structural change is not detected: {change_type}")
        self.metrics["detected_change_types"] = sorted(detected)

    def load_released_bridges(self) -> set[tuple[str, str, str]]:
        if self.bridge_catalog_path is None:
            return set()
        try:
            catalog = load_object(self.bridge_catalog_path)
        except AuthorityError as exc:
            self.error(exc.code, str(exc))
            return set()
        release_report_path = self.bridge_catalog_path.parent / "bridge-library-release-report.json"
        if not release_report_path.is_file():
            self.error("bridge_catalog.release_report", "bridge catalog release report is missing")
            return set()
        try:
            release_report = load_object(release_report_path)
        except AuthorityError as exc:
            self.error(exc.code, str(exc))
            return set()
        self.check(catalog.get("status") == "released", "bridge_catalog.status", "bridge catalog is not released")
        self.check(release_report.get("status") == "released", "bridge_catalog.release_status", "bridge catalog release report is not released")
        outputs = release_report.get("outputs", {})
        self.check(
            resolve_path(self.root, outputs.get("released_bridge_catalog")) == self.bridge_catalog_path,
            "bridge_catalog.release_path",
            "bridge release report identifies another catalog",
        )
        self.check(
            outputs.get("released_bridge_catalog_sha256") == sha256(self.bridge_catalog_path),
            "bridge_catalog.release_hash",
            "released bridge catalog hash is stale",
        )
        result: set[tuple[str, str, str]] = set()
        bridges = catalog.get("bridges")
        if not isinstance(bridges, list):
            self.error("bridge_catalog.shape", "bridge catalog must contain a bridges array")
            return result
        for bridge in bridges:
            if isinstance(bridge, dict) and bridge.get("status") == "released":
                values = (
                    bridge.get("concept_id"), bridge.get("bridge_candidate_id"),
                    bridge.get("bridge_contract_id"),
                )
                if all(isinstance(value, str) and value for value in values):
                    result.add(values)  # type: ignore[arg-type]
        return result

    def detect_changes(
        self,
        plan: dict[str, Any],
        baseline: dict[str, Any],
        selected: set[str],
        item_units: dict[str, str],
        units: dict[str, dict[str, Any]],
    ) -> set[str]:
        detected: set[str] = set()
        baseline_selected = set(baseline.get("selection", {}).get("selected_item_ids", []))
        if selected != baseline_selected:
            detected.add("change_item_selection")
        if any(unit.get("unit_type") == "prerequisite_bridge" for unit in units.values()):
            detected.add("add_prerequisite_bridge")
        baseline_units = {
            unit.get("unit_id"): unit for unit in baseline.get("learning_units", [])
            if isinstance(unit, dict)
        }
        baseline_item_units = {
            item_id: unit_id for unit_id, unit in baseline_units.items()
            for item_id in unit.get("contract_item_ids", [])
        }
        common = selected & baseline_selected
        baseline_groups = {
            frozenset((left, right))
            for left in common for right in common if left < right
            and baseline_item_units.get(left) == baseline_item_units.get(right)
        }
        actual_groups = {
            frozenset((left, right))
            for left in common for right in common if left < right
            and item_units.get(left) == item_units.get(right)
        }
        if baseline_groups != actual_groups:
            detected.add("regroup_contract_items")
        baseline_order = {unit_id: index for index, unit_id in enumerate(baseline.get("instruction_sequence", []))}
        actual_order = {unit_id: index for index, unit_id in enumerate(plan.get("instruction_sequence", []))}
        reordered = False
        for left in common:
            for right in common:
                if left >= right:
                    continue
                base_pair = (
                    baseline_order.get(baseline_item_units.get(left, ""), -1),
                    baseline_order.get(baseline_item_units.get(right, ""), -1),
                )
                actual_pair = (
                    actual_order.get(item_units.get(left, ""), -1),
                    actual_order.get(item_units.get(right, ""), -1),
                )
                if base_pair[0] != base_pair[1] and actual_pair[0] != actual_pair[1]:
                    if (base_pair[0] < base_pair[1]) != (actual_pair[0] < actual_pair[1]):
                        reordered = True
        if reordered:
            detected.add("reorder_learning_units")
        return detected

    def validate_confirmatory(
        self,
        request: dict[str, Any],
        profile: dict[str, Any] | None,
        plan: dict[str, Any],
    ) -> None:
        if request.get("status") != "frozen" or request.get("review", {}).get("review_status") != "approved":
            self.error("confirmatory.request", "confirmatory use requires a frozen, approved learning request")
        if plan.get("condition") in {"P1", "P2"} and (profile is None or profile.get("review_status") != "approved"):
            self.error("confirmatory.profile", "confirmatory use requires an approved learner profile")
        if plan.get("condition") == "P2":
            binding = plan.get("profile_concept_assessment_binding")
            path = resolve_path(self.root, binding.get("file")) if isinstance(binding, dict) else None
            if path is None or not path.is_file() or load_object(path).get("assessment_status") != "reviewed":
                self.error("confirmatory.assessment", "confirmatory P2 use requires a reviewed concept assessment")


def write_report(path: Path | None, report: dict[str, Any]) -> None:
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if path is None:
        print(rendered, end="")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--pathway", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--phase", choices=("pilot", "confirmatory"), default="pilot")
    parser.add_argument("--bridge-catalog", type=Path)
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    pathway_path = args.pathway.resolve()
    output_path = args.output.resolve() if args.output else None
    validator = Validator(
        root,
        args.phase,
        args.bridge_catalog.resolve() if args.bridge_catalog else None,
        pathway_path,
    )
    plan: dict[str, Any] = {}
    try:
        plan = load_object(pathway_path)
        validator.validate(plan)
    except (AuthorityError, OSError, KeyError, TypeError, ValueError) as exc:
        code = exc.code if isinstance(exc, AuthorityError) else "validator.exception"
        validator.error(code, str(exc))
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    report = {
        "schema_version": "1.0",
        "validator": "validate-pathway-plan-v1",
        "phase": args.phase,
        "pathway": display_path(pathway_path, root),
        "pathway_sha256": sha256(pathway_path) if pathway_path.is_file() else None,
        "bridge_catalog": (
            {
                "file": display_path(args.bridge_catalog.resolve(), root),
                "sha256": sha256(args.bridge_catalog.resolve()),
            }
            if args.bridge_catalog is not None and args.bridge_catalog.resolve().is_file()
            else None
        ),
        "schemas": {
            "pathway_plan": {
                "file": "experiments/rq2/schemas/pathway-plan.schema.json",
                "sha256": sha256(root / "experiments/rq2/schemas/pathway-plan.schema.json"),
            },
            "profile_concept_assessment": {
                "file": "experiments/rq2/schemas/profile-concept-assessment.schema.json",
                "sha256": sha256(root / "experiments/rq2/schemas/profile-concept-assessment.schema.json"),
            },
        },
        "condition": plan.get("condition"),
        "valid": not validator.errors,
        "error_count": len(validator.errors),
        "warning_count": len(validator.warnings),
        "errors": validator.errors,
        "warnings": validator.warnings,
        "metrics": validator.metrics,
        "validated_at": generated_at,
    }
    write_report(output_path, report)
    if report["valid"]:
        print(f"PASS: valid {plan.get('condition')} pathway plan")
        return 0
    print(f"FAIL: {len(validator.errors)} pathway validation error(s)")
    for error in validator.errors:
        print(f"ERROR [{error['code']}]: {error['message']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
