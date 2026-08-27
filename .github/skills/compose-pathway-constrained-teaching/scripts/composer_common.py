#!/usr/bin/env python3
"""Shared deterministic helpers for the RQ2 teaching Composer."""

from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
from typing import Any


class ComposerError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise ComposerError(code, message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), "file.missing", f"missing file: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComposerError("json.invalid", f"cannot read JSON {path}: {exc}") from exc
    require(isinstance(value, dict), "json.root", f"JSON root must be an object: {path}")
    return value


def resolve(root: Path, raw: str | Path) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def display(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binding(root: Path, path: Path) -> dict[str, str]:
    return {"file": display(root, path), "sha256": digest(path)}


def verify_binding(root: Path, value: Any, label: str) -> tuple[Path, dict[str, Any]]:
    require(isinstance(value, dict), f"{label}.binding", f"{label} binding must be an object")
    require(isinstance(value.get("file"), str), f"{label}.file", f"{label} binding needs file")
    path = resolve(root, value["file"])
    require(path.is_file(), f"{label}.missing", f"{label} file is missing: {path}")
    require(value.get("sha256") == digest(path), f"{label}.hash", f"{label} SHA-256 is stale")
    return path, load_json(path)


def verify_timestamp(value: str, label: str) -> None:
    require(isinstance(value, str) and value, f"{label}.missing", f"{label} is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ComposerError(f"{label}.format", f"{label} must be an ISO-8601 timestamp") from exc
    require(parsed.tzinfo is not None, f"{label}.timezone", f"{label} must include a timezone")


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
DISPLAY_MATH_RE = re.compile(r"\$\$.*?\$\$|\\\[.*?\\\]", re.DOTALL)
INLINE_MATH_RE = re.compile(r"(?<!\\)\$(?!\$).*?(?<!\\)\$", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
ENGLISH_WORD_RE = re.compile(r"[A-Za-z]+(?:['’-][A-Za-z]+)*|\d+(?:\.\d+)?")


def count_english_prose_words(content: str) -> int:
    """Match the RQ1 english_prose_v1 counting boundary."""
    text = FENCED_CODE_RE.sub(" ", content)
    text = HTML_COMMENT_RE.sub(" ", text)
    text = DISPLAY_MATH_RE.sub(" ", text)
    text = INLINE_MATH_RE.sub(" ", text)
    text = INLINE_CODE_RE.sub(" ", text)
    return len(ENGLISH_WORD_RE.findall(text))
