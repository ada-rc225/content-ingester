#!/usr/bin/env python3
"""Capture or safely apply an independent human review record."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any


APPROVAL_STATEMENT = (
    "I approve this contract as the frozen generation reference for the identified source version."
)
FREEZE_NOTE = "Record the SHA-256 of this complete frozen contract outside this file before generation."
FINAL_ITEM_DECISIONS = {"approved_as_written", "approved_with_correction", "excluded"}


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def review_basis_sha256(contract: dict[str, Any]) -> str:
    """Hash generation content while excluding mutable human-review decisions."""
    basis = copy.deepcopy(contract)
    basis["lifecycle_status"] = "candidate"
    basis["approval"] = None
    for item in basis.get("contract_items", []):
        for check in item.get("semantic_checks", []):
            check["review_status"] = "proposed"
        item["review"] = {
            "source_fidelity": "unreviewed",
            "mathematical_status": "unreviewed",
            "algorithmic_status": "unreviewed",
            "decision": "pending",
            "reviewer_notes": [],
        }
    for issue in basis.get("candidate_source_issues", []):
        issue["resolution"] = "pending_review"
        issue["approved_generation_content"] = None
    canonical = json.dumps(basis, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def capture_review(contract: dict[str, Any]) -> dict[str, Any]:
    approval = contract.get("approval")
    reviewer = None
    if isinstance(approval, dict):
        reviewer = {
            key: approval[key]
            for key in ("reviewer_id", "reviewer_role", "reviewed_at")
            if key in approval
        }
    return {
        "schema_version": "1.0",
        "contract_binding": {
            "contract_id": contract.get("contract_id"),
            "contract_version": contract.get("contract_version"),
            "review_basis_sha256": review_basis_sha256(contract),
        },
        "review_status": "approved" if contract.get("lifecycle_status") == "frozen" else "in_progress",
        "reviewer": reviewer,
        "semantic_check_reviews": [
            {"check_id": check.get("check_id"), "review_status": check.get("review_status")}
            for item in contract.get("contract_items", [])
            for check in item.get("semantic_checks", [])
        ],
        "item_reviews": [
            {"item_id": item.get("item_id"), **copy.deepcopy(item.get("review", {}))}
            for item in contract.get("contract_items", [])
        ],
        "source_issue_reviews": [
            {
                "issue_id": issue.get("issue_id"),
                "resolution": issue.get("resolution"),
                "approved_generation_content": copy.deepcopy(issue.get("approved_generation_content")),
            }
            for issue in contract.get("candidate_source_issues", [])
        ],
        "final_approval": copy.deepcopy(approval),
    }


def keyed(records: Any, key: str, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(records, list):
        raise ValueError(f"{label} must be an array")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get(key), str):
            raise ValueError(f"invalid {label} record")
        record_id = record[key]
        if record_id in result:
            raise ValueError(f"duplicate {label} ID: {record_id}")
        result[record_id] = record
    return result


def apply_review(contract: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    binding = review.get("contract_binding")
    if not isinstance(binding, dict):
        raise ValueError("human review has no contract_binding")
    for field in ("contract_id", "contract_version"):
        if binding.get(field) != contract.get(field):
            raise ValueError(f"human review {field} does not match contract")
    actual_basis = review_basis_sha256(contract)
    if binding.get("review_basis_sha256") != actual_basis:
        raise ValueError("human review basis hash does not match contract generation content")

    item_reviews = keyed(review.get("item_reviews"), "item_id", "item review")
    contract_items = keyed(contract.get("contract_items"), "item_id", "contract item")
    if set(item_reviews) != set(contract_items):
        raise ValueError("human review and contract item ID sets differ")

    check_reviews = keyed(review.get("semantic_check_reviews"), "check_id", "semantic check review")
    contract_checks = {
        check["check_id"]: check
        for item in contract.get("contract_items", [])
        for check in item.get("semantic_checks", [])
    }
    if set(check_reviews) != set(contract_checks):
        raise ValueError("human review and contract semantic-check ID sets differ")

    issue_reviews = keyed(review.get("source_issue_reviews"), "issue_id", "source issue review")
    contract_issues = keyed(contract.get("candidate_source_issues"), "issue_id", "source issue")
    if set(issue_reviews) != set(contract_issues):
        raise ValueError("human review and contract source-issue ID sets differ")

    merged = copy.deepcopy(contract)
    for item in merged["contract_items"]:
        item_id = item["item_id"]
        item["review"] = {
            key: copy.deepcopy(value)
            for key, value in item_reviews[item_id].items()
            if key != "item_id"
        }
        for check in item.get("semantic_checks", []):
            check["review_status"] = check_reviews[check["check_id"]]["review_status"]
    for issue in merged.get("candidate_source_issues", []):
        issue_review = issue_reviews[issue["issue_id"]]
        issue["resolution"] = issue_review["resolution"]
        issue["approved_generation_content"] = copy.deepcopy(
            issue_review.get("approved_generation_content")
        )

    review_status = review.get("review_status")
    if review_status == "in_progress":
        merged["lifecycle_status"] = "under_review"
        merged["approval"] = None
    elif review_status == "approved":
        reviewer = review.get("reviewer")
        final_approval = review.get("final_approval")
        if not isinstance(reviewer, dict):
            raise ValueError("approved human review requires reviewer identity")
        if not isinstance(final_approval, dict):
            raise ValueError("approved human review requires final_approval")
        for field in ("reviewer_id", "reviewer_role", "reviewed_at"):
            if reviewer.get(field) != final_approval.get(field):
                raise ValueError(f"reviewer and final_approval differ for {field}")
        if final_approval.get("approval_statement") != APPROVAL_STATEMENT:
            raise ValueError("final_approval has an invalid approval_statement")
        if final_approval.get("freeze_note") != FREEZE_NOTE:
            raise ValueError("final_approval has an invalid freeze_note")
        if any(record.get("review_status") != "approved" for record in check_reviews.values()):
            raise ValueError("approved human review requires every semantic check to be approved")
        for item_id, item_review in item_reviews.items():
            if item_review.get("source_fidelity") not in {"verified", "mismatch"}:
                raise ValueError(f"approved human review has incomplete source fidelity: {item_id}")
            for field in ("mathematical_status", "algorithmic_status"):
                if item_review.get(field) not in {"verified_correct", "source_issue", "not_applicable"}:
                    raise ValueError(f"approved human review has incomplete {field}: {item_id}")
            if item_review.get("decision") not in FINAL_ITEM_DECISIONS:
                raise ValueError(f"approved human review has no final decision: {item_id}")
        if any(record.get("resolution") == "pending_review" for record in issue_reviews.values()):
            raise ValueError("approved human review contains a pending source issue")
        merged["lifecycle_status"] = "frozen"
        merged["approval"] = copy.deepcopy(final_approval)
    else:
        raise ValueError("review_status must be in_progress or approved")
    return merged


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    capture = subparsers.add_parser("capture", help="Capture review fields from a contract")
    capture.add_argument("--contract", required=True)
    capture.add_argument("--output", required=True)
    apply_parser = subparsers.add_parser("apply", help="Apply review to a separate contract file")
    apply_parser.add_argument("--contract", required=True)
    apply_parser.add_argument("--review", required=True)
    apply_parser.add_argument("--output", required=True)
    args = parser.parse_args()

    try:
        if args.command == "capture":
            contract_path = Path(args.contract).resolve()
            output_path = Path(args.output).resolve()
            if output_path == contract_path:
                raise ValueError("review output must not overwrite the contract")
            write_json(output_path, capture_review(load_json(contract_path)))
            print(f"Captured human review to {output_path}")
        else:
            contract_path = Path(args.contract).resolve()
            review_path = Path(args.review).resolve()
            output_path = Path(args.output).resolve()
            if output_path in {contract_path, review_path}:
                raise ValueError("merged output must be a separate file")
            write_json(output_path, apply_review(load_json(contract_path), load_json(review_path)))
            print(f"Applied human review to {output_path}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
