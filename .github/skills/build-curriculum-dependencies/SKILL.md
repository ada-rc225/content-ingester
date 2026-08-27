---
name: build-curriculum-dependencies
description: Build, revise, and deterministically validate curriculum dependency-model candidates from one released Frozen Reference Contract, then create hash-bound pending human-review templates. Use after the Grounding Release Gate for an initial RC-item dependency candidate or after a completed revision-required dependency review to create a bounded next-version candidate. Do not use to generate lessons, choose content for a learner profile, approve dependencies, release curriculum models, or modify Contract mathematics.
---

# Build curriculum dependencies

Create or revise one reviewable dependency-model candidate bound to a released
Frozen Reference Contract.

## Preconditions

Select exactly one mode:

- `initial`: require one released `frozen_reference_contract.json` and one new
  candidate output directory.
- `revision`: additionally require the parent `contract-dependencies.json` and
  its completed, hash-bound `curriculum-dependency-review.json` with both root
  and overall status `revision_required`.

Reject candidate Contracts, raw sources, learner profiles, task briefs, adapted
lessons, and evaluator output as mathematical authority. In revision mode, use
the prior candidate only as the starting proposal and the verified review only
as bounded change authority; the Frozen Contract remains mathematical authority.

Read `references/dependency-classification-rules.md` before proposing relations.
Do not load the JSON schema into the writing context.

## Initial mode

1. Verify the release and create a compact Contract view by running:

   ```bash
   python3 .github/skills/discipline-aware-teaching-adaptation/scripts/prepare_frozen_grounding.py \
     --workspace-root . \
     --contract <release-dir>/frozen_reference_contract.json \
     --output <candidate-dir>/dependency-build-receipt.json \
     --view-output <candidate-dir>/dependency-contract-view.json
   ```

   Stop on any release, approval, hash, source, inventory, or validation error.

2. Read only the receipt, compact view, and classification rules. Create
   `<candidate-dir>/contract-dependencies.json` conforming to
   `references/dependency-model.schema.json`. Use builder version `1.1`.

3. Include every non-excluded RC item exactly once. Use only item IDs in the
   bound Contract. Distinguish hard, explanatory, implementation, co-requisite,
   and recommended-neighbour relationships. Give every item at least one
   rationale. Use a fallback only for omitted explanatory dependencies; never
   use it to bypass a hard dependency.

4. Record missing external concepts as prerequisite candidates. A candidate may
   identify a `bridge_candidate_id`, but it must use `status=candidate` and must
   not contain generated bridge teaching content or claim release approval.

5. Run:

   ```bash
   python3 .github/skills/build-curriculum-dependencies/scripts/validate_dependency_model.py \
     --workspace-root . \
     --contract <release-dir>/frozen_reference_contract.json \
     --candidate <candidate-dir>/contract-dependencies.json \
     --output <candidate-dir>/dependency-validation-report.json
   ```

6. Patch only the candidate on validation failure and rerun. Continue only when
   the report has `valid=true`.

7. Generate the human-review template only after validation passes:

   ```bash
   python3 .github/skills/build-curriculum-dependencies/scripts/create_dependency_review.py \
     --workspace-root . \
     --candidate <candidate-dir>/contract-dependencies.json \
     --validation-report <candidate-dir>/dependency-validation-report.json \
     --output <candidate-dir>/curriculum-dependency-review.json
   ```

   Do not hand-author this file. The generator binds it to the exact candidate
   and validation-report hashes and initializes every field and overall
   decision to `pending`. Stop if the output already exists or the candidate
   changed after validation.

## Revision mode

1. Use a new output directory and repeat the Frozen Contract preflight from
   initial step 1. Never write into the parent candidate directory.

2. Verify the completed parent review and create the immutable revision scope:

   ```bash
   python3 .github/skills/build-curriculum-dependencies/scripts/prepare_dependency_revision.py \
     --workspace-root . \
     --contract <release-dir>/frozen_reference_contract.json \
     --parent-candidate <parent-dir>/contract-dependencies.json \
     --parent-review <parent-dir>/curriculum-dependency-review.json \
     --output <candidate-dir>/dependency-revision-receipt.json
   ```

   Stop if the review is pending, incomplete, approved, stale, bound to another
   Contract or candidate, missing reviewer identity, or has no requested change.

3. Read the new compact Contract view, parent candidate, revision receipt, and
   classification rules. Do not use the parent review directly after the receipt
   exists. Create the receipt's exact `next_model_id`, preserve all unmarked
   fields, apply every marked change, use builder version `1.1`, and reset the
   candidate to `review_status=unreviewed` and `approval=null`.

4. Run the base validator as in initial step 5, then validate revision scope:

   ```bash
   python3 .github/skills/build-curriculum-dependencies/scripts/validate_dependency_revision.py \
     --workspace-root . \
     --parent-candidate <parent-dir>/contract-dependencies.json \
     --parent-review <parent-dir>/curriculum-dependency-review.json \
     --revision-receipt <candidate-dir>/dependency-revision-receipt.json \
     --candidate <candidate-dir>/contract-dependencies.json \
     --dependency-validation-report <candidate-dir>/dependency-validation-report.json \
     --output <candidate-dir>/dependency-revision-validation-report.json
   ```

   Stop on unreviewed changes, unapplied requested fields, invalid model-version
   increments, stale hashes, unauthorized concept removal, or base-validation
   failure. Do not broaden the scope to make validation pass; require an amended
   human review instead.

5. Generate a fresh pending review bound to both validation layers:

   ```bash
   python3 .github/skills/build-curriculum-dependencies/scripts/create_dependency_review.py \
     --workspace-root . \
     --candidate <candidate-dir>/contract-dependencies.json \
     --validation-report <candidate-dir>/dependency-validation-report.json \
     --revision-receipt <candidate-dir>/dependency-revision-receipt.json \
     --revision-validation-report <candidate-dir>/dependency-revision-validation-report.json \
     --output <candidate-dir>/curriculum-dependency-review.json
   ```

   Never inherit parent approvals. Every new field and overall decision must be
   `pending`, with null reviewer and comments.

## Boundaries

- Produce `lifecycle_status=candidate`, `review_status=unreviewed`, and
  `approval=null` only.
- Produce `curriculum-dependency-review.json` with `review_status=pending`, a
  null reviewer, and no machine-supplied approvals or review comments.
- Preserve parent artifacts. Refuse same-directory revision and existing output
  files; increment only the dependency-model version.
- Never treat review comments as permission to change fields that the review did
  not explicitly mark `revision_required`.
- Do not infer curriculum inclusion, a common core, or a canonical sequence.
- Do not read or use a learner profile; the dependency model is topic-level.
- Do not create, approve, or release prerequisite bridges.
- Do not change canonical statements, formulas, conditions, or prohibited drift.
- Treat the model as an auditable proposal for later subject/curriculum review,
  not proof that every pedagogical dependency is uniquely correct.
