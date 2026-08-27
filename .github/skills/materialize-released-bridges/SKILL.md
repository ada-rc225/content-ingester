---
name: materialize-released-bridges
description: Deterministically derive a bridge-resolved P2 pathway from an approved provisional pathway and a released bridge catalog. Use after Bridge Library Release Gate succeeds, when approved candidate bridge requirements must become released prerequisite-bridge units without replanning Contract selection, grouping, or learner judgements. Reject stale hashes, unmatched catalogs, non-approved parent reviews, and reused output directories.
---

# Materialize Released Bridges

Convert approved bridge requirements into released learning units without
replanning the pathway.

## Required inputs

Require:

- one approved provisional P2 `pathway-plan.json`;
- its approved `pathway-plan-review.json`;
- `released-bridge-catalog.json`;
- its `bridge-library-release-report.json`;
- a new pathway ID, fixed UTC generation time, and new output directory.

Read `references/materialization-policy.md` before execution.

## Workflow

1. Run the deterministic materializer:

   ```bash
   python3 .github/skills/materialize-released-bridges/scripts/materialize_released_bridges.py \
     --workspace-root . \
     --parent-pathway <approved-run>/pathway-plan.json \
     --parent-review <approved-run>/pathway-plan-review.json \
     --bridge-catalog <bridge-release>/released-bridge-catalog.json \
     --bridge-release-report <bridge-release>/bridge-library-release-report.json \
     --pathway-id <new-pathway-id> \
     --generated-at <fixed-UTC-timestamp> \
     --output-dir <new-run-dir>
   ```

2. Validate the result with the same released catalog:

   ```bash
   python3 experiments/rq2/scripts/validate_pathway_plan.py \
     --workspace-root . \
     --pathway <new-run-dir>/pathway-plan.json \
     --bridge-catalog <bridge-release>/released-bridge-catalog.json \
     --output <new-run-dir>/pathway-validation-report.json \
     --phase pilot
   ```

3. Verify that the report is valid, records the catalog path and SHA-256, the
   receipt binds the new pathway hash, `plan_status=complete`, and every
   requirement and prerequisite-bridge unit is released.

For an exactly catalog-bound historical parent whose bridge requirements use
the documented legacy aliases, the materializer deterministically normalizes
only the child copy according to `references/materialization-policy.md`. It
records each compatibility action in the receipt and never changes the parent.

## Outputs

The materializer creates only:

- `pathway-plan.json`;
- `bridge-resolution-receipt.json`.

The validation command adds `pathway-validation-report.json`. Do not create a
new full pathway review: the receipt binds the already approved pathway review
and the separately approved released bridge library.

## Boundaries

- Never overwrite the parent or an existing output directory.
- Never change Contract selection, existing unit order relative to other
  existing units, grouping, learning-goal mappings, concept assessment, or
  learner-profile judgements.
- Never resolve a bridge absent from the released catalog or absent from the
  catalog's exact parent pathway/review bindings.
- Never call Adaptive Curriculum Pathway Planner revision mode for this state
  transition.
- Never infer a legacy rationale from free text: use only the canonical
  rationale, the `reason` alias, or the same concept's rationale in the
  hash-bound profile-concept assessment, in that order.
- Stop if ordinary pathway validation fails.
