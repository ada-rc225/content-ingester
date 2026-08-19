---
name: evaluate-rq2-pathways
description: Independently and blindly evaluate one RQ2 pathway-constrained lesson against its learner profile, learning request, selected Frozen Contract scope, and sanitized pathway evidence. Use for evidence-anchored 1-5 ratings of disciplinary framing, prerequisite match, context-boundary awareness, and sequence quality; exploratory example authenticity; selected-content semantic safety; judge reliability; and controller-side P2-P1/P2-P0 aggregation without treating automated judgement as student evidence or expert ground truth.
---

# Evaluate RQ2 pathways

Use protocol `RQ2-EVAL-v1`. Keep pointwise outcome evaluation separate from generation, pathway approval, and condition-level analysis.

## Read first

Read `references/evaluation-protocol.md` completely. Read `references/rq2-evaluation-judgement.schema.json` before writing a judgement. Do not read generation prompts, pathway reviews, condition mappings, other lessons, other judge outputs, or unblinded source directories.

## Preconditions

Require one blind sample bundle created by `scripts/prepare_blind_sample.py`. It must contain:

- `evaluation-manifest.json`;
- `lesson.md`;
- `learner-profile.json`;
- `learning-request.json`;
- `frozen-reference-contract.json`;
- `pathway-evidence.json`;
- `structural-validation-evidence.json`.

Refuse candidate Contracts, stale hashes, invalid structural evidence, condition labels, or an output directory containing a prior judgement for the same sample and pass. The learner profile is visible because profile fit is an outcome; the P0/P1/P2 condition is not.

## Pointwise workflow

1. Verify the bundle:

   `python3 .github/skills/evaluate-rq2-pathways/scripts/validate_blind_sample.py --bundle <bundle-dir>`

2. Generate a complete pending template:

   `python3 .github/skills/evaluate-rq2-pathways/scripts/create_judgement_template.py --bundle <bundle-dir> --output <output-dir>/judgement.json --evaluator-id <id> --provider <provider> --model <model> --access-route <route> --pass-index <n> --evaluated-at <ISO-8601>`

3. Read only the seven bundle files and complete every pending judgement. Copy short exact lesson excerpts; never invent line numbers. Use abstention when the evidence does not support a stable decision.
4. Judge the four primary pedagogy dimensions independently. Do not form an overall pedagogy score. Keep example authenticity exploratory.
5. Judge every selected Contract item, every selected formula reference, every selected algorithm/code item, every requested learning goal, and every unsupported factual claim. A declared lesson-map binding is not proof of semantic coverage.
6. Run deterministic validation and scoring:

   `python3 .github/skills/evaluate-rq2-pathways/scripts/validate_and_score.py --bundle <bundle-dir> --judgement <output-dir>/judgement.json --output <output-dir>/score-report.json`

7. Patch only fields named by validation errors and rerun. Never edit `score-report.json` manually.

## Independence controls

- Evaluate one anonymous sample per fresh context and pass.
- Do not compare lessons during pointwise judgement.
- Use the same evaluator prompt and inference settings across confirmatory samples.
- Preserve independent passes; do not silently reconcile them.
- Do not infer a condition from style, breadth, bridges, or sequence.
- Do not reward verbosity or a larger selected scope.
- Do not claim learner comprehension, learning gain, or student preference.
- Treat automated ratings as operational measurements requiring reliability analysis and human calibration/adjudication.

## After all blind passes

Assess reliability before opening condition mappings:

`python3 .github/skills/evaluate-rq2-pathways/scripts/assess_judge_reliability.py --judgement <judgement.json> [--judgement ...] --output <reliability-report.json>`

Only an experiment-controller context may use `aggregate_rq2_scores.py` with separately stored mappings. The pointwise Evaluator must never open mappings or produce condition rankings.

