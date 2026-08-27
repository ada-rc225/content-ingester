#!/usr/bin/env python3
"""Deterministically merge, validate, fingerprint, and release a frozen contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from manage_human_review import apply_review, load_json, review_basis_sha256, write_json
from validate_reference_contract import VALIDATOR_VERSION, validate_contract


OUTPUT_NAMES = (
    "frozen_reference_contract.json",
    "frozen_contract_validation_report.json",
    "frozen_contract.sha256",
    "release_gate_report.json",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path, workspace_root: Path) -> str:
    try:
        return path.resolve().relative_to(workspace_root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--contract", required=True)
    parser.add_argument("--review", required=True)
    parser.add_argument("--source-manifest", required=True)
    parser.add_argument("--grounding-inventory", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    contract_path = Path(args.contract).resolve()
    review_path = Path(args.review).resolve()
    manifest_path = Path(args.source_manifest).resolve()
    inventory_path = Path(args.grounding_inventory).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_paths = {name: output_dir / name for name in OUTPUT_NAMES}
    existing = [path for path in output_paths.values() if path.exists()]
    if existing:
        parser.error(
            "release outputs already exist; use a new versioned output directory: "
            + ", ".join(str(path) for path in existing)
        )

    temporary_path: Path | None = None
    try:
        contract = load_json(contract_path)
        review = load_json(review_path)
        frozen = apply_review(contract, review)
        if frozen.get("lifecycle_status") != "frozen":
            raise ValueError("human review is not approved; refusing to release")

        output_dir.mkdir(parents=True, exist_ok=True)
        descriptor, raw_temporary_path = tempfile.mkstemp(
            prefix=".release_candidate_", suffix=".json", dir=output_dir
        )
        os.close(descriptor)
        temporary_path = Path(raw_temporary_path)
        write_json(temporary_path, frozen)

        metrics: dict = {}
        findings = validate_contract(
            temporary_path,
            workspace_root,
            manifest_path,
            inventory_path,
            metrics,
        )
        if findings:
            messages = "; ".join(f"{finding.code}: {finding.message}" for finding in findings)
            raise ValueError(f"frozen contract validation failed: {messages}")

        frozen_path = output_paths["frozen_reference_contract.json"]
        temporary_path.replace(frozen_path)
        temporary_path = None
        frozen_sha256 = sha256_file(frozen_path)

        validation_report = {
            "validator": VALIDATOR_VERSION,
            "valid": True,
            "error_count": 0,
            "coverage_metrics": metrics,
            "errors": [],
        }
        write_json(output_paths["frozen_contract_validation_report.json"], validation_report)
        output_paths["frozen_contract.sha256"].write_text(
            f"{frozen_sha256}  frozen_reference_contract.json\n", encoding="utf-8"
        )

        release_report = {
            "release_gate": "grounding-release-gate-v1",
            "status": "released",
            "released_at": datetime.now(timezone.utc).isoformat(),
            "contract_id": frozen.get("contract_id"),
            "contract_version": frozen.get("contract_version"),
            "review_basis_sha256": review_basis_sha256(frozen),
            "reviewer": review.get("reviewer"),
            "inputs": {
                "contract": display_path(contract_path, workspace_root),
                "contract_sha256": sha256_file(contract_path),
                "human_review": display_path(review_path, workspace_root),
                "human_review_sha256": sha256_file(review_path),
                "source_manifest": display_path(manifest_path, workspace_root),
                "grounding_inventory": display_path(inventory_path, workspace_root),
            },
            "outputs": {
                "frozen_contract": display_path(frozen_path, workspace_root),
                "frozen_contract_sha256": frozen_sha256,
                "validation_report": display_path(
                    output_paths["frozen_contract_validation_report.json"], workspace_root
                ),
                "sha256_file": display_path(output_paths["frozen_contract.sha256"], workspace_root),
            },
        }
        write_json(output_paths["release_gate_report.json"], release_report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
        parser.error(str(exc))

    print(f"Released frozen contract to {output_paths['frozen_reference_contract.json']}")
    print(f"SHA-256: {frozen_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
