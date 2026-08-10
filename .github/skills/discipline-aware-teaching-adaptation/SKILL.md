---
name: discipline-aware-teaching-adaptation
description: Replan and rewrite supplied mathematical or computational teaching material for a specified discipline, education level, prior knowledge, and learning goal. Use for token-efficient, source-grounded long-form adaptation from Markdown, notebooks, PDF, PPTX, code, or text; retain compact mathematical invariants, section-level provenance, source fingerprints, and executable-code evidence without Atomic Learning page splitting or publishing.
---

# Discipline-aware teaching adaptation

Create one readable audience-specific lesson using compact structured grounding. Use C2 skill version `2.1`.

## Read first

Read `references/grounding-and-adaptation-rules.md` and `references/output-contract.md`. Read `references/evaluation-rubric.md` only before final review. Do not load schema text into the generation prompt; write to the documented shape and let the validator check it.

## Workflow

1. Resolve the source, learner profile, topic scope, and run directory. Write `run_manifest.json` with truthful metadata and `learner_profile.json` with explicit assumptions.

2. Run `scripts/build_source_manifest.py` to create `source_manifest.json`. Do not paste its hash or full JSON into the lesson-generation prompt. If an exact source hash and topic scope already have reviewed core invariants, reuse them instead of extracting them again.

3. Read the complete relevant source once. Create `core_invariants.json` with only the definitions, assumptions, equations, theorem conditions/results, convergence results, algorithm update rules, and code semantics whose alteration would constitute mathematical drift or algorithmic error. Use at most 12 concise invariants; target 6–10. Do not create invariants for transitions, analogies, examples, exercises, or general background.

4. Create compact `adaptation_plan.json`. Plan 3–12 readable chapters. Give each chapter a `SEC-NN` ID, title, purpose, and relevant invariant IDs. Include implementation and assessment as proper chapters when they are part of the requested lesson.

5. Write `adapted_content.md` for students. Prioritise narrative quality:

   - start with one H1 title;
   - place `<!-- section: SEC-NN -->` immediately before each planned H2 heading;
   - reproduce every planned H2 title in the planned order;
   - use headings, transitions, examples, equations, code, and exercises naturally;
   - keep evidence IDs out of visible prose;
   - state analogy boundaries and mathematical conditions;
   - never let provenance structure replace instructional structure.

6. Create compact `provenance.json` after the lesson. Use one record per planned section. Reference invariant IDs and short adaptation-type labels; do not repeat lesson sentences, equations, or long justifications.

7. Run `scripts/execute_code_blocks.py`, then `scripts/validate_adapter_outputs.py`. Fix only the artifact named by an error and rerun. Never rewrite all artifacts because of one failed cross-reference, and never hand-edit `validation_report.json`.

8. Write `adaptation_summary.md` after validation, using at most 300 words. Summarise decisions and limitations without reproducing the lesson, invariants, plan, or provenance.

## Token discipline

- Write artifacts directly with file-editing tools.
- Never emit or ask the user to run a monolithic heredoc, embedded Python program, or shell command containing generated lesson/JSON content.
- Use terminal commands only to call existing deterministic scripts or validators.
- Do not duplicate `adapted_content.md` inside JSON fields, summaries, commands, or chat responses.
- On validation failure, inspect the short report and patch only affected fields.
- Keep the source manifest outside the narrative prompt; it is experimental metadata, not teaching context.

## Research boundary

Treat `treatment_valid=true` as protocol integrity only. Do not equate source consistency, code execution, or internal review with independently established mathematical correctness, and do not claim one run answers RQ1.
