#!/usr/bin/env python3
"""Validate C2 artifacts, cross-references, hashes, anchors, coverage, and code."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ARTIFACT_SCHEMAS = {
    "run_manifest.json": "run-manifest.schema.json",
    "source_manifest.json": "source-manifest.schema.json",
    "learner_profile.json": "learner-profile.schema.json",
    "adaptation_plan.json": "adaptation-plan.schema.json",
    "source_claims.json": "source-claims.schema.json",
    "claim_ledger.json": "claim-ledger.schema.json",
    "provenance.json": "provenance.schema.json",
    "code_validation.json": "code-validation.schema.json",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def duplicate_values(values):
    seen, duplicates = set(), set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--schemas-dir", default=str(Path(__file__).resolve().parent.parent / "references"))
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    root = Path(args.workspace_root).resolve()
    schemas_dir = Path(args.schemas_dir).resolve()
    errors, warnings, schema_checks = [], [], []
    documents = {}

    for artifact, schema_name in ARTIFACT_SCHEMAS.items():
        artifact_path = run_dir / artifact
        artifact_errors = []
        try:
            document = load_json(artifact_path)
            schema = load_json(schemas_dir / schema_name)
            validator = Draft202012Validator(schema, format_checker=FormatChecker())
            for issue in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
                location = ".".join(str(part) for part in issue.path) or "$"
                artifact_errors.append(f"{location}: {issue.message}")
            documents[artifact] = document
        except (OSError, json.JSONDecodeError) as exc:
            artifact_errors.append(str(exc))
        schema_checks.append({"artifact": artifact, "status": "failed" if artifact_errors else "passed", "errors": artifact_errors})
        errors.extend(f"{artifact}: {message}" for message in artifact_errors)

    source_hashes_valid = False
    claim_anchors_valid = False
    source_coverage_complete = False
    provenance_complete = False
    code_execution_passed = False

    if "source_manifest.json" in documents:
        source_hashes_valid = True
        for source in documents["source_manifest.json"].get("sources", []):
            source_path = Path(source["path"])
            if not source_path.is_absolute():
                source_path = root / source_path
            if not source_path.is_file():
                errors.append(f"missing source file: {source['path']}")
                source_hashes_valid = False
                continue
            actual = hashlib.sha256(source_path.read_bytes()).hexdigest()
            if actual != source["sha256"]:
                errors.append(f"source hash mismatch: {source['source_id']}")
                source_hashes_valid = False
            if source_path.stat().st_size != source["size_bytes"]:
                errors.append(f"source size mismatch: {source['source_id']}")
                source_hashes_valid = False

    required_cross_docs = {"source_manifest.json", "source_claims.json", "claim_ledger.json", "provenance.json"}
    if required_cross_docs.issubset(documents):
        source_ids = [item["source_id"] for item in documents["source_manifest.json"].get("sources", [])]
        source_claims = documents["source_claims.json"].get("claims", [])
        generated_claims = documents["claim_ledger.json"].get("generated_claims", [])
        records = documents["provenance.json"].get("records", [])
        source_claim_ids = [item["source_claim_id"] for item in source_claims]
        generated_claim_ids = [item["generated_claim_id"] for item in generated_claims]

        for label, values in (("source_id", source_ids), ("source_claim_id", source_claim_ids), ("generated_claim_id", generated_claim_ids), ("provenance_id", [r["provenance_id"] for r in records])):
            for duplicate in sorted(duplicate_values(values)):
                errors.append(f"duplicate {label}: {duplicate}")

        source_id_set, source_claim_set, generated_claim_set = set(source_ids), set(source_claim_ids), set(generated_claim_ids)
        run_manifest = documents.get("run_manifest.json", {})
        plan = documents.get("adaptation_plan.json", {})
        learner_profile = documents.get("learner_profile.json", {})
        provenance = documents["provenance.json"]
        if set(run_manifest.get("source_ids", [])) != source_id_set:
            errors.append("run_manifest source_ids do not exactly match source_manifest")
        if set(plan.get("source_ids", [])) != source_id_set:
            errors.append("adaptation_plan source_ids do not exactly match source_manifest")
        profile_ids = {run_manifest.get("profile_id"), plan.get("profile_id"), learner_profile.get("profile_id"), provenance.get("profile_id")}
        if len(profile_ids) != 1:
            errors.append(f"profile_id mismatch across artifacts: {sorted(str(value) for value in profile_ids)}")
        if set(provenance.get("source_ids", [])) != source_id_set:
            errors.append("provenance source_ids do not exactly match source_manifest")
        for claim in source_claims:
            if claim["source_id"] not in source_id_set:
                errors.append(f"unknown source_id in {claim['source_claim_id']}: {claim['source_id']}")
        for claim in generated_claims:
            unknown = set(claim["source_claim_ids"]) - source_claim_set
            if unknown:
                errors.append(f"unknown source claims in {claim['generated_claim_id']}: {sorted(unknown)}")
            if claim["support_class"] in {"directly_supported", "derived_from_source"} and not claim["source_claim_ids"]:
                errors.append(f"supported claim has no source reference: {claim['generated_claim_id']}")
        for record in records:
            if record["generated_claim_id"] not in generated_claim_set:
                errors.append(f"unknown generated claim in {record['provenance_id']}: {record['generated_claim_id']}")
            unknown = set(record["source_claim_ids"]) - source_claim_set
            if unknown:
                errors.append(f"unknown source claims in {record['provenance_id']}: {sorted(unknown)}")
        plan_claim_ids = {
            claim_id
            for chapter in plan.get("chapter_sequence", [])
            for claim_id in chapter.get("source_claim_ids", [])
        } | {
            claim_id
            for bridge in plan.get("discipline_bridges", [])
            for claim_id in bridge.get("source_claim_ids", [])
        } | {
            item.get("source_claim_id") for item in plan.get("coverage_decisions", [])
        }
        unknown_plan_claims = plan_claim_ids - source_claim_set
        if unknown_plan_claims:
            errors.append(f"unknown source claims in adaptation_plan: {sorted(unknown_plan_claims)}")
        source_decisions = {claim["source_claim_id"]: claim["coverage_decision"] for claim in source_claims}
        plan_decisions = {item["source_claim_id"]: item["decision"] for item in plan.get("coverage_decisions", [])}
        if plan_decisions != source_decisions:
            errors.append("adaptation_plan coverage_decisions do not exactly match source_claims")

        content_path = run_dir / "adapted_content.md"
        if content_path.is_file():
            anchors = set(re.findall(r"<!--\s*(claim-GEN-[A-Za-z0-9._-]+)\s*-->", content_path.read_text(encoding="utf-8")))
            expected = {claim["anchor"] for claim in generated_claims}
            claim_anchors_valid = anchors == expected and all(claim["anchor"] == f"claim-{claim['generated_claim_id']}" for claim in generated_claims)
            code_anchors = {block.get("anchor") for block in documents.get("code_validation.json", {}).get("blocks", [])}
            if None in code_anchors or not code_anchors.issubset(expected):
                claim_anchors_valid = False
                errors.append("every executable code block must follow a valid generated-claim anchor")
            if anchors != expected:
                errors.append(f"claim anchor mismatch; missing={sorted(expected - anchors)}, extra={sorted(anchors - expected)}")
        else:
            errors.append("missing adapted_content.md")

        covered_source_claims = {claim_id for record in records for claim_id in record["source_claim_ids"]}
        required_source_claims = {claim["source_claim_id"] for claim in source_claims if claim["coverage_decision"] not in {"deferred", "omitted"}}
        source_coverage_complete = required_source_claims.issubset(covered_source_claims)
        if not source_coverage_complete:
            errors.append(f"uncovered source claims: {sorted(required_source_claims - covered_source_claims)}")

        record_generated_ids = [record["generated_claim_id"] for record in records]
        provenance_complete = set(record_generated_ids) == generated_claim_set and not duplicate_values(record_generated_ids)
        if not provenance_complete:
            errors.append("each generated claim must have exactly one provenance record")

    if "run_manifest.json" in documents and "code_validation.json" in documents:
        status = documents["code_validation.json"].get("overall_status")
        required = documents["run_manifest.json"].get("code_execution_required", False)
        code_execution_passed = status == "passed" or (status == "no_code" and not required)
        if not code_execution_passed:
            errors.append(f"code validation does not satisfy code_execution_required={required}: {status}")

    schemas_passed = all(item["status"] == "passed" for item in schema_checks)
    treatment_valid = all([schemas_passed, source_hashes_valid, claim_anchors_valid, source_coverage_complete, provenance_complete, code_execution_passed])
    warnings.append("This report verifies treatment integrity and mechanical checks, not mathematical correctness; use an independent evaluator for RQ1 outcomes.")
    run_id = documents.get("run_manifest.json", {}).get("run_id", run_dir.name)
    report = {
        "run_id": run_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema_checks": schema_checks,
        "source_hashes_valid": source_hashes_valid,
        "claim_anchors_valid": claim_anchors_valid,
        "source_coverage_complete": source_coverage_complete,
        "provenance_complete": provenance_complete,
        "code_execution_passed": code_execution_passed,
        "treatment_valid": treatment_valid,
        "content_correctness_verified": False,
        "errors": errors,
        "warnings": warnings,
    }
    (run_dir / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if treatment_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
