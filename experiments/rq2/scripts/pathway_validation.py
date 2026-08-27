#!/usr/bin/env python3
"""Shared deterministic helpers for RQ2 pathway validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SOURCE_KEYS = ("contract_id", "contract_version", "sha256")


def load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def duplicate_values(values: list[Any]) -> list[Any]:
    seen: set[Any] = set()
    duplicates: list[Any] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def source_binding_errors(
    expected: dict[str, Any], actual: dict[str, Any], label: str
) -> list[str]:
    errors: list[str] = []
    for key in SOURCE_KEYS:
        if actual.get(key) != expected.get(key):
            errors.append(
                f"{label} source_contract.{key} does not match the common-core binding"
            )
    return errors


def unit_map_and_errors(pathway: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    units = pathway.get("learning_units")
    order = pathway.get("instruction_sequence")
    if not isinstance(units, list) or not units:
        return {}, ["learning_units must be a non-empty array"]
    if not isinstance(order, list) or not order:
        return {}, ["instruction_sequence must be a non-empty array"]

    unit_map: dict[str, dict[str, Any]] = {}
    for index, unit in enumerate(units):
        if not isinstance(unit, dict):
            errors.append(f"learning_units[{index}] must be an object")
            continue
        unit_id = unit.get("unit_id")
        if not isinstance(unit_id, str) or not unit_id:
            errors.append(f"learning_units[{index}].unit_id must be a non-empty string")
            continue
        if unit_id in unit_map:
            errors.append(f"duplicate unit_id: {unit_id}")
        unit_map[unit_id] = unit
        for field in ("prerequisite_unit_ids", "learning_objective_ids", "contract_item_ids"):
            if not isinstance(unit.get(field), list):
                errors.append(f"learning unit {unit_id} field {field} must be an array")

    for duplicate in duplicate_values(order):
        errors.append(f"duplicate unit ID in instruction_sequence: {duplicate}")
    if set(order) != set(unit_map):
        missing = sorted(set(unit_map) - set(order))
        unknown = sorted(set(order) - set(unit_map))
        if missing:
            errors.append(f"instruction_sequence omits learning units: {missing}")
        if unknown:
            errors.append(f"instruction_sequence references unknown learning units: {unknown}")
    return unit_map, errors


def graph_errors(pathway: dict[str, Any], unit_map: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    order = pathway.get("instruction_sequence", [])
    positions = {unit_id: index for index, unit_id in enumerate(order)}
    adjacency: dict[str, list[str]] = {unit_id: [] for unit_id in unit_map}

    for unit_id, unit in unit_map.items():
        prerequisites = unit.get("prerequisite_unit_ids", [])
        for duplicate in duplicate_values(prerequisites):
            errors.append(f"learning unit {unit_id} repeats prerequisite {duplicate}")
        for prerequisite in prerequisites:
            if prerequisite == unit_id:
                errors.append(f"learning unit {unit_id} cannot depend on itself")
            elif prerequisite not in unit_map:
                errors.append(f"learning unit {unit_id} has unknown prerequisite {prerequisite}")
            else:
                adjacency[prerequisite].append(unit_id)
                if positions.get(prerequisite, len(order)) >= positions.get(unit_id, -1):
                    errors.append(
                        f"instruction_sequence places {unit_id} before prerequisite {prerequisite}"
                    )

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(unit_id: str) -> None:
        if unit_id in visiting:
            errors.append(f"prerequisite graph contains a cycle at {unit_id}")
            return
        if unit_id in visited:
            return
        visiting.add(unit_id)
        for dependent in adjacency.get(unit_id, []):
            visit(dependent)
        visiting.remove(unit_id)
        visited.add(unit_id)

    for unit_id in unit_map:
        visit(unit_id)
    return errors


def flattened_unit_values(unit_map: dict[str, dict[str, Any]], field: str) -> set[str]:
    return {
        value
        for unit in unit_map.values()
        for value in unit.get(field, [])
        if isinstance(value, str)
    }


def simplified_decisions(pathway: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for decision in pathway.get("selection_decisions", []):
        if isinstance(decision, dict) and isinstance(decision.get("item_id"), str):
            result[decision["item_id"]] = decision.get("decision", "")
    return result


def write_report(path: Path | None, report: dict[str, Any]) -> None:
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if path is None:
        print(rendered, end="")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
