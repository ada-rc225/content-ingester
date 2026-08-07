---
name: discipline-aware-teaching-adaptation
description: Replan and rewrite supplied mathematical or computational teaching material for a specified learner discipline, education level, prior knowledge, and learning goal. Use for grounded long-form adaptation from Markdown, notebooks, PDF, PPTX, code, or text; produce claim-level provenance, source fingerprints, executable-code evidence, and RQ1-ready structured-grounding artifacts without Atomic Learning page splitting or publishing.
---

# Discipline-aware teaching adaptation

Create one coherent audience-specific lesson while preserving the supplied source's mathematical and algorithmic meaning. Treat this skill as structured-grounding condition C2, version `2.0`.

## Resolve directories

Resolve at run start and retain the resolved paths:

- `TEACHING_ADAPTER_INPUTS_DIR` (default `inputs/content-to-ingest`)
- `TEACHING_ADAPTER_PROFILES_DIR` (default `inputs/learner-profiles`)
- `TEACHING_ADAPTER_OUTPUTS_DIR` (default `adapted-materials`)

Keep every generated artifact under one run directory. For experiments, use the user-specified `experiments/.../c2-structured-grounding/run-NN/` directory.

## Read references

Before generating content, read:

- `references/grounding-and-adaptation-rules.md`
- `references/output-contract.md`

Before review, read `references/evaluation-rubric.md`. Use the JSON schemas named by the output contract; do not improvise their structure.

## Workflow

### 1. Record the run

Create `run_manifest.json` before drafting. Record the actual provider, model, access route, prompt/agent/skill versions, timestamp, source IDs, and whether executable code is required. Never guess unavailable model metadata; use a truthful explicit value such as `not-exposed-by-runtime` and note the limitation.

Normalise one learner target into `learner_profile.json`. Put uncertain inferences in `assumptions_requiring_review`.

### 2. Fingerprint and read every source

Run:

```bash
python .github/skills/discipline-aware-teaching-adaptation/scripts/build_source_manifest.py \
  --workspace-root . --source <source-file> --output <run-dir>/source_manifest.json
```

Repeat `--source` for multiple files. Read the complete relevant source after fingerprinting. Preserve notebook cell order and distinguish Markdown, code, and outputs. Use stable heading, line, cell, page, slide, or section locators.

### 3. Extract source claims before adaptation

Create `source_claims.json` before selecting analogies or writing prose. Assign stable `SRC-*` IDs to definitions, equations, assumptions, theorem results, algorithm steps, convergence conditions, code semantics, source examples, and exercises. Record conditions and one explicit coverage decision for every meaningful item.

Do not silently repair or extend questionable mathematics. Record defects for provenance review. Distinguish “consistent with the supplied source” from “mathematically verified by an independent authority.”

### 4. Plan the lesson

Create `adaptation_plan.json` before the lesson. Plan the entry point, coherent chapter sequence, prerequisite bridges, terminology, representative domain problem, derivation depth, implementation emphasis, assessment, and coverage decisions. This is chapter-level pedagogy, not Atomic Learning atomisation.

### 5. Generate content and its claim ledger

Create `adapted_content.md` and `claim_ledger.json` together.

- Place `<!-- claim-GEN-... -->` immediately before every substantive mathematical, algorithmic, implementation, or domain claim.
- Give every anchor exactly one matching entry in `claim_ledger.json`.
- Connect source-supported claims to `SRC-*` IDs.
- Label additions as `pedagogical_adaptation`, `domain_bridge`, or `implementation_bridge`; never present them as source-authored.
- Mark unsupported or contradicted claims honestly. Do not repair them by changing only the ledger.
- Use `claimed_exact`, never “verified exact,” unless independent evidence exists.
- State the boundary of every substantial analogy.
- Keep canonical terminology, equations, assumptions, and algorithm semantics explicit.

### 6. Create bidirectional provenance

Create `provenance.json`. Give each generated claim exactly one record linking its `GEN-*` ID and anchor to zero or more `SRC-*` IDs. Every retained, reordered, or summarised source claim must be reachable from provenance. Give deferred and omitted source claims a reason in `source_claims.json`.

### 7. Execute generated Python

Run:

```bash
python .github/skills/discipline-aware-teaching-adaptation/scripts/execute_code_blocks.py \
  --content <run-dir>/adapted_content.md --output <run-dir>/code_validation.json
```

Treat execution failure or timeout as a failed mechanical check. Execution success proves only that a block ran successfully, not that its mathematical meaning is correct.

### 8. Validate the C2 treatment

Run:

```bash
python .github/skills/discipline-aware-teaching-adaptation/scripts/validate_adapter_outputs.py \
  --workspace-root . --run-dir <run-dir>
```

This writes `validation_report.json`. Do not describe a run as a valid C2 treatment unless the command exits zero and `treatment_valid` is true. Fix artifacts and rerun when it fails; do not hand-edit the final boolean.

### 9. Review without self-certifying the research outcome

Use `references/evaluation-rubric.md` and create `adaptation_summary.md`. Report design decisions, assumptions, source issues, mechanical validation, and rubric observations. Do not use this internal summary as the formal RQ1 outcome measurement. Mathematical drift, unsupported claims, and algorithmic errors require an independent, blinded evaluator or separately specified automatic metric.

## Boundaries

Do not split into Atomic Learning pages, create page metadata or graphs, publish content, silently correct source defects, treat source consistency as universal mathematical correctness, or claim RQ1 is answered from a single internally reviewed run.
