from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[2]
VALIDATE_EXERCISES_PATH = SKILL / "scripts" / "validate_exercises.py"
VALIDATE_OUTPUTS_PATH = SKILL / "scripts" / "validate_adapter_outputs.py"
ADAPTATION_SCHEMA_PATH = SKILL / "references" / "adaptation-plan.schema.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate_exercises = load_module("validate_exercises", VALIDATE_EXERCISES_PATH)
validate_outputs = load_module("validate_adapter_outputs", VALIDATE_OUTPUTS_PATH)


POWER_RESULT = {
    "initial_vector_used": [3.0, 1.0],
    "product": [12.0, 1.0],
    "next_vector": [0.9965457582448796, 0.08304547985373997],
    "rayleigh_quotient": 3.979310344827586,
    "residual": [0.02061818810161853, -0.24741825721941837],
    "residual_norm": 0.24827586206896554,
}


def power_check(expected: dict | None = None) -> dict:
    return {
        "check_id": "CK-001",
        "kind": "power_iteration_step",
        "matrix": [[4.0, 0.0], [0.0, 1.0]],
        "initial_vector": [3.0, 1.0],
        "normalize_initial": False,
        "expected_value": copy.deepcopy(POWER_RESULT if expected is None else expected),
        "absolute_tolerance": 1e-12,
    }


class PowerIterationCheckerTests(unittest.TestCase):
    def test_correct_power_iteration_step_passes(self) -> None:
        result = validate_exercises.validate_consistency_check(power_check())
        self.assertTrue(result["passed"])
        self.assertTrue(result["is_unified_chain"])
        self.assertTrue(validate_exercises.values_close(result["derived_value"], POWER_RESULT, 1e-12))

    def test_normalized_initial_vector_masquerading_as_next_vector_fails(self) -> None:
        wrong = copy.deepcopy(POWER_RESULT)
        wrong["next_vector"] = [0.9486832981, 0.316227766]
        self.assertFalse(validate_exercises.validate_consistency_check(power_check(wrong))["passed"])

    def test_wrong_rayleigh_quotient_fails(self) -> None:
        wrong = copy.deepcopy(POWER_RESULT)
        wrong["rayleigh_quotient"] = 4.0
        self.assertFalse(validate_exercises.validate_consistency_check(power_check(wrong))["passed"])

    def test_wrong_residual_norm_fails(self) -> None:
        wrong = copy.deepcopy(POWER_RESULT)
        wrong["residual_norm"] = 0.0
        self.assertFalse(validate_exercises.validate_consistency_check(power_check(wrong))["passed"])

    def test_non_square_matrix_fails(self) -> None:
        check = power_check()
        check["matrix"] = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
        with self.assertRaisesRegex(ValueError, "square"):
            validate_exercises.validate_power_iteration_step(check)

    def test_dimension_mismatch_fails(self) -> None:
        check = power_check()
        check["initial_vector"] = [1.0]
        with self.assertRaisesRegex(ValueError, "dimension"):
            validate_exercises.validate_power_iteration_step(check)

    def test_zero_initial_vector_fails(self) -> None:
        check = power_check()
        check["initial_vector"] = [0.0, 0.0]
        with self.assertRaisesRegex(ValueError, "nonzero"):
            validate_exercises.validate_power_iteration_step(check)

    def test_zero_matrix_vector_product_is_breakdown(self) -> None:
        check = power_check()
        check["matrix"] = [[0.0, 0.0], [0.0, 1.0]]
        check["initial_vector"] = [1.0, 0.0]
        with self.assertRaisesRegex(ValueError, "breakdown"):
            validate_exercises.validate_power_iteration_step(check)

    def test_objective_gradient_update_regression(self) -> None:
        check = {
            "check_id": "CK-001",
            "kind": "objective_gradient_update",
            "objective_expression": "(x - 2.0)**2",
            "variables": ["x"],
            "point": [3.0],
            "step_size": 0.2,
            "expected_gradient": [2.0],
            "expected_value": [2.6],
            "absolute_tolerance": 1e-12,
        }
        result = validate_exercises.validate_consistency_check(check)
        self.assertTrue(result["passed"])
        self.assertEqual(result["derived_value"], [2.6])

    def test_expression_values_cannot_verify_literal_answers(self) -> None:
        check = {
            "check_id": "CK-001",
            "kind": "expression_values",
            "expressions": ["0.9486832981", "0.316227766"],
            "variables": ["x"],
            "point": [1.0],
            "expected_value": [0.9486832981, 0.316227766],
            "absolute_tolerance": 1e-12,
        }
        with self.assertRaisesRegex(ValueError, "declared variable"):
            validate_exercises.validate_consistency_check(check)


