#!/usr/bin/env python3
"""Unit tests for validate_reference_contract.py."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_reference_contract.py"
SPEC = importlib.util.spec_from_file_location("validate_reference_contract", SCRIPT)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class ReferenceContractValidatorTests(unittest.TestCase):
    def fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path, Path, dict]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        source = root / "source.md"
        source.write_text("# Topic\n$$\nalpha\nbeta\n$$\ngamma\n", encoding="utf-8")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        inventory = {
            "source": {
                "source_id": "source",
                "path": "source.md",
                "format": "markdown",
                "sha256": digest,
            },
            "source_units": [
                {
                    "source_unit_id": "SU-001",
                    "unit_type": "display_math",
                    "scope_role": "core_material",
                    "locator": {"line_start": 2, "line_end": 5},
                    "exact_text": "$$\nalpha\nbeta\n$$",
                },
                {
                    "source_unit_id": "SU-002",
                    "unit_type": "paragraph",
                    "scope_role": "core_material",
                    "locator": {"line_start": 6, "line_end": 6},
                    "exact_text": "gamma",
                },
            ],
            "formulas": [
                {
                    "formula_id": "FM-001",
                    "source_unit_id": "SU-001",
                    "scope_role": "core_material",
                    "exact_latex": "alpha\nbeta",
                    "exact_block": "$$\nalpha\nbeta\n$$",
                }
            ],
        }
        inventory_path = root / "grounding_inventory.json"
        inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
        contract = {
            "grounding_inventory": {
                "path": "grounding_inventory.json",
                "sha256": hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
            },
            "coverage_scope": {
                "reference_only_formula_ids": [],
                "reference_only_source_unit_ids": ["SU-002"],
            },
            "source_materials": [
                {
                    "source_id": "source",
                    "path": "source.md",
                    "format": "markdown",
                    "sha256": digest,
                    "role": "authoritative",
                }
            ],
            "contract_items": [
                {
                    "item_id": "RC-001",
                    "item_type": "equation",
                    "required_for_generation": True,
                    "generation_requirement": "required",
                    "evidence": [
                        {
                            "source_id": "source",
                            "source_unit_id": "SU-001",
                            "locator": {
                                "locator_type": "markdown_heading_lines",
                                "value": "# Topic, lines 2-5",
                            },
                            "exact_excerpt": "$$\nalpha\nbeta\n$$",
                        }
                    ],
                    "canonical_latex": ["alpha\nbeta"],
                    "formula_refs": ["FM-001"],
                    "semantic_checks": [{"check_id": "CHK-001"}],
                }
            ],
            "candidate_source_issues": [],
        }
        contract_path = root / "reference_contract.json"
        return temporary, root, contract_path, contract

    def validate(self, root: Path, contract_path: Path, contract: dict):
        contract_path.write_text(json.dumps(contract), encoding="utf-8")
        return VALIDATOR.validate_contract(contract_path, root)

    def test_valid_contract_passes(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        self.assertEqual(self.validate(root, contract_path, contract), [])

    def test_non_contiguous_excerpt_fails(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        contract["contract_items"][0]["evidence"][0]["exact_excerpt"] = "alpha\ngamma"
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("EXCERPT_NOT_CONTIGUOUS", codes)

    def test_locator_must_contain_excerpt(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        contract["contract_items"][0]["evidence"][0]["locator"]["value"] = "line 6"
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("LOCATOR_DOES_NOT_CONTAIN_EXCERPT", codes)

    def test_source_hash_must_match(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        contract["source_materials"][0]["sha256"] = "0" * 64
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("SOURCE_HASH_MISMATCH", codes)

    def test_canonical_latex_requires_evidence_coverage(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        contract["contract_items"][0]["canonical_latex"] = [r"\delta"]
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("CANONICAL_LATEX_UNSUPPORTED_BY_EVIDENCE", codes)

    def test_canonical_latex_must_exactly_match_inventory(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        contract["contract_items"][0]["canonical_latex"] = ["alpha beta"]
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("CANONICAL_LATEX_INVENTORY_MISMATCH", codes)

    def test_structural_only_excerpt_fails(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        evidence = contract["contract_items"][0]["evidence"][0]
        evidence["locator"]["value"] = "line 1"
        evidence["exact_excerpt"] = "# Topic"
        evidence["source_unit_id"] = "SU-001"
        contract["contract_items"][0]["item_type"] = "exercise"
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("EXCERPT_STRUCTURAL_ONLY", codes)

    def test_table_of_contents_excerpt_fails(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        evidence = contract["contract_items"][0]["evidence"][0]
        evidence["exact_excerpt"] = "7. [Exercises & Problems]"
        contract["contract_items"][0]["item_type"] = "exercise"
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("EXCERPT_STRUCTURAL_ONLY", codes)

    def test_unmapped_core_formula_fails(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        contract["contract_items"][0]["formula_refs"] = []
        contract["contract_items"][0]["canonical_latex"] = []
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("CORE_FORMULA_UNCLASSIFIED", codes)

    def test_formula_requires_its_source_unit_as_evidence(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        evidence = contract["contract_items"][0]["evidence"][0]
        evidence["source_unit_id"] = "SU-002"
        evidence["locator"]["value"] = "line 6"
        evidence["exact_excerpt"] = "gamma"
        contract["coverage_scope"]["reference_only_source_unit_ids"] = ["SU-001"]
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("FORMULA_EVIDENCE_MISSING", codes)

    def test_ids_and_references_must_be_valid(self):
        temporary, root, contract_path, contract = self.fixture()
        self.addCleanup(temporary.cleanup)
        duplicate = dict(contract["contract_items"][0])
        duplicate["semantic_checks"] = [{"check_id": "CHK-002"}]
        contract["contract_items"].append(duplicate)
        contract["candidate_source_issues"] = [
            {
                "issue_id": "ISSUE-001",
                "affected_item_ids": ["RC-999"],
                "evidence": [
                    {
                        "source_id": "missing-source",
                        "locator": {
                            "locator_type": "markdown_heading_lines",
                            "value": "line 2",
                        },
                        "exact_excerpt": "alpha",
                    }
                ],
            }
        ]
        codes = {finding.code for finding in self.validate(root, contract_path, contract)}
        self.assertIn("ITEM_ID_DUPLICATE", codes)
        self.assertIn("AFFECTED_ITEM_UNKNOWN", codes)
        self.assertIn("EVIDENCE_SOURCE_UNKNOWN", codes)


if __name__ == "__main__":
    unittest.main()
