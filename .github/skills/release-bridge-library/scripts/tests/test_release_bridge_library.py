from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[5]
SCRIPT = ROOT / ".github/skills/release-bridge-library/scripts/release_bridge_library.py"
CANDIDATE_DIR = ROOT / "bridge-library/power-iteration-v1/candidate-v3"
CANDIDATE = CANDIDATE_DIR / "bridge-library-candidate.json"
VALIDATION = CANDIDATE_DIR / "bridge-library-validation-report.json"
REVIEW = CANDIDATE_DIR / "bridge-library-review.json"
FIXED_TIME = "2026-08-18T18:00:00Z"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class BridgeLibraryReleaseTests(unittest.TestCase):
    def run_gate(self, output: Path, review: Path = REVIEW) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--workspace-root", str(ROOT),
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
        value = json.loads(REVIEW.read_text(encoding="utf-8"))
        change(value)
        path = directory / "review.json"
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        return path

    def test_releases_approved_candidate_without_content_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "release"
            result = self.run_gate(output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(
                {path.name for path in output.iterdir()},
                {
                    "released-bridge-catalog.json",
                    "frozen-bridge-library-review.json",
                    "frozen-bridge-library-validation-report.json",
                    "released-bridge-catalog.sha256",
                    "bridge-library-release-report.json",
                },
            )
            candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
            catalog_path = output / "released-bridge-catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            self.assertEqual(catalog["status"], "released")
            self.assertTrue(all(item["status"] == "released" for item in catalog["bridges"]))
            expected = json.loads(json.dumps(candidate))
            expected["status"] = "released"
            for item in expected["bridges"]:
                item["status"] = "released"
            expected["approval"] = catalog["approval"]
            self.assertEqual(catalog, expected)
            checksum = (output / "released-bridge-catalog.sha256").read_text(encoding="utf-8").split()[0]
            self.assertEqual(checksum, digest(catalog_path))
            validation = json.loads((output / "frozen-bridge-library-validation-report.json").read_text(encoding="utf-8"))
            self.assertTrue(validation["valid"])
            self.assertEqual(validation["error_count"], 0)
            release = json.loads((output / "bridge-library-release-report.json").read_text(encoding="utf-8"))
            self.assertEqual(release["status"], "released")

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
            review = self.changed_review(directory, lambda value: value["candidate_binding"].__setitem__("candidate_sha256", "0" * 64))
            output = directory / "release"
            result = self.run_gate(output, review)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review.candidate_hash", result.stdout)
            self.assertFalse(output.exists())

    def test_rejects_incomplete_bridge_review(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            def change(value: dict) -> None:
                value["bridge_reviews"][0]["field_decisions"]["source_quality"] = "pending"
            review = self.changed_review(directory, change)
            output = directory / "release"
            result = self.run_gate(output, review)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("review.field_decision", result.stdout)
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
