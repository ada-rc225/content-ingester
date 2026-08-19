#!/usr/bin/env python3
"""Verify P2 planning authorities and create a compact, hash-bound planning view."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from pathway_authorities import (
    AuthorityError,
    display_path,
    sha256,
    verify_curriculum_model_release,
    verify_learning_request,
    verify_p0_baseline,
    verify_profile,
    verify_reference_contract_release,
)


def write_new(path: Path, value: dict) -> None:
    if path.exists():
        raise AuthorityError("output.exists", f"refusing to overwrite existing output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--reference-contract", type=Path, required=True)
    parser.add_argument("--curriculum-model", type=Path, required=True)
    parser.add_argument("--learning-request", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--baseline-pathway", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--view-output", type=Path, required=True)
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    paths = {
        "reference_contract": args.reference_contract.resolve(),
        "curriculum_model": args.curriculum_model.resolve(),
        "learning_request": args.learning_request.resolve(),
        "profile": args.profile.resolve(),
        "baseline_pathway": args.baseline_pathway.resolve(),
    }
    output_path = args.output.resolve()
    view_path = args.view_output.resolve()
    if output_path == view_path:
        print("ERROR [output.collision]: receipt and view outputs must differ")
        return 1
    try:
        contract = verify_reference_contract_release(root, paths["reference_contract"])
        model, release = verify_curriculum_model_release(root, paths["curriculum_model"], paths["reference_contract"])
        request = verify_learning_request(root, paths["learning_request"], paths["reference_contract"], contract)
        profile = verify_profile(root, paths["profile"], request)
        baseline = verify_p0_baseline(root, paths["baseline_pathway"], paths["reference_contract"], paths["learning_request"])
        generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
        receipt = {
            "schema_version": "1.0",
            "preflight": "adaptive-curriculum-pathway-planning-v1",
            "valid": True,
            "inputs": {
                name: {"file": display_path(path, root), "sha256": sha256(path)}
                for name, path in paths.items()
            },
            "identities": {
                "contract_id": contract["contract_id"],
                "contract_version": contract["contract_version"],
                "curriculum_model_id": model["model_id"],
                "learning_request_id": request["request_id"],
                "profile_id": profile["profile_id"],
                "baseline_pathway_id": baseline["pathway_id"],
            },
            "review_state": {
                "learning_request": request["review"]["review_status"],
                "learner_profile": profile["review_status"],
                "curriculum_model": model["review_status"],
            },
            "bridge_release_status": release.get("bridge_release_status"),
            "generated_at": generated_at,
        }
        model_items = {item["item_id"]: item for item in model["items"]}
        compact_items = []
        for item in contract["contract_items"]:
            item_id = item["item_id"]
            dependency = model_items[item_id]
            compact_items.append({
                "item_id": item_id,
                "item_type": item["item_type"],
                "criticality": item["criticality"],
                "canonical_statement": item["canonical_statement"],
                "canonical_latex": item["canonical_latex"],
                "formula_refs": item["formula_refs"],
                "conditions": item["conditions"],
                "prohibited_drift": item["prohibited_drift"],
                "hard_dependencies": dependency["hard_dependencies"],
                "explanatory_dependencies": dependency["explanatory_dependencies"],
                "implementation_dependencies": dependency["implementation_dependencies"],
                "co_requisite_item_ids": dependency["co_requisite_item_ids"],
                "recommended_neighbours": dependency["recommended_neighbours"],
                "external_prerequisite_concept_ids": dependency["external_prerequisite_concept_ids"],
                "fallback_when_explanatory_dependencies_omitted": dependency["fallback_when_explanatory_dependencies_omitted"],
            })
        view = {
            "schema_version": "1.0",
            "view_type": "adaptive-curriculum-pathway-planning-view",
            "bindings": receipt["inputs"],
            "topic": request["topic"],
            "contract_topic": contract["topic"],
            "learning_request": {
                "request_id": request["request_id"],
                "request_version": request["request_version"],
                "learning_goal": request["learning_goal"],
                "target_capabilities": request["target_capabilities"],
                "delivery_constraints": request["delivery_constraints"],
                "selection_policy": request["selection_policy"],
            },
            "learner_profile": profile,
            "baseline": {
                "pathway_id": baseline["pathway_id"],
                "selected_item_ids": baseline["selection"]["selected_item_ids"],
                "instruction_sequence": baseline["instruction_sequence"],
                "learning_units": baseline["learning_units"],
            },
            "contract_items": compact_items,
            "external_prerequisite_concepts": model["external_prerequisite_concepts"],
        }
        write_new(output_path, receipt)
        try:
            write_new(view_path, view)
        except Exception:
            output_path.unlink(missing_ok=True)
            raise
    except (AuthorityError, OSError, KeyError, TypeError) as exc:
        code = exc.code if isinstance(exc, AuthorityError) else "preflight.input"
        print(f"ERROR [{code}]: {exc}")
        return 1
    print(f"PASS: P2 planning inputs verified; receipt={output_path}; view={view_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
