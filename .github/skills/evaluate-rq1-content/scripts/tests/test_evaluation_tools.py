from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class EvaluationToolsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.contract = self.root / "frozen.json"
        write_json(self.contract, {
            "contract_id": "test-topic",
            "contract_version": "1.0.0",
            "lifecycle_status": "frozen",
            "approval": {"reviewer_id": "test"},
            "contract_items": [
                {
                    "item_id": "RC-001", "item_type": "definition", "criticality": "critical",
                    "generation_requirement": "required", "required_for_generation": True,
                    "canonical_statement": "A definition.", "formula_refs": [],
                    "conditions": ["Condition A."], "prohibited_drift": ["Do not reverse A."],
                },
                {
                    "item_id": "RC-002", "item_type": "algorithm_rule", "criticality": "supporting",
                    "generation_requirement": "conditional", "required_for_generation": False,
                    "canonical_statement": "An optional rule.", "formula_refs": ["FM-001"],
                    "conditions": [], "prohibited_drift": [],
                },
            ],
            "candidate_source_issues": [],
        })
        self.profile = self.root / "profile.json"
        write_json(self.profile, {"profile_id": "test-learners"})
        self.task = self.root / "task.txt"
        self.task.write_text("Teach the common topic.\n", encoding="utf-8")
        self.samples = []
        for index, condition in enumerate(("c0-ungrounded", "c1-source-conditioned", "c2-structured-grounding"), 1):
            path = self.root / f"{condition}.md"
            path.write_text(f"<!-- section: SEC-0{index} -->\n# Anonymous lesson\n\nA definition.\n", encoding="utf-8")
            self.samples.append((condition, f"run-{index:02d}", path))
        self.bundle = self.root / "blind"
        self.mapping = self.root / "secret" / "mapping.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_script(self, script: str, *args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, expect, result.stdout + result.stderr)
        return result

    def build_bundle(self) -> None:
        arguments = [
            "--bundle-id", "test-bundle", "--contract", str(self.contract),
            "--learner-profile", str(self.profile), "--task-brief", str(self.task),
            "--output-dir", str(self.bundle), "--mapping-output", str(self.mapping), "--seed", "7",
        ]
        for condition, run_id, path in self.samples:
            arguments.extend(["--sample", f"{condition}::{run_id}={path}"])
        self.run_script("build_blind_bundle.py", *arguments)

    def test_builds_and_validates_condition_blind_bundle(self) -> None:
        self.build_bundle()
        self.run_script("validate_blind_bundle.py", "--bundle", str(self.bundle))
        manifest_text = (self.bundle / "evaluation_manifest.json").read_text(encoding="utf-8")
        self.assertNotIn("c0-ungrounded", manifest_text)
        self.assertNotIn("structured-grounding", manifest_text)
        for sample in (self.bundle / "samples").glob("*.md"):
            self.assertNotIn("<!--", sample.read_text(encoding="utf-8"))

    def test_validates_and_scores_judgement(self) -> None:
        self.build_bundle()
        manifest_path = self.bundle / "evaluation_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        sample = manifest["samples"][0]
        import hashlib
        sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        judgement = {
            "schema_version": "1.0", "evaluation_protocol": "RQ1-EVAL-v1",
            "evaluator": {
                "evaluator_run_id": "judge-pass-1", "evaluator_id": "judge-a", "provider": "test",
                "model": "test-model", "prompt_version": "RQ1-EVAL-v1", "pass_index": 1,
                "generated_at": "2026-08-15T12:00:00+00:00",
            },
            "bundle_binding": {
                "bundle_id": manifest["bundle_id"], "manifest_sha256": sha(manifest_path),
                "contract_id": "test-topic", "contract_version": "1.0.0",
                "contract_sha256": sha(self.bundle / "frozen_reference_contract.json"),
                "sample_id": sample["sample_id"], "content_sha256": sample["content_sha256"],
            },
            "item_evaluations": [
                {
                    "item_id": "RC-001", "applicability": "applicable", "selection_basis": "required",
                    "coverage": "full", "severity": "none", "drift_types": [],
                    "lesson_evidence": [{"heading": "Anonymous lesson", "exact_excerpt": "A definition."}],
                    "condition_checks": [{"condition": "Condition A.", "status": "preserved", "lesson_evidence": [{"heading": "Anonymous lesson", "exact_excerpt": "A definition."}], "rationale": "The bounded test fixture represents this condition as preserved."}],
                    "contract_requirement_checked": "A definition.", "rationale": "The item is present.",
                    "confidence": 0.9, "abstain": False,
                },
                {
                    "item_id": "RC-002", "applicability": "not_applicable", "selection_basis": "conditional_not_selected",
                    "coverage": "not_applicable", "severity": "not_applicable", "drift_types": [],
                    "lesson_evidence": [], "condition_checks": [], "contract_requirement_checked": "An optional rule.",
                    "rationale": "The optional method is not selected.", "confidence": 0.9, "abstain": False,
                },
            ],
            "atomic_claim_evaluations": [{
                "claim_id": "AC-001", "heading": "Anonymous lesson", "exact_claim": "A definition.",
                "claim_type": "mathematical", "verdict": "supported", "supporting_item_ids": ["RC-001"],
                "lesson_evidence": [{"heading": "Anonymous lesson", "exact_excerpt": "A definition."}],
                "severity": "none", "rationale": "Matches RC-001.", "confidence": 0.9, "abstain": False,
            }],
            "pedagogy_evaluations": [
                {"dimension": dimension, "score": 3, "lesson_evidence": [{"heading": "Anonymous lesson", "exact_excerpt": "A definition."}], "rationale": "Adequate fixture.", "confidence": 0.7, "abstain": False}
                for dimension in ("learner_alignment", "disciplinary_authenticity", "pedagogical_coherence", "theory_implementation_alignment", "readability", "analogy_safety", "exercise_validity")
            ],
            "limitations": ["Synthetic test fixture."],
        }
        judgement_path = self.root / "judgement.json"
        report_path = self.root / "score.json"
        write_json(judgement_path, judgement)
        self.run_script("validate_and_score.py", "--bundle", str(self.bundle), "--judgement", str(judgement_path), "--output", str(report_path))
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["primary_outcome"]["major_critical_error_rate"], 0.0)
        self.assertEqual(report["fidelity_outcomes"]["required_item_strict_coverage"], 1.0)
        self.assertEqual(report["fidelity_outcomes"]["unsupported_claim_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
