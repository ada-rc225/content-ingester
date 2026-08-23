# Gradient Descent unified fixed-pathway plans

This directory contains the deterministic P0/P1 control pathways for the RQ2
Gradient Descent pilot. They are bound to the released Gradient Descent Frozen
Reference Contract and the shared second-year learning request.

## P0

`p0/pathway-plan.json` normalizes the fixed baseline defined by:

- `experiments/rq2/specs/gradient-descent/canonical-pathway.json`;
- `experiments/rq2/specs/gradient-descent/common-core.json`;
- `experiments/rq2/specs/gradient-descent/p0-normalization-map.json`;
- the released Gradient Descent Frozen Reference Contract; and
- `experiments/rq2/learning-requests/gradient-descent-second-year.json`.

The P0 baseline selects 12 of 30 Contract items in six ordered learning units.
It covers basic Gradient Descent, constant and Armijo step selection, and convex
and strongly convex convergence. Acceleration, stochastic/adaptive methods,
Newton methods, and BFGS remain outside the fixed baseline.

## P1

Each `p1/<profile>/pathway-plan.json` is a deterministic exact structural copy
of P0. Only the pathway identity, condition, profile binding, baseline binding,
and generation metadata differ. Selection, goal mappings, grouping,
prerequisites, sequence, bridge state, and scope summary are identical.

All four pathway validation reports currently have `valid=true` and zero
errors. The learning request, profiles, and fixed-baseline specifications remain
pilot candidates requiring their recorded human review before confirmatory use.
