# RQ2 Power Iteration Three-Run Evaluation Report

Status: expanded pilot, pre-adjudication. This report combines run-01, run-02, and run-03 while preserving the original single-run report and raw judgements.

Evaluation date: 26 August 2026  
Protocol: RQ2-EVAL-v1  
Topic: Power Iteration

## Executive conclusion

The original RQ2 evidence was underpowered at the lesson-generation level because every profile-condition cell had only one run. Runs 02 and 03 now bring the composition layer to three runs: 21 generated lessons, 27 profile-relative blind samples, 54 fresh-context judgements, and 54 deterministically validated score reports.

The expanded evidence remains pilot evidence rather than a confirmatory result:

- H2a receives partial support against P0. Across the three runs, the P2-P0 median paired difference is +1.0 for disciplinary framing and +0.5 for sequence quality; it is zero for prerequisite match and context-boundary awareness.
- H2a is not supported against the strong P1 control. All four P2-P1 median paired differences are zero. Framing records 1 win, 6 ties, and 2 losses; sequence records 1 win and 8 ties; the other two dimensions are all ties. P1 and P2 remain strongly ceiling-saturated.
- The existing H2b result remains valid: P2 pathways differ materially across profiles in validated, profile-linked ways. Runs 02 and 03 reused the reviewed and materialized final pathways, however, so they replicate lesson composition rather than pathway planning.
- H2c is not satisfied. Requiring both evaluator passes to clear the conjunctive gate gives P0 9/9, P1 8/9, and P2 only 4/9.

The stable descriptive finding is therefore that profile-aware P1/P2 lessons improve some outcomes relative to generic P0, while dependency-aware P2 does not improve the rubric scores over P1 and currently exposes more formula, boundary-condition, or authority-extension failures during composition.

## Sample and generation audit

Each run contains one shared P0 lesson, three P1 lessons, and three P2 lessons.

| Condition | Independently generated lessons | Profile-relative blind samples | Evaluator passes per sample |
|---|---:|---:|---:|
| P0 | 3 | 9 | 2 |
| P1 | 9 | 9 | 2 |
| P2 | 9 | 9 | 2 |
| Total | 21 | 27 | 54 judgements |

P0 is generated once per run and evaluated against all three profiles; its nine blind samples are not nine independent lessons. All 21 `lesson.md` SHA-256 hashes are distinct. Every Composer validation report is `valid=true`, with zero errors and warnings, compliant 1,500–2,000-word English prose, and passing required Python execution validation.

Generation settings were not fully frozen. Run-01 records GitHub Copilot / GPT-5.6 Luna / VS Code Copilot Chat, whereas runs 02–03 record OpenAI / gpt-5.6-sol / codex-exec-ephemeral. Evaluator metadata also changes from `codex-default` in run-01 to `gpt-5.6-sol` in runs 02–03. The added runs therefore extend the pilot but do not meet the confirmatory requirement for the same model family and generation settings.

## Per-run outcomes

The four ordered dimensions below are disciplinary framing, prerequisite match, context-boundary awareness, and sequence quality. Judge passes are first collapsed by sample median.

| Run | H2c P0 | H2c P1 | H2c P2 | P2-P1 median paired differences | P2-P0 median paired differences |
|---|---:|---:|---:|---|---|
| run-01 | 3/3 | 2/3 | 2/3 | (0, 0, 0, 0) | (+1.0, 0, 0, +0.5) |
| run-02 | 3/3 | 3/3 | 1/3 | (0, 0, 0, 0) | (+1.0, 0, 0, +1.0) |
| run-03 | 3/3 | 3/3 | 1/3 | (0, 0, 0, 0) | (+1.0, +0.5, 0, 0) |

P2 never exceeds P1 on the median contrast in any primary dimension. The P2-P0 framing direction is positive in every run; sequence gains are clearest in runs 01–02.

## Combined H2a outcomes

| Primary dimension | P0 median | P1 median | P2 median | P2-P1 median difference | P2-P0 median difference |
|---|---:|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 4.0 | 5.0 | 5.0 | 0.0 | +1.0 |
| Prerequisite match | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Context-boundary awareness | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Sequence quality | 4.5 | 5.0 | 5.0 | 0.0 | +0.5 |

The descriptive P2-P1 mean paired differences are -0.056 for framing, +0.056 for sequence, and zero for the other dimensions. With one topic and ceiling-saturated scores, these are descriptive rather than inferential or portable effects. Example authenticity remains exploratory and cannot accept H2a.

## H2b interpretation boundary

