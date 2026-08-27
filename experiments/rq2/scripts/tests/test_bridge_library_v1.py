#!/usr/bin/env python3
"""Regression tests for the simplified RQ2 bridge-library workflow."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
SKILL_SCRIPTS = (
    ROOT / ".github/skills/build-grounded-bridge-library/scripts"
)
VALIDATOR = SKILL_SCRIPTS / "validate_bridge_library.py"
REVIEW_GENERATOR = SKILL_SCRIPTS / "create_bridge_library_review.py"
MODEL = (
    ROOT
    / "curriculum-models/power-iteration-v1/release"
    / "frozen-contract-dependencies.json"
)
CANDIDATE = (
    ROOT
    / "bridge-library/power-iteration-v1/candidate"
    / "bridge-library-candidate.json"
)
PAIRS = [
    (
        "experiments/rq2/pathway-plans/power-iteration-v1/p2/"
        "applied-mathematics/run-03"
    ),
    (
        "experiments/rq2/pathway-plans/power-iteration-v1/p2/"
        "computer-science/run-02"
    ),
    (
        "experiments/rq2/pathway-plans/power-iteration-v1/p2/"
        "mechanical-engineering/run-02"
    ),
]


def validator_command(candidate: Path, output: Path) -> list[str]:
    command = [
        "python3", str(VALIDATOR),
        "--workspace-root", str(ROOT),
        "--model", str(MODEL),
        "--candidate", str(candidate),
    ]
    for relative in PAIRS:
        run_dir = ROOT / relative
        command.extend([
            "--pathway-review",
            str(run_dir / "pathway-plan.json"),
            str(run_dir / "pathway-plan-review.json"),
        ])
    command.extend(["--output", str(output)])
    return command


class BridgeLibraryWorkflowTests(unittest.TestCase):
    def test_current_candidate_validates_and_review_is_fully_pending(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            report = temporary / "validation.json"
            completed = subprocess.run(
                validator_command(CANDIDATE, report),
                check=False, capture_output=True, text=True,
            )
            self.assertEqual(
                completed.returncode, 0, completed.stdout + completed.stderr
            )
            validation = json.loads(report.read_text(encoding="utf-8"))
            self.assertTrue(validation["valid"])
            self.assertEqual(
                validation["metrics"]["required_bridge_count"], 4
            )

            review = temporary / "review.json"
            completed = subprocess.run(
                [
                    "python3", str(REVIEW_GENERATOR),
                    "--workspace-root", str(ROOT),
                    "--candidate", str(CANDIDATE),
                    "--validation-report", str(report),
                    "--output", str(review),
                ],
                check=False, capture_output=True, text=True,
            )
            self.assertEqual(
                completed.returncode, 0, completed.stdout + completed.stderr
            )
            value = json.loads(review.read_text(encoding="utf-8"))
            self.assertEqual(value["review_status"], "pending")
            self.assertEqual(len(value["bridge_reviews"]), 4)
            for item in value["bridge_reviews"]:
                self.assertEqual(item["decision"], "pending")
                self.assertEqual(
                    set(item["field_decisions"].values()), {"pending"}
                )
            self.assertEqual(
                value["overall_review"]["decision"], "pending"
            )

    def test_unused_or_missing_bridge_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            value = json.loads(CANDIDATE.read_text(encoding="utf-8"))
            value["bridges"] = value["bridges"][:-1]
            candidate = temporary / "candidate.json"
            candidate.write_text(
                json.dumps(value, indent=2) + "\n", encoding="utf-8"
            )
            report = temporary / "validation.json"
            completed = subprocess.run(
                validator_command(candidate, report),
                check=False, capture_output=True, text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            validation = json.loads(report.read_text(encoding="utf-8"))
            self.assertFalse(validation["valid"])
            self.assertIn(
                "candidate.demand_coverage",
                {error["code"] for error in validation["errors"]},
            )


if __name__ == "__main__":
    unittest.main()
