from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[5]
SCRIPT = ROOT / ".github/skills/materialize-released-bridges/scripts/materialize_released_bridges.py"
VALIDATOR = ROOT / "experiments/rq2/scripts/validate_pathway_plan.py"
CATALOG_DIR = ROOT / "bridge-library/power-iteration-v1/release"
CATALOG = CATALOG_DIR / "released-bridge-catalog.json"
RELEASE_REPORT = CATALOG_DIR / "bridge-library-release-report.json"
FIXED_TIME = "2026-08-18T22:00:00Z"


PARENTS = {
    "applied": ROOT / "experiments/rq2/pathway-plans/power-iteration-v1/p2/applied-mathematics/run-03",
    "computer": ROOT / "experiments/rq2/pathway-plans/power-iteration-v1/p2/computer-science/run-02",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ReleasedBridgeMaterializerTests(unittest.TestCase):
    def run_materializer(
        self,
        parent: Path,
        output: Path,
        pathway_id: str,
        review: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--workspace-root", str(ROOT),
                "--parent-pathway", str(parent / "pathway-plan.json"),
                "--parent-review", str(review or parent / "pathway-plan-review.json"),
                "--bridge-catalog", str(CATALOG),
                "--bridge-release-report", str(RELEASE_REPORT),
                "--pathway-id", pathway_id,
                "--generated-at", FIXED_TIME,
                "--output-dir", str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def validate(self, output: Path) -> dict:
        report = output / "pathway-validation-report.json"
        result = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--workspace-root", str(ROOT),
                "--pathway", str(output / "pathway-plan.json"),
                "--bridge-catalog", str(CATALOG),
                "--output", str(report),
                "--phase", "pilot",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(report.read_text(encoding="utf-8"))

    def test_materializes_one_bridge_and_records_catalog_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run-04"
            parent_dir = PARENTS["applied"]
            parent = json.loads((parent_dir / "pathway-plan.json").read_text(encoding="utf-8"))
            result = self.run_materializer(parent_dir, output, "power-iteration-p2-applied-mathematics-bridge-resolved-v1")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            plan_path = output / "pathway-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            self.assertEqual(plan["plan_status"], "complete")
            self.assertEqual(plan["scope_summary"]["released_bridge_count"], 1)
            bridge_units = [item for item in plan["learning_units"] if item["unit_type"] == "prerequisite_bridge"]
            self.assertEqual(len(bridge_units), 1)
            self.assertEqual(bridge_units[0]["bridge_contract_id"], "BRC-NUMPY-VECTOR-OPERATIONS-v1")
            self.assertLess(plan["instruction_sequence"].index("BRIDGE-001"), plan["instruction_sequence"].index("P2-AM-U11"))
            existing = [item for item in plan["instruction_sequence"] if not item.startswith("BRIDGE-")]
            self.assertEqual(existing, parent["instruction_sequence"])
            receipt = json.loads((output / "bridge-resolution-receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["output_pathway"]["sha256"], digest(plan_path))
            validation = self.validate(output)
            self.assertTrue(validation["valid"])
            self.assertEqual(validation["bridge_catalog"]["file"], "bridge-library/power-iteration-v1/release/released-bridge-catalog.json")
            self.assertEqual(validation["bridge_catalog"]["sha256"], digest(CATALOG))

    def test_materializes_three_bridges_without_reordering_parent_units(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "run-03"
            parent_dir = PARENTS["computer"]
            parent = json.loads((parent_dir / "pathway-plan.json").read_text(encoding="utf-8"))
            result = self.run_materializer(parent_dir, output, "power-iteration-p2-computer-science-bridge-resolved-v1")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            plan = json.loads((output / "pathway-plan.json").read_text(encoding="utf-8"))
            bridge_units = [item for item in plan["learning_units"] if item["unit_type"] == "prerequisite_bridge"]
            self.assertEqual(len(bridge_units), 3)
            self.assertEqual(plan["scope_summary"]["released_bridge_count"], 3)
            self.assertTrue(all(item["resolution_status"] == "released" for item in plan["bridge_requirements"]))
            existing = [item for item in plan["instruction_sequence"] if not item.startswith("BRIDGE-")]
            self.assertEqual(existing, parent["instruction_sequence"])
            self.assertTrue(self.validate(output)["valid"])

    def test_rejects_review_not_bound_by_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            parent_dir = PARENTS["applied"]
            review = json.loads((parent_dir / "pathway-plan-review.json").read_text(encoding="utf-8"))
            changed_review = directory / "review.json"
            changed_review.write_text(json.dumps(review, indent=2) + "\n", encoding="utf-8")
            output = directory / "output"
            result = self.run_materializer(parent_dir, output, "power-iteration-p2-applied-mathematics-bridge-resolved-v1", changed_review)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("catalog.review_path", result.stdout)
            self.assertFalse(output.exists())

    def test_refuses_existing_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "output"
            output.mkdir()
            sentinel = output / "keep.txt"
            sentinel.write_text("keep", encoding="utf-8")
            result = self.run_materializer(PARENTS["applied"], output, "power-iteration-p2-applied-mathematics-bridge-resolved-v1")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("output.exists", result.stdout)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
