# RQ2: pathway-level adaptation

## Research question and hypothesis

Can dependency-aware, learner-profile-driven pathway adaptation produce
materially different and pedagogically appropriate content selections and
learning sequences while preserving the correctness, provenance, and dependency
coherence of the mathematical content selected for each learner?

H2a predicts higher disciplinary framing appropriateness, prerequisite match,
context-boundary awareness, and sequence quality for P2 than P0/P1. H2b
predicts at least one profile-justified, dependency-valid structural difference
between P2 pathways. H2c requires complete coverage, provenance, correctness,
and dependency coherence for every pathway's selected content. Learner-reported
comprehensibility is outside the current no-student-study scope and must not be
inferred from expert or AI scores.

## Confirmatory comparison

Use the same Frozen Reference Contract, shared learning request, model family,
generation budget, and output form in every condition. P0/P1 share the fixed
baseline selection and sequence. Only P2 receives the Frozen Curriculum
Dependency Model and permission to select and restructure content.

| Condition | Learner information | Wording/examples | Contract selection and sequence |
|---|---|---|---|
| P0 generic | No discipline profile | Generic | One fixed comprehensive selection and sequence |
| P1 local adaptation | Full profile | Adapted inside fixed learning units | Exactly the P0 item selection and sequence |
| P2 pathway-level | Full profile | Adapted | May decide every Contract item, reorder/regroup selected content, and request or use prerequisite bridges |

P1 is the critical control: it prevents discipline-specific vocabulary or
examples alone from being counted as pathway adaptation. A learning unit is an
analysis/planning unit, not a page: every condition produces one continuous
student-facing lesson. P0 should be generated once per run
and reused across profiles during evaluation; generating a nominally generic
baseline separately for each profile would introduce avoidable variation.

## Experimental unit and minimum design

- Start with one topic whose Frozen Contract is already stable (power iteration
  is the recommended pilot), then confirm on gradient descent.
- Use at least three meaningfully different disciplinary profiles. The profiles
  must differ in authentic prior knowledge and representational preferences,
  not just in discipline labels.
- Generate three independent runs for each profile-condition cell. With three
  profiles and P1/P2, this gives 18 adapted pathways, plus three reusable P0
  runs per topic.
- Blind evaluators to condition and profile identity wherever the rubric does
  not require profile comparison.
- Freeze prompts, contracts, profiles, generation settings, and the analysis
  rules before inspecting condition summaries.

The initial profiles are placeholders for piloting and must be reviewed by a
subject/discipline educator before confirmatory generation.

## Primary outcomes

Score each pathway separately; do not form one fidelity-pedagogy composite.

1. **Disciplinary framing appropriateness** (1-5): terminology,
   representations, motivations, and interpretive perspectives are suitable for
   the profile and materially support understanding rather than merely changing
   discipline-specific nouns.
2. **Prerequisite match** (1-5): introduced concepts match declared knowledge,
   with explicit bridges for missing prerequisites.
3. **Context-boundary awareness** (1-5): disciplinary analogies and contextual
   interpretations state the assumptions and limitations needed to avoid
   presenting an idealized teaching bridge as a general domain fact or
   production method.
4. **Sequence quality** (1-5): ordering respects dependencies and provides a
   justified progression for the profile.
Also judge learning-goal coverage, inclusion/exclusion appropriateness,
unnecessary content load, and the quality of profile-linked selection rationales.
For these four outcomes, report P2-P1 and P2-P0 contrasts with uncertainty
intervals. Treat individual pathway runs and learner ratings as nested within
topic/profile; do not treat rubric items or duplicate judge passes as independent
sample size.

## Exploratory outcome

Score **example authenticity** (1-5) separately: whether a contextual example
resembles a plausible disciplinary task rather than merely relabelling a generic
mathematical example. Report it descriptively as exploratory evidence. Do not
include it in H2a acceptance, combine it with the four primary outcomes, or
reinterpret framing quality as evidence that the application itself is
authentic.

