---
name: release-curriculum-model
description: Deterministically verify and freeze one independently approved curriculum dependency-model candidate that is bound to a released Frozen Reference Contract. Use after curriculum-dependency-review.json is complete and approved. Reject stale hashes, incomplete or revision-required reviews, invalid base or revision validation, changed source contracts, and existing release targets. Do not build dependencies, edit review decisions, select learner-specific content, or release prerequisite bridge content.
---

# Release curriculum model

Freeze an approved dependency model without changing its pedagogical content or
the human review decisions.

## Required inputs

Require exactly these paths:

- a released `frozen_reference_contract.json`;
- the candidate `contract-dependencies.json`;
- its passing `dependency-validation-report.json`;
- its independently completed `curriculum-dependency-review.json`;
- a new versioned output directory.

If the review has a non-null `revision_binding`, the recorded revision receipt,
revision validation report, parent candidate, and parent review are also required
and are resolved from the binding. Do not guess substitutes.

Read `references/release-policy.md` before release. Do not load JSON schemas into
the writing context; the release script fingerprints them.

## Release workflow

1. Confirm the review records `review_status=approved`, an approved overall
   decision, a reviewer ID and role, and a reviewed time. A placeholder or model-
   invented identity is not independent review unless the user confirms it is the
   authorised record.
2. Run only the deterministic gate:

   ```bash
   python3 .github/skills/release-curriculum-model/scripts/release_curriculum_model.py \
     --workspace-root . \
     --contract <release-dir>/frozen_reference_contract.json \
     --candidate <candidate-dir>/contract-dependencies.json \
     --validation-report <candidate-dir>/dependency-validation-report.json \
     --review <candidate-dir>/curriculum-dependency-review.json \
     --output-dir <new-release-dir>
   ```

3. On failure, stop. Do not edit the candidate or review, invent approval, or
   bypass a failing check. Return the failing code to the Builder or reviewer.
4. On success, verify the model fingerprint:

   ```bash
   shasum -a 256 -c <new-release-dir>/frozen-curriculum-model.sha256
   ```

5. Read the frozen validation and release reports. Say `released` only when the
   gate reports zero errors, the checksum passes, and all five artifacts exist.

## Output contract

The new output directory contains only:

- `frozen-contract-dependencies.json`;
- `frozen-curriculum-review.json`;
- `frozen-curriculum-validation-report.json`;
- `frozen-curriculum-model.sha256`;
- `curriculum-release-report.json`.

The frozen model changes only release-state metadata: root and item review status
become `approved`, lifecycle becomes `frozen`, and approval evidence is attached.
All dependency relations, rationales, confidence values, and external prerequisite
records remain unchanged. External prerequisite records retain `status=candidate`:
freezing the dependency model does not release bridge teaching content.

## Boundaries

- Never overwrite an existing release directory.
- Never release a pending, in-review, or revision-required review.
- Never act as the dependency Builder or human reviewer.
- Never modify Frozen Contract mathematics or dependency content during release.
- Never turn a `bridge_candidate_id` into usable teaching content or approval.
- Never use a learner profile or choose a pathway; those are downstream tasks.
- Treat release as an auditable binding to the recorded review, not proof that the
  dependency model is the only pedagogically valid representation.
