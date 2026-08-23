#!/usr/bin/env python3
"""Regression tests for P2 review-template and review-bounded revision workflow."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "experiments/rq2/pathway-plans/power-iteration-v1/p2/computer-science/run-01"
PARENT_PLAN = RUN / "pathway-plan.json"
PARENT_ASSESSMENT = RUN / "profile-concept-assessment.json"
PARENT_VALIDATION = RUN / "pathway-validation-report.json"
CREATE_REVIEW = ROOT / ".github/skills/plan-adaptive-curriculum-pathways/scripts/create_pathway_plan_review.py"
PREPARE_REVISION = ROOT / ".github/skills/plan-adaptive-curriculum-pathways/scripts/prepare_pathway_revision.py"
VALIDATE_REVISION = ROOT / ".github/skills/plan-adaptive-curriculum-pathways/scripts/validate_pathway_revision.py"
VALIDATE_PLAN = ROOT / "experiments/rq2/scripts/validate_pathway_plan.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


class PathwayReviewRevisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.directory = Path(self.temp.name)
        self.review_path = self.directory / "parent-review.json"
        self.create_review(self.review_path)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def create_review(self, output: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3", str(CREATE_REVIEW), "--workspace-root", str(ROOT),
                "--pathway", str(PARENT_PLAN), "--validation-report", str(PARENT_VALIDATION),
                "--assessment", str(PARENT_ASSESSMENT), "--output", str(output),
            ],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )

    def finalized_review(self) -> dict:
        review = load(self.review_path)
        review["review_status"] = "revision_required"
        review["reviewer"] = {"reviewer_id": "reviewer-001", "reviewer_role": "Curriculum reviewer"}
        for section in ("selection_reviews", "concept_reviews", "learning_goal_reviews", "pathway_change_reviews"):
            for record in review[section]:
                record["field_decisions"] = {field: "approved" for field in record["field_decisions"]}
                record["decision"] = "approved"
        for section in ("structure_review", "scope_review"):
            review[section]["field_decisions"] = {
                field: "approved" for field in review[section]["field_decisions"]
            }
            review[section]["decision"] = "approved"
        target = review["pathway_change_reviews"][0]
        target["field_decisions"]["rationale"] = "revision_required"
        target["decision"] = "revision_required"
        target["comment"] = "Replace the rationale with wording that precisely matches the retained item order."
        review["overall_review"] = {
            "decision": "revision_required",
            "reviewed_at": "2026-08-18T16:00:00Z",
            "comment": "Revise only the first pathway-change rationale.",
        }
        return review

    def prepare_receipt(self, review: dict | None = None) -> tuple[subprocess.CompletedProcess[str], Path]:
        if review is not None:
            write(self.review_path, review)
        receipt = self.directory / "revision/pathway-revision-receipt.json"
        result = subprocess.run(
            [
                "python3", str(PREPARE_REVISION), "--workspace-root", str(ROOT),
                "--parent-pathway", str(PARENT_PLAN),
                "--parent-validation-report", str(PARENT_VALIDATION),
                "--parent-assessment", str(PARENT_ASSESSMENT),
                "--parent-review", str(self.review_path), "--output", str(receipt),
            ],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        return result, receipt

    def make_candidate(self, receipt_path: Path, unauthorized: bool = False) -> tuple[Path, Path, Path]:
        receipt = load(receipt_path)
        assessment = copy.deepcopy(load(PARENT_ASSESSMENT))
        assessment["assessment_id"] = receipt["parent_assessment"]["next_assessment_id"]
        assessment["generated_by"] = {
            "producer": "adaptive-curriculum-pathway-planner",
            "producer_version": "1.1",
            "generated_at": "2026-08-18T16:05:00Z",
        }
        assessment_path = self.directory / "revision/profile-concept-assessment.json"
        write(assessment_path, assessment)

        plan = copy.deepcopy(load(PARENT_PLAN))
        plan["pathway_id"] = receipt["parent_pathway"]["next_pathway_id"]
        plan["profile_concept_assessment_binding"] = {
            "artifact_id": assessment["assessment_id"],
            "file": display(assessment_path),
            "sha256": digest(assessment_path),
        }
        plan["pathway_changes"][0]["rationale"] = "The characteristic-polynomial item is omitted while the remaining item order is preserved for this computational pathway."
        if unauthorized:
            plan["selection"]["decisions"][0]["rationale"] = "Unauthorized selection-rationale change."
        plan["generated_by"] = {
            "producer": "adaptive-curriculum-pathway-planner",
            "producer_version": "1.1",
            "method": "adaptive_pathway_planning",
            "generated_at": "2026-08-18T16:05:00Z",
        }
        plan_path = self.directory / "revision/pathway-plan.json"
        write(plan_path, plan)
        validation_path = self.directory / "revision/pathway-validation-report.json"
        result = subprocess.run(
            [
                "python3", str(VALIDATE_PLAN), "--workspace-root", str(ROOT),
                "--pathway", str(plan_path), "--output", str(validation_path),
                "--phase", "pilot",
            ],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return plan_path, assessment_path, validation_path

    def run_revision_validator(
        self, receipt: Path, plan: Path, assessment: Path, validation: Path
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        report = self.directory / "revision/pathway-revision-validation-report.json"
        result = subprocess.run(
            [
                "python3", str(VALIDATE_REVISION), "--workspace-root", str(ROOT),
                "--revision-receipt", str(receipt), "--candidate-pathway", str(plan),
                "--candidate-assessment", str(assessment),
                "--candidate-validation-report", str(validation), "--output", str(report),
            ],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        return result, load(report)

    def test_review_template_is_fully_pending_and_hash_bound(self) -> None:
        review = load(self.review_path)
        self.assertEqual(review["review_status"], "pending")
        self.assertEqual(review["candidate_binding"]["pathway_sha256"], digest(PARENT_PLAN))
        records = review["selection_reviews"] + review["concept_reviews"] + review["learning_goal_reviews"] + review["pathway_change_reviews"]
        self.assertTrue(all(record["decision"] == "pending" for record in records))
        self.assertTrue(all(set(record["field_decisions"].values()) == {"pending"} for record in records))
        self.assertEqual(review["overall_review"]["decision"], "pending")

    def test_revision_preflight_rejects_pending_review(self) -> None:
        result, _ = self.prepare_receipt()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("review.status", result.stdout)

    def test_revision_preflight_rejects_tampered_snapshot(self) -> None:
        review = self.finalized_review()
        review["selection_reviews"][0]["planned_decision"] = "exclude"
        result, _ = self.prepare_receipt(review)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("review.selection_snapshot", result.stdout)

    def test_authorized_rationale_revision_passes(self) -> None:
        result, receipt = self.prepare_receipt(self.finalized_review())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        plan, assessment, validation = self.make_candidate(receipt)
        checked, report = self.run_revision_validator(receipt, plan, assessment, validation)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertTrue(report["valid"])

    def test_legacy_parent_assessment_status_resets_to_provisional(self) -> None:
        result, receipt_path = self.prepare_receipt(self.finalized_review())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        legacy_parent = copy.deepcopy(load(PARENT_ASSESSMENT))
        legacy_parent["assessment_status"] = "pilot_candidate"
        legacy_parent_path = self.directory / "legacy-parent-assessment.json"
        write(legacy_parent_path, legacy_parent)

        receipt = load(receipt_path)
        receipt["parent_assessment"]["file"] = display(legacy_parent_path)
        receipt["parent_assessment"]["sha256"] = digest(legacy_parent_path)
        write(receipt_path, receipt)

        plan, assessment, validation = self.make_candidate(receipt_path)
        self.assertEqual(load(assessment)["assessment_status"], "provisional")
        checked, report = self.run_revision_validator(receipt_path, plan, assessment, validation)
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        self.assertTrue(report["valid"])

    def test_unreviewed_selection_change_fails(self) -> None:
        result, receipt = self.prepare_receipt(self.finalized_review())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        plan, assessment, validation = self.make_candidate(receipt, unauthorized=True)
        checked, report = self.run_revision_validator(receipt, plan, assessment, validation)
        self.assertNotEqual(checked.returncode, 0)
        self.assertIn("scope.selection_rationale", {error["code"] for error in report["errors"]})


if __name__ == "__main__":
    unittest.main()
