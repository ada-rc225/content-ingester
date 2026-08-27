#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PROTOCOL_ID = "RQ2-EVAL-v1"
PRIMARY_DIMENSIONS = (
    "disciplinary_framing_appropriateness",
    "prerequisite_match",
    "context_boundary_awareness",
    "sequence_quality",
)
BUNDLE_FILES = (
    "evaluation-manifest.json",
    "lesson.md",
    "learner-profile.json",
    "learning-request.json",
    "frozen-reference-contract.json",
    "pathway-evidence.json",
    "structural-validation-evidence.json",
)
ALGORITHM_ITEM_TYPES = {"algorithm_rule", "code_semantics"}


class EvaluationError(RuntimeError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvaluationError(f"expected a JSON object: {path}")
    return value


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(root: Path, value: str | None) -> Path:
    if not isinstance(value, str) or not value:
        raise EvaluationError("missing file path")
    path = Path(value)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def binding(root: Path, path: Path) -> dict[str, str]:
    return {"file": relative(root, path), "sha256": sha256(path)}


def verify_binding(root: Path, record: dict[str, Any], label: str) -> Path:
    path = resolve(root, record.get("file"))
    if not path.is_file():
        raise EvaluationError(f"{label} file does not exist: {path}")
    expected = record.get("sha256")
    actual = sha256(path)
    if expected != actual:
        raise EvaluationError(f"{label} SHA-256 is stale: expected {expected}, got {actual}")
    return path


def exact_lesson_excerpt(lesson: str, excerpt: str) -> bool:
    return bool(excerpt) and excerpt in lesson


def has_condition_component(path: Path) -> bool:
    return any(part.lower() in {"p0", "p1", "p2"} for part in path.parts)


def selected_contract_items(bundle: Path) -> tuple[list[str], dict[str, dict[str, Any]]]:
    pathway = load_json(bundle / "pathway-evidence.json")
    contract = load_json(bundle / "frozen-reference-contract.json")
    selected = pathway.get("selected_item_ids")
    if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
        raise EvaluationError("pathway-evidence selected_item_ids is invalid")
    items = {
        item.get("item_id"): item
        for item in contract.get("contract_items", [])
        if isinstance(item, dict) and isinstance(item.get("item_id"), str)
    }
    if not set(selected).issubset(items):
        raise EvaluationError("pathway selects items absent from the Frozen Contract")
    return selected, items

