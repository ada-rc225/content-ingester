#!/usr/bin/env python3
"""Validate and atomically release an approved curriculum dependency model."""

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


GATE = "curriculum-model-release-gate-v1"
ITEM_FIELDS = (
    "hard_dependencies",
    "explanatory_dependencies",
    "implementation_dependencies",
    "co_requisite_item_ids",
    "recommended_neighbours",
    "external_prerequisite_concept_ids",
    "fallback_when_explanatory_dependencies_omitted",
    "rationale_and_confidence",
)
CONCEPT_FIELDS = (
    "need_type",
    "supports_item_ids",
    "bridge_candidate_id",
    "content_boundary_and_rationale",
)
RELEASE_FILES = (
    "frozen-contract-dependencies.json",
    "frozen-curriculum-review.json",
    "frozen-curriculum-validation-report.json",
    "frozen-curriculum-model.sha256",
    "curriculum-release-report.json",
)


class GateError(ValueError):
    """A release-policy failure with a stable diagnostic code."""

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
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_recorded_path(root: Path, raw_path: Any) -> Path | None:
    if not isinstance(raw_path, str) or not raw_path:
        return None
    path = Path(raw_path)
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


def validate_input_paths(paths: dict[str, Path]) -> None:
    for label, path in paths.items():
        require(path.is_file(), "input.missing", f"missing {label}: {path}")


def validate_candidate_state(candidate: dict[str, Any]) -> None:
    require(candidate.get("lifecycle_status") == "candidate", "candidate.lifecycle", "dependency model must be a candidate")
    require(candidate.get("review_status") == "unreviewed", "candidate.review_status", "candidate review_status must be unreviewed before release")
    require(candidate.get("approval") is None, "candidate.approval", "candidate approval must be null before release")
    require(isinstance(candidate.get("model_id"), str) and candidate["model_id"], "candidate.model_id", "candidate model_id is missing")
    items = candidate.get("items")
    concepts = candidate.get("external_prerequisite_concepts")
    require(isinstance(items, list) and items, "candidate.items", "candidate must contain dependency items")
    require(isinstance(concepts, list), "candidate.concepts", "candidate external prerequisites must be an array")
    require(all(isinstance(item, dict) and item.get("review_status") == "unreviewed" for item in items), "candidate.item_status", "every candidate item review_status must be unreviewed")
    require(all(isinstance(concept, dict) and concept.get("status") == "candidate" for concept in concepts), "candidate.bridge_status", "every external prerequisite must remain status=candidate")


def validate_base_report(
    root: Path,
    contract_path: Path,
    candidate_path: Path,
    report_path: Path,
    candidate: dict[str, Any],
    report: dict[str, Any],
) -> None:
    require(report.get("valid") is True and report.get("error_count") == 0, "validation.failed", "dependency validation report is not valid")
    inputs = report.get("inputs")
    require(isinstance(inputs, dict), "validation.inputs", "dependency validation report inputs are missing")
    require(resolve_recorded_path(root, inputs.get("contract")) == contract_path, "validation.contract", "dependency validation report identifies another Frozen Contract")
    require(inputs.get("contract_sha256") == sha256(contract_path), "validation.contract_hash", "Frozen Contract changed after dependency validation")
    require(resolve_recorded_path(root, inputs.get("candidate")) == candidate_path, "validation.candidate", "dependency validation report identifies another candidate")
    require(inputs.get("candidate_sha256") == sha256(candidate_path), "validation.candidate_hash", "candidate changed after dependency validation")
    source = candidate.get("source_contract")
    require(isinstance(source, dict), "candidate.source_contract", "candidate source_contract binding is missing")
    require(resolve_recorded_path(root, source.get("file")) == contract_path, "candidate.contract", "candidate identifies another Frozen Contract")
    require(source.get("sha256") == sha256(contract_path), "candidate.contract_hash", "candidate Frozen Contract hash is stale")


