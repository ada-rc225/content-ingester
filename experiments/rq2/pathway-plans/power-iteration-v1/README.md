# Power Iteration unified fixed-pathway plans

This directory contains protocol-v0.3 pilot planning artifacts generated without
LLM selection or rewriting.

## P0

`p0/pathway-plan.json` is the deterministic unified-schema normalization of:

- `experiments/rq2/specs/power-iteration/canonical-pathway.json`;
- `experiments/rq2/specs/power-iteration/common-core.json`;
- `experiments/rq2/specs/power-iteration/p0-normalization-map.json`;
- the Power Iteration Frozen Reference Contract; and
- the shared second-year learning request.

Its normalization receipt binds all inputs and the output by SHA-256. The plan
contains all 18 canonical Contract items in the original eight learning units
and original order.

## P1

Each `p1/<profile>/pathway-plan.json` is an exact controlled P0 copy. Only these
root fields differ from P0:

- `pathway_id`;
- `condition`;
- `profile_binding`;
- `baseline_pathway_binding`;
- `generated_by`.

The copy receipt records this policy and binds P0, profile, and output hashes.
Every adjacent validation report currently has `valid=true` and zero errors.

## P2 review state

Each current `p2/<profile>/run-01/` contains a validated provisional P2 plan,
concept assessment, and hash-bound `pathway-plan-review.json`. Every review field
and overall decision is initially `pending`. Human review covers content scope,
concept mastery and bridges, goal support, grouping, sequence, prerequisites,
and rationale accuracy. It does not assess time or add unit-duration limits.

If a review requires changes, invoke Adaptive Curriculum Pathway Planner v1.1
in `revision` mode and write to a new sibling directory. The parent directory is
immutable. Revision preflight authorizes exact fields, and revision validation
rejects any unmarked change. The revised candidate receives a new pending review.

These are pilot artifacts. The normalization map, shared learning request, and
learner profiles retain their recorded review requirements and must be approved
before confirmatory generation.
