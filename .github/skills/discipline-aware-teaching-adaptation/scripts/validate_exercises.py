#!/usr/bin/env python3
"""Validate exercise structure, model consistency, numeric answers, and code."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import operator
import re
from pathlib import Path


SECTION_RE = re.compile(r"<!--\s*section:\s*(SEC-[0-9]{2})\s*-->")
EXERCISE_RE = re.compile(r"<!--\s*exercise:\s*(EX-[0-9]{3,})\s*-->")
SOLUTION_RE = re.compile(r"<!--\s*solution:\s*(EX-[0-9]{3,})\s*-->")
ANSWER_RE = re.compile(
    r"<!--\s*answer:\s*(EX-[0-9]{3,})\s*-->\s*\n\*\*Checked answer:\*\*\s*`([^`\n]+)`"
)
DERIVED_ANSWER_RE = re.compile(
    r"<!--\s*derived-answer:\s*(EX-[0-9]{3,})\s*-->\s*\n\*\*Result from the derivation:\*\*\s*`([^`\n]+)`"
)
EXPECTED_STDOUT_RE = re.compile(
    r"<!--\s*expected-stdout:\s*(EX-[0-9]{3,})/([1-9][0-9]*)\s*-->\s*\n\*\*Expected output:\*\*\s*`([^`\n]+)`"
)
BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY_OPERATORS = {ast.UAdd: operator.pos, ast.USub: operator.neg}
ALLOWED_FUNCTIONS = {"sin", "cos", "exp", "log", "sqrt"}


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("expression may contain only numbers, arithmetic, and numeric lists")
    if not math.isfinite(float(value)) or abs(float(value)) > 1e100:
        raise ValueError("numeric result is non-finite or outside the validation limit")
    return value


def evaluate_node(node):
    if isinstance(node, ast.Expression):
        return evaluate_node(node.body)
    if isinstance(node, ast.Constant):
        return checked_number(node.value)
    if isinstance(node, (ast.List, ast.Tuple)):
        if len(node.elts) > 100:
            raise ValueError("numeric list is too long")
        return [evaluate_node(item) for item in node.elts]
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
        return checked_number(UNARY_OPERATORS[type(node.op)](evaluate_node(node.operand)))
    if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
        left, right = evaluate_node(node.left), evaluate_node(node.right)
        if isinstance(left, list) or isinstance(right, list):
            raise ValueError("list arithmetic must be expressed element by element")
        if isinstance(node.op, ast.Pow) and abs(float(right)) > 10:
            raise ValueError("power exponent exceeds the validation limit")
        return checked_number(BINARY_OPERATORS[type(node.op)](left, right))
    raise ValueError(f"unsupported expression element: {type(node).__name__}")


def safe_numeric_eval(expression: str):
    if not expression or len(expression) > 500:
        raise ValueError("python_expression must contain 1-500 characters")
    tree = ast.parse(expression, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 100:
        raise ValueError("python_expression is too complex")
    return evaluate_node(tree)


def _dual_expression(node, variables: list[str], values: dict[str, float]):
    """Evaluate a scalar expression and its gradient using forward autodiff."""
    dimension = len(variables)
    zeros = [0.0] * dimension
    if isinstance(node, ast.Expression):
        return _dual_expression(node.body, variables, values)
    if isinstance(node, ast.Constant):
        return float(checked_number(node.value)), zeros
    if isinstance(node, ast.Name):
        if node.id not in values:
            raise ValueError(f"unknown variable: {node.id}")
        gradient = [0.0] * dimension
        gradient[variables.index(node.id)] = 1.0
        return values[node.id], gradient
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPERATORS:
        value, gradient = _dual_expression(node.operand, variables, values)
        if isinstance(node.op, ast.USub):
            return -value, [-item for item in gradient]
        return value, gradient
    if isinstance(node, ast.BinOp) and type(node.op) in BINARY_OPERATORS:
        left, left_gradient = _dual_expression(node.left, variables, values)
        right, right_gradient = _dual_expression(node.right, variables, values)
        if isinstance(node.op, ast.Add):
            return left + right, [a + b for a, b in zip(left_gradient, right_gradient)]
        if isinstance(node.op, ast.Sub):
            return left - right, [a - b for a, b in zip(left_gradient, right_gradient)]
        if isinstance(node.op, ast.Mult):
            return left * right, [a * right + left * b for a, b in zip(left_gradient, right_gradient)]
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise ZeroDivisionError("division by zero")
            return left / right, [
                (a * right - left * b) / (right * right)
                for a, b in zip(left_gradient, right_gradient)
            ]
        if isinstance(node.op, ast.Pow):
            if any(abs(item) > 0 for item in right_gradient):
                raise ValueError("variable exponents are not supported")
            if abs(right) > 10:
                raise ValueError("power exponent exceeds the validation limit")
            value = left**right
            factor = 0.0 if right == 0 else right * (left ** (right - 1))
            return value, [factor * item for item in left_gradient]
        raise ValueError(f"operator is not differentiable here: {type(node.op).__name__}")
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCTIONS or len(node.args) != 1 or node.keywords:
            raise ValueError("only one-argument sin, cos, exp, log, and sqrt calls are allowed")
        argument, argument_gradient = _dual_expression(node.args[0], variables, values)
        name = node.func.id
        if name == "sin":
            value, derivative = math.sin(argument), math.cos(argument)
        elif name == "cos":
            value, derivative = math.cos(argument), -math.sin(argument)
        elif name == "exp":
            value = derivative = math.exp(argument)
        elif name == "log":
            if argument <= 0:
                raise ValueError("log argument must be positive")
            value, derivative = math.log(argument), 1.0 / argument
        else:
            if argument <= 0:
                raise ValueError("sqrt argument must be positive for gradient validation")
            value, derivative = math.sqrt(argument), 0.5 / math.sqrt(argument)
        return value, [derivative * item for item in argument_gradient]
    raise ValueError(f"unsupported model expression element: {type(node).__name__}")


def safe_model_eval(expression: str, variables: list[str], point: list[float]):
    if not isinstance(expression, str) or not expression or len(expression) > 500:
        raise ValueError("model expression must contain 1-500 characters")
    if not isinstance(variables, list) or not 1 <= len(variables) <= 10:
        raise ValueError("model variables must contain 1-10 names")
    if len(set(variables)) != len(variables) or any(not isinstance(name, str) or not name.isidentifier() for name in variables):
        raise ValueError("model variable names must be unique Python identifiers")
    if not isinstance(point, list) or len(point) != len(variables):
        raise ValueError("model point must contain one value per variable")
    numeric_point = [float(checked_number(value)) for value in point]
    tree = ast.parse(expression, mode="eval")
    if sum(1 for _ in ast.walk(tree)) > 150:
        raise ValueError("model expression is too complex")
    value, gradient = _dual_expression(tree, variables, dict(zip(variables, numeric_point)))
    checked_number(value)
    for component in gradient:
        checked_number(component)
    return value, gradient


def validate_consistency_check(check: dict) -> tuple[bool, str, object | None]:
    kind = check.get("kind")
    variables = check.get("variables")
    point = check.get("point")
    expected = check.get("expected_value")
    tolerance = check.get("absolute_tolerance", 0.0)
    check_id = check.get("check_id", "unnamed-check")
    if kind == "objective_gradient":
        value, actual = safe_model_eval(check.get("objective_expression"), variables, point)
        passed = values_close(actual, expected, tolerance)
        return passed, f"{check_id}: objective value={value!r}; gradient={actual!r}; expected={expected!r}", None
    if kind == "objective_gradient_update":
        value, gradient = safe_model_eval(check.get("objective_expression"), variables, point)
        step_size = checked_number(check.get("step_size"))
        if float(step_size) <= 0:
            raise ValueError("objective_gradient_update step_size must be positive")
        numeric_point = [float(checked_number(component)) for component in point]
        update = [component - float(step_size) * derivative for component, derivative in zip(numeric_point, gradient)]
        expected_gradient = check.get("expected_gradient")
        gradient_passed = values_close(gradient, expected_gradient, tolerance)
        update_passed = values_close(update, expected, tolerance)
        return (
            gradient_passed and update_passed,
            f"{check_id}: objective value={value!r}; gradient={gradient!r}; expected gradient={expected_gradient!r}; "
            f"update={update!r}; expected update={expected!r}",
            update,
        )
    if kind == "expression_values":
        expressions = check.get("expressions")
        if not isinstance(expressions, list) or not expressions:
            raise ValueError("expression_values requires at least one expression")
        actual_values = [safe_model_eval(expression, variables, point)[0] for expression in expressions]
        actual = actual_values[0] if not isinstance(expected, list) and len(actual_values) == 1 else actual_values
        passed = values_close(actual, expected, tolerance)
        return passed, f"{check_id}: expression values={actual!r}; expected={expected!r}", None
    raise ValueError(f"unknown consistency-check kind: {kind!r}")


def values_close(actual, expected, tolerance: float) -> bool:
    if isinstance(actual, list) or isinstance(expected, list):
        return isinstance(actual, list) and isinstance(expected, list) and len(actual) == len(expected) and all(
            values_close(a, b, tolerance) for a, b in zip(actual, expected)
        )
    if isinstance(actual, bool) or isinstance(expected, bool):
        return False
    if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
        return False
    return math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tolerance)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", required=True)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--code-validation", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    content_path = Path(args.content).resolve()
    plan_path = Path(args.plan).resolve()
    code_path = Path(args.code_validation).resolve()
    output_path = Path(args.output).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    results: list[dict] = []

    try:
        content = content_path.read_text(encoding="utf-8")
        plan = load_json(plan_path)
        code = load_json(code_path)
        exercises = plan.get("exercise_plan", [])
        section_matches = list(SECTION_RE.finditer(content))
        exercise_matches = list(EXERCISE_RE.finditer(content))
        solution_matches = list(SOLUTION_RE.finditer(content))
        answer_matches = list(ANSWER_RE.finditer(content))
        derived_answer_matches = list(DERIVED_ANSWER_RE.finditer(content))
        expected_stdout_matches = list(EXPECTED_STDOUT_RE.finditer(content))
        exercise_positions = {}
        solution_positions = {}
        answer_values = {}
        derived_answer_values = {}
        expected_stdout_values = {}
        for match in exercise_matches:
            exercise_positions.setdefault(match.group(1), []).append(match.start())
        for match in solution_matches:
            solution_positions.setdefault(match.group(1), []).append(match.start())
        for match in answer_matches:
            answer_values.setdefault(match.group(1), []).append((match.start(), match.group(2)))
        for match in derived_answer_matches:
            derived_answer_values.setdefault(match.group(1), []).append((match.start(), match.group(2)))
        for match in expected_stdout_matches:
            key = (match.group(1), int(match.group(2)))
            expected_stdout_values.setdefault(key, []).append((match.start(), match.group(3)))
        section_positions = {match.group(1): match.start() for match in section_matches}
        ordered_section_positions = sorted((position, section_id) for section_id, position in section_positions.items())

        planned_ids = [item.get("exercise_id") for item in exercises]
        actual_ids = [match.group(1) for match in exercise_matches]
        sequential_ids = [f"EX-{index:03d}" for index in range(1, len(exercises) + 1)]
        if planned_ids != sequential_ids:
            errors.append(f"exercise IDs must be consecutive in reading order: expected={sequential_ids}, actual={planned_ids}")
        if actual_ids != planned_ids:
            errors.append(f"exercise marker order differs from exercise_plan: expected={planned_ids}, actual={actual_ids}")
        unknown_solution_ids = set(solution_positions) - set(planned_ids)
        unknown_answer_ids = set(answer_values) - set(planned_ids)
        unknown_derived_ids = set(derived_answer_values) - set(planned_ids)
        unknown_stdout_ids = {exercise_id for exercise_id, _ in expected_stdout_values} - set(planned_ids)
        if unknown_solution_ids:
            errors.append(f"solution markers reference unknown exercises: {sorted(unknown_solution_ids)}")
        if unknown_answer_ids:
            errors.append(f"checked-answer markers reference unknown exercises: {sorted(unknown_answer_ids)}")
        if unknown_derived_ids:
            errors.append(f"derived-answer markers reference unknown exercises: {sorted(unknown_derived_ids)}")
        if unknown_stdout_ids:
            errors.append(f"expected-stdout markers reference unknown exercises: {sorted(unknown_stdout_ids)}")

        for item in exercises:
            exercise_id = item.get("exercise_id")
            section_id = item.get("section_id")
            method = item.get("verification", {}).get("method")
            details: list[str] = []
            ex_positions = exercise_positions.get(exercise_id, [])
            sol_positions = solution_positions.get(exercise_id, [])
            section_start = section_positions.get(section_id)
            section_end = len(content)
            if section_start is not None:
                later = [position for position, _ in ordered_section_positions if position > section_start]
                if later:
                    section_end = later[0]
            exercise_end = section_end
            if ex_positions:
                later_exercises = [match.start() for match in exercise_matches if match.start() > ex_positions[0]]
                if later_exercises:
                    exercise_end = min(exercise_end, later_exercises[0])
            markers_valid = len(ex_positions) == 1 and section_start is not None and section_start < ex_positions[0] < section_end
            solution_present = len(sol_positions) == 1 and bool(ex_positions) and ex_positions[0] < sol_positions[0] < exercise_end
            binding_declared = bool(item.get("contract_item_ids"))
            if not markers_valid:
                errors.append(f"{exercise_id}: exercise marker is missing, duplicated, out of order, or outside {section_id}")
            if item.get("solution_required") and not solution_present:
                errors.append(f"{exercise_id}: required worked-solution marker is missing or misplaced")
            if not binding_declared:
                errors.append(f"{exercise_id}: no Contract item binding is declared")

            calculation_passed = True
            code_passed = True
            consistency_passed = True
            unified_calculation_passed = True
            visible_derivation_consistent = True
            stdout_claims_consistent = True
            verification = item.get("verification", {})
            consistency_checks = verification.get("consistency_checks", [])
            unified_results = []
            for check in consistency_checks:
                try:
                    check_passed, check_detail, derived_value = validate_consistency_check(check)
                    consistency_passed = consistency_passed and check_passed
                    details.append(check_detail)
                    if check.get("kind") == "objective_gradient_update":
                        unified_results.append(derived_value)
                        unified_calculation_passed = unified_calculation_passed and check_passed
                except (SyntaxError, TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
                    consistency_passed = False
                    if check.get("kind") == "objective_gradient_update":
                        unified_calculation_passed = False
                    details.append(f"{check.get('check_id', 'unnamed-check')}: consistency check failed: {exc}")
            if not consistency_passed:
                errors.append(f"{exercise_id}: model consistency verification failed")

            if method in {"deterministic_calculation", "combined"}:
                expression = verification.get("python_expression")
                expected = verification.get("expected_value")
                tolerance = verification.get("absolute_tolerance", 0.0)
                if unified_results:
                    unified_calculation_passed = unified_calculation_passed and len(unified_results) == 1 and expression is None
                    calculated = unified_results[0] if len(unified_results) == 1 else None
                    if not unified_calculation_passed:
                        details.append("objective-gradient-update verification requires exactly one unified chain and no free python_expression")
                    calculation_passed = unified_calculation_passed and values_close(calculated, expected, tolerance)
                    details.append(f"unified objective-gradient-update chain produced {calculated!r}; expected {expected!r}")
                else:
                    try:
                        calculated = safe_numeric_eval(expression)
                        calculation_passed = values_close(calculated, expected, tolerance)
                        details.append(f"deterministic calculation produced {calculated!r}; expected {expected!r}")
                    except (SyntaxError, TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
                        calculation_passed = False
                        details.append(f"deterministic calculation failed: {exc}")

                visible_derived_answer = None
                raw_derivations = derived_answer_values.get(exercise_id, [])
                if len(raw_derivations) != 1:
                    visible_derivation_consistent = False
                    details.append("exactly one visible result-from-the-derivation line is required")
                else:
                    derivation_position, raw_derivation = raw_derivations[0]
                    if not solution_present or not (sol_positions[0] < derivation_position < exercise_end):
                        visible_derivation_consistent = False
                        details.append("result-from-the-derivation line must occur inside the worked solution section")
                    try:
                        visible_derived_answer = json.loads(raw_derivation)
                    except json.JSONDecodeError as exc:
                        visible_derivation_consistent = False
                        details.append(f"result from the derivation is not valid JSON: {exc}")
                    else:
                        if not values_close(visible_derived_answer, expected, tolerance):
                            visible_derivation_consistent = False
                            details.append(f"visible derivation result {visible_derived_answer!r} differs from expected value")

                visible_answer = None
                raw_answers = answer_values.get(exercise_id, [])
                if len(raw_answers) != 1:
                    calculation_passed = False
                    details.append("exactly one checked-answer line is required")
                else:
                    answer_position, raw_answer = raw_answers[0]
                    if not solution_present or not (sol_positions[0] < answer_position < exercise_end):
                        calculation_passed = False
                        details.append("checked-answer line must occur inside the worked solution section")
                    try:
                        visible_answer = json.loads(raw_answer)
                    except json.JSONDecodeError as exc:
                        calculation_passed = False
                        details.append(f"checked answer is not valid JSON: {exc}")
                    else:
                        if not values_close(visible_answer, expected, tolerance):
                            calculation_passed = False
                            details.append(f"checked answer {visible_answer!r} differs from expected value")
                if visible_answer is not None and visible_derived_answer is not None and not values_close(visible_answer, visible_derived_answer, tolerance):
                    visible_derivation_consistent = False
                    details.append(f"checked answer {visible_answer!r} differs from visible derivation result {visible_derived_answer!r}")
                if not visible_derivation_consistent:
                    errors.append(f"{exercise_id}: checked answer and visible derivation are inconsistent")
                if not calculation_passed or not unified_calculation_passed:
                    errors.append(f"{exercise_id}: deterministic answer verification failed")
            elif answer_values.get(exercise_id) or derived_answer_values.get(exercise_id):
                visible_derivation_consistent = False
                errors.append(f"{exercise_id}: checked-answer and derived-answer lines are reserved for deterministic_calculation or combined verification")

            if method in {"code_execution", "combined"}:
                blocks = [block for block in code.get("blocks", []) if block.get("exercise_id") == exercise_id]
                code_passed = bool(blocks) and all(block.get("execution_status") == "passed" for block in blocks)
                details.append(f"{len(blocks)} exercise-linked Python block(s) found")
                if not code_passed:
                    errors.append(f"{exercise_id}: requires at least one passing exercise-linked Python block")
                expected_keys = {(exercise_id, index) for index in range(1, len(blocks) + 1)}
                actual_keys = {key for key in expected_stdout_values if key[0] == exercise_id}
                if actual_keys != expected_keys:
                    stdout_claims_consistent = False
                    details.append(f"expected-output markers must cover each exercise code block exactly once: expected={sorted(expected_keys)}, actual={sorted(actual_keys)}")
                for index, block in enumerate(blocks, start=1):
                    claims = expected_stdout_values.get((exercise_id, index), [])
                    if len(claims) != 1:
                        stdout_claims_consistent = False
                        continue
                    claim_position, raw_claim = claims[0]
                    if not solution_present or not (sol_positions[0] < claim_position < exercise_end):
                        stdout_claims_consistent = False
                        details.append(f"expected output for code block {index} must occur inside the worked solution section")
                    try:
                        expected_stdout = json.loads(raw_claim)
                    except json.JSONDecodeError as exc:
                        stdout_claims_consistent = False
                        details.append(f"expected output for code block {index} is not a valid JSON string: {exc}")
                        continue
                    if not isinstance(expected_stdout, str):
                        stdout_claims_consistent = False
                        details.append(f"expected output for code block {index} must be a JSON string")
                    elif expected_stdout != block.get("stdout"):
                        stdout_claims_consistent = False
                        details.append(f"expected output for code block {index} differs from executed stdout: expected={expected_stdout!r}, actual={block.get('stdout')!r}")
                if not stdout_claims_consistent:
                    errors.append(f"{exercise_id}: visible expected output does not match executed stdout")
            elif any(exercise_id == key[0] for key in expected_stdout_values):
                stdout_claims_consistent = False
                errors.append(f"{exercise_id}: expected-stdout lines are reserved for code_execution or combined verification")

            verification_status = "passed" if all([
                calculation_passed,
                code_passed,
                consistency_passed,
                unified_calculation_passed,
                visible_derivation_consistent,
                stdout_claims_consistent,
            ]) else "failed"
            results.append(
                {
                    "exercise_id": exercise_id,
                    "exercise_type": item.get("exercise_type"),
                    "markers_valid": markers_valid,
                    "solution_present": solution_present,
                    "contract_binding_declared": binding_declared,
                    "verification_method": method,
                    "model_consistency_passed": consistency_passed,
                    "unified_calculation_passed": unified_calculation_passed,
                    "visible_derivation_consistent": visible_derivation_consistent,
                    "stdout_claims_consistent": stdout_claims_consistent,
                    "verification_status": verification_status,
                    "details": details,
                }
            )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(str(exc))
        exercises = []

    report = {
        "content_file": str(content_path),
        "content_sha256": sha256(content_path) if content_path.is_file() else "0" * 64,
        "plan_file": str(plan_path),
        "plan_sha256": sha256(plan_path) if plan_path.is_file() else "0" * 64,
        "code_validation_file": str(code_path),
        "code_validation_sha256": sha256(code_path) if code_path.is_file() else "0" * 64,
        "overall_status": "failed" if errors else "passed",
        "exercise_count": len(exercises),
        "exercises": results,
        "errors": errors,
        "warnings": warnings,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if errors:
        print(f"FAIL: {len(errors)} exercise validation error(s)")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {len(exercises)} generated exercise(s) are structurally bound; deterministic checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