def rerun_base_validator(
    root: Path,
    contract_path: Path,
    candidate_path: Path,
    supplied_report: dict[str, Any],
    output_path: Path,
) -> None:
    script = root / ".github/skills/build-curriculum-dependencies/scripts/validate_dependency_model.py"
    require(script.is_file(), "validator.missing", f"missing dependency validator: {script}")
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--workspace-root", str(root),
            "--contract", str(contract_path),
            "--candidate", str(candidate_path),
            "--output", str(output_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    require(result.returncode == 0, "validation.rerun", (result.stdout + result.stderr).strip() or "base dependency validation failed")
    fresh = load_object(output_path)
    require(fresh == supplied_report, "validation.stale_report", "stored dependency validation report differs from a fresh deterministic validation")


def validate_review_binding(
    root: Path,
    contract_path: Path,
    candidate_path: Path,
    validation_path: Path,
    candidate: dict[str, Any],
    review: dict[str, Any],
) -> None:
    binding = review.get("candidate_binding")
    require(isinstance(binding, dict), "review.binding", "review candidate_binding is missing")
    require(binding.get("model_id") == candidate.get("model_id"), "review.model_id", "review binds another dependency model")
    require(resolve_recorded_path(root, binding.get("candidate_file")) == candidate_path, "review.candidate", "review identifies another candidate")
    require(binding.get("candidate_sha256") == sha256(candidate_path), "review.candidate_hash", "candidate changed after review template generation")
    require(resolve_recorded_path(root, binding.get("validation_report_file")) == validation_path, "review.validation", "review identifies another validation report")
    require(binding.get("validation_report_sha256") == sha256(validation_path), "review.validation_hash", "validation report changed after review template generation")
    require(resolve_recorded_path(root, binding.get("source_contract_file")) == contract_path, "review.contract", "review identifies another Frozen Contract")
    require(binding.get("source_contract_sha256") == sha256(contract_path), "review.contract_hash", "Frozen Contract changed after review template generation")


def validate_not_applicable(item: dict[str, Any], field: str) -> None:
    if field in ITEM_FIELDS[:6]:
        require(item.get(field) == [], "review.not_applicable", f"{item.get('item_id')}.{field} is not empty and cannot be not_applicable")
    elif field == "fallback_when_explanatory_dependencies_omitted":
        fallback = item.get(field)
        require(isinstance(fallback, dict) and fallback.get("allowed") is False and fallback.get("instruction") is None, "review.not_applicable", f"{item.get('item_id')}.{field} is active and cannot be not_applicable")
    else:
        raise GateError("review.not_applicable", f"{item.get('item_id')}.{field} cannot be not_applicable")


def validate_review_completion(candidate: dict[str, Any], review: dict[str, Any]) -> dict[str, str]:
    require(review.get("review_status") == "approved", "review.status", "review_status must be approved")
    reviewer = review.get("reviewer")
    require(isinstance(reviewer, dict), "review.reviewer", "reviewer record is missing")
    reviewer_id = reviewer.get("reviewer_id")
    reviewer_role = reviewer.get("reviewer_role")
    require(isinstance(reviewer_id, str) and reviewer_id.strip(), "review.reviewer_id", "reviewer_id must be a non-empty recorded identity")
    require(isinstance(reviewer_role, str) and reviewer_role.strip(), "review.reviewer_role", "reviewer_role must be a non-empty recorded role")
    overall = review.get("overall_review")
    require(isinstance(overall, dict) and overall.get("decision") == "approved", "review.overall", "overall review decision must be approved")
    reviewed_at = parse_timestamp(overall.get("reviewed_at"), "overall_review.reviewed_at")

    items = candidate["items"]
    item_map = {item.get("item_id"): item for item in items}
    item_reviews = review.get("item_reviews")
    require(isinstance(item_reviews, list), "review.items", "item_reviews must be an array")
    review_ids = [record.get("item_id") for record in item_reviews if isinstance(record, dict)]
    require(len(review_ids) == len(item_reviews) and len(review_ids) == len(set(review_ids)), "review.item_ids", "item reviews contain invalid or duplicate IDs")
    require(set(review_ids) == set(item_map), "review.item_coverage", "review item coverage must exactly equal candidate item coverage")
    for record in item_reviews:
        item_id = record["item_id"]
        require(record.get("decision") == "approved", "review.item_decision", f"{item_id} decision is not approved")
        decisions = record.get("field_decisions")
        require(isinstance(decisions, dict) and set(decisions) == set(ITEM_FIELDS), "review.item_fields", f"{item_id} field decisions are incomplete")
        for field, decision in decisions.items():
            require(decision in {"approved", "not_applicable"}, "review.field_decision", f"{item_id}.{field} decision is {decision!r}")
            if decision == "not_applicable":
                validate_not_applicable(item_map[item_id], field)

    concepts = candidate["external_prerequisite_concepts"]
    concept_map = {concept.get("concept_id"): concept for concept in concepts}
    concept_reviews = review.get("external_prerequisite_reviews")
    require(isinstance(concept_reviews, list), "review.concepts", "external_prerequisite_reviews must be an array")
    concept_ids = [record.get("concept_id") for record in concept_reviews if isinstance(record, dict)]
    require(len(concept_ids) == len(concept_reviews) and len(concept_ids) == len(set(concept_ids)), "review.concept_ids", "concept reviews contain invalid or duplicate IDs")
    require(set(concept_ids) == set(concept_map), "review.concept_coverage", "concept review coverage must exactly equal candidate concept coverage")
    for record in concept_reviews:
        concept_id = record["concept_id"]
        require(record.get("decision") == "approved", "review.concept_decision", f"{concept_id} decision is not approved")
        decisions = record.get("field_decisions")
        require(isinstance(decisions, dict) and set(decisions) == set(CONCEPT_FIELDS), "review.concept_fields", f"{concept_id} field decisions are incomplete")
        for field, decision in decisions.items():
            require(decision == "approved", "review.concept_field_decision", f"{concept_id}.{field} decision must be approved because the candidate field is populated")

    return {
        "reviewer_id": reviewer_id,
        "reviewer_role": reviewer_role,
        "reviewed_at": reviewed_at,
    }


def validate_revision_lineage(
    root: Path,
    candidate_path: Path,
    validation_path: Path,
    review: dict[str, Any],
    work_dir: Path,
) -> dict[str, Any] | None:
    binding = review.get("revision_binding")
    if binding is None:
        return None
    require(isinstance(binding, dict), "revision.binding", "revision_binding must be null or an object")
    receipt_path = resolve_recorded_path(root, binding.get("receipt_file"))
    revision_report_path = resolve_recorded_path(root, binding.get("validation_report_file"))
    require(receipt_path is not None and receipt_path.is_file(), "revision.receipt", "bound revision receipt is missing")
    require(revision_report_path is not None and revision_report_path.is_file(), "revision.report", "bound revision validation report is missing")
    require(binding.get("receipt_sha256") == sha256(receipt_path), "revision.receipt_hash", "revision receipt hash does not match review")
    require(binding.get("validation_report_sha256") == sha256(revision_report_path), "revision.report_hash", "revision validation report hash does not match review")
    receipt = load_object(receipt_path)
    report = load_object(revision_report_path)
    require(receipt.get("mode") == "revision", "revision.mode", "revision receipt mode must be revision")
    require(report.get("valid") is True and report.get("error_count") == 0, "revision.invalid", "revision validation report is not valid")
    parent_candidate = receipt.get("parent_candidate")
    parent_review = receipt.get("parent_review")
    require(isinstance(parent_candidate, dict) and isinstance(parent_review, dict), "revision.parents", "revision receipt parent bindings are missing")
    parent_candidate_path = resolve_recorded_path(root, parent_candidate.get("file"))
    parent_review_path = resolve_recorded_path(root, parent_review.get("file"))
    require(parent_candidate_path is not None and parent_candidate_path.is_file(), "revision.parent_candidate", "parent candidate is missing")
    require(parent_review_path is not None and parent_review_path.is_file(), "revision.parent_review", "parent review is missing")
    require(parent_candidate.get("sha256") == sha256(parent_candidate_path) == binding.get("parent_candidate_sha256"), "revision.parent_candidate_hash", "parent candidate hash does not match revision lineage")
    require(parent_review.get("sha256") == sha256(parent_review_path) == binding.get("parent_review_sha256"), "revision.parent_review_hash", "parent review hash does not match revision lineage")

    inputs = report.get("inputs")
    require(isinstance(inputs, dict), "revision.inputs", "revision validation inputs are missing")
    expected = {
        "parent_candidate": parent_candidate_path,
        "parent_review": parent_review_path,
        "revision_receipt": receipt_path,
        "candidate": candidate_path,
        "dependency_validation_report": validation_path,
    }
    for field, path in expected.items():
        require(resolve_recorded_path(root, inputs.get(field)) == path, "revision.input_path", f"revision validation identifies another {field}")
        require(inputs.get(f"{field}_sha256") == sha256(path), "revision.input_hash", f"{field} changed after revision validation")

    validator = root / ".github/skills/build-curriculum-dependencies/scripts/validate_dependency_revision.py"
    require(validator.is_file(), "validator.missing", f"missing revision validator: {validator}")
    rerun_path = work_dir / "rerun-revision-validation.json"
    result = subprocess.run(
        [
            sys.executable,
            str(validator),
            "--workspace-root", str(root),
            "--parent-candidate", str(parent_candidate_path),
            "--parent-review", str(parent_review_path),
            "--revision-receipt", str(receipt_path),
            "--candidate", str(candidate_path),
            "--dependency-validation-report", str(validation_path),
            "--output", str(rerun_path),
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    require(result.returncode == 0, "revision.rerun", (result.stdout + result.stderr).strip() or "revision-scope validation failed")
    require(load_object(rerun_path) == report, "revision.stale_report", "stored revision validation report differs from a fresh deterministic validation")
    return {
        "receipt": display_path(receipt_path, root),
        "receipt_sha256": sha256(receipt_path),
        "validation_report": display_path(revision_report_path, root),
        "validation_report_sha256": sha256(revision_report_path),
        "parent_candidate": display_path(parent_candidate_path, root),
        "parent_candidate_sha256": sha256(parent_candidate_path),
        "parent_review": display_path(parent_review_path, root),
        "parent_review_sha256": sha256(parent_review_path),
    }


def make_frozen_model(
    candidate: dict[str, Any],
    review: dict[str, Any],
    review_hash: str,
    identity: dict[str, str],
    released_at: str,
) -> dict[str, Any]:
    frozen = deepcopy(candidate)
    frozen["lifecycle_status"] = "frozen"
    frozen["review_status"] = "approved"
    for item in frozen["items"]:
        item["review_status"] = "approved"
    frozen["approval"] = {
        "review_id": review["review_id"],
        "reviewer_id": identity["reviewer_id"],
        "reviewer_role": identity["reviewer_role"],
        "reviewed_at": identity["reviewed_at"],
        "review_sha256": review_hash,
        "release_gate": GATE,
        "released_at": released_at,
    }
    return frozen


def validate_frozen_transition(candidate: dict[str, Any], frozen: dict[str, Any]) -> None:
    expected = deepcopy(candidate)
    expected["lifecycle_status"] = "frozen"
    expected["review_status"] = "approved"
    expected["approval"] = frozen.get("approval")
    for item in expected["items"]:
        item["review_status"] = "approved"
    require(frozen == expected, "release.transition", "frozen model changed fields outside the authorised state transition")
    require(all(concept.get("status") == "candidate" for concept in frozen["external_prerequisite_concepts"]), "release.bridge_status", "release must not approve prerequisite bridge candidates")


def released_at_value(raw: str | None) -> str:
    if raw is None:
        return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    return parse_timestamp(raw, "released_at")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--validation-report", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--released-at", help="Fixed ISO 8601 release time for reproducible tests")
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    paths = {
        "contract": args.contract.resolve(),
        "candidate": args.candidate.resolve(),
        "validation_report": args.validation_report.resolve(),
        "review": args.review.resolve(),
    }
    output_dir = args.output_dir.resolve()
    if output_dir.exists():
        print(f"ERROR [release.exists]: refusing to overwrite existing release directory: {output_dir}")
        return 1

    stage: Path | None = None
    validation_work: Path | None = None
    try:
        validate_input_paths(paths)
        contract = load_object(paths["contract"])
        candidate = load_object(paths["candidate"])
        report = load_object(paths["validation_report"])
        review = load_object(paths["review"])
        validate_candidate_state(candidate)
        validate_base_report(root, paths["contract"], paths["candidate"], paths["validation_report"], candidate, report)
        validate_review_binding(root, paths["contract"], paths["candidate"], paths["validation_report"], candidate, review)
        identity = validate_review_completion(candidate, review)

        output_dir.parent.mkdir(parents=True, exist_ok=True)
        validation_work = Path(tempfile.mkdtemp(prefix=".curriculum-release-validation-", dir=output_dir.parent))
        rerun_base_validator(root, paths["contract"], paths["candidate"], report, validation_work / "rerun-base-validation.json")
        revision = validate_revision_lineage(root, paths["candidate"], paths["validation_report"], review, validation_work)

        released_at = released_at_value(args.released_at)
        review_hash = sha256(paths["review"])
        frozen = make_frozen_model(candidate, review, review_hash, identity, released_at)
        validate_frozen_transition(candidate, frozen)

        stage = Path(tempfile.mkdtemp(prefix=".curriculum-release-stage-", dir=output_dir.parent))
        frozen_path = stage / RELEASE_FILES[0]
        frozen_review_path = stage / RELEASE_FILES[1]
        frozen_validation_path = stage / RELEASE_FILES[2]
        checksum_path = stage / RELEASE_FILES[3]
        release_report_path = stage / RELEASE_FILES[4]
        write_object(frozen_path, frozen)
        shutil.copyfile(paths["review"], frozen_review_path)
        frozen_hash = sha256(frozen_path)
        checksum_path.write_text(f"{frozen_hash}  {frozen_path.name}\n", encoding="utf-8")

        schema_dir = Path(__file__).resolve().parents[1] / "references"
        frozen_schema = schema_dir / "frozen-curriculum-model.schema.json"
        release_schema = schema_dir / "curriculum-release-report.schema.json"
        validate_input_paths({"frozen schema": frozen_schema, "release schema": release_schema})
        validation = {
            "schema_version": "1.0",
            "validator": "curriculum-model-release-v1",
            "valid": True,
            "error_count": 0,
            "errors": [],
            "checks": {
                "frozen_contract_release_valid": True,
                "candidate_base_validation_rerun": True,
                "candidate_review_binding_valid": True,
                "review_complete_and_approved": True,
                "review_coverage_exact": True,
                "revision_scope_validation_rerun": revision is not None,
                "release_transition_content_preserved": True,
                "external_prerequisite_bridges_not_released": True,
            },
            "inputs": {
                "contract": display_path(paths["contract"], root),
                "contract_sha256": sha256(paths["contract"]),
                "candidate": display_path(paths["candidate"], root),
                "candidate_sha256": sha256(paths["candidate"]),
                "validation_report": display_path(paths["validation_report"], root),
                "validation_report_sha256": sha256(paths["validation_report"]),
                "review": display_path(paths["review"], root),
                "review_sha256": review_hash,
                "revision": revision,
                "frozen_schema": display_path(frozen_schema, root),
                "frozen_schema_sha256": sha256(frozen_schema),
                "release_report_schema": display_path(release_schema, root),
                "release_report_schema_sha256": sha256(release_schema),
            },
            "metrics": {
                "item_count": len(candidate["items"]),
                "external_prerequisite_concept_count": len(candidate["external_prerequisite_concepts"]),
                "approved_item_review_count": len(review["item_reviews"]),
                "approved_concept_review_count": len(review["external_prerequisite_reviews"]),
            },
        }
        write_object(frozen_validation_path, validation)

        output_paths = {name: output_dir / name for name in RELEASE_FILES}
        release_report = {
            "schema_version": "1.0",
            "release_gate": GATE,
            "status": "released",
            "released_at": released_at,
            "model_id": frozen["model_id"],
            "source_contract": frozen["source_contract"],
            "approval": frozen["approval"],
            "inputs": validation["inputs"],
            "outputs": {
                "frozen_model": display_path(output_paths[RELEASE_FILES[0]], root),
                "frozen_model_sha256": frozen_hash,
                "frozen_review": display_path(output_paths[RELEASE_FILES[1]], root),
                "frozen_review_sha256": sha256(frozen_review_path),
                "validation_report": display_path(output_paths[RELEASE_FILES[2]], root),
                "validation_report_sha256": sha256(frozen_validation_path),
                "checksum": display_path(output_paths[RELEASE_FILES[3]], root),
            },
            "bridge_release_status": "not_released",
        }
        write_object(release_report_path, release_report)
        require(tuple(sorted(path.name for path in stage.iterdir())) == tuple(sorted(RELEASE_FILES)), "release.outputs", "staged release contains unexpected files")
        os.replace(stage, output_dir)
        stage = None
    except (GateError, OSError, KeyError) as exc:
        code = exc.code if isinstance(exc, GateError) else "release.io"
        print(f"ERROR [{code}]: {exc}")
        return 1
    finally:
        if stage is not None and stage.exists():
            shutil.rmtree(stage)
        if validation_work is not None and validation_work.exists():
            shutil.rmtree(validation_work)

    print(f"PASS: curriculum dependency model released to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
