#!/usr/bin/env python3
"""Validate an RQ1 blind bundle without opening its secret condition mapping."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


FORBIDDEN_LABELS = ("c0-", "c1-", "c2-", "ungrounded", "source-conditioned", "structured-grounding")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_inside(bundle: Path, relative: str) -> Path:
    path = (bundle / relative).resolve()
    try:
        path.relative_to(bundle)
    except ValueError as exc:
        raise ValueError(f"path escapes bundle: {relative}") from exc
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    manifest_path = bundle / "evaluation_manifest.json"
    if not manifest_path.is_file():
        parser.error(f"missing manifest: {manifest_path}")
    if any(label in str(bundle).lower() for label in FORBIDDEN_LABELS):
        parser.error("bundle path exposes an experimental condition")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[str] = []
    if manifest.get("schema_version") != "1.0" or manifest.get("evaluation_protocol") != "RQ1-EVAL-v1":
        errors.append("unsupported manifest schema or protocol")
    contract_path = resolve_inside(bundle, manifest.get("contract", {}).get("file", ""))
    if not contract_path.is_file():
        errors.append("missing frozen contract")
    else:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        if contract.get("lifecycle_status") != "frozen" or not contract.get("approval"):
            errors.append("contract is not approved and frozen")
        if digest(contract_path) != manifest["contract"].get("sha256"):
            errors.append("contract SHA-256 mismatch")
    for key in ("learner_profile", "task_brief"):
        record = manifest.get(key, {})
        path = resolve_inside(bundle, record.get("file", ""))
        if not path.is_file() or digest(path) != record.get("sha256"):
            errors.append(f"{key} missing or SHA-256 mismatch")
    ids = []
    for sample in manifest.get("samples", []):
        sample_id = sample.get("sample_id", "")
        ids.append(sample_id)
        path = resolve_inside(bundle, sample.get("file", ""))
        if any(label in path.name.lower() for label in FORBIDDEN_LABELS):
            errors.append(f"sample filename exposes condition: {path.name}")
        if not path.is_file() or digest(path) != sample.get("content_sha256"):
            errors.append(f"sample missing or SHA-256 mismatch: {sample_id}")
    if len(ids) != len(set(ids)):
        errors.append("duplicate sample IDs")
    if not ids:
        errors.append("bundle contains no samples")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Blind bundle valid: {manifest['bundle_id']} ({len(ids)} samples)")
    print(f"Manifest SHA-256: {digest(manifest_path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
