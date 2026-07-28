---
name: proposed-structure-review-and-edit
description: Review and revise proposed_structure.json with dependency-aware edits.
---

# proposed-structure-review-and-edit

Use this skill after initial structure generation to refine `<output-dir>/proposed_structure.json`
until the user confirms the structure is good and is ready to move to the next stage.

Resolve paths from `.env` before running:

- `CONTENT_INGESTER_INPUTS_DIR` (default: `inputs`)
- `CONTENT_INGESTER_OUTPUTS_DIR` (default: `outputs`)

Reference `.github/instructions/updating-proposed-structure.md` for the required edit workflow.

## Tasks

- Validate required fields for each page.
- Refine prerequisite ordering and avoid cycles.
- Improve split decisions to keep one learning objective per page.
- Reconcile tags against `<input-dir>/live-website-export/tags_current.md`.
- Review all assumptions inferred in `generation_context`.
- Confirm that every learner profile has exactly one intended pathway unless multiple alternatives are explicitly requested.
- Verify that core concept definitions, formulae, conditions, and dependencies remain discipline-independent.
- Check that pathway entry points, ordering, required/optional choices, examples, proof depth, implementation focus, and assessment match the learner profile.
- Ensure required steps do not depend on optional steps and that prerequisites appear earlier in each pathway.

## Regenerate graph after edits

```bash
python .github/skills/input-to-proposed-structure/generate_prerequisite_graph.py --source proposed_structure --inputs-dir <input-dir> --proposed-file <output-dir>/proposed_structure.json --output-dir <output-dir>
```

## Output

- Updated `<output-dir>/proposed_structure.json`
- Updated `<output-dir>/dependency_graph.md`
- Updated `<output-dir>/pathways/<pathway-id>.md` files
