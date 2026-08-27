# RQ2 Gradient Descent Three-Run Evaluation Report

Status: expanded pilot, before human adjudication. This report combines run-01, run-02, and run-03 while preserving the original single-run report and all pointwise judgements.

Evaluation date: 26 August 2026  
Protocol: RQ2-EVAL-v1  
Topic: Gradient Descent

## Main conclusion

Gradient Descent now has three lesson-generation runs. The evidence set contains 21 lessons, 27 profile-relative blind samples, 54 isolated evaluator judgements, and 54 score reports with `valid=true`.

The combined result remains expanded-pilot evidence:

- H2a is partly supported against P0. The median paired P2-P0 difference is +1.0 for disciplinary framing and +0.5 for sequence quality; it is zero for prerequisite match and context-boundary awareness.
- H2a is not supported against the stronger P1 control. All four median paired P2-P1 differences are zero, and the descriptive mean differences for framing and prerequisite match slightly favour P1. P1 and P2 show substantial ceiling concentration.
- The existing H2b structural result remains supported: all three P2 profile pathways have validated, profile-rationale-linked material differences. Runs 02 and 03 reused the same final pathways, however, so they add lesson-composition replication rather than independent pathway-planning replication.
- H2c is not uniformly satisfied. Requiring both evaluator passes to pass gives P0 9/9, P1 9/9, and P2 8/9. The only failure is the run-01 mechanical-engineering P2 sample; every run-02 and run-03 sample passes in both evaluations.

The defensible RQ2 interpretation is therefore that profile-aware P1/P2 composition improves some automated pedagogical measures over generic P0 and that P2 produces genuine structural adaptation. The evidence does not show that P2 outperforms P1 on the rubric, and it does not establish uniform P2 safety.

## Sample and generation audit

Each run contains one shared P0 lesson, three P1 lessons, and three P2 lessons.

| Condition | Independently generated lessons | Profile-relative blind samples | Evaluator judgements |
|---|---:|---:|---:|
| P0 | 3 | 9 | 18 |
| P1 | 9 | 9 | 18 |
| P2 | 9 | 9 | 18 |
| Total | 21 | 27 | 54 |

Each P0 lesson is evaluated relative to all three profiles, so the nine P0 blind samples are not nine independent lesson generations. All 21 `lesson.md` SHA-256 hashes are unique. The 21 Composer validation reports are all `valid=true` with zero errors and zero warnings; all 21 code validations are `passed`; and every lesson satisfies the prespecified 2,200–2,500 English-prose word range.

The generation environment was not fully frozen. Run-01 manifests identify GitHub Copilot / GPT-5.6 Luna / VS Code agent, whereas runs 02 and 03 identify OpenAI / gpt-5.6-sol / codex-exec-ephemeral. All 54 evaluations identify OpenAI / gpt-5.6-sol / RQ2-EVAL-v1. The added runs are consequently useful as an expanded pilot and robustness check, but they are not a strict confirmatory replication under identical generation settings.

## Per-run results

The vectors below are ordered as disciplinary framing, prerequisite match, context-boundary awareness, and sequence quality. Scores are first reduced to the median of the two judges for each profile-condition sample and then compared within matched profiles.

| Run | H2c P0 | H2c P1 | H2c P2 | Median paired P2-P1 differences | Median paired P2-P0 differences |
|---|---:|---:|---:|---|---|
| run-01 | 3/3 | 3/3 | 2/3 | (0, 0, 0, 0) | (+1.0, 0, 0, +1.0) |
| run-02 | 3/3 | 3/3 | 3/3 | (0, 0, 0, 0) | (+1.0, 0, 0, 0) |
| run-03 | 3/3 | 3/3 | 3/3 | (0, 0, 0, 0) | (+1.5, 0, 0, +0.5) |

Every run has zero median P2-P1 differences on all four dimensions. P2 improves framing over P0 in the same direction in all three runs. A median sequence improvement appears in runs 01 and 03, while run-02 has a zero median sequence difference.

## Combined H2a results

| Primary measure | P0 median | P1 median | P2 median | Median P2-P1 difference | Median P2-P0 difference |
|---|---:|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 3.5 | 5.0 | 5.0 | 0.0 | +1.0 |
| Prerequisite match | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Context-boundary awareness | 5.0 | 5.0 | 5.0 | 0.0 | 0.0 |
| Sequence quality | 4.5 | 5.0 | 5.0 | 0.0 | +0.5 |

The matched P2-P1 win/tie/loss counts are 1/6/2 for framing, 0/6/3 for prerequisite match, 1/7/1 for boundary awareness, and 1/8/0 for sequence. Their mean paired differences are -0.222, -0.222, 0, and +0.056. Against P0, framing is 6/3/0 and sequence is 5/4/0; these are the most stable descriptive improvements. The sample covers only one topic, so no significance or generalisability claim is made.

