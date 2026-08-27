#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rq2_eval_common import (
    ALGORITHM_ITEM_TYPES,
    PRIMARY_DIMENSIONS,
    PROTOCOL_ID,
    EvaluationError,
    exact_lesson_excerpt,
    load_json,
    selected_contract_items,
    sha256,
    write_json,
)
from validate_blind_sample import validate as validate_bundle


def ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def index_unique(entries: Any, key: str, label: str, errors: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(entries, list):
        errors.append(f"{label} must be an array")
        return result
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"{label}[{index}] must be an object")
            continue
        value = entry.get(key)
        if not isinstance(value, str) or not value:
            errors.append(f"{label}[{index}].{key} is required")
            continue
        if value in result:
            errors.append(f"{label} contains duplicate {key} {value}")
        result[value] = entry
    return result


def validate_evidence(entry: dict[str, Any], lesson: str, location: str, errors: list[str], required: bool = True) -> None:
    evidence = entry.get("evidence_excerpts")
    if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
        errors.append(f"{location}.evidence_excerpts must be a string array")
        return
    if required and not evidence:
        errors.append(f"{location} needs exact lesson evidence")
    for excerpt in evidence:
        if not exact_lesson_excerpt(lesson, excerpt):
            errors.append(f"{location} contains an excerpt not found verbatim in lesson.md")


def validate_rationale(entry: dict[str, Any], location: str, errors: list[str]) -> None:
    rationale = entry.get("rationale")
    if not isinstance(rationale, str) or not rationale.strip() or "PENDING" in rationale.upper():
        errors.append(f"{location}.rationale is incomplete")


