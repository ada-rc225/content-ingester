#!/usr/bin/env python3
"""Create an exact profile-bound P1 copy of one validated unified P0 plan."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any

from validate_pathway_plan import Validator


REPO_ROOT = Path(__file__).resolve().parents[3]
AUTHORITY_SCRIPTS = REPO_ROOT / ".github/skills/plan-adaptive-curriculum-pathways/scripts"
import sys

sys.path.insert(0, str(AUTHORITY_SCRIPTS))

from pathway_authorities import (  # noqa: E402
    AuthorityError,
    display_path,
    load_object,
    resolve_path,
    sha256,
    verify_profile,
)


PATHWAY_ID_RE = re.compile(r"^[A-Za-z0-9]+(?:[-_.][A-Za-z0-9]+)*$")


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise AuthorityError(code, message)


def validate_timestamp(value: str) -> None:
    require(value.endswith("Z"), "generated_at.format", "--generated-at must be a UTC ISO-8601 timestamp ending in Z")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError("generated_at.format", "--generated-at is not a valid ISO-8601 timestamp") from exc


def build_copy(
    root: Path,
    p0_path: Path,
    profile_path: Path,
    pathway_id: str,
    generated_at: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    p0 = load_object(p0_path)
    require(p0.get("condition") == "P0", "P0.condition", "--p0 must identify a unified P0 plan")
    p0_validator = Validator(root, "pilot", None)
    p0_validator.validate(p0)
    require(not p0_validator.errors, "P0.validation", f"P0 failed unified validation: {p0_validator.errors}")

    request_binding = p0.get("learning_request_binding")
    require(isinstance(request_binding, dict), "P0.request", "P0 learning-request binding is missing")
    request_path = resolve_path(root, request_binding.get("file"))
    require(request_path is not None and request_path.is_file(), "P0.request_file", "P0 learning-request file is missing")
    request = load_object(request_path)
    profile = verify_profile(root, profile_path, request)

    p1 = copy.deepcopy(p0)
    p1["pathway_id"] = pathway_id
    p1["condition"] = "P1"
    p1["profile_binding"] = {
        "profile_id": profile["profile_id"],
        "file": display_path(profile_path, root),
        "sha256": sha256(profile_path),
    }
    p1["baseline_pathway_binding"] = {
        "pathway_id": p0["pathway_id"],
        "file": display_path(p0_path, root),
        "sha256": sha256(p0_path),
    }
    p1["generated_by"] = {
        "producer": "copy-p1-pathway",
        "producer_version": "1.0",
        "method": "deterministic_P0_copy",
        "generated_at": generated_at,
    }

    validator = Validator(root, "pilot", None)
    validator.validate(p1)
    require(not validator.errors, "output.validation", f"P1 copy failed unified validation: {validator.errors}")
    receipt = {
        "schema_version": "1.0",
        "operation": "deterministic-p1-copy-v1",
        "inputs": {
            "P0_pathway": {"file": display_path(p0_path, root), "sha256": sha256(p0_path)},
            "learner_profile": {"file": display_path(profile_path, root), "sha256": sha256(profile_path)},
        },
        "P0_pathway_id": p0["pathway_id"],
        "P1_pathway_id": pathway_id,
        "profile_id": profile["profile_id"],
        "controlled_copy_policy": {
            "exact_P0_fields": [
                "topic", "source_authorities", "profile_concept_assessment_binding",
                "learning_request_binding", "selection_authority", "selection",
                "learning_goal_mappings", "learning_units", "instruction_sequence",
                "bridge_requirements", "pathway_changes", "scope_summary",
                "rendering_policy", "plan_status",
            ],
            "changed_fields": [
                "pathway_id", "condition", "profile_binding",
                "baseline_pathway_binding", "generated_by",
            ],
        },
        "generated_at": generated_at,
    }
    return p1, receipt


def write_pair(output: Path, receipt_path: Path, plan: dict[str, Any], receipt: dict[str, Any], root: Path) -> None:
    require(output != receipt_path, "output.collision", "plan and receipt outputs must differ")
    require(not output.exists(), "output.exists", f"refusing to overwrite {output}")
    require(not receipt_path.exists(), "receipt.exists", f"refusing to overwrite {receipt_path}")
    output.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    receipt["output"] = {"file": display_path(output, root), "sha256": sha256(output)}
    try:
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    except Exception:
        output.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--p0", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--pathway-id", required=True)
    parser.add_argument("--generated-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    root = Path(args.workspace_root).resolve()
    try:
        require(bool(PATHWAY_ID_RE.fullmatch(args.pathway_id)), "pathway_id.format", "--pathway-id has an invalid format")
        validate_timestamp(args.generated_at)
        plan, receipt = build_copy(
            root, args.p0.resolve(), args.profile.resolve(),
            args.pathway_id, args.generated_at,
        )
        write_pair(args.output.resolve(), args.receipt.resolve(), plan, receipt, root)
    except (AuthorityError, OSError, KeyError, TypeError, ValueError) as exc:
        code = exc.code if isinstance(exc, AuthorityError) else "copy.input"
        print(f"ERROR [{code}]: {exc}")
        return 1
    print(f"PASS: wrote exact profile-bound P1 copy to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
