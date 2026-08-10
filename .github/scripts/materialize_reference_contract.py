#!/usr/bin/env python3
"""Materialize source evidence and canonical LaTeX from a compact contract plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def workspace_relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def materialize(
    plan: dict[str, Any],
    inventory: dict[str, Any],
    manifest: dict[str, Any],
    inventory_path: Path,
    workspace_root: Path,
) -> dict[str, Any]:
    units = {unit["source_unit_id"]: unit for unit in inventory["source_units"]}
    formulas = {formula["formula_id"]: formula for formula in inventory["formulas"]}
    source_id = inventory["source"]["source_id"]

    source_materials = []
    for source in manifest["sources"]:
        source_materials.append(
            {
                key: source[key]
                for key in ("source_id", "path", "format", "sha256", "role")
            }
        )

    mapped_units: set[str] = set()
    mapped_formulas: set[str] = set()

    def evidence_for(unit_ids: list[str]) -> list[dict[str, Any]]:
        evidence = []
        for unit_id in unit_ids:
            unit = units.get(unit_id)
            if unit is None:
                raise ValueError(f"unknown source unit in plan: {unit_id}")
            locator = unit["locator"]
            evidence.append(
                {
                    "source_id": source_id,
                    "source_unit_id": unit_id,
                    "locator": {
                        "locator_type": "markdown_heading_lines",
                        "value": f"lines {locator['line_start']}-{locator['line_end']}",
                    },
                    "exact_excerpt": unit["exact_text"],
                }
            )
        return evidence

    contract_items = []
    for planned_item in plan["items"]:
        formula_ids = planned_item.get("formula_refs", [])
        source_unit_ids = list(planned_item.get("source_unit_refs", []))
        for formula_id in formula_ids:
            formula = formulas.get(formula_id)
            if formula is None:
                raise ValueError(f"unknown formula in plan: {formula_id}")
            if formula["scope_role"] == "exercise":
                raise ValueError(f"exercise formula is outside default scope: {formula_id}")
            if formula["source_unit_id"] not in source_unit_ids:
                source_unit_ids.append(formula["source_unit_id"])
        if len(source_unit_ids) != len(set(source_unit_ids)):
            raise ValueError(f"duplicate source unit in {planned_item['item_id']}")
        mapped_units.update(source_unit_ids)
        mapped_formulas.update(formula_ids)
        generation_requirement = planned_item["generation_requirement"]
        contract_items.append(
            {
                "item_id": planned_item["item_id"],
                "item_type": planned_item["item_type"],
                "criticality": planned_item["criticality"],
                "required_for_generation": generation_requirement == "required",
                "generation_requirement": generation_requirement,
                "evidence": evidence_for(source_unit_ids),
                "canonical_statement": planned_item["canonical_statement"],
                "canonical_latex": [formulas[formula_id]["exact_latex"] for formula_id in formula_ids],
                "formula_refs": formula_ids,
                "conditions": planned_item.get("conditions", []),
                "prohibited_drift": planned_item.get("prohibited_drift", []),
                "semantic_checks": planned_item["semantic_checks"],
                "review": {
                    "source_fidelity": "unreviewed",
                    "mathematical_status": "unreviewed",
                    "algorithmic_status": "unreviewed",
                    "decision": "pending",
                    "reviewer_notes": [],
                },
            }
        )

    candidate_source_issues = []
    for planned_issue in plan.get("candidate_source_issues", []):
        issue = {key: value for key, value in planned_issue.items() if key != "source_unit_refs"}
        issue["evidence"] = evidence_for(planned_issue["source_unit_refs"])
        issue["resolution"] = "pending_review"
        issue["approved_generation_content"] = None
        candidate_source_issues.append(issue)

    reference_only_formulas = sorted(
        formula_id
        for formula_id, formula in formulas.items()
        if formula["scope_role"] == "derivation" and formula_id not in mapped_formulas
    )
    expected_reference_only_units = {
        unit_id
        for unit_id, unit in units.items()
        if unit["scope_role"] in {"core_material", "derivation"}
        and unit["unit_type"] != "heading"
        and unit_id not in mapped_units
    }
    planned_reference_only_units = set(plan.get("reference_only_source_unit_refs", []))
    if planned_reference_only_units != expected_reference_only_units:
        missing = sorted(expected_reference_only_units - planned_reference_only_units)
        unexpected = sorted(planned_reference_only_units - expected_reference_only_units)
        raise ValueError(
            "reference_only_source_unit_refs must explicitly classify every unused included "
            f"source unit; missing={missing}, unexpected={unexpected}"
        )
    reference_only_units = sorted(planned_reference_only_units)

    return {
        "schema_version": "2.0",
        "contract_id": plan["contract_id"],
        "contract_version": plan["contract_version"],
        "topic": plan["topic"],
        "lifecycle_status": "candidate",
        "authority_policy": {
            "source_of_truth": "curated_institutional_material",
            "silent_correction_forbidden": True,
            "conflict_handling": "flag_for_human_review",
        },
        "source_materials": source_materials,
        "grounding_inventory": {
            "path": workspace_relative(inventory_path, workspace_root),
            "sha256": sha256(inventory_path),
        },
        "coverage_scope": {
            "included_source_roles": ["core_material", "derivation"],
            "excluded_source_roles": ["exercise"],
            "exercise_policy": "excluded_by_default",
            "reference_only_source_unit_ids": reference_only_units,
            "reference_only_formula_ids": reference_only_formulas,
            "core_formula_mapping_target": 1.0,
        },
        "contract_items": contract_items,
        "candidate_source_issues": candidate_source_issues,
        "approval": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--inventory", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    plan_path = Path(args.plan).resolve()
    inventory_path = Path(args.inventory).resolve()
    manifest_path = Path(args.source_manifest).resolve()
    output_path = Path(args.output).resolve()
    try:
        contract = materialize(
            load_json(plan_path),
            load_json(inventory_path),
            load_json(manifest_path),
            inventory_path,
            workspace_root,
        )
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}: {len(contract['contract_items'])} candidate contract items")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
