#!/usr/bin/env python3
"""Build a deterministic source-unit and display-formula inventory for Markdown."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
DISPLAY_DELIMITER_RE = re.compile(r"^\s*\$\$\s*$")
EXERCISE_HEADING_RE = re.compile(r"\b(?:exercises?|problems)\b", re.IGNORECASE)
DERIVATION_HEADING_RE = re.compile(r"\bproof\b", re.IGNORECASE)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_workspace_path(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"source path escapes workspace root: {path}") from exc


def build_inventory(source_path: Path, workspace_root: Path, source_id: str) -> dict:
    text = source_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    heading_stack: list[tuple[int, str, bool, bool]] = []
    source_units: list[dict] = []
    formulas: list[dict] = []

    def heading_path() -> list[str]:
        return [title for _, title, _, _ in heading_stack]

    def scope_role() -> str:
        if any(is_exercise for _, _, is_exercise, _ in heading_stack):
            return "exercise"
        if any(is_derivation for _, _, _, is_derivation in heading_stack):
            return "derivation"
        return "core_material"

    def add_unit(start_index: int, end_index: int, unit_type: str, role_override: str | None = None) -> str:
        source_unit_id = f"SU-{len(source_units) + 1:03d}"
        exact_text = "".join(lines[start_index : end_index + 1]).rstrip("\r\n")
        source_units.append(
            {
                "source_unit_id": source_unit_id,
                "unit_type": unit_type,
                "scope_role": role_override or scope_role(),
                "heading_path": heading_path(),
                "locator": {
                    "line_start": start_index + 1,
                    "line_end": end_index + 1,
                },
                "exact_text": exact_text,
            }
        )
        return source_unit_id

    index = 0
    while index < len(lines):
        stripped = lines[index].rstrip("\r\n")
        if not stripped.strip():
            index += 1
            continue

        heading_match = HEADING_RE.match(stripped)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group(2)
            while heading_stack and heading_stack[-1][0] >= level:
                heading_stack.pop()
            heading_stack.append(
                (
                    level,
                    title,
                    EXERCISE_HEADING_RE.search(title) is not None,
                    DERIVATION_HEADING_RE.search(title) is not None,
                )
            )
            add_unit(index, index, "heading")
            index += 1
            continue

        if DISPLAY_DELIMITER_RE.match(stripped):
            end_index = index + 1
            while end_index < len(lines) and not DISPLAY_DELIMITER_RE.match(
                lines[end_index].rstrip("\r\n")
            ):
                end_index += 1
            if end_index >= len(lines):
                raise ValueError(f"unclosed display-math block beginning at line {index + 1}")
            previous_text = source_units[-1]["exact_text"] if source_units else ""
            role_override = (
                "derivation"
                if scope_role() == "core_material" and re.search(r"\bproof outline\b", previous_text, re.IGNORECASE)
                else None
            )
            source_unit_id = add_unit(index, end_index, "display_math", role_override)
            exact_block = source_units[-1]["exact_text"]
            exact_latex = "".join(lines[index + 1 : end_index]).strip("\r\n")
            if not exact_latex.strip():
                raise ValueError(f"empty display-math block at lines {index + 1}-{end_index + 1}")
            formulas.append(
                {
                    "formula_id": f"FM-{len(formulas) + 1:03d}",
                    "source_unit_id": source_unit_id,
                    "scope_role": source_units[-1]["scope_role"],
                    "heading_path": heading_path(),
                    "locator": {
                        "line_start": index + 1,
                        "line_end": end_index + 1,
                    },
                    "exact_latex": exact_latex,
                    "exact_block": exact_block,
                }
            )
            index = end_index + 1
            continue

        end_index = index
        while end_index + 1 < len(lines):
            next_line = lines[end_index + 1].rstrip("\r\n")
            if not next_line.strip() or HEADING_RE.match(next_line) or DISPLAY_DELIMITER_RE.match(next_line):
                break
            end_index += 1
        add_unit(index, end_index, "paragraph")
        index = end_index + 1

    relative_path = relative_workspace_path(source_path, workspace_root)
    return {
        "schema_version": "1.0",
        "inventory_id": f"{source_id}-grounding-inventory",
        "source": {
            "source_id": source_id,
            "path": relative_path,
            "format": "markdown",
            "sha256": sha256(source_path),
        },
        "scope_policy": {
            "included_roles": ["core_material", "derivation"],
            "excluded_roles": ["exercise"],
            "exercise_detection": "markdown heading contains exercise or plural problems",
        },
        "source_units": source_units,
        "formulas": formulas,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--source", required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = workspace_root / source_path
    source_path = source_path.resolve()
    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = workspace_root / output_path

    try:
        inventory = build_inventory(source_path, workspace_root, args.source_id)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    core_formulas = sum(
        formula["scope_role"] == "core_material" for formula in inventory["formulas"]
    )
    derivation_formulas = sum(
        formula["scope_role"] == "derivation" for formula in inventory["formulas"]
    )
    exercise_formulas = len(inventory["formulas"]) - core_formulas - derivation_formulas
    print(
        f"Wrote {output_path}: {len(inventory['source_units'])} source units, "
        f"{core_formulas} core formulas, {derivation_formulas} derivation formulas, "
        f"{exercise_formulas} excluded exercise formulas"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
