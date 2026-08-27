---
name: compose-pathway-constrained-teaching
description: Render and deterministically validate one continuous RQ2 student-facing lesson from a complete unified P0, P1, or P2 pathway. Use when generating controlled P0/P1/P2 pilot or confirmatory lessons, enforcing condition-specific profile access, selected Contract scope, released bridge scope, pathway order, input hash binding, executable Python blocks, and a shared word-count protocol. Do not use for pathway planning, bridge construction, human evaluation, or mathematical approval.
---

# Compose Pathway-Constrained Teaching

Create one lesson from one already validated, complete pathway. Use the same
workflow for P0, P1, and P2 so that the experimental treatment is the pathway
and profile permission, not a different writing system.

## Workflow

1. Require an unused run directory, run ID, fixed timestamp, provider, model,
   access route, prompt version, complete pathway, passing pathway validation
   report, and shared word-count protocol. Supply a released bridge catalog only
   for P2 pathways containing bridge units.
2. Run `scripts/prepare_composition_inputs.py`. Stop on any stale binding,
   invalid pathway report, unresolved bridge, condition-policy violation, or
   existing output directory.
3. Read `references/composition-policy.md` completely. Then compose from
   `composition-input-view.json` only. Do not reopen authority files, other
   profiles, other condition outputs, or evaluation results.
4. Write `lesson.md` and `lesson-map.json` using
   `references/lesson-map.schema.json`. Keep audit IDs out of visible prose.
   Place `<!-- section: SEC-NN -->` immediately before each mapped `##` heading.
5. Execute every fenced Python block:

   ```bash
   python3 .github/skills/discipline-aware-teaching-adaptation/scripts/execute_code_blocks.py \
     --content <run-dir>/lesson.md \
     --output <run-dir>/code-validation.json
   ```

6. Run `scripts/validate_composer_outputs.py` with the fixed generation
   metadata. It deterministically writes `lesson-manifest.json` and
   `lesson-validation-report.json`.
7. If validation fails, patch only `lesson.md` or `lesson-map.json`, rerun code
   execution, and rerun final validation. Never alter the receipt or view.

## Condition isolation

- P0 receives no profile and must remain discipline-neutral.
- P1 receives exactly one profile but must render the exact fixed P0 selection,
  grouping, prerequisites, and sequence encoded in its P1 pathway.
- P2 receives exactly one profile and renders its already frozen selection,
  units, sequence, and released bridges. Never replan during composition.

## Completion contract

Finish only with:

- `composition-input-receipt.json`
- `composition-input-view.json`
- `lesson.md`
- `lesson-map.json`
- `code-validation.json`
- `lesson-manifest.json`
- `lesson-validation-report.json`

The deterministic report proves bindings, declared selected-content coverage,
pathway-order preservation, released-bridge mapping, code execution, and length
compliance. It does not certify semantic mathematical correctness, pedagogical
quality, or learning gains; those belong to the independent RQ2 evaluation.
