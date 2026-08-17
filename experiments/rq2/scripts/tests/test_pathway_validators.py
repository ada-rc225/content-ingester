from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RQ2 = Path(__file__).resolve().parents[2]
SCRIPTS = RQ2 / "scripts"
SPECS = RQ2 / "specs" / "power-iteration"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class PathwayValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.canonical = load(SPECS / "canonical-pathway.json")
        self.common = load(SPECS / "common-core.json")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_validator(
        self, script: str, actual: dict, *extra: str, expected: int = 0
    ) -> dict:
        actual_path = self.root / "actual.json"
        report_path = self.root / "report.json"
        write(actual_path, actual)
        command = [
            sys.executable,
            str(SCRIPTS / script),
            "--canonical",
            str(SPECS / "canonical-pathway.json"),
            "--actual",
            str(actual_path),
            "--common-core",
            str(SPECS / "common-core.json"),
            "--permissions",
            str(SPECS / "condition-permissions.json"),
            *extra,
            "--output",
            str(report_path),
        ]
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return load(report_path)

    def fixed_fixture(self, condition: str = "P1") -> dict:
        actual = copy.deepcopy(self.canonical)
        actual["pathway_id"] = f"PI-{condition}-TEST"
        actual["condition"] = condition
        actual["profile_id"] = (
            "mechanical-engineering-year-2-rq2-pilot" if condition == "P1" else None
        )
        return actual

    def adaptive_fixture(self) -> dict:
        actual = copy.deepcopy(self.canonical)
        actual["pathway_id"] = "PI-P2-TEST"
        actual["condition"] = "P2"
        actual["profile_id"] = "mechanical-engineering-year-2-rq2-pilot"
        actual["instruction_sequence"] = [
            "PI-U01", "PI-U03", "PI-U02", "PI-U04", "PI-U05", "PI-U06", "PI-U07", "PI-U08"
        ]
        selected = [
            item_id
            for item_id in self.common["all_contract_item_ids"]
            if item_id != "RC-002"
        ]
        actual["selected_contract_item_ids"] = selected
        actual["excluded_contract_item_ids"] = ["RC-002"]
        by_id = {unit["unit_id"]: unit for unit in actual["learning_units"]}
        by_id["PI-U01"]["contract_item_ids"].remove("RC-002")
        actual["selection_decisions"] = []
        for item_id in self.common["selectable_item_ids"]:
            included = item_id != "RC-002"
            actual["selection_decisions"].append({
                "item_id": item_id,
                "decision": "include" if included else "exclude",
                "profile_attribute": "the declared learner profile and time budget",
                "rationale": (
                    "Use the limited time for the normalized iteration and convergence conditions."
                    if not included
                    else "Retain this extension because it supports the declared depth or implementation background."
                )
            })
        actual["pathway_changes"] = [
            {
                "change_type": "reorder_learning_units",
                "profile_attribute": "algorithmic update is a useful concrete entry point",
                "rationale": "Introduce the normalized update before the spectral derivation."
            },
            {
                "change_type": "regroup_contract_items",
                "profile_attribute": "characteristic-polynomial review is unnecessary for this profile",
                "rationale": "Remove the excluded optional item from the opening conceptual unit."
            },
            {
                "change_type": "change_item_selection",
                "profile_attribute": "time is better spent on convergence and implementation",
                "rationale": "Exclude characteristic-polynomial review and include the non-symmetric boundary."
            }
        ]
        return actual

    def test_accepts_exact_p0_and_p1_pathways(self) -> None:
        for condition in ("P0", "P1"):
            report = self.run_validator(
                "validate_fixed_pathway.py",
                self.fixed_fixture(condition),
                "--condition",
                condition,
            )
            self.assertTrue(report["valid"])
            self.assertEqual(report["checks"]["universal_core_coverage"], 1.0)

    def test_fixed_validator_rejects_reordering(self) -> None:
        actual = self.fixed_fixture()
        actual["instruction_sequence"][1], actual["instruction_sequence"][2] = (
            actual["instruction_sequence"][2],
            actual["instruction_sequence"][1],
        )
        report = self.run_validator(
            "validate_fixed_pathway.py", actual, "--condition", "P1", expected=1
        )
        self.assertFalse(report["valid"])
        self.assertTrue(any("changed instruction_sequence" in error for error in report["errors"]))

    def test_fixed_validator_rejects_contract_reassignment(self) -> None:
        actual = self.fixed_fixture()
        units = {unit["unit_id"]: unit for unit in actual["learning_units"]}
        units["PI-U01"]["contract_item_ids"].remove("RC-014")
        units["PI-U02"]["contract_item_ids"].append("RC-014")
        report = self.run_validator(
            "validate_fixed_pathway.py", actual, "--condition", "P1", expected=1
        )
        self.assertTrue(any("contract_item_ids" in error for error in report["errors"]))

    def test_accepts_rationalized_adaptive_pathway(self) -> None:
        report = self.run_validator(
            "validate_adaptive_pathway.py", self.adaptive_fixture()
        )
        self.assertTrue(report["valid"])
        self.assertTrue(report["materially_different"])
        self.assertEqual(report["checks"]["universal_core_coverage"], 1.0)
        self.assertIn("reorder_learning_units", report["detected_change_types"])
        self.assertIn("change_item_selection", report["detected_change_types"])

    def test_adaptive_validator_rejects_missing_universal_core(self) -> None:
        actual = self.adaptive_fixture()
        actual["selected_contract_item_ids"].remove("RC-001")
        actual["excluded_contract_item_ids"].append("RC-001")
        units = {unit["unit_id"]: unit for unit in actual["learning_units"]}
        units["PI-U01"]["contract_item_ids"].remove("RC-001")
        report = self.run_validator(
            "validate_adaptive_pathway.py", actual, expected=1
        )
        self.assertTrue(any("omits universal core" in error for error in report["errors"]))
        self.assertTrue(any("excludes non-selectable" in error for error in report["errors"]))

    def test_adaptive_validator_rejects_unapproved_bridge(self) -> None:
        actual = self.adaptive_fixture()
        bridge = {
            "unit_id": "PI-B01",
            "title": "Vector norm refresher",
            "unit_type": "prerequisite_bridge",
            "bridge_contract_id": "BR-NORM-UNRELEASED",
            "prerequisite_unit_ids": ["PI-U01"],
            "learning_objective_ids": [],
            "contract_item_ids": []
        }
        actual["learning_units"].append(bridge)
        actual["instruction_sequence"].insert(1, "PI-B01")
        actual["pathway_changes"].append({
            "change_type": "add_prerequisite_bridge",
            "profile_attribute": "vector norm knowledge is fragile",
            "rationale": "Refresh normalization before applying the update."
        })
        catalog = self.root / "bridges.json"
        write(catalog, {"bridges": []})
        report = self.run_validator(
            "validate_adaptive_pathway.py",
            actual,
            "--bridge-catalog",
            str(catalog),
            expected=1,
        )
        self.assertTrue(any("unapproved bridge" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
