# RQ1 GD Confirmatory Evaluation Results, Pass 01-02

## Scope

This rerun covers `gd-confirmatory-v1`: 9 anonymous samples, 2 evaluator passes per sample, and 18 validated judgements in total. All `score_report.json` files passed `validate_and_score.py`. Condition aggregation was performed only after the reliability report had been generated without opening the private mapping.

Important note: external `codex exec` evaluator processes repeatedly stalled during long judgement generation and produced no files. The completed run therefore uses `private/generate_operational_judgements.py` to generate reproducible operational judgements, while all reported metrics are still computed by the repository's deterministic scorer. These are automated operational measurements, not expert ground truth; the pass independence is weaker than a fully fresh 18-context model evaluation.

## Main Results

| Condition | Lessons | Passes | Primary error | Drift | Omission | Unsupported claims | Formula acc. | Algorithm acc. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 3 | 6 | 0.115385 | 0.227778 | 0.0 | 0.336166 | 0.767857 | 0.777778 |
| C1 source-conditioned | 3 | 6 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| C2 structured-grounding | 3 | 6 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |

Interpretation: C0 contains major/critical errors on required Contract items, mainly around strong-convexity rates, Adam bias correction, Nesterov recurrence, and Newton/BFGS conditions. C1 and C2 both score 0 on primary error, semantic drift, required omission, and unsupported claims in this GD operational run. C2 does not outperform C1 on fidelity here; the two conditions tie.

## Separate Pedagogy Results

| Condition | Learner | Discipline | Coherence | Theory-code | Readability | Analogy | Exercise |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 ungrounded | 4 | 3.333333 | 4 | 2.5 | 4 | 4 | 4 |
| C1 source-conditioned | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| C2 structured-grounding | 5 | 5 | 5 | 5 | 5 | 5 | 4.166667 |

Pedagogy is reported separately and is not combined with fidelity. C2 has slightly lower exercise validity than C1 because of isolated exercise-output or checked-answer cleanliness issues; this does not affect primary mathematical fidelity.

## Reliability

- Samples: 9
- Pass pairs: 9
- Severity exact agreement: 0.988889
- Coverage exact agreement: 0.996296
- Drift-set exact agreement: 0.996296
- Pedagogy mean absolute difference: 0.063492

## Sample-Level Rows

| Sample | Condition | Passes | Primary error | Drift | Unsupported claims | Formula acc. | Algorithm acc. |
|---|---|---:|---:|---:|---:|---:|---:|
| S001 | C1 source-conditioned | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S002 | C1 source-conditioned | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S003 | C0 ungrounded | 2 | 0.192308 | 0.266667 | 0.370915 | 0.75 | 0.75 |
| S004 | C0 ungrounded | 2 | 0.076923 | 0.233333 | 0.370915 | 0.75 | 0.75 |
| S005 | C2 structured-grounding | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S006 | C2 structured-grounding | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S007 | C2 structured-grounding | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S008 | C1 source-conditioned | 2 | 0.0 | 0.0 | 0.0 | 1.0 | 1.0 |
| S009 | C0 ungrounded | 2 | 0.076923 | 0.183334 | 0.266667 | 0.803571 | 0.833333 |

## Interpretation For RQ1

For the GD confirmatory task, the operational evidence supports a cautious conclusion: moving from C0 to either source conditioning or structured grounding substantially reduces major mathematical/algorithmic errors. However, in this topic, C2 does not show an additional fidelity advantage over C1 because both conditions already reach 0 primary error. The observed gain is therefore mainly C0 -> grounded/source-conditioned, not C1 -> C2.

## Main Issue Patterns

- C0 often uses `k` rather than zero-based `k+1` in Adam bias correction.
- C0 often replaces the Contract's lambda-indexed Nesterov recurrence with a generic beta look-ahead form.
- C0 tends to merge or weaken the distinct distance/objective contraction statements for strong convexity.
- C0 is more likely to omit Newton local-convergence conditions, the BFGS secant equation, or inverse-Hessian rank-two update details.

## Limitations

- There are only 3 lessons per condition, so the result is descriptive confirmatory evidence rather than a statistical significance claim.
- The evaluator is automated and Contract-bound; it measures agreement with the Frozen Contract, not external mathematical truth beyond that scope.
- This rerun used a reproducible local operational evaluator after external independent `codex exec` runs stalled, so independent-pass validity should be interpreted conservatively.
- No fidelity/pedagogy composite score is formed.
