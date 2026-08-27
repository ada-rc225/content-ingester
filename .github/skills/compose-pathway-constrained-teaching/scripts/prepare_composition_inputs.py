#!/usr/bin/env python3
"""Prepare a condition-isolated, hash-bound context for one RQ2 lesson."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

from composer_common import (
    ComposerError,
    binding,
    digest,
    display,
    load_json,
    require,
    resolve,
    verify_binding,
    verify_timestamp,
    write_json,
)


RUN_ID_RE = re.compile(r"^[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)*$")


def ordered_union(groups: list[list[str]]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for group in groups:
        for value in group:
            if value not in seen:
                result.append(value)
                seen.add(value)
    return result


def validate_word_protocol(protocol: dict[str, Any], condition: str, topic: str) -> None:
    require(protocol.get("schema_version") == "1.0", "word_protocol.schema", "word protocol schema_version must be 1.0")
    require(protocol.get("status") in {"draft_for_pilot", "frozen"}, "word_protocol.status", "word protocol must be draft_for_pilot or frozen")
    require(protocol.get("topic") == topic, "word_protocol.topic", "word protocol topic differs from pathway")
    require(protocol.get("language") == "English", "word_protocol.language", "Composer v1.0 supports English only")
    require(protocol.get("enabled") is True, "word_protocol.enabled", "word-count control must be enabled")
    minimum, maximum = protocol.get("minimum"), protocol.get("maximum")
    require(isinstance(minimum, int) and isinstance(maximum, int) and 1 <= minimum <= maximum, "word_protocol.range", "word range must satisfy 1 <= minimum <= maximum")
    require(protocol.get("counting_method") == "english_prose_v1", "word_protocol.method", "unsupported word-count method")
    applies = protocol.get("applies_to_conditions")
    require(isinstance(applies, list) and set(applies) == {"P0", "P1", "P2"}, "word_protocol.conditions", "one protocol must apply to P0, P1, and P2")
    require(condition in applies, "word_protocol.condition", "word protocol does not include this condition")


def find_bridge(catalog: dict[str, Any], contract_id: str) -> dict[str, Any] | None:
    for item in catalog.get("bridges", []):
        if isinstance(item, dict) and item.get("bridge_contract_id") == contract_id:
            return item
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--pathway", required=True)
    parser.add_argument("--pathway-validation-report", required=True)
    parser.add_argument("--bridge-catalog")
    parser.add_argument("--word-count-protocol", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--prepared-at", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    try:
        root = Path(args.workspace_root).resolve()
        pathway_path = resolve(root, args.pathway)
        report_path = resolve(root, args.pathway_validation_report)
        protocol_path = resolve(root, args.word_count_protocol)
        output_dir = resolve(root, args.output_dir)
        require(RUN_ID_RE.fullmatch(args.run_id) is not None, "run_id.format", "run-id has an invalid format")
        verify_timestamp(args.prepared_at, "prepared_at")
        require(not output_dir.exists(), "output.exists", f"output directory already exists: {output_dir}")

        pathway = load_json(pathway_path)
        report = load_json(report_path)
        protocol = load_json(protocol_path)
        condition = pathway.get("condition")
        topic = pathway.get("topic")
        require(condition in {"P0", "P1", "P2"}, "pathway.condition", "pathway condition must be P0, P1, or P2")
        require(pathway.get("plan_status") == "complete", "pathway.status", "Composer requires a complete pathway")
        require(isinstance(topic, str) and topic, "pathway.topic", "pathway topic is missing")
        require(report.get("valid") is True and report.get("error_count") == 0, "pathway_report.valid", "pathway validation report is not passing")
        require(report.get("pathway_sha256") == digest(pathway_path), "pathway_report.hash", "pathway validation report does not bind the supplied pathway")
        require(report.get("condition") == condition, "pathway_report.condition", "pathway validation report condition differs")
        validate_word_protocol(protocol, condition, topic)

        authorities = pathway.get("source_authorities")
        require(isinstance(authorities, dict), "pathway.authorities", "source_authorities must be an object")
        contract_path, contract = verify_binding(root, authorities.get("reference_contract"), "reference_contract")
        request_path, request = verify_binding(root, pathway.get("learning_request_binding"), "learning_request")
        require(contract.get("lifecycle_status") == "frozen", "reference_contract.status", "reference contract is not frozen")
        require(request.get("schema_version") == "1.0", "learning_request.schema", "learning request schema_version must be 1.0")
        require(request.get("topic") == topic, "learning_request.topic", "learning request topic differs")

        profile_path: Path | None = None
        profile: dict[str, Any] | None = None
        if condition == "P0":
            require(pathway.get("profile_binding") is None, "P0.profile", "P0 must not bind a profile")
        else:
            profile_path, profile = verify_binding(root, pathway.get("profile_binding"), "profile")
            require(profile.get("profile_id") == pathway["profile_binding"].get("profile_id"), "profile.id", "profile ID differs from pathway binding")

        selected = pathway.get("selection", {}).get("selected_item_ids")
        excluded = pathway.get("selection", {}).get("excluded_item_ids")
        require(isinstance(selected, list) and selected, "selection.selected", "selected_item_ids must be non-empty")
        require(isinstance(excluded, list), "selection.excluded", "excluded_item_ids must be an array")
        require(not (set(selected) & set(excluded)), "selection.partition", "selected and excluded items overlap")
        contract_items = {
            item.get("item_id"): item for item in contract.get("contract_items", [])
            if isinstance(item, dict) and isinstance(item.get("item_id"), str)
        }
        require(set(selected) <= set(contract_items), "selection.contract", "selected items are absent from the reference contract")
        selected_items = [contract_items[item_id] for item_id in selected]

        units_by_id = {
            item.get("unit_id"): item for item in pathway.get("learning_units", [])
            if isinstance(item, dict) and isinstance(item.get("unit_id"), str)
        }
        sequence = pathway.get("instruction_sequence")
        require(isinstance(sequence, list) and set(sequence) == set(units_by_id) and len(sequence) == len(units_by_id), "pathway.sequence", "instruction sequence must cover every unit exactly once")
        ordered_units = [units_by_id[unit_id] for unit_id in sequence]
        mapped_items = ordered_union([
            unit.get("contract_item_ids", []) for unit in ordered_units
            if isinstance(unit.get("contract_item_ids"), list)
        ])
        raw_mapped_items = [
            item_id for unit in ordered_units for item_id in unit.get("contract_item_ids", [])
        ]
        require(
            set(mapped_items) == set(selected) and len(raw_mapped_items) == len(selected),
            "pathway.unit_coverage",
            "ordered learning units must map every selected item exactly once",
        )

        bridge_ids = [
            unit.get("bridge_contract_id") for unit in ordered_units
            if unit.get("unit_type") == "prerequisite_bridge"
        ]
        require(all(isinstance(value, str) and value for value in bridge_ids), "bridge.unit_id", "bridge units need released contract IDs")
        bridge_catalog_path: Path | None = None
        bridge_catalog: dict[str, Any] | None = None
        released_bridges: list[dict[str, Any]] = []
        if condition in {"P0", "P1"}:
            require(not bridge_ids, f"{condition}.bridges", f"{condition} must not contain bridge units")
            require(args.bridge_catalog is None, f"{condition}.bridge_catalog", f"{condition} must not receive a bridge catalog")
        elif bridge_ids:
            require(args.bridge_catalog is not None, "P2.bridge_catalog", "P2 bridge units require a released bridge catalog")
            bridge_catalog_path = resolve(root, args.bridge_catalog)
            bridge_catalog = load_json(bridge_catalog_path)
            require(bridge_catalog.get("status") == "released", "bridge_catalog.status", "bridge catalog is not released")
            report_catalog = report.get("bridge_catalog")
            require(isinstance(report_catalog, dict), "pathway_report.bridge_catalog", "pathway report lacks bridge catalog binding")
            require(resolve(root, report_catalog.get("file", "")) == bridge_catalog_path, "pathway_report.bridge_path", "pathway report binds another bridge catalog")
            require(report_catalog.get("sha256") == digest(bridge_catalog_path), "pathway_report.bridge_hash", "pathway bridge catalog hash is stale")
            for bridge_id in bridge_ids:
                bridge = find_bridge(bridge_catalog, bridge_id)
                require(bridge is not None and bridge.get("status") == "released", "bridge.release", f"bridge is not released: {bridge_id}")
                released_bridges.append(bridge)
            require(len({item["bridge_contract_id"] for item in released_bridges}) == len(bridge_ids), "bridge.duplicate", "bridge units must map distinct released contracts")
        else:
            require(args.bridge_catalog is None, "P2.unused_bridge_catalog", "do not supply a catalog when the P2 pathway has no bridge units")

        composition_policy = {
            "external_retrieval_allowed": False,
            "other_profiles_allowed": False,
            "other_condition_outputs_allowed": False,
            "evaluation_results_allowed": False,
            "profile_visible": condition in {"P1", "P2"},
            "profile_adaptation_allowed": condition in {"P1", "P2"},
            "pathway_replanning_allowed": False,
            "selected_contract_scope_exact": True,
            "instruction_sequence_exact": True,
            "discipline_neutral_required": condition == "P0",
        }
        view = {
            "schema_version": "1.0",
            "run_id": args.run_id,
            "condition": condition,
            "topic": topic,
            "composition_policy": composition_policy,
            "word_count_protocol": protocol,
            "learning_request": request,
            "learner_profile": profile,
            "pathway": {
                "pathway_id": pathway.get("pathway_id"),
                "selected_item_ids": selected,
                "excluded_item_ids": excluded,
                "selection_decisions": pathway.get("selection", {}).get("decisions", []),
                "learning_goal_mappings": pathway.get("learning_goal_mappings", []),
                "instruction_sequence": sequence,
                "ordered_learning_units": ordered_units,
                "rendering_policy": pathway.get("rendering_policy"),
            },
            "selected_contract_items": selected_items,
            "released_bridge_contracts": released_bridges,
        }

        inputs: dict[str, Any] = {
            "pathway": binding(root, pathway_path),
            "pathway_validation_report": binding(root, report_path),
            "reference_contract": binding(root, contract_path),
            "learning_request": binding(root, request_path),
            "word_count_protocol": binding(root, protocol_path),
            "profile": binding(root, profile_path) if profile_path else None,
            "bridge_catalog": binding(root, bridge_catalog_path) if bridge_catalog_path else None,
        }
        output_dir.mkdir(parents=True)
        view_path = output_dir / "composition-input-view.json"
        write_json(view_path, view)
        receipt = {
            "schema_version": "1.0",
            "preparer": "prepare-composition-inputs-v1",
            "prepared_at": args.prepared_at,
            "run_id": args.run_id,
            "condition": condition,
            "topic": topic,
            "inputs": inputs,
            "treatment_isolation": composition_policy,
            "output_view": binding(root, view_path),
        }
        write_json(output_dir / "composition-input-receipt.json", receipt)
        print(f"PASS: prepared {condition} composition inputs in {display(root, output_dir)}")
        return 0
    except ComposerError as exc:
        print(f"FAIL [{exc.code}]: {exc}")
        return 1
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"FAIL [unexpected]: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
