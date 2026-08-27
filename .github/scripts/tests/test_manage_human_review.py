#!/usr/bin/env python3
"""Unit tests for manage_human_review.py."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "manage_human_review.py"
SPEC = importlib.util.spec_from_file_location("manage_human_review", SCRIPT)
assert SPEC and SPEC.loader
REVIEW = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = REVIEW
SPEC.loader.exec_module(REVIEW)


class HumanReviewTests(unittest.TestCase):
    def contract(self) -> dict:
        return {
            "contract_id": "topic",
            "contract_version": "1.0.0",
            "lifecycle_status": "under_review",
            "approval": None,
            "contract_items": [
                {
                    "item_id": "RC-001",
                    "canonical_statement": "A source-grounded claim.",
                    "semantic_checks": [
                        {"check_id": "CHK-001", "review_status": "approved"}
                    ],
                    "review": {
                        "source_fidelity": "verified",
                        "mathematical_status": "verified_correct",
                        "algorithmic_status": "not_applicable",
                        "decision": "approved_as_written",
                        "reviewer_notes": ["Reviewed."],
                    },
                }
            ],
            "candidate_source_issues": [],
        }

    def test_capture_apply_round_trip(self):
        contract = self.contract()
        review = REVIEW.capture_review(contract)
        self.assertEqual(REVIEW.apply_review(contract, review), contract)

    def test_basis_hash_ignores_review_fields(self):
        contract = self.contract()
        original_hash = REVIEW.review_basis_sha256(contract)
        contract["contract_items"][0]["review"]["reviewer_notes"] = ["Changed note."]
        contract["contract_items"][0]["semantic_checks"][0]["review_status"] = "proposed"
        self.assertEqual(REVIEW.review_basis_sha256(contract), original_hash)

    def test_basis_hash_rejects_generation_content_change(self):
        contract = self.contract()
        review = REVIEW.capture_review(contract)
        contract["contract_items"][0]["canonical_statement"] = "Changed claim."
        with self.assertRaisesRegex(ValueError, "basis hash"):
            REVIEW.apply_review(contract, review)

    def test_approved_review_requires_matching_reviewer_identity(self):
        contract = self.contract()
        review = REVIEW.capture_review(contract)
        review["review_status"] = "approved"
        review["reviewer"] = {
            "reviewer_id": "reviewer-1",
            "reviewer_role": "Mathematics reviewer",
            "reviewed_at": "2026-08-10T12:00:00+01:00",
        }
        review["final_approval"] = {
            **review["reviewer"],
            "reviewer_id": "different-reviewer",
            "approval_statement": REVIEW.APPROVAL_STATEMENT,
            "freeze_note": REVIEW.FREEZE_NOTE,
        }
        with self.assertRaisesRegex(ValueError, "differ for reviewer_id"):
            REVIEW.apply_review(contract, review)


if __name__ == "__main__":
    unittest.main()
