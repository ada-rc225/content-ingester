---
name: discipline-aware-teaching-adaptation
description: Replan and rewrite authoritative mathematical or computational teaching material for a specified learner discipline, education level, prior knowledge, and learning goal. Use when adapting Markdown, Jupyter notebooks, PDF, or PPTX teaching material into a grounded long-form lesson without Atomic Learning page splitting, slugs, metadata, prerequisite graphs, or publishing.
---

# Discipline-aware teaching adaptation

Transform authoritative teaching material into one coherent, audience-specific lesson while preserving its mathematical and algorithmic meaning.

## Resolve run directories

Resolve at run start:

- `TEACHING_ADAPTER_INPUTS_DIR` (default: `inputs/content-to-ingest`)
- `TEACHING_ADAPTER_PROFILES_DIR` (default: `inputs/learner-profiles`)
- `TEACHING_ADAPTER_OUTPUTS_DIR` (default: `adapted-materials`)

Pass resolved paths through the whole run. Keep every generated artifact under the resolved adapter output directory.

## Read required references

Before adaptation, read:

- `references/grounding-and-adaptation-rules.md`
- `references/output-contract.md`

Read `references/evaluation-rubric.md` before the final review.

## Workflow

### 1. Establish the run target

Identify:

- authoritative source file or files;
- one learner profile;
- target topic or scope;
- output folder `<adapter-output-dir>/<topic>/<profile-id>/`.

Adapt one learner profile per output folder. Never overwrite another profile's result.

If the user supplies learner information in prose, normalise it into `learner_profile.json` using `references/learner-profile.schema.json`. Record uncertain inferences in `assumptions_requiring_review`.

### 2. Extract the source

Read all relevant source material before drafting.

- Preserve notebook cell order and distinguish Markdown, code, and outputs.
- For PDFs, use the repository PDF extractor when available.
- For PPTX files, use the repository PPTX extractor when available.
- Record the source path and a stable section, heading, slide, page, or cell locator for every core item.

Treat source material as authoritative for definitions, formulae, assumptions, algorithms, results, and code semantics.

### 3. Build the invariant concept record

Identify:

- definitions;
- formulae and notation;
- assumptions and domains;
- theorem statements and conclusions;
- algorithm steps;
- theory-to-code correspondences;
- source examples and exercises;
- dependencies between concepts.

Do this before selecting discipline analogies. Do not silently repair, replace, or extend questionable source mathematics. Record source defects or ambiguities for review.

### 4. Plan the adaptation

Create `adaptation_plan.json` before writing the lesson.

Plan:

- discipline-relevant entry point;
- long-form chapter sequence;
- prerequisite bridges;
- terminology mappings;
- representative domain problem;
- proof and derivation depth;
- computational implementation emphasis;
- exercises and assessments;
- retained, reordered, summarised, deferred, and omitted source sections.

The chapter structure is pedagogical organisation within one lesson. It is not Atomic Learning atomisation.

Pause for approval when the user requests plan review. Otherwise proceed and clearly record all assumptions.

### 5. Write the adapted lesson

Create `adapted_content.md`.

- Begin from a problem or representation familiar to the learner profile.
- Introduce standard mathematical terminology no later than the point where the domain bridge has established intuition.
- Preserve canonical definitions, equations, conditions, and algorithm semantics.
- Make theory-to-implementation links explicit.
- Match language, proof depth, code complexity, and exercises to the profile.
- State the boundary of every analogy that could otherwise mislead.
- Do not mention Atomic Learning pages or the downstream ingestion workflow in the lesson.

### 6. Create provenance

Create `provenance.json` using `references/provenance.schema.json`.

For each mathematical or algorithmic core item, record:

- source locator;
- transformation type;
- preservation status;
- destination chapter.

Classify transformations as:

- `preserved`;
- `reordered`;
- `summarised`;
- `discipline_bridge`;
- `implementation_bridge`;
- `deferred`;
- `omitted`.

Every deferred or omitted item requires a reason.

### 7. Review

Use `references/evaluation-rubric.md`.

Check:

- mathematical fidelity;
- source coverage and traceability;
- disciplinary authenticity;
- learner-profile alignment;
- adaptation depth;
- theory-to-implementation alignment;
- analogy boundaries;
- internal coherence.

Write `adaptation_summary.md` with decisions, assumptions, source issues, and review findings.

## Required outputs

Produce exactly these core artifacts:

```text
<adapter-output-dir>/<topic>/<profile-id>/
├── learner_profile.json
├── adaptation_plan.json
├── adapted_content.md
├── provenance.json
└── adaptation_summary.md
```

Source-derived images or data may be placed in `resources/`.

## Boundaries

Do not:

- split the lesson into Atomic Learning pages;
- generate page slugs or page metadata;
- create prerequisite or related-page graphs;
- copy platform licence files;
- publish or upload content;
- present added domain analogies as source-authored claims;
- add unsupported mathematical results;
- hide source errors by silently correcting them.

The adapted lesson is derived teaching material, not a new authoritative source.
