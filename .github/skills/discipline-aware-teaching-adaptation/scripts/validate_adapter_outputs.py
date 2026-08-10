#!/usr/bin/env python3
"""Validate compact C2 evidence, section structure, source hashes, and code."""

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
    "core_invariants.json": "core-invariants.schema.json",
    "adaptation_plan.json": "adaptation-plan.schema.json",
    "provenance.json": "provenance.schema.json",
    "code_validation.json": "code-validation.schema.json",
}
SECTION_RE = re.compile(r"<!--\s*section:\s*(SEC-[0-9]{2})\s*-->\s*\n##\s+(.+?)\s*$", re.MULTILINE)
CODE_RE = re.compile(r"```(?:python|py)\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def duplicates(values):
    seen, repeated = set(), set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return repeated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--schemas-dir", default=str(Path(__file__).resolve().parent.parent / "references"))
    args = parser.parse_args()

    run_dir = Path(args.run_dir).resolve()
    root = Path(args.workspace_root).resolve()
    schemas_dir = Path(args.schemas_dir).resolve()
    errors, warnings, schema_checks, documents = [], [], [], {}

    for artifact, schema_name in ARTIFACT_SCHEMAS.items():
        artifact_errors = []
        try:
            document = load_json(run_dir / artifact)
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
    section_structure_valid = False
    invariant_coverage_complete = False
    provenance_complete = False
    code_execution_passed = False

    manifest = documents.get("source_manifest.json")
    if manifest:
        source_hashes_valid = True
        for source in manifest.get("sources", []):
            source_path = Path(source["path"])
            if not source_path.is_absolute():
                source_path = root / source_path
            if not source_path.is_file():
                errors.append(f"missing source file: {source['path']}")
                source_hashes_valid = False
                continue
            if hashlib.sha256(source_path.read_bytes()).hexdigest() != source["sha256"]:
                errors.append(f"source hash mismatch: {source['source_id']}")
                source_hashes_valid = False
            if source_path.stat().st_size != source["size_bytes"]:
                errors.append(f"source size mismatch: {source['source_id']}")
                source_hashes_valid = False

    required = {"run_manifest.json", "source_manifest.json", "learner_profile.json", "core_invariants.json", "adaptation_plan.json", "provenance.json", "code_validation.json"}
    if required.issubset(documents):
        run = documents["run_manifest.json"]
        plan = documents["adaptation_plan.json"]
        profile = documents["learner_profile.json"]
        provenance = documents["provenance.json"]
        invariants = documents["core_invariants.json"].get("invariants", [])
        source_ids = {item["source_id"] for item in manifest.get("sources", [])}
        if run.get("agent_version") != "2.1" or run.get("skill_version") != "2.1":
            errors.append("compact validator requires agent_version=2.1 and skill_version=2.1")
        invariant_ids = [item["invariant_id"] for item in invariants]
        invariant_set = set(invariant_ids)
        planned_sections = plan.get("chapter_sequence", [])
        planned_ids = [item["section_id"] for item in planned_sections]

        for label, values in (("invariant_id", invariant_ids), ("section_id", planned_ids)):
            for duplicate in sorted(duplicates(values)):
                errors.append(f"duplicate {label}: {duplicate}")

        if set(run.get("source_ids", [])) != source_ids or set(plan.get("source_ids", [])) != source_ids or set(provenance.get("source_ids", [])) != source_ids:
            errors.append("source_ids must exactly match source_manifest across run, plan, and provenance")
        profile_ids = {run.get("profile_id"), plan.get("profile_id"), profile.get("profile_id"), provenance.get("profile_id")}
        if len(profile_ids) != 1:
            errors.append(f"profile_id mismatch across artifacts: {sorted(str(value) for value in profile_ids)}")
        for invariant in invariants:
            if invariant["source_id"] not in source_ids:
                errors.append(f"unknown source_id in {invariant['invariant_id']}: {invariant['source_id']}")

        orders = [item["order"] for item in planned_sections]
        if orders != list(range(1, len(planned_sections) + 1)):
            errors.append("chapter order must be consecutive and match array order")
        planned_invariants = {value for item in planned_sections for value in item.get("invariant_ids", [])}
        unknown_plan_invariants = planned_invariants - invariant_set
        if unknown_plan_invariants:
            errors.append(f"unknown invariants in adaptation_plan: {sorted(unknown_plan_invariants)}")

        content_path = run_dir / "adapted_content.md"
        if content_path.is_file():
            content = content_path.read_text(encoding="utf-8")
            actual_sections = SECTION_RE.findall(content)
            actual_pairs = [(section_id, title.strip()) for section_id, title in actual_sections]
            expected_pairs = [(item["section_id"], item["title"].strip()) for item in planned_sections]
            section_structure_valid = actual_pairs == expected_pairs
            if not section_structure_valid:
                errors.append(f"content sections must exactly match plan; expected={expected_pairs}, actual={actual_pairs}")
            if "claim-GEN-" in content:
                warnings.append("Legacy claim anchors remain in adapted_content.md; v2.1 uses section anchors only.")
        else:
            errors.append("missing adapted_content.md")

        provenance_sections = provenance.get("sections", [])
        provenance_ids = [item["section_id"] for item in provenance_sections]
        provenance_by_id = {item["section_id"]: item for item in provenance_sections}
        plan_by_id = {item["section_id"]: item for item in planned_sections}
        provenance_complete = provenance_ids == planned_ids and not duplicates(provenance_ids)
        if provenance_complete:
            for section_id in planned_ids:
                recorded = set(provenance_by_id[section_id].get("invariant_ids", []))
                planned = set(plan_by_id[section_id].get("invariant_ids", []))
                if recorded != planned:
                    provenance_complete = False
                    errors.append(f"provenance invariant mismatch for {section_id}")
                unknown = recorded - invariant_set
                if unknown:
                    provenance_complete = False
                    errors.append(f"unknown invariants in provenance {section_id}: {sorted(unknown)}")
        else:
            errors.append("provenance sections must exactly match planned section order")

        covered = {value for item in provenance_sections for value in item.get("invariant_ids", [])}
        invariant_coverage_complete = invariant_set == planned_invariants == covered
        if not invariant_coverage_complete:
            errors.append(f"invariant coverage mismatch; uncovered={sorted(invariant_set - covered)}, unplanned={sorted(invariant_set - planned_invariants)}")

        code = documents["code_validation.json"]
        status = code.get("overall_status")
        code_required = run.get("code_execution_required", False)
        code_execution_passed = status == "passed" or (status == "no_code" and not code_required)
        try:
            recorded_content_path = Path(code.get("content_file", "")).resolve()
        except OSError:
            recorded_content_path = Path()
        if recorded_content_path != content_path.resolve():
            code_execution_passed = False
            errors.append("code_validation content_file does not identify this run's adapted_content.md")
        content_code_hashes = [hashlib.sha256(block.encode("utf-8")).hexdigest() for block in CODE_RE.findall(content)] if content_path.is_file() else []
        recorded_code_hashes = [block.get("code_sha256") for block in code.get("blocks", [])]
        if content_code_hashes != recorded_code_hashes:
            code_execution_passed = False
            errors.append("code_validation hashes do not match current Python blocks")
        valid_section_ids = set(planned_ids)
        invalid_code_anchors = [block.get("block_id") for block in code.get("blocks", []) if block.get("anchor") not in valid_section_ids]
        if invalid_code_anchors:
            code_execution_passed = False
            errors.append(f"code blocks without valid section anchors: {invalid_code_anchors}")
        if not code_execution_passed:
            errors.append(f"code validation does not satisfy code_execution_required={code_required}: {status}")

    schemas_passed = all(item["status"] == "passed" for item in schema_checks)
    treatment_valid = not errors and all([schemas_passed, source_hashes_valid, section_structure_valid, invariant_coverage_complete, provenance_complete, code_execution_passed])
    warnings.append("This report verifies compact C2 treatment integrity, not mathematical correctness; use an independent evaluator for RQ1 outcomes.")
    report = {
        "run_id": documents.get("run_manifest.json", {}).get("run_id", run_dir.name),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema_checks": schema_checks,
        "source_hashes_valid": source_hashes_valid,
        "section_structure_valid": section_structure_valid,
        "invariant_coverage_complete": invariant_coverage_complete,
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
