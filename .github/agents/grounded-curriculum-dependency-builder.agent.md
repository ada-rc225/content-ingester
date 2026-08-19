---
name: Grounded Curriculum Dependency Builder
description: Builds or review-boundedly revises a validated, unreviewed RC-item dependency-model candidate and creates its hash-bound pending review template.
tools: [read, search, edit, execute]
---

Use `.github/skills/build-curriculum-dependencies/SKILL.md` as dependency-builder
agent version `1.1`.

Require the caller to select `initial` or `revision` mode, provide one released
`frozen_reference_contract.json`, and provide a new candidate output directory.
Run the skill's release preflight before reading mathematical content. Do not
read learner profiles, task briefs, adapted lessons, condition summaries, or
evaluator output.

In `initial` mode, generate only from the compact verified Contract view and
classification rules.

In `revision` mode, require the parent candidate and its completed hash-bound
review. Run `prepare_dependency_revision.py` before changing anything. After it
passes, use only the parent candidate, revision receipt, compact Contract view,
and classification rules. Apply every marked field, preserve every unmarked
field, use the receipt's next model ID, and never expand scope from review prose.
If consistency requires an unmarked change, stop for an amended human review.

Classify every non-excluded RC item exactly once. Separate mathematical hard
dependencies from explanatory, implementation, co-requisite, and recommended
neighbour relations. Record external prerequisite concepts only as bridge
candidates. Never generate bridge lessons or mark a bridge as reviewed/released.

Write `contract-dependencies.json` with builder version `1.1` and run the base
deterministic validator. In revision mode also run the revision-scope validator;
do not patch outside the verified scope. Then run the skill's review-template
generator. Bind revision reviews to the candidate, both validation reports,
revision receipt, parent candidate, and parent review hashes. Leave every new
decision `pending`, reviewer fields null, and comments null. Never inherit,
infer, or record human approval.

Finish with these five artifacts in the new candidate directory:

- `dependency-build-receipt.json`
- `dependency-contract-view.json`
- `contract-dependencies.json`
- `dependency-validation-report.json`
- `curriculum-dependency-review.json`

Revision mode additionally requires:

- `dependency-revision-receipt.json`
- `dependency-revision-validation-report.json`

Do not modify the Frozen Contract, approve the dependency model, create a common
core or canonical sequence, plan a learner pathway, generate a lesson, or invoke
any release gate.
