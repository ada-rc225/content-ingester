# RQ1 automated evaluation protocol v1

## Contents

1. Measurement model
2. Contract-item judgements
3. Atomic-claim judgements
4. Pedagogy judgements
5. Evidence and abstention
6. Reliability and validity checks

## 1. Measurement model

The primary outcome is the proportion of evaluable **required** Contract items containing a `major` or `critical` mathematical or algorithmic error. The required-item denominator is common across samples and does not penalise a lesson merely for selecting more optional material. Report the error rate across all selected applicable items as a secondary breadth-sensitive result. Report fidelity, omission, unsupported claims, and pedagogy separately; do not form an overall composite.

The Frozen Contract is the normative authority for this experiment, including approved corrections under resolved `candidate_source_issues`. The evaluator tests agreement with that authority, not truth beyond its declared scope.

Severity meanings:

- `none`: the selected content preserves the relevant meaning, formula, conditions, and algorithm semantics;
- `minor`: a local imprecision that does not materially change learner understanding or implementation;
- `major`: an error, contradiction, or omission likely to cause materially incorrect understanding, calculation, or implementation;
- `critical`: a central definition, theorem, convergence claim, or algorithm is reversed, invalidated, or dangerously overgeneralised;
- `uncertain`: the available evidence cannot support a stable decision;
- `not_applicable`: a conditional item was not selected by the lesson.

## 2. Contract-item judgements

Evaluate every Contract item exactly once.

Required items:

- set `selection_basis` to `required`;
- set `applicability` to `applicable`, unless genuinely uncertain;
- use `omitted` when absent and `contradicted` when the lesson states an incompatible account.

Conditional items:

- use `conditional_selected` and `applicable` when the lesson teaches, invokes, or relies on the method or result;
- use `conditional_not_selected`, `not_applicable`, and `not_applicable` coverage/severity when it is absent and not needed by the common task brief;
- do not reward or penalise unselected optional breadth.

Coverage meanings:

- `full`: the complete obligation and material conditions are present;
- `partial`: the core idea is recognisable but a non-material part is absent;
- `omitted`: an applicable obligation is absent;
- `contradicted`: the lesson presents an incompatible statement;
- `uncertain` or `not_applicable`: as above.

Use one or more drift labels when present:

- `condition_dropped`
- `scope_overgeneralised`
- `formula_changed`
- `algorithm_changed`
- `concept_conflated`
- `analogy_promoted_to_fact`
- `prohibited_drift_triggered`
- `unsupported_extension`

Judge each Contract condition independently as `preserved`, `omitted`, `contradicted`, `not_applicable`, or `uncertain`.

## 3. Atomic-claim judgements

Split compound factual sentences into the smallest independently verifiable claims. Include mathematical, algorithmic, implementation, and disciplinary-application claims. Exclude headings, transitions, learning instructions, opinions, and purely motivational language.

Claim verdicts:

- `supported`: entailed by one or more Contract items or an approved correction;
- `unsupported`: factual but not supported within the Contract's authority boundary;
- `contradicted`: incompatible with the Contract;
- `not_verifiable`: outside the Contract and not safely classifiable as an unsupported mathematical extension.

Generated discipline context is not automatically an error. Mark it supported only when the Contract supports the factual mapping; otherwise use `not_verifiable` when it is clearly bounded as analogy, and `unsupported` or `contradicted` when it is asserted as fact without support.

## 4. Pedagogy judgements

Score each dimension from 1 to 5 with exact evidence:

- `learner_alignment`: depth and scaffolding fit the common profile;
- `disciplinary_authenticity`: context reflects credible disciplinary reasoning rather than noun substitution;
- `pedagogical_coherence`: prerequisites, sequencing, synthesis, and exercises form a defensible progression;
- `theory_implementation_alignment`: prose, mathematics, examples, and code agree;
- `readability`: headings, paragraphs, transitions, and notation are usable;
- `analogy_safety`: important mappings have explicit, proportionate boundaries;
- `exercise_validity`: tasks are solvable, aligned with taught material, and solutions are internally consistent.

Anchors: 1 = seriously deficient; 2 = substantial weaknesses; 3 = adequate with notable limitations; 4 = strong with minor limitations; 5 = consistently strong. Use `not_applicable` only when the lesson contains no material relevant to the dimension.

## 5. Evidence and abstention

Copy short exact excerpts from the anonymous lesson. Never invent line numbers. Omission can have no lesson excerpt. Set `abstain=true`, use uncertain categorical values, and explain the missing evidence whenever the Contract or lesson does not permit a defensible judgement. Confidence is a self-report for audit, not a correctness probability and not an outcome metric.

## 6. Reliability and validity checks

For confirmatory evaluation:

- run at least two fresh pointwise passes per sample;
- compute exact agreement and weighted agreement outside the judge;
- use a second evaluator model family when feasible;
- test the instrument on known clean examples and single-error synthetic mutations derived from Contract conditions and prohibited-drift rules;
- test pairwise ranking, if used, in both answer orders and discard position-inconsistent decisions;
- inspect correlation between word count and pedagogy scores as a verbosity-bias audit;
- retain all raw judgements and model/version metadata.

Automated evaluation is an operational instrument, not expert ground truth. Mutation sensitivity demonstrates detection of seeded errors but cannot establish performance on every naturally occurring error.
