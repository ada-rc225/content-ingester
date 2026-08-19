# Curriculum dependency classification rules

## Relationship types

- `hard_dependencies`: RC items whose mathematical meaning or valid statement
  is necessary before the current item can be taught as selected. Omission is
  not repairable by a shorter explanation.
- `explanatory_dependencies`: RC items that support a derivation or deeper
  explanation but may be omitted when an explicit fallback is available.
- `implementation_dependencies`: RC items required to implement or diagnose the
  current item without changing its mathematical statement.
- `co_requisite_item_ids`: items intended to be introduced together where a
  directed prerequisite would be artificial. Do not duplicate them in another
  relationship category.
- `recommended_neighbours`: useful sequencing proximity only. This relation is
  not a coverage or validity requirement.

Directed hard, explanatory, and implementation relations must form an acyclic
graph. Prefer the weakest defensible relationship: do not label an item hard
merely because the source presented it earlier.

## Fallback rules

Set `fallback_when_explanatory_dependencies_omitted.allowed=true` only when the
current item remains accurate and teachable without one or more explanatory
dependencies. State the resulting depth boundary, such as presenting a theorem
and its hypotheses without the full derivation. A fallback cannot waive hard or
implementation dependencies.

When no explanatory dependency exists, set `allowed=false` and `instruction`
to `null`.

## External prerequisite concepts

Use an external prerequisite only for a concept not represented by any RC item
but plausibly needed to understand a selected item. Record:

- a stable lower-case `concept_id`;
- affected RC item IDs;
- whether the concept is required or recommended;
- a proposed `bridge_candidate_id`;
- a narrow content boundary and rationale.

The dependency candidate does not contain bridge teaching prose, formulas, or
approval. Every bridge remains `candidate` until a separate grounded review and
release workflow exists.

## Prohibited inferences

- Do not change Contract mathematics or repair perceived source errors.
- Do not use learner-profile preferences to construct topic-level dependencies.
- Do not convert source order directly into hard dependency edges.
- Do not treat common co-occurrence as mathematical necessity.
- Do not use a dependency model to decide RQ2 include/exclude outcomes.
- Do not describe an unreviewed dependency candidate as approved or released.

