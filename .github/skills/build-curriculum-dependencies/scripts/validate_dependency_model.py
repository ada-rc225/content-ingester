#!/usr/bin/env python3
"""Validate a curriculum dependency candidate against a released Frozen Contract."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import re
from pathlib import Path
from typing import Any

CHECKSUM_RE = re.compile(r"^([a-f0-9]{64})\s+\*?frozen_reference_contract\.json\s*$")
ITEM_ID_RE = re.compile(r"^RC-[0-9]{3,}$")
CONCEPT_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BRIDGE_ID_RE = re.compile(r"^BR-[A-Z0-9]+(?:-[A-Z0-9]+)*-v[0-9]+$")
HASH_RE = re.compile(r"^[a-f0-9]{64}$")
DIRECTED_FIELDS = (
    "hard_dependencies",
    "explanatory_dependencies",
    "implementation_dependencies",
)
DISJOINT_FIELDS = DIRECTED_FIELDS + ("co_requisite_item_ids",)


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


def resolve_recorded_path(root: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def add_error(errors: list[dict[str, str]], code: str, message: str) -> None:
    errors.append({"code": code, "message": message})


def require_keys(
    value: dict[str, Any], required: set[str], allowed: set[str], location: str,
    errors: list[dict[str, str]],
) -> None:
    missing = required - set(value)
    extra = set(value) - allowed
    if missing:
        add_error(errors, "schema.required", f"{location} is missing fields: {sorted(missing)}")
    if extra:
        add_error(errors, "schema.additional", f"{location} has unsupported fields: {sorted(extra)}")


def string_array(
    value: Any, pattern: re.Pattern[str], location: str, errors: list[dict[str, str]]
) -> list[str]:
    if not isinstance(value, list):
        add_error(errors, "schema.type", f"{location} must be an array")
        return []
    if not all(isinstance(item, str) and pattern.fullmatch(item) for item in value):
        add_error(errors, "schema.pattern", f"{location} contains an invalid identifier")
    if len(value) != len(set(value)):
        add_error(errors, "schema.unique", f"{location} must contain unique values")
    return [item for item in value if isinstance(item, str)]


def validate_candidate_shape(candidate: dict[str, Any], errors: list[dict[str, str]]) -> None:
    root_fields = {
        "schema_version", "model_id", "lifecycle_status", "source_contract",
        "builder", "items", "external_prerequisite_concepts", "review_status", "approval",
    }
    require_keys(candidate, root_fields, root_fields, "$", errors)
    constants = {
        "schema_version": "1.0",
        "lifecycle_status": "candidate",
        "review_status": "unreviewed",
        "approval": None,
    }
    for field, expected in constants.items():
        if candidate.get(field) != expected:
            add_error(errors, "schema.const", f"{field} must equal {expected!r}")
    if not isinstance(candidate.get("model_id"), str) or not re.fullmatch(
        r"[a-z0-9]+(?:-[a-z0-9]+)*-dependencies-v[0-9]+", candidate.get("model_id", "")
    ):
        add_error(errors, "schema.pattern", "model_id has an invalid format")

    binding = candidate.get("source_contract")
    binding_fields = {"contract_id", "contract_version", "topic", "file", "sha256"}
    if not isinstance(binding, dict):
        add_error(errors, "schema.type", "source_contract must be an object")
    else:
        require_keys(binding, binding_fields, binding_fields, "source_contract", errors)
        for field in ("contract_id", "topic", "file"):
            if not isinstance(binding.get(field), str) or not binding.get(field):
                add_error(errors, "schema.type", f"source_contract.{field} must be a non-empty string")
        if not isinstance(binding.get("contract_version"), str) or not re.fullmatch(
            r"[0-9]+\.[0-9]+\.[0-9]+", binding.get("contract_version", "")
        ):
            add_error(errors, "schema.pattern", "source_contract.contract_version is invalid")
        if not isinstance(binding.get("sha256"), str) or not HASH_RE.fullmatch(binding.get("sha256", "")):
            add_error(errors, "schema.pattern", "source_contract.sha256 is invalid")

    builder = candidate.get("builder")
    builder_fields = {"agent", "agent_version", "skill", "skill_version", "generated_at"}
    if not isinstance(builder, dict):
        add_error(errors, "schema.type", "builder must be an object")
    else:
        require_keys(builder, builder_fields, builder_fields, "builder", errors)
        expected_builder = {
            "agent": "grounded-curriculum-dependency-builder",
            "skill": "build-curriculum-dependencies",
        }
        for field, expected in expected_builder.items():
            if builder.get(field) != expected:
                add_error(errors, "schema.const", f"builder.{field} must equal {expected!r}")
        for field in ("agent_version", "skill_version"):
            if builder.get(field) not in {"1.0", "1.1"}:
                add_error(errors, "schema.enum", f"builder.{field} must be 1.0 or 1.1")
        generated_at = builder.get("generated_at")
        try:
            datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        except (AttributeError, ValueError):
            add_error(errors, "schema.format", "builder.generated_at must be an ISO 8601 date-time")

    item_fields = {
        "item_id", "hard_dependencies", "explanatory_dependencies",
        "implementation_dependencies", "co_requisite_item_ids", "recommended_neighbours",
        "external_prerequisite_concept_ids", "fallback_when_explanatory_dependencies_omitted",
        "rationale", "confidence", "review_status",
    }
    items = candidate.get("items")
    if not isinstance(items, list) or not items:
        add_error(errors, "schema.type", "items must be a non-empty array")
        items = []
    for index, item in enumerate(items):
        location = f"items[{index}]"
        if not isinstance(item, dict):
            add_error(errors, "schema.type", f"{location} must be an object")
            continue
        require_keys(item, item_fields, item_fields, location, errors)
        if not isinstance(item.get("item_id"), str) or not ITEM_ID_RE.fullmatch(item.get("item_id", "")):
            add_error(errors, "schema.pattern", f"{location}.item_id is invalid")
        for field in DISJOINT_FIELDS + ("recommended_neighbours",):
            string_array(item.get(field), ITEM_ID_RE, f"{location}.{field}", errors)
        string_array(
            item.get("external_prerequisite_concept_ids"), CONCEPT_ID_RE,
            f"{location}.external_prerequisite_concept_ids", errors,
        )
        fallback = item.get("fallback_when_explanatory_dependencies_omitted")
        if not isinstance(fallback, dict):
            add_error(errors, "schema.type", f"{location}.fallback must be an object")
        else:
            require_keys(fallback, {"allowed", "instruction"}, {"allowed", "instruction"}, f"{location}.fallback", errors)
            if not isinstance(fallback.get("allowed"), bool):
                add_error(errors, "schema.type", f"{location}.fallback.allowed must be boolean")
            instruction = fallback.get("instruction")
            if fallback.get("allowed") is True and (not isinstance(instruction, str) or not instruction):
                add_error(errors, "schema.type", f"{location}.fallback instruction is required")
            if fallback.get("allowed") is False and instruction is not None:
                add_error(errors, "schema.const", f"{location}.fallback instruction must be null")
        rationale = item.get("rationale")
        if not isinstance(rationale, list) or not rationale or not all(isinstance(text, str) and text for text in rationale):
            add_error(errors, "schema.type", f"{location}.rationale must contain non-empty strings")
        elif len(rationale) != len(set(rationale)):
            add_error(errors, "schema.unique", f"{location}.rationale must be unique")
        if item.get("confidence") not in {"low", "medium", "high"}:
            add_error(errors, "schema.enum", f"{location}.confidence is invalid")
        if item.get("review_status") != "unreviewed":
            add_error(errors, "schema.const", f"{location}.review_status must be unreviewed")

    concept_fields = {
        "concept_id", "name", "need_type", "supports_item_ids", "bridge_candidate_id",
        "status", "content_boundary", "rationale",
    }
    concepts = candidate.get("external_prerequisite_concepts")
    if not isinstance(concepts, list):
        add_error(errors, "schema.type", "external_prerequisite_concepts must be an array")
        concepts = []
    for index, concept in enumerate(concepts):
        location = f"external_prerequisite_concepts[{index}]"
        if not isinstance(concept, dict):
            add_error(errors, "schema.type", f"{location} must be an object")
            continue
        require_keys(concept, concept_fields, concept_fields, location, errors)
        if not isinstance(concept.get("concept_id"), str) or not CONCEPT_ID_RE.fullmatch(concept.get("concept_id", "")):
            add_error(errors, "schema.pattern", f"{location}.concept_id is invalid")
        for field in ("name", "content_boundary", "rationale"):
            if not isinstance(concept.get(field), str) or not concept.get(field):
                add_error(errors, "schema.type", f"{location}.{field} must be a non-empty string")
        if concept.get("need_type") not in {"required", "recommended"}:
            add_error(errors, "schema.enum", f"{location}.need_type is invalid")
        string_array(concept.get("supports_item_ids"), ITEM_ID_RE, f"{location}.supports_item_ids", errors)
        if not isinstance(concept.get("bridge_candidate_id"), str) or not BRIDGE_ID_RE.fullmatch(concept.get("bridge_candidate_id", "")):
            add_error(errors, "schema.pattern", f"{location}.bridge_candidate_id is invalid")
        if concept.get("status") != "candidate":
            add_error(errors, "schema.const", f"{location}.status must be candidate")


def release_errors(
    root: Path, contract_path: Path, contract: dict[str, Any], errors: list[dict[str, str]]
) -> str:
    contract_hash = sha256(contract_path)
    release_path = contract_path.with_name("release_gate_report.json")
    checksum_path = contract_path.with_name("frozen_contract.sha256")
    validation_path = contract_path.with_name("frozen_contract_validation_report.json")
    if contract_path.name != "frozen_reference_contract.json":
        add_error(errors, "contract.filename", "contract must be named frozen_reference_contract.json")
    if contract.get("lifecycle_status") != "frozen" or not isinstance(contract.get("approval"), dict):
        add_error(errors, "contract.lifecycle", "contract is not approved and frozen")
    for path, code in (
        (release_path, "release.missing_report"),
        (checksum_path, "release.missing_checksum"),
        (validation_path, "release.missing_validation"),
    ):
        if not path.is_file():
            add_error(errors, code, f"missing release artifact: {path}")
    if checksum_path.is_file():
        match = CHECKSUM_RE.fullmatch(checksum_path.read_text(encoding="utf-8"))
        if match is None or match.group(1) != contract_hash:
            add_error(errors, "release.checksum", "frozen contract checksum is invalid or mismatched")
    if release_path.is_file():
        release = load_object(release_path)
        outputs = release.get("outputs", {})
        if release.get("status") != "released":
            add_error(errors, "release.status", "release gate status is not released")
        if release.get("contract_id") != contract.get("contract_id"):
            add_error(errors, "release.contract_id", "release contract_id does not match")
        if release.get("contract_version") != contract.get("contract_version"):
            add_error(errors, "release.contract_version", "release contract_version does not match")
        if outputs.get("frozen_contract_sha256") != contract_hash:
            add_error(errors, "release.contract_hash", "release report Contract hash does not match")
        recorded = outputs.get("frozen_contract")
        if not isinstance(recorded, str) or resolve_recorded_path(root, recorded) != contract_path:
            add_error(errors, "release.contract_path", "release report identifies a different Contract")
    if validation_path.is_file():
        validation = load_object(validation_path)
        if validation.get("valid") is not True or validation.get("error_count") != 0:
            add_error(errors, "release.validation", "frozen Contract validation did not pass")
    return contract_hash


def find_cycle(graph: dict[str, set[str]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            start = stack.index(node)
            return stack[start:] + [node]
        if node in visited:
            return None
        visiting.add(node)
        stack.append(node)
        for dependency in sorted(graph.get(node, set())):
            cycle = visit(dependency)
            if cycle:
                return cycle
        stack.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in sorted(graph):
        cycle = visit(node)
        if cycle:
            return cycle
    return None


def validate_semantics(
    root: Path,
    contract_path: Path,
    contract: dict[str, Any],
    contract_hash: str,
    candidate: dict[str, Any],
    errors: list[dict[str, str]],
) -> dict[str, Any]:
    binding = candidate.get("source_contract", {})
    expected_binding = {
        "contract_id": contract.get("contract_id"),
        "contract_version": contract.get("contract_version"),
        "topic": contract.get("topic"),
        "sha256": contract_hash,
    }
    for key, expected in expected_binding.items():
        if binding.get(key) != expected:
            add_error(errors, f"binding.{key}", f"source_contract.{key} does not match Frozen Contract")
    recorded_file = binding.get("file")
    if not isinstance(recorded_file, str) or resolve_recorded_path(root, recorded_file) != contract_path:
        add_error(errors, "binding.file", "source_contract.file identifies a different Frozen Contract")

    contract_ids = {
        item.get("item_id")
        for item in contract.get("contract_items", [])
        if item.get("review", {}).get("decision") != "excluded"
    }
    entries = candidate.get("items", [])
    entry_ids = [entry.get("item_id") for entry in entries if isinstance(entry, dict)]
    if len(entry_ids) != len(set(entry_ids)):
        add_error(errors, "items.duplicate", "candidate contains duplicate RC item records")
    if set(entry_ids) != contract_ids:
        add_error(
            errors,
            "items.coverage",
            f"candidate item set must equal non-excluded Contract items; missing={sorted(contract_ids - set(entry_ids))}, unknown={sorted(set(entry_ids) - contract_ids)}",
        )

    entry_map = {entry.get("item_id"): entry for entry in entries if isinstance(entry, dict)}
    graph: dict[str, set[str]] = {item_id: set() for item_id in contract_ids}
    for item_id, entry in entry_map.items():
        if item_id not in contract_ids:
            continue
        category_sets: dict[str, set[str]] = {}
        for field in DISJOINT_FIELDS:
            values = set(entry.get(field, []))
            category_sets[field] = values
            unknown = values - contract_ids
            if unknown:
                add_error(errors, "relationship.unknown", f"{item_id}.{field} has unknown items: {sorted(unknown)}")
            if item_id in values:
                add_error(errors, "relationship.self", f"{item_id}.{field} contains a self-reference")
        for index, left in enumerate(DISJOINT_FIELDS):
            for right in DISJOINT_FIELDS[index + 1 :]:
                overlap = category_sets[left] & category_sets[right]
                if overlap:
                    add_error(
                        errors,
                        "relationship.overlap",
                        f"{item_id} repeats {sorted(overlap)} across {left} and {right}",
                    )
        directed = set().union(*(category_sets[field] for field in DIRECTED_FIELDS))
        graph[item_id].update(directed & contract_ids)
        fallback = entry.get("fallback_when_explanatory_dependencies_omitted", {})
        explanatory = category_sets.get("explanatory_dependencies", set())
        if explanatory and fallback.get("allowed") is not True:
            add_error(errors, "fallback.missing", f"{item_id} has explanatory dependencies but no allowed fallback")
        if not explanatory and fallback.get("allowed") is True:
            add_error(errors, "fallback.unneeded", f"{item_id} allows a fallback without explanatory dependencies")

    cycle = find_cycle(graph)
    if cycle:
        add_error(errors, "relationship.cycle", "directed dependency cycle: " + " -> ".join(cycle))

    for item_id, entry in entry_map.items():
        for co_item in entry.get("co_requisite_item_ids", []):
            if co_item in entry_map and item_id not in entry_map[co_item].get("co_requisite_item_ids", []):
                add_error(errors, "relationship.corequisite", f"co-requisite relation {item_id}<->{co_item} is not reciprocal")

    concepts = candidate.get("external_prerequisite_concepts", [])
    concept_ids = [concept.get("concept_id") for concept in concepts if isinstance(concept, dict)]
    if len(concept_ids) != len(set(concept_ids)):
        add_error(errors, "concepts.duplicate", "candidate contains duplicate external concept IDs")
    concept_map = {concept.get("concept_id"): concept for concept in concepts if isinstance(concept, dict)}
    for concept_id, concept in concept_map.items():
        supports = set(concept.get("supports_item_ids", []))
        unknown = supports - contract_ids
        if unknown:
            add_error(errors, "concepts.unknown_item", f"{concept_id} supports unknown items: {sorted(unknown)}")
        for item_id in supports & contract_ids:
            if item_id in entry_map and concept_id not in entry_map[item_id].get("external_prerequisite_concept_ids", []):
                add_error(errors, "concepts.reverse_binding", f"{concept_id} lists {item_id}, but the item does not reference the concept")
    for item_id, entry in entry_map.items():
        for concept_id in entry.get("external_prerequisite_concept_ids", []):
            if concept_id not in concept_map:
                add_error(errors, "concepts.unknown", f"{item_id} references unknown concept {concept_id}")
            elif item_id not in concept_map[concept_id].get("supports_item_ids", []):
                add_error(errors, "concepts.forward_binding", f"{item_id} references {concept_id}, but the concept does not list the item")

    return {
        "contract_item_count": len(contract_ids),
        "candidate_item_count": len(entry_ids),
        "directed_dependency_count": sum(len(values) for values in graph.values()),
        "external_prerequisite_concept_count": len(concept_ids),
        "directed_graph_acyclic": cycle is None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--schema", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(args.workspace_root).resolve()
    contract_path = args.contract.resolve()
    candidate_path = args.candidate.resolve()
    schema_path = args.schema.resolve() if args.schema else Path(__file__).resolve().parents[1] / "references" / "dependency-model.schema.json"
    output_path = args.output.resolve()
    errors: list[dict[str, str]] = []
    metrics: dict[str, Any] = {}
    try:
        contract = load_object(contract_path)
        candidate = load_object(candidate_path)
        load_object(schema_path)
        contract_hash = release_errors(root, contract_path, contract, errors)
        validate_candidate_shape(candidate, errors)
        metrics = validate_semantics(root, contract_path, contract, contract_hash, candidate, errors)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        add_error(errors, "validator.input", str(exc))
    report = {
        "schema_version": "1.0",
        "validator": "curriculum-dependency-model-v1",
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors,
        "inputs": {
            "contract": display_path(contract_path, root),
            "contract_sha256": sha256(contract_path) if contract_path.is_file() else None,
            "candidate": display_path(candidate_path, root),
            "candidate_sha256": sha256(candidate_path) if candidate_path.is_file() else None,
            "schema": display_path(schema_path, root),
            "schema_sha256": sha256(schema_path) if schema_path.is_file() else None,
        },
        "metrics": metrics,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        for error in errors:
            print(f"ERROR [{error['code']}]: {error['message']}")
        return 1
    print(f"PASS: dependency candidate valid; report written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