def validate_rating(entry: dict[str, Any], lesson: str, location: str, errors: list[str], allow_na: bool = False) -> None:
    validate_rationale(entry, location, errors)
    abstain = entry.get("abstain")
    score = entry.get("score")
    not_applicable = entry.get("not_applicable", False) if allow_na else False
    if abstain is True:
        if score is not None:
            errors.append(f"{location}: abstention requires a null score")
        validate_evidence(entry, lesson, location, errors, required=False)
    elif not_applicable:
        if score is not None:
            errors.append(f"{location}: not_applicable requires a null score")
        validate_evidence(entry, lesson, location, errors, required=False)
    else:
        if not isinstance(score, int) or isinstance(score, bool) or not 1 <= score <= 5:
            errors.append(f"{location}.score must be an integer from 1 to 5")
        validate_evidence(entry, lesson, location, errors, required=True)
    if entry.get("confidence") not in {"low", "medium", "high"}:
        errors.append(f"{location}.confidence is invalid")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and deterministically score one RQ2 judgement.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--judgement", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    bundle = Path(args.bundle).resolve()
    judgement_path = Path(args.judgement).resolve()
    output = Path(args.output).resolve()
    errors: list[str] = []
    try:
        bundle_errors = validate_bundle(bundle)
        if bundle_errors:
            raise EvaluationError("invalid blind bundle: " + "; ".join(bundle_errors))
        if output.exists():
            raise EvaluationError(f"refusing to overwrite deterministic score report: {output}")
        judgement = load_json(judgement_path)
        manifest = load_json(bundle / "evaluation-manifest.json")
        pathway = load_json(bundle / "pathway-evidence.json")
        request = load_json(bundle / "learning-request.json")
        structural = load_json(bundle / "structural-validation-evidence.json")
        lesson = (bundle / "lesson.md").read_text(encoding="utf-8")
        selected, items = selected_contract_items(bundle)

        if judgement.get("schema_version") != "1.0" or judgement.get("protocol_id") != PROTOCOL_ID:
            errors.append("judgement schema_version or protocol_id is invalid")
        if judgement.get("sample_id") != manifest.get("sample_id"):
            errors.append("judgement sample_id differs from the blind bundle")
        evaluator = judgement.get("evaluator")
        if not isinstance(evaluator, dict):
            errors.append("evaluator metadata is missing")
            evaluator = {}
        for field in ("evaluator_id", "provider", "model", "access_route", "evaluated_at"):
            if not isinstance(evaluator.get(field), str) or not evaluator[field].strip():
                errors.append(f"evaluator.{field} is required")
        if evaluator.get("prompt_version") != PROTOCOL_ID:
            errors.append("evaluator.prompt_version is invalid")
        if not isinstance(evaluator.get("pass_index"), int) or evaluator.get("pass_index", 0) < 1:
            errors.append("evaluator.pass_index must be positive")

        primary = index_unique(judgement.get("primary_pedagogy_judgements"), "dimension", "primary_pedagogy_judgements", errors)
        if set(primary) != set(PRIMARY_DIMENSIONS):
            errors.append("primary pedagogy judgements must cover exactly the four protocol dimensions")
        for dimension, entry in primary.items():
            validate_rating(entry, lesson, f"primary.{dimension}", errors)

        exploratory = index_unique(judgement.get("exploratory_judgements"), "dimension", "exploratory_judgements", errors)
        if set(exploratory) != {"example_authenticity"}:
            errors.append("exploratory judgements must contain only example_authenticity")
        for dimension, entry in exploratory.items():
            validate_rating(entry, lesson, f"exploratory.{dimension}", errors)

        expected_goals = {
            item.get("capability_id"): item
            for item in request.get("target_capabilities", []) if isinstance(item, dict)
        }
        goals = index_unique(judgement.get("learning_goal_judgements"), "capability_id", "learning_goal_judgements", errors)
        if set(goals) != set(expected_goals):
            errors.append("learning-goal judgements do not exactly cover the learning request")
        for goal_id, entry in goals.items():
            location = f"learning_goal.{goal_id}"
            validate_rationale(entry, location, errors)
            if entry.get("priority") != expected_goals.get(goal_id, {}).get("priority"):
                errors.append(f"{location}.priority differs from the learning request")
            if entry.get("coverage") not in {"complete", "partial", "missing", "uncertain"}:
                errors.append(f"{location}.coverage is invalid")
            abstain = entry.get("abstain") is True
            if abstain != (entry.get("coverage") == "uncertain"):
                errors.append(f"{location}: uncertain coverage and abstention must agree")
            validate_evidence(entry, lesson, location, errors, required=not abstain and entry.get("coverage") != "missing")

        selection_quality = judgement.get("selection_quality")
        if not isinstance(selection_quality, dict):
            errors.append("selection_quality must be an object")
            selection_quality = {}
        for name in ("inclusion_appropriateness", "exclusion_appropriateness", "profile_rationale_quality"):
            entry = selection_quality.get(name, {})
            validate_rating(entry, lesson, f"selection_quality.{name}", errors, allow_na=True)
        if pathway.get("excluded_item_ids") and selection_quality.get("exclusion_appropriateness", {}).get("not_applicable") is True:
            errors.append("exclusion appropriateness cannot be not_applicable when items were excluded")
        load_entry = selection_quality.get("unnecessary_content_load", {})
        validate_rationale(load_entry, "selection_quality.unnecessary_content_load", errors)
        level = load_entry.get("level")
        if level not in {"none", "low", "moderate", "high", "severe", "uncertain"}:
            errors.append("unnecessary_content_load.level is invalid")
        if (level == "uncertain") != (load_entry.get("abstain") is True):
            errors.append("unnecessary content load uncertainty and abstention must agree")
        validate_evidence(load_entry, lesson, "selection_quality.unnecessary_content_load", errors, required=level not in {"none", "uncertain"})

        item_entries = index_unique(judgement.get("selected_item_judgements"), "item_id", "selected_item_judgements", errors)
        if set(item_entries) != set(selected):
            errors.append("selected-item judgements do not exactly cover selected Contract items")
        valid_coverage = {"full", "partial", "omitted", "contradicted", "uncertain"}
        valid_semantic = {"correct", "minor_error", "major_error", "critical_error", "uncertain"}
        valid_provenance = {"supported", "unmapped", "uncertain"}
        for item_id, entry in item_entries.items():
            location = f"selected_item.{item_id}"
            validate_rationale(entry, location, errors)
            if entry.get("coverage") not in valid_coverage or entry.get("semantic_correctness") not in valid_semantic or entry.get("provenance") not in valid_provenance:
                errors.append(f"{location} has an invalid categorical judgement")
            uncertain = "uncertain" in {entry.get("coverage"), entry.get("semantic_correctness"), entry.get("provenance")}
            if uncertain != (entry.get("abstain") is True):
                errors.append(f"{location}: uncertain decisions and abstention must agree")
            evidence_required = not uncertain and entry.get("coverage") not in {"omitted"}
            validate_evidence(entry, lesson, location, errors, required=evidence_required)
            expected_requirements = [items[item_id].get("canonical_statement", ""), *items[item_id].get("conditions", [])]
            if entry.get("contract_requirements") != expected_requirements:
                errors.append(f"{location}.contract_requirements changed from the generated template")

        formula_to_items: dict[str, list[str]] = {}
        for item_id in selected:
            for formula_ref in items[item_id].get("formula_refs", []):
                formula_to_items.setdefault(formula_ref, []).append(item_id)
        formulas = index_unique(judgement.get("formula_judgements"), "formula_ref", "formula_judgements", errors)
        if set(formulas) != set(formula_to_items):
            errors.append("formula judgements do not exactly cover selected formula references")
        for formula_ref, entry in formulas.items():
            location = f"formula.{formula_ref}"
            validate_rationale(entry, location, errors)
            if entry.get("item_ids") != formula_to_items.get(formula_ref):
                errors.append(f"{location}.item_ids changed from the generated template")
            status = entry.get("occurrence_status")
            if status == "present":
                if entry.get("provenance") not in {"supported", "unmapped"} or entry.get("accuracy") not in {"correct", "incorrect"}:
                    errors.append(f"{location}: present formula needs resolved provenance and accuracy")
                if entry.get("accuracy") == "correct" and entry.get("severity") != "none":
                    errors.append(f"{location}: correct formula severity must be none")
                if entry.get("accuracy") == "incorrect" and entry.get("severity") not in {"minor", "major", "critical"}:
                    errors.append(f"{location}: incorrect formula needs an error severity")
                if entry.get("abstain") is True:
                    errors.append(f"{location}: resolved present formula cannot abstain")
                validate_evidence(entry, lesson, location, errors, required=True)
            elif status == "not_present":
                if any(entry.get(field) != "not_applicable" for field in ("provenance", "accuracy", "severity")):
                    errors.append(f"{location}: not-present formula fields must be not_applicable")
                if entry.get("abstain") is True:
                    errors.append(f"{location}: not-present is a resolved decision, not abstention")
                validate_evidence(entry, lesson, location, errors, required=False)
            elif status == "uncertain":
                if any(entry.get(field) != "uncertain" for field in ("provenance", "accuracy", "severity")) or entry.get("abstain") is not True:
                    errors.append(f"{location}: uncertain formula fields and abstention must agree")
                validate_evidence(entry, lesson, location, errors, required=False)
            else:
                errors.append(f"{location}.occurrence_status is invalid")

        expected_algorithms = {
            item_id for item_id in selected if items[item_id].get("item_type") in ALGORITHM_ITEM_TYPES
        }
        algorithms = index_unique(judgement.get("algorithm_judgements"), "item_id", "algorithm_judgements", errors)
        if set(algorithms) != expected_algorithms:
            errors.append("algorithm judgements do not exactly cover selected algorithm/code items")
        for item_id, entry in algorithms.items():
            location = f"algorithm.{item_id}"
            validate_rationale(entry, location, errors)
            accuracy = entry.get("accuracy")
            severity = entry.get("severity")
            if accuracy == "correct" and severity != "none":
                errors.append(f"{location}: correct algorithm severity must be none")
            elif accuracy == "incorrect" and severity not in {"minor", "major", "critical"}:
                errors.append(f"{location}: incorrect algorithm needs an error severity")
            elif accuracy == "uncertain" and (severity != "uncertain" or entry.get("abstain") is not True):
                errors.append(f"{location}: uncertain algorithm fields and abstention must agree")
            elif accuracy not in {"correct", "incorrect", "uncertain"}:
                errors.append(f"{location}.accuracy is invalid")
            if accuracy in {"correct", "incorrect"} and entry.get("abstain") is True:
                errors.append(f"{location}: resolved algorithm cannot abstain")
            validate_evidence(entry, lesson, location, errors, required=accuracy in {"correct", "incorrect"})

        claims = judgement.get("unsupported_claims")
        if not isinstance(claims, list):
            errors.append("unsupported_claims must be an array")
            claims = []
        claim_ids: set[str] = set()
        for index, claim in enumerate(claims):
            location = f"unsupported_claims[{index}]"
            if not isinstance(claim, dict):
                errors.append(f"{location} must be an object")
                continue
            claim_id = claim.get("claim_id")
            if not isinstance(claim_id, str) or claim_id in claim_ids:
                errors.append(f"{location}.claim_id is missing or duplicated")
            claim_ids.add(claim_id)
            excerpt = claim.get("evidence_excerpt")
            if not isinstance(excerpt, str) or not exact_lesson_excerpt(lesson, excerpt):
                errors.append(f"{location}.evidence_excerpt is not verbatim lesson evidence")
            if claim.get("claim_type") not in {"mathematical", "algorithmic", "disciplinary_application", "other_factual"}:
                errors.append(f"{location}.claim_type is invalid")
            if claim.get("verdict") not in {"unsupported", "contradicted", "not_verifiable"}:
                errors.append(f"{location}.verdict is invalid")
            if claim.get("severity") not in {"minor", "major", "critical", "uncertain"}:
                errors.append(f"{location}.severity is invalid")
            validate_rationale(claim, location, errors)

        dependency = judgement.get("dependency_coherence")
        if not isinstance(dependency, dict):
            errors.append("dependency_coherence must be an object")
            dependency = {}
        validate_rationale(dependency, "dependency_coherence", errors)
        verdict = dependency.get("verdict")
        if verdict not in {"pass", "fail", "uncertain"}:
            errors.append("dependency_coherence.verdict is invalid")
        if (verdict == "uncertain") != (dependency.get("abstain") is True):
            errors.append("dependency coherence uncertainty and abstention must agree")
        validate_evidence(dependency, lesson, "dependency_coherence", errors, required=verdict == "fail")

        overall = judgement.get("overall_recommendation")
        if not isinstance(overall, dict) or overall.get("decision") not in {"pass", "requires_adjudication", "fail"}:
            errors.append("overall_recommendation.decision is invalid")
            overall = {}
        validate_rationale(overall, "overall_recommendation", errors)

        if errors:
            print(f"FAIL: invalid RQ2 judgement ({len(errors)} errors)")
            for error in errors:
                print(f"- {error}")
            return 1

        required_goals = [entry for entry in goals.values() if entry.get("priority") == "required"]
        goal_coverage = ratio(sum(entry.get("coverage") == "complete" for entry in required_goals), len(required_goals))
        item_full_coverage = ratio(sum(entry.get("coverage") == "full" for entry in item_entries.values()), len(item_entries))
        present_formulas = [entry for entry in formulas.values() if entry.get("occurrence_status") == "present"]
        formula_provenance = ratio(sum(entry.get("provenance") == "supported" for entry in present_formulas), len(present_formulas))
        evaluable_formulas = [entry for entry in present_formulas if entry.get("accuracy") in {"correct", "incorrect"}]
        formula_accuracy = ratio(sum(entry.get("accuracy") == "correct" for entry in evaluable_formulas), len(evaluable_formulas))
        evaluable_algorithms = [entry for entry in algorithms.values() if entry.get("accuracy") in {"correct", "incorrect"}]
        algorithm_accuracy = ratio(sum(entry.get("accuracy") == "correct" for entry in evaluable_algorithms), len(evaluable_algorithms))
        lesson_metrics = structural.get("lesson_metrics", {})
        released_count = lesson_metrics.get("released_bridge_count")
        mapped_count = lesson_metrics.get("mapped_bridge_count")
        bridge_compliance = 1.0 if isinstance(released_count, int) and mapped_count == released_count else 0.0
        structural_pass = structural.get("pathway_valid") is True and structural.get("lesson_output_valid") is True

        critical_count = (
            sum(entry.get("semantic_correctness") == "critical_error" for entry in item_entries.values())
            + sum(entry.get("severity") == "critical" for entry in formulas.values())
            + sum(entry.get("severity") == "critical" for entry in algorithms.values())
            + sum(isinstance(entry, dict) and entry.get("severity") == "critical" for entry in claims)
        )
        unsupported_math_algorithm = sum(
            isinstance(entry, dict)
            and entry.get("claim_type") in {"mathematical", "algorithmic"}
            and entry.get("verdict") in {"unsupported", "contradicted"}
            for entry in claims
        )
        safety_abstentions = (
            sum(entry.get("abstain") is True for entry in goals.values())
            + sum(entry.get("abstain") is True for entry in item_entries.values())
            + sum(entry.get("abstain") is True for entry in formulas.values())
            + sum(entry.get("abstain") is True for entry in algorithms.values())
            + int(dependency.get("abstain") is True)
        )
        pedagogy_abstentions = sum(entry.get("abstain") is True for entry in primary.values())
        exploratory_abstentions = sum(entry.get("abstain") is True for entry in exploratory.values())

        applicable_accuracy_pass = (formula_accuracy in {None, 1.0}) and (algorithm_accuracy in {None, 1.0})
        gate_pass = all([
            goal_coverage == 1.0,
            item_full_coverage == 1.0,
            formula_provenance in {None, 1.0},
            structural_pass,
            bridge_compliance == 1.0,
            dependency.get("verdict") == "pass",
            applicable_accuracy_pass,
            critical_count == 0,
            unsupported_math_algorithm == 0,
            safety_abstentions == 0,
        ])

        if overall.get("decision") == "pass" and not gate_pass:
            print("FAIL: overall recommendation cannot pass when the deterministic H2c gate fails")
            return 1

        score_report = {
            "schema_version": "1.0",
            "protocol_id": PROTOCOL_ID,
            "sample_id": judgement.get("sample_id"),
            "evaluator": evaluator,
            "inputs": {
                "blind_manifest_sha256": sha256(bundle / "evaluation-manifest.json"),
                "judgement_sha256": sha256(judgement_path),
            },
            "primary_pedagogy_scores": {dimension: primary[dimension].get("score") for dimension in PRIMARY_DIMENSIONS},
            "exploratory_scores": {"example_authenticity": exploratory["example_authenticity"].get("score")},
            "selection_quality": {
                "inclusion_appropriateness": selection_quality["inclusion_appropriateness"].get("score"),
                "exclusion_appropriateness": selection_quality["exclusion_appropriateness"].get("score"),
                "unnecessary_content_load": load_entry.get("level"),
                "profile_rationale_quality": selection_quality["profile_rationale_quality"].get("score"),
            },
            "selected_content_safety": {
                "required_learning_goal_coverage": goal_coverage,
                "selected_contract_item_full_coverage": item_full_coverage,
                "present_formula_provenance_coverage": formula_provenance,
                "hard_dependency_structural_validation": 1.0 if structural_pass else 0.0,
                "released_bridge_compliance": bridge_compliance,
                "dependency_coherence_verdict": dependency.get("verdict"),
                "formula_accuracy": formula_accuracy,
                "algorithm_accuracy": algorithm_accuracy,
                "critical_error_count": critical_count,
                "unsupported_mathematical_or_algorithmic_claim_count": unsupported_math_algorithm,
                "safety_abstention_count": safety_abstentions,
                "gate_pass": gate_pass,
            },
            "abstentions": {
                "primary_pedagogy": pedagogy_abstentions,
                "exploratory": exploratory_abstentions,
                "selected_content_safety": safety_abstentions,
            },
            "scope": {
                "selected_contract_item_count": len(selected),
                "selected_formula_reference_count": len(formulas),
                "present_formula_count": len(present_formulas),
                "selected_algorithm_or_code_item_count": len(algorithms),
                "unsupported_claim_count": len(claims),
                "student_facing_word_count": lesson_metrics.get("english_prose_word_count"),
            },
            "overall_recommendation": overall,
            "interpretation_boundary": "Automated operational measurement; not student evidence or expert ground truth.",
            "valid": True,
        }
        write_json(output, score_report)
        print(f"PASS: valid RQ2 judgement; H2c_gate={str(gate_pass).lower()}")
        return 0
    except (EvaluationError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