This outcome definition is a pilot-stage, pre-confirmatory amendment recorded
as `RQ2-OUTCOME-AMENDMENT-001` in `protocol.json`. It replaces disciplinary
relevance and confirmatory example authenticity with the two more specific
constructs above before the rubric and analysis rules are frozen. Existing
pilot lessons remain unchanged and are not confirmatory observations.

## Selected-content fidelity gate

Before pedagogy is interpreted, each output must pass deterministic provenance,
contract coverage, dependency, formula, and executable-code validation.

Freeze these rules before confirmatory data collection:

- required learning-goal coverage and selected-item coverage must both be 100%;
- selected-formula provenance, hard-dependency satisfaction, and released-bridge
  compliance must be 100%;
- no critical mathematical or algorithmic error is allowed;
- no unsupported mathematical claim is allowed; and
- formula and algorithm accuracy must be assessed against selected opportunities,
  not against raw counts from the more comprehensive P0/P1 baseline.

If a P2 pathway fails the gate, it cannot be described as pedagogically
successful even if its adaptation ratings are high. Report failures rather
than silently regenerating them. Any regeneration policy must be fixed in
advance and applied equally across conditions.

## Demonstrating that pathways are materially different

H2 requires more than high rubric scores. Record a machine-readable pathway
plan for every output and compare profiles within P2 using:

- normalized learning-unit order edit distance;
- selected/excluded Contract-item differences;
- prerequisite-bridge additions;
- prerequisite-relation differences;
- location of first introduction for every selected target concept; and
- a written rationale linking every structural change to a profile attribute.

Declare a P2 profile pair materially different only when it has at least one
dependency-valid change in Contract selection, learning order, or prerequisite
bridging and the change is judged pedagogically justified. Lexical or example
changes alone do not satisfy this criterion.

## Learner study boundary

The current project does not run a student study. It may report expert-judged
disciplinary framing appropriateness, prerequisite match, context-boundary
awareness, sequence quality, readability, and exploratory example authenticity,
but it must not rename readability as learner-reported comprehensibility or
claim measured learning gains.

## Execution stages

1. Build a candidate Contract-item dependency model from the released Frozen
   Contract using `Grounded Curriculum Dependency Builder`.
2. Review and freeze the dependency model with `Curriculum Model Release Gate`
   before it becomes pathway authority.
3. Review and freeze the shared learning request and learner profiles.
4. Normalize the fixed P0 baseline into the unified pathway-plan schema and
   create exact P1 copies with profile bindings.
5. Use Adaptive Curriculum Pathway Planner v1.1 to generate provisional P2
   plans, pending hash-bound reviews, and review-bounded revisions where needed.
6. Approve the revised pathway scope and concept judgements, then build, review,
   and release only the prerequisite bridges the approved plans actually
   request.
7. Build one Pathway-Constrained Teaching Composer for P0/P1/P2 and run the
   Power Iteration pilot.
8. Revise the rubric only from blinded pilot observations, then freeze it.
9. Run three confirmatory generations per cell on both topics.
10. Conduct two blind expert/AI-assisted ratings, followed by adjudication of
    disagreements and all mathematical errors.

## RQ2 blind evaluation agent

Use `RQ2 Independent Evaluator` only after a lesson has passed Composer
validation. It evaluates one anonymous lesson at a time, can see the learner
profile needed for profile-fit judgements, and cannot see whether the lesson is
P0, P1, or P2. It writes an evidence-anchored `judgement.json`; a deterministic
script validates that every selected Contract item, selected formula reference,
algorithm/code item, and learning goal was judged before producing
`score-report.json`.

Create a blind sample from an unblinded experiment-controller context. Store the
mapping outside the bundle and use opaque paths that do not contain condition
labels:

```bash
python3 .github/skills/evaluate-rq2-pathways/scripts/prepare_blind_sample.py \
  --workspace-root . \
  --lesson-run <lesson-run-dir> \
  --profile <learner-profile.json> \
  --sample-id <opaque-sample-id> \
  --bundle-dir <blind-root>/<opaque-sample-id> \
  --mapping-output <controller-only-root>/<opaque-sample-id>-mapping.json \
  --generated-at <ISO-8601>
```

Select `RQ2 Independent Evaluator` in a fresh context and instruct it:

