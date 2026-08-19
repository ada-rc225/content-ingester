#!/usr/bin/env python3
"""Create a compact, fully pending human-review form for a valid bridge library."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


FIELDS = (
    "correctness",
    "source_quality",
    "content_boundary",
    "dependency_support",
    "pedagogical_sufficiency",
)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return str(path.resolve())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--validation-report", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(args.workspace_root).resolve()
    candidate_path = args.candidate.resolve()
    validation_path = args.validation_report.resolve()
    output_path = args.output.resolve()
    if output_path.exists():
        print(f"ERROR [output.exists]: refusing to overwrite {output_path}")
        return 1
    try:
        candidate = load_object(candidate_path)
        validation = load_object(validation_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR [input.read]: {exc}")
        return 1
    if (
        validation.get("valid") is not True
        or validation.get("error_count") != 0
    ):
        print("ERROR [validation.status]: bridge-library validation did not pass")
        return 1
    inputs = validation.get("inputs", {})
    if (
        inputs.get("candidate") != display(candidate_path, root)
        or inputs.get("candidate_sha256") != digest(candidate_path)
    ):
        print("ERROR [validation.binding]: candidate changed after validation")
        return 1
    review = {
        "schema_version": "1.0",
        "review_id": f"{candidate['library_id']}-review-v1",
        "review_status": "pending",
        "candidate_binding": {
            "library_id": candidate["library_id"],
            "candidate_file": display(candidate_path, root),
            "candidate_sha256": digest(candidate_path),
            "validation_report_file": display(validation_path, root),
            "validation_report_sha256": digest(validation_path),
        },
        "template_generator": {
            "agent": "grounded-bridge-library-builder",
            "agent_version": "1.0",
            "skill": "build-grounded-bridge-library",
            "skill_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(
                timespec="seconds"
            ).replace("+00:00", "Z"),
        },
        "reviewer": {"reviewer_id": None, "reviewer_role": None},
        "bridge_reviews": [
            {
                "bridge_contract_id": bridge["bridge_contract_id"],
                "bridge_candidate_id": bridge["bridge_candidate_id"],
                "concept_id": bridge["concept_id"],
                "requested_by_profile_ids":
                    bridge["requested_by_profile_ids"],
                "supports_item_ids": bridge["supports_item_ids"],
                "content_block_ids": [
                    item["content_id"]
                    for item in bridge["teaching_content"]
                ],
                "source_ids": [
                    source["source_id"] for source in bridge["sources"]
                ],
                "field_decisions": {
                    field: "pending" for field in FIELDS
                },
                "decision": "pending",
                "comment": None,
            }
            for bridge in candidate["bridges"]
        ],
        "overall_review": {
            "decision": "pending",
            "reviewed_at": None,
            "comment": None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(review, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"CREATED: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
