#!/usr/bin/env python3
"""Validate C2 v3.6 frozen-contract, length, exercise, and code evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ARTIFACT_SCHEMAS = {
    "run_manifest.json": "run-manifest.schema.json",
    "grounding_receipt.json": "grounding-receipt.schema.json",
    "grounding_view.json": "grounding-view.schema.json",
    "learner_profile.json": "learner-profile.schema.json",
    "adaptation_plan.json": "adaptation-plan.schema.json",
    "provenance.json": "provenance.schema.json",
    "code_validation.json": "code-validation.schema.json",
    "exercise_validation.json": "exercise-validation.schema.json",
}
SECTION_RE = re.compile(r"<!--\s*section:\s*(SEC-[0-9]{2})\s*-->\s*\n##\s+(.+?)\s*$", re.MULTILINE)
CODE_RE = re.compile(r"```(?:python|py)\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
VISIBLE_ITEM_ID_RE = re.compile(r"\bRC-[0-9]{3,}\b")
FENCED_BLOCK_RE = re.compile(r"^```[^\n]*\n.*?^```[ \t]*$", re.MULTILINE | re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
DISPLAY_MATH_RE = re.compile(r"\$\$.*?\$\$|\\\[.*?\\\]", re.DOTALL)
INLINE_MATH_RE = re.compile(r"(?<!\\)\$(?!\$).*?(?<!\\)\$", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
ENGLISH_WORD_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Za-z]+(?:[-'’][A-Za-z]+)*(?![A-Za-z0-9_])")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def duplicates(values):
    seen, repeated = set(), set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return repeated


def resolve_workspace_path(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def contract_identity(document: dict) -> dict:
    return {
        "contract_id": document.get("contract_id"),
        "contract_version": document.get("contract_version"),
        "sha256": document.get("sha256"),
    }


def count_english_prose_words(content: str) -> int:
    """Count visible English prose, excluding code fences, comments, math, and inline code."""
    visible = FENCED_BLOCK_RE.sub(" ", content)
    visible = HTML_COMMENT_RE.sub(" ", visible)
    visible = DISPLAY_MATH_RE.sub(" ", visible)
    visible = INLINE_MATH_RE.sub(" ", visible)
    visible = INLINE_CODE_RE.sub(" ", visible)
    visible = MARKDOWN_LINK_RE.sub(r"\1", visible)
    return len(ENGLISH_WORD_RE.findall(visible))


def schema_errors(document, schema: dict, root_schema: dict, path: str = "$") -> list[str]:
    """Validate the JSON-Schema subset used by C2 artifacts without third-party packages."""
    errors: list[str] = []
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/"):
            return [f"{path}: unsupported schema reference {ref}"]
        target = root_schema
        for part in ref[2:].split("/"):
            target = target[part.replace("~1", "/").replace("~0", "~")]
        return schema_errors(document, target, root_schema, path)
    if "oneOf" in schema:
        matches = [
            candidate
            for candidate in schema["oneOf"]
            if not schema_errors(document, candidate, root_schema, path)
        ]
        if len(matches) != 1:
            return [f"{path}: must match exactly one allowed schema"]
        return []
    if "const" in schema and document != schema["const"]:
        errors.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and document not in schema["enum"]:
        errors.append(f"{path}: must be one of {schema['enum']!r}")

    expected_type = schema.get("type")
    expected_types = expected_type if isinstance(expected_type, list) else [expected_type] if expected_type else []

    def matches_type(name: str) -> bool:
        return {
            "object": isinstance(document, dict),
            "array": isinstance(document, list),
            "string": isinstance(document, str),
            "integer": isinstance(document, int) and not isinstance(document, bool),
            "number": isinstance(document, (int, float)) and not isinstance(document, bool),
            "boolean": isinstance(document, bool),
            "null": document is None,
        }.get(name, True)

    if expected_types and not any(matches_type(name) for name in expected_types):
        return [f"{path}: expected type {expected_type!r}"]

    if isinstance(document, dict):
        properties = schema.get("properties", {})
        for field in schema.get("required", []):
            if field not in document:
                errors.append(f"{path}: missing required property {field!r}")
        if schema.get("additionalProperties") is False:
            for field in document.keys() - properties.keys():
                errors.append(f"{path}.{field}: additional property is not allowed")
        for field, child_schema in properties.items():
            if field in document:
                errors.extend(schema_errors(document[field], child_schema, root_schema, f"{path}.{field}"))
    elif isinstance(document, list):
        if len(document) < schema.get("minItems", 0):
            errors.append(f"{path}: requires at least {schema['minItems']} items")
        if "maxItems" in schema and len(document) > schema["maxItems"]:
            errors.append(f"{path}: allows at most {schema['maxItems']} items")
        if schema.get("uniqueItems"):
            serialised = [json.dumps(item, sort_keys=True) for item in document]
            if len(serialised) != len(set(serialised)):
                errors.append(f"{path}: array items must be unique")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, value in enumerate(document):
                errors.extend(schema_errors(value, item_schema, root_schema, f"{path}[{index}]"))
    elif isinstance(document, str):
        if len(document) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than {schema['minLength']}")
        if "maxLength" in schema and len(document) > schema["maxLength"]:
            errors.append(f"{path}: string is longer than {schema['maxLength']}")
        if "pattern" in schema and re.search(schema["pattern"], document) is None:
            errors.append(f"{path}: does not match {schema['pattern']!r}")
        if schema.get("format") == "date-time":
            try:
                datetime.fromisoformat(document.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{path}: invalid date-time")
    elif isinstance(document, (int, float)) and not isinstance(document, bool):
        if "minimum" in schema and document < schema["minimum"]:
            errors.append(f"{path}: must be at least {schema['minimum']}")
        if "maximum" in schema and document > schema["maximum"]:
            errors.append(f"{path}: must be at most {schema['maximum']}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--schemas-dir", default=str(Path(__file__).resolve().parent.parent / "references"))
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    root = Path(args.workspace_root).resolve()
    schemas_dir = Path(args.schemas_dir).resolve()
    errors, warnings, schema_checks, documents = [], [], [], {}

    for artifact, schema_name in ARTIFACT_SCHEMAS.items():
        artifact_errors = []
        try:
            document = load_json(run_dir / artifact)
            schema = load_json(schemas_dir / schema_name)
            artifact_errors.extend(schema_errors(document, schema, schema))
            if isinstance(document, dict):
                documents[artifact] = document
        except (OSError, json.JSONDecodeError) as exc:
            artifact_errors.append(str(exc))
        schema_checks.append({"artifact": artifact, "status": "failed" if artifact_errors else "passed", "errors": artifact_errors})
        errors.extend(f"{artifact}: {message}" for message in artifact_errors)

    frozen_contract_valid = False
    contract_binding_valid = False
    source_hashes_valid = False
    section_structure_valid = False
    prose_word_count = 0
    word_count_compliant = False
    required_item_coverage_complete = False
    conditional_item_accounting_complete = False
    provenance_complete = False
    exercise_structure_valid = False
    exercise_verification_passed = False
    code_execution_passed = False

    required_artifacts = set(ARTIFACT_SCHEMAS)
    if required_artifacts.issubset(documents):
        run = documents["run_manifest.json"]
        receipt = documents["grounding_receipt.json"]
        view = documents["grounding_view.json"]
        plan = documents["adaptation_plan.json"]
        profile = documents["learner_profile.json"]
        provenance = documents["provenance.json"]
        exercise_validation = documents["exercise_validation.json"]

        receipt_path = run_dir / "grounding_receipt.json"
        if run.get("grounding_receipt_sha256") != sha256(receipt_path):
            errors.append("run_manifest grounding_receipt_sha256 does not match grounding_receipt.json")
        view_path = run_dir / "grounding_view.json"
        if receipt.get("generation_view", {}).get("path") != "grounding_view.json" or receipt.get("generation_view", {}).get("sha256") != sha256(view_path):
            errors.append("grounding_receipt generation_view does not match grounding_view.json")

        contract_record = receipt.get("contract", {})
        contract_path = resolve_workspace_path(root, contract_record.get("path", ""))
        release_record = receipt.get("release", {})
        release_path = resolve_workspace_path(root, release_record.get("report_path", ""))
        validation_record = receipt.get("validation", {})
        frozen_validation_path = resolve_workspace_path(root, validation_record.get("report_path", ""))
        inventory_record = receipt.get("grounding_inventory", {})
        inventory_path = resolve_workspace_path(root, inventory_record.get("path", ""))
        contract = release = frozen_validation = None

        try:
            contract = load_json(contract_path)
            release = load_json(release_path)
            frozen_validation = load_json(frozen_validation_path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read frozen grounding dependency: {exc}")

        if contract and release and frozen_validation:
            contract_hash = sha256(contract_path)
            release_hash = sha256(release_path)
            validation_hash = sha256(frozen_validation_path)
            inventory_hash = sha256(inventory_path) if inventory_path.is_file() else None
            identity = {
                "contract_id": contract.get("contract_id"),
                "contract_version": contract.get("contract_version"),
                "sha256": contract_hash,
            }
            contract_binding_valid = (
                contract_record.get("sha256") == contract_hash
                and contract_identity(view.get("contract", {})) == identity
                and contract_identity(plan.get("grounding_contract", {})) == identity
                and contract_identity(provenance.get("grounding_contract", {})) == identity
                and release_record.get("report_sha256") == release_hash
                and validation_record.get("report_sha256") == validation_hash
                and inventory_record.get("sha256") == inventory_hash
                and release.get("outputs", {}).get("frozen_contract_sha256") == contract_hash
            )
            if not contract_binding_valid:
                errors.append("contract, receipt, run plan, provenance, release, validation, or inventory fingerprints do not bind to one frozen contract")

            source_hashes_valid = True
            contract_source_ids = set()
            for source in contract.get("source_materials", []):
                contract_source_ids.add(source.get("source_id"))
                source_path = resolve_workspace_path(root, source.get("path", ""))
                if not source_path.is_file() or sha256(source_path) != source.get("sha256"):
                    source_hashes_valid = False
                    errors.append(f"source hash mismatch or missing source: {source.get('source_id')}")
            receipt_source_ids = {item.get("source_id") for item in receipt.get("source_materials", [])}
            if receipt_source_ids != contract_source_ids:
                source_hashes_valid = False
                errors.append("grounding receipt source set differs from frozen contract")
            if receipt.get("source_materials") != contract.get("source_materials"):
                source_hashes_valid = False
                errors.append("grounding receipt source records differ from frozen contract")
            if set(run.get("source_ids", [])) != contract_source_ids or set(plan.get("source_ids", [])) != contract_source_ids or set(provenance.get("source_ids", [])) != contract_source_ids:
                source_hashes_valid = False
                errors.append("source_ids must exactly match frozen contract across run, plan, and provenance")

            release_inputs = release.get("inputs", {})
            manifest_path = resolve_workspace_path(root, release_inputs.get("source_manifest", ""))
            scripts_dir = root / ".github" / "scripts"
            if (scripts_dir / "validate_reference_contract.py").is_file() and manifest_path.is_file() and inventory_path.is_file():
                sys.path.insert(0, str(scripts_dir))
                from validate_reference_contract import validate_contract  # type: ignore

                metrics: dict = {}
                findings = validate_contract(contract_path, root, manifest_path, inventory_path, metrics)
            else:
                findings = ["required validator, source manifest, or grounding inventory is missing"]
            frozen_contract_valid = (
                contract.get("lifecycle_status") == "frozen"
                and isinstance(contract.get("approval"), dict)
                and release.get("status") == "released"
                and frozen_validation.get("valid") is True
                and frozen_validation.get("error_count") == 0
                and not findings
            )
            if not frozen_contract_valid:
                rendered = [f"{item.code}: {item.message}" if hasattr(item, "code") else str(item) for item in findings]
                errors.append("frozen contract or release validation failed" + (f": {rendered}" if rendered else ""))

            item_records = {item.get("item_id"): item for item in contract.get("contract_items", [])}
            receipt_items = receipt.get("generation_items", {})
            required_ids = set(receipt_items.get("required_item_ids", []))
            conditional_ids = set(receipt_items.get("conditional_item_ids", []))
            excluded_ids = set(receipt_items.get("excluded_item_ids", []))
            actual_required = {
                item_id for item_id, item in item_records.items()
                if item.get("generation_requirement") == "required" and item.get("review", {}).get("decision") != "excluded"
            }
            actual_conditional = {
                item_id for item_id, item in item_records.items()
                if item.get("generation_requirement") == "conditional" and item.get("review", {}).get("decision") != "excluded"
            }
            actual_excluded = {item_id for item_id, item in item_records.items() if item.get("review", {}).get("decision") == "excluded"}
            if (required_ids, conditional_ids, excluded_ids) != (actual_required, actual_conditional, actual_excluded):
                errors.append("grounding receipt generation item sets differ from current frozen contract")
            view_required = {item.get("item_id") for item in view.get("required_items", [])}
            view_conditional = {item.get("item_id") for item in view.get("conditional_items", [])}
            view_excluded = set(view.get("excluded_item_ids", []))
            if (view_required, view_conditional, view_excluded) != (required_ids, conditional_ids, excluded_ids):
                errors.append("grounding_view item sets differ from grounding receipt")
            expected_required_items = []
            expected_conditional_items = []
            source_issues = contract.get("candidate_source_issues", [])
            for item in contract.get("contract_items", []):
                decision = item.get("review", {}).get("decision")
                if decision == "excluded":
                    continue
                statement = item.get("canonical_statement")
                latex = item.get("canonical_latex", [])
                basis = "approved_as_written"
                if decision == "approved_with_correction":
                    corrections = [
                        issue.get("approved_generation_content")
                        for issue in source_issues
                        if item.get("item_id") in issue.get("affected_item_ids", [])
                        and issue.get("resolution") == "approved_correction"
                    ]
                    if len(corrections) == 1 and isinstance(corrections[0], dict):
                        statement = corrections[0].get("statement")
                        latex = corrections[0].get("latex", [])
                        basis = "approved_correction"
                projected = {
                    "item_id": item.get("item_id"),
                    "item_type": item.get("item_type"),
                    "criticality": item.get("criticality"),
                    "content_basis": basis,
                    "canonical_statement": statement,
                    "canonical_latex": latex,
                    "formula_refs": item.get("formula_refs", []),
                    "conditions": item.get("conditions", []),
                    "prohibited_drift": item.get("prohibited_drift", []),
                }
                target = expected_required_items if item.get("generation_requirement") == "required" else expected_conditional_items
                target.append(projected)
            if view.get("required_items") != expected_required_items or view.get("conditional_items") != expected_conditional_items:
                errors.append("grounding_view canonical content is not the deterministic projection of the frozen contract")

            plan_required = set(plan.get("required_contract_item_ids", []))
            decisions = plan.get("conditional_item_decisions", [])
            decision_ids = [item.get("item_id") for item in decisions]
            conditional_item_accounting_complete = set(decision_ids) == conditional_ids and not duplicates(decision_ids)
            if not conditional_item_accounting_complete:
                errors.append(f"conditional item decisions must account for every conditional item exactly once; missing={sorted(conditional_ids - set(decision_ids))}, unknown={sorted(set(decision_ids) - conditional_ids)}")
            included_conditional = {item.get("item_id") for item in decisions if item.get("included") is True}

            planned_sections = plan.get("chapter_sequence", [])
            planned_ids = [item.get("section_id") for item in planned_sections]
            orders = [item.get("order") for item in planned_sections]
            if orders != list(range(1, len(planned_sections) + 1)):
                errors.append("chapter order must be consecutive and match array order")
            for duplicate in sorted(duplicates(planned_ids)):
                errors.append(f"duplicate section_id: {duplicate}")
            planned_contract_ids = {value for item in planned_sections for value in item.get("contract_item_ids", [])}
            expected_planned_ids = required_ids | included_conditional
            required_item_coverage_complete = plan_required == required_ids and planned_contract_ids == expected_planned_ids
            if not required_item_coverage_complete:
                errors.append(f"planned contract coverage mismatch; missing={sorted(expected_planned_ids - planned_contract_ids)}, unexpected={sorted(planned_contract_ids - expected_planned_ids)}, required-list-difference={sorted(plan_required ^ required_ids)}")
            prohibited = planned_contract_ids & excluded_ids
            if prohibited:
                errors.append(f"excluded contract items used in adaptation plan: {sorted(prohibited)}")

            exercise_protocol = run.get("exercise_protocol", {})
            exercise_plan = plan.get("exercise_plan", [])
            exercise_section_id = plan.get("exercise_section_id")
            exercise_ids = [item.get("exercise_id") for item in exercise_plan]
            exercise_orders = [item.get("order") for item in exercise_plan]
            sequential_exercise_ids = [f"EX-{index:03d}" for index in range(1, len(exercise_plan) + 1)]
            expected_exercise_count = exercise_protocol.get("expected_count", 0)
            protocol_valid = True
            if exercise_orders != list(range(1, len(exercise_plan) + 1)):
                protocol_valid = False
                errors.append("exercise order must be consecutive and match array order")
            if exercise_ids != sequential_exercise_ids:
                protocol_valid = False
                errors.append(f"exercise IDs must be consecutive in reading order: expected={sequential_exercise_ids}, actual={exercise_ids}")
            if duplicates(exercise_ids):
                protocol_valid = False
                errors.append(f"duplicate exercise IDs: {sorted(duplicates(exercise_ids))}")
            if exercise_protocol.get("enabled"):
                final_section_id = planned_ids[-1] if planned_ids else None
                if exercise_section_id != final_section_id:
                    protocol_valid = False
                    errors.append(f"exercise_section_id must identify the final planned chapter: expected={final_section_id}, actual={exercise_section_id}")
                misplaced_exercises = [item.get("exercise_id") for item in exercise_plan if item.get("section_id") != exercise_section_id]
                if misplaced_exercises:
                    protocol_valid = False
                    errors.append(f"all exercises must be placed in the final exercise chapter {exercise_section_id}: misplaced={misplaced_exercises}")
                if expected_exercise_count < 1 or len(exercise_plan) != expected_exercise_count:
                    protocol_valid = False
                    errors.append(f"exercise protocol requires exactly {expected_exercise_count} planned exercises; actual={len(exercise_plan)}")
                actual_types = {item.get("exercise_type") for item in exercise_plan}
                missing_types = set(exercise_protocol.get("required_types", [])) - actual_types
                if missing_types:
                    protocol_valid = False
                    errors.append(f"exercise plan is missing required types: {sorted(missing_types)}")
                if exercise_protocol.get("worked_solutions_required") and any(not item.get("solution_required") for item in exercise_plan):
                    protocol_valid = False
                    errors.append("exercise protocol requires a worked solution for every exercise")
            elif expected_exercise_count != 0 or exercise_plan or exercise_protocol.get("required_types") or exercise_section_id is not None:
                protocol_valid = False
                errors.append("disabled exercise protocol requires expected_count=0, no required types, a null exercise_section_id, and an empty exercise_plan")
            for exercise in exercise_plan:
                if exercise.get("section_id") not in set(planned_ids):
                    protocol_valid = False
                    errors.append(f"{exercise.get('exercise_id')}: unknown exercise section {exercise.get('section_id')}")
                exercise_contract_ids = set(exercise.get("contract_item_ids", []))
                if not exercise_contract_ids or not exercise_contract_ids.issubset(expected_planned_ids):
                    protocol_valid = False
                    errors.append(f"{exercise.get('exercise_id')}: exercise Contract items must be selected lesson items; invalid={sorted(exercise_contract_ids - expected_planned_ids)}")
                method = exercise.get("verification", {}).get("method")
                expression = exercise.get("verification", {}).get("python_expression")
                expected_value = exercise.get("verification", {}).get("expected_value")
                consistency_checks = exercise.get("verification", {}).get("consistency_checks", [])
                unified_kinds = {"objective_gradient", "objective_gradient_update", "power_iteration_step"}
                unified_checks = [check for check in consistency_checks if check.get("kind") in unified_kinds]
                if method in {"deterministic_calculation", "combined"} and expected_value is None:
                    protocol_valid = False
                    errors.append(f"{exercise.get('exercise_id')}: deterministic verification requires expected_value")
                elif method in {"deterministic_calculation", "combined"} and unified_checks:
                    if len(unified_checks) != 1 or expression is not None or unified_checks[0].get("expected_value") != expected_value:
                        protocol_valid = False
                        errors.append(f"{exercise.get('exercise_id')}: structured deterministic verification requires exactly one unified check, the same expected value, and null python_expression")
                elif method in {"deterministic_calculation", "combined"} and exercise.get("exercise_type") == "hand_calculation":
                    protocol_valid = False
                    errors.append(f"{exercise.get('exercise_id')}: hand_calculation requires a supported unified structured checker")
                elif method in {"deterministic_calculation", "combined"} and not isinstance(expression, str):
                    protocol_valid = False
                    errors.append(f"{exercise.get('exercise_id')}: non-unified deterministic verification requires python_expression")
                if method in {"contract_binding", "code_execution"} and (expression is not None or expected_value is not None):
                    protocol_valid = False
                    errors.append(f"{exercise.get('exercise_id')}: {method} must not declare a numeric expression or expected value")
                if exercise.get("exercise_type") == "hand_calculation" and not consistency_checks:
                    protocol_valid = False
                    errors.append(f"{exercise.get('exercise_id')}: hand_calculation requires at least one model consistency check")
                check_ids = [check.get("check_id") for check in consistency_checks]
                if duplicates(check_ids):
                    protocol_valid = False
                    errors.append(f"{exercise.get('exercise_id')}: duplicate consistency-check IDs: {sorted(duplicates(check_ids))}")
                for check in consistency_checks:
                    kind = check.get("kind")
                    variables = check.get("variables", [])
                    point = check.get("point", [])
                    check_expected = check.get("expected_value")
                    if kind in {"objective_gradient", "objective_gradient_update", "expression_values"} and len(variables) != len(point):
                        protocol_valid = False
                        errors.append(f"{exercise.get('exercise_id')}/{check.get('check_id')}: point length must match variables")
                    if kind == "objective_gradient":
                        if (not isinstance(check.get("objective_expression"), str) or check.get("expressions")
                                or check.get("step_size") is not None or check.get("expected_gradient") is not None
                                or not isinstance(check_expected, list) or len(check_expected) != len(variables)):
                            protocol_valid = False
                            errors.append(f"{exercise.get('exercise_id')}/{check.get('check_id')}: objective_gradient requires one objective and expected gradient, with no update fields")
                    elif kind == "objective_gradient_update":
                        expected_gradient = check.get("expected_gradient")
                        step_size = check.get("step_size")
                        if (not isinstance(check.get("objective_expression"), str) or check.get("expressions")
                                or not isinstance(step_size, (int, float)) or isinstance(step_size, bool) or step_size <= 0
                                or not isinstance(expected_gradient, list) or len(expected_gradient) != len(variables)
                                or not isinstance(check_expected, list) or len(check_expected) != len(variables)
                                or check_expected != expected_value):
                            protocol_valid = False
                            errors.append(f"{exercise.get('exercise_id')}/{check.get('check_id')}: objective_gradient_update must bind one objective, point, positive step, expected gradient, and the same expected update used by the exercise")
                    elif kind == "power_iteration_step":
                        matrix = check.get("matrix", [])
                        initial_vector = check.get("initial_vector", [])
                        square = bool(matrix) and all(isinstance(row, list) and len(row) == len(matrix) for row in matrix)
                        if (not square or len(initial_vector) != len(matrix)
                                or not isinstance(check.get("normalize_initial"), bool)
                                or not isinstance(check_expected, dict)
                                or check_expected != expected_value):
                            protocol_valid = False
                            errors.append(f"{exercise.get('exercise_id')}/{check.get('check_id')}: power_iteration_step requires a square matrix, a matching initial vector, normalization choice, and the same structured result used by the exercise")
                    elif kind == "expression_values":
                        component_expressions = check.get("expressions", [])
                        expected_length = len(check_expected) if isinstance(check_expected, list) else 1
                        if (check.get("objective_expression") is not None or check.get("step_size") is not None
                                or check.get("expected_gradient") is not None or not component_expressions
                                or len(component_expressions) != expected_length):
                            protocol_valid = False
                            errors.append(f"{exercise.get('exercise_id')}/{check.get('check_id')}: expression_values requires no objective and one expression per expected value")

            content_path = run_dir / "adapted_content.md"
            if content_path.is_file():
                content = content_path.read_text(encoding="utf-8")
                actual_pairs = [(section_id, title.strip()) for section_id, title in SECTION_RE.findall(content)]
                expected_pairs = [(item.get("section_id"), item.get("title", "").strip()) for item in planned_sections]
                section_structure_valid = actual_pairs == expected_pairs
                if not section_structure_valid:
                    errors.append(f"content sections must exactly match plan; expected={expected_pairs}, actual={actual_pairs}")
                if VISIBLE_ITEM_ID_RE.search(content):
                    errors.append("adapted_content.md exposes internal RC item IDs; keep evidence identifiers out of student-facing prose")
                prose_word_count = count_english_prose_words(content)
                word_protocol = run.get("word_count_protocol", {})
                minimum = word_protocol.get("minimum")
                maximum = word_protocol.get("maximum")
                if word_protocol.get("enabled"):
                    if not isinstance(minimum, int) or isinstance(minimum, bool) or minimum < 1 or not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < minimum:
                        errors.append("enabled word_count_protocol requires 1 <= minimum <= maximum")
                    else:
                        word_count_compliant = minimum <= prose_word_count <= maximum
                        if not word_count_compliant:
                            errors.append(f"adapted_content.md prose word count is outside the configured range: actual={prose_word_count}, expected={minimum}-{maximum}, method=english_prose_v1")
                else:
                    word_count_compliant = minimum == 0 and maximum == 0
                    if not word_count_compliant:
                        errors.append("disabled word_count_protocol requires minimum=0 and maximum=0")
            else:
                content = ""
                errors.append("missing adapted_content.md")

            provenance_sections = provenance.get("sections", [])
            provenance_ids = [item.get("section_id") for item in provenance_sections]
            provenance_by_id = {item.get("section_id"): item for item in provenance_sections}
            plan_by_id = {item.get("section_id"): item for item in planned_sections}
            provenance_complete = provenance_ids == planned_ids and not duplicates(provenance_ids)
            if provenance_complete:
                for section_id in planned_ids:
                    recorded = set(provenance_by_id[section_id].get("contract_item_ids", []))
                    planned = set(plan_by_id[section_id].get("contract_item_ids", []))
                    if recorded != planned:
                        provenance_complete = False
                        errors.append(f"provenance contract-item mismatch for {section_id}")
            else:
                errors.append("provenance sections must exactly match planned section order")
            covered = {value for item in provenance_sections for value in item.get("contract_item_ids", [])}
            if covered != expected_planned_ids:
                provenance_complete = False
                errors.append(f"provenance coverage mismatch; missing={sorted(expected_planned_ids - covered)}, unexpected={sorted(covered - expected_planned_ids)}")

            provenance_exercises = provenance.get("exercises", [])
            provenance_exercise_ids = [item.get("exercise_id") for item in provenance_exercises]
            exercise_by_id = {item.get("exercise_id"): item for item in exercise_plan}
            provenance_exercise_by_id = {item.get("exercise_id"): item for item in provenance_exercises}
            if provenance_exercise_ids != exercise_ids or duplicates(provenance_exercise_ids):
                provenance_complete = False
                errors.append("exercise provenance must exactly match exercise_plan order")
            else:
                for exercise_id in exercise_ids:
                    planned_exercise = exercise_by_id[exercise_id]
                    recorded_exercise = provenance_exercise_by_id[exercise_id]
                    if (
                        recorded_exercise.get("section_id") != planned_exercise.get("section_id")
                        or set(recorded_exercise.get("contract_item_ids", [])) != set(planned_exercise.get("contract_item_ids", []))
                        or recorded_exercise.get("verification_method") != planned_exercise.get("verification", {}).get("method")
                    ):
                        provenance_complete = False
                        errors.append(f"exercise provenance mismatch for {exercise_id}")

            profile_ids = {run.get("profile_id"), plan.get("profile_id"), profile.get("profile_id"), provenance.get("profile_id")}
            if len(profile_ids) != 1:
                errors.append(f"profile_id mismatch across artifacts: {sorted(str(value) for value in profile_ids)}")

            code = documents["code_validation.json"]
            status = code.get("overall_status")
            code_required = run.get("code_execution_required", False)
            code_execution_passed = status == "passed" or (status == "no_code" and not code_required)
            recorded_content_path = Path(code.get("content_file", "")).resolve()
            if recorded_content_path != content_path.resolve():
                code_execution_passed = False
                errors.append("code_validation content_file does not identify this run's adapted_content.md")
            content_code_hashes = [hashlib.sha256(block.encode("utf-8")).hexdigest() for block in CODE_RE.findall(content)]
            recorded_code_hashes = [block.get("code_sha256") for block in code.get("blocks", [])]
            if content_code_hashes != recorded_code_hashes:
                code_execution_passed = False
                errors.append("code_validation hashes do not match current Python blocks")
            invalid_code_anchors = [block.get("block_id") for block in code.get("blocks", []) if block.get("anchor") not in set(planned_ids)]
            if invalid_code_anchors:
                code_execution_passed = False
                errors.append(f"code blocks without valid section anchors: {invalid_code_anchors}")
            invalid_code_exercises = [block.get("block_id") for block in code.get("blocks", []) if block.get("exercise_id") is not None and block.get("exercise_id") not in set(exercise_ids)]
            if invalid_code_exercises:
                code_execution_passed = False
                errors.append(f"code blocks with unknown exercise IDs: {invalid_code_exercises}")
            for block in code.get("blocks", []):
                exercise_id = block.get("exercise_id")
                if exercise_id in exercise_by_id and block.get("anchor") != exercise_by_id[exercise_id].get("section_id"):
                    code_execution_passed = False
                    errors.append(f"{block.get('block_id')}: exercise code section differs from exercise_plan")
            if not code_execution_passed:
                errors.append(f"code validation does not satisfy code_execution_required={code_required}: {status}")

            content_hash = sha256(content_path) if content_path.is_file() else None
            plan_path = run_dir / "adaptation_plan.json"
            code_path = run_dir / "code_validation.json"
            exercise_results = exercise_validation.get("exercises", [])
            exercise_result_ids = [item.get("exercise_id") for item in exercise_results]
            exercise_structure_valid = (
                protocol_valid
                and exercise_validation.get("content_file") == str(content_path.resolve())
                and exercise_validation.get("content_sha256") == content_hash
                and exercise_validation.get("plan_file") == str(plan_path.resolve())
                and exercise_validation.get("plan_sha256") == sha256(plan_path)
                and exercise_validation.get("code_validation_file") == str(code_path.resolve())
                and exercise_validation.get("code_validation_sha256") == sha256(code_path)
                and exercise_validation.get("exercise_count") == len(exercise_plan)
                and exercise_result_ids == exercise_ids
                and all(item.get("markers_valid") and (item.get("solution_present") or not exercise_by_id[item.get("exercise_id")].get("solution_required")) and item.get("contract_binding_declared") for item in exercise_results)
                and all(item.get("model_consistency_passed") for item in exercise_results)
                and all(item.get("unified_calculation_passed") for item in exercise_results)
                and all(item.get("visible_derivation_consistent") for item in exercise_results)
                and all(item.get("stdout_claims_consistent") for item in exercise_results)
            )
            if not exercise_structure_valid:
                errors.append("exercise validation does not match the current content, plan, code evidence, markers, solutions, or protocol")
            exercise_verification_passed = (
                exercise_validation.get("overall_status") == "passed"
                and all(item.get("verification_status") == "passed" for item in exercise_results)
            )
            if not exercise_verification_passed:
                errors.append("one or more generated exercise checks failed")

    schemas_passed = all(item["status"] == "passed" for item in schema_checks)
    treatment_valid = not errors and all([
        schemas_passed,
        frozen_contract_valid,
        contract_binding_valid,
        source_hashes_valid,
        section_structure_valid,
        word_count_compliant,
        required_item_coverage_complete,
        conditional_item_accounting_complete,
        provenance_complete,
        exercise_structure_valid,
        exercise_verification_passed,
        code_execution_passed,
    ])
    warnings.append("Validation is limited to frozen-grounding treatment integrity, declared RC-item coverage, and configured automatic checks; complete lesson correctness is outside this report's scope.")
    report = {
        "run_id": documents.get("run_manifest.json", {}).get("run_id", run_dir.name),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validation_scope": "grounding_and_configured_checks_only",
        "schema_checks": schema_checks,
        "frozen_contract_valid": frozen_contract_valid,
        "contract_binding_valid": contract_binding_valid,
        "source_hashes_valid": source_hashes_valid,
        "section_structure_valid": section_structure_valid,
        "prose_word_count": prose_word_count,
        "word_count_compliant": word_count_compliant,
        "required_item_coverage_complete": required_item_coverage_complete,
        "conditional_item_accounting_complete": conditional_item_accounting_complete,
        "provenance_complete": provenance_complete,
        "exercise_structure_valid": exercise_structure_valid,
        "exercise_verification_passed": exercise_verification_passed,
        "code_execution_passed": code_execution_passed,
        "treatment_valid": treatment_valid,
        "errors": errors,
        "warnings": warnings,
    }
    (run_dir / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if treatment_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
