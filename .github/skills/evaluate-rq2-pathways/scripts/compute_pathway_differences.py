#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
from pathlib import Path
from typing import Any

from rq2_eval_common import EvaluationError, load_json, relative, resolve, sha256, verify_binding, write_json


MATERIALIZER = "released-bridge-pathway-materializer-v1"
MATERIALIZATION_RULE = "first-consuming-unit-v1"


def labelled(values: list[str], label: str, root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise EvaluationError(f"{label} must use NAME=PATH: {value}")
        name, raw_path = value.split("=", 1)
        if not name or name in result:
            raise EvaluationError(f"invalid or duplicate {label} name: {name}")
        path = resolve(root, raw_path)
        if not path.is_file():
            raise EvaluationError(f"missing {label} file: {path}")
        result[name] = path
    return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EvaluationError(message)


def verified_record(root: Path, value: Any, label: str) -> Path:
    require(isinstance(value, dict), f"{label} binding is missing")
    return verify_binding(root, value, label)


def validate_approved_review(
    root: Path,
    pathway_path: Path,
    pathway: dict[str, Any],
    review_path: Path,
    review: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    require(review.get("review_status") == "approved", f"{label} review_status is not approved")
    overall_review = review.get("overall_review")
    require(isinstance(overall_review, dict), f"{label} overall_review is missing")
    require(
        overall_review.get("decision") == "approved",
        f"{label} overall review decision is not approved",
    )
    binding = review.get("candidate_binding")
    require(isinstance(binding, dict), f"{label} candidate_binding is missing")
    require(
        binding.get("pathway_id") == pathway.get("pathway_id"),
        f"{label} review identifies another pathway ID",
    )
    require(
        resolve(root, binding.get("pathway_file")) == pathway_path,
        f"{label} review identifies another pathway file",
    )
    require(
        binding.get("pathway_sha256") == sha256(pathway_path),
        f"{label} pathway changed after review",
    )
    return {
        "authority_type": "direct_approved_review",
        "review_file": relative(root, review_path),
        "review_sha256": sha256(review_path),
    }


def validate_materialization_receipt(
    root: Path,
    pathway_path: Path,
    pathway: dict[str, Any],
    receipt_path: Path,
    receipt: dict[str, Any],
    label: str,
) -> dict[str, Any]:
    require(receipt.get("materializer") == MATERIALIZER, f"{label} receipt has an unsupported materializer")
    require(receipt.get("rule_id") == MATERIALIZATION_RULE, f"{label} receipt has an unsupported insertion rule")

    output_path = verified_record(root, receipt.get("output_pathway"), f"{label} output pathway")
    require(output_path == pathway_path, f"{label} receipt identifies another output pathway")
    require(pathway.get("condition") == "P2", f"{label} materialized pathway is not P2")
    require(pathway.get("plan_status") == "complete", f"{label} materialized pathway is not complete")

    parent_path = verified_record(root, receipt.get("parent_pathway"), f"{label} parent pathway")
    parent_review_path = verified_record(root, receipt.get("parent_review"), f"{label} parent review")
    catalog_path = verified_record(root, receipt.get("bridge_catalog"), f"{label} bridge catalog")
    release_report_path = verified_record(
        root,
        receipt.get("bridge_release_report"),
        f"{label} bridge release report",
    )
    parent = load_json(parent_path)
    parent_review = load_json(parent_review_path)
    catalog = load_json(catalog_path)
    release_report = load_json(release_report_path)

    validate_approved_review(
        root,
        parent_path,
        parent,
        parent_review_path,
        parent_review,
        f"{label} parent",
    )
    require(parent.get("condition") == "P2", f"{label} parent pathway is not P2")
    require(parent.get("plan_status") == "provisional", f"{label} parent pathway is not provisional")
    require(parent.get("pathway_id") != pathway.get("pathway_id"), f"{label} output pathway ID was not renewed")

    require(catalog.get("status") == "released", f"{label} bridge catalog is not released")
    bridges = catalog.get("bridges")
    require(isinstance(bridges, list) and bool(bridges), f"{label} released bridge catalog is empty")
    require(
        all(isinstance(item, dict) and item.get("status") == "released" for item in bridges),
        f"{label} bridge catalog contains an unreleased bridge",
    )
    require(release_report.get("status") == "released", f"{label} bridge release report is not released")
    require(
        release_report.get("library_id") == catalog.get("library_id"),
        f"{label} release report identifies another bridge library",
    )
    outputs = release_report.get("outputs")
    require(isinstance(outputs, dict), f"{label} bridge release outputs are missing")
    require(
        resolve(root, outputs.get("released_bridge_catalog")) == catalog_path,
        f"{label} release report identifies another bridge catalog",
    )
    require(
        outputs.get("released_bridge_catalog_sha256") == sha256(catalog_path),
        f"{label} release report bridge catalog hash is stale",
    )

    bindings = catalog.get("pathway_bindings")
    require(isinstance(bindings, list), f"{label} bridge catalog pathway bindings are missing")
    matches = [
        item for item in bindings
        if isinstance(item, dict) and item.get("pathway_id") == parent.get("pathway_id")
    ]
    require(len(matches) == 1, f"{label} bridge catalog must bind the parent pathway exactly once")
    binding = matches[0]
    require(
        resolve(root, binding.get("pathway_file")) == parent_path,
        f"{label} bridge catalog identifies another parent pathway",
    )
    require(
        binding.get("pathway_sha256") == sha256(parent_path),
        f"{label} bridge catalog parent pathway hash is stale",
    )
    require(
        resolve(root, binding.get("review_file")) == parent_review_path,
        f"{label} bridge catalog identifies another parent review",
    )
    require(
        binding.get("review_sha256") == sha256(parent_review_path),
        f"{label} bridge catalog parent review hash is stale",
    )

    resolved_bridges = receipt.get("resolved_bridges")
    require(
        isinstance(resolved_bridges, list) and bool(resolved_bridges),
        f"{label} receipt contains no resolved bridge",
    )
    require(
        all(
            isinstance(item, dict)
            and isinstance(item.get("bridge_contract_id"), str)
            and isinstance(item.get("bridge_unit_id"), str)
            and isinstance(item.get("first_consumer_unit_id"), str)
            for item in resolved_bridges
        ),
        f"{label} receipt has an invalid resolved bridge record",
    )
    return {
        "authority_type": "approved_parent_review_via_materialization_receipt",
        "receipt_file": relative(root, receipt_path),
        "receipt_sha256": sha256(receipt_path),
        "parent_pathway_file": relative(root, parent_path),
        "parent_pathway_sha256": sha256(parent_path),
        "parent_review_file": relative(root, parent_review_path),
        "parent_review_sha256": sha256(parent_review_path),
        "bridge_catalog_file": relative(root, catalog_path),
        "bridge_catalog_sha256": sha256(catalog_path),
        "bridge_release_report_file": relative(root, release_report_path),
        "bridge_release_report_sha256": sha256(release_report_path),
    }


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
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--pathway", action="append", required=True, help="PROFILE=pathway-plan.json")
    parser.add_argument("--validation", action="append", default=[], help="PROFILE=pathway-validation-report.json")
    parser.add_argument("--review", action="append", default=[], help="PROFILE=pathway-plan-review.json")
    parser.add_argument(
        "--materialization-receipt",
        action="append",
        default=[],
        help="PROFILE=bridge-resolution-receipt.json",
    )
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.workspace_root).resolve()
    output = Path(args.output).resolve()
    try:
        if output.exists():
            raise EvaluationError(f"refusing to overwrite pathway difference report: {output}")
        pathways = labelled(args.pathway, "pathway", root)
        validations = labelled(args.validation, "validation", root) if args.validation else {}
        reviews = labelled(args.review, "review", root) if args.review else {}
        receipts = (
            labelled(args.materialization_receipt, "materialization receipt", root)
            if args.materialization_receipt else {}
        )
        if validations and set(validations) != set(pathways):
            raise EvaluationError("validation labels must exactly match pathway labels")
        overlapping_authority = set(reviews) & set(receipts)
        if overlapping_authority:
            raise EvaluationError(
                "each profile must use either --review or --materialization-receipt, not both: "
                + ", ".join(sorted(overlapping_authority))
            )
        authority_labels = set(reviews) | set(receipts)
        if authority_labels and authority_labels != set(pathways):
            raise EvaluationError(
                "review and materialization-receipt labels together must exactly match pathway labels"
            )

        pathway_documents = {name: load_json(path) for name, path in pathways.items()}
        features = {name: pathway_features(pathway_documents[name]) for name in pathways}
        validation_status = {
            name: load_json(validations[name]).get("valid") is True if name in validations else None
            for name in pathways
        }
        review_authority: dict[str, dict[str, Any]] = {}
        for name, review_path in reviews.items():
            review_authority[name] = validate_approved_review(
                root,
                pathways[name],
                pathway_documents[name],
                review_path,
                load_json(review_path),
                name,
            )
        for name, receipt_path in receipts.items():
            review_authority[name] = validate_materialization_receipt(
                root,
                pathways[name],
                pathway_documents[name],
                receipt_path,
                load_json(receipt_path),
                name,
            )
        review_status = {
            name: True if name in review_authority else None
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
                "both_pathway_reviews_approved": both_reviewed if review_authority else None,
                "review_authority": {
                    "left": review_authority.get(left_name),
                    "right": review_authority.get(right_name),
                } if review_authority else None,
                "profile_rationales_present": rationale_present,
                "material_difference_candidate": structural_change and rationale_present,
                "material_difference_confirmed": (
                    structural_change and rationale_present and both_valid and both_reviewed
                    if validations and review_authority else None
                ),
            })

        report = {
            "schema_version": "1.1",
            "metric_set": "RQ2-STRUCTURAL-DIFFERENCE-v1",
            "profile_count": len(pathways),
            "pair_count": len(pairs),
            "pairs": pairs,
            "interpretation": {
                "zero_distance": "No difference for that structural representation.",
                "material_difference": "Requires a detected structural change, profile-linked rationale, deterministic validity, and review authority established by either a directly bound approved review or a verified bridge-materialization receipt inheriting an approved parent review.",
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
