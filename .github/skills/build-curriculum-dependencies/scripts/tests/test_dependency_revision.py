from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
SCRIPTS = Path(__file__).resolve().parents[1]
PREPARE = SCRIPTS / "prepare_dependency_revision.py"
VALIDATE_MODEL = SCRIPTS / "validate_dependency_model.py"
VALIDATE_REVISION = SCRIPTS / "validate_dependency_revision.py"
CREATE_REVIEW = SCRIPTS / "create_dependency_review.py"
CONTRACT = REPO / "experiments/rq1/reference-contracts/power-iteration-v1/release/frozen_reference_contract.json"
PARENT = REPO / "curriculum-models/power-iteration-v1/candidate/contract-dependencies.json"
PARENT_REVIEW = REPO / "curriculum-models/power-iteration-v1/candidate/curriculum-dependency-review.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


class DependencyRevisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.output_dir = self.root / "candidate-v2"
        self.review_path = self.root / "completed-review.json"
        self.receipt_path = self.output_dir / "dependency-revision-receipt.json"
        self.candidate_path = self.output_dir / "contract-dependencies.json"
        self.validation_path = self.output_dir / "dependency-validation-report.json"
        self.revision_report_path = self.output_dir / "dependency-revision-validation-report.json"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_command(self, command: list[str], expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(command, text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def finalized_review(self) -> dict:
        review = copy.deepcopy(load(PARENT_REVIEW))
        review["review_status"] = "revision_required"
        review["reviewer"] = {
            "reviewer_id": "reviewer-01",
            "reviewer_role": "Curriculum Dependency Reviewer",
        }
        review["overall_review"] = {
            "decision": "revision_required",
            "reviewed_at": "2026-08-17T22:30:00+01:00",
            "comment": "Apply the bounded dependency corrections recorded below.",
        }
        for record in review["item_reviews"]:
            record["field_decisions"] = {
                field: "approved" for field in record["field_decisions"]
            }
            record["decision"] = "approved"
            record["comment"] = None
        for record in review["external_prerequisite_reviews"]:
            record["field_decisions"] = {
                field: "approved" for field in record["field_decisions"]
            }
            record["decision"] = "approved"
            record["comment"] = None

        item_fields = {
            "RC-006": [
                "hard_dependencies",
                "explanatory_dependencies",
                "fallback_when_explanatory_dependencies_omitted",
                "rationale_and_confidence",
            ],
            "RC-007": ["external_prerequisite_concept_ids", "rationale_and_confidence"],
            "RC-011": ["external_prerequisite_concept_ids"],
            "RC-017": ["external_prerequisite_concept_ids"],
            "RC-018": [
                "hard_dependencies",
                "explanatory_dependencies",
                "fallback_when_explanatory_dependencies_omitted",
                "rationale_and_confidence",
            ],
        }
        for record in review["item_reviews"]:
            if record["item_id"] in item_fields:
                for field in item_fields[record["item_id"]]:
                    record["field_decisions"][field] = "revision_required"
                record["decision"] = "revision_required"
                record["comment"] = f"Revise {record['item_id']} within the marked fields."

        concept_fields = {
            "orthogonality-and-projection": ["supports_item_ids", "content_boundary_and_rationale"],
            "determinants-characteristic-polynomials": ["need_type", "content_boundary_and_rationale"],
            "iterative-algorithms-and-stopping": [
                "need_type",
                "supports_item_ids",
                "bridge_candidate_id",
                "content_boundary_and_rationale",
            ],
        }
        for record in review["external_prerequisite_reviews"]:
            if record["concept_id"] in concept_fields:
                for field in concept_fields[record["concept_id"]]:
                    record["field_decisions"][field] = "revision_required"
                record["decision"] = "revision_required"
                record["comment"] = f"Revise {record['concept_id']} within the marked fields."
        return review

    def revised_candidate(self) -> dict:
        candidate = copy.deepcopy(load(PARENT))
        candidate["model_id"] = "power-iteration-dependencies-v2"
        candidate["builder"]["agent_version"] = "1.1"
        candidate["builder"]["skill_version"] = "1.1"
        candidate["builder"]["generated_at"] = "2026-08-17T23:00:00Z"
        items = {item["item_id"]: item for item in candidate["items"]}

        items["RC-006"]["hard_dependencies"].remove("RC-005")
        items["RC-006"]["explanatory_dependencies"] = ["RC-005"]
        items["RC-006"]["fallback_when_explanatory_dependencies_omitted"] = {
            "allowed": True,
            "instruction": "Introduce A^k x_0 as repeated matrix-vector products without the normalised update.",
        }
        items["RC-006"]["rationale"] = [
            "The spectral basis and magnitude gap are necessary; the normalised update supplies application context."
        ]
        items["RC-007"]["external_prerequisite_concept_ids"] = ["orthogonality-and-projection"]
        items["RC-007"]["rationale"].append(
            "Minimal projection knowledge remains necessary when the full spectral derivation is omitted."
        )
        items["RC-011"]["external_prerequisite_concept_ids"] = []
        items["RC-017"]["external_prerequisite_concept_ids"].remove("iterative-algorithms-and-stopping")
        items["RC-018"]["hard_dependencies"].remove("RC-004")
        items["RC-018"]["explanatory_dependencies"] = ["RC-002", "RC-004", "RC-014"]
        items["RC-018"]["fallback_when_explanatory_dependencies_omitted"] = {
            "allowed": True,
            "instruction": "Supply the exact eigenvalues and compare their magnitudes locally before checking the estimate and residual.",
        }
        items["RC-018"]["rationale"] = [
            "The worked result needs eigenpair, Rayleigh, residual, and runtime items; general dominance theory is explanatory."
        ]

        concepts = {
            concept["concept_id"]: concept
            for concept in candidate["external_prerequisite_concepts"]
        }
        concepts["orthogonality-and-projection"]["supports_item_ids"] = [
            "RC-003", "RC-006", "RC-007", "RC-012"
        ]
        concepts["orthogonality-and-projection"]["content_boundary"] = (
            "Define inner products, orthogonality, unit vectors, and scalar projection coefficients; exclude the spectral theorem."
        )
        concepts["orthogonality-and-projection"]["rationale"] = (
            "The affected items use orthogonality or a non-zero projection coefficient."
        )
        concepts["determinants-characteristic-polynomials"]["need_type"] = "required"
        concepts["determinants-characteristic-polynomials"]["rationale"] = (
            "When RC-002 is selected, determinant knowledge is required to interpret its characteristic equation."
        )
        candidate["external_prerequisite_concepts"] = [
            concept for concept in candidate["external_prerequisite_concepts"]
            if concept["concept_id"] != "iterative-algorithms-and-stopping"
        ]
        return candidate

    def prepare(self, review: dict | None = None, expected: int = 0) -> None:
        write(self.review_path, review if review is not None else self.finalized_review())
        self.run_command(
            [
                sys.executable,
                str(PREPARE),
                "--workspace-root", str(REPO),
                "--contract", str(CONTRACT),
                "--parent-candidate", str(PARENT),
                "--parent-review", str(self.review_path),
                "--output", str(self.receipt_path),
            ],
            expected,
        )

    def validate_revised(self, candidate: dict, expected: int = 0) -> dict:
        write(self.candidate_path, candidate)
        self.run_command(
            [
                sys.executable,
                str(VALIDATE_MODEL),
                "--workspace-root", str(REPO),
                "--contract", str(CONTRACT),
                "--candidate", str(self.candidate_path),
                "--output", str(self.validation_path),
            ]
        )
        self.run_command(
            [
                sys.executable,
                str(VALIDATE_REVISION),
                "--workspace-root", str(REPO),
                "--parent-candidate", str(PARENT),
                "--parent-review", str(self.review_path),
                "--revision-receipt", str(self.receipt_path),
                "--candidate", str(self.candidate_path),
                "--dependency-validation-report", str(self.validation_path),
                "--output", str(self.revision_report_path),
            ],
            expected,
        )
        return load(self.revision_report_path)

    def test_accepts_bounded_revision_and_creates_new_pending_review(self) -> None:
        self.prepare()
        report = self.validate_revised(self.revised_candidate())
        self.assertTrue(report["valid"])
        self.assertEqual(report["metrics"]["removed_concept_ids"], ["iterative-algorithms-and-stopping"])
        review_v2_path = self.output_dir / "curriculum-dependency-review.json"
        self.run_command(
            [
                sys.executable,
                str(CREATE_REVIEW),
                "--workspace-root", str(REPO),
                "--candidate", str(self.candidate_path),
                "--validation-report", str(self.validation_path),
                "--revision-receipt", str(self.receipt_path),
                "--revision-validation-report", str(self.revision_report_path),
                "--output", str(review_v2_path),
            ]
        )
        review_v2 = load(review_v2_path)
        self.assertEqual(review_v2["review_status"], "pending")
        self.assertIsNotNone(review_v2["revision_binding"])
        self.assertEqual(
            review_v2["revision_binding"]["parent_candidate_sha256"],
            load(self.receipt_path)["parent_candidate"]["sha256"],
        )

    def test_rejects_pending_parent_review(self) -> None:
        review = self.finalized_review()
        review["review_status"] = "pending"
        review["reviewer"] = {"reviewer_id": None, "reviewer_role": None}
        review["overall_review"] = {
            "decision": "pending",
            "reviewed_at": None,
            "comment": None,
        }
        self.prepare(review, expected=1)

    def test_rejects_stale_parent_candidate_binding(self) -> None:
        review = self.finalized_review()
        review["candidate_binding"]["candidate_sha256"] = "0" * 64
        self.prepare(review, expected=1)

    def test_rejects_change_to_unreviewed_item_field(self) -> None:
        self.prepare()
        candidate = self.revised_candidate()
        candidate["items"][0]["recommended_neighbours"].append("RC-005")
        report = self.validate_revised(candidate, expected=1)
        self.assertTrue(any(error["code"] == "scope.item_field" for error in report["errors"]))

    def test_rejects_revision_field_left_unchanged(self) -> None:
        self.prepare()
        candidate = self.revised_candidate()
        parent = load(PARENT)
        parent_rc006 = next(item for item in parent["items"] if item["item_id"] == "RC-006")
        rc006 = next(item for item in candidate["items"] if item["item_id"] == "RC-006")
        rc006["rationale"] = parent_rc006["rationale"]
        report = self.validate_revised(candidate, expected=1)
        self.assertTrue(any(error["code"] == "scope.item_unapplied" for error in report["errors"]))

    def test_rejects_forged_revision_scope(self) -> None:
        self.prepare()
        receipt = load(self.receipt_path)
        receipt["revision_scope"]["item_changes"].append(
            {
                "item_id": "RC-001",
                "fields": ["recommended_neighbours"],
                "comment": "Unauthorized expansion of the reviewed scope.",
            }
        )
        write(self.receipt_path, receipt)
        report = self.validate_revised(self.revised_candidate(), expected=1)
        self.assertTrue(any(error["code"] == "receipt.item_scope" for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