## H2b: structural differences and the replication boundary

The confirmed report marks every cross-profile P2 comparison as a material difference:

| P2 profile pair | Selection distance | Normalised order distance | Grouping distance | Bridge distance |
|---|---:|---:|---:|---:|
| Applied mathematics vs computer science | 0.0000 | 0.5000 | 0.0000 | 0.2500 |
| Applied mathematics vs mechanical engineering | 0.0000 | 0.5000 | 0.0000 | 0.0000 |
| Computer science vs mechanical engineering | 0.0000 | 0.0000 | 0.0000 | 0.2500 |

All Gradient Descent P2 pathways select the same 12 Contract items. The material differences arise from order, released bridges, and declared depth rather than selection. Each comparison is tied to valid pathways, profile rationales, and approved parent-review/materialisation authority, so these are structural changes rather than lexical substitutions.

All three composition runs use the same final P0/P1/P2 pathway files. They test whether repeated lesson composition from fixed pathways yields similar outcomes; they do not test whether independently rerunning the Planner would reproduce the same adaptations.

## H2c safety gate

| Condition | Both passes pass | Result |
|---|---:|---|
| P0 | 9/9 | All pass |
| P1 | 9/9 | All pass |
| P2 | 8/9 | Run-01 mechanical engineering fails |

Across all 54 score reports, the minima for required-goal coverage, selected-Contract-item coverage, formula provenance, hard-dependency validation, released-bridge compliance, formula accuracy, and algorithm accuracy are all 1.0. There are no critical errors, and every dependency-coherence verdict is `pass`.

The only repeated gate failure is S-V95J, P2 mechanical engineering run-01. Both passes identify mathematical or algorithmic diagnostic advice outside Frozen Contract and released-bridge authority, including a finite-difference gradient check. The second pass additionally flags step/acceptance and gradient-diagnostic advice. The selected Gradient Descent core, formulas, and algorithms remain complete and correct, but the conjunctive H2c gate does not permit these unsupported extensions.

Some H2c-passing samples still receive discipline-authenticity adjudication recommendations for bounded application analogies that cannot be independently verified from the available authority. Those recommendations are separate from mathematical or algorithmic safety failures and are not substitutes for expert disciplinary review.

## Evaluator reliability

| Measure | Exact agreement | Mean absolute difference | Differences of at least 2 | Ordinal Krippendorff alpha |
|---|---:|---:|---:|---:|
| Disciplinary framing appropriateness | 0.852 | 0.148 | 0 | 0.930 |
| Prerequisite match | 0.852 | 0.148 | 0 | 0.264 |
| Context-boundary awareness | 0.926 | 0.074 | 0 | -0.019 |
| Sequence quality | 0.889 | 0.111 | 0 | 0.765 |

No primary dimension has a judgement difference of two points or more. Prerequisite and boundary scores have high exact agreement but low or slightly negative alpha because ratings are concentrated near 4–5 with very little marginal variance. This should not be interpreted as strong scale discrimination. The two passes are isolated repeat measurements from the same automated evaluator configuration, not two independent human experts.

## RQ2 decision

| Component | Three-run decision |
|---|---|
| H2a: P2 has higher pedagogical ratings | Partly supported against P0 for framing and sequence; not supported against P1 |
| H2b: P2 produces materially different, profile-linked pathways | Supported by the existing structural evidence; the added runs do not independently rerun the Planner |
| H2c: each selected pathway preserves correctness, provenance, and dependency coherence | Not uniformly satisfied; P2 passes 8/9 samples in both evaluations |
| Overall RQ2 | Supports structural-adaptation feasibility and some descriptive benefit over P0; does not support P2 superiority over P1 or uniform safety |

## Next steps

1. Human-adjudicate S-V95J and bounded disciplinary claims while retaining both original judgements.
2. Freeze the generation model, access route, prompt, budget, and output settings before a confirmatory run.
3. If the research claim includes planning replication, independently rerun the Planner for each P2 cell rather than only rerunning the Composer from reused pathways.
4. Refine the prerequisite and context-boundary anchors to reduce 4–5 ceiling saturation.
5. Do not claim learner comprehension, learning gain, or authentic professional-practice effectiveness without multiple topics, disciplinary expert review, or student evidence.

## Main evidence files

- `aggregate-results-run-01-03.json`: combined condition summaries and paired comparisons;
- `aggregate-results.json`, `aggregate-results-run-02.json`, and `aggregate-results-run-03.json`: per-run aggregates;
- `reliability-report-run-01-03.json`: overall reliability across 54 judgements;
- `reliability-report.json`, `reliability-report-run-02.json`, and `reliability-report-run-03.json`: per-run reliability;
- `pathway-difference-report-confirmed.json`: cross-profile P2 structural differences;
- `blind-samples/`, `judge-pass-01/`, `judge-pass-02/`, and `private-mappings/`: auditable pointwise evidence.
