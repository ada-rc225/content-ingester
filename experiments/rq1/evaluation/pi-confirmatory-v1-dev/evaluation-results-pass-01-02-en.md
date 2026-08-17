# PI-context RQ1 Automated Evaluation Results (Passes 01–02)

## Executive conclusion

For the Power Iteration confirmatory-v1 data, `c2-structured-grounding` has the strongest overall descriptive profile. Its major/critical error rate across the 13 generation-required Contract items is **0%**, formula-item accuracy is **100%**, algorithm-item accuracy is **81.25%**, and it leads five of the seven pedagogy dimensions. `c1-source-conditioned` also improves on C0 for primary error and has the lowest unsupported-claim rate, **2.64%**. `c0-ungrounded` performs worst on primary error, semantic drift, unsupported claims, formula accuracy, and algorithm accuracy.

This is not yet a statistically generalisable causal result. Most importantly, all three C2 runs have the same content hash: the nominal sample size is three, but C2 contains only one unique lesson. The evidence therefore supports the narrower conclusion that structured grounding performed best on this PI text, not that it will reliably dominate across independent generations.

## Condition-level fidelity outcomes

The two evaluator passes were first averaged within each lesson. The three nominal run-level lesson values were then averaged within each condition. Lower error rates and higher accuracy rates are better.

| Condition | Nominal runs / unique texts | Major/critical error | Semantic drift | Required-item omission | Unsupported claims | Condition failure | Formula accuracy | Algorithm accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 3 / 3 | 5.13% | 20.37% | 0.00% | 18.47% | 9.90% | 76.67% | 66.67% |
| C1 source-conditioned | 3 / 3 | 3.85% | 9.26% | 0.00% | **2.64%** | 2.60% | **100.00%** | 79.17% |
| C2 structured-grounding | 3 / 1 | **0.00%** | **8.33%** | 0.00% | 4.97% | **1.56%** | **100.00%** | **81.25%** |

Relative to C0, C2 reduces semantic drift by approximately **59.1%**, unsupported claims by **73.1%**, and condition failures by **84.2%**. Formula accuracy rises by 23.33 percentage points and algorithm accuracy by 14.58 points. C1 has a lower unsupported-claim rate than C2, so C2 is not best on every fidelity measure.

Required-item omission is zero in all three conditions. The meaningful differences are therefore not complete topic absence, but condition loss, implementation-contract changes, altered formulas or examples, and claims not supported by the Frozen Contract.

## Condition-level pedagogy outcomes

Pedagogy dimensions use a 1–5 scale, where higher is better. They are not collapsed into a composite score.

| Condition | Learner alignment | Disciplinary authenticity | Pedagogical coherence | Theory–implementation alignment | Readability | Analogy safety | Exercise validity |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 4.00 | 3.33 | 3.83 | 2.00 | 4.67 | 5.00 | 2.50 |
| C1 source-conditioned | 4.00 | 3.33 | 3.83 | 3.00 | **5.00** | 5.00 | 2.00 |
| C2 structured-grounding | **5.00** | **4.00** | **5.00** | **4.00** | 4.83 | 5.00 | **4.33** |

C2's advantage is not limited to fidelity. It targets the second-year mechanical-engineering audience more explicitly, organises the concept–algorithm–code progression more coherently, and comes closer to the required three-exercise design. C1 is substantially more faithful than C0, but all three C1 lessons receive an exercise-validity mean of 2.0 because their hand-calculation and code-diagnostic tasks do not fully match the task brief. Analogy safety is 5.0 in every condition, indicating that the mechanical-engineering analogies are consistently bounded.

## Run-level outcomes

Each row is the within-lesson mean of two evaluator passes. Anonymous sample IDs are retained for audit tracing.

| Condition | Run | Sample | Major/critical error | Drift | Unsupported claims | Formula accuracy | Algorithm accuracy | Exercise validity |
|---|---|---|---:|---:|---:|---:|---:|---:|
| C0 | run-01 | S004 | 3.85% | 19.44% | 17.70% | 80.00% | 68.75% | 2.0 |
| C0 | run-02 | S002 | 3.85% | 22.22% | 20.09% | 75.00% | 62.50% | 2.5 |
| C0 | run-03 | S005 | 7.69% | 19.44% | 17.62% | 75.00% | 68.75% | 3.0 |
| C1 | run-01 | S006 | 3.85% | 8.33% | 4.69% | 100.00% | 81.25% | 2.0 |
| C1 | run-02 | S003 | 7.69% | 11.11% | 1.67% | 100.00% | 75.00% | 2.0 |
| C1 | run-03 | S008 | 0.00% | 8.33% | 1.56% | 100.00% | 81.25% | 2.0 |
| C2 | run-01 | S007 | 0.00% | 11.11% | 7.13% | 100.00% | 75.00% | 4.5 |
| C2 | run-02 | S009 | 0.00% | 8.33% | 4.14% | 100.00% | 81.25% | 4.5 |
| C2 | run-03 | S001 | 0.00% | 5.56% | 3.64% | 100.00% | 87.50% | 4.0 |

