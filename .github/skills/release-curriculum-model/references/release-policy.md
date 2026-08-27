# Curriculum model release policy

## State transition

The gate may transform only release-state metadata:

- model `lifecycle_status`: `candidate` to `frozen`;
- model `review_status`: `unreviewed` to `approved`;
- each item `review_status`: `unreviewed` to `approved`;
- model `approval`: `null` to the hash-bound review and release record.

Every other candidate field must be preserved exactly. In particular, an
external prerequisite concept remains a proposal with `status=candidate`.

## Approval completeness

Release requires:

- root and overall review decisions are `approved`;
- reviewer ID, reviewer role, and reviewed time are present;
- every item and concept record decision is `approved`;
- every field decision is `approved` or `not_applicable`;
- `not_applicable` is used only for an absent relation or inactive fallback;
- review coverage exactly equals candidate item and concept coverage.

## Immutable bindings

The gate verifies current SHA-256 values for the Frozen Contract, candidate,
base validation report, review, and—when present—the revision receipt, revision
validation report, parent candidate, and parent review. It reruns base validation
and revision-scope validation before publication.

## Failure behavior

Any mismatch is a release failure. The gate performs no content repair and emits
no partial release directory. Existing release targets are never overwritten.
