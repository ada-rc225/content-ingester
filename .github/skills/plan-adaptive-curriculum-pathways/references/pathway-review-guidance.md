# Pathway-plan review guidance

Review the candidate, assessment, profile, P0 baseline, and validation report.
Do not assess lesson prose: it does not exist yet. Do not add time or unit-duration
requirements; output length belongs to the later Composer word-count protocol.

## Completing decisions

For every field, replace `pending` with `approved`, `revision_required`, or
`not_applicable`. Set each record decision to:

- `approved` when no field in that record requires revision;
- `revision_required` when at least one field requires revision, with a comment
  stating the exact requested change.

For a revision, set root `review_status`, overall decision, reviewer identity,
reviewed time, and overall comment. The Planner never fills these fields.

## What each section controls

- `selection_reviews`: include/exclude, role, rationale, and profile evidence for
  one RC item.
- `concept_reviews`: mastery/confidence, profile evidence/rationale, and the
  corresponding bridge requirement.
- `learning_goal_reviews`: coverage, supporting item IDs, and mapping rationale.
- `structure_review`: grouping, order, prerequisites, unit purpose, and goal IDs.
- `pathway_change_reviews`: whether a declared structural change is accurate and
  whether its profile basis and rationale match the actual plan.
- `scope_review`: whether the overall selection, failure/convergence subset, and
  profile-specific scope are pedagogically appropriate.

## Cross-field revisions

Mark every field that must change. For example:

- excluding an item normally also requires marking unit grouping, affected goal
  mappings, affected bridge requirements, and affected pathway-change records;
- changing mastery normally also requires marking `bridge_requirement` when the
  bridge set or status must change;
- changing unit IDs requires revision of every structure field;
- correcting a reorder claim may require structure order plus change structural
  accuracy and rationale.

If the revision cannot remain coherent without changing an approved field,
amend the review before invoking revision mode.
