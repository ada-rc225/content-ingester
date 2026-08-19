#!/usr/bin/env python3
"""Regression tests for the unified RQ2 pathway-plan validator and P2 preflight."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[4]
VALIDATOR = ROOT / "experiments/rq2/scripts/validate_pathway_plan.py"
PREFLIGHT = ROOT / ".github/skills/plan-adaptive-curriculum-pathways/scripts/prepare_pathway_inputs.py"
CONTRACT = ROOT / "experiments/rq1/reference-contracts/power-iteration-v1/release/frozen_reference_contract.json"
MODEL = ROOT / "curriculum-models/power-iteration-v1/release/frozen-contract-dependencies.json"
MODEL_RELEASE = MODEL.with_name("curriculum-release-report.json")
REQUEST = ROOT / "experiments/rq2/learning-requests/power-iteration-second-year.json"
PROFILE = ROOT / "experiments/rq2/profiles/computer-science-year-2.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def scope(item_ids: list[str], bridge_count: int = 0) -> dict:
    contract_items = {item["item_id"]: item for item in load(CONTRACT)["contract_items"]}
    return {
        "selected_contract_item_count": len(item_ids),
        "excluded_contract_item_count": len(contract_items) - len(item_ids),
        "critical_item_count": sum(contract_items[item_id]["criticality"] == "critical" for item_id in item_ids),
        "formula_count": len({ref for item_id in item_ids for ref in contract_items[item_id]["formula_refs"]}),
        "algorithm_or_code_item_count": sum(contract_items[item_id]["item_type"] in {"algorithm_rule", "code_semantics"} for item_id in item_ids),
        "released_bridge_count": bridge_count,
        "estimated_duration_minutes": 90,
    }


def reference_binding() -> dict:
    contract = load(CONTRACT)
    return {
        "contract_id": contract["contract_id"],
        "contract_version": contract["contract_version"],
        "file": rel(CONTRACT),
        "sha256": digest(CONTRACT),
    }


def request_binding() -> dict:
    request = load(REQUEST)
    return {
        "request_id": request["request_id"],
        "request_version": request["request_version"],
        "file": rel(REQUEST),
        "sha256": digest(REQUEST),
    }


def decisions(selected: set[str], p2: bool) -> list[dict]:
    all_ids = [item["item_id"] for item in load(CONTRACT)["contract_items"]]
    return [
        {
            "item_id": item_id,
            "decision": "include" if item_id in selected else "exclude",
            "selected_role": "target" if item_id in selected else None,
            "rationale": "Selected for requested capability coverage." if item_id in selected else "Not required for this bounded pathway.",
            "profile_basis": ([{"profile_field": "preferred_representations", "evidence": "pseudocode and stopping criteria"}] if p2 else []),
        }
        for item_id in all_ids
    ]


def goal_mappings(selected: set[str]) -> list[dict]:
    candidates = {
        "LG-001": ["RC-001", "RC-005"],
        "LG-002": ["RC-009", "RC-010", "RC-011"],
        "LG-003": ["RC-004", "RC-007"],
        "LG-004": ["RC-016", "RC-017"],
    }
    return [
        {
            "capability_id": capability,
            "supporting_item_ids": [item for item in items if item in selected],
            "coverage": "complete" if any(item in selected for item in items) else "unmet",
            "rationale": "Mapped directly to selected Contract items." if any(item in selected for item in items) else "Optional capability is outside this pathway.",
        }
        for capability, items in candidates.items()
    ]


def baseline_plan() -> dict:
    all_ids = [item["item_id"] for item in load(CONTRACT)["contract_items"]]
    selected = set(all_ids)
    return {
        "schema_version": "1.0",
        "pathway_id": "power-iteration-p0-v1",
        "condition": "P0",
        "plan_status": "complete",
        "topic": load(REQUEST)["topic"],
        "source_authorities": {"reference_contract": reference_binding(), "curriculum_model": None},
        "profile_binding": None,
        "profile_concept_assessment_binding": None,
        "learning_request_binding": request_binding(),
        "baseline_pathway_binding": None,
        "selection_authority": "fixed_baseline",
        "selection": {
            "all_contract_item_ids": all_ids,
            "selected_item_ids": all_ids,
            "excluded_item_ids": [],
            "decisions": decisions(selected, False),
        },
        "learning_goal_mappings": goal_mappings(selected),
        "learning_units": [{
            "unit_id": "P0-U001",
            "unit_type": "contract_content",
            "purpose": "Normalize the complete canonical baseline without profile adaptation.",
            "contract_item_ids": all_ids,
            "bridge_contract_id": None,
            "prerequisite_unit_ids": [],
            "learning_goal_ids": ["LG-001", "LG-002", "LG-003", "LG-004"],
        }],
        "instruction_sequence": ["P0-U001"],
        "bridge_requirements": [],
        "pathway_changes": [],
        "scope_summary": scope(all_ids),
        "rendering_policy": {
            "output_form": "one_continuous_student_facing_lesson",
            "learning_units_are_pages": False,
            "target_duration_minutes": 90,
        },
        "generated_by": {
            "producer": "normalize-p0-pathway",
            "producer_version": "1.0",
            "method": "deterministic_baseline_normalization",
            "generated_at": "2026-08-18T12:00:00Z",
        },
    }


def assessment(path: Path) -> dict:
    model = load(MODEL)
    profile = load(PROFILE)
    return {
        "schema_version": "1.0",
        "assessment_id": "computer-science-year-2-concept-assessment-v1",
        "assessment_status": "provisional",
        "profile_binding": {"profile_id": profile["profile_id"], "file": rel(PROFILE), "sha256": digest(PROFILE)},
        "curriculum_model_binding": {"model_id": model["model_id"], "file": rel(MODEL), "sha256": digest(MODEL)},
        "concept_assessments": [
            {
                "concept_id": concept["concept_id"],
                "concept_name": concept["name"],
                "mastery": "mastered",
                "confidence": "medium",
                "profile_evidence": [{"profile_field": "prior_knowledge", "value": "vectors and matrices"}],
                "rationale": "The profile provides sufficient evidence for this pilot fixture.",
            }
            for concept in model["external_prerequisite_concepts"]
        ],
        "generated_by": {
            "producer": "adaptive-curriculum-pathway-planner",
            "producer_version": "1.0",
            "generated_at": "2026-08-18T12:05:00Z",
        },
    }


def p2_plan(baseline_path: Path, assessment_path: Path) -> dict:
    all_ids = [item["item_id"] for item in load(CONTRACT)["contract_items"]]
    selected_list = ["RC-001", "RC-004", "RC-005", "RC-007", "RC-009", "RC-010", "RC-011"]
    selected = set(selected_list)
    model = load(MODEL)
    profile = load(PROFILE)
    fallback_7 = next(item for item in model["items"] if item["item_id"] == "RC-007")["fallback_when_explanatory_dependencies_omitted"]["instruction"]
    fallback_10 = next(item for item in model["items"] if item["item_id"] == "RC-010")["fallback_when_explanatory_dependencies_omitted"]["instruction"]
    return {
        "schema_version": "1.0",
        "pathway_id": "power-iteration-cs-p2-v1",
        "condition": "P2",
        "plan_status": "complete",
        "topic": load(REQUEST)["topic"],
        "source_authorities": {
            "reference_contract": reference_binding(),
            "curriculum_model": {
                "model_id": model["model_id"], "file": rel(MODEL), "sha256": digest(MODEL),
                "release_report_file": rel(MODEL_RELEASE), "release_report_sha256": digest(MODEL_RELEASE),
            },
        },
        "profile_binding": {"profile_id": profile["profile_id"], "file": rel(PROFILE), "sha256": digest(PROFILE)},
        "profile_concept_assessment_binding": {
            "artifact_id": load(assessment_path)["assessment_id"],
            "file": str(assessment_path.resolve()),
            "sha256": digest(assessment_path),
        },
        "learning_request_binding": request_binding(),
        "baseline_pathway_binding": {
            "pathway_id": load(baseline_path)["pathway_id"],
            "file": str(baseline_path.resolve()),
            "sha256": digest(baseline_path),
        },
        "selection_authority": "dependency_aware_planner",
        "selection": {
            "all_contract_item_ids": all_ids,
            "selected_item_ids": selected_list,
            "excluded_item_ids": [item for item in all_ids if item not in selected],
            "decisions": decisions(selected, True),
        },
        "learning_goal_mappings": goal_mappings(selected),
        "learning_units": [
            {"unit_id": "P2-U001", "unit_type": "contract_content", "purpose": "Establish eigenpair meaning.", "contract_item_ids": ["RC-001"], "bridge_contract_id": None, "prerequisite_unit_ids": [], "learning_goal_ids": ["LG-001"]},
            {"unit_id": "P2-U002", "unit_type": "contract_content", "purpose": "Introduce assumptions, update, and eigenvalue estimate.", "contract_item_ids": ["RC-004", "RC-005", "RC-009"], "bridge_contract_id": None, "prerequisite_unit_ids": ["P2-U001"], "learning_goal_ids": ["LG-001", "LG-002", "LG-003"]},
            {"unit_id": "P2-U003", "unit_type": "contract_content", "purpose": fallback_10, "contract_item_ids": ["RC-010"], "bridge_contract_id": None, "prerequisite_unit_ids": ["P2-U001", "P2-U002"], "learning_goal_ids": ["LG-002"]},
            {"unit_id": "P2-U004", "unit_type": "contract_content", "purpose": fallback_7, "contract_item_ids": ["RC-007", "RC-011"], "bridge_contract_id": None, "prerequisite_unit_ids": ["P2-U002", "P2-U003"], "learning_goal_ids": ["LG-002", "LG-003"]},
        ],
        "instruction_sequence": ["P2-U001", "P2-U002", "P2-U003", "P2-U004"],
        "bridge_requirements": [],
        "pathway_changes": [
            {"change_type": "change_item_selection", "affected_ids": ["RC-002"], "profile_basis": [{"profile_field": "preferred_representations", "evidence": "pseudocode and stopping criteria"}], "rationale": "Bound scope to requested capabilities."},
            {"change_type": "regroup_contract_items", "affected_ids": ["P2-U001", "P2-U002"], "profile_basis": [{"profile_field": "preferred_representations", "evidence": "iteration invariants"}], "rationale": "Separate prerequisites from dependent operational content."},
        ],
        "scope_summary": scope(selected_list),
        "rendering_policy": {"output_form": "one_continuous_student_facing_lesson", "learning_units_are_pages": False, "target_duration_minutes": 90},
        "generated_by": {"producer": "adaptive-curriculum-pathway-planner", "producer_version": "1.0", "method": "adaptive_pathway_planning", "generated_at": "2026-08-18T12:10:00Z"},
    }


class PathwayPlanValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(dir=ROOT)
        self.directory = Path(self.temp.name)
        self.baseline_path = self.directory / "p0.json"
        self.assessment_path = self.directory / "assessment.json"
        self.plan_path = self.directory / "p2.json"
        self.baseline_path.write_text(json.dumps(baseline_plan(), indent=2) + "\n", encoding="utf-8")
        self.assessment_path.write_text(json.dumps(assessment(self.assessment_path), indent=2) + "\n", encoding="utf-8")
        self.plan_path.write_text(json.dumps(p2_plan(self.baseline_path, self.assessment_path), indent=2) + "\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_validator(self, plan: dict | None = None) -> tuple[subprocess.CompletedProcess[str], dict]:
        if plan is not None:
            self.plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        report_path = self.directory / "report.json"
        result = subprocess.run(
            ["python3", str(VALIDATOR), "--workspace-root", str(ROOT), "--pathway", str(self.plan_path), "--output", str(report_path), "--phase", "pilot"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        return result, load(report_path)

    def test_valid_p2_plan_passes(self) -> None:
        result, report = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(report["metrics"]["detected_change_types"], ["change_item_selection", "regroup_contract_items"])

    def test_missing_hard_dependency_fails(self) -> None:
        plan = load(self.plan_path)
        plan["selection"]["selected_item_ids"].remove("RC-004")
        plan["selection"]["excluded_item_ids"].append("RC-004")
        decision = next(item for item in plan["selection"]["decisions"] if item["item_id"] == "RC-004")
        decision.update({"decision": "exclude", "selected_role": None})
        plan["learning_units"][1]["contract_item_ids"].remove("RC-004")
        plan["learning_goal_mappings"][2]["supporting_item_ids"].remove("RC-004")
        plan["scope_summary"] = scope(plan["selection"]["selected_item_ids"])
        result, report = self.run_validator(plan)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("dependency.hard_dependencies", {error["code"] for error in report["errors"]})

    def test_stale_assessment_hash_fails(self) -> None:
        plan = load(self.plan_path)
        plan["profile_concept_assessment_binding"]["sha256"] = "0" * 64
        _, report = self.run_validator(plan)
        self.assertIn("concept_assessment.hash", {error["code"] for error in report["errors"]})

    def test_unmet_concept_requires_bridge_declaration(self) -> None:
        assessed = load(self.assessment_path)
        next(item for item in assessed["concept_assessments"] if item["concept_id"] == "vector-norms-and-normalization")["mastery"] = "missing"
        self.assessment_path.write_text(json.dumps(assessed, indent=2) + "\n", encoding="utf-8")
        plan = load(self.plan_path)
        plan["profile_concept_assessment_binding"]["sha256"] = digest(self.assessment_path)
        _, report = self.run_validator(plan)
        self.assertIn("bridges.coverage", {error["code"] for error in report["errors"]})

    def test_p1_cannot_bind_curriculum_model(self) -> None:
        baseline = load(self.baseline_path)
        plan = copy.deepcopy(baseline)
        profile = load(PROFILE)
        plan.update({
            "pathway_id": "power-iteration-cs-p1-v1",
            "condition": "P1",
            "profile_binding": {"profile_id": profile["profile_id"], "file": rel(PROFILE), "sha256": digest(PROFILE)},
            "baseline_pathway_binding": {"pathway_id": baseline["pathway_id"], "file": str(self.baseline_path.resolve()), "sha256": digest(self.baseline_path)},
            "generated_by": {"producer": "copy-p1-pathway", "producer_version": "1.0", "method": "deterministic_P0_copy", "generated_at": "2026-08-18T12:15:00Z"},
        })
        plan["source_authorities"]["curriculum_model"] = {
            "model_id": load(MODEL)["model_id"], "file": rel(MODEL), "sha256": digest(MODEL),
            "release_report_file": rel(MODEL_RELEASE), "release_report_sha256": digest(MODEL_RELEASE),
        }
        _, report = self.run_validator(plan)
        self.assertIn("P1.curriculum_model", {error["code"] for error in report["errors"]})

    def test_preflight_accepts_released_inputs_and_unified_p0(self) -> None:
        receipt = self.directory / "receipt.json"
        view = self.directory / "view.json"
        result = subprocess.run(
            [
                "python3", str(PREFLIGHT), "--workspace-root", str(ROOT),
                "--reference-contract", str(CONTRACT), "--curriculum-model", str(MODEL),
                "--learning-request", str(REQUEST), "--profile", str(PROFILE),
                "--baseline-pathway", str(self.baseline_path), "--output", str(receipt),
                "--view-output", str(view),
            ],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(load(receipt)["valid"])
        self.assertEqual(load(view)["topic"], load(REQUEST)["topic"])


if __name__ == "__main__":
    unittest.main()
