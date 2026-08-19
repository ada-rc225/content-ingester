#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from rq2_eval_common import (
    ALGORITHM_ITEM_TYPES,
    PRIMARY_DIMENSIONS,
    PROTOCOL_ID,
    EvaluationError,
    load_json,
    selected_contract_items,
    write_json,
)
from validate_blind_sample import validate as validate_bundle


def parse_time(value: str) -> str:
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def pending_rating(dimension: str) -> dict:
    return {
        "dimension": dimension,
        "score": None,
        "evidence_excerpts": [],
        "rationale": "PENDING",
        "confidence": "low",
        "abstain": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a complete pending RQ2 judgement template.")
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--evaluator-id", required=True)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--access-route", required=True)
    parser.add_argument("--pass-index", required=True, type=int)
    parser.add_argument("--evaluated-at", required=True, type=parse_time)
    args = parser.parse_args()

    bundle = Path(args.bundle).resolve()
    output = Path(args.output).resolve()
    try:
        errors = validate_bundle(bundle)
        if errors:
            raise EvaluationError("invalid blind bundle: " + "; ".join(errors))
        if output.exists():
            raise EvaluationError(f"refusing to overwrite existing judgement: {output}")
        if args.pass_index < 1:
            raise EvaluationError("pass-index must be positive")
        manifest = load_json(bundle / "evaluation-manifest.json")
        pathway = load_json(bundle / "pathway-evidence.json")
        request = load_json(bundle / "learning-request.json")
        selected, items = selected_contract_items(bundle)

        formula_to_items: dict[str, list[str]] = {}
        for item_id in selected:
            for formula_ref in items[item_id].get("formula_refs", []):
                formula_to_items.setdefault(formula_ref, []).append(item_id)
        algorithm_ids = [
            item_id for item_id in selected
            if items[item_id].get("item_type") in ALGORITHM_ITEM_TYPES
        ]

        excluded = pathway.get("excluded_item_ids", [])
        selection_rating = {
            "score": None,
            "not_applicable": False,
            "evidence_excerpts": [],
            "rationale": "PENDING",
            "confidence": "low",
            "abstain": True,
        }
        exclusion_rating = dict(selection_rating)
        if not excluded:
            exclusion_rating = {
                "score": None,
                "not_applicable": True,
                "evidence_excerpts": [],
                "rationale": "No Contract items were excluded; exclusion appropriateness is not applicable.",
                "confidence": "high",
                "abstain": False,
            }

        judgement = {
            "schema_version": "1.0",
            "protocol_id": PROTOCOL_ID,
            "sample_id": manifest.get("sample_id"),
            "evaluator": {
                "evaluator_id": args.evaluator_id,
                "provider": args.provider,
                "model": args.model,
                "access_route": args.access_route,
                "prompt_version": PROTOCOL_ID,
                "pass_index": args.pass_index,
                "evaluated_at": args.evaluated_at,
            },
            "primary_pedagogy_judgements": [pending_rating(item) for item in PRIMARY_DIMENSIONS],
            "exploratory_judgements": [pending_rating("example_authenticity")],
            "learning_goal_judgements": [
                {
                    "capability_id": capability.get("capability_id"),
                    "priority": capability.get("priority"),
                    "coverage": "uncertain",
                    "evidence_excerpts": [],
                    "rationale": "PENDING",
                    "confidence": "low",
                    "abstain": True,
                }
                for capability in request.get("target_capabilities", [])
            ],
            "selection_quality": {
                "inclusion_appropriateness": selection_rating,
                "exclusion_appropriateness": exclusion_rating,
                "unnecessary_content_load": {
                    "level": "uncertain",
                    "evidence_excerpts": [],
                    "rationale": "PENDING",
                    "confidence": "low",
                    "abstain": True,
                },
                "profile_rationale_quality": dict(selection_rating),
            },
            "selected_item_judgements": [
                {
                    "item_id": item_id,
                    "coverage": "uncertain",
                    "semantic_correctness": "uncertain",
                    "provenance": "uncertain",
                    "evidence_excerpts": [],
                    "contract_requirements": [
                        items[item_id].get("canonical_statement", ""),
                        *items[item_id].get("conditions", []),
                    ],
                    "rationale": "PENDING",
                    "confidence": "low",
                    "abstain": True,
                }
                for item_id in selected
            ],
            "formula_judgements": [
                {
                    "formula_ref": formula_ref,
                    "item_ids": item_ids,
                    "occurrence_status": "uncertain",
                    "provenance": "uncertain",
                    "accuracy": "uncertain",
                    "severity": "uncertain",
                    "evidence_excerpts": [],
                    "rationale": "PENDING",
                    "confidence": "low",
                    "abstain": True,
                }
                for formula_ref, item_ids in sorted(formula_to_items.items())
            ],
            "algorithm_judgements": [
                {
                    "item_id": item_id,
                    "accuracy": "uncertain",
                    "severity": "uncertain",
                    "evidence_excerpts": [],
                    "rationale": "PENDING",
                    "confidence": "low",
                    "abstain": True,
                }
                for item_id in algorithm_ids
            ],
            "unsupported_claims": [],
            "dependency_coherence": {
                "verdict": "uncertain",
                "evidence_excerpts": [],
                "rationale": "PENDING",
                "confidence": "low",
                "abstain": True,
            },
            "overall_recommendation": {
                "decision": "requires_adjudication",
                "rationale": "PENDING",
            },
        }
        write_json(output, judgement)
        print(f"PASS: pending judgement template created at {output}")
        return 0
    except (EvaluationError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
