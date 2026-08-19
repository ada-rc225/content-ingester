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

## Authorised changes

- assign a new `pathway_id`;
- set `plan_status=complete` after all requirements resolve;
- set requirement `resolution_status=released` and record its released contract
  ID;
- append a release-evidence sentence to requirement rationale;
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
