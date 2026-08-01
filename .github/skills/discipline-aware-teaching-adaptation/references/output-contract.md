# Output contract

## Directory

```text
<adapter-output-dir>/<topic>/<profile-id>/
├── learner_profile.json
├── adaptation_plan.json
├── adapted_content.md
├── provenance.json
├── adaptation_summary.md
└── resources/
```

Create `resources/` only when the adapted lesson needs source-derived assets or data.

## learner_profile.json

Validate against `learner-profile.schema.json`.

It records the actual adaptation target, including inferred assumptions. Do not rely only on the chat prompt because the artifact must be reproducible.

## adaptation_plan.json

Validate against `adaptation-plan.schema.json`.

It records the teaching design before prose generation:

- entry point;
- chapter sequence;
- bridges;
- depth;
- implementation;
- assessment;
- source coverage decisions.

## adapted_content.md

Write one coherent lesson. Chapters are allowed and expected. Do not create platform page boundaries, slugs, metadata, prerequisite lists, or publication instructions.

Use standard Markdown. Preserve mathematical notation faithfully. Reference local resources with relative paths.

## provenance.json

Validate against `provenance.schema.json`.

Each record must connect a source locator to an adapted destination or record why it was deferred or omitted.

## adaptation_summary.md

Include:

- target profile;
- major structural changes;
- mathematical invariants checked;
- added disciplinary and implementation bridges;
- deferred or omitted material;
- assumptions requiring review;
- source defects;
- final rubric findings.
