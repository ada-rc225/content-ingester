#!/usr/bin/env python3
"""Validate that a revised dependency candidate stays within an approved review scope."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import prepare_dependency_revision as revision_preflight


ITEM_FIELD_MAP = {
    "hard_dependencies": ("hard_dependencies",),
    "explanatory_dependencies": ("explanatory_dependencies",),
    "implementation_dependencies": ("implementation_dependencies",),
    "co_requisite_item_ids": ("co_requisite_item_ids",),
    "recommended_neighbours": ("recommended_neighbours",),
    "external_prerequisite_concept_ids": ("external_prerequisite_concept_ids",),
    "fallback_when_explanatory_dependencies_omitted": (
        "fallback_when_explanatory_dependencies_omitted",
    ),
    "rationale_and_confidence": ("rationale", "confidence"),
}
CONCEPT_FIELD_MAP = {
    "need_type": ("need_type",),
    "supports_item_ids": ("supports_item_ids",),
    "bridge_candidate_id": ("bridge_candidate_id",),
    "content_boundary_and_rationale": ("content_boundary", "rationale"),
}


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


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def changed_fields(parent: dict[str, Any], revised: dict[str, Any]) -> set[str]:
    return {field for field in set(parent) | set(revised) if parent.get(field) != revised.get(field)}


def verify_bound_file(
    root: Path,
    recorded: dict[str, Any],
    path: Path,
    label: str,
    errors: list[dict[str, str]],
) -> None:
    if resolve_recorded_path(root, recorded.get("file")) != path:
        add_error(errors, f"binding.{label}.file", f"revision receipt identifies another {label}")
    if recorded.get("sha256") != sha256(path):
        add_error(errors, f"binding.{label}.hash", f"{label} hash does not match revision receipt")


def validate_root(
    parent: dict[str, Any],
    revised: dict[str, Any],
    receipt: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    for field in set(parent) | set(revised):
        if field not in {"model_id", "builder", "items", "external_prerequisite_concepts"} and parent.get(field) != revised.get(field):
            add_error(errors, "scope.root", f"unreviewed root field changed: {field}")
    expected_model_id = receipt.get("parent_candidate", {}).get("next_model_id")
    if revised.get("model_id") != expected_model_id:
        add_error(errors, "version.model_id", f"revised model_id must be {expected_model_id!r}")
    builder = revised.get("builder")
    expected_builder = {
        "agent": "grounded-curriculum-dependency-builder",
        "agent_version": "1.1",
        "skill": "build-curriculum-dependencies",
        "skill_version": "1.1",
    }
    if not isinstance(builder, dict):
        add_error(errors, "version.builder", "revised candidate builder metadata is missing")
    else:
        for field, expected in expected_builder.items():
            if builder.get(field) != expected:
                add_error(errors, "version.builder", f"builder.{field} must equal {expected!r}")
    source = revised.get("source_contract")
    if not isinstance(source, dict) or source.get("sha256") != receipt.get("source_contract", {}).get("sha256"):
        add_error(errors, "binding.contract", "revised candidate binds a different Frozen Contract")


def validate_items(
    parent: dict[str, Any],
    revised: dict[str, Any],
    receipt: dict[str, Any],
    errors: list[dict[str, str]],
) -> tuple[list[str], dict[str, list[str]]]:
    parent_items = parent.get("items", [])
    revised_items = revised.get("items", [])
    parent_ids = [item.get("item_id") for item in parent_items if isinstance(item, dict)]
    revised_ids = [item.get("item_id") for item in revised_items if isinstance(item, dict)]
    if revised_ids != parent_ids:
        add_error(errors, "scope.items", "revised item order and coverage must equal the parent candidate")
    parent_map = {item.get("item_id"): item for item in parent_items if isinstance(item, dict)}
    revised_map = {item.get("item_id"): item for item in revised_items if isinstance(item, dict)}
    scope_entries = receipt.get("revision_scope", {}).get("item_changes", [])
    scope = {
        entry.get("item_id"): set(entry.get("fields", []))
        for entry in scope_entries
        if isinstance(entry, dict)
    }
    changed_item_ids: list[str] = []
    changed_by_item: dict[str, list[str]] = {}
    for item_id, parent_item in parent_map.items():
        revised_item = revised_map.get(item_id)
        if not isinstance(revised_item, dict):
            continue
        actual = changed_fields(parent_item, revised_item)
        permitted_groups = scope.get(item_id, set())
        permitted_fields = {
            field
            for group in permitted_groups
            for field in ITEM_FIELD_MAP.get(group, ())
        }
        unauthorized = actual - permitted_fields
        if unauthorized:
            add_error(errors, "scope.item_field", f"{item_id} changed unreviewed fields: {sorted(unauthorized)}")
        for group in permitted_groups:
            mapped = set(ITEM_FIELD_MAP.get(group, ()))
            if not (actual & mapped):
                add_error(errors, "scope.item_unapplied", f"{item_id}.{group} was marked revision_required but did not change")
        if actual:
            changed_item_ids.append(item_id)
            changed_by_item[item_id] = sorted(actual)
    unknown_scope = set(scope) - set(parent_map)
    if unknown_scope:
        add_error(errors, "scope.item_unknown", f"revision receipt has unknown item IDs: {sorted(unknown_scope)}")
    return changed_item_ids, changed_by_item


def validate_concepts(
    parent: dict[str, Any],
    revised: dict[str, Any],
    receipt: dict[str, Any],
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    parent_concepts = parent.get("external_prerequisite_concepts", [])
    revised_concepts = revised.get("external_prerequisite_concepts", [])
    parent_map = {concept.get("concept_id"): concept for concept in parent_concepts if isinstance(concept, dict)}
    revised_map = {concept.get("concept_id"): concept for concept in revised_concepts if isinstance(concept, dict)}
    scope_entries = receipt.get("revision_scope", {}).get("concept_changes", [])
    scope = {
        entry.get("concept_id"): entry
        for entry in scope_entries
        if isinstance(entry, dict)
    }
    item_scope = {
        entry.get("item_id"): set(entry.get("fields", []))
        for entry in receipt.get("revision_scope", {}).get("item_changes", [])
        if isinstance(entry, dict)
    }
    item_external_revision = {
        item_id
        for item_id, fields in item_scope.items()
        if "external_prerequisite_concept_ids" in fields
    }
    removed: list[str] = []
    changed: dict[str, list[str]] = {}
    for concept_id, parent_concept in parent_map.items():
        revised_concept = revised_map.get(concept_id)
        scope_entry = scope.get(concept_id, {})
        permitted_groups = set(scope_entry.get("fields", []))
        if revised_concept is None:
            if scope_entry.get("record_removal_allowed") is not True:
                add_error(errors, "scope.concept_remove", f"removal of {concept_id} was not authorized")
                continue
            affected_items = set(parent_concept.get("supports_item_ids", []))
            if not affected_items <= item_external_revision:
                add_error(
                    errors,
                    "scope.concept_remove_items",
                    f"removing {concept_id} requires external-prerequisite review for items {sorted(affected_items - item_external_revision)}",
                )
            removed.append(concept_id)
            continue
        actual = changed_fields(parent_concept, revised_concept)
        permitted_fields = {
            field
            for group in permitted_groups
            for field in CONCEPT_FIELD_MAP.get(group, ())
        }
        unauthorized = actual - permitted_fields
        if unauthorized:
            add_error(errors, "scope.concept_field", f"{concept_id} changed unreviewed fields: {sorted(unauthorized)}")
        for group in permitted_groups:
            mapped = set(CONCEPT_FIELD_MAP.get(group, ()))
            if not (actual & mapped):
                add_error(errors, "scope.concept_unapplied", f"{concept_id}.{group} was marked revision_required but did not change")
        if actual:
            changed[concept_id] = sorted(actual)

    added = sorted(set(revised_map) - set(parent_map))
    for concept_id in added:
        supports = set(revised_map[concept_id].get("supports_item_ids", []))
        if not supports or not supports <= item_external_revision:
            add_error(
                errors,
                "scope.concept_add",
                f"new concept {concept_id} may support only items with reviewed external-prerequisite changes",
            )
    unknown_scope = set(scope) - set(parent_map)
    if unknown_scope:
        add_error(errors, "scope.concept_unknown", f"revision receipt has unknown parent concept IDs: {sorted(unknown_scope)}")
    return {
        "changed": changed,
        "added": added,
        "removed": removed,
    }


def validate_dependency_report(
    root: Path,
    candidate_path: Path,
    report_path: Path,
    report: dict[str, Any],
    errors: list[dict[str, str]],
) -> None:
    if report.get("valid") is not True or report.get("error_count") != 0:
        add_error(errors, "validation.failed", "revised dependency candidate did not pass base validation")
    inputs = report.get("inputs")
    if not isinstance(inputs, dict):
        add_error(errors, "validation.inputs", "base validation report inputs are missing")
        return
    if resolve_recorded_path(root, inputs.get("candidate")) != candidate_path:
        add_error(errors, "validation.candidate", "base validation report identifies another candidate")
    if inputs.get("candidate_sha256") != sha256(candidate_path):
        add_error(errors, "validation.candidate_hash", "revised candidate changed after base validation")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--parent-candidate", type=Path, required=True)
    parser.add_argument("--parent-review", type=Path, required=True)
    parser.add_argument("--revision-receipt", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--dependency-validation-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    paths = {
        "parent_candidate": args.parent_candidate.resolve(),
        "parent_review": args.parent_review.resolve(),
        "revision_receipt": args.revision_receipt.resolve(),
        "candidate": args.candidate.resolve(),
        "dependency_validation_report": args.dependency_validation_report.resolve(),
    }
    output_path = args.output.resolve()
    errors: list[dict[str, str]] = []
    metrics: dict[str, Any] = {}
    try:
        parent = load_object(paths["parent_candidate"])
        review = load_object(paths["parent_review"])
        receipt = load_object(paths["revision_receipt"])
        revised = load_object(paths["candidate"])
        dependency_report = load_object(paths["dependency_validation_report"])
        if receipt.get("mode") != "revision":
            add_error(errors, "receipt.mode", "revision receipt mode must be revision")
        verify_bound_file(root, receipt.get("parent_candidate", {}), paths["parent_candidate"], "parent_candidate", errors)
        verify_bound_file(root, receipt.get("parent_review", {}), paths["parent_review"], "parent_review", errors)
        contract_path = resolve_recorded_path(root, receipt.get("source_contract", {}).get("file"))
        if contract_path is None or not contract_path.is_file():
            add_error(errors, "binding.contract", "revision receipt Frozen Contract is missing")
        else:
            revision_preflight.verify_parent_candidate(
                root,
                contract_path,
                paths["parent_candidate"],
                parent,
            )
            revision_preflight.verify_review_binding(
                root,
                contract_path,
                paths["parent_candidate"],
                parent,
                review,
            )
        revision_preflight.verify_final_review(review)
        expected_item_scope, expected_concept_scope = revision_preflight.collect_revision_scope(parent, review)
        actual_scope = receipt.get("revision_scope", {})
        if actual_scope.get("item_changes") != expected_item_scope:
            add_error(errors, "receipt.item_scope", "revision receipt item scope does not match the parent review")
        if actual_scope.get("concept_changes") != expected_concept_scope:
            add_error(errors, "receipt.concept_scope", "revision receipt concept scope does not match the parent review")
        if receipt.get("parent_candidate", {}).get("next_model_id") != revision_preflight.next_model_id(parent.get("model_id", "")):
            add_error(errors, "receipt.next_model_id", "revision receipt next_model_id is invalid")
        expected_generator = {
            "agent": "grounded-curriculum-dependency-builder",
            "agent_version": "1.1",
            "skill": "build-curriculum-dependencies",
            "skill_version": "1.1",
        }
        generator = receipt.get("generated_by", {})
        for field, expected in expected_generator.items():
            if generator.get(field) != expected:
                add_error(errors, "receipt.generator", f"revision receipt generated_by.{field} is invalid")
        validate_dependency_report(root, paths["candidate"], paths["dependency_validation_report"], dependency_report, errors)
        validate_root(parent, revised, receipt, errors)
        changed_items, item_fields = validate_items(parent, revised, receipt, errors)
        concept_metrics = validate_concepts(parent, revised, receipt, errors)
        metrics = {
            "changed_item_ids": changed_items,
            "changed_item_fields": item_fields,
            "changed_concepts": concept_metrics["changed"],
            "added_concept_ids": concept_metrics["added"],
            "removed_concept_ids": concept_metrics["removed"],
        }
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        add_error(errors, "validator.input", str(exc))

    report = {
        "schema_version": "1.0",
        "validator": "curriculum-dependency-revision-v1",
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
        "inputs": {
            field: display_path(path, root)
            for field, path in paths.items()
        },
        "metrics": metrics,
    }
    for field, path in paths.items():
        report["inputs"][f"{field}_sha256"] = sha256(path) if path.is_file() else None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        for error in errors:
            print(f"ERROR [{error['code']}]: {error['message']}")
        return 1
    print(f"PASS: dependency revision stays within reviewed scope; report written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
