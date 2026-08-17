# RQ2: pathway-level adaptation

## Research question and hypothesis

Can pathway-level adaptation produce materially different and pedagogically
appropriate learning sequences for students from different disciplinary
backgrounds while preserving the same mathematical core?

H2 predicts that pathway-level adaptation will improve disciplinary relevance,
prerequisite match, example authenticity, and pedagogical sequencing relative
to generic material or local wording adaptation. Mathematical-core consistency
must not materially decline. Learner-reported comprehensibility is outside the
current no-student-study scope and must not be inferred from expert or AI scores.

## Confirmatory comparison

Use the same frozen mathematical contract, learning objectives, assessment
targets, model family, generation budget, and output length in every condition.
Only the permitted adaptation mechanism changes.

| Condition | Learner information | Wording/examples | Contract selection and sequence |
|---|---|---|---|
| P0 generic | No discipline profile | Generic | One fixed comprehensive selection and sequence |
| P1 local adaptation | Full profile | Adapted inside fixed learning units | Exactly the P0 item selection and sequence |
| P2 pathway-level | Full profile | Adapted | May include/exclude selectable Contract items, reorder learning units, and add approved prerequisite bridges |

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

1. **Disciplinary relevance** (1-5): examples and motivations help this profile
   understand the mathematics.
2. **Prerequisite match** (1-5): introduced concepts match declared knowledge,
   with explicit bridges for missing prerequisites.
3. **Example authenticity** (1-5): examples are plausible within the discipline
   and avoid false claims or decorative relabelling.
4. **Sequence quality** (1-5): ordering respects dependencies and provides a
   justified progression for the profile.
For these four outcomes, report P2-P1 and P2-P0 contrasts with uncertainty
intervals. Treat individual pathway runs and learner ratings as nested within
topic/profile; do not treat rubric items or duplicate judge passes as independent
sample size.

## Mathematical-core preservation gate

Before pedagogy is interpreted, each output must pass deterministic provenance,
contract coverage, dependency, formula, and executable-code validation.

Confirmatory non-inferiority rule (freeze before data collection):

- universal-core coverage and selected-item coverage must both be 100%;
- no critical mathematical or algorithmic error is allowed;
- the P2 major/critical-error rate must be no more than 2 percentage points
  worse than P1; and
- formula and algorithm accuracy must each be no more than 5 percentage points
  worse than P1.

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
- location of first introduction for every core concept; and
- a written rationale linking every structural change to a profile attribute.

Declare a P2 profile pair materially different only when it has at least one
dependency-valid change in Contract selection, learning order, or prerequisite
bridging and the change is judged pedagogically justified. Lexical or example
changes alone do not satisfy this criterion.

## Learner study boundary

The current project does not run a student study. It may report expert-judged
prerequisite match, sequence quality, disciplinary relevance, authenticity, and
readability, but it must not rename readability as learner-reported
comprehensibility or claim measured learning gains.

## Execution stages

1. Review and freeze the learner profiles and canonical pathway.
2. Pilot P0/P1/P2 on power iteration, one run per cell.
3. Validate core preservation and verify that P2 creates genuine structural
   differences rather than cosmetic rewrites.
4. Revise the rubric only from blinded pilot observations, then freeze it.
5. Run three confirmatory generations per cell on both topics.
6. Conduct two blind expert/AI-assisted ratings, followed by adjudication of
   disagreements and all mathematical errors.

## Initial artifacts

- `protocol.json`: machine-readable frozen-design candidate.
- `profiles/*.json`: pilot learner profiles requiring educator review.
- `specs/power-iteration/common-core.json`: shared Contract items, learning
  outcomes, assessment targets, and selection boundary for the PI pilot.
- `specs/power-iteration/canonical-pathway.json`: the immutable P0/P1 content
  selection and learning sequence, and the reference point for measuring P2.
- `specs/power-iteration/condition-permissions.json`: the treatment-isolation
  matrix for P0, P1, and P2.
- `specs/power-iteration/notation-policy.json`: permitted semantic notation
  adaptation and prohibited problem changes.

Validate a P0 or P1 pathway manifest with:

```bash
python3 experiments/rq2/scripts/validate_fixed_pathway.py \
  --canonical experiments/rq2/specs/power-iteration/canonical-pathway.json \
  --actual <run-dir>/pathway.json \
  --common-core experiments/rq2/specs/power-iteration/common-core.json \
  --permissions experiments/rq2/specs/power-iteration/condition-permissions.json \
  --condition P1 \
  --output <run-dir>/pathway-validation.json
```

Validate a P2 pathway manifest with:

```bash
python3 experiments/rq2/scripts/validate_adaptive_pathway.py \
  --canonical experiments/rq2/specs/power-iteration/canonical-pathway.json \
  --actual <run-dir>/pathway.json \
  --common-core experiments/rq2/specs/power-iteration/common-core.json \
  --permissions experiments/rq2/specs/power-iteration/condition-permissions.json \
  --bridge-catalog <released-bridge-catalog.json> \
  --output <run-dir>/pathway-validation.json
```

The adaptive validator treats a selection- and sequence-unchanged P2 pathway as valid but
reports `materially_different=false`; such a run is a valid negative result,
not evidence that pathway-level adaptation occurred.
