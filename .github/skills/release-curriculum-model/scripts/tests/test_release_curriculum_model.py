from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[5]
SCRIPT = ROOT / ".github/skills/release-curriculum-model/scripts/release_curriculum_model.py"
CONTRACT = ROOT / "experiments/rq1/reference-contracts/power-iteration-v1/release/frozen_reference_contract.json"
CANDIDATE_DIR = ROOT / "curriculum-models/power-iteration-v1/candidate-v2"
CANDIDATE = CANDIDATE_DIR / "contract-dependencies.json"
VALIDATION = CANDIDATE_DIR / "dependency-validation-report.json"
REVIEW = CANDIDATE_DIR / "curriculum-dependency-review.json"
FIXED_TIME = "2026-08-18T12:00:00Z"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CurriculumModelReleaseTests(unittest.TestCase):
    def run_gate(self, output: Path, review: Path = REVIEW) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--workspace-root", str(ROOT),
                "--contract", str(CONTRACT),
                "--candidate", str(CANDIDATE),
                "--validation-report", str(VALIDATION),
                "--review", str(review),
                "--output-dir", str(output),
                "--released-at", FIXED_TIME,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def changed_review(self, directory: Path, change) -> Path:
        review = json.loads(REVIEW.read_text(encoding="utf-8"))
        change(review)
        path = directory / "review.json"
        path.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
        return path

    @staticmethod
    def approve_populated_fields(review: dict) -> None:
        for item_id in ("RC-009", "RC-010", "RC-012"):
            record = next(item for item in review["item_reviews"] if item["item_id"] == item_id)
            record["field_decisions"]["external_prerequisite_concept_ids"] = "approved"

    def test_releases_approved_revision_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            review = self.changed_review(directory, self.approve_populated_fields)
            output = directory / "release"
            result = self.run_gate(output, review)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {
                    "frozen-contract-dependencies.json",
                    "frozen-curriculum-review.json",
                    "frozen-curriculum-validation-report.json",
                    "frozen-curriculum-model.sha256",
                    "curriculum-release-report.json",
                },
            )
            candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
            frozen_path = output / "frozen-contract-dependencies.json"
            frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
            self.assertEqual(frozen["lifecycle_status"], "frozen")
            self.assertEqual(frozen["review_status"], "approved")
            self.assertTrue(all(item["review_status"] == "approved" for item in frozen["items"]))
            self.assertTrue(all(concept["status"] == "candidate" for concept in frozen["external_prerequisite_concepts"]))
            self.assertEqual(
                [{k: v for k, v in item.items() if k != "review_status"} for item in frozen["items"]],
                [{k: v for k, v in item.items() if k != "review_status"} for item in candidate["items"]],
            )
            checksum = (output / "frozen-curriculum-model.sha256").read_text(encoding="utf-8").split()[0]
            self.assertEqual(checksum, file_hash(frozen_path))
            validation = json.loads((output / "frozen-curriculum-validation-report.json").read_text(encoding="utf-8"))
            self.assertTrue(validation["valid"])
            self.assertTrue(validation["checks"]["revision_scope_validation_rerun"])
            release = json.loads((output / "curriculum-release-report.json").read_text(encoding="utf-8"))
            self.assertEqual(release["status"], "released")
            self.assertEqual(release["bridge_release_status"], "not_released")

    def test_rejects_pending_review_without_partial_release(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            review = self.changed_review(directory, lambda value: value.__setitem__("review_status", "pending"))
            output = directory / "release"
            result = self.run_gate(output, review)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review.status", result.stdout)
            self.assertFalse(output.exists())

    def test_rejects_stale_candidate_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            review = self.changed_review(
                directory,
                lambda value: value["candidate_binding"].__setitem__("candidate_sha256", "0" * 64),
            )
            output = directory / "release"
            result = self.run_gate(output, review)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review.candidate_hash", result.stdout)
            self.assertFalse(output.exists())

    def test_rejects_invalid_not_applicable_decision(self) -> None:
        def change(review: dict) -> None:
            record = next(item for item in review["item_reviews"] if item["item_id"] == "RC-002")
            record["field_decisions"]["hard_dependencies"] = "not_applicable"

        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            review = self.changed_review(directory, change)
            output = directory / "release"
            result = self.run_gate(output, review)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review.not_applicable", result.stdout)
            self.assertFalse(output.exists())

    def test_rejects_stale_revision_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            def change(value: dict) -> None:
                self.approve_populated_fields(value)
                value["revision_binding"]["receipt_sha256"] = "0" * 64

            review = self.changed_review(directory, change)
            output = directory / "release"
            result = self.run_gate(output, review)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("revision.receipt_hash", result.stdout)
            self.assertFalse(output.exists())

    def test_refuses_existing_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "release"
            output.mkdir()
            sentinel = output / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            result = self.run_gate(output)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("release.exists", result.stdout)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
