---
name: build-grounded-bridge-library
description: Build or revise a compact, web-sourced RQ2 prerequisite bridge-library candidate from approved P2 pathway requirements, validate its authority and source bindings, and generate a hash-bound pending human-review form. Use when unresolved pathway bridge candidates must become reviewable prerequisite teaching inputs. Do not use for pathway selection, lesson composition, human approval, or release.
---

# Build Grounded Bridge Library

Create one compact candidate library. Keep bridge governance deliberately
lighter than pathway governance because pathway adaptation is the RQ2 focus.

## Workflow

1. Require a released Frozen Curriculum Model and approved reviews for every
   supplied P2 pathway. Refuse a reused output directory.
2. Read `references/authoring-rules.md` completely.
3. Extract the exact union of unresolved `candidate` bridge requirements. Merge
   repeated concepts and preserve requesting profile IDs and RC-item bindings.
4. Search official documentation or institutional course materials. Write
   `bridge-library-candidate.json` against
   `experiments/rq2/schemas/bridge-library.schema.json`.
5. Run `scripts/validate_bridge_library.py`.
6. If validation passes, run `scripts/create_bridge_library_review.py`. Leave
   every field decision, bridge decision, and overall decision `pending`.

## Commands

```bash
python3 .github/skills/build-grounded-bridge-library/scripts/validate_bridge_library.py \
  --workspace-root . \
  --model curriculum-models/power-iteration-v1/release/frozen-contract-dependencies.json \
  --candidate <candidate-dir>/bridge-library-candidate.json \
  --pathway-review <pathway-plan.json> <pathway-plan-review.json> \
  --output <candidate-dir>/bridge-library-validation-report.json

python3 .github/skills/build-grounded-bridge-library/scripts/create_bridge_library_review.py \
  --workspace-root . \
  --candidate <candidate-dir>/bridge-library-candidate.json \
  --validation-report <candidate-dir>/bridge-library-validation-report.json \
  --output <candidate-dir>/bridge-library-review.json
```

Repeat `--pathway-review` for every pathway. In revision mode, use the completed
review as instructions, write a new candidate directory, and rerun the same two
commands. Do not create a revision receipt or inherit approval.

After an authorised reviewer approves the complete new review, use
`release-bridge-library`; do not change candidate status in this Builder.

## Boundaries

- Generate only bridges requested by supplied approved pathways.
- Copy candidate identity, supported RC items, and boundary from the Frozen
  Curriculum Model; never invent or broaden them.
- Bind every teaching-content block to at least one source.
- Do not duplicate Frozen Reference Contract target content.
- Do not mark candidates approved or released.
- Do not generate pathways, lessons, evaluations, or release artifacts.
