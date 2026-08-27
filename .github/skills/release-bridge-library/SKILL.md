---
name: release-bridge-library
description: Deterministically verify and freeze an approved RQ2 bridge-library candidate as a released bridge catalog. Use after bridge-library-validation-report.json passes and bridge-library-review.json is fully approved. Reject stale hashes, incomplete reviews, changed curriculum/pathway authorities, invalid candidates, and existing release targets. Do not build, revise, or approve bridge content.
---

# Release Bridge Library

Freeze one approved bridge-library candidate without changing its teaching
content, sources, boundaries, or dependency bindings.

## Required inputs

Require exactly these paths:

- `bridge-library-candidate.json`;
- its passing `bridge-library-validation-report.json`;
- its completed, approved `bridge-library-review.json`;
- a new output directory.

Read `references/release-policy.md` before release.

## Workflow

1. Confirm the review records `review_status=approved`, an approved overall
   decision, a reviewer ID and role, a reviewed time, and approved decisions for
   every bridge and all five review fields.
2. Run only the deterministic gate:

   ```bash
   python3 .github/skills/release-bridge-library/scripts/release_bridge_library.py \
     --workspace-root . \
     --candidate <candidate-dir>/bridge-library-candidate.json \
     --validation-report <candidate-dir>/bridge-library-validation-report.json \
     --review <candidate-dir>/bridge-library-review.json \
     --output-dir <new-release-dir>
   ```

3. On failure, stop. Do not edit the candidate or review and do not leave a
   partial release.
4. On success, verify:

   ```bash
   shasum -a 256 -c <new-release-dir>/released-bridge-catalog.sha256
   ```

5. Say `released` only when the checksum passes, the release validation has
   zero errors, and all five artifacts exist.

## Output contract

The output directory contains only:

- `released-bridge-catalog.json`;
- `frozen-bridge-library-review.json`;
- `frozen-bridge-library-validation-report.json`;
- `released-bridge-catalog.sha256`;
- `bridge-library-release-report.json`.

The release transition changes only root and bridge `status` values from
`candidate` to `released` and adds a root `approval` record. The catalog is the
file supplied to downstream pathway validation with `--bridge-catalog`.

## Boundaries

- Never overwrite an existing release directory.
- Never release a pending or revision-required review.
- Never fill review decisions or repair candidate content.
- Never change learning outcomes, teaching content, sources, boundaries,
  learner demand, RC bindings, or authority hashes.
- Treat recorded reviewer identity exactly as written; do not describe a
  pseudonymous or model-assisted record as independent expert review.