class ExerciseValidatorIntegrationTests(unittest.TestCase):
    def run_validation(
        self,
        derived: object,
        checked: object,
        expected: object | None = None,
        verification: dict | None = None,
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        expected = copy.deepcopy(POWER_RESULT if expected is None else expected)
        if verification is None:
            verification = {
                "method": "deterministic_calculation",
                "python_expression": None,
                "expected_value": expected,
                "absolute_tolerance": 1e-12,
                "consistency_checks": [power_check(expected)],
            }
        plan = {
            "exercise_plan": [
                {
                    "exercise_id": "EX-001",
                    "section_id": "SEC-01",
                    "exercise_type": "hand_calculation",
                    "contract_item_ids": ["RC-001"],
                    "solution_required": True,
                    "verification": verification,
                }
            ]
        }
        derived_json = json.dumps(derived, separators=(",", ":"))
        checked_json = json.dumps(checked, separators=(",", ":"))
        content = (
            "# Lesson\n\n<!-- section: SEC-01 -->\n## Exercises\n\n"
            "<!-- exercise: EX-001 -->\n### Exercise\nCompute one iteration.\n\n"
            "<!-- solution: EX-001 -->\n### Solution\nThe complete calculation gives:\n\n"
            f"<!-- derived-answer: EX-001 -->\n**Result from the derivation:** `{derived_json}`\n\n"
            f"<!-- answer: EX-001 -->\n**Checked answer:** `{checked_json}`\n"
        )
        with tempfile.TemporaryDirectory() as raw_temp:
            run_dir = Path(raw_temp)
            content_path = run_dir / "adapted_content.md"
            plan_path = run_dir / "adaptation_plan.json"
            code_path = run_dir / "code_validation.json"
            report_path = run_dir / "exercise_validation.json"
            content_path.write_text(content, encoding="utf-8")
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            code_path.write_text(json.dumps({"blocks": []}), encoding="utf-8")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATE_EXERCISES_PATH),
                    "--content",
                    str(content_path),
                    "--plan",
                    str(plan_path),
                    "--code-validation",
                    str(code_path),
                    "--output",
                    str(report_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            report = json.loads(report_path.read_text(encoding="utf-8"))
        return completed, report

    def test_structured_result_passes_end_to_end(self) -> None:
        completed, report = self.run_validation(POWER_RESULT, POWER_RESULT)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(report["overall_status"], "passed")

    def test_derivation_checked_answer_and_validator_must_all_agree(self) -> None:
        wrong = copy.deepcopy(POWER_RESULT)
        wrong["next_vector"] = [0.9486832981, 0.316227766]
        cases = [
            (wrong, POWER_RESULT, POWER_RESULT),
            (POWER_RESULT, wrong, POWER_RESULT),
            (wrong, wrong, POWER_RESULT),
        ]
        for derived, checked, expected in cases:
            with self.subTest(derived_wrong=derived == wrong, checked_wrong=checked == wrong):
                completed, report = self.run_validation(derived, checked, expected)
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(report["overall_status"], "failed")

    def test_literal_expression_values_cannot_self_verify_a_hand_calculation(self) -> None:
        wrong = [0.9486832981, 0.316227766]
        verification = {
            "method": "deterministic_calculation",
            "python_expression": "[0.9486832981, 0.316227766]",
            "expected_value": wrong,
            "absolute_tolerance": 1e-12,
            "consistency_checks": [
                {
                    "check_id": "CK-001",
                    "kind": "expression_values",
                    "expressions": ["0.9486832981", "0.316227766"],
                    "variables": ["x"],
                    "point": [0.0],
                    "expected_value": wrong,
                    "absolute_tolerance": 1e-12,
                }
            ],
        }
        completed, report = self.run_validation(wrong, wrong, wrong, verification)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("EX-001: model consistency verification failed", report["errors"])
        self.assertIn("EX-001: deterministic answer verification failed", report["errors"])

    def test_unified_checker_forbids_free_python_expression(self) -> None:
        verification = {
            "method": "deterministic_calculation",
            "python_expression": "[1.0]",
            "expected_value": POWER_RESULT,
            "absolute_tolerance": 1e-12,
            "consistency_checks": [power_check()],
        }
        completed, report = self.run_validation(POWER_RESULT, POWER_RESULT, POWER_RESULT, verification)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("EX-001: deterministic answer verification failed", report["errors"])


class AdaptationPlanSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema = json.loads(ADAPTATION_SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_power_iteration_branch_accepts_only_its_fields(self) -> None:
        check_schema = self.schema["$defs"]["consistencyCheck"]
        self.assertEqual(validate_outputs.schema_errors(power_check(), check_schema, self.schema), [])
        mixed = power_check()
        mixed["variables"] = ["x"]
        self.assertTrue(validate_outputs.schema_errors(mixed, check_schema, self.schema))

    def test_verification_expected_value_accepts_structured_object(self) -> None:
        expected_schema = self.schema["$defs"]["verificationExpectedValue"]
        self.assertEqual(validate_outputs.schema_errors(POWER_RESULT, expected_schema, self.schema), [])

    def test_legacy_gradient_update_shape_remains_valid(self) -> None:
        check_schema = self.schema["$defs"]["consistencyCheck"]
        check = {
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
        self.assertEqual(validate_outputs.schema_errors(check, check_schema, self.schema), [])
        self.assertTrue(validate_exercises.validate_consistency_check(check)["passed"])


if __name__ == "__main__":
    unittest.main()
