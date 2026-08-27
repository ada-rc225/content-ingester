# RQ1 conclusion and gate to RQ2

## Decision

RQ1 has enough **descriptive, operational evidence** to close the current
generation-and-automated-evaluation phase and start RQ2. The evidence supports
H1's direction for source grounding versus an ungrounded baseline. It does not
support a claim of statistical significance, general causal effectiveness, or
expert-validated mathematical correctness.

Recommended thesis wording:

> Across two confirmatory topics, source-grounded generation showed a
> consistently stronger contract-bound fidelity profile than ungrounded
> generation, with fewer major mathematical errors and semantic drift, fewer
> unsupported claims, and higher formula and algorithm accuracy. Given the
> small number of generated lessons and reliance on automated contract-bound
> evaluation, these findings are descriptive evidence in support of H1 rather
> than a general causal estimate.

## Evidence mapped to H1

| H1 outcome | Gradient descent | Power iteration | Assessment |
|---|---:|---:|---|
| Major/critical error, C0 -> C1/C2 | 11.54% -> 0% / 0% | 1.28% -> 0% / 0% | Direction supported in both topics |
| Semantic drift, C0 -> C1/C2 | 22.78% -> 0% / 0% | 14.71% -> 7.41% / 5.56% | Direction supported in both topics |
| Unsupported claims, C0 -> C1/C2 | 33.62% -> 0% / 0% | 14.71% -> 1.91% / 2.59% | Direction supported in both topics |
| Formula accuracy, C0 -> C1/C2 | 76.79% -> 100% / 100% | 87.04% -> 100% / 100% | Direction supported in both topics |
| Algorithm accuracy, C0 -> C1/C2 | 77.78% -> 100% / 100% | 72.92% -> 83.33% / 87.50% | Direction supported in both topics |
| Required-source coverage | 100% in all conditions | 100% in all conditions | Ceiling effect; H1 coverage advantage not demonstrated |

The strongest defensible conclusion is **C0 versus grounded generation**.
There is no consistent evidence that structured grounding (C2) is superior to
simple source conditioning (C1): they tie on the gradient-descent task, while
C2 has somewhat lower drift and algorithm error but slightly more unsupported
content than C1 on power iteration.

## Why the conclusion must remain bounded

- There are three generated lessons per condition per topic. These are
  repeated generations, not independent student or classroom observations.
- Both evaluations are automated and measure conformance to a Frozen Contract,
  not mathematical truth outside that contract.
- The power-iteration passes measure same-model repeatability rather than
  cross-model or expert agreement.
- The gradient-descent rerun used reproducible operational judgements after
  external evaluator processes stalled. Its two passes therefore have weaker
  independence than the power-iteration passes.
- Required-item omission is zero in every condition, so the current experiment
  cannot establish the hypothesised source-coverage advantage.
- No inferential test, confidence interval based on an adequate independent
  sample, expert adjudication, or learner outcome is available.

## RQ1 closure checklist

- [x] Two mathematical topics evaluated with the same conceptual comparison.
- [x] Three condition runs and two judgement passes represented per topic.
- [x] Fidelity and pedagogy reported separately.
- [x] Reliability and limitations recorded.
- [x] H1 outcomes reported individually rather than as a composite.
- [ ] Optional strengthening: expert audit of a stratified subset of contract
  items and all major/critical errors.
- [ ] Optional strengthening: a new topic or larger run count if a statistical
  or generalisable claim is required.

The two optional items are not blockers for starting RQ2. They are blockers
only for upgrading the RQ1 conclusion beyond descriptive operational evidence.