```text
Evaluate exactly one anonymous RQ2 sample using RQ2-EVAL-v1.
Blind bundle: <blind-root>/<opaque-sample-id>
Output directory: <evaluation-root>/<opaque-sample-id>/judge-01
Evaluator metadata: provider=<provider>, model=<model>, access route=<route>,
evaluator ID=<id>, pass index=1, evaluated at=<ISO-8601>.
Do not read condition mappings, other samples, generation files, or prior judgements.
Create judgement.json and the deterministic score-report.json only.
```

Run at least two fresh passes per sample. Assess raw inter-judge reliability
before opening mappings:

```bash
python3 .github/skills/evaluate-rq2-pathways/scripts/assess_judge_reliability.py \
  --judgement <sample-a-judge-01.json> \
  --judgement <sample-a-judge-02.json> \
  --judgement <sample-b-judge-01.json> \
  --judgement <sample-b-judge-02.json> \
  --output <reliability-report.json>
```

Only the experiment controller may subsequently combine score reports with the
separately stored mappings through `aggregate_rq2_scores.py`. The four primary
ordinal outcomes remain separate; example authenticity remains exploratory;
automated ratings are operational measurements rather than student evidence or
expert ground truth. No student questionnaire is required for this artifact-level
RQ2, and the resulting evidence cannot support claims about measured learning or
learner-reported comprehensibility.

For the final cross-profile P2 structural comparison, bind each
bridge-materialized pathway through its receipt rather than creating a duplicate
review:

```bash
python3 .github/skills/evaluate-rq2-pathways/scripts/compute_pathway_differences.py \
  --workspace-root . \
  --pathway <profile>=<final-pathway-plan.json> \
  --validation <profile>=<final-pathway-validation-report.json> \
  --materialization-receipt <profile>=<bridge-resolution-receipt.json> \
  --output <pathway-difference-report.json>
```

Repeat the three labelled options once per profile. The evaluator accepts one
review authority per profile: `--review` for a directly reviewed pathway, or
`--materialization-receipt` for a final pathway that inherits its approved
planning review through verified bridge materialization.

## Initial artifacts

- `protocol.json`: machine-readable frozen-design candidate.
- `learning-requests/power-iteration-second-year.json`: the shared task anchor;
  it fixes required capabilities without fixing a universal P2 item set. Its
  existing duration value is compatibility metadata, not a Planner review or
  selection criterion.
- `schemas/learning-request.schema.json`: the shared-task structural contract.
- `schemas/pathway-plan.schema.json`: one pathway format for P0, P1, and P2;
  condition-specific rules ensure only P2 can bind the curriculum dependency
  model.
- `schemas/profile-concept-assessment.schema.json`: the Planner's explicit,
  hash-bound judgement of each profile's prerequisite-concept mastery.
- `schemas/pathway-plan-review.schema.json`: the pending human-review and
  revision-authorization contract for each P2 candidate.
- `schemas/bridge-library.schema.json`: the compact candidate format for only
  the prerequisite bridges requested by approved P2 pathways.
- `profiles/*.json`: pilot learner profiles requiring educator review.
- `specs/power-iteration/common-core.json`: historical P0/P1 fixed-baseline
  scope; it is not a universal-core constraint on P2 under protocol v0.3.
- `specs/power-iteration/canonical-pathway.json`: the immutable P0/P1 content
  selection and learning sequence, and the reference point for measuring P2.
- `specs/power-iteration/condition-permissions.json`: the treatment-isolation
  matrix for P0, P1, and P2.
- `specs/power-iteration/notation-policy.json`: permitted semantic notation
  adaptation and prohibited problem changes.

The reusable, non-experimental dependency lineage is stored separately under
`curriculum-models/power-iteration-v1/`. The original proposal is `candidate/`;
the review-bounded reconstruction is `candidate-v2/`. A Builder output is always
marked `candidate`, `unreviewed`, and `approval=null`. Passing deterministic
validation establishes structural and release-binding integrity, not pedagogical
approval. The Builder also creates `curriculum-dependency-review.json`, bound to
the exact candidate and validation-report hashes. All item, prerequisite-concept,
and overall decisions initially remain `pending` for an independent subject or
curriculum reviewer to complete.

