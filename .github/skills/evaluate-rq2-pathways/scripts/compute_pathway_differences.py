#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
from pathlib import Path
from typing import Any

from rq2_eval_common import EvaluationError, load_json, write_json


def labelled(values: list[str], label: str) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise EvaluationError(f"{label} must use NAME=PATH: {value}")
        name, raw_path = value.split("=", 1)
        if not name or name in result:
            raise EvaluationError(f"invalid or duplicate {label} name: {name}")
        path = Path(raw_path).resolve()
        if not path.is_file():
            raise EvaluationError(f"missing {label} file: {path}")
        result[name] = path
    return result


def jaccard_distance(left: set[Any], right: set[Any]) -> float:
    union = left | right
    return round(1 - len(left & right) / len(union), 6) if union else 0.0


def levenshtein(left: list[str], right: list[str]) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_value in enumerate(left, 1):
        current = [left_index]
        for right_index, right_value in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + (left_value != right_value),
            ))
        previous = current
    return previous[-1]


def pathway_features(pathway: dict[str, Any]) -> dict[str, Any]:
    selection = pathway.get("selection", {})
    selected = set(selection.get("selected_item_ids", []))
    units = {
        unit.get("unit_id"): unit
        for unit in pathway.get("learning_units", []) if isinstance(unit, dict)
    }
    item_sequence: list[str] = []
    grouping_pairs: set[tuple[str, str]] = set()
    bridges: set[str] = set()
    for unit_id in pathway.get("instruction_sequence", []):
        unit = units.get(unit_id, {})
        item_ids = [item for item in unit.get("contract_item_ids", []) if item in selected]
        for item_id in item_ids:
            if item_id not in item_sequence:
                item_sequence.append(item_id)
        for left, right in itertools.combinations(sorted(set(item_ids)), 2):
            grouping_pairs.add((left, right))
        bridge_id = unit.get("bridge_contract_id")
        if isinstance(bridge_id, str) and bridge_id:
            bridges.add(bridge_id)
    depth_signature = {
        affected_id
        for change in pathway.get("pathway_changes", []) if isinstance(change, dict)
        and change.get("change_type") == "change_theory_implementation_application_depth"
        for affected_id in change.get("affected_ids", []) if isinstance(affected_id, str)
    }
    rationale_present = all(
        isinstance(change, dict)
        and isinstance(change.get("profile_basis"), list) and bool(change.get("profile_basis"))
        and isinstance(change.get("rationale"), str) and bool(change.get("rationale").strip())
        for change in pathway.get("pathway_changes", [])
    )
    return {
        "selected": selected,
        "item_sequence": item_sequence,
        "grouping_pairs": grouping_pairs,
        "bridges": bridges,
        "depth_signature": depth_signature,
        "profile_rationale_present": rationale_present,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute deterministic pairwise RQ2 pathway differences.")
    parser.add_argument("--pathway", action="append", required=True, help="PROFILE=pathway-plan.json")
    parser.add_argument("--validation", action="append", default=[], help="PROFILE=pathway-validation-report.json")
    parser.add_argument("--review", action="append", default=[], help="PROFILE=pathway-plan-review.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    try:
        if output.exists():
            raise EvaluationError(f"refusing to overwrite pathway difference report: {output}")
        pathways = labelled(args.pathway, "pathway")
        validations = labelled(args.validation, "validation") if args.validation else {}
        reviews = labelled(args.review, "review") if args.review else {}
        if validations and set(validations) != set(pathways):
            raise EvaluationError("validation labels must exactly match pathway labels")
        if reviews and set(reviews) != set(pathways):
            raise EvaluationError("review labels must exactly match pathway labels")

        features = {name: pathway_features(load_json(path)) for name, path in pathways.items()}
        validation_status = {
            name: load_json(validations[name]).get("valid") is True if name in validations else None
            for name in pathways
        }
        review_status = {
            name: load_json(reviews[name]).get("overall_review", {}).get("decision") == "approved" if name in reviews else None
            for name in pathways
        }
        pairs = []
        for left_name, right_name in itertools.combinations(sorted(pathways), 2):
            left, right = features[left_name], features[right_name]
            raw_edit = levenshtein(left["item_sequence"], right["item_sequence"])
            max_length = max(len(left["item_sequence"]), len(right["item_sequence"]))
            selection_distance = jaccard_distance(left["selected"], right["selected"])
            order_distance = round(raw_edit / max_length, 6) if max_length else 0.0
            grouping_distance = jaccard_distance(left["grouping_pairs"], right["grouping_pairs"])
            bridge_distance = jaccard_distance(left["bridges"], right["bridges"])
            depth_changed = left["depth_signature"] != right["depth_signature"]
            change_flags = {
                "item_selection_changed": selection_distance > 0,
                "first_introduction_sequence_changed": order_distance > 0,
                "grouping_changed": grouping_distance > 0,
                "released_bridges_changed": bridge_distance > 0,
                "declared_depth_signature_changed": depth_changed,
            }
            both_valid = validation_status[left_name] is True and validation_status[right_name] is True
            both_reviewed = review_status[left_name] is True and review_status[right_name] is True
            rationale_present = left["profile_rationale_present"] and right["profile_rationale_present"]
            structural_change = any(change_flags.values())
            pairs.append({
                "left_profile": left_name,
                "right_profile": right_name,
                "selection_jaccard_distance": selection_distance,
                "normalized_item_sequence_edit_distance": order_distance,
                "raw_item_sequence_edit_distance": raw_edit,
                "grouping_pair_jaccard_distance": grouping_distance,
                "released_bridge_jaccard_distance": bridge_distance,
                "change_flags": change_flags,
                "both_pathways_valid": both_valid if validations else None,
                "both_pathway_reviews_approved": both_reviewed if reviews else None,
                "profile_rationales_present": rationale_present,
                "material_difference_candidate": structural_change and rationale_present,
                "material_difference_confirmed": structural_change and rationale_present and both_valid and both_reviewed if validations and reviews else None,
            })

        report = {
            "schema_version": "1.0",
            "metric_set": "RQ2-STRUCTURAL-DIFFERENCE-v1",
            "profile_count": len(pathways),
            "pair_count": len(pairs),
            "pairs": pairs,
            "interpretation": {
                "zero_distance": "No difference for that structural representation.",
                "material_difference": "Requires a detected structural change, profile-linked rationale, deterministic validity, and approved pathway reviews.",
                "lexical_changes": "Not measured and never sufficient.",
            },
        }
        write_json(output, report)
        print(f"PASS: computed {len(pairs)} RQ2 pathway comparisons")
        return 0
    except (EvaluationError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
