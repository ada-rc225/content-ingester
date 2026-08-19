---
name: plan-adaptive-curriculum-pathways
description: Build or review-boundedly revise an RQ2 P2 learner-profile-driven pathway, validate dependency and provenance constraints, and create a hash-bound pending pathway-plan review. Use for initial P2 planning, human-review template creation, or revisions explicitly authorized by a completed pathway-plan-review.json. Do not use for P0/P1 generation, bridge-content generation, lesson rendering, evaluation, approval, or release.
---

# Plan Adaptive Curriculum Pathways

Create one auditable P2 plan without changing authority artifacts. Require the
caller to choose `initial` or `revision` mode and a new output directory.

## Initial mode

Require a released Frozen Reference Contract, released Frozen Curriculum Model,
shared learning request, one learner profile, and validated unified P0 plan.

1. Run `scripts/prepare_pathway_inputs.py` to verify releases and hashes.
2. Read `references/planning-rules.md` completely.
3. Write `profile-concept-assessment.json` and `pathway-plan.json` against their
   schemas. Use producer version `1.1`.
4. Run `experiments/rq2/scripts/validate_pathway_plan.py --phase pilot`.
5. Run `scripts/create_pathway_plan_review.py`. Leave every decision pending.

## Revision mode

Require the parent plan, assessment, passing validation report, completed review,
and a different new output directory.

1. Run `scripts/prepare_pathway_revision.py`. Stop if the review is pending,
   stale, incomplete, approved without revisions, or snapshot-tampered.
2. Run the ordinary input preflight using authorities bound by the parent plan.
3. Read `references/pathway-review-guidance.md`, then use only the parent
   artifacts, revision receipt, compact planning view, review comments, and
   planning rules. Apply all marked fields and preserve all unmarked fields. Use
   the receipt's next IDs.
4. Run unified pathway validation.
5. Run `scripts/validate_pathway_revision.py`. Stop on any out-of-scope change.
6. Generate a new fully pending review with
   `scripts/create_pathway_plan_review.py`, supplying both revision artifacts.

Do not silently make a consistency change outside the authorized scope. Request
an amended review instead.

## Review-template command

```bash
python3 .github/skills/plan-adaptive-curriculum-pathways/scripts/create_pathway_plan_review.py \
  --workspace-root . \
  --pathway <run-dir>/pathway-plan.json \
  --validation-report <run-dir>/pathway-validation-report.json \
  --assessment <run-dir>/profile-concept-assessment.json \
  --output <run-dir>/pathway-plan-review.json
```

## Boundaries

- Candidate or missing bridges make a plan provisional and cannot become units.
- After such requirements are separately approved and released, hand the
  approved provisional plan to `materialize-released-bridges`; do not use
  Planner revision mode for that release-state transition.
- Do not add unit-time estimates or time-review fields. Preserve legacy duration
  metadata only for compatibility; the Composer will enforce word-count limits.
- Learning units are planning units, not pages.
- Do not generate bridge content, lessons, P0/P1 artifacts, evaluations,
  approvals, or releases.
- Refuse overwrite in both modes.