Build another candidate after a Grounding Release Gate succeeds by selecting
`Grounded Curriculum Dependency Builder`, or invoke its skill workflow from
`.github/skills/build-curriculum-dependencies/SKILL.md`.

The same Builder owns review-driven reconstruction. Select `revision` mode only
after the parent review is complete and marked `revision_required`; provide the
parent candidate and review plus a new candidate directory. The Builder creates
a hash-bound revision receipt, increments the dependency-model version, applies
only explicitly reviewed fields, runs base and revision-scope validation, and
generates a new review with every decision reset to `pending`. The Curriculum
Model Release Gate must not perform or repair revisions.

After an authorised reviewer approves every populated field, every item and
concept, and the overall decision, select `Curriculum Model Release Gate` or run:

```bash
python3 .github/skills/release-curriculum-model/scripts/release_curriculum_model.py \
  --workspace-root . \
  --contract experiments/rq1/reference-contracts/power-iteration-v1/release/frozen_reference_contract.json \
  --candidate curriculum-models/power-iteration-v1/candidate-v2/contract-dependencies.json \
  --validation-report curriculum-models/power-iteration-v1/candidate-v2/dependency-validation-report.json \
  --review curriculum-models/power-iteration-v1/candidate-v2/curriculum-dependency-review.json \
  --output-dir curriculum-models/power-iteration-v1/release
```

The gate reruns base and revision-scope validation, verifies every review and
SHA-256 binding, and writes the release atomically. It changes only lifecycle,
item-review, and approval metadata. In particular, prerequisite bridge records
remain `status=candidate`; a frozen dependency model does not release bridge
teaching content.

### Current Power Iteration release status

`curriculum-models/power-iteration-v1/release/` is released and valid. Its frozen
dependency model is P2 planning authority only; P0/P1 continue to use the fixed
baseline pathway.

The v0.3 Planner is implemented as version 1.1 in
`.github/agents/adaptive-curriculum-pathway-planner.agent.md` backed by
`.github/skills/plan-adaptive-curriculum-pathways/`. It accepts the two released
authorities, one profile, the shared request, and a unified P0 baseline. Its
preflight verifies every release and SHA-256 binding before the Planner can make
P2 decisions:

```bash
python3 .github/skills/plan-adaptive-curriculum-pathways/scripts/prepare_pathway_inputs.py \
  --workspace-root . \
  --reference-contract experiments/rq1/reference-contracts/power-iteration-v1/release/frozen_reference_contract.json \
  --curriculum-model curriculum-models/power-iteration-v1/release/frozen-contract-dependencies.json \
  --learning-request experiments/rq2/learning-requests/power-iteration-second-year.json \
  --profile <profile.json> \
  --baseline-pathway <unified-p0-plan.json> \
  --output <p2-run-dir>/planner-input-receipt.json \
  --view-output <p2-run-dir>/planner-input-view.json
```

The Planner writes a profile-concept assessment and unified P2 plan, then uses
the same deterministic validator that will later validate P0 and exact P1
copies:

```bash
python3 experiments/rq2/scripts/validate_pathway_plan.py \
  --workspace-root . \
  --pathway <run-dir>/pathway-plan.json \
  --output <run-dir>/pathway-validation-report.json \
  --phase pilot
```

After validation, the Planner must create an entirely pending review:

```bash
python3 .github/skills/plan-adaptive-curriculum-pathways/scripts/create_pathway_plan_review.py \
  --workspace-root . \
  --pathway <run-dir>/pathway-plan.json \
  --validation-report <run-dir>/pathway-validation-report.json \
  --assessment <run-dir>/profile-concept-assessment.json \
  --output <run-dir>/pathway-plan-review.json
```

The review covers every item decision, concept assessment and bridge decision,
learning-goal mapping, grouping, sequence, prerequisites, pathway-change claim,
failure/convergence scope, and overall profile appropriateness. It deliberately
contains no unit-time or time-feasibility decision. The later Composer owns a
frozen word-count protocol.

When a completed review has `review_status=revision_required`, invoke Planner
`revision` mode with the parent plan, assessment, validation report, review, and
a new output directory. The deterministic preflight creates the permitted scope:

