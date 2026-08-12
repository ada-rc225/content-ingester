---
name: discipline-aware-teaching-adaptation
description: Replan and rewrite mathematical or computational teaching material for a specified discipline, education level, prior knowledge, and learning goal using an independently reviewed, released Frozen Reference Contract as the sole mathematical grounding authority. Use for C2 structured-grounding runs that must preserve approved mathematical and algorithmic content, enforce a configured prose length, generate readable discipline-aware lessons followed by a final worked-exercise chapter, trace exercises to Contract items, verify unified objective-gradient-update calculations, visible answers, and Python stdout, and produce a validated long-form lesson without Atomic Learning page splitting.
---

# Discipline-aware teaching adaptation

Create one readable audience-specific lesson using C2 Frozen Contract skill version `3.5`.

## Read first

Read `references/grounding-and-adaptation-rules.md` and `references/output-contract.md`. Read `references/evaluation-rubric.md` only before final review. Do not load schema files into the writing context.

## Preconditions

Require the user to identify one `frozen_reference_contract.json`, learner target, topic scope, and run directory. Do not accept a candidate `reference_contract.json`, `human_review.json`, raw source alone, or an older invariant file as grounding truth.

Before planning or writing, run:

`python3 .github/skills/discipline-aware-teaching-adaptation/scripts/prepare_frozen_grounding.py --workspace-root . --contract <frozen-contract> --output <run-dir>/grounding_receipt.json`

This also creates `grounding_view.json`. If release status, approval, Contract SHA-256, Validator report, inventory, source hashes, or current Contract validation fails, stop without generating teaching content. Never invoke the Contract Builder, Human Reviewer, materializer, or Release Gate from this Skill.

## Workflow

1. Read `grounding_receipt.json`, `grounding_view.json`, and the learner request. Use `grounding_view.json` as the only mathematical and algorithmic generation authority. Do not re-extract invariants or use model memory to extend the approved mathematical core.

2. Write `run_manifest.json` with truthful metadata and the SHA-256 of `grounding_receipt.json`. Record `word_count_protocol` from the request. For an English RQ1 run requesting 2500–3000 prose words, use `enabled=true`, `minimum=2500`, `maximum=3000`, and `counting_method=english_prose_v1`. Use `enabled=false` with both limits set to zero only when no length constraint exists. Write `learner_profile.json` with explicit learner assumptions.

3. Create `adaptation_plan.json` with 3–12 readable chapters. Complete the instructional sequence first and reserve the final planned chapter for exercises and worked solutions. Record that final chapter in `exercise_section_id`. Include every required Contract item in the instructional chapters. Decide every conditional item exactly once and give a short scope-based rationale. Include only conditional items needed by the requested lesson. Never include excluded items.

4. Record the requested exercise protocol in `run_manifest.json`. For an RQ1 exercise run, default to exactly three worked exercises—one `concept_check`, one `hand_calculation`, and one `code_diagnostic`—unless the user specifies another common protocol for C0/C1/C2. Place every exercise in the final `exercise_section_id`; do not interleave exercises with instructional chapters. Assign `EX-001`, `EX-002`, and so on in reading order. Plan each exercise with its difficulty, objective, selected RC item IDs, generated discipline context, and verification method. Exercises are generated pedagogical material, not Contract evidence. Use `contract_binding` for conceptual, derivational, or transfer exercises. Every hand calculation must include a consistency check. When the task states an objective, gradient, point, step size, and gradient update, use exactly one `objective_gradient_update` check: record the objective expression, variables, point, positive step size, expected gradient, and expected update; set the verification-level `expected_value` to the same update and `python_expression` to null. The validator must derive the gradient and update from this single chain. Use `objective_gradient` only when no update is requested, and `expression_values` for other derived quantities. Set unused check fields to null and use Python expression syntax (`**`, `sin`, `cos`, `exp`, `log`, `sqrt`).

5. Give each chapter a `SEC-NN` ID, title, purpose, and relevant `RC-NNN` item IDs. Reorder and scaffold approved content for the learner, but preserve each selected item's canonical statement, formulae, conditions, and prohibited-drift boundaries. Give the final exercise chapter a student-facing title such as `Exercises and worked solutions`; its chapter-level Contract item list may be empty because each exercise records its own binding.

