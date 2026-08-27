from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
SKILL = ROOT / ".github" / "skills" / "discipline-aware-teaching-adaptation"
PREPARE = SKILL / "scripts" / "prepare_frozen_grounding.py"
VALIDATE = SKILL / "scripts" / "validate_adapter_outputs.py"
EXECUTE_CODE = SKILL / "scripts" / "execute_code_blocks.py"
VALIDATE_EXERCISES = SKILL / "scripts" / "validate_exercises.py"
RELEASED_CONTRACT = ROOT / "experiments" / "rq1" / "reference-contracts" / "gradient-descent-v5" / "release" / "frozen_reference_contract.json"
LEGACY_CONTRACT = RELEASED_CONTRACT.parent.parent / "frozen_reference_contract.json"


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@unittest.skipUnless(RELEASED_CONTRACT.is_file(), "released gradient-descent v5 fixture is unavailable")
class FrozenGroundingTests(unittest.TestCase):
    def prepare(self, run_dir: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(PREPARE),
                "--workspace-root",
                str(ROOT),
                "--contract",
                str(RELEASED_CONTRACT),
                "--output",
                str(run_dir / "grounding_receipt.json"),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_preflight_accepts_only_complete_release(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            run_dir = Path(raw_temp)
            completed = self.prepare(run_dir)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((run_dir / "grounding_receipt.json").is_file())
            self.assertTrue((run_dir / "grounding_view.json").is_file())

            rejected = subprocess.run(
                [
                    sys.executable,
                    str(PREPARE),
                    "--workspace-root",
                    str(ROOT),
                    "--contract",
                    str(LEGACY_CONTRACT),
                    "--output",
                    str(run_dir / "legacy_receipt.json"),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("missing release gate report", rejected.stderr)

    def test_v36_validator_links_length_derivation_calculation_and_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as raw_temp:
            run_dir = Path(raw_temp)
            completed = self.prepare(run_dir)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            receipt = json.loads((run_dir / "grounding_receipt.json").read_text(encoding="utf-8"))
            view = json.loads((run_dir / "grounding_view.json").read_text(encoding="utf-8"))
            required_ids = receipt["generation_items"]["required_item_ids"]
            conditional_ids = receipt["generation_items"]["conditional_item_ids"]
            source_ids = [item["source_id"] for item in receipt["source_materials"]]
            identity = {
                "contract_id": view["contract"]["contract_id"],
                "contract_version": view["contract"]["contract_version"],
                "sha256": view["contract"]["sha256"],
            }
            sections = [
                {"section_id": "SEC-01", "order": 1, "title": "Foundations", "purpose": "Introduce the approved mathematical foundations.", "contract_item_ids": required_ids[:5]},
                {"section_id": "SEC-02", "order": 2, "title": "Algorithm", "purpose": "Connect the approved definitions to the algorithm.", "contract_item_ids": required_ids[5:9]},
                {"section_id": "SEC-03", "order": 3, "title": "Convergence", "purpose": "Explain the approved convergence results.", "contract_item_ids": required_ids[9:]},
            ]
            write_json(
                run_dir / "run_manifest.json",
                {
                    "research_question": "RQ1",
                    "condition": "c2-structured-grounding",
                    "run_id": "test-run",
                    "topic": view["contract"]["topic"],
                    "profile_id": "mechanical-engineering-year-2",
                    "provider": "test-provider",
                    "model": "test-model",
                    "access_route": "unit-test",
                    "prompt_version": "3.6",
                    "agent_version": "3.6",
                    "skill_version": "3.6",
                    "run_date": datetime.now(timezone.utc).isoformat(),
                    "source_ids": source_ids,
                    "grounding_receipt_file": "grounding_receipt.json",
                    "grounding_receipt_sha256": file_hash(run_dir / "grounding_receipt.json"),
                    "code_execution_required": True,
                    "word_count_protocol": {
                        "enabled": True,
                        "minimum": 20,
                        "maximum": 200,
                        "counting_method": "english_prose_v1",
                    },
                    "exercise_protocol": {
                        "enabled": True,
                        "expected_count": 3,
                        "required_types": ["concept_check", "hand_calculation", "code_diagnostic"],
                        "worked_solutions_required": True,
                    },
                },
            )
            write_json(
                run_dir / "learner_profile.json",
                {
                    "profile_id": "mechanical-engineering-year-2",
                    "discipline": "mechanical engineering",
                    "education_level": "second-year undergraduate",
                    "prior_knowledge": ["calculus", "vectors"],
                    "computational_background": ["basic Python"],
                    "learning_goals": ["connect optimisation theory and implementation"],
                    "preferred_contexts": ["potential energy"],
                    "target_depth": "intermediate",
                    "proof_depth": "guided",
                    "assumptions_requiring_review": [],
                },
            )
            write_json(
                run_dir / "adaptation_plan.json",
                {
                    "topic": view["contract"]["topic"],
                    "profile_id": "mechanical-engineering-year-2",
                    "source_ids": source_ids,
                    "grounding_contract": identity,
                    "entry_point": {
                        "discipline_context": "Potential energy and equilibrium.",
                        "rationale": "Use a familiar mechanical model.",
                        "analogy_boundary": "The mapping does not replace the canonical optimisation assumptions.",
                    },
                    "required_contract_item_ids": required_ids,
                    "conditional_item_decisions": [
                        {"item_id": item_id, "included": False, "rationale": "Outside this compact test lesson scope."}
                        for item_id in conditional_ids
                    ],
                    "chapter_sequence": sections,
                    "exercise_section_id": "SEC-03",
                    "implementation_strategy": "Use only approved algorithm semantics.",
                    "assessment_strategy": "Check definitions and update interpretation.",
                    "exercise_plan": [
                        {
                            "exercise_id": "EX-001",
                            "order": 1,
                            "section_id": "SEC-03",
                            "exercise_type": "concept_check",
                            "difficulty": "introductory",
                            "learning_objective": "Distinguish stationarity from sufficient optimality.",
                            "contract_item_ids": [required_ids[1]],
                            "discipline_context": "Mechanical equilibrium",
                            "solution_required": True,
                            "verification": {"method": "contract_binding", "python_expression": None, "expected_value": None, "absolute_tolerance": 0, "consistency_checks": []},
                        },
                        {
                            "exercise_id": "EX-002",
                            "order": 2,
                            "section_id": "SEC-03",
                            "exercise_type": "hand_calculation",
                            "difficulty": "intermediate",
                            "learning_objective": "Apply one scalar gradient descent update.",
                            "contract_item_ids": [required_ids[9]],
                            "discipline_context": "Quadratic potential energy",
                            "solution_required": True,
                            "verification": {
                                "method": "deterministic_calculation",
                                "python_expression": None,
                                "expected_value": [2.6],
                                "absolute_tolerance": 1e-12,
                                "consistency_checks": [
                                    {
                                        "check_id": "CK-001",
                                        "kind": "objective_gradient_update",
                                        "objective_expression": "(x - 2.0)**2",
                                        "expressions": [],
                                        "variables": ["x"],
                                        "point": [3.0],
                                        "step_size": 0.2,
                                        "expected_gradient": [2.0],
                                        "expected_value": [2.6],
                                        "absolute_tolerance": 1e-12,
                                    }
                                ],
                            },
                        },
                        {
                            "exercise_id": "EX-003",
                            "order": 3,
                            "section_id": "SEC-03",
                            "exercise_type": "code_diagnostic",
                            "difficulty": "intermediate",
                            "learning_objective": "Connect the scalar update to executable Python.",
                            "contract_item_ids": [required_ids[9]],
                            "discipline_context": "Numerical relaxation",
                            "solution_required": True,
                            "verification": {"method": "code_execution", "python_expression": None, "expected_value": None, "absolute_tolerance": 0, "consistency_checks": []},
                        },
                    ],
                },
            )
            write_json(
                run_dir / "provenance.json",
                {
                    "profile_id": "mechanical-engineering-year-2",
                    "source_ids": source_ids,
                    "grounding_contract": identity,
                    "sections": [
                        {"section_id": item["section_id"], "contract_item_ids": item["contract_item_ids"], "adaptation_types": ["preserved"]}
                        for item in sections
                    ],
                    "exercises": [
                        {"exercise_id": "EX-001", "section_id": "SEC-03", "contract_item_ids": [required_ids[1]], "content_origin": "generated_pedagogical_material", "verification_method": "contract_binding"},
                        {"exercise_id": "EX-002", "section_id": "SEC-03", "contract_item_ids": [required_ids[9]], "content_origin": "generated_pedagogical_material", "verification_method": "deterministic_calculation"},
                        {"exercise_id": "EX-003", "section_id": "SEC-03", "contract_item_ids": [required_ids[9]], "content_origin": "generated_pedagogical_material", "verification_method": "code_execution"},
                    ],
                },
            )
            content_path = run_dir / "adapted_content.md"
            lesson = (
                "# Test lesson\n\n<!-- section: SEC-01 -->\n## Foundations\n\nText.\n\n"
                "<!-- section: SEC-02 -->\n## Algorithm\n\nText.\n\n"
                "<!-- section: SEC-03 -->\n## Convergence\n\nText.\n\n"
                "<!-- exercise: EX-001 -->\n### Exercise 1\nIs stationarity sufficient for a minimum?\n\n"
                "<!-- solution: EX-001 -->\n#### Worked solution\nNo; additional conditions are required.\n\n"
                "<!-- exercise: EX-002 -->\n### Exercise 2\nCompute one scalar update.\n\n"
                "<!-- solution: EX-002 -->\n#### Worked solution\nSubstitution gives the result below.\n\n"
                "<!-- derived-answer: EX-002 -->\n**Result from the derivation:** `[2.6]`\n\n"
                "<!-- answer: EX-002 -->\n**Checked answer:** `[2.6]`\n\n"
                "<!-- exercise: EX-003 -->\n### Exercise 3\nImplement the update.\n\n"
                "<!-- solution: EX-003 -->\n#### Worked solution\n```python\nx = 3.0\nx = x - 0.2 * (2 * x - 4.0)\nassert abs(x - 2.6) < 1e-12\nprint(x)\n```\n"
                "<!-- expected-stdout: EX-003/1 -->\n**Expected output:** `\"2.6\\n\"`\n"
            )
            content_path.write_text(lesson, encoding="utf-8")
            code_run = subprocess.run(
                [sys.executable, str(EXECUTE_CODE), "--content", str(content_path), "--output", str(run_dir / "code_validation.json")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(code_run.returncode, 0, code_run.stderr)
            exercise_run = subprocess.run(
                [sys.executable, str(VALIDATE_EXERCISES), "--content", str(content_path), "--plan", str(run_dir / "adaptation_plan.json"), "--code-validation", str(run_dir / "code_validation.json"), "--output", str(run_dir / "exercise_validation.json")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(exercise_run.returncode, 0, exercise_run.stdout + exercise_run.stderr)
            exercise_report = json.loads((run_dir / "exercise_validation.json").read_text(encoding="utf-8"))
            self.assertNotIn("manual_review_required", exercise_report)
            self.assertEqual(exercise_report["exercises"][0]["verification_method"], "contract_binding")
            self.assertEqual(exercise_report["exercises"][0]["verification_status"], "passed")

            validation = subprocess.run(
                [sys.executable, str(VALIDATE), "--workspace-root", str(ROOT), "--run-dir", str(run_dir)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertTrue((run_dir / "validation_report.json").is_file(), validation.stderr)
            report = json.loads((run_dir / "validation_report.json").read_text(encoding="utf-8"))
            self.assertEqual(validation.returncode, 0, report["errors"])
            self.assertTrue(report["treatment_valid"])
            self.assertEqual(report["validation_scope"], "grounding_and_configured_checks_only")
            self.assertNotIn("content_correctness_verified", report)
            self.assertTrue(report["exercise_structure_valid"])
            self.assertTrue(report["exercise_verification_passed"])
            self.assertTrue(report["word_count_compliant"])
            self.assertGreaterEqual(report["prose_word_count"], 20)

            plan_path = run_dir / "adaptation_plan.json"
            misplaced_plan = json.loads(plan_path.read_text(encoding="utf-8"))
            misplaced_plan["exercise_section_id"] = "SEC-02"
            write_json(plan_path, misplaced_plan)
            misplaced = subprocess.run(
                [sys.executable, str(VALIDATE), "--workspace-root", str(ROOT), "--run-dir", str(run_dir)],
                capture_output=True,
                text=True,
                check=False,
            )
            misplaced_report = json.loads((run_dir / "validation_report.json").read_text(encoding="utf-8"))
            self.assertNotEqual(misplaced.returncode, 0)
            self.assertIn(
                "exercise_section_id must identify the final planned chapter: expected=SEC-03, actual=SEC-02",
                misplaced_report["errors"],
            )
            misplaced_plan["exercise_section_id"] = "SEC-03"
            write_json(plan_path, misplaced_plan)
            subprocess.run(
                [sys.executable, str(VALIDATE), "--workspace-root", str(ROOT), "--run-dir", str(run_dir)],
                check=True,
            )

            content_path.write_text(lesson.replace("**Checked answer:** `[2.6]`", "**Checked answer:** `[2.7]`"), encoding="utf-8")
            wrong_answer = subprocess.run(
                [sys.executable, str(VALIDATE_EXERCISES), "--content", str(content_path), "--plan", str(run_dir / "adaptation_plan.json"), "--code-validation", str(run_dir / "code_validation.json"), "--output", str(run_dir / "exercise_validation.json")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(wrong_answer.returncode, 0)
            wrong_report = json.loads((run_dir / "exercise_validation.json").read_text(encoding="utf-8"))
            self.assertIn("EX-002: deterministic answer verification failed", wrong_report["errors"])

            content_path.write_text(lesson.replace("**Result from the derivation:** `[2.6]`", "**Result from the derivation:** `[2.7]`"), encoding="utf-8")
            wrong_derivation = subprocess.run(
                [sys.executable, str(VALIDATE_EXERCISES), "--content", str(content_path), "--plan", str(plan_path), "--code-validation", str(run_dir / "code_validation.json"), "--output", str(run_dir / "exercise_validation.json")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(wrong_derivation.returncode, 0)
            wrong_derivation_report = json.loads((run_dir / "exercise_validation.json").read_text(encoding="utf-8"))
            self.assertIn("EX-002: checked answer and visible derivation are inconsistent", wrong_derivation_report["errors"])

            content_path.write_text(lesson.replace('**Expected output:** `"2.6\\n"`', '**Expected output:** `"2.7\\n"`'), encoding="utf-8")
            wrong_stdout = subprocess.run(
                [sys.executable, str(VALIDATE_EXERCISES), "--content", str(content_path), "--plan", str(plan_path), "--code-validation", str(run_dir / "code_validation.json"), "--output", str(run_dir / "exercise_validation.json")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(wrong_stdout.returncode, 0)
            wrong_stdout_report = json.loads((run_dir / "exercise_validation.json").read_text(encoding="utf-8"))
            self.assertIn("EX-003: visible expected output does not match executed stdout", wrong_stdout_report["errors"])
            content_path.write_text(lesson, encoding="utf-8")

            inconsistent_plan = json.loads(plan_path.read_text(encoding="utf-8"))
            inconsistent_plan["exercise_plan"][1]["verification"]["consistency_checks"][0]["expected_value"] = [3.0]
            write_json(plan_path, inconsistent_plan)
            inconsistent_model = subprocess.run(
                [sys.executable, str(VALIDATE_EXERCISES), "--content", str(content_path), "--plan", str(plan_path), "--code-validation", str(run_dir / "code_validation.json"), "--output", str(run_dir / "exercise_validation.json")],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(inconsistent_model.returncode, 0)
            inconsistent_report = json.loads((run_dir / "exercise_validation.json").read_text(encoding="utf-8"))
            self.assertIn("EX-002: model consistency verification failed", inconsistent_report["errors"])
            inconsistent_plan["exercise_plan"][1]["verification"]["consistency_checks"][0]["expected_value"] = [2.6]
            write_json(plan_path, inconsistent_plan)

            subprocess.run([sys.executable, str(EXECUTE_CODE), "--content", str(content_path), "--output", str(run_dir / "code_validation.json")], check=True)
            subprocess.run([sys.executable, str(VALIDATE_EXERCISES), "--content", str(content_path), "--plan", str(run_dir / "adaptation_plan.json"), "--code-validation", str(run_dir / "code_validation.json"), "--output", str(run_dir / "exercise_validation.json")], check=True)

            run_manifest_path = run_dir / "run_manifest.json"
            short_manifest = json.loads(run_manifest_path.read_text(encoding="utf-8"))
            short_manifest["word_count_protocol"]["minimum"] = 1
            short_manifest["word_count_protocol"]["maximum"] = 10
            write_json(run_manifest_path, short_manifest)
            wrong_length = subprocess.run(
                [sys.executable, str(VALIDATE), "--workspace-root", str(ROOT), "--run-dir", str(run_dir)],
                capture_output=True,
                text=True,
                check=False,
            )
            wrong_length_report = json.loads((run_dir / "validation_report.json").read_text(encoding="utf-8"))
            self.assertNotEqual(wrong_length.returncode, 0)
            self.assertFalse(wrong_length_report["word_count_compliant"])
            self.assertTrue(any("prose word count is outside" in error for error in wrong_length_report["errors"]))
            short_manifest["word_count_protocol"]["minimum"] = 20
            short_manifest["word_count_protocol"]["maximum"] = 200
            write_json(run_manifest_path, short_manifest)

            view["required_items"][0]["canonical_statement"] = "Tampered mathematical statement."
            write_json(run_dir / "grounding_view.json", view)
            receipt["generation_view"]["sha256"] = file_hash(run_dir / "grounding_view.json")
            write_json(run_dir / "grounding_receipt.json", receipt)
            run_manifest = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
            run_manifest["grounding_receipt_sha256"] = file_hash(run_dir / "grounding_receipt.json")
            write_json(run_dir / "run_manifest.json", run_manifest)
            rejected = subprocess.run(
                [sys.executable, str(VALIDATE), "--workspace-root", str(ROOT), "--run-dir", str(run_dir)],
                capture_output=True,
                text=True,
                check=False,
            )
            rejected_report = json.loads((run_dir / "validation_report.json").read_text(encoding="utf-8"))
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn(
                "grounding_view canonical content is not the deterministic projection of the frozen contract",
                rejected_report["errors"],
            )


if __name__ == "__main__":
    unittest.main()
