from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SCRIPT = Path(__file__).resolve().parents[1] / "validate_dependency_model.py"
CONTRACT = REPO / "experiments/rq1/reference-contracts/power-iteration-v1/release/frozen_reference_contract.json"
CANDIDATE = REPO / "curriculum-models/power-iteration-v1/candidate/contract-dependencies.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class DependencyModelValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.candidate = load(CANDIDATE)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_candidate(self, candidate: dict, expected: int) -> dict:
        candidate_path = self.root / "candidate.json"
        report_path = self.root / "report.json"
        candidate_path.write_text(json.dumps(candidate, indent=2) + "\n", encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--workspace-root",
                str(REPO),
                "--contract",
                str(CONTRACT),
                "--candidate",
                str(candidate_path),
                "--output",
                str(report_path),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return load(report_path)

    def test_accepts_bound_complete_acyclic_candidate(self) -> None:
        report = self.run_candidate(self.candidate, 0)
        self.assertTrue(report["valid"])
        self.assertEqual(report["metrics"]["contract_item_count"], 18)
        self.assertEqual(report["metrics"]["candidate_item_count"], 18)
        self.assertTrue(report["metrics"]["directed_graph_acyclic"])

    def test_rejects_missing_contract_item(self) -> None:
        candidate = copy.deepcopy(self.candidate)
        candidate["items"] = [item for item in candidate["items"] if item["item_id"] != "RC-018"]
        report = self.run_candidate(candidate, 1)
        self.assertTrue(any(error["code"] == "items.coverage" for error in report["errors"]))

    def test_rejects_directed_dependency_cycle(self) -> None:
        candidate = copy.deepcopy(self.candidate)
        by_id = {item["item_id"]: item for item in candidate["items"]}
        by_id["RC-001"]["hard_dependencies"] = ["RC-005"]
        report = self.run_candidate(candidate, 1)
        self.assertTrue(any(error["code"] == "relationship.cycle" for error in report["errors"]))

    def test_rejects_inconsistent_external_concept_binding(self) -> None:
        candidate = copy.deepcopy(self.candidate)
        concept = next(
            item for item in candidate["external_prerequisite_concepts"]
            if item["concept_id"] == "matrix-vector-products"
        )
        concept["supports_item_ids"].remove("RC-005")
        report = self.run_candidate(candidate, 1)
        self.assertTrue(any(error["code"] == "concepts.forward_binding" for error in report["errors"]))

    def test_rejects_candidate_that_claims_release(self) -> None:
        candidate = copy.deepcopy(self.candidate)
        candidate["lifecycle_status"] = "released"
        report = self.run_candidate(candidate, 1)
        self.assertTrue(any(error["code"] == "schema.const" for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()

