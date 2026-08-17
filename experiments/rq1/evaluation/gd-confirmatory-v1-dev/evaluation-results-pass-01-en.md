# RQ1 Gradient Descent confirmatory-v1 Evaluation Results

## Evaluation Scope

- Protocol: `RQ1-EVAL-v1`
- Evaluator: `rq1-judge-sol` (OpenAI Codex CLI, `gpt-5.6-sol`)
- Anonymous samples: 9, comprising 3 independent lesson outputs per experimental condition
- Evaluation passes: 1 blind judge pass per sample
- Status: all 9 `score_report.json` files passed schema, hash, evidence-excerpt, and deterministic-scoring validation

This report presents fidelity and pedagogy separately and does not calculate a single composite score. Lower error, drift, omission, and unsupported-claim rates are better; higher formula and algorithm accuracy rates are better.

## Condition-Level Fidelity Results

| Condition | n | Major/Critical Error Rate | Semantic Drift Rate | Required-Item Omission Rate | Unsupported/Contradicted Claim Rate | Formula Accuracy | Algorithm Accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 3 | 10.26% | 34.29% | 2.56% | 15.28% | 46.25% | 44.44% |
| C1 source-conditioned | 3 | 0.00% | 25.56% | 0.00% | **1.14%** | 69.05% | 61.11% |
| C2 structured-grounding | 3 | **0.00%** | **1.11%** | **0.00%** | 3.04% | **98.81%** | **97.22%** |

The denominator of the primary major/critical error rate is the 13 generation-required Contract items in each lesson. Across the three C0 lessons, there were 4 major or critical errors among 39 required-item judgements. C1 and C2 both recorded 0 errors among 39 judgements.

Compared with C0, C2 reduced semantic drift by approximately 96.8%, increased formula accuracy by 52.56 percentage points, and increased algorithm accuracy by 52.78 percentage points. Compared with C1, C2 reduced semantic drift by approximately 95.7%, increased formula accuracy by 29.76 percentage points, and increased algorithm accuracy by 36.11 percentage points.

C1 achieved the lowest unsupported/contradicted claim rate. C2's slightly higher rate arose mainly from internally inconsistent expected outputs in newly generated coding exercises in two lessons, rather than errors in the core knowledge represented by the Frozen Contract.

## Condition-Level Pedagogy Results

The following values are three-sample means on a 1–5 scale.

| Condition | Learner Alignment | Disciplinary Authenticity | Pedagogical Coherence | Theory–Implementation Alignment | Readability | Analogy Safety | Exercise Validity |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 4.33 | 3.67 | 4.67 | 3.33 | 4.67 | 4.00 | 4.67 |
| C1 source-conditioned | **5.00** | **4.00** | **5.00** | **5.00** | **5.00** | 4.33 | **5.00** |
| C2 structured-grounding | **5.00** | **4.00** | 4.67 | 4.33 | **5.00** | **5.00** | 3.67 |

C1 performed best in instructional organisation and theory–implementation alignment. C2 achieved the highest analogy-safety score, but contradictory expected outputs in the coding-diagnostic exercises from runs 02 and 03 reduced its mean exercise-validity score. This finding indicates that structured grounding can substantially constrain existing knowledge and algorithm semantics, but it does not automatically guarantee the correctness of newly generated examples, code outputs, or exercise answers. Such material still requires executable tests or a dedicated exercise validator.

## Sample-Level Results

| Condition / Run | Anonymous Sample | Major/Critical Error Rate | Drift Rate | Unsupported Claim Rate | Formula Accuracy | Algorithm Accuracy |
|---|---|---:|---:|---:|---:|---:|
| C0 / run-01 | S008 | 7.69% | 44.83% | 15.38% | 44.44% | 25.00% |
| C0 / run-02 | S009 | 7.69% | 41.38% | 8.89% | 40.74% | 41.67% |
| C0 / run-03 | S001 | 15.38% | 16.67% | 21.57% | 53.57% | 66.67% |
| C1 / run-01 | S004 | 0.00% | 13.33% | 0.00% | 82.14% | 75.00% |
| C1 / run-02 | S005 | 0.00% | 33.33% | 1.49% | 64.29% | 50.00% |
| C1 / run-03 | S006 | 0.00% | 30.00% | 1.92% | 60.71% | 58.33% |
| C2 / run-01 | S007 | 0.00% | 0.00% | 0.00% | 100.00% | 100.00% |
| C2 / run-02 | S002 | 0.00% | 0.00% | 3.23% | 100.00% | 100.00% |
| C2 / run-03 | S003 | 0.00% | 3.33% | 5.88% | 96.43% | 91.67% |

## Conclusion

The results from this evaluation pass support the mechanism proposed in RQ1. Compared with generation without grounding, providing source context eliminated major and critical errors in the generation-required items. Adding a structured Frozen Contract further reduced condition loss and semantic drift substantially, while raising formula and algorithm accuracy to nearly 100%.

However, this remains an operational pilot rather than a final confirmatory result that can establish statistical significance or evaluator reliability. Each condition currently contains only three lessons, and each lesson received only one AI judge pass. Neither within-evaluator repeatability nor agreement across evaluators has therefore been estimated. A formal thesis or paper should include at least one independent repeat evaluation and report agreement or reliability. If no repeat evaluation is conducted, these results should be explicitly described as single-evaluator, single-pass automated measurements.
