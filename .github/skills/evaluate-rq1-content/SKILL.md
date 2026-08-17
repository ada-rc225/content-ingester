---
name: evaluate-rq1-content
description: Independently and blindly evaluate long-form RQ1 teaching adaptations against one released Frozen Reference Contract. Use for item-level mathematical and algorithmic fidelity, semantic drift, required-content omission, unsupported atomic claims, and secondary pedagogy scoring across anonymised C0/C1/C2 samples, with deterministic metric recomputation and judge-bias controls.
---

# Evaluate RQ1 content

Evaluate anonymous teaching samples with protocol version `RQ1-EVAL-v1`. Keep outcome evaluation separate from generation and C2 treatment validation.

## Read first

Read `references/evaluation-protocol.md` completely. Read `references/evaluation-judgement.schema.json` before writing judgements. Do not read generation rubrics, source lessons, adaptation plans, provenance, validation reports, summaries, run manifests, condition mappings, or outputs from another sample.

## Preconditions

Require one blind bundle produced by `scripts/build_blind_bundle.py`. It must contain:

- `evaluation_manifest.json`;
- one released `frozen_reference_contract.json`;
- one common `learner_profile.json`;
- one common `task_brief.txt`;
- anonymous lesson files under `samples/`.

Refuse a bundle whose sample names, files, manifest, or surrounding path expose C0/C1/C2 labels. Refuse candidate Contracts and unblinded inputs. Do not open the separately stored condition mapping.

## Workflow

1. Verify bundle hashes with:

   `python3 .github/skills/evaluate-rq1-content/scripts/validate_blind_bundle.py --bundle <bundle-dir>`

2. Read only the bundle manifest, Frozen Contract, common learner profile, task brief, and the single anonymous sample being judged.
3. Evaluate every Contract item exactly once. Required items are applicable. For each conditional item, decide whether the anonymous lesson selects that method or result; do not penalise an unselected conditional item.
4. Judge coverage, error severity, drift types, each stated condition, exact lesson evidence, confidence, and abstention. Apply approved Contract corrections recorded under resolved source issues. Never trust hidden or claimed RC mappings from a generated lesson.
5. Decompose every substantive mathematical, algorithmic, implementation, and disciplinary-application claim in the lesson into atomic claims. Mark each supported, unsupported, contradicted, or not verifiable from the Contract. Do not treat pedagogy, transitions, or instructions as factual claims.
6. Score the seven pedagogy dimensions independently. Do not create an overall quality score and never allow good prose to cancel a mathematical error.
7. Write one `judgement.json` for one sample and one independent judge pass. Use exact excerpts rather than invented line references. Keep the sample ID anonymous.
8. Run:

   `python3 .github/skills/evaluate-rq1-content/scripts/validate_and_score.py --bundle <bundle-dir> --judgement <judgement.json> --output <score-report.json>`

9. Patch only the judgement fields named by validation errors and rerun. Never edit a deterministic score report.

## Independence and bias controls

- Use pointwise item-level evaluation as the primary instrument. Do not compare two lessons in the same judge context.
- Start a fresh context for each sample and pass. Use the same evaluator model, prompt version, and inference settings throughout a confirmatory comparison.
- Run at least two independent passes per sample; three are preferred. Preserve disagreements rather than silently reconciling them.
- Keep word count out of correctness judgements. Report verbosity or readability only under their named pedagogy dimensions.
- Return `uncertain` with `abstain=true` when the Contract cannot support a defensible decision.
- Do not infer experimental condition from prose style, formatting, or likely authorship.

After all blind passes are complete, compute judge stability without opening the mapping:

`python3 .github/skills/evaluate-rq1-content/scripts/assess_judge_reliability.py --judgement <pass-1.json> --judgement <pass-2.json> [--judgement ...] --output <reliability-report.json>`

## Metric boundary

Treat the generated score report as the RQ1 operational outcome measurement. Treat C2 `treatment_valid`, Contract release status, code execution during generation, and generation-side coverage declarations only as manipulation checks. Never use those C2-only fields to score C0 or C1.

Use `scripts/aggregate_rq1_scores.py` only after all judging is complete and only from a separate experiment-controller context that is allowed to read the condition mapping. The evaluator itself must remain blind.
