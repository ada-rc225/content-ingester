from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[5]
SKILL = ROOT / ".github/skills/compose-pathway-constrained-teaching"
PREPARE = SKILL / "scripts/prepare_composition_inputs.py"
VALIDATE = SKILL / "scripts/validate_composer_outputs.py"
EXECUTE = ROOT / ".github/skills/discipline-aware-teaching-adaptation/scripts/execute_code_blocks.py"
WORD_PROTOCOL = ROOT / "experiments/rq2/word-count-protocols/power-iteration-pilot.json"
P0 = ROOT / "experiments/rq2/pathway-plans/power-iteration-v1/p0"
P1 = ROOT / "experiments/rq2/pathway-plans/power-iteration-v1/p1/applied-mathematics"
P2 = ROOT / "experiments/rq2/pathway-plans/power-iteration-v1/p2/applied-mathematics/run-04"
BRIDGES = ROOT / "bridge-library/power-iteration-v1/release/released-bridge-catalog.json"
FIXED_TIME = "2026-08-18T23:55:00Z"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True, check=False
    )


class ComposerTests(unittest.TestCase):
    def prepare(self, output: Path, condition: str) -> subprocess.CompletedProcess[str]:
        source = {"P0": P0, "P1": P1, "P2": P2}[condition]
        command = [
            str(PREPARE),
            "--workspace-root", str(ROOT),
            "--pathway", str(source / "pathway-plan.json"),
            "--pathway-validation-report", str(source / "pathway-validation-report.json"),
            "--word-count-protocol", str(WORD_PROTOCOL),
            "--run-id", f"power-iteration-{condition.lower()}-test-run-01",
            "--prepared-at", FIXED_TIME,
            "--output-dir", str(output),
        ]
        if condition == "P2":
            command.extend(["--bridge-catalog", str(BRIDGES)])
        return run(*command)

    def write_valid_lesson(self, output: Path) -> None:
        view = json.loads((output / "composition-input-view.json").read_text(encoding="utf-8"))
        units = view["pathway"]["ordered_learning_units"]
        sections = []
        lesson_parts = ["# Power Iteration"]
        for index, unit in enumerate(units, start=1):
            section_id = f"SEC-{index:02d}"
            heading = f"Learning stage {index}"
            bridge_ids = (
                [unit["bridge_contract_id"]]
                if unit["unit_type"] == "prerequisite_bridge"
                else []
            )
            sections.append({
                "section_id": section_id,
                "heading": heading,
                "unit_ids": [unit["unit_id"]],
                "contract_item_ids": unit["contract_item_ids"],
                "bridge_contract_ids": bridge_ids,
            })
            lesson_parts.extend([
                f"<!-- section: {section_id} -->",
                f"## {heading}",
                "This section develops the assigned mathematical idea in pathway order.",
            ])
        lesson_parts.append(" ".join(["explanation"] * 1500))
        (output / "lesson.md").write_text("\n\n".join(lesson_parts) + "\n", encoding="utf-8")
        (output / "lesson-map.json").write_text(
            json.dumps({
                "schema_version": "1.0",
                "run_id": view["run_id"],
                "lesson_file": "lesson.md",
                "sections": sections,
            }, indent=2) + "\n",
            encoding="utf-8",
        )
        executed = run(
            str(EXECUTE), "--content", str(output / "lesson.md"),
            "--output", str(output / "code-validation.json"),
        )
        self.assertEqual(executed.returncode, 0, executed.stdout + executed.stderr)

    def finalize(self, output: Path) -> subprocess.CompletedProcess[str]:
        return run(
            str(VALIDATE),
            "--workspace-root", str(ROOT),
            "--run-dir", str(output),
            "--provider", "test-provider",
            "--model", "test-model",
            "--access-route", "test-route",
            "--prompt-version", "composer-v1",
            "--generated-at", FIXED_TIME,
        )

    def test_valid_p0_run_has_no_profile_and_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            prepared = self.prepare(output, "P0")
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            view = json.loads((output / "composition-input-view.json").read_text(encoding="utf-8"))
            self.assertIsNone(view["learner_profile"])
            self.assertTrue(view["composition_policy"]["discipline_neutral_required"])
            self.write_valid_lesson(output)
            result = self.finalize(output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads((output / "lesson-validation-report.json").read_text(encoding="utf-8"))
            self.assertTrue(report["valid"])
            self.assertFalse(report["validation_scope"]["semantic_mathematical_correctness_assessed"])

    def test_p1_exposes_exactly_bound_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            prepared = self.prepare(output, "P1")
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            view = json.loads((output / "composition-input-view.json").read_text(encoding="utf-8"))
            self.assertEqual(view["learner_profile"]["profile_id"], "applied-mathematics-year-2-rq2-pilot")
            self.assertEqual(view["released_bridge_contracts"], [])

    def test_p2_exposes_only_pathway_released_bridge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            prepared = self.prepare(output, "P2")
            self.assertEqual(prepared.returncode, 0, prepared.stdout + prepared.stderr)
            view = json.loads((output / "composition-input-view.json").read_text(encoding="utf-8"))
            self.assertEqual(
                [item["bridge_contract_id"] for item in view["released_bridge_contracts"]],
                ["BRC-NUMPY-VECTOR-OPERATIONS-v1"],
            )
            self.assertEqual(len(view["selected_contract_items"]), 18)

    def test_validator_rejects_reordered_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            self.assertEqual(self.prepare(output, "P0").returncode, 0)
            self.write_valid_lesson(output)
            lesson_map = json.loads((output / "lesson-map.json").read_text(encoding="utf-8"))
            lesson_map["sections"][0], lesson_map["sections"][1] = lesson_map["sections"][1], lesson_map["sections"][0]
            (output / "lesson-map.json").write_text(json.dumps(lesson_map, indent=2) + "\n", encoding="utf-8")
            result = self.finalize(output)
            self.assertNotEqual(result.returncode, 0)
            report = json.loads((output / "lesson-validation-report.json").read_text(encoding="utf-8"))
            codes = {item["code"] for item in report["errors"]}
            self.assertIn("map.sequence", codes)

    def test_p0_rejects_bridge_catalog_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run"
            result = run(
                str(PREPARE),
                "--workspace-root", str(ROOT),
                "--pathway", str(P0 / "pathway-plan.json"),
                "--pathway-validation-report", str(P0 / "pathway-validation-report.json"),
                "--bridge-catalog", str(BRIDGES),
                "--word-count-protocol", str(WORD_PROTOCOL),
                "--run-id", "power-iteration-p0-test-run-01",
                "--prepared-at", FIXED_TIME,
                "--output-dir", str(output),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("P0.bridge_catalog", result.stdout)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