6. Write `adapted_content.md` for students:

   - start with one H1 title;
   - place `<!-- section: SEC-NN -->` immediately before each planned H2 heading;
   - reproduce planned H2 titles in order;
   - keep RC IDs and provenance metadata out of visible prose;
   - distinguish canonical mathematics from pedagogical analogy;
   - state each substantial analogy boundary once, at its first use, and do not present generated disciplinary framing as source evidence;
   - organise a chapter with descriptive H3 subheadings when it covers several distinct concepts;
   - place assumptions next to the theorem or algorithm they constrain, but do not repeat the same caveat in later paragraphs unless the scope changes;
   - prefer direct sentences, short transitions, and one main teaching purpose per paragraph;
   - avoid compliance language such as “Contract”, “approved”, “must not”, or “source permits” in visible student prose;
   - meet the requested length through explanation, examples, and synthesis rather than repeated disclaimers;
   - add no new theorem, convergence guarantee, update rule, numerical constant, or factual application claim unless supported by a selected Contract item;
   - preserve implementation semantics and make requested Python executable;
   - place `<!-- exercise: EX-NNN -->` immediately before each exercise and `<!-- solution: EX-NNN -->` immediately before its worked solution;
   - for `deterministic_calculation` or `combined`, finish the visible derivation with `<!-- derived-answer: EX-NNN -->` followed by `**Result from the derivation:** \`<JSON number or numeric array>\``, then include `<!-- answer: EX-NNN -->` followed by `**Checked answer:** \`<the same JSON value>\`` inside the solution;
   - ensure every objective, derivative/gradient, supplied intermediate value, update, and checked answer in an exercise agrees with its configured consistency and numeric checks;
   - finish all instructional explanations and synthesis before the final exercise H2;
   - place every exercise and its worked solution under that final H2, with no later instructional section;
   - place Python used by `code_execution` or `combined` after that exercise's marker and before the next section, so execution evidence binds to the exercise;
   - after each Python block belonging to a code-verified exercise, add `<!-- expected-stdout: EX-NNN/K -->` followed by `**Expected output:** \`<JSON string>\``, where `K` is the one-based code-block order within that exercise and the decoded string exactly matches stdout, including `\\n`.

7. Create `provenance.json` after writing, with one compact record per section and one record per exercise. Its Contract identity, section IDs, exercise IDs, verification methods, and RC mappings must exactly match the plan. Mark exercise origin as `generated_pedagogical_material`. Do not repeat lesson prose or equations.

8. Run `scripts/execute_code_blocks.py`, then `scripts/validate_exercises.py`, then `scripts/validate_adapter_outputs.py`. The exercise validator checks markers, reading-order IDs, worked solutions, RC bindings, unified objective-gradient-update calculations, equality of visible derivation and checked answers, and equality of visible expected output and executed stdout. The final validator also enforces `word_count_protocol`; `english_prose_v1` excludes fenced code, HTML comments, displayed/inline math, and inline code before counting English word tokens. Patch only the named generated artifact on failure and rerun. Never hand-edit `grounding_receipt.json`, `grounding_view.json`, `code_validation.json`, `exercise_validation.json`, or `validation_report.json`.

9. Read `references/evaluation-rubric.md`, perform an internal quality check, and write `adaptation_summary.md` in at most 300 words. Summarise the configured automatic checks without requesting a post-generation human review. Do not claim that Contract binding, numeric checks, or code execution prove the complete lesson correct or answer RQ1.

## Token discipline

- Use the compact deterministic `grounding_view.json` for generation; do not paste the complete Frozen Contract, evidence excerpts, source manifest, inventory, or hashes into the lesson prompt.
- Write artifacts directly with file-editing tools.
- Never emit or request a monolithic heredoc, embedded artifact-generating program, or command containing lesson/JSON content.
- Do not duplicate the lesson in JSON, summaries, commands, or chat.
- Keep provenance section-level and repair only failed fields.

## Research boundary

Treat `treatment_valid=true` as C2 protocol integrity: the run used one released Frozen Contract, declared complete required-item coverage, accounted for conditional items, preserved section/exercise provenance, and passed configured binding, numeric, and code checks. This generation workflow does not include post-generation human semantic approval. Assess mathematical drift and errors later through the same separate blinded RQ1 evaluation applied to C0, C1, and C2.
