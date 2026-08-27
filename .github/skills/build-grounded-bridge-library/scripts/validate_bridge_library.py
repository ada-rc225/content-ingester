#!/usr/bin/env python3
"""Validate a compact RQ2 bridge-library candidate against approved P2 demand."""

from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path.resolve())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument(
        "--pathway-review", nargs=2, action="append",
        metavar=("PATHWAY", "REVIEW"), required=True,
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    model_path = args.model.resolve()
    candidate_path = args.candidate.resolve()
    output_path = args.output.resolve()
    if output_path.exists():
        print(f"ERROR [output.exists]: refusing to overwrite {output_path}")
        return 1

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def check(condition: bool, code: str, message: str) -> None:
        if not condition:
            errors.append({"code": code, "message": message})

    try:
        model = load_object(model_path)
        candidate = load_object(candidate_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR [input.read]: {exc}")
        return 1

    release_report_path = model_path.parent / "curriculum-release-report.json"
    check(
        model_path.name == "frozen-contract-dependencies.json",
        "model.filename", "model must be a frozen curriculum model",
    )
    check(
        release_report_path.is_file(),
        "model.release_report", "curriculum release report is missing",
    )
    if release_report_path.is_file():
        report = load_object(release_report_path)
        check(
            report.get("status") == "released",
            "model.release_status", "curriculum model is not released",
        )
        check(
            report.get("outputs", {}).get("frozen_model_sha256")
            == digest(model_path),
            "model.release_hash", "released model hash is stale",
        )

    model_concepts = {
        item.get("concept_id"): item
        for item in model.get("external_prerequisite_concepts", [])
        if isinstance(item, dict) and isinstance(item.get("concept_id"), str)
    }
    demand_profiles: dict[str, set[str]] = defaultdict(set)
    demand_items: dict[str, set[str]] = defaultdict(set)
    expected_bindings: dict[str, dict[str, str]] = {}

    for raw_pathway, raw_review in args.pathway_review:
        pathway_path = Path(raw_pathway).resolve()
        review_path = Path(raw_review).resolve()
        try:
            pathway = load_object(pathway_path)
            review = load_object(review_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append({"code": "pathway.read", "message": str(exc)})
            continue
        pathway_id = pathway.get("pathway_id")
        profile_id = pathway.get("profile_binding", {}).get("profile_id")
        check(
            pathway.get("condition") == "P2",
            "pathway.condition", f"{pathway_id} is not P2",
        )
        check(
            review.get("review_status") == "approved",
            "review.status", f"{pathway_id} review is not approved",
        )
        check(
            review.get("overall_review", {}).get("decision") == "approved",
            "review.overall", f"{pathway_id} overall review is not approved",
        )
        binding = review.get("candidate_binding", {})
        check(
            binding.get("pathway_id") == pathway_id,
            "review.pathway_id",
            f"review identifies another pathway: {pathway_id}",
        )
        check(
            binding.get("pathway_sha256") == digest(pathway_path),
            "review.pathway_hash", f"review hash is stale: {pathway_id}",
        )
        expected_bindings[pathway_id] = {
            "pathway_id": pathway_id,
            "pathway_file": display(pathway_path, root),
            "pathway_sha256": digest(pathway_path),
            "review_file": display(review_path, root),
            "review_sha256": digest(review_path),
            "profile_id": profile_id,
        }
        for requirement in pathway.get("bridge_requirements", []):
            if requirement.get("resolution_status") != "candidate":
                continue
            concept_id = requirement.get("concept_id")
            check(
                concept_id in model_concepts,
                "demand.concept", f"unknown demanded concept: {concept_id}",
            )
            if isinstance(concept_id, str) and isinstance(profile_id, str):
                demand_profiles[concept_id].add(profile_id)
                demand_items[concept_id].update(
                    requirement.get("required_by_item_ids", [])
                )
                if concept_id in model_concepts:
                    check(
                        requirement.get("bridge_candidate_id")
                        == model_concepts[concept_id].get("bridge_candidate_id"),
                        "demand.candidate_id",
                        f"candidate ID differs from model: {concept_id}",
                    )

    check(
        candidate.get("schema_version") == "1.0",
        "candidate.schema_version", "schema_version must be 1.0",
    )
    check(
        candidate.get("status") == "candidate",
        "candidate.status", "library status must be candidate",
    )
    generator = candidate.get("generated_by", {})
    check(
        generator.get("agent") == "grounded-bridge-library-builder",
        "candidate.generator", "unexpected generator agent",
    )
    model_binding = candidate.get("curriculum_model_binding", {})
    check(
        model_binding.get("model_id") == model.get("model_id"),
        "candidate.model_id", "model ID binding differs",
    )
    check(
        model_binding.get("file") == display(model_path, root),
        "candidate.model_path", "model path binding differs",
    )
    check(
        model_binding.get("sha256") == digest(model_path),
        "candidate.model_hash", "model hash binding is stale",
    )

    actual_bindings = {
        item.get("pathway_id"): item
        for item in candidate.get("pathway_bindings", [])
        if isinstance(item, dict)
    }
    check(
        actual_bindings == expected_bindings,
        "candidate.pathway_bindings",
        "candidate pathway bindings do not exactly match supplied approved pathways",
    )

    bridges = candidate.get("bridges")
    check(
        isinstance(bridges, list) and bool(bridges),
        "candidate.bridges", "bridges must be a non-empty array",
    )
    bridge_map: dict[str, dict[str, Any]] = {}
    for index, bridge in enumerate(bridges if isinstance(bridges, list) else []):
        location = f"bridges[{index}]"
        if not isinstance(bridge, dict):
            errors.append({
                "code": "bridge.type",
                "message": f"{location} is not an object",
            })
            continue
        concept_id = bridge.get("concept_id")
        check(
            isinstance(concept_id, str) and concept_id not in bridge_map,
            "bridge.concept_id",
            f"duplicate or invalid concept at {location}",
        )
        if not isinstance(concept_id, str):
            continue
        bridge_map[concept_id] = bridge
        model_entry = model_concepts.get(concept_id)
        check(
            model_entry is not None,
            "bridge.model_concept", f"{concept_id} is absent from the model",
        )
        if model_entry is None:
            continue
        check(
            bridge.get("status") == "candidate",
            "bridge.status", f"{concept_id} must remain candidate",
        )
        check(
            bridge.get("bridge_candidate_id")
            == model_entry.get("bridge_candidate_id"),
            "bridge.candidate_id", f"wrong candidate ID: {concept_id}",
        )
        expected_contract_id = model_entry["bridge_candidate_id"].replace(
            "BR-", "BRC-", 1
        )
        check(
            bridge.get("bridge_contract_id") == expected_contract_id,
            "bridge.contract_id", f"wrong bridge contract ID: {concept_id}",
        )
        check(
            bridge.get("name") == model_entry.get("name"),
            "bridge.name", f"name differs from model: {concept_id}",
        )
        check(
            bridge.get("content_boundary") == model_entry.get("content_boundary"),
            "bridge.boundary", f"boundary differs from model: {concept_id}",
        )
        check(
            set(bridge.get("supports_item_ids", [])) == demand_items[concept_id],
            "bridge.supports",
            f"RC support differs from approved demand: {concept_id}",
        )
        check(
            set(bridge.get("requested_by_profile_ids", []))
            == demand_profiles[concept_id],
            "bridge.profiles", f"profile demand differs: {concept_id}",
        )
        check(
            bool(bridge.get("learning_outcomes")),
            "bridge.outcomes", f"learning outcomes are empty: {concept_id}",
        )
        check(
            bool(bridge.get("excluded_content")),
            "bridge.exclusions", f"excluded content is empty: {concept_id}",
        )
        contents = bridge.get("teaching_content", [])
        sources = bridge.get("sources", [])
        content_ids = {
            item.get("content_id")
            for item in contents
            if isinstance(item, dict)
        }
        source_map = {
            item.get("source_id"): item
            for item in sources
            if isinstance(item, dict)
        }
        check(
            len(content_ids) == len(contents) and None not in content_ids,
            "bridge.content_ids",
            f"content IDs are invalid or duplicated: {concept_id}",
        )
        check(
            len(source_map) == len(sources) and None not in source_map,
            "bridge.source_ids",
            f"source IDs are invalid or duplicated: {concept_id}",
        )
        for content in contents:
            if not isinstance(content, dict):
                continue
            refs = content.get("source_ids", [])
            check(
                bool(refs),
                "content.sources", f"unbound content block in {concept_id}",
            )
            check(
                set(refs).issubset(source_map),
                "content.source_ids",
                f"unknown source binding in {concept_id}/{content.get('content_id')}",
            )
        for source in sources:
            if not isinstance(source, dict):
                continue
            supports = set(source.get("supports_content_ids", []))
            check(
                bool(supports) and supports.issubset(content_ids),
                "source.content_ids",
                f"invalid source coverage in {concept_id}/{source.get('source_id')}",
            )
            check(
                str(source.get("url", "")).startswith("https://"),
                "source.url", f"source URL must use HTTPS in {concept_id}",
            )
        reverse_coverage = {
            content_id
            for source in sources
            if isinstance(source, dict)
            for content_id in source.get("supports_content_ids", [])
        }
        check(
            content_ids == reverse_coverage,
            "source.coverage",
            f"source declarations do not cover every content block: {concept_id}",
        )

    check(
        set(bridge_map) == set(demand_profiles),
        "candidate.demand_coverage",
        "candidate bridge set must exactly match approved unresolved demand",
    )

    result = {
        "schema_version": "1.0",
        "validator": "validate-bridge-library-v1",
        "validated_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
        "valid": not errors,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "inputs": {
            "model": display(model_path, root),
            "model_sha256": digest(model_path),
            "candidate": display(candidate_path, root),
            "candidate_sha256": digest(candidate_path),
            "pathway_review_pairs": [
                {
                    "pathway": display(Path(pair[0]).resolve(), root),
                    "review": display(Path(pair[1]).resolve(), root),
                }
                for pair in args.pathway_review
            ],
        },
        "metrics": {
            "approved_pathway_count": len(expected_bindings),
            "required_bridge_count": len(demand_profiles),
            "candidate_bridge_count": len(bridge_map),
            "source_count": sum(
                len(bridge.get("sources", []))
                for bridge in bridge_map.values()
            ),
            "content_block_count": sum(
                len(bridge.get("teaching_content", []))
                for bridge in bridge_map.values()
            ),
        },
        "errors": errors,
        "warnings": warnings,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"{'VALID' if result['valid'] else 'INVALID'}: {output_path}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
