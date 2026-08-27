#!/usr/bin/env python3
"""Finalize and validate one pathway-constrained RQ2 lesson run."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
from typing import Any

from composer_common import (
    ComposerError,
    binding,
    count_english_prose_words,
    digest,
    display,
    load_json,
    require,
    resolve,
    verify_timestamp,
    write_json,
)


PYTHON_BLOCK_RE = re.compile(r"```(?:python|py)\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
SECTION_MARKER_RE = re.compile(r"<!--\s*section:\s*(SEC-[0-9]{2,})\s*-->")
VISIBLE_AUDIT_ID_RE = re.compile(r"\b(?:RC-[0-9]{3,}|BRQ-[0-9]{3,}|BRC-[A-Za-z0-9_.-]+)\b")


class Checks:
    def __init__(self) -> None:
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []

    def check(self, condition: bool, code: str, message: str) -> bool:
        if not condition:
            self.errors.append({"code": code, "message": message})
        return condition


def ordered_union(groups: list[list[str]]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for value in group:
            if value not in seen:
                seen.add(value)
                result.append(value)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--access-route", required=True)
    parser.add_argument("--prompt-version", required=True)
    parser.add_argument("--generated-at", required=True)
    args = parser.parse_args()

    try:
        root = Path(args.workspace_root).resolve()
        run_dir = resolve(root, args.run_dir)
        verify_timestamp(args.generated_at, "generated_at")
        require(run_dir.is_dir(), "run_dir.missing", f"run directory is missing: {run_dir}")
        receipt_path = run_dir / "composition-input-receipt.json"
        view_path = run_dir / "composition-input-view.json"
        lesson_path = run_dir / "lesson.md"
        map_path = run_dir / "lesson-map.json"
        code_path = run_dir / "code-validation.json"
        receipt = load_json(receipt_path)
        view = load_json(view_path)
        lesson = lesson_path.read_text(encoding="utf-8") if lesson_path.is_file() else ""
        lesson_map = load_json(map_path) if map_path.is_file() else {}
        code = load_json(code_path) if code_path.is_file() else {}
        checks = Checks()

        checks.check(receipt.get("schema_version") == "1.0", "receipt.schema", "receipt schema_version must be 1.0")
        checks.check(receipt.get("preparer") == "prepare-composition-inputs-v1", "receipt.preparer", "unexpected input preparer")
        checks.check(view.get("schema_version") == "1.0", "view.schema", "view schema_version must be 1.0")
        checks.check(receipt.get("output_view", {}).get("sha256") == digest(view_path), "view.hash", "composition input view hash differs from receipt")
        checks.check(resolve(root, receipt.get("output_view", {}).get("file", "")) == view_path, "view.path", "receipt identifies another input view")
        checks.check(receipt.get("run_id") == view.get("run_id"), "run_id.view", "receipt and view run IDs differ")
        checks.check(receipt.get("condition") == view.get("condition"), "condition.view", "receipt and view conditions differ")
        checks.check(receipt.get("topic") == view.get("topic"), "topic.view", "receipt and view topics differ")

        current_inputs: dict[str, Any] = {}
        for label, item in receipt.get("inputs", {}).items():
            if item is None:
                current_inputs[label] = None
                continue
            if not isinstance(item, dict) or not isinstance(item.get("file"), str):
                checks.check(False, f"input.{label}.binding", f"invalid input binding for {label}")
                continue
            path = resolve(root, item["file"])
            exists = path.is_file()
            checks.check(exists, f"input.{label}.missing", f"bound input is missing: {label}")
            if exists:
                checks.check(item.get("sha256") == digest(path), f"input.{label}.hash", f"bound input hash is stale: {label}")
                current_inputs[label] = binding(root, path)

        condition = view.get("condition")
        policy = view.get("composition_policy", {})
        profile = view.get("learner_profile")
        checks.check(condition in {"P0", "P1", "P2"}, "condition.invalid", "condition must be P0, P1, or P2")
        if condition == "P0":
            checks.check(profile is None, "P0.profile", "P0 input view must not expose a learner profile")
            checks.check(receipt.get("inputs", {}).get("profile") is None, "P0.profile_binding", "P0 receipt must not bind a profile")
            checks.check(policy.get("discipline_neutral_required") is True, "P0.neutral", "P0 must require discipline-neutral composition")
        else:
            checks.check(isinstance(profile, dict), f"{condition}.profile", f"{condition} input view must expose exactly one profile")
            checks.check(isinstance(receipt.get("inputs", {}).get("profile"), dict), f"{condition}.profile_binding", f"{condition} receipt must bind one profile")
        checks.check(policy.get("external_retrieval_allowed") is False, "policy.retrieval", "external retrieval must be forbidden")
        checks.check(policy.get("pathway_replanning_allowed") is False, "policy.replanning", "composition must not permit replanning")

        checks.check(lesson_path.is_file() and bool(lesson.strip()), "lesson.missing", "lesson.md is missing or empty")
        checks.check(lesson_map.get("schema_version") == "1.0", "map.schema", "lesson map schema_version must be 1.0")
        checks.check(lesson_map.get("run_id") == view.get("run_id"), "map.run_id", "lesson map run ID differs")
        checks.check(lesson_map.get("lesson_file") == "lesson.md", "map.lesson", "lesson map must identify lesson.md")

        h1_count = len(re.findall(r"(?m)^# [^#\n].*$", lesson))
        checks.check(h1_count == 1, "lesson.h1", "lesson must contain exactly one H1 title")
        audit_ids = VISIBLE_AUDIT_ID_RE.findall(lesson)
        checks.check(not audit_ids, "lesson.audit_ids", "student-facing lesson must not expose RC, BRQ, or BRC audit IDs")

        pathway = view.get("pathway", {})
        ordered_units = pathway.get("ordered_learning_units", [])
        sequence = pathway.get("instruction_sequence", [])
        units = {
            unit.get("unit_id"): unit for unit in ordered_units
            if isinstance(unit, dict) and isinstance(unit.get("unit_id"), str)
        }
        sections = lesson_map.get("sections")
        if not isinstance(sections, list):
            checks.check(False, "map.sections", "lesson map sections must be an array")
            sections = []
        section_ids: list[str] = []
        flattened_units: list[str] = []
        mapped_contract_items: list[str] = []
        mapped_bridge_ids: list[str] = []
        for index, section in enumerate(sections, start=1):
            if not isinstance(section, dict):
                checks.check(False, "map.section", "each lesson-map section must be an object")
                continue
            expected_section_id = f"SEC-{index:02d}"
            section_id = section.get("section_id")
            heading = section.get("heading")
            unit_ids = section.get("unit_ids")
            contract_ids = section.get("contract_item_ids")
            bridge_ids = section.get("bridge_contract_ids")
            checks.check(section_id == expected_section_id, "map.section_id", f"expected section ID {expected_section_id}")
            checks.check(isinstance(heading, str) and bool(heading.strip()) and "#" not in heading, "map.heading", f"{section_id} needs a plain heading")
            checks.check(isinstance(unit_ids, list) and bool(unit_ids), "map.units", f"{section_id} needs one or more units")
            checks.check(isinstance(contract_ids, list) and len(contract_ids) == len(set(contract_ids)), "map.contract_items", f"{section_id} contract items must be a unique array")
            checks.check(isinstance(bridge_ids, list) and len(bridge_ids) == len(set(bridge_ids)), "map.bridge_ids", f"{section_id} bridge IDs must be a unique array")
            if not isinstance(unit_ids, list) or not isinstance(contract_ids, list) or not isinstance(bridge_ids, list):
                continue
            section_ids.append(section_id)
            flattened_units.extend(unit_ids)
            expected_items = ordered_union([
                units.get(unit_id, {}).get("contract_item_ids", []) for unit_id in unit_ids
            ])
            expected_bridges = ordered_union([[
                units.get(unit_id, {}).get("bridge_contract_id")
            ] if units.get(unit_id, {}).get("unit_type") == "prerequisite_bridge" else [] for unit_id in unit_ids])
            checks.check(all(unit_id in units for unit_id in unit_ids), "map.unknown_unit", f"{section_id} contains an unknown pathway unit")
            checks.check(contract_ids == expected_items, "map.item_scope", f"{section_id} Contract mapping differs from its pathway units")
            checks.check(bridge_ids == expected_bridges, "map.bridge_scope", f"{section_id} bridge mapping differs from its pathway units")
            mapped_contract_items.extend(contract_ids)
            mapped_bridge_ids.extend(bridge_ids)
            if isinstance(heading, str) and isinstance(section_id, str):
                pattern = rf"<!--\s*section:\s*{re.escape(section_id)}\s*-->\s*\n##\s+{re.escape(heading.strip())}\s*$"
                checks.check(re.search(pattern, lesson, re.MULTILINE) is not None, "lesson.section_anchor", f"missing exact hidden anchor and H2 heading for {section_id}")

        checks.check(flattened_units == sequence, "map.sequence", "flattened lesson-map units must exactly equal instruction_sequence")
        checks.check(SECTION_MARKER_RE.findall(lesson) == section_ids, "lesson.section_order", "lesson section anchors must exactly match map order")
        selected = pathway.get("selected_item_ids", [])
        checks.check(len(mapped_contract_items) == len(set(mapped_contract_items)), "map.item_duplicate", "a Contract item is mapped more than once")
        checks.check(set(mapped_contract_items) == set(selected), "map.selected_coverage", "lesson map must cover exactly every selected Contract item")
        expected_bridge_ids = [
            unit.get("bridge_contract_id") for unit in ordered_units
            if unit.get("unit_type") == "prerequisite_bridge"
        ]
        checks.check(mapped_bridge_ids == expected_bridge_ids, "map.bridge_coverage", "lesson map must cover released bridge units in pathway order")

        protocol = view.get("word_count_protocol", {})
        prose_count = count_english_prose_words(lesson)
        minimum, maximum = protocol.get("minimum"), protocol.get("maximum")
        word_count_compliant = isinstance(minimum, int) and isinstance(maximum, int) and minimum <= prose_count <= maximum
        checks.check(word_count_compliant, "lesson.word_count", f"English prose count {prose_count} is outside {minimum}-{maximum}")

        code_blocks = PYTHON_BLOCK_RE.findall(lesson)
        code_results = code.get("blocks") if isinstance(code.get("blocks"), list) else []
        expected_code_status = "no_code" if not code_blocks else "passed"
        checks.check(code.get("overall_status") == expected_code_status, "code.status", f"code validation must report {expected_code_status}")
        checks.check(len(code_results) == len(code_blocks), "code.count", "code-validation block count differs from lesson")
        for index, block in enumerate(code_blocks):
            if index < len(code_results):
                expected_hash = hashlib.sha256(block.encode("utf-8")).hexdigest()
                checks.check(code_results[index].get("code_sha256") == expected_hash, "code.hash", f"code block {index + 1} hash differs")
                checks.check(code_results[index].get("execution_status") == "passed", "code.execution", f"code block {index + 1} did not execute successfully")

        manifest = {
            "schema_version": "1.0",
            "composer": "pathway-constrained-teaching-composer-v1",
            "run_id": view.get("run_id"),
            "condition": condition,
            "topic": view.get("topic"),
            "profile_id": profile.get("profile_id") if isinstance(profile, dict) else None,
            "generation": {
                "provider": args.provider,
                "model": args.model,
                "access_route": args.access_route,
                "prompt_version": args.prompt_version,
                "generated_at": args.generated_at,
            },
            "inputs": {
                "composition_input_receipt": binding(root, receipt_path),
                "composition_input_view": binding(root, view_path),
                **current_inputs,
            },
            "outputs": {
                "lesson": binding(root, lesson_path) if lesson_path.is_file() else None,
                "lesson_map": binding(root, map_path) if map_path.is_file() else None,
                "code_validation": binding(root, code_path) if code_path.is_file() else None,
            },
            "word_count_protocol": protocol,
            "observed_english_prose_word_count": prose_count,
        }
        manifest_path = run_dir / "lesson-manifest.json"
        write_json(manifest_path, manifest)
        report = {
            "schema_version": "1.0",
            "validator": "validate-composer-outputs-v1",
            "run_id": view.get("run_id"),
            "condition": condition,
            "topic": view.get("topic"),
            "valid": not checks.errors,
            "error_count": len(checks.errors),
            "warning_count": len(checks.warnings),
            "errors": checks.errors,
            "warnings": checks.warnings,
            "metrics": {
                "selected_contract_item_count": len(selected),
                "mapped_contract_item_count": len(mapped_contract_items),
                "excluded_contract_item_count": len(pathway.get("excluded_item_ids", [])),
                "learning_unit_count": len(sequence),
                "mapped_learning_unit_count": len(flattened_units),
                "released_bridge_count": len(expected_bridge_ids),
                "mapped_bridge_count": len(mapped_bridge_ids),
                "section_count": len(sections),
                "python_code_block_count": len(code_blocks),
                "english_prose_word_count": prose_count,
                "word_count_compliant": word_count_compliant,
            },
            "validation_scope": {
                "input_bindings": True,
                "condition_context_isolation": True,
                "declared_selected_content_mapping": True,
                "pathway_order": True,
                "released_bridge_mapping": True,
                "python_execution": True,
                "word_count": True,
                "semantic_mathematical_correctness_assessed": False,
                "pedagogical_quality_assessed": False,
            },
            "manifest": binding(root, manifest_path),
            "validated_at": args.generated_at,
        }
        write_json(run_dir / "lesson-validation-report.json", report)
        if checks.errors:
            print(f"FAIL: invalid composed lesson ({len(checks.errors)} errors)")
            for error in checks.errors:
                print(f"- [{error['code']}] {error['message']}")
            return 1
        print(f"PASS: valid {condition} composed lesson; prose_words={prose_count}")
        return 0
    except ComposerError as exc:
        print(f"FAIL [{exc.code}]: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"FAIL [unexpected]: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
