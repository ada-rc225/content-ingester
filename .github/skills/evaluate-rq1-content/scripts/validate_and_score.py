#!/usr/bin/env python3
"""Validate one blind RQ1 judgement and deterministically compute outcome metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PEDAGOGY_DIMENSIONS = {
    "learner_alignment", "disciplinary_authenticity", "pedagogical_coherence",
    "theory_implementation_alignment", "readability", "analogy_safety", "exercise_validity",
}
ALGORITHM_TYPES = {"algorithm_rule", "initialisation", "stopping_condition", "failure_condition", "code_semantics"}
SEVERITY_WEIGHT = {"none": 0, "minor": 1, "major": 2, "critical": 3}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rate(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 6) if denominator else None


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def schema_errors(instance: object, schema: dict, root: dict, path: str = "$") -> list[str]:
    """Validate the JSON-Schema subset used by the judgement contract without dependencies."""
    errors: list[str] = []
    if "$ref" in schema:
        target: object = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]  # type: ignore[index]
        return schema_errors(instance, target, root, path)  # type: ignore[arg-type]
    if "oneOf" in schema:
        matches = [candidate for candidate in schema["oneOf"] if not schema_errors(instance, candidate, root, path)]
        if len(matches) != 1:
            errors.append(f"{path}: must match exactly one allowed schema")
        return errors
    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected constant {schema['const']!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} is not allowed")
    expected = schema.get("type")
    type_ok = {
        "object": isinstance(instance, dict),
        "array": isinstance(instance, list),
        "string": isinstance(instance, str),
        "integer": isinstance(instance, int) and not isinstance(instance, bool),
        "number": isinstance(instance, (int, float)) and not isinstance(instance, bool),
        "boolean": isinstance(instance, bool),
        "null": instance is None,
    }.get(expected, True)
    if expected and not type_ok:
        errors.append(f"{path}: expected {expected}")
        return errors
    if isinstance(instance, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in instance:
                errors.append(f"{path}: missing required property {key}")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}: unexpected property {key}")
        for key, subschema in properties.items():
            if key in instance:
                errors.extend(schema_errors(instance[key], subschema, root, f"{path}.{key}"))
    elif isinstance(instance, list):
        if len(instance) < schema.get("minItems", 0):
            errors.append(f"{path}: too few items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: too many items")
        if schema.get("uniqueItems"):
            encoded = [json.dumps(value, sort_keys=True) for value in instance]
            if len(encoded) != len(set(encoded)):
                errors.append(f"{path}: items must be unique")
        if "items" in schema:
            for index, value in enumerate(instance):
                errors.extend(schema_errors(value, schema["items"], root, f"{path}[{index}]"))
    elif isinstance(instance, str):
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: string is too short")
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append(f"{path}: string is too long")
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: string does not match {schema['pattern']}")
        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(instance.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{path}: invalid date-time")
    elif isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--judgement", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    judgement_path = args.judgement.resolve()
    output_path = args.output.resolve()
    if output_path.exists():
        parser.error(f"refusing to overwrite score report: {output_path}")

    script_dir = Path(__file__).resolve().parent
    schema_path = script_dir.parent / "references" / "evaluation-judgement.schema.json"
    manifest_path = bundle / "evaluation_manifest.json"
    contract_path = bundle / "frozen_reference_contract.json"
    for path in (schema_path, manifest_path, contract_path, judgement_path):
        if not path.is_file():
            parser.error(f"missing input: {path}")

    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    judgement = json.loads(judgement_path.read_text(encoding="utf-8"))
    errors = schema_errors(judgement, schema, schema)

    binding = judgement.get("bundle_binding", {})
    if binding.get("bundle_id") != manifest.get("bundle_id"):
        fail("bundle_id does not match manifest", errors)
    if binding.get("manifest_sha256") != digest(manifest_path):
        fail("manifest SHA-256 does not match", errors)
    if binding.get("contract_id") != contract.get("contract_id") or binding.get("contract_version") != contract.get("contract_version"):
        fail("Contract identity does not match", errors)
    if binding.get("contract_sha256") != digest(contract_path):
        fail("Contract SHA-256 does not match", errors)
    sample_records = {record["sample_id"]: record for record in manifest.get("samples", [])}
    sample_id = binding.get("sample_id")
    if sample_id not in sample_records:
        fail("sample_id is not in the blind bundle", errors)
    elif binding.get("content_sha256") != sample_records[sample_id]["content_sha256"]:
        fail("sample content SHA-256 does not match", errors)

    contract_items = {item["item_id"]: item for item in contract.get("contract_items", [])}
    evaluations = judgement.get("item_evaluations", [])
    evaluation_ids = [item.get("item_id") for item in evaluations]
    if set(evaluation_ids) != set(contract_items) or len(evaluation_ids) != len(set(evaluation_ids)):
        fail("item_evaluations must contain every Contract item exactly once", errors)

    for evaluation in evaluations:
        item_id = evaluation.get("item_id")
        contract_item = contract_items.get(item_id)
        if not contract_item:
            continue
        required = contract_item.get("generation_requirement") == "required"
        if required and evaluation.get("selection_basis") != "required":
            fail(f"{item_id}: required item must use selection_basis=required", errors)
        if required and evaluation.get("applicability") == "not_applicable":
            fail(f"{item_id}: required item cannot be not_applicable", errors)
        if evaluation.get("selection_basis") == "conditional_not_selected":
            if (evaluation.get("applicability"), evaluation.get("coverage"), evaluation.get("severity")) != ("not_applicable", "not_applicable", "not_applicable"):
                fail(f"{item_id}: unselected conditional item must be consistently not_applicable", errors)
        if evaluation.get("applicability") == "applicable" and evaluation.get("severity") == "not_applicable":
            fail(f"{item_id}: applicable item cannot have not_applicable severity", errors)
        if evaluation.get("abstain") and "uncertain" not in (evaluation.get("applicability"), evaluation.get("coverage"), evaluation.get("severity")):
            fail(f"{item_id}: abstention must use an uncertain judgement", errors)
        contract_conditions = contract_item.get("conditions", [])
        judged_conditions = [entry.get("condition") for entry in evaluation.get("condition_checks", [])]
        if judged_conditions != contract_conditions:
            fail(f"{item_id}: condition_checks must reproduce Contract conditions in order", errors)
        if evaluation.get("coverage") == "omitted" and evaluation.get("lesson_evidence"):
            fail(f"{item_id}: omitted item should not cite lesson evidence", errors)

    claim_ids = [claim.get("claim_id") for claim in judgement.get("atomic_claim_evaluations", [])]
    if len(claim_ids) != len(set(claim_ids)):
        fail("atomic claim IDs must be unique", errors)
    for claim in judgement.get("atomic_claim_evaluations", []):
        unknown = set(claim.get("supporting_item_ids", [])) - set(contract_items)
        if unknown:
            fail(f"{claim.get('claim_id')}: unknown supporting Contract items {sorted(unknown)}", errors)
        if claim.get("verdict") == "supported" and not claim.get("supporting_item_ids"):
            fail(f"{claim.get('claim_id')}: supported claim needs at least one Contract item", errors)
        if claim.get("abstain") and claim.get("verdict") != "uncertain":
            fail(f"{claim.get('claim_id')}: abstention must use verdict=uncertain", errors)

    pedagogy = judgement.get("pedagogy_evaluations", [])
    dimensions = [entry.get("dimension") for entry in pedagogy]
    if set(dimensions) != PEDAGOGY_DIMENSIONS or len(dimensions) != len(set(dimensions)):
        fail("pedagogy_evaluations must contain all seven dimensions exactly once", errors)
    for entry in pedagogy:
        if entry.get("abstain") and entry.get("score") != "uncertain":
            fail(f"{entry.get('dimension')}: abstention must use score=uncertain", errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    applicable = [entry for entry in evaluations if entry["applicability"] == "applicable" and not entry["abstain"] and entry["severity"] != "uncertain"]
    required_evals = [entry for entry in evaluations if contract_items[entry["item_id"]]["generation_requirement"] == "required"]
    required_evaluable = [entry for entry in required_evals if entry["applicability"] == "applicable" and not entry["abstain"] and entry["severity"] != "uncertain"]
    required_full = sum(entry["coverage"] == "full" for entry in required_evals)
    required_omitted = sum(entry["coverage"] == "omitted" for entry in required_evals)
    major_critical = sum(entry["severity"] in ("major", "critical") for entry in applicable)
    required_major_critical = sum(entry["severity"] in ("major", "critical") for entry in required_evaluable)
    drifted = sum(bool(entry["drift_types"]) for entry in applicable)
    severity_burden = sum(SEVERITY_WEIGHT[entry["severity"]] for entry in applicable)
    critical_contract = [entry for entry in applicable if contract_items[entry["item_id"]]["criticality"] == "critical"]
    critical_contract_errors = sum(entry["severity"] in ("major", "critical") for entry in critical_contract)

    conditions = [check for entry in evaluations for check in entry["condition_checks"] if check["status"] in ("preserved", "omitted", "contradicted")]
    condition_failures = sum(check["status"] in ("omitted", "contradicted") for check in conditions)

    formula_evals = [entry for entry in applicable if contract_items[entry["item_id"]].get("formula_refs")]
    formula_correct = sum(entry["severity"] == "none" and entry["coverage"] == "full" and "formula_changed" not in entry["drift_types"] for entry in formula_evals)
    algorithm_evals = [entry for entry in applicable if contract_items[entry["item_id"]]["item_type"] in ALGORITHM_TYPES]
    algorithm_correct = sum(entry["severity"] == "none" and entry["coverage"] == "full" and "algorithm_changed" not in entry["drift_types"] for entry in algorithm_evals)

    claims = judgement["atomic_claim_evaluations"]
    claim_evaluable = [claim for claim in claims if claim["verdict"] in ("supported", "unsupported", "contradicted") and not claim["abstain"]]
    unsupported = sum(claim["verdict"] in ("unsupported", "contradicted") for claim in claim_evaluable)
    report = {
        "schema_version": "1.0",
        "evaluation_protocol": "RQ1-EVAL-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed",
        "input": {
            "judgement_file": str(judgement_path),
            "judgement_sha256": digest(judgement_path),
            "bundle_id": manifest["bundle_id"],
            "sample_id": sample_id,
            "evaluator_run_id": judgement["evaluator"]["evaluator_run_id"],
            "pass_index": judgement["evaluator"]["pass_index"],
        },
        "primary_outcome": {
            "major_critical_error_count": required_major_critical,
            "evaluable_required_item_count": len(required_evaluable),
            "major_critical_error_rate": rate(required_major_critical, len(required_evaluable)),
        },
        "fidelity_outcomes": {
            "all_applicable_major_critical_error_count": major_critical,
            "all_applicable_major_critical_error_rate": rate(major_critical, len(applicable)),
            "severity_counts": dict(Counter(entry["severity"] for entry in applicable)),
            "severity_weighted_error_burden": severity_burden,
            "severity_weighted_error_rate": rate(severity_burden, 3 * len(applicable)),
            "drifted_item_count": drifted,
            "semantic_drift_rate": rate(drifted, len(applicable)),
            "critical_contract_item_error_rate": rate(critical_contract_errors, len(critical_contract)),
            "formula_item_accuracy": rate(formula_correct, len(formula_evals)),
            "algorithm_item_accuracy": rate(algorithm_correct, len(algorithm_evals)),
            "condition_failure_rate": rate(condition_failures, len(conditions)),
            "required_item_strict_coverage": rate(required_full, len(required_evals)),
            "required_item_omission_rate": rate(required_omitted, len(required_evals)),
            "unsupported_or_contradicted_claim_count": unsupported,
            "evaluable_atomic_claim_count": len(claim_evaluable),
            "unsupported_claim_rate": rate(unsupported, len(claim_evaluable)),
            "not_verifiable_claim_count": sum(claim["verdict"] == "not_verifiable" for claim in claims),
        },
        "pedagogy_outcomes": {
            entry["dimension"]: entry["score"] for entry in pedagogy
        },
        "uncertainty": {
            "item_abstention_count": sum(entry["abstain"] for entry in evaluations),
            "claim_abstention_count": sum(claim["abstain"] for claim in claims),
            "pedagogy_abstention_count": sum(entry["abstain"] for entry in pedagogy),
        },
        "warnings": [
            "These are automated operational measurements against the Frozen Contract, not expert ground truth.",
            "Do not combine fidelity and pedagogy into one overall score."
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Judgement valid; score report written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