```bash
python3 .github/skills/plan-adaptive-curriculum-pathways/scripts/prepare_pathway_revision.py \
  --workspace-root . \
  --parent-pathway <parent-dir>/pathway-plan.json \
  --parent-validation-report <parent-dir>/pathway-validation-report.json \
  --parent-assessment <parent-dir>/profile-concept-assessment.json \
  --parent-review <parent-dir>/pathway-plan-review.json \
  --output <new-dir>/pathway-revision-receipt.json
```

After the revised candidate passes unified validation, run
`validate_pathway_revision.py`. It rejects changes to any unmarked selection,
concept, goal, structure, bridge, or rationale field. A successful revision
receives new pathway and assessment IDs and another completely pending review;
human approval is never inherited.

Add `--bridge-catalog <released-bridge-catalog.json>` only if a P2 plan claims a
released bridge. Candidate or missing bridges are requirements, not learning
units, and force `plan_status=provisional`. Confirmatory validation additionally
requires the learning request, profile, and concept assessment to have their
required human-review states.

P0 normalization and P1 copying are deterministic scripts rather than separate
generative agents. `normalize_p0_pathway.py` translates the fixed canonical P0
specification into the unified schema using the hash-bound
`p0-normalization-map.json`. The map makes the old `LO-PI-*` to shared `LG-*`
metadata migration explicit without changing selection, grouping,
prerequisites, or order. `copy_p1_pathway.py` copies the controlled P0 fields
byte-for-byte and changes only the P1 identity, condition, profile binding,
baseline binding, and generation metadata. Both scripts require an explicit UTC
generation timestamp, refuse overwrite, validate before writing, and emit
hash-bound receipts.

Generate P0 with:

```bash
python3 experiments/rq2/scripts/normalize_p0_pathway.py \
  --workspace-root . \
  --canonical experiments/rq2/specs/power-iteration/canonical-pathway.json \
  --common-core experiments/rq2/specs/power-iteration/common-core.json \
  --reference-contract experiments/rq1/reference-contracts/power-iteration-v1/release/frozen_reference_contract.json \
  --learning-request experiments/rq2/learning-requests/power-iteration-second-year.json \
  --normalization-map experiments/rq2/specs/power-iteration/p0-normalization-map.json \
  --pathway-id power-iteration-p0-v1 \
  --generated-at <fixed-UTC-run-timestamp> \
  --output <p0-dir>/pathway-plan.json \
  --receipt <p0-dir>/p0-normalization-receipt.json
```

Generate one P1 per profile with:

```bash
python3 experiments/rq2/scripts/copy_p1_pathway.py \
  --workspace-root . \
  --p0 <p0-dir>/pathway-plan.json \
  --profile <profile.json> \
  --pathway-id <profile-specific-p1-id> \
  --generated-at <fixed-UTC-run-timestamp> \
  --output <p1-dir>/pathway-plan.json \
  --receipt <p1-dir>/p1-copy-receipt.json
```

The current pilot artifacts are under
`pathway-plans/power-iteration-v1/`: one validated P0 and exact validated P1
copies for applied mathematics, computer science, and mechanical engineering.
The normalization map and profiles still require their recorded human reviews
before confirmatory use.

The earlier fixed-pathway command is retained for protocol v0.2 reproduction:

```bash
python3 experiments/rq2/scripts/validate_fixed_pathway.py \
  --canonical experiments/rq2/specs/power-iteration/canonical-pathway.json \
  --actual <run-dir>/pathway.json \
  --common-core experiments/rq2/specs/power-iteration/common-core.json \
  --permissions experiments/rq2/specs/power-iteration/condition-permissions.json \
  --condition P1 \
  --output <run-dir>/pathway-validation.json
```

The following adaptive-pathway command also belongs to protocol v0.2 and is retained only
for historical pilot reproduction:

