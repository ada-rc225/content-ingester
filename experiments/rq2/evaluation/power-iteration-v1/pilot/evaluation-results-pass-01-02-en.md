# RQ2 Power Iteration Pilot Evaluation

Status: pilot, pre-adjudication report. This English document is the authoritative report for formal use. The accompanying Chinese document is a supplementary translation for researcher review.

Evaluation date: 19 August 2026  
Protocol: RQ2-EVAL-v1  
Topic: Power Iteration

## Executive conclusion

The pilot provides partial, not confirmatory, support for RQ2.

Dependency-aware P2 planning produced clearly different, profile-linked and deterministically valid pathway structures. Relative to P0, P2 received better ratings for disciplinary framing and sequence quality. Relative to the stronger P1 control, however, P2 showed almost no additional gain on the four primary pedagogy ratings: the median paired difference was zero in every dimension, with only one framing win and otherwise ties. This suggests that local profile-aware composition already reached a rating ceiling in this pilot, while P2's main observable contribution was structural differentiation rather than a large additional rubric-score gain.

Selected mathematical content was generally complete, correctly mapped, formula-accurate and dependency-coherent. The safety result was not uniformly successful. The computer-science P2 lesson failed H2c in both passes because it added algorithmic complexity and reproducibility claims outside the selected Frozen Contract and released bridge authority. One pass also identified a minor input-validation defect in the computer-science P1 implementation. These findings require adjudication and prevent a claim that correctness and provenance were preserved for every pilot output.

The current evidence therefore supports the feasibility of dependency-aware pathway adaptation and confirms materially different, profile-linked P2 pathways under the pre-specified structural metric. It does not yet establish that P2 is pedagogically superior to P1 or that H2c is satisfied across all profiles.

## Design and analysis set

The evaluated conditions were:

| Condition | Experimental role |
|---|---|
| P0 | One generic lesson using the fixed comprehensive pathway, evaluated relative to each of the three profiles |
| P1 | Profile-aware wording and examples inside an unchanged P0 selection and sequence |
| P2 | Profile-aware selection, ordering, grouping, depth and released prerequisite bridges |

The pilot contains seven unique generated lessons: one P0 lesson, three P1 lessons and three P2 lessons. For matched analysis, the same P0 artifact was evaluated against all three profiles, producing nine profile-relative blind samples. P0's three ratings must not be interpreted as three independent generated lessons.

Each blind sample received two fresh automated evaluator passes, giving 18 judgements and 18 deterministically validated score reports. Conditions remained hidden during pointwise judgement. The learner profile remained visible because profile fit is an outcome. The two passes are repeated automated measurements, not independent human experts and not additional lesson observations.

Lesson length was reasonably controlled:

| Condition/profile | English prose words | Sections | Selected Contract items | Released bridges |
|---|---:|---:|---:|---:|
| P0, reused | 1,636 | 8 | 18 | 0 |
| P1, applied mathematics | 1,500 | 8 | 18 | 0 |
| P1, computer science | 1,516 | 8 | 18 | 0 |
| P1, mechanical engineering | 1,554 | 8 | 18 | 0 |
| P2, applied mathematics | 1,568 | 7 | 18 | 1 |
| P2, computer science | 1,500 | 8 | 17 | 3 |
| P2, mechanical engineering | 1,554 | 18 | 17 | 3 |

Code-block quantity was not used as a teaching-quality measure. Code and algorithm safety were evaluated only where selected Contract opportunities required them.

## H2a: primary pedagogy outcomes

The following values collapse the two evaluator passes to the sample median and then summarize the three matched profiles. No composite pedagogy score was formed.

| Dimension | P0 median | P1 median | P2 median | P2-P1 median paired difference | P2-P0 median paired difference |
|---|---:|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 4.0 | 5.0 | 5.0 | 0.0 | +1.0 |
| Prerequisite match | 4.5 | 5.0 | 5.0 | 0.0 | 0.0 |
| Context-boundary awareness | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Sequence quality | 4.5 | 5.0 | 5.0 | 0.0 | +0.5 |

For P2-P1, disciplinary framing produced one win and two ties, giving a descriptive probability of superiority of 0.667. All three profiles tied on prerequisite match, context-boundary awareness and sequence quality. For P2-P0, framing and sequence each produced two wins and one tie, with descriptive probabilities of superiority of 0.833. Prerequisite match produced one win and two ties. Context-boundary awareness was tied for all profiles because every condition was rated at the ceiling.

Interpretation:

- P2 improved the weaker generic baseline most clearly in disciplinary framing and sequence quality.
- P2 did not materially outperform P1 on the primary ratings in this one-run pilot.
- P1 is functioning as a demanding control: profile-aware wording and representations can already score highly even when item selection and pathway order are fixed.
- Ceiling effects limit the sensitivity of the present rubric and lesson set, especially for context-boundary awareness.

Example authenticity remained exploratory. The sample-median pattern was approximately P0 = 2, P1 = 3 and P2 = 3. This suggests more credible disciplinary framing than the generic baseline, but it is not evidence of authentic professional practice and is not used to accept H2a.

## H2b: structural pathway differentiation

The P1 pathways were exact structural controls. Every cross-profile P1 comparison had zero selection, order, grouping, bridge and depth distance.

All three P2 cross-profile comparisons were deterministically valid, contained profile-linked rationales and were confirmed as material differences:

