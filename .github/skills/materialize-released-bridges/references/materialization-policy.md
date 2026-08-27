# Released bridge materialization policy

## Fixed insertion rule

For each parent bridge requirement, preserve requirement order and:

1. Require an exact catalog match on `concept_id` and `bridge_candidate_id`.
2. Find the first unit in `instruction_sequence` whose `contract_item_ids`
   intersects `required_by_item_ids`.
3. Insert exactly one `prerequisite_bridge` unit immediately before that first
   consumer.
4. Copy the first consumer's original prerequisites to the bridge unit.
5. Append the bridge unit ID to the first consumer's prerequisites.
6. Assign to the bridge unit the ordered union of learning goals from every
   consuming Contract unit.

Use unit IDs `BRIDGE-001`, `BRIDGE-002`, ... in requirement order. Refuse any
collision.

## Legacy bridge-requirement normalization

Some approved Planner outputs predate the canonical bridge-requirement shape.
Before insertion, the materializer may normalize only the child copy of an
exactly catalog-bound, approved parent pathway:

1. Preserve a canonical `requirement_id` when it equals the ordered
   `BRQ-001`, `BRQ-002`, ... identifier; when it is absent or only a legacy
   `bridge_requirement_id` exists, generate the canonical ID from requirement
   order.
2. Preserve a non-empty `rationale`. Otherwise rename a non-empty legacy
   `reason`; if neither exists, copy the rationale for the same `concept_id`
   from the parent's hash-bound profile-concept assessment. The assessment
   mastery must equal the requirement mastery.
3. Add a missing `released_bridge_contract_id` as `null` before resolving it.
4. Remove only the known legacy aliases `bridge_requirement_id`,
   `triggering_item_ids`, `status`, and `reason`. Their duplicate item/status
   values must agree with the canonical fields; conflicting aliases fail.
5. Record every compatibility action on the corresponding resolved-bridge
   receipt entry.

Unknown fields, conflicting aliases, invalid canonical IDs, missing assessment
evidence, or semantic changes fail closed. Normalization may not change
`concept_id`, `bridge_candidate_id`, `required_by_item_ids`, `learner_mastery`,
or the parent's unresolved status, and it never edits the parent artifact.

## Authorised changes

- assign a new `pathway_id`;
- set `plan_status=complete` after all requirements resolve;
- set requirement `resolution_status=released` and record its released contract
  ID;
- append a release-evidence sentence to requirement rationale;
- apply the bounded legacy bridge-requirement normalization above to the child
  copy only;
- add prerequisite-bridge units and insert them into `instruction_sequence`;
- add each bridge unit as a prerequisite of its first consumer;
- append one `add_prerequisite_bridge` pathway-change record;
- update `released_bridge_count`;
- replace generation metadata with materializer identity and time.

All other fields and the relative order of existing instruction units must be
preserved exactly.

## Evidence

Require the released catalog to bind the exact parent pathway and approved
review hashes. Bind the parent artifacts, catalog, release report, output plan,
resolved contracts, first consumers, and rule version in
`bridge-resolution-receipt.json`.