The three C2 rows represent the same lesson text. Their numerical differences reflect independent judge-pass variability, not variation among three generated lessons.

## Main error patterns

### C0 ungrounded

- Convergence requirements are often weakened, especially non-zero initial projection onto the dominant eigenvector, strict dominant-magnitude assumptions, and breakdown conditions.
- Implementations frequently omit positive `max_iterations` or tolerance validation, alter exception behaviour or tuple order, and replace the required matrix and starting vector.
- Formula and algorithm accuracy are lowest. Exercises often omit the required normalised step, Rayleigh quotient, residual, or complete buggy/corrected code pair.

### C1 source-conditioned

- Mathematical formulas are preserved well: all three lessons have 100% formula accuracy, and the condition has the lowest unsupported-claim rate.
- Remaining weaknesses concentrate in convergence conditions and implementation contracts, especially parameter validation and maximum-iteration behaviour.
- Exercise design does not fully follow the exact task-brief structure, so stronger fidelity does not automatically translate into strong exercise validity.

### C2 structured-grounding

- No generation-required item receives a major or critical error. Formula and algorithm preservation are strongest, as is the overall pedagogical structure.
- Residual drift is concentrated in implementation details, including failure to enforce a positive tolerance and changing the Contract's breakdown `RuntimeError` to `ValueError`. The two passes vary slightly in how they classify these boundary cases.
- The passes also differ on whether the code-diagnostic exercise supplies a sufficiently complete corrected routine, although overall exercise quality remains substantially higher than C0 and C1.
- Identical outputs across the three runs indicate strong determinism in the current C2 workflow and prevent measurement of C2 generation variability in this experiment.

## Evaluator reliability

Nine anonymous lessons were evaluated in two fresh pointwise contexts each, giving 18 passes. All 18 judgements passed schema validation, hash binding, and deterministic scoring. Both passes used `gpt-5.6-sol`, but neither context could read the other pass.

| Repeatability measure | Overall result |
|---|---:|
| Exact severity agreement | 92.59% |
| Exact coverage agreement | 93.21% |
| Exact drift-set agreement | 87.65% |
| Pedagogy mean absolute difference | 0.254 / 5 |

Most disagreement occurs at the `minor`/`major` boundary for S002, S004, S005, and S006, including whether S005's hand-calculation residual should count as a major defect. No pass was manually selected: the aggregation averages both passes according to the fixed rule. These agreement rates measure repeatability of the same AI judge, not agreement with experts or ground-truth correctness.

## Method and input integrity

- Evaluation protocol: `RQ1-EVAL-v1`.
- Evaluator: OpenAI Codex CLI, model `gpt-5.6-sol`, evaluator ID `rq1-pi-judge-sol`.
- Frozen Contract: `power-iteration` v1.0.0, with 18 items, including 13 generation-required items; SHA-256 `3c749a34a0bc3d1bacd3022a8e403c4f6b090afcd99359245d51987db45e2ce7`.
- Blind-bundle manifest SHA-256: `7159b8a785d6e73ae43da27f27aa97d7f6bc0c4c854a133b5adc5e3938b1f2d1`.
- All 18 judgements and global repeatability statistics were completed before the condition mapping was opened. Evaluators could not access condition labels, generation artifacts, or other lessons.
- Before evaluation, `experiments/rq1/evaluation-specs/pi-confirmatory-v1/task_brief.txt` was found to contain a stale Gradient Descent brief. To avoid scoring PI lessons against the wrong task, it was restored from the consistent task requirements preserved in the three PI C2 run manifests, adaptation plans, and Frozen Contract before the blind bundle was built. This correction should remain in the audit trail; future experiments should freeze and hash the task brief before generation.

## Interpretation boundary

These are automated operational measurements produced by an AI evaluator against a Frozen Contract, not expert ground truth. Two passes from the same model measure repeatability, not cross-model or expert validity. Each condition has only three nominal runs, the study covers one Power Iteration topic, and C2 has only one unique lesson. No significance test, causal effect, or composite score is reported. A stronger follow-up should require distinct outputs in each condition and add a known-label mutation benchmark to estimate evaluator sensitivity and specificity.

## Artifact index

- `condition-summary-pass-01-02.json`: condition summaries, lesson rows, and pass rows for fidelity outcomes.
- `pedagogy-summary-pass-01-02.json`: pedagogy and condition-failure summaries.
- `reliability-report-pass-01-02.json`: overall and per-sample repeatability.
- `judgements/S001`–`judgements/S009`: 18 raw judgements, score reports, and per-sample reliability reports.

