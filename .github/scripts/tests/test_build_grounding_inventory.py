#!/usr/bin/env python3
"""Unit tests for build_grounding_inventory.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "build_grounding_inventory.py"
SPEC = importlib.util.spec_from_file_location("build_grounding_inventory", SCRIPT)
assert SPEC and SPEC.loader
INVENTORY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = INVENTORY
SPEC.loader.exec_module(INVENTORY)


class GroundingInventoryBuilderTests(unittest.TestCase):
    def test_core_and_exercise_formulas_are_separated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_text(
                "# Topic\n\n## Problem Formulation\n\n$$\na=b\n$$\n\n"
                "## Exercises\n\n$$\nx=y\n$$\n",
                encoding="utf-8",
            )
            inventory = INVENTORY.build_inventory(source, root, "source")
            self.assertEqual(len(inventory["formulas"]), 2)
            self.assertEqual(inventory["formulas"][0]["scope_role"], "core_material")
            self.assertEqual(inventory["formulas"][1]["scope_role"], "exercise")

    def test_unclosed_display_math_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_text("# Topic\n\n$$\na=b\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unclosed display-math"):
                INVENTORY.build_inventory(source, root, "source")


if __name__ == "__main__":
    unittest.main()
