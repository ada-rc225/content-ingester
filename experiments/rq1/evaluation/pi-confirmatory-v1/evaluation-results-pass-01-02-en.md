# PI-context RQ1 Automated Evaluation Results (Passes 01-02)

## Executive conclusion

Across the current Power Iteration confirmatory-v1 set of 9 anonymous lessons and 18 independent evaluator passes, `c2-structured-grounding` has the strongest descriptive fidelity profile: **0.00%** major/critical error rate, the lowest semantic drift rate (**5.56%**), the lowest condition failure rate (**0.00%**), **100.00%** formula accuracy, and the highest algorithm accuracy (**87.50%**). `c1-source-conditioned` also has no major/critical errors and has the lowest unsupported-claim rate (**1.91%**). `c0-ungrounded` has the highest primary error, drift, and unsupported-claim rates, and the lowest formula and algorithm accuracy.

This remains a small-sample, single-topic, AI-judge operational evaluation rather than a statistical or expert-ground-truth result. Unlike the earlier dev report, the current C2 rows have 3 unique prepared texts in the blind bundle, so the condition summary can describe three nominal runs, but it still should not be read as a general causal estimate.

## Condition-level fidelity outcomes

The two evaluator passes were first averaged within each lesson, then the three run-level lesson values were averaged within condition. Lower error rates and higher accuracy rates are better.

| Condition | Nominal runs / unique texts | Major/critical error | Semantic drift | Required-item omission | Unsupported claims | Condition failure | Formula accuracy | Algorithm accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 3 / 3 | 1.28% | 14.71% | **0.00%** | 14.71% | 6.45% | 87.04% | 72.92% |
| C1 source-conditioned | 3 / 3 | **0.00%** | 7.41% | **0.00%** | **1.91%** | 2.08% | **100.00%** | 83.33% |
| C2 structured-grounding | 3 / 3 | **0.00%** | **5.56%** | **0.00%** | 2.59% | **0.00%** | **100.00%** | **87.50%** |

Relative to C0, C2 reduces semantic drift by about **62.2%**, unsupported claims by **82.4%**, and condition failures by **100.0%**. Formula accuracy rises by **12.96** percentage points and algorithm accuracy by **14.58** points. Required-item omission is 0% in every condition, so the differentiating issues are implementation contracts, preserved conditions, drift, and claims outside the Frozen Contract.

## Condition-level pedagogy outcomes

Pedagogy dimensions use a 1-5 scale, where higher is better. They are not collapsed into a composite score.

| Condition | Learner alignment | Disciplinary authenticity | Pedagogical coherence | Theory-implementation alignment | Readability | Analogy safety | Exercise validity |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | **5.00** | 4.00 | **5.00** | 3.33 | **5.00** | **5.00** | **5.00** |
| C1 source-conditioned | **5.00** | **4.17** | **5.00** | 3.83 | **5.00** | **5.00** | **5.00** |
| C2 structured-grounding | **5.00** | 4.00 | 4.83 | **4.00** | **5.00** | **5.00** | 4.83 |

Pedagogy scores are high across all three conditions in this run. The main separation is in theory-implementation alignment and condition failure rate. C2 has the highest theory-implementation alignment, C1 has slightly higher disciplinary authenticity, and C0/C1 are essentially tied with or slightly above C2 for exercise validity. The stronger and cleaner signal is therefore in fidelity, not a blanket pedagogy advantage.

## Run-level outcomes

Each row is the within-lesson mean of two evaluator passes. Anonymous sample IDs are retained for audit tracing.

| Condition | Run | Sample | Major/critical error | Drift | Unsupported claims | Formula accuracy | Algorithm accuracy | Theory-implementation | Exercise validity |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| C0 | run-01 | S009 | 0.00% | 8.82% | 14.42% | 94.44% | 81.25% | 4.00 | 5.00 |
| C0 | run-02 | S004 | 0.00% | 23.53% | 12.02% | 83.33% | 62.50% | 3.00 | 5.00 |
| C0 | run-03 | S003 | 3.85% | 11.76% | 17.70% | 83.33% | 75.00% | 3.00 | 5.00 |
| C1 | run-01 | S001 | 0.00% | 8.33% | 2.04% | 100.00% | 81.25% | 4.00 | 5.00 |
| C1 | run-02 | S002 | 0.00% | 5.56% | 2.56% | 100.00% | 87.50% | 3.50 | 5.00 |
| C1 | run-03 | S008 | 0.00% | 8.33% | 1.11% | 100.00% | 81.25% | 4.00 | 5.00 |
| C2 | run-01 | S005 | 0.00% | 5.56% | 3.89% | 100.00% | 87.50% | 4.00 | 4.50 |
| C2 | run-02 | S006 | 0.00% | 5.56% | 2.14% | 100.00% | 87.50% | 4.00 | 5.00 |
| C2 | run-03 | S007 | 0.00% | 5.56% | 1.74% | 100.00% | 87.50% | 4.00 | 5.00 |

## Main error patterns

- C0 is weakest on semantic drift, unsupported claims, formula accuracy, and algorithm accuracy. S003 contains one generation-required major/critical error, while S004 has the highest drift rate.
- C1 preserves formulas most consistently: all three lessons have 100% formula accuracy and the lowest unsupported-claim rate. Remaining issues are concentrated in implementation contracts and some condition details.
- C2 maintains 0% major/critical errors, 0% condition failures, and the highest algorithm accuracy across its three lessons. Residual disagreements mostly concern boundary implementation details such as positive tolerance or `max_iterations` validation, exception class, and return order.

## Evaluator reliability

Nine anonymous lessons were evaluated in two fresh pointwise contexts each, giving 18 passes. Both passes used the same model but could not read each other's results.

| Repeatability measure | Overall result |
|---|---:|
| Exact severity agreement | 95.68% |
| Exact coverage agreement | 96.30% |
| Exact drift-set agreement | 94.44% |
| Pedagogy mean absolute difference | 0.063 / 5 |

These rates measure repeatability of the same AI judge, not agreement with experts or true correctness. No single pass was manually selected; aggregation uses the fixed rule of averaging the two passes within each lesson.

## Method and input integrity

- Evaluation protocol: `RQ1-EVAL-v1`.
- Evaluator: OpenAI Codex CLI, model `gpt-5.6-sol`, evaluator ID `rq1-pi-confirmatory-judge-sol`.
- Frozen Contract: `power-iteration` v1.0.0; SHA-256 `3c749a34a0bc3d1bacd3022a8e403c4f6b090afcd99359245d51987db45e2ce7`.
- Blind-bundle manifest SHA-256: `3ed24c09abe9df71ffbef3fd80793f29d6dcc68a288c84c68d8d0bb3a4bd112b`.
- All 18 fresh pointwise judge passes were completed before unblinding; evaluators could not read condition mappings, source runs, other samples, or the other pass.
- 18/18 judgements passed schema validation, hash binding, and deterministic scoring checks.

## Interpretation boundary

These are automated operational measurements against a Frozen Contract, not expert ground truth. Each condition has only three runs and the study covers one Power Iteration topic. The two passes come from the same model, so they test repeatability but not cross-model or expert validity. No p-values, causal effect, or composite score is reported.

## Artifact index

- `condition-summary-pass-01-02.json`: condition summaries, lesson rows, and pass rows for fidelity outcomes.
- `pedagogy-summary-pass-01-02.json`: pedagogy and condition-failure summaries.
- `reliability-report-pass-01-02.json`: overall and per-sample repeatability.
- `judgements/S001`-`judgements/S009`: 18 raw judgements, score reports, and per-sample reliability reports.
