#!/usr/bin/env python3
"""Validate and atomically release an approved RQ2 bridge library."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any


GATE = "bridge-library-release-gate-v1"
REVIEW_FIELDS = (
    "correctness",
    "source_quality",
    "content_boundary",
    "dependency_support",
    "pedagogical_sufficiency",
)
RELEASE_FILES = (
    "released-bridge-catalog.json",
    "frozen-bridge-library-review.json",
    "frozen-bridge-library-validation-report.json",
    "released-bridge-catalog.sha256",
    "bridge-library-release-report.json",
)


class GateError(ValueError):
    """Release-policy failure with a stable diagnostic code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise GateError(code, message)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError("input.read", f"cannot read JSON object {path}: {exc}") from exc
    require(isinstance(value, dict), "input.type", f"JSON root must be an object: {path}")
    return value


def write_object(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_path(root: Path, raw: Any) -> Path | None:
    if not isinstance(raw, str) or not raw:
        return None
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def parse_timestamp(raw: Any, field: str) -> str:
    require(isinstance(raw, str) and raw, "review.timestamp", f"{field} must be a date-time")
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GateError("review.timestamp", f"{field} must be an ISO 8601 date-time") from exc
    require(parsed.tzinfo is not None, "review.timestamp", f"{field} must include a timezone")
    return raw


def validate_candidate(candidate: dict[str, Any]) -> None:
    require(candidate.get("schema_version") == "1.0", "candidate.schema", "candidate schema_version must be 1.0")
    require(candidate.get("status") == "candidate", "candidate.status", "library status must be candidate")
    require(isinstance(candidate.get("library_id"), str) and candidate["library_id"], "candidate.id", "library_id is missing")
    bridges = candidate.get("bridges")
    require(isinstance(bridges, list) and bridges, "candidate.bridges", "candidate must contain bridges")
    require(all(isinstance(item, dict) and item.get("status") == "candidate" for item in bridges), "candidate.bridge_status", "every bridge must have status=candidate")
    concept_ids = [item.get("concept_id") for item in bridges]
    require(all(isinstance(value, str) and value for value in concept_ids), "candidate.concept_id", "every bridge needs a concept_id")
    require(len(concept_ids) == len(set(concept_ids)), "candidate.concept_id", "bridge concept IDs must be unique")


def validate_stored_report(
    root: Path,
    candidate_path: Path,
    report_path: Path,
    report: dict[str, Any],
) -> None:
    require(report.get("valid") is True, "validation.failed", "bridge validation is not valid")
    require(report.get("error_count") == 0, "validation.errors", "bridge validation contains errors")
    require(report.get("warning_count") == 0, "validation.warnings", "bridge validation contains warnings")
    inputs = report.get("inputs")
    require(isinstance(inputs, dict), "validation.inputs", "validation inputs are missing")
    require(resolve_path(root, inputs.get("candidate")) == candidate_path, "validation.candidate", "validation identifies another candidate")
    require(inputs.get("candidate_sha256") == sha256(candidate_path), "validation.candidate_hash", "candidate changed after validation")
    require(report_path.is_file(), "input.missing", f"missing validation report: {report_path}")


def rerun_validator(
    root: Path,
    candidate_path: Path,
    stored: dict[str, Any],
    output_path: Path,
) -> None:
    inputs = stored["inputs"]
    model_path = resolve_path(root, inputs.get("model"))
    require(model_path is not None and model_path.is_file(), "validation.model", "recorded Frozen Curriculum Model is missing")
    require(inputs.get("model_sha256") == sha256(model_path), "validation.model_hash", "Frozen Curriculum Model changed after validation")
    pairs = inputs.get("pathway_review_pairs")
    require(isinstance(pairs, list) and pairs, "validation.pathways", "recorded pathway/review pairs are missing")
    command = [
        sys.executable,
        str(root / ".github/skills/build-grounded-bridge-library/scripts/validate_bridge_library.py"),
        "--workspace-root", str(root),
        "--model", str(model_path),
        "--candidate", str(candidate_path),
    ]
    for pair in pairs:
        require(isinstance(pair, dict), "validation.pathways", "invalid pathway/review pair")
        pathway = resolve_path(root, pair.get("pathway"))
        review = resolve_path(root, pair.get("review"))
        require(pathway is not None and pathway.is_file(), "validation.pathway", "recorded pathway is missing")
        require(review is not None and review.is_file(), "validation.pathway_review", "recorded pathway review is missing")
        command.extend(["--pathway-review", str(pathway), str(review)])
    command.extend(["--output", str(output_path)])
    result = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    require(result.returncode == 0, "validation.rerun", (result.stdout + result.stderr).strip() or "bridge validation rerun failed")
    fresh = load_object(output_path)
    stored_normalized = deepcopy(stored)
    fresh_normalized = deepcopy(fresh)
    stored_normalized.pop("validated_at", None)
    fresh_normalized.pop("validated_at", None)
    require(fresh_normalized == stored_normalized, "validation.stale_report", "stored validation differs from a fresh run")


def expected_review_record(bridge: dict[str, Any]) -> dict[str, Any]:
    return {
        "bridge_contract_id": bridge.get("bridge_contract_id"),
        "bridge_candidate_id": bridge.get("bridge_candidate_id"),
        "concept_id": bridge.get("concept_id"),
        "requested_by_profile_ids": bridge.get("requested_by_profile_ids"),
        "supports_item_ids": bridge.get("supports_item_ids"),
        "content_block_ids": [item.get("content_id") for item in bridge.get("teaching_content", [])],
        "source_ids": [item.get("source_id") for item in bridge.get("sources", [])],
    }


def validate_review(
    root: Path,
    candidate_path: Path,
    report_path: Path,
    candidate: dict[str, Any],
    review: dict[str, Any],
) -> dict[str, str]:
    binding = review.get("candidate_binding")
    require(isinstance(binding, dict), "review.binding", "review candidate_binding is missing")
    require(binding.get("library_id") == candidate.get("library_id"), "review.library_id", "review identifies another library")
    require(resolve_path(root, binding.get("candidate_file")) == candidate_path, "review.candidate", "review identifies another candidate")
    require(binding.get("candidate_sha256") == sha256(candidate_path), "review.candidate_hash", "candidate changed after review generation")
    require(resolve_path(root, binding.get("validation_report_file")) == report_path, "review.validation", "review identifies another validation report")
    require(binding.get("validation_report_sha256") == sha256(report_path), "review.validation_hash", "validation report changed after review generation")
    require(review.get("review_status") == "approved", "review.status", "review_status must be approved")
    reviewer = review.get("reviewer")
    require(isinstance(reviewer, dict), "review.reviewer", "reviewer record is missing")
    reviewer_id = reviewer.get("reviewer_id")
    reviewer_role = reviewer.get("reviewer_role")
    require(isinstance(reviewer_id, str) and reviewer_id.strip(), "review.reviewer_id", "reviewer_id is missing")
    require(isinstance(reviewer_role, str) and reviewer_role.strip(), "review.reviewer_role", "reviewer_role is missing")
    overall = review.get("overall_review")
    require(isinstance(overall, dict) and overall.get("decision") == "approved", "review.overall", "overall decision must be approved")
    reviewed_at = parse_timestamp(overall.get("reviewed_at"), "overall_review.reviewed_at")
    records = review.get("bridge_reviews")
    require(isinstance(records, list), "review.bridges", "bridge_reviews must be an array")
    by_concept = {record.get("concept_id"): record for record in records if isinstance(record, dict)}
    bridges = candidate["bridges"]
    require(len(by_concept) == len(records), "review.coverage", "bridge reviews contain invalid or duplicate concept IDs")
    require(set(by_concept) == {item["concept_id"] for item in bridges}, "review.coverage", "review coverage must exactly match candidate bridges")
    for bridge in bridges:
        concept_id = bridge["concept_id"]
        record = by_concept[concept_id]
        for field, expected in expected_review_record(bridge).items():
            require(record.get(field) == expected, "review.bridge_binding", f"review binding differs for {concept_id}.{field}")
        require(record.get("decision") == "approved", "review.bridge_decision", f"{concept_id} is not approved")
        decisions = record.get("field_decisions")
        require(isinstance(decisions, dict) and set(decisions) == set(REVIEW_FIELDS), "review.fields", f"{concept_id} field decisions are incomplete")
        require(all(value == "approved" for value in decisions.values()), "review.field_decision", f"{concept_id} has a non-approved field")
    return {
        "reviewer_id": reviewer_id,
        "reviewer_role": reviewer_role,
        "reviewed_at": reviewed_at,
    }


def make_released_catalog(
    candidate: dict[str, Any],
    review: dict[str, Any],
    review_hash: str,
    identity: dict[str, str],
    released_at: str,
) -> dict[str, Any]:
    catalog = deepcopy(candidate)
    catalog["status"] = "released"
    for bridge in catalog["bridges"]:
        bridge["status"] = "released"
    catalog["approval"] = {
        "review_id": review["review_id"],
        "reviewer_id": identity["reviewer_id"],
        "reviewer_role": identity["reviewer_role"],
        "reviewed_at": identity["reviewed_at"],
        "review_sha256": review_hash,
        "release_gate": GATE,
        "released_at": released_at,
    }
    return catalog


def validate_transition(candidate: dict[str, Any], catalog: dict[str, Any]) -> None:
    expected = deepcopy(candidate)
    expected["status"] = "released"
    for bridge in expected["bridges"]:
        bridge["status"] = "released"
    expected["approval"] = catalog.get("approval")
    require(catalog == expected, "release.transition", "release changed fields outside the authorised transition")


def release_time(raw: str | None) -> str:
    if raw is not None:
        return parse_timestamp(raw, "released_at")
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--validation-report", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--released-at", help="Fixed ISO 8601 release time for reproducible tests")
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    candidate_path = args.candidate.resolve()
    report_path = args.validation_report.resolve()
    review_path = args.review.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        print(f"ERROR [release.exists]: refusing to overwrite existing release directory: {output_dir}")
        return 1

    stage: Path | None = None
    work: Path | None = None
    try:
        for label, path in (("candidate", candidate_path), ("validation report", report_path), ("review", review_path)):
            require(path.is_file(), "input.missing", f"missing {label}: {path}")
        candidate = load_object(candidate_path)
        report = load_object(report_path)
        review = load_object(review_path)
        validate_candidate(candidate)
        validate_stored_report(root, candidate_path, report_path, report)
        identity = validate_review(root, candidate_path, report_path, candidate, review)

        output_dir.parent.mkdir(parents=True, exist_ok=True)
        work = Path(tempfile.mkdtemp(prefix=".bridge-release-validation-", dir=output_dir.parent))
        rerun_validator(root, candidate_path, report, work / "rerun-validation.json")

        released_at = release_time(args.released_at)
        review_hash = sha256(review_path)
        catalog = make_released_catalog(candidate, review, review_hash, identity, released_at)
        validate_transition(candidate, catalog)

        stage = Path(tempfile.mkdtemp(prefix=".bridge-release-stage-", dir=output_dir.parent))
        catalog_path = stage / RELEASE_FILES[0]
        frozen_review_path = stage / RELEASE_FILES[1]
        release_validation_path = stage / RELEASE_FILES[2]
        checksum_path = stage / RELEASE_FILES[3]
        release_report_path = stage / RELEASE_FILES[4]
        write_object(catalog_path, catalog)
        shutil.copyfile(review_path, frozen_review_path)
        catalog_hash = sha256(catalog_path)
        checksum_path.write_text(f"{catalog_hash}  {catalog_path.name}\n", encoding="utf-8")

        reference_dir = Path(__file__).resolve().parents[1] / "references"
        catalog_schema = reference_dir / "released-bridge-catalog.schema.json"
        release_schema = reference_dir / "bridge-library-release-report.schema.json"
        require(catalog_schema.is_file() and release_schema.is_file(), "schema.missing", "release schemas are missing")
        validation = {
            "schema_version": "1.0",
            "validator": "bridge-library-release-v1",
            "valid": True,
            "error_count": 0,
            "warning_count": 0,
            "errors": [],
            "warnings": [],
            "checks": {
                "candidate_validation_rerun": True,
                "curriculum_and_pathway_authorities_current": True,
                "candidate_review_binding_valid": True,
                "review_complete_and_approved": True,
                "review_coverage_exact": True,
                "release_transition_content_preserved": True,
            },
            "inputs": {
                "candidate": display_path(candidate_path, root),
                "candidate_sha256": sha256(candidate_path),
                "validation_report": display_path(report_path, root),
                "validation_report_sha256": sha256(report_path),
                "review": display_path(review_path, root),
                "review_sha256": review_hash,
                "catalog_schema": display_path(catalog_schema, root),
                "catalog_schema_sha256": sha256(catalog_schema),
                "release_report_schema": display_path(release_schema, root),
                "release_report_schema_sha256": sha256(release_schema),
            },
            "metrics": {
                "released_bridge_count": len(catalog["bridges"]),
                "approved_bridge_review_count": len(review["bridge_reviews"]),
                "source_count": sum(len(item["sources"]) for item in catalog["bridges"]),
                "content_block_count": sum(len(item["teaching_content"]) for item in catalog["bridges"]),
            },
        }
        write_object(release_validation_path, validation)

        output_paths = {name: output_dir / name for name in RELEASE_FILES}
        release_report = {
            "schema_version": "1.0",
            "release_gate": GATE,
            "status": "released",
            "released_at": released_at,
            "library_id": catalog["library_id"],
            "approval": catalog["approval"],
            "inputs": validation["inputs"],
            "outputs": {
                "released_bridge_catalog": display_path(output_paths[RELEASE_FILES[0]], root),
                "released_bridge_catalog_sha256": catalog_hash,
                "frozen_review": display_path(output_paths[RELEASE_FILES[1]], root),
                "frozen_review_sha256": sha256(frozen_review_path),
                "release_validation_report": display_path(output_paths[RELEASE_FILES[2]], root),
                "release_validation_report_sha256": sha256(release_validation_path),
                "checksum": display_path(output_paths[RELEASE_FILES[3]], root),
            },
        }
        write_object(release_report_path, release_report)
        require({path.name for path in stage.iterdir()} == set(RELEASE_FILES), "release.outputs", "staged release contains unexpected files")
        os.replace(stage, output_dir)
        stage = None
    except (GateError, OSError, KeyError, TypeError) as exc:
        code = exc.code if isinstance(exc, GateError) else "release.io"
        print(f"ERROR [{code}]: {exc}")
        return 1
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
        if work is not None and work.exists():
            shutil.rmtree(work)

    print(f"PASS: bridge library released to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
