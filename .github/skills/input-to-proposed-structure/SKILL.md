---
name: input-to-proposed-structure
description: Read ingestion inputs, propose atomic page structure, and generate dependency graph.
---

# input-to-proposed-structure

Use this skill to produce `<output-dir>/proposed_structure.json` from the configured input directory.

Resolve paths from `.env` before running:

- `CONTENT_INGESTER_INPUTS_DIR` (default: `inputs`)
- `CONTENT_INGESTER_OUTPUTS_DIR` (default: `outputs`)

## Read

- `<input-dir>/live-website-export/current_content.md`
- `<input-dir>/live-website-export/tags_current.md`
- New content files in `<input-dir>/content-to-ingest/` (Markdown, notebooks, PDFs, and PPTX files; for PDFs use `.github/instructions/pdf-data-extraction.md` first; for PPTX use `.github/instructions/pptx-data-extraction.md` first)
- `.github/instructions/atomisation-guidelines.md`
- `.github/instructions/discipline-aware-teaching-guidelines.md`
- `.github/instructions/updating-proposed-structure.md`

## Produce

- `<output-dir>/proposed_structure.json`
- `<output-dir>/dependency_graph.md` by running:
- One pathway graph per learner profile in `<output-dir>/pathways/<pathway-id>.md`

```bash
python .github/skills/input-to-proposed-structure/generate_prerequisite_graph.py --source proposed_structure --inputs-dir <input-dir> --proposed-file <output-dir>/proposed_structure.json --output-dir <output-dir>
```

## Required source-analysis sequence

Do not draft `pages` directly from a high-level summary of the inputs.

1. Inventory every meaningful source section, including advanced topics, proofs, examples, exercises, and appendices.
2. Create `source_analysis` in `proposed_structure.json` before creating the final page list.
3. For every candidate learning unit, record its source location, candidate objective, concepts, prerequisites, unit type, split signals, decision, and rationale.
4. Apply the explicit split and combine tests in `.github/instructions/atomisation-guidelines.md`.
5. Build `pages` from the analysed units. A single source file may produce many pages.
6. Record `source_unit_ids` and `core_concept_ids` on every page so that generated content remains traceable to both the source and the discipline-independent mathematics.
7. Check that every candidate unit has a recorded decision. Never silently drop a unit.
8. Validate the proposal before generating the dependency graph:

```bash
python .github/skills/input-to-proposed-structure/validate_proposed_structure.py --proposed-file <output-dir>/proposed_structure.json
```

## Required pathway-design sequence

After source analysis and before finalising `pages`:

1. Normalise user-provided learner requirements into `generation_context.profiles`. Record inferred information in `assumptions_requiring_review`.
2. Extract discipline-independent definitions, expressions, conditions, and dependencies into `core_concept_model`.
3. Create one `learning_pathways` entry per learner profile.
4. Give each pathway a discipline-relevant entry point, ordered page sequence, required and optional concepts, adaptation strategy, and pedagogical rationale.
5. Preserve canonical mathematics across pathways. Adapt entry points, ordering, vocabulary, examples, implementation emphasis, proof depth, and assessment rather than changing definitions or results.
6. Run the validator to check all profile, concept, source-unit, pathway, prerequisite, and page references.
7. Generate the global dependency graph and the per-profile pathway graphs.

## Guardrails

- Preserve existing platform content boundaries.
- Mark proposed prerequisite gaps as `status: "missing"`.
- Keep each page focused on one learning objective.
- Do not interpret "one learning objective per page" as "one page per input file".
- Do not combine introduction, application, derivation, proof, exercise, and extension material merely to produce a single disciplinary overview.
- If one strong split signal or two supporting split signals apply, split by default unless the proposal records a concrete reason why the units are inseparable.
- The number of requested disciplines affects adaptation, not the number of learning units discovered in the source.
- If the same topic may be taught to different disciplinary audiences, capture the discipline context and the intended adaptation in the proposed structure, including tailored examples and a suitable teaching sequence.
- A required pathway step must not depend on an optional step.
- Every proposed prerequisite used by a pathway page must appear earlier in that pathway.
