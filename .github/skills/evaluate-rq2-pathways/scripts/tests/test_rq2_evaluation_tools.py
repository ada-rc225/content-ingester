from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
SCRIPTS = ROOT / ".github/skills/evaluate-rq2-pathways/scripts"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class RQ2EvaluationToolsTests(unittest.TestCase):
    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def make_minimal_bundle(self, base: Path) -> Path:
        bundle = base / "sample-opaque-001"
        bundle.mkdir()
        lesson = "The update is x_{k+1}=Ax_k/||Ax_k|| and it requires Ax_k to be non-zero."
        (bundle / "lesson.md").write_text(lesson, encoding="utf-8")
        write_json(bundle / "learner-profile.json", {
            "profile_id": "learner-a",
            "discipline": "mathematics",
            "education_level": "undergraduate",
            "prior_knowledge": ["linear algebra"],
        })
        write_json(bundle / "learning-request.json", {
            "schema_version": "1.0",
            "request_id": "req-1",
            "target_capabilities": [{"capability_id": "LG-001", "priority": "required", "description": "Trace the update."}],
        })
        write_json(bundle / "frozen-reference-contract.json", {
            "schema_version": "1.0",
            "lifecycle_status": "frozen",
            "contract_items": [{
                "item_id": "RC-001",
                "item_type": "algorithm_rule",
                "canonical_statement": "Normalize a non-zero matrix-vector product.",
                "conditions": ["Ax_k is non-zero."],
                "formula_refs": ["FM-001"],
            }],
        })
        write_json(bundle / "pathway-evidence.json", {
            "schema_version": "1.0",
            "topic": "iteration",
            "selected_item_ids": ["RC-001"],
            "excluded_item_ids": [],
            "selection_decisions": [{"item_id": "RC-001", "decision": "include", "rationale": "Required by the learner goal.", "profile_basis": [{"profile_field": "prior_knowledge", "evidence": "linear algebra"}]}],
            "learning_goal_mappings": [{"capability_id": "LG-001", "supporting_item_ids": ["RC-001"], "coverage": "complete"}],
            "learning_units": [{"unit_id": "U-001", "unit_type": "contract_content", "purpose": "Trace update", "contract_item_ids": ["RC-001"], "bridge_contract_id": None, "prerequisite_unit_ids": [], "learning_goal_ids": ["LG-001"]}],
            "instruction_sequence": ["U-001"],
            "bridge_requirements": [],
            "released_bridges": [],
            "pathway_changes": [],
            "scope_summary": {"selected_contract_item_count": 1},
        })
        write_json(bundle / "structural-validation-evidence.json", {
            "schema_version": "1.0",
            "pathway_valid": True,
            "lesson_output_valid": True,
            "pathway_metrics": {},
            "lesson_metrics": {"released_bridge_count": 0, "mapped_bridge_count": 0, "english_prose_word_count": 12},
            "validation_scope": {"semantic_mathematical_correctness_assessed": False, "pedagogical_quality_assessed": False},
        })
        files = {}
        for name in (
            "lesson.md", "learner-profile.json", "learning-request.json",
            "frozen-reference-contract.json", "pathway-evidence.json", "structural-validation-evidence.json",
        ):
            files[name] = {"sha256": sha(bundle / name)}
        write_json(bundle / "evaluation-manifest.json", {
            "schema_version": "1.0",
            "protocol_id": "RQ2-EVAL-v1",
            "sample_id": "SAMPLE-001",
            "created_at": "2026-08-19T12:00:00Z",
            "files": files,
            "independence_policy": {"condition_hidden": True, "profile_visible_for_fit_judgement": True, "single_sample_pointwise_evaluation": True, "other_samples_excluded": True},
            "authority_checks": {"frozen_contract_release_verified": True, "pathway_validation_verified": True, "lesson_output_validation_verified": True},
        })
        return bundle

    def complete_template(self, path: Path, score: int = 5) -> None:
        value = json.loads(path.read_text(encoding="utf-8"))
        excerpt = "The update is x_{k+1}=Ax_k/||Ax_k|| and it requires Ax_k to be non-zero."
        for entry in value["primary_pedagogy_judgements"] + value["exploratory_judgements"]:
            entry.update(score=score, evidence_excerpts=[excerpt], rationale="The exact lesson evidence supports this resolved rating.", confidence="high", abstain=False)
        for entry in value["learning_goal_judgements"]:
            entry.update(coverage="complete", evidence_excerpts=[excerpt], rationale="The requested capability is explicitly taught.", confidence="high", abstain=False)
        for name in ("inclusion_appropriateness", "profile_rationale_quality"):
            value["selection_quality"][name].update(score=score, evidence_excerpts=[excerpt], rationale="The selected content is justified and useful.", confidence="high", abstain=False)
        value["selection_quality"]["unnecessary_content_load"].update(level="none", evidence_excerpts=[], rationale="No unnecessary content is present.", confidence="high", abstain=False)
        for entry in value["selected_item_judgements"]:
            entry.update(coverage="full", semantic_correctness="correct", provenance="supported", evidence_excerpts=[excerpt], rationale="The selected obligation and condition are correct.", confidence="high", abstain=False)
        for entry in value["formula_judgements"]:
            entry.update(occurrence_status="present", provenance="supported", accuracy="correct", severity="none", evidence_excerpts=[excerpt], rationale="The formula is present, mapped, and correct.", confidence="high", abstain=False)
        for entry in value["algorithm_judgements"]:
            entry.update(accuracy="correct", severity="none", evidence_excerpts=[excerpt], rationale="The algorithmic update preserves its required condition.", confidence="high", abstain=False)
        value["dependency_coherence"].update(verdict="pass", evidence_excerpts=[], rationale="The only unit has no unmet prerequisite.", confidence="high", abstain=False)
        value["overall_recommendation"] = {"decision": "pass", "rationale": "All resolved pedagogy judgements and safety checks pass."}
        write_json(path, value)

    def test_minimal_bundle_template_and_score(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            bundle = self.make_minimal_bundle(base)
            result = self.run_script("validate_blind_sample.py", "--bundle", str(bundle))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            judgement = base / "judgement.json"
            result = self.run_script(
                "create_judgement_template.py", "--bundle", str(bundle), "--output", str(judgement),
                "--evaluator-id", "judge-a", "--provider", "test", "--model", "test-model",
                "--access-route", "test", "--pass-index", "1", "--evaluated-at", "2026-08-19T12:00:00Z",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.complete_template(judgement)
            score = base / "score.json"
            result = self.run_script("validate_and_score.py", "--bundle", str(bundle), "--judgement", str(judgement), "--output", str(score))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(score.read_text(encoding="utf-8"))
            self.assertTrue(report["selected_content_safety"]["gate_pass"])
            self.assertEqual(report["primary_pedagogy_scores"]["sequence_quality"], 5)

    def test_reliability_report(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            bundle = self.make_minimal_bundle(base)
            judgements = []
            for pass_index, score in ((1, 5), (2, 4)):
                path = base / f"judgement-{pass_index}.json"
                result = self.run_script(
                    "create_judgement_template.py", "--bundle", str(bundle), "--output", str(path),
                    "--evaluator-id", f"judge-{pass_index}", "--provider", "test", "--model", "test-model",
                    "--access-route", "test", "--pass-index", str(pass_index), "--evaluated-at", "2026-08-19T12:00:00Z",
                )
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.complete_template(path, score)
                judgements.append(path)
            output = base / "reliability.json"
            args = [item for path in judgements for item in ("--judgement", str(path))]
            result = self.run_script("assess_judge_reliability.py", *args, "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(report["dimensions"]["sequence_quality"]["mean_absolute_difference"], 1)

    def test_prepare_current_pilot_sample(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            bundle = base / "opaque-sample"
            mapping = base / "controller-mapping.json"
            result = self.run_script(
                "prepare_blind_sample.py",
                "--workspace-root", str(ROOT),
                "--lesson-run", "experiments/rq2/lesson-runs/power-iteration-v1/pilot/p2/applied-mathematics/run-01",
                "--profile", "experiments/rq2/profiles/applied-mathematics-year-2.json",
                "--sample-id", "PI-AM-OPAQUE-001",
                "--bundle-dir", str(bundle),
                "--mapping-output", str(mapping),
                "--generated-at", "2026-08-19T12:00:00Z",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            result = self.run_script("validate_blind_sample.py", "--bundle", str(bundle))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            pathway_text = (bundle / "pathway-evidence.json").read_text(encoding="utf-8")
            self.assertNotIn('"condition":', pathway_text)
            self.assertEqual(json.loads(mapping.read_text(encoding="utf-8"))["condition"], "P2")

    def test_pathway_difference_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            left = base / "left.json"
            right = base / "right.json"
            common = {
                "selection": {"selected_item_ids": ["A", "B"]},
                "learning_units": [
                    {"unit_id": "U1", "contract_item_ids": ["A"], "bridge_contract_id": None},
                    {"unit_id": "U2", "contract_item_ids": ["B"], "bridge_contract_id": None},
                ],
                "instruction_sequence": ["U1", "U2"],
                "pathway_changes": [{"change_type": "reorder_learning_units", "affected_ids": ["A", "B"], "profile_basis": [{"x": "y"}], "rationale": "profile reason"}],
            }
            write_json(left, common)
            changed = json.loads(json.dumps(common))
            changed["instruction_sequence"] = ["U2", "U1"]
            write_json(right, changed)
            output = base / "differences.json"
            result = self.run_script("compute_pathway_differences.py", "--pathway", f"a={left}", "--pathway", f"b={right}", "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            pair = json.loads(output.read_text(encoding="utf-8"))["pairs"][0]
            self.assertGreater(pair["normalized_item_sequence_edit_distance"], 0)
            self.assertTrue(pair["material_difference_candidate"])

    def test_condition_aggregation_uses_matched_samples(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            score_paths = []
            mapping_paths = []
            for condition, score in (("P0", 2), ("P1", 3), ("P2", 5)):
                sample_id = f"S-{condition}"
                score_path = base / f"score-{condition}.json"
                mapping_path = base / f"mapping-{condition}.json"
                write_json(score_path, {
                    "schema_version": "1.0",
                    "protocol_id": "RQ2-EVAL-v1",
                    "sample_id": sample_id,
                    "valid": True,
                    "evaluator": {"evaluator_id": "judge-a", "pass_index": 1},
                    "primary_pedagogy_scores": {dimension: score for dimension in ("disciplinary_framing_appropriateness", "prerequisite_match", "context_boundary_awareness", "sequence_quality")},
                    "selected_content_safety": {"gate_pass": True},
                })
                write_json(mapping_path, {
                    "schema_version": "1.0",
                    "protocol_id": "RQ2-EVAL-v1",
                    "sample_id": sample_id,
                    "condition": condition,
                    "topic": "topic-a",
                    "profile_id": "profile-a",
                    "run_id": f"topic-{condition.lower()}-run-01",
                })
                score_paths.append(score_path)
                mapping_paths.append(mapping_path)
            output = base / "aggregate.json"
            arguments = [item for path in score_paths for item in ("--score-report", str(path))]
            arguments += [item for path in mapping_paths for item in ("--mapping", str(path))]
            result = self.run_script("aggregate_rq2_scores.py", *arguments, "--output", str(output))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text(encoding="utf-8"))
            framing = report["paired_contrasts"]["P2-P1"]["disciplinary_framing_appropriateness"]
            self.assertEqual(framing["matched_pair_count"], 1)
            self.assertEqual(framing["probability_of_superiority"], 1.0)
            self.assertEqual(framing["median_paired_difference"], 2)


if __name__ == "__main__":
    unittest.main()