The existing confirmed report retains material P2 differences across all profile pairs:

| P2 profile pair | Selection distance | Normalized order distance | Grouping distance | Bridge distance |
|---|---:|---:|---:|---:|
| Applied mathematics vs computer science | 0.0556 | 0.6667 | 0.3000 | 1.0000 |
| Applied mathematics vs mechanical engineering | 0.0556 | 0.6667 | 1.0000 | 1.0000 |
| Computer science vs mechanical engineering | 0.0000 | 0.1176 | 1.0000 | 0.0000 |

These are validated, profile-rationalized structural changes rather than wording changes. Because all lesson runs use the same final pathway files, H2b reflects one confirmed pathway set composed three times, not three independent Planner outputs.

## H2c failures

The combined two-pass gate results are P0 9/9, P1 8/9, and P2 4/9.

Gate failures requiring adjudication are:

1. P1 computer science run-01 (S-C08S): one evaluator finds that positive non-integer `max_iterations` is not explicitly rejected, leaving RC-017 only partially covered.
2. P2 computer science run-01 (S-H65S): both evaluators identify complexity/reproducibility claims outside Frozen Contract and released-bridge authority.
3. P2 applied mathematics runs 02 and 03 (S-M52V and S-Z82P): both evaluators identify a missing backslash that renders literal `qquad` in FM-005; formula accuracy is 15/16.
4. P2 mechanical engineering run-02 (S-P63H): both evaluators find that positive non-integer `max_iterations` does not receive the Contract-required clear `ValueError`.
5. P2 mechanical engineering run-03 (S-D94H): one evaluator finds that an unconditional eigendirection-preservation claim omits the lambda-zero exception; the other does not classify it as an error, so the disagreement must be adjudicated.

Some safety-passing samples also receive discipline-authenticity adjudication recommendations for bounded `not_verifiable` application analogies. These are separate from H2c and must not be treated as domain-expert ground truth.

## Evaluator reliability

| Dimension | Exact agreement | Mean absolute difference | Differences of at least 2 | Ordinal Krippendorff alpha |
|---|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 0.815 | 0.185 | 0 | 0.678 |
| Prerequisite match | 0.778 | 0.222 | 0 | -0.104 |
| Context-boundary awareness | 1.000 | 0.000 | 0 | 1.000 |
| Sequence quality | 0.815 | 0.185 | 0 | 0.681 |

No primary rating differs by two or more points. Prerequisite-match exact agreement improves, but ordinal alpha remains negative because ratings are concentrated almost entirely at 4–5. Perfect context-boundary agreement is likewise ceiling-saturated. The two passes are repeated automated-evaluator measurements, not two independent human experts.

## RQ2 decision

| Component | Three-run decision |
|---|---|
| H2a: P2 has higher pedagogical ratings | Partially supported against P0; not supported against P1 |
| H2b: P2 creates materially different profile-linked pathways | Supported by the existing structural evidence; not independently replanned in runs 02–03 |
| H2c: every selected pathway preserves correctness, provenance, and dependency coherence | Not satisfied; only 4/9 P2 samples pass both evaluator gates |
| Overall RQ2 | Feasibility and some descriptive P2-vs-P0 benefit are supported; P2-vs-P1 superiority and uniform safety are not |

## Required next steps

1. Human-adjudicate every gate failure and bounded disciplinary claim while preserving both raw judgements.
2. Freeze a single generation and evaluator model family, prompt, budget, and output setting before confirmatory runs.
3. If the claim requires independent pathway replication, rerun the P2 Planner per cell rather than only recomposing a reused pathway.
4. Recalibrate prerequisite-match and context-boundary anchors to reduce 4–5 ceiling saturation.
5. Complete Gradient Descent under the same design before making cross-topic portability claims.
6. Do not claim learner comprehension, learning gain, or authentic professional-practice validity without a student study or independent discipline experts.

## Principal evidence

- `aggregate-results-run-01-03.json`: combined condition summaries and paired contrasts;
- `aggregate-results.json`, `aggregate-results-run-02.json`, and `aggregate-results-run-03.json`: per-run aggregates;
- `reliability-report-run-01-03.json`: reliability over all 54 raw judgements;
- `reliability-report.json`, `reliability-report-run-02.json`, and `reliability-report-run-03.json`: per-run reliability;
- `pathway-difference-report-confirmed.json`: existing confirmed cross-profile P2 structure;
- `blind-samples/`, `judge-pass-01/`, `judge-pass-02/`, and `private-mappings/`: auditable pointwise evidence.
