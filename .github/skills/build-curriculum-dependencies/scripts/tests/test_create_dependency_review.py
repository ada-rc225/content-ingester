from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SCRIPT = Path(__file__).resolve().parents[1] / "create_dependency_review.py"
CANDIDATE = REPO / "curriculum-models/power-iteration-v1/candidate/contract-dependencies.json"
VALIDATION = REPO / "curriculum-models/power-iteration-v1/candidate/dependency-validation-report.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class DependencyReviewTemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_generator(
        self,
        candidate: Path = CANDIDATE,
        validation: Path = VALIDATION,
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--workspace-root",
                str(REPO),
                "--candidate",
                str(candidate),
                "--validation-report",
                str(validation),
                "--output",
                str(self.root / "curriculum-dependency-review.json"),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def test_creates_fully_pending_hash_bound_review(self) -> None:
        self.run_generator()
        review = load(self.root / "curriculum-dependency-review.json")
        candidate = load(CANDIDATE)
        self.assertEqual(review["review_status"], "pending")
        self.assertIsNone(review["revision_binding"])
        self.assertEqual(review["candidate_binding"]["candidate_sha256"], sha256(CANDIDATE))
        self.assertEqual(
            [entry["item_id"] for entry in review["item_reviews"]],
            [entry["item_id"] for entry in candidate["items"]],
        )
        self.assertEqual(
            [entry["concept_id"] for entry in review["external_prerequisite_reviews"]],
            [entry["concept_id"] for entry in candidate["external_prerequisite_concepts"]],
        )
        for entry in review["item_reviews"]:
            self.assertEqual(entry["decision"], "pending")
            self.assertTrue(all(value == "pending" for value in entry["field_decisions"].values()))
        self.assertEqual(review["overall_review"]["decision"], "pending")
        self.assertIsNone(review["reviewer"]["reviewer_id"])

    def test_refuses_to_overwrite_review(self) -> None:
        self.run_generator()
        self.run_generator(expected=1)

    def test_rejects_candidate_changed_after_validation(self) -> None:
        candidate = copy.deepcopy(load(CANDIDATE))
        candidate["items"][0]["confidence"] = "medium"
        candidate_path = self.root / "changed-candidate.json"
        candidate_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
        validation = copy.deepcopy(load(VALIDATION))
        validation["inputs"]["candidate"] = str(candidate_path)
        validation_path = self.root / "validation.json"
        validation_path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
        self.run_generator(candidate_path, validation_path, expected=1)

    def test_rejects_non_passing_validation_report(self) -> None:
        validation = copy.deepcopy(load(VALIDATION))
        validation["valid"] = False
        validation["error_count"] = 1
        validation_path = self.root / "failed-validation.json"
        validation_path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
        self.run_generator(CANDIDATE, validation_path, expected=1)


if __name__ == "__main__":
    unittest.main()
