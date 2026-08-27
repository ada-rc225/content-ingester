#!/usr/bin/env python3
"""Verify a released frozen contract and emit a compact run binding receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


FINAL_DECISIONS = {"approved_as_written", "approved_with_correction", "excluded"}
CHECKSUM_RE = re.compile(r"^([a-f0-9]{64})\s+\*?frozen_reference_contract\.json\s*$")


def load_json(path: Path) -> dict:
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--release-report")
    parser.add_argument("--output", required=True)
    parser.add_argument("--view-output")
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    contract_path = Path(args.contract).resolve()
    release_path = (
        Path(args.release_report).resolve()
        if args.release_report
        else contract_path.with_name("release_gate_report.json")
    )
    checksum_path = contract_path.with_name("frozen_contract.sha256")
    validation_path = contract_path.with_name("frozen_contract_validation_report.json")
    output_path = Path(args.output).resolve()
    view_path = Path(args.view_output).resolve() if args.view_output else output_path.with_name("grounding_view.json")

    try:
        for path, label in (
            (contract_path, "frozen contract"),
            (release_path, "release gate report"),
            (checksum_path, "frozen contract checksum"),
            (validation_path, "frozen contract validation report"),
        ):
            require(path.is_file(), f"missing {label}: {path}")

        contract = load_json(contract_path)
        release = load_json(release_path)
        validation = load_json(validation_path)
        contract_hash = sha256(contract_path)

        require(contract_path.name == "frozen_reference_contract.json", "contract must be named frozen_reference_contract.json")
        require(contract.get("lifecycle_status") == "frozen", "contract lifecycle_status is not frozen")
        require(isinstance(contract.get("approval"), dict), "frozen contract approval is missing")
        authority = contract.get("authority_policy", {})
        require(authority.get("source_of_truth") == "curated_institutional_material", "contract source_of_truth is not curated_institutional_material")
        require(authority.get("silent_correction_forbidden") is True, "contract permits silent correction")

        checksum_match = CHECKSUM_RE.fullmatch(checksum_path.read_text(encoding="utf-8"))
        require(checksum_match is not None, "frozen_contract.sha256 has an invalid format or filename")
        require(checksum_match.group(1) == contract_hash, "frozen contract SHA-256 does not match frozen_contract.sha256")

        require(release.get("status") == "released", "release gate status is not released")
        release_outputs = release.get("outputs", {})
        require(release.get("contract_id") == contract.get("contract_id"), "release contract_id differs from frozen contract")
        require(release.get("contract_version") == contract.get("contract_version"), "release contract_version differs from frozen contract")
        require(release_outputs.get("frozen_contract_sha256") == contract_hash, "release report frozen contract hash mismatch")
        recorded_contract = resolve_recorded_path(root, release_outputs.get("frozen_contract", ""))
        require(recorded_contract == contract_path, "release report identifies a different frozen contract path")

        require(validation.get("valid") is True and validation.get("error_count") == 0, "frozen contract validation report did not pass")
        recorded_validation = release_outputs.get("validation_report")
        require(isinstance(recorded_validation, str) and resolve_recorded_path(root, recorded_validation) == validation_path, "release report identifies a different validation report")

        release_inputs = release.get("inputs", {})
        manifest_raw = release_inputs.get("source_manifest")
        inventory_raw = release_inputs.get("grounding_inventory")
        require(isinstance(manifest_raw, str) and manifest_raw, "release report has no source_manifest input")
        require(isinstance(inventory_raw, str) and inventory_raw, "release report has no grounding_inventory input")
        manifest_path = resolve_recorded_path(root, manifest_raw)
        inventory_path = resolve_recorded_path(root, inventory_raw)
        require(manifest_path.is_file(), f"released source manifest is missing: {manifest_path}")
        require(inventory_path.is_file(), f"released grounding inventory is missing: {inventory_path}")

        scripts_dir = root / ".github" / "scripts"
        require((scripts_dir / "validate_reference_contract.py").is_file(), "reference contract validator is missing")
        sys.path.insert(0, str(scripts_dir))
        from validate_reference_contract import validate_contract  # type: ignore

        metrics: dict = {}
        findings = validate_contract(contract_path, root, manifest_path, inventory_path, metrics)
        require(not findings, "current frozen contract validation failed: " + "; ".join(f"{item.code}: {item.message}" for item in findings))

        required_ids: list[str] = []
        conditional_ids: list[str] = []
        excluded_ids: list[str] = []
        required_items: list[dict] = []
        conditional_items: list[dict] = []
        issues = contract.get("candidate_source_issues", [])
        for item in contract.get("contract_items", []):
            item_id = item.get("item_id")
            decision = item.get("review", {}).get("decision")
            require(decision in FINAL_DECISIONS, f"{item_id}: item has no final review decision")
            if decision == "excluded":
                excluded_ids.append(item_id)
                require(item.get("generation_requirement") != "required", f"{item_id}: a required item is excluded")
            else:
                statement = item.get("canonical_statement")
                latex = item.get("canonical_latex", [])
                content_basis = "approved_as_written"
                if decision == "approved_with_correction":
                    corrections = [
                        issue.get("approved_generation_content")
                        for issue in issues
                        if item_id in issue.get("affected_item_ids", [])
                        and issue.get("resolution") == "approved_correction"
                    ]
                    require(len(corrections) == 1 and isinstance(corrections[0], dict), f"{item_id}: approved_with_correction requires exactly one approved correction")
                    statement = corrections[0].get("statement")
                    latex = corrections[0].get("latex", [])
                    content_basis = "approved_correction"
                generation_item = {
                    "item_id": item_id,
                    "item_type": item.get("item_type"),
                    "criticality": item.get("criticality"),
                    "content_basis": content_basis,
                    "canonical_statement": statement,
                    "canonical_latex": latex,
                    "formula_refs": item.get("formula_refs", []),
                    "conditions": item.get("conditions", []),
                    "prohibited_drift": item.get("prohibited_drift", []),
                }
                if item.get("generation_requirement") == "required":
                    required_ids.append(item_id)
                    required_items.append(generation_item)
                else:
                    conditional_ids.append(item_id)
                    conditional_items.append(generation_item)
        require(bool(required_ids), "frozen contract has no approved required generation items")

        inventory_descriptor = contract.get("grounding_inventory", {})
        require(inventory_descriptor.get("sha256") == sha256(inventory_path), "grounding inventory hash mismatch")
        approval = contract["approval"]
        view = {
            "schema_version": "1.0",
            "contract": {
                "contract_id": contract["contract_id"],
                "contract_version": contract["contract_version"],
                "sha256": contract_hash,
                "topic": contract["topic"],
            },
            "required_items": required_items,
            "conditional_items": conditional_items,
            "excluded_item_ids": excluded_ids,
        }
        view_path.parent.mkdir(parents=True, exist_ok=True)
        view_path.write_text(json.dumps(view, indent=2) + "\n", encoding="utf-8")
        receipt = {
            "schema_version": "1.0",
            "contract": {
                "path": display_path(contract_path, root),
                "sha256": contract_hash,
                "contract_id": contract["contract_id"],
                "contract_version": contract["contract_version"],
                "topic": contract["topic"],
                "lifecycle_status": contract["lifecycle_status"],
                "source_of_truth": authority["source_of_truth"],
                "reviewer_id": approval["reviewer_id"],
                "reviewer_role": approval["reviewer_role"],
                "reviewed_at": approval["reviewed_at"],
            },
            "release": {
                "report_path": display_path(release_path, root),
                "report_sha256": sha256(release_path),
                "release_gate": release["release_gate"],
                "status": release["status"],
                "released_at": release["released_at"],
            },
            "validation": {
                "report_path": display_path(validation_path, root),
                "report_sha256": sha256(validation_path),
                "validator": validation["validator"],
                "valid": validation["valid"],
                "error_count": validation["error_count"],
            },
            "source_materials": contract["source_materials"],
            "grounding_inventory": {
                "path": display_path(inventory_path, root),
                "sha256": sha256(inventory_path),
            },
            "generation_view": {
                "path": view_path.name,
                "sha256": sha256(view_path),
            },
            "generation_items": {
                "required_item_ids": required_ids,
                "conditional_item_ids": conditional_ids,
                "excluded_item_ids": excluded_ids,
            },
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    print(f"PASS: released frozen grounding verified; receipt written to {output_path}; generation view written to {view_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