```bash
python3 experiments/rq2/scripts/validate_adaptive_pathway.py \
  --canonical experiments/rq2/specs/power-iteration/canonical-pathway.json \
  --actual <run-dir>/pathway.json \
  --common-core experiments/rq2/specs/power-iteration/common-core.json \
  --permissions experiments/rq2/specs/power-iteration/condition-permissions.json \
  --bridge-catalog <released-bridge-catalog.json> \
  --output <run-dir>/pathway-validation.json
```

Do not use either old validator for protocol v0.3 confirmatory runs because they
enforce the old universal-core design. `validate_pathway_plan.py` resolves the
Frozen Reference Contract, Frozen Curriculum Dependency Model, learner profile,
shared learning request, baseline, concept assessment, and optional released
bridge catalog from the plan's hash-bound references.
A valid P2 plan with no structural difference remains a valid negative result,
not evidence that pathway-level adaptation occurred.

## Simplified prerequisite Bridge Library

Bridge construction is supporting infrastructure, not a separate RQ2
experiment. The project therefore uses one deterministic structural/provenance
check, one compact human review, and one library-level release gate. It does not
create per-bridge release agents, revision receipts, or revision-scope
validators.

Select `Grounded Bridge Library Builder`, or follow
`.github/skills/build-grounded-bridge-library/SKILL.md`. Supply the Frozen
Curriculum Model and the latest approved P2 pathway/review pairs. The Builder
must derive the exact unresolved-demand union, merge shared concepts across
profiles, search official or institutional sources, and generate only:

- `bridge-library-candidate.json`;
- `bridge-library-validation-report.json`; and
- `bridge-library-review.json`.

For the current Power Iteration pilot the approved candidate is under
`bridge-library/power-iteration-v1/candidate-v3/`. It contains four demanded
bridges: vector norms/normalization, orthogonality/projection, inner
products/quadratic forms, and basic NumPy vector operations. Matrix-vector
products and characteristic polynomials remain Curriculum Model candidates but
are not generated because no approved current pathway requests them.

Validate a new candidate with:

```bash
python3 .github/skills/build-grounded-bridge-library/scripts/validate_bridge_library.py \
  --workspace-root . \
  --model curriculum-models/power-iteration-v1/release/frozen-contract-dependencies.json \
  --candidate <candidate-dir>/bridge-library-candidate.json \
  --pathway-review <pathway-plan.json> <approved-pathway-review.json> \
  --output <candidate-dir>/bridge-library-validation-report.json
```

Repeat `--pathway-review` for every included P2 pathway. Then generate the
review form:

```bash
python3 .github/skills/build-grounded-bridge-library/scripts/create_bridge_library_review.py \
  --workspace-root . \
  --candidate <candidate-dir>/bridge-library-candidate.json \
  --validation-report <candidate-dir>/bridge-library-validation-report.json \
  --output <candidate-dir>/bridge-library-review.json
```

Each bridge has only five human decisions: correctness, source quality, content
boundary, dependency support, and pedagogical sufficiency. A requested revision
uses the same Builder and the same validator in a new candidate directory; no
approval is inherited.

After the complete review is approved, select `Bridge Library Release Gate` or
run:

```bash
python3 .github/skills/release-bridge-library/scripts/release_bridge_library.py \
  --workspace-root . \
  --candidate bridge-library/power-iteration-v1/candidate-v3/bridge-library-candidate.json \
  --validation-report bridge-library/power-iteration-v1/candidate-v3/bridge-library-validation-report.json \
  --review bridge-library/power-iteration-v1/candidate-v3/bridge-library-review.json \
  --output-dir bridge-library/power-iteration-v1/release
```

The gate reruns bridge validation against the recorded Curriculum Model and P2
pathway/review pairs, verifies the exact review hashes and complete approval,
and publishes atomically. It changes only the root and per-bridge statuses from
`candidate` to `released` and adds hash-bound approval metadata. The resulting
`release/released-bridge-catalog.json` is the catalog accepted by
`validate_pathway_plan.py --bridge-catalog`.

Do not overwrite the approved provisional pathways after bridge release. Select
`Released Bridge Pathway Materializer` to create a new run. It applies the
fixed first-consuming-unit rule and writes a hash-bound receipt without
replanning selection, grouping, or the relative order of existing units:

```bash
python3 .github/skills/materialize-released-bridges/scripts/materialize_released_bridges.py \
  --workspace-root . \
  --parent-pathway <approved-run>/pathway-plan.json \
  --parent-review <approved-run>/pathway-plan-review.json \
  --bridge-catalog bridge-library/power-iteration-v1/release/released-bridge-catalog.json \
  --bridge-release-report bridge-library/power-iteration-v1/release/bridge-library-release-report.json \
  --pathway-id <new-bridge-resolved-pathway-id> \
  --generated-at <fixed-UTC-timestamp> \
  --output-dir <new-run-dir>
```

Then run ordinary pathway validation with the same `--bridge-catalog`. The
validation report records the exact catalog path and SHA-256. A valid resolved
plan is `complete` and contains one prerequisite-bridge unit for every released
requirement. Its `bridge-resolution-receipt.json` replaces another full pathway
review for this deterministic state transition.

Historical, already approved Planner outputs may use legacy bridge-requirement
aliases or omit canonical identifiers. For an exact parent/review pair already
bound by the released catalog, the materializer normalizes only the new child:
it generates ordered `BRQ-*` IDs, maps `reason` to `rationale`, or copies a
missing rationale from the same concept in the hash-bound concept assessment.
It removes only documented legacy aliases and records every action in the
receipt. New Planner outputs must use the canonical schema directly; ordinary
pathway validation rejects missing or legacy bridge-requirement fields.

## Pathway-Constrained Teaching Composer

After P0, exact P1 copies, and bridge-resolved P2 pathways are complete, select
`Pathway-Constrained Teaching Composer`. One Composer implementation renders all
three conditions so that condition permissions, not separate writing agents,
define the treatment:

- P0 receives no profile and writes a discipline-neutral lesson;
- P1 receives exactly one profile but cannot alter its fixed pathway;
- P2 receives exactly one profile and its final pathway plus only the released
  bridges actually used by that pathway.

For a new run, first create the condition-isolated view. The P2 form is:

```bash
python3 .github/skills/compose-pathway-constrained-teaching/scripts/prepare_composition_inputs.py \
  --workspace-root . \
  --pathway <final-p2-run>/pathway-plan.json \
  --pathway-validation-report <final-p2-run>/pathway-validation-report.json \
  --bridge-catalog bridge-library/power-iteration-v1/release/released-bridge-catalog.json \
  --word-count-protocol experiments/rq2/word-count-protocols/power-iteration-pilot.json \
  --run-id <unique-run-id> \
  --prepared-at <fixed-UTC-timestamp> \
  --output-dir <unused-lesson-run-dir>
```

For P0 and P1 omit `--bridge-catalog`. After preflight, the Composer reads only
`composition-input-view.json`, then writes `lesson.md` and `lesson-map.json`.
The hidden `<!-- section: SEC-NN -->` anchors and lesson map preserve a separate
audit trace without exposing RC or bridge IDs in student-facing prose.

Execute Python blocks and finalize the run:

```bash
python3 .github/skills/discipline-aware-teaching-adaptation/scripts/execute_code_blocks.py \
  --content <lesson-run-dir>/lesson.md \
  --output <lesson-run-dir>/code-validation.json

python3 .github/skills/compose-pathway-constrained-teaching/scripts/validate_composer_outputs.py \
  --workspace-root . \
  --run-dir <lesson-run-dir> \
  --provider <provider> \
  --model <model> \
  --access-route <access-route> \
  --prompt-version pathway-constrained-teaching-composer-v1 \
  --generated-at <same-fixed-UTC-timestamp>
```

The final validator checks current input hashes, condition-context isolation,
exact selected-item mapping, complete unit order, released bridge mapping,
Python execution, and the shared prose-word interval. It creates
`lesson-manifest.json` and `lesson-validation-report.json`. These checks do not
certify semantic mathematical correctness or pedagogical superiority; the
independent RQ2 evaluator owns those judgements.

The included Power Iteration word-count protocol is a pilot candidate using the
same 1,500--2,000 English-prose interval previously exercised by the RQ1 Power
Iteration runs. Review it after blinded pilot inspection and freeze it before
confirmatory generation without changing its range between conditions.