| P2 profile pair | Selection distance | Normalized order distance | Grouping distance | Bridge distance | Structural interpretation |
|---|---:|---:|---:|---:|---|
| Applied mathematics vs computer science | 0.0556 | 0.6667 | 0.3000 | 1.0000 | Selection, order, grouping, bridge and depth changed |
| Applied mathematics vs mechanical engineering | 0.0556 | 0.6667 | 1.0000 | 1.0000 | Selection, order, grouping, bridge and depth changed |
| Computer science vs mechanical engineering | 0.0000 | 0.1176 | 1.0000 | 0.0000 | Order, grouping and depth changed despite identical selected-item sets |

Within each profile, P2 also differed structurally from P1:

| Profile | Selection distance | Normalized order distance | Grouping distance | Bridge distance |
|---|---:|---:|---:|---:|
| Applied mathematics | 0.0000 | 0.1111 | 0.5882 | 1.0000 |
| Computer science | 0.0556 | 0.6111 | 0.4667 | 1.0000 |
| Mechanical engineering | 0.0556 | 0.6111 | 1.0000 | 1.0000 |

These are substantive pathway differences rather than lexical changes. Applied mathematics retained the full item set but changed order, grouping, bridge use and declared depth. Computer science and mechanical engineering additionally excluded one Contract item.

Under the strict metric, all three comparisons are now confirmed. Each final pathway has a `bridge-resolution-receipt.json` that hash-binds the materialized output to its approved parent pathway review, the released bridge catalog and the bridge release report. The evaluator independently verified every referenced file and hash, the parent review decision, the catalog's exact parent pathway/review binding and the released status before inheriting review authority. This does not claim that the reviewer directly reviewed the materialized file; it records that the reviewed planning decisions were carried through the constrained bridge-materialization step.

## H2c: selected-content safety

The all-pass sample counts were:

| Condition | Samples passing H2c in both evaluator passes |
|---|---:|
| P0 | 3/3 |
| P1 | 2/3 |
| P2 | 2/3 |

Across all outputs, required learning-goal coverage, formula provenance, structural dependency validation and released-bridge compliance were strong. No critical mathematical or algorithmic errors were reported. The failures were localized:

1. Computer-science P1: one evaluator pass judged RC-017 partially covered with a minor algorithmic error. The implementation rejects max_iterations values below one but does not explicitly require an integer; a positive non-integer reaches range and raises TypeError rather than the intended clear validation error. The other pass accepted the implementation. Human adjudication is required.
2. Computer-science P2: both passes found unsupported algorithmic complexity claims outside the selected Contract and released bridges. Both agreed on dense O(n^2) and sparse nonzero-dependent cost claims; one pass additionally flagged iteration-work and reproducibility characterizations. The selected mathematics, formulas and core algorithm were otherwise judged complete and correct. Because H2c is conjunctive, these provenance extensions make the whole sample fail.

The P2 computer-science issue is directly actionable: either remove the extra complexity/reproducibility assertions or add a separately grounded and reviewed source/bridge authority for them. It should not be repaired silently after inspecting results; any regeneration rule used in confirmatory work must be pre-specified and applied consistently.

## Evaluator reliability

| Dimension | Exact agreement | Mean absolute difference | Disagreements of at least 2 | Ordinal Krippendorff alpha |
|---|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 0.889 | 0.111 | 0 | 0.799 |
| Prerequisite match | 0.556 | 0.444 | 0 | -0.214 |
| Context-boundary awareness | 1.000 | 0.000 | 0 | 1.000 |
| Sequence quality | 0.778 | 0.222 | 0 | 0.655 |

No primary rating differed by two or more points. The negative prerequisite alpha occurred despite only one-point disagreements and reflects weak discrimination plus severe ceiling concentration in this small sample. It should not be treated as adequate reliability. Prerequisite-match anchors need calibration examples and human adjudication before confirmatory scoring. Context-boundary agreement is perfect but also ceiling-saturated, so high agreement alone does not establish sensitivity.

## RQ2 decision for this pilot

| Component | Pilot decision |
|---|---|
| H2a: P2 has higher pedagogical ratings | Partially supported versus P0; not supported versus P1 in this pilot |
| H2b: P2 produces materially different profile-linked pathways | Supported: all three cross-profile comparisons are deterministically valid and confirmed through verified materialization-receipt review authority |
| H2c: every selected pathway preserves correctness, provenance and dependency coherence | Not fully satisfied before adjudication because one P1 and one P2 computer-science sample failed the conjunctive gate |
| Overall RQ2 | Feasibility and structural adaptation supported; comparative pedagogical superiority and uniform safety not yet established |

## Required next actions

1. Human-adjudicate the P1 RC-017 integer-validation issue and the P2 computer-science unsupported complexity claims. Preserve both raw passes.
2. Calibrate prerequisite-match anchors with positive, borderline and negative examples; the current repeatability is insufficient.
3. Freeze the corrected pilot protocol and then run the planned three independent generations per profile-condition cell. Do not count repeated judges or profile-relative P0 ratings as independent lesson runs.
4. Repeat the same design on Gradient Descent before making a cross-topic portability claim. The present cross-topic summary contains only Power Iteration.
5. Keep example authenticity exploratory and do not claim learner comprehension or learning gain without a student study.

## Generated evidence

- aggregate-results.json: condition summaries and paired contrasts;
- reliability-report.json: raw pass agreement;
- pathway-difference-report-confirmed.json: confirmed cross-profile P2 structure comparisons with verified receipt-based review authority;
- pathway-difference-report.json: retained pre-inheritance candidate report for audit history;
- p1-pathway-difference-report.json: fixed-pathway control check;
- three profile-specific P2-vs-P1 pathway-difference reports;
- blind-samples, judge-pass-01, judge-pass-02 and private-mappings: auditable pointwise evidence.
