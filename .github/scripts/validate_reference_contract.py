#!/usr/bin/env python3
"""Deterministically validate source evidence in a grounding contract.

This validator deliberately uses only the Python standard library. It checks
properties that must not be delegated to an LLM: source identity, exact
substring evidence, line-range containment, canonical-LaTeX evidence coverage,
structural-only evidence, grounding-inventory coverage, and identifier/reference integrity. Version 3
supports line-addressable UTF-8 Markdown, text, and code sources.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ITEM_ID_RE = re.compile(r"^RC-[0-9]{3,}$")
ISSUE_ID_RE = re.compile(r"^ISSUE-[0-9]{3,}$")
CHECK_ID_RE = re.compile(r"^CHK-[0-9]{3,}$")
SOURCE_UNIT_ID_RE = re.compile(r"^SU-[0-9]{3,}$")
FORMULA_ID_RE = re.compile(r"^FM-[0-9]{3,}$")
LINE_RANGE_RE = re.compile(
    r"\blines?\s+([0-9]+)(?:\s*[-–—]\s*([0-9]+))?\b",
    re.IGNORECASE,
)
LINE_LOCATOR_TYPES = {
    "markdown_heading_lines",
    "text_lines",
    "code_lines",
}
TEXT_FORMATS = {"markdown", "text", "code"}
MARKDOWN_TOC_ENTRY_RE = re.compile(
    r"^[0-9]+[.)]\s+\[[^\]]+\](?:\(#[^)]+\))?$"
)


@dataclass(frozen=True)
class Finding:
    code: str
    location: str
    message: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"file does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON in {path}: line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def resolve_workspace_path(root: Path, raw_path: str) -> Path:
    root = root.resolve()
    candidate = Path(raw_path)
    resolved = (candidate if candidate.is_absolute() else root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"path escapes workspace root: {raw_path}") from exc
    return resolved


def line_region(text: str, start: int, end: int) -> str | None:
    lines = text.splitlines(keepends=True)
    if start < 1 or end < start or end > len(lines):
        return None
    return "".join(lines[start - 1 : end])


def normalize_latex(value: str) -> str:
    """Normalize presentation-only differences without claiming equivalence."""
    normalized = unicodedata.normalize("NFKC", value)
    normalized = normalized.replace("$$", "").replace("$", "")
    normalized = re.sub(r"\\(?:qquad|quad)\b", "", normalized)
    for spacing_command in (r"\,", r"\;", r"\:", r"\!"):
        normalized = normalized.replace(spacing_command, "")
    normalized = re.sub(r"\s+", "", normalized)
    return normalized.rstrip(".,;")


def is_structural_only_excerpt(excerpt: str) -> bool:
    """Reject headings, separators, and table-of-contents links as evidence."""
    stripped = excerpt.strip()
    if re.fullmatch(r"(?:[-*_]\s*){3,}", stripped):
        return True
    if re.fullmatch(r"#{1,6}\s+\S.*", stripped):
        return True
    return MARKDOWN_TOC_ENTRY_RE.fullmatch(stripped) is not None


def validate_contract(
    contract_path: Path,
    workspace_root: Path,
    source_manifest_path: Path | None = None,
    grounding_inventory_path: Path | None = None,
    metrics_out: dict[str, Any] | None = None,
) -> list[Finding]:
    findings: list[Finding] = []
    contract = load_json(contract_path)
    if not isinstance(contract, dict):
        return [Finding("CONTRACT_NOT_OBJECT", "$", "contract root must be an object")]

    raw_sources = contract.get("source_materials")
    if not isinstance(raw_sources, list) or not raw_sources:
        return [
            Finding(
                "SOURCE_MATERIALS_INVALID",
                "$.source_materials",
                "source_materials must be a non-empty array",
            )
        ]

    source_records: dict[str, dict[str, Any]] = {}
    source_texts: dict[str, str] = {}
    actual_hashes: dict[str, str] = {}

    for index, record in enumerate(raw_sources):
        location = f"$.source_materials[{index}]"
        if not isinstance(record, dict):
            findings.append(Finding("SOURCE_RECORD_INVALID", location, "source must be an object"))
            continue
        source_id = record.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            findings.append(Finding("SOURCE_ID_INVALID", location, "source_id must be non-empty"))
            continue
        if source_id in source_records:
            findings.append(
                Finding("SOURCE_ID_DUPLICATE", location, f"duplicate source_id: {source_id}")
            )
            continue
        source_records[source_id] = record

        raw_path = record.get("path")
        if not isinstance(raw_path, str) or not raw_path:
            findings.append(Finding("SOURCE_PATH_INVALID", location, "path must be non-empty"))
            continue
        try:
            source_path = resolve_workspace_path(workspace_root, raw_path)
        except ValueError as exc:
            findings.append(Finding("SOURCE_PATH_OUTSIDE_WORKSPACE", location, str(exc)))
            continue
        if not source_path.is_file():
            findings.append(
                Finding("SOURCE_FILE_MISSING", location, f"source file not found: {raw_path}")
            )
            continue

        actual_hash = sha256(source_path)
        actual_hashes[source_id] = actual_hash
        recorded_hash = record.get("sha256")
        if recorded_hash != actual_hash:
            findings.append(
                Finding(
                    "SOURCE_HASH_MISMATCH",
                    f"{location}.sha256",
                    f"{source_id}: recorded {recorded_hash!r}, actual {actual_hash}",
                )
            )

        source_format = record.get("format")
        if source_format not in TEXT_FORMATS:
            findings.append(
                Finding(
                    "SOURCE_FORMAT_UNSUPPORTED",
                    f"{location}.format",
                    f"{source_id}: deterministic excerpt validation supports {sorted(TEXT_FORMATS)}, "
                    f"not {source_format!r}; use an authoritative extracted-text source",
                )
            )
            continue
        try:
            source_texts[source_id] = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            findings.append(
                Finding(
                    "SOURCE_NOT_UTF8",
                    location,
                    f"{source_id}: cannot decode source as UTF-8: {exc}",
                )
            )

    manifest_path = source_manifest_path
    if manifest_path is None:
        sibling_manifest = contract_path.parent / "source_manifest.json"
        if sibling_manifest.is_file():
            manifest_path = sibling_manifest
    if manifest_path is not None:
        try:
            manifest = load_json(manifest_path)
        except ValueError as exc:
            findings.append(Finding("MANIFEST_INVALID", "$manifest", str(exc)))
        else:
            raw_manifest_sources = manifest.get("sources") if isinstance(manifest, dict) else None
            if not isinstance(raw_manifest_sources, list):
                findings.append(
                    Finding(
                        "MANIFEST_SOURCES_INVALID",
                        "$manifest.sources",
                        "manifest sources must be an array",
                    )
                )
            else:
                manifest_records: dict[str, dict[str, Any]] = {}
                for index, record in enumerate(raw_manifest_sources):
                    location = f"$manifest.sources[{index}]"
                    if not isinstance(record, dict) or not isinstance(record.get("source_id"), str):
                        findings.append(
                            Finding("MANIFEST_SOURCE_INVALID", location, "invalid manifest source")
                        )
                        continue
                    source_id = record["source_id"]
                    if source_id in manifest_records:
                        findings.append(
                            Finding(
                                "MANIFEST_SOURCE_ID_DUPLICATE",
                                location,
                                f"duplicate source_id: {source_id}",
                            )
                        )
                    manifest_records[source_id] = record
                if set(manifest_records) != set(source_records):
                    findings.append(
                        Finding(
                            "MANIFEST_SOURCE_SET_MISMATCH",
                            "$manifest.sources",
                            "manifest and contract source_id sets differ",
                        )
                    )
                for source_id in sorted(set(manifest_records) & set(source_records)):
                    manifest_record = manifest_records[source_id]
                    contract_record = source_records[source_id]
                    for field in ("path", "format", "sha256", "role"):
                        if manifest_record.get(field) != contract_record.get(field):
                            findings.append(
                                Finding(
                                    "MANIFEST_CONTRACT_MISMATCH",
                                    f"$manifest.sources[{source_id}].{field}",
                                    f"{source_id}: manifest and contract differ for {field}",
                                )
                            )
                    if manifest_record.get("sha256") != actual_hashes.get(source_id):
                        findings.append(
                            Finding(
                                "MANIFEST_HASH_MISMATCH",
                                f"$manifest.sources[{source_id}].sha256",
                                f"{source_id}: manifest hash does not match source file",
                            )
                        )

    inventory_descriptor = contract.get("grounding_inventory")
    inventory_path = grounding_inventory_path
    if not isinstance(inventory_descriptor, dict):
        findings.append(
            Finding(
                "GROUNDING_INVENTORY_DESCRIPTOR_INVALID",
                "$.grounding_inventory",
                "grounding_inventory must identify a fingerprinted inventory",
            )
        )
    else:
        raw_inventory_path = inventory_descriptor.get("path")
        if not isinstance(raw_inventory_path, str) or not raw_inventory_path:
            findings.append(
                Finding(
                    "GROUNDING_INVENTORY_PATH_INVALID",
                    "$.grounding_inventory.path",
                    "inventory path must be a non-empty string",
                )
            )
        else:
            try:
                descriptor_path = resolve_workspace_path(workspace_root, raw_inventory_path)
            except ValueError as exc:
                findings.append(
                    Finding("GROUNDING_INVENTORY_PATH_INVALID", "$.grounding_inventory.path", str(exc))
                )
            else:
                if inventory_path is None:
                    inventory_path = descriptor_path
                elif inventory_path.resolve() != descriptor_path:
                    findings.append(
                        Finding(
                            "GROUNDING_INVENTORY_PATH_MISMATCH",
                            "$.grounding_inventory.path",
                            "CLI inventory path differs from the contract descriptor",
                        )
                    )
                if descriptor_path.is_file():
                    actual_inventory_hash = sha256(descriptor_path)
                    if inventory_descriptor.get("sha256") != actual_inventory_hash:
                        findings.append(
                            Finding(
                                "GROUNDING_INVENTORY_HASH_MISMATCH",
                                "$.grounding_inventory.sha256",
                                "recorded inventory hash does not match the inventory file",
                            )
                        )
                else:
                    findings.append(
                        Finding(
                            "GROUNDING_INVENTORY_MISSING",
                            "$.grounding_inventory.path",
                            f"inventory file not found: {raw_inventory_path}",
                        )
                    )

    inventory: dict[str, Any] = {}
    if inventory_path is not None and inventory_path.is_file():
        try:
            loaded_inventory = load_json(inventory_path)
        except ValueError as exc:
            findings.append(Finding("GROUNDING_INVENTORY_INVALID", "$inventory", str(exc)))
        else:
            if isinstance(loaded_inventory, dict):
                inventory = loaded_inventory
            else:
                findings.append(
                    Finding("GROUNDING_INVENTORY_INVALID", "$inventory", "inventory must be an object")
                )

    inventory_source = inventory.get("source") if inventory else None
    if inventory and not isinstance(inventory_source, dict):
        findings.append(
            Finding("GROUNDING_INVENTORY_SOURCE_INVALID", "$inventory.source", "source must be an object")
        )
        inventory_source = None
    if isinstance(inventory_source, dict):
        inventory_source_id = inventory_source.get("source_id")
        contract_source = source_records.get(inventory_source_id)
        if contract_source is None:
            findings.append(
                Finding(
                    "GROUNDING_INVENTORY_SOURCE_UNKNOWN",
                    "$inventory.source.source_id",
                    f"unknown source_id: {inventory_source_id!r}",
                )
            )
        else:
            for field in ("path", "format", "sha256"):
                if inventory_source.get(field) != contract_source.get(field):
                    findings.append(
                        Finding(
                            "GROUNDING_INVENTORY_SOURCE_MISMATCH",
                            f"$inventory.source.{field}",
                            f"inventory and contract differ for {field}",
                        )
                    )

    source_units: dict[str, dict[str, Any]] = {}
    raw_source_units = inventory.get("source_units", []) if inventory else []
    if not isinstance(raw_source_units, list):
        findings.append(
            Finding("SOURCE_UNITS_INVALID", "$inventory.source_units", "source_units must be an array")
        )
        raw_source_units = []
    inventory_source_id = inventory_source.get("source_id") if isinstance(inventory_source, dict) else None
    inventory_source_text = source_texts.get(inventory_source_id)
    for index, unit in enumerate(raw_source_units):
        location = f"$inventory.source_units[{index}]"
        if not isinstance(unit, dict):
            findings.append(Finding("SOURCE_UNIT_INVALID", location, "source unit must be an object"))
            continue
        unit_id = unit.get("source_unit_id")
        if not isinstance(unit_id, str) or SOURCE_UNIT_ID_RE.fullmatch(unit_id) is None:
            findings.append(Finding("SOURCE_UNIT_ID_INVALID", f"{location}.source_unit_id", f"invalid source unit ID: {unit_id!r}"))
            continue
        if unit_id in source_units:
            findings.append(Finding("SOURCE_UNIT_ID_DUPLICATE", f"{location}.source_unit_id", f"duplicate source unit ID: {unit_id}"))
            continue
        source_units[unit_id] = unit
        exact_text = unit.get("exact_text")
        locator = unit.get("locator")
        if not isinstance(exact_text, str) or not exact_text:
            findings.append(Finding("SOURCE_UNIT_TEXT_INVALID", f"{location}.exact_text", "exact_text must be non-empty"))
        if not isinstance(locator, dict):
            findings.append(Finding("SOURCE_UNIT_LOCATOR_INVALID", f"{location}.locator", "locator must be an object"))
        elif inventory_source_text is not None and isinstance(exact_text, str):
            start = locator.get("line_start")
            end = locator.get("line_end")
            if not isinstance(start, int) or not isinstance(end, int):
                findings.append(Finding("SOURCE_UNIT_LOCATOR_INVALID", f"{location}.locator", "line_start and line_end must be integers"))
            else:
                region = line_region(inventory_source_text, start, end)
                if region is None or region.rstrip("\r\n") != exact_text:
                    findings.append(
                        Finding(
                            "SOURCE_UNIT_SOURCE_MISMATCH",
                            f"{location}.exact_text",
                            "source unit is not the complete text at its recorded line range",
                        )
                    )

    formulas: dict[str, dict[str, Any]] = {}
    raw_formulas = inventory.get("formulas", []) if inventory else []
    if not isinstance(raw_formulas, list):
        findings.append(Finding("FORMULAS_INVALID", "$inventory.formulas", "formulas must be an array"))
        raw_formulas = []
    for index, formula in enumerate(raw_formulas):
        location = f"$inventory.formulas[{index}]"
        if not isinstance(formula, dict):
            findings.append(Finding("FORMULA_INVALID", location, "formula must be an object"))
            continue
        formula_id = formula.get("formula_id")
        if not isinstance(formula_id, str) or FORMULA_ID_RE.fullmatch(formula_id) is None:
            findings.append(Finding("FORMULA_ID_INVALID", f"{location}.formula_id", f"invalid formula ID: {formula_id!r}"))
            continue
        if formula_id in formulas:
            findings.append(Finding("FORMULA_ID_DUPLICATE", f"{location}.formula_id", f"duplicate formula ID: {formula_id}"))
            continue
        formulas[formula_id] = formula
        unit_id = formula.get("source_unit_id")
        unit = source_units.get(unit_id)
        if unit is None:
            findings.append(Finding("FORMULA_SOURCE_UNIT_UNKNOWN", f"{location}.source_unit_id", f"unknown source unit: {unit_id!r}"))
            continue
        if unit.get("unit_type") != "display_math":
            findings.append(Finding("FORMULA_SOURCE_UNIT_NOT_MATH", f"{location}.source_unit_id", "formula must reference a display_math source unit"))
        if formula.get("scope_role") != unit.get("scope_role"):
            findings.append(Finding("FORMULA_SCOPE_MISMATCH", f"{location}.scope_role", "formula and source unit scope roles differ"))
        exact_latex = formula.get("exact_latex")
        exact_block = formula.get("exact_block")
        if exact_block != unit.get("exact_text"):
            findings.append(Finding("FORMULA_BLOCK_MISMATCH", f"{location}.exact_block", "formula block differs from its source unit"))
        if not isinstance(exact_latex, str) or not exact_latex.strip():
            findings.append(Finding("FORMULA_LATEX_INVALID", f"{location}.exact_latex", "exact_latex must be non-empty"))
        elif isinstance(exact_block, str) and normalize_latex(exact_latex) != normalize_latex(exact_block):
            findings.append(Finding("FORMULA_LATEX_SOURCE_MISMATCH", f"{location}.exact_latex", "exact_latex differs from the display-math source block"))

    raw_items = contract.get("contract_items")
    if not isinstance(raw_items, list) or not raw_items:
        findings.append(
            Finding(
                "CONTRACT_ITEMS_INVALID",
                "$.contract_items",
                "contract_items must be a non-empty array",
            )
        )
        raw_items = []

    item_ids: set[str] = set()
    check_ids: set[str] = set()
    mapped_formula_ids: set[str] = set()
    mapped_formula_requirements: dict[str, set[str]] = {}
    mapped_source_unit_ids: set[str] = set()

    def validate_evidence(raw_evidence: Any, owner_location: str) -> None:
        if not isinstance(raw_evidence, list) or not raw_evidence:
            findings.append(
                Finding("EVIDENCE_INVALID", f"{owner_location}.evidence", "evidence must be non-empty")
            )
            return
        for evidence_index, evidence in enumerate(raw_evidence):
            location = f"{owner_location}.evidence[{evidence_index}]"
            if not isinstance(evidence, dict):
                findings.append(Finding("EVIDENCE_RECORD_INVALID", location, "must be an object"))
                continue
            source_id = evidence.get("source_id")
            if source_id not in source_records:
                findings.append(
                    Finding(
                        "EVIDENCE_SOURCE_UNKNOWN",
                        f"{location}.source_id",
                        f"unknown source_id: {source_id!r}",
                    )
                )
                continue
            source_unit_id = evidence.get("source_unit_id")
            source_unit = source_units.get(source_unit_id)
            if source_unit is None:
                findings.append(
                    Finding(
                        "EVIDENCE_SOURCE_UNIT_UNKNOWN",
                        f"{location}.source_unit_id",
                        f"unknown source_unit_id: {source_unit_id!r}",
                    )
                )
            excerpt = evidence.get("exact_excerpt")
            if not isinstance(excerpt, str) or not excerpt:
                findings.append(
                    Finding(
                        "EXCERPT_INVALID",
                        f"{location}.exact_excerpt",
                        "exact_excerpt must be a non-empty string",
                    )
                )
                continue
            if source_unit is not None:
                if excerpt != source_unit.get("exact_text"):
                    findings.append(
                        Finding(
                            "EVIDENCE_INCOMPLETE_SOURCE_UNIT",
                            f"{location}.exact_excerpt",
                            "evidence must equal the complete deterministic source unit",
                        )
                    )
                if source_unit.get("scope_role") == "exercise":
                    findings.append(
                        Finding(
                            "EXCLUDED_SOURCE_UNIT_REFERENCED",
                            f"{location}.source_unit_id",
                            "exercise source units are outside the default grounding scope",
                        )
                    )
            if is_structural_only_excerpt(excerpt):
                findings.append(
                    Finding(
                        "EXCERPT_STRUCTURAL_ONLY",
                        f"{location}.exact_excerpt",
                        "a heading, separator, or table-of-contents entry cannot support a contract claim",
                    )
                )
            source_text = source_texts.get(source_id)
            if source_text is None:
                continue
            if excerpt not in source_text:
                findings.append(
                    Finding(
                        "EXCERPT_NOT_CONTIGUOUS",
                        f"{location}.exact_excerpt",
                        "exact_excerpt is not an exact contiguous substring of its source",
                    )
                )

            locator = evidence.get("locator")
            if not isinstance(locator, dict):
                findings.append(Finding("LOCATOR_INVALID", f"{location}.locator", "must be an object"))
                continue
            locator_type = locator.get("locator_type")
            locator_value = locator.get("value")
            if locator_type not in LINE_LOCATOR_TYPES:
                findings.append(
                    Finding(
                        "LOCATOR_TYPE_UNSUPPORTED",
                        f"{location}.locator.locator_type",
                        f"line-containment validation does not support {locator_type!r}",
                    )
                )
                continue
            if not isinstance(locator_value, str):
                findings.append(
                    Finding(
                        "LOCATOR_VALUE_INVALID",
                        f"{location}.locator.value",
                        "locator value must be a string",
                    )
                )
                continue
            match = LINE_RANGE_RE.search(locator_value)
            if match is None:
                findings.append(
                    Finding(
                        "LOCATOR_LINE_RANGE_MISSING",
                        f"{location}.locator.value",
                        "locator must contain 'line N' or 'lines N-M'",
                    )
                )
                continue
            start = int(match.group(1))
            end = int(match.group(2) or match.group(1))
            region = line_region(source_text, start, end)
            if region is None:
                findings.append(
                    Finding(
                        "LOCATOR_LINE_RANGE_INVALID",
                        f"{location}.locator.value",
                        f"line range {start}-{end} is outside the source or reversed",
                    )
                )
            elif excerpt not in region:
                findings.append(
                    Finding(
                        "LOCATOR_DOES_NOT_CONTAIN_EXCERPT",
                        f"{location}.locator.value",
                        f"lines {start}-{end} do not contain the complete exact_excerpt",
                    )
                )

    for index, item in enumerate(raw_items):
        location = f"$.contract_items[{index}]"
        if not isinstance(item, dict):
            findings.append(Finding("ITEM_INVALID", location, "contract item must be an object"))
            continue
        item_id = item.get("item_id")
        if not isinstance(item_id, str) or ITEM_ID_RE.fullmatch(item_id) is None:
            findings.append(
                Finding("ITEM_ID_INVALID", f"{location}.item_id", f"invalid item_id: {item_id!r}")
            )
        elif item_id in item_ids:
            findings.append(
                Finding("ITEM_ID_DUPLICATE", f"{location}.item_id", f"duplicate item_id: {item_id}")
            )
        else:
            item_ids.add(item_id)
        if item.get("item_type") == "exercise":
            findings.append(
                Finding(
                    "EXERCISE_ITEM_OUT_OF_SCOPE",
                    f"{location}.item_type",
                    "exercises are excluded from the core grounding contract by default",
                )
            )
        generation_requirement = item.get("generation_requirement")
        required_for_generation = item.get("required_for_generation")
        if generation_requirement not in {"required", "conditional"}:
            findings.append(
                Finding(
                    "GENERATION_REQUIREMENT_INVALID",
                    f"{location}.generation_requirement",
                    "generation_requirement must be required or conditional",
                )
            )
        elif required_for_generation != (generation_requirement == "required"):
            findings.append(
                Finding(
                    "GENERATION_REQUIREMENT_CONFLICT",
                    f"{location}.required_for_generation",
                    "required_for_generation must be true exactly when generation_requirement is required",
                )
            )
        item_evidence = item.get("evidence")
        if isinstance(item_evidence, list):
            mapped_source_unit_ids.update(
                record.get("source_unit_id")
                for record in item_evidence
                if isinstance(record, dict) and isinstance(record.get("source_unit_id"), str)
            )
        validate_evidence(item_evidence, location)
        semantic_checks = item.get("semantic_checks", [])
        if not isinstance(semantic_checks, list):
            findings.append(
                Finding(
                    "SEMANTIC_CHECKS_INVALID",
                    f"{location}.semantic_checks",
                    "semantic_checks must be an array",
                )
            )
        else:
            if not semantic_checks:
                findings.append(
                    Finding(
                        "SEMANTIC_CHECKS_EMPTY",
                        f"{location}.semantic_checks",
                        "every core contract item requires at least one proposed semantic check",
                    )
                )
            for check_index, check in enumerate(semantic_checks):
                check_location = f"{location}.semantic_checks[{check_index}].check_id"
                check_id = check.get("check_id") if isinstance(check, dict) else None
                if not isinstance(check_id, str) or CHECK_ID_RE.fullmatch(check_id) is None:
                    findings.append(
                        Finding("CHECK_ID_INVALID", check_location, f"invalid check_id: {check_id!r}")
                    )
                elif check_id in check_ids:
                    findings.append(
                        Finding("CHECK_ID_DUPLICATE", check_location, f"duplicate check_id: {check_id}")
                    )
                else:
                    check_ids.add(check_id)

        raw_formula_refs = item.get("formula_refs")
        valid_formula_refs: list[str] = []
        if not isinstance(raw_formula_refs, list):
            findings.append(
                Finding(
                    "FORMULA_REFS_INVALID",
                    f"{location}.formula_refs",
                    "formula_refs must be an array",
                )
            )
        else:
            seen_item_formula_refs: set[str] = set()
            evidence_records = item.get("evidence")
            evidence_unit_ids = {
                record.get("source_unit_id")
                for record in evidence_records
                if isinstance(record, dict)
            } if isinstance(evidence_records, list) else set()
            for formula_index, formula_id in enumerate(raw_formula_refs):
                formula_location = f"{location}.formula_refs[{formula_index}]"
                if not isinstance(formula_id, str) or FORMULA_ID_RE.fullmatch(formula_id) is None:
                    findings.append(Finding("FORMULA_REF_INVALID", formula_location, f"invalid formula reference: {formula_id!r}"))
                    continue
                if formula_id in seen_item_formula_refs:
                    findings.append(Finding("FORMULA_REF_DUPLICATE", formula_location, f"duplicate formula reference: {formula_id}"))
                    continue
                seen_item_formula_refs.add(formula_id)
                formula_record = formulas.get(formula_id)
                if formula_record is None:
                    findings.append(Finding("FORMULA_REFERENCE_UNKNOWN", formula_location, f"unknown formula ID: {formula_id}"))
                    continue
                if formula_record.get("scope_role") == "exercise":
                    findings.append(Finding("EXCLUDED_FORMULA_REFERENCED", formula_location, "exercise formulas are outside the default grounding scope"))
                    continue
                valid_formula_refs.append(formula_id)
                mapped_formula_ids.add(formula_id)
                mapped_formula_requirements.setdefault(formula_id, set()).add(str(generation_requirement))
                if formula_record.get("source_unit_id") not in evidence_unit_ids:
                    findings.append(
                        Finding(
                            "FORMULA_EVIDENCE_MISSING",
                            formula_location,
                            "the formula's complete display-math source unit must be item evidence",
                        )
                    )

        canonical_latex = item.get("canonical_latex")
        if not isinstance(canonical_latex, list):
            findings.append(
                Finding(
                    "CANONICAL_LATEX_INVALID",
                    f"{location}.canonical_latex",
                    "canonical_latex must be an array",
                )
            )
        else:
            expected_latex = [formulas[formula_id].get("exact_latex") for formula_id in valid_formula_refs]
            if canonical_latex != expected_latex:
                findings.append(
                    Finding(
                        "CANONICAL_LATEX_INVENTORY_MISMATCH",
                        f"{location}.canonical_latex",
                        "canonical_latex must exactly match formula_refs in order",
                    )
                )
            evidence = item.get("evidence")
            evidence_excerpts = (
                [
                    record.get("exact_excerpt")
                    for record in evidence
                    if isinstance(record, dict)
                    and isinstance(record.get("exact_excerpt"), str)
                ]
                if isinstance(evidence, list)
                else []
            )
            normalized_evidence = [normalize_latex(value) for value in evidence_excerpts]
            for formula_index, formula in enumerate(canonical_latex):
                formula_location = f"{location}.canonical_latex[{formula_index}]"
                if not isinstance(formula, str) or not formula.strip():
                    findings.append(
                        Finding(
                            "CANONICAL_LATEX_ENTRY_INVALID",
                            formula_location,
                            "canonical LaTeX entries must be non-empty strings",
                        )
                    )
                    continue
                normalized_formula = normalize_latex(formula)
                if not normalized_formula:
                    findings.append(
                        Finding(
                            "CANONICAL_LATEX_ENTRY_INVALID",
                            formula_location,
                            "canonical LaTeX is empty after presentation normalization",
                        )
                    )
                elif not any(
                    normalized_formula in normalized_excerpt
                    for normalized_excerpt in normalized_evidence
                ):
                    findings.append(
                        Finding(
                            "CANONICAL_LATEX_UNSUPPORTED_BY_EVIDENCE",
                            formula_location,
                            "no single exact_excerpt contains this formula after whitespace-only "
                            "and LaTeX-spacing normalization",
                        )
                    )

    coverage_scope = contract.get("coverage_scope")
    reference_only_formula_ids: set[str] = set()
    reference_only_source_unit_ids: set[str] = set()
    if not isinstance(coverage_scope, dict):
        findings.append(Finding("COVERAGE_SCOPE_INVALID", "$.coverage_scope", "coverage_scope must be an object"))
    else:
        raw_reference_formulas = coverage_scope.get("reference_only_formula_ids")
        if not isinstance(raw_reference_formulas, list):
            findings.append(Finding("REFERENCE_ONLY_FORMULAS_INVALID", "$.coverage_scope.reference_only_formula_ids", "must be an array"))
        else:
            for index, formula_id in enumerate(raw_reference_formulas):
                location = f"$.coverage_scope.reference_only_formula_ids[{index}]"
                if formula_id not in formulas:
                    findings.append(Finding("REFERENCE_ONLY_FORMULA_UNKNOWN", location, f"unknown formula ID: {formula_id!r}"))
                elif formulas[formula_id].get("scope_role") != "derivation":
                    findings.append(Finding("REFERENCE_ONLY_FORMULA_NOT_DERIVATION", location, "only deterministically identified derivation formulas may be reference-only"))
                elif formula_id in reference_only_formula_ids:
                    findings.append(Finding("REFERENCE_ONLY_FORMULA_DUPLICATE", location, f"duplicate formula ID: {formula_id}"))
                else:
                    reference_only_formula_ids.add(formula_id)
        raw_reference_units = coverage_scope.get("reference_only_source_unit_ids")
        if not isinstance(raw_reference_units, list):
            findings.append(Finding("REFERENCE_ONLY_SOURCE_UNITS_INVALID", "$.coverage_scope.reference_only_source_unit_ids", "must be an array"))
        else:
            for index, unit_id in enumerate(raw_reference_units):
                location = f"$.coverage_scope.reference_only_source_unit_ids[{index}]"
                unit = source_units.get(unit_id)
                if unit is None:
                    findings.append(Finding("REFERENCE_ONLY_SOURCE_UNIT_UNKNOWN", location, f"unknown source unit ID: {unit_id!r}"))
                elif unit.get("scope_role") not in {"core_material", "derivation"} or unit.get("unit_type") == "heading":
                    findings.append(Finding("REFERENCE_ONLY_SOURCE_UNIT_EXCLUDED", location, "only included non-heading source units may be reference-only"))
                elif unit_id in reference_only_source_unit_ids:
                    findings.append(Finding("REFERENCE_ONLY_SOURCE_UNIT_DUPLICATE", location, f"duplicate source unit ID: {unit_id}"))
                else:
                    reference_only_source_unit_ids.add(unit_id)

    overlap_formulas = mapped_formula_ids & reference_only_formula_ids
    for formula_id in sorted(overlap_formulas):
        findings.append(
            Finding(
                "FORMULA_CLASSIFICATION_CONFLICT",
                "$.coverage_scope.reference_only_formula_ids",
                f"{formula_id} is both mapped and reference-only",
            )
        )
    overlap_units = mapped_source_unit_ids & reference_only_source_unit_ids
    for unit_id in sorted(overlap_units):
        findings.append(
            Finding(
                "SOURCE_UNIT_CLASSIFICATION_CONFLICT",
                "$.coverage_scope.reference_only_source_unit_ids",
                f"{unit_id} is both mapped and reference-only",
            )
        )

    core_formula_ids = {
        formula_id
        for formula_id, formula in formulas.items()
        if formula.get("scope_role") == "core_material"
    }
    derivation_formula_ids = {
        formula_id
        for formula_id, formula in formulas.items()
        if formula.get("scope_role") == "derivation"
    }
    unclassified_formula_ids = core_formula_ids - mapped_formula_ids - reference_only_formula_ids
    for formula_id in sorted(unclassified_formula_ids):
        findings.append(
            Finding(
                "CORE_FORMULA_UNCLASSIFIED",
                "$.coverage_scope",
                f"{formula_id} is neither mapped to a contract item nor marked reference-only",
            )
        )
    unclassified_derivation_formula_ids = derivation_formula_ids - mapped_formula_ids - reference_only_formula_ids
    for formula_id in sorted(unclassified_derivation_formula_ids):
        findings.append(
            Finding(
                "DERIVATION_FORMULA_UNCLASSIFIED",
                "$.coverage_scope",
                f"{formula_id} is neither mapped to a contract item nor marked reference-only",
            )
        )

    core_source_unit_ids = {
        unit_id
        for unit_id, unit in source_units.items()
        if unit.get("scope_role") in {"core_material", "derivation"} and unit.get("unit_type") != "heading"
    }
    unclassified_source_unit_ids = core_source_unit_ids - mapped_source_unit_ids - reference_only_source_unit_ids
    for unit_id in sorted(unclassified_source_unit_ids):
        findings.append(
            Finding(
                "CORE_SOURCE_UNIT_UNCLASSIFIED",
                "$.coverage_scope",
                f"{unit_id} is neither mapped to a contract item nor marked reference-only",
            )
        )

    mapped_core_formula_ids = mapped_formula_ids & core_formula_ids
    core_mapping_denominator = len(core_formula_ids - reference_only_formula_ids)
    core_formula_mapping_rate = (
        len(mapped_core_formula_ids) / core_mapping_denominator
        if core_mapping_denominator
        else 1.0
    )
    classified_formula_rate = (
        len((mapped_formula_ids | reference_only_formula_ids) & core_formula_ids) / len(core_formula_ids)
        if core_formula_ids
        else 1.0
    )
    classified_source_unit_rate = (
        len((mapped_source_unit_ids | reference_only_source_unit_ids) & core_source_unit_ids) / len(core_source_unit_ids)
        if core_source_unit_ids
        else 1.0
    )
    if core_formula_mapping_rate != 1.0:
        findings.append(
            Finding(
                "CORE_FORMULA_MAPPING_TARGET_NOT_MET",
                "$.coverage_scope.core_formula_mapping_target",
                f"core formula mapping rate is {core_formula_mapping_rate:.6f}, expected 1.0",
            )
        )
    if metrics_out is not None:
        metrics_out.update(
            {
                "inventory_formula_count": len(formulas),
                "core_formula_count": len(core_formula_ids),
                "derivation_formula_count": len(derivation_formula_ids),
                "excluded_exercise_formula_count": len(formulas) - len(core_formula_ids) - len(derivation_formula_ids),
                "mapped_core_formula_count": len(mapped_core_formula_ids),
                "reference_only_formula_count": len(reference_only_formula_ids),
                "core_formula_mapping_rate": core_formula_mapping_rate,
                "core_formula_classification_rate": classified_formula_rate,
                "core_source_unit_count": len(core_source_unit_ids),
                "mapped_core_source_unit_count": len(mapped_source_unit_ids & core_source_unit_ids),
                "reference_only_source_unit_count": len(reference_only_source_unit_ids),
                "core_source_unit_classification_rate": classified_source_unit_rate,
            }
        )

    raw_issues = contract.get("candidate_source_issues", [])
    issue_ids: set[str] = set()
    if not isinstance(raw_issues, list):
        findings.append(
            Finding(
                "SOURCE_ISSUES_INVALID",
                "$.candidate_source_issues",
                "candidate_source_issues must be an array",
            )
        )
        raw_issues = []
    for index, issue in enumerate(raw_issues):
        location = f"$.candidate_source_issues[{index}]"
        if not isinstance(issue, dict):
            findings.append(Finding("SOURCE_ISSUE_INVALID", location, "issue must be an object"))
            continue
        issue_id = issue.get("issue_id")
        if not isinstance(issue_id, str) or ISSUE_ID_RE.fullmatch(issue_id) is None:
            findings.append(
                Finding("ISSUE_ID_INVALID", f"{location}.issue_id", f"invalid issue_id: {issue_id!r}")
            )
        elif issue_id in issue_ids:
            findings.append(
                Finding(
                    "ISSUE_ID_DUPLICATE",
                    f"{location}.issue_id",
                    f"duplicate issue_id: {issue_id}",
                )
            )
        else:
            issue_ids.add(issue_id)
        affected_ids = issue.get("affected_item_ids")
        if not isinstance(affected_ids, list):
            findings.append(
                Finding(
                    "AFFECTED_ITEM_IDS_INVALID",
                    f"{location}.affected_item_ids",
                    "affected_item_ids must be an array",
                )
            )
        else:
            for affected_index, affected_id in enumerate(affected_ids):
                if affected_id not in item_ids:
                    findings.append(
                        Finding(
                            "AFFECTED_ITEM_UNKNOWN",
                            f"{location}.affected_item_ids[{affected_index}]",
                            f"unknown item_id: {affected_id!r}",
                        )
                    )
        validate_evidence(issue.get("evidence"), location)

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", required=True, help="Path to reference_contract.json")
    parser.add_argument("--workspace-root", default=".", help="Workspace root for source paths")
    parser.add_argument("--source-manifest", help="Optional source_manifest.json; sibling used by default")
    parser.add_argument("--grounding-inventory", help="Optional grounding_inventory.json; contract path used by default")
    parser.add_argument("--report", help="Optional JSON validation report output")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    contract_path = Path(args.contract).resolve()
    manifest_path = Path(args.source_manifest).resolve() if args.source_manifest else None
    inventory_path = Path(args.grounding_inventory).resolve() if args.grounding_inventory else None
    metrics: dict[str, Any] = {}

    try:
        findings = validate_contract(
            contract_path,
            workspace_root,
            manifest_path,
            inventory_path,
            metrics,
        )
    except ValueError as exc:
        findings = [Finding("VALIDATION_INPUT_ERROR", "$", str(exc))]

    report = {
        "validator": "reference-contract-evidence-v3",
        "valid": not findings,
        "error_count": len(findings),
        "coverage_metrics": metrics,
        "errors": [asdict(finding) for finding in findings],
    }
    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if findings:
        print(f"FAIL: {len(findings)} deterministic validation error(s)")
        for finding in findings:
            print(f"[{finding.code}] {finding.location}: {finding.message}")
        return 1

    print(
        "PASS: source/inventory hashes, complete source units, formula mappings, "
        "coverage targets, IDs, and evidence references are valid"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
