#!/usr/bin/env python3
"""Regression tests for deterministic unified P0 normalization and P1 copying."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
NORMALIZER = ROOT / "experiments/rq2/scripts/normalize_p0_pathway.py"
COPIER = ROOT / "experiments/rq2/scripts/copy_p1_pathway.py"
VALIDATOR = ROOT / "experiments/rq2/scripts/validate_pathway_plan.py"
CANONICAL = ROOT / "experiments/rq2/specs/power-iteration/canonical-pathway.json"
COMMON_CORE = ROOT / "experiments/rq2/specs/power-iteration/common-core.json"
MAPPING = ROOT / "experiments/rq2/specs/power-iteration/p0-normalization-map.json"
CONTRACT = ROOT / "experiments/rq1/reference-contracts/power-iteration-v1/release/frozen_reference_contract.json"
REQUEST = ROOT / "experiments/rq2/learning-requests/power-iteration-second-year.json"
PROFILE = ROOT / "experiments/rq2/profiles/computer-science-year-2.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class FixedPathwayGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.directory = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def normalize(self, output: Path, receipt: Path, mapping: Path = MAPPING) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3", str(NORMALIZER), "--workspace-root", str(ROOT),
                "--canonical", str(CANONICAL), "--common-core", str(COMMON_CORE),
                "--reference-contract", str(CONTRACT), "--learning-request", str(REQUEST),
                "--normalization-map", str(mapping), "--pathway-id", "power-iteration-p0-v1",
                "--generated-at", "2026-08-18T14:00:00Z", "--output", str(output),
                "--receipt", str(receipt),
            ],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )

    def copy_p1(self, p0: Path, output: Path, receipt: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3", str(COPIER), "--workspace-root", str(ROOT),
                "--p0", str(p0), "--profile", str(PROFILE),
                "--pathway-id", "power-iteration-computer-science-p1-v1",
                "--generated-at", "2026-08-18T14:05:00Z", "--output", str(output),
                "--receipt", str(receipt),
            ],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )

    def test_p0_normalization_is_byte_deterministic_and_valid(self) -> None:
        first = self.directory / "first-p0.json"
        second = self.directory / "second-p0.json"
        result_one = self.normalize(first, self.directory / "first-receipt.json")
        result_two = self.normalize(second, self.directory / "second-receipt.json")
        self.assertEqual(result_one.returncode, 0, result_one.stdout + result_one.stderr)
        self.assertEqual(result_two.returncode, 0, result_two.stdout + result_two.stderr)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        plan = load(first)
        self.assertEqual(plan["condition"], "P0")
        self.assertEqual(plan["instruction_sequence"], ["PI-U01", "PI-U02", "PI-U03", "PI-U04", "PI-U05", "PI-U06", "PI-U07", "PI-U08"])
        report = self.directory / "p0-validation.json"
        validated = subprocess.run(
            ["python3", str(VALIDATOR), "--workspace-root", str(ROOT), "--pathway", str(first), "--output", str(report), "--phase", "pilot"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
        self.assertTrue(load(report)["valid"])

    def test_p1_copy_is_byte_deterministic_and_changes_only_control_fields(self) -> None:
        p0 = self.directory / "p0.json"
        self.assertEqual(self.normalize(p0, self.directory / "p0-receipt.json").returncode, 0)
        first = self.directory / "first-p1.json"
        second = self.directory / "second-p1.json"
        result_one = self.copy_p1(p0, first, self.directory / "first-p1-receipt.json")
        result_two = self.copy_p1(p0, second, self.directory / "second-p1-receipt.json")
        self.assertEqual(result_one.returncode, 0, result_one.stdout + result_one.stderr)
        self.assertEqual(result_two.returncode, 0, result_two.stdout + result_two.stderr)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        p0_value, p1_value = load(p0), load(first)
        changed = {
            key for key in p0_value
            if p0_value.get(key) != p1_value.get(key)
        }
        self.assertEqual(changed, {"pathway_id", "condition", "profile_binding", "baseline_pathway_binding", "generated_by"})

    def test_normalizer_rejects_stale_mapping_hash(self) -> None:
        mapping = load(MAPPING)
        mapping["bindings"]["canonical_pathway"]["sha256"] = "0" * 64
        stale = self.directory / "stale-map.json"
        stale.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")
        result = self.normalize(self.directory / "p0.json", self.directory / "receipt.json", stale)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("mapping.canonical_pathway.hash", result.stdout)

    def test_p1_copier_rejects_non_p0_input(self) -> None:
        invalid = self.directory / "not-p0.json"
        invalid.write_text('{"condition":"P2"}\n', encoding="utf-8")
        result = self.copy_p1(invalid, self.directory / "p1.json", self.directory / "receipt.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("P0.condition", result.stdout)

    def test_generators_refuse_overwrite(self) -> None:
        p0 = self.directory / "p0.json"
        receipt = self.directory / "receipt.json"
        self.assertEqual(self.normalize(p0, receipt).returncode, 0)
        result = self.normalize(p0, self.directory / "other-receipt.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("output.exists", result.stdout)


if __name__ == "__main__":
    unittest.main()
