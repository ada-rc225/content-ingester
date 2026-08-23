# RQ2 automated evaluation protocol v1

## 1. Measurement boundary

Evaluate whether dependency-aware, learner-profile-driven adaptation produces pedagogically appropriate and structurally different lessons while preserving the selected mathematical content. This is an artifact evaluation without students. Never relabel expert- or agent-judged readability as learner-reported comprehensibility or measured learning.

Use three evidence layers without combining them into one score:

1. four ordinal pedagogy outcomes for H2a;
2. deterministic structural pathway differences for H2b;
3. a conjunctive selected-content safety gate for H2c.

The exact RQ2 rubric is researcher-developed. Its construct rationale is informed by disciplinary discourse, expertise-reversal, analogy-boundary, learning-space, and instructional-sequence research; citations do not turn it into a pre-validated standardized scale. Freeze this protocol, its anchors, evaluator settings, and analysis rules before confirmatory judging.

## 2. Primary pedagogy outcomes

Score each dimension from 1 to 5. Use 2 and 4 only as genuine intermediate states. Every score needs exact lesson evidence and a profile-based rationale.

### Disciplinary framing appropriateness

- `1`: terminology, representation, motivation, or interpretation conflicts with the profile or is materially misleading.
- `3`: framing is broadly compatible but generic, superficial, or only intermittently useful.
- `5`: disciplinary terminology, representations, motivations, and perspectives consistently support understanding rather than merely relabeling a generic lesson.

Do not use application authenticity as a proxy for this score.

### Prerequisite match

- `1`: the lesson relies on knowledge declared missing or fragile and supplies no usable bridge before first use.
- `3`: the lesson broadly fits the profile but leaves a material assumption implicit or provides incomplete/late scaffolding.
- `5`: assumed knowledge matches the profile and every material gap is addressed explicitly before first use without unnecessary remedial load.

### Context-boundary awareness

- `1`: an analogy or disciplinary interpretation is promoted to a general domain fact or production method.
- `3`: the lesson signals idealization or limits, but an important assumption, non-mapping, or scope boundary remains unclear or late.
- `5`: each substantial contextual mapping states proportionate assumptions, limits, and non-mappings at first use, without repetitive warning prose.

### Sequence quality

- `1`: ordering violates a prerequisite or makes an explanation materially harder to follow.
- `3`: ordering is dependency-valid and adequate but largely generic or weakly justified for the profile.
- `5`: ordering and grouping are dependency-valid, coherent, and explicitly suited to the profile's knowledge and preferred representations.

The four scores remain separate. Never average them into a single confirmatory outcome.

### Code and implementation neutrality

The presence, quantity, or executability of code is not itself evidence of
pedagogical quality and must not increase any primary score. Judge whether the
selected scope fits the shared learning request and learner profile. A
profile-appropriate omission of optional code content must not lower a primary
score, while omitting a required learning capability remains a coverage
failure. Algorithm explanations without source code may therefore be fully
appropriate for one profile even when another profile receives an executable
implementation.

## 3. Exploratory outcome

Score `example_authenticity` from 1 to 5, or abstain when domain evidence is inadequate:

- `1`: a generic mathematical task with cosmetic disciplinary nouns;
- `3`: a plausible educational approximation with important simplifications;
- `5`: a credible disciplinary task or practice whose assumptions and simplifications are accurately represented.

Report this score descriptively. Do not use it to accept or reject H2a. A safe contextual frame is not proof of authentic professional practice.

## 4. Learning goals and selection quality

Judge every learning-request capability as `complete`, `partial`, `missing`, or `uncertain`. Required-goal coverage is the proportion of required capabilities judged complete.

Score inclusion appropriateness, exclusion appropriateness, and profile-rationale quality from 1 to 5. Use `not_applicable` for exclusion appropriateness when nothing was excluded. Record unnecessary content load as `none`, `low`, `moderate`, `high`, `severe`, or `uncertain`; lower load is better, but it is not part of the four primary outcomes.

Do not reward P2 for deleting a required capability. Do not penalise a condition merely for teaching more selected content; identify only content whose inclusion is pedagogically unjustified for the shared request and profile.

## 5. Selected-content semantic safety

Judge every selected Contract item exactly once.

Coverage:

- `full`: the canonical obligation and material conditions are represented;
- `partial`: the central idea is present but a non-critical part is missing;
- `omitted`: the selected obligation is absent;
- `contradicted`: the lesson gives an incompatible account;
- `uncertain`: available evidence cannot support a stable decision.

Semantic correctness:

- `correct`;
- `minor_error`: local imprecision unlikely to change the central calculation or implementation;
- `major_error`: likely to cause materially incorrect understanding, calculation, or implementation;
- `critical_error`: reverses or invalidates a central definition, theorem, convergence condition, or algorithm;
- `uncertain`.

Provenance:

- `supported`: the lesson statement is within the selected Contract or released bridge authority;
- `unmapped`: a mathematical/algorithmic assertion lacks that authority;
- `uncertain`.

Judge each unique formula reference selected by the pathway. `not_present` is excluded from formula-accuracy denominators but remains visible through item coverage. For a present formula, judge source mapping and mathematical accuracy. Judge every selected `algorithm_rule` or `code_semantics` item separately for algorithmic accuracy.

Create algorithm/code judgements only for selected `algorithm_rule` and
`code_semantics` items. When no such item is selected, keep the judgement list
empty and report algorithm accuracy as JSON `null` (interpreted as
`not_applicable`); do not manufacture a failure or reward the absence of code.

Atomise unsupported mathematical, algorithmic, and disciplinary-application claims. A clearly bounded analogy outside Contract scope may be `not_verifiable`; an unbounded mathematical or algorithmic extension is `unsupported`; an incompatible claim is `contradicted`.

## 6. H2c safety gate

The deterministic score report computes:

- required learning-goal coverage;
- selected-item full semantic coverage;
- present-formula provenance coverage;
- structural pathway validation;
- released-bridge mapping compliance;
- formula and algorithm accuracy over evaluable opportunities;
- critical mathematical/algorithmic error count;
- unsupported mathematical/algorithmic claim count.

The lesson passes only when every applicable proportion is `1.0`, all required semantic decisions are resolved, dependency coherence passes, and both prohibited error counts are zero. A zero opportunity denominator is reported as `not_applicable`, not manufactured as `1.0`.

Generation-side validators establish bindings, declared mappings, ordering, bridge mapping, code execution, and length. They do not establish semantic mathematical correctness or pedagogical quality.

## 7. Structural difference analysis

Controller-side comparison uses selected Contract-item sets, first-introduction item sequences, co-grouped item-pair sets, released bridge sets, and declared depth changes.

For item sets `A` and `B`:

`selection_distance = 1 - |A intersection B| / |A union B|`.

For first-introduction sequences `Q_a` and `Q_b`:

`order_distance = Levenshtein(Q_a, Q_b) / max(|Q_a|, |Q_b|)`.

A profile pair is materially different only when both pathways validate, at least one accepted structural feature changes, and the relevant profile-linked rationale has passed independent review. Review authority may be established either by an approved review directly hash-bound to the pathway or, for a deterministic released-bridge materialization, by a verified receipt that binds the final output to its approved parent review, released bridge catalog, release report, and exact hashes. This is inherited review authority over preserved planning decisions, not a claim that the reviewer directly reviewed the materialized file. Lexical or example change alone is insufficient.

## 8. Reliability and adjudication

Run at least two fresh blind passes per sample. Compute exact agreement and ordinal Krippendorff alpha for each primary dimension across samples. Judge passes are repeated measurements, not additional generated lessons.

Require human adjudication for:

- primary ratings differing by at least two points;
- every critical or major mathematical/algorithmic error;
- every unsupported mathematical/algorithmic claim;
- every safety-gate failure;
- contested disciplinary authenticity or application claims;
- a pre-specified random audit sample.

Preserve raw judgements. Use adjudication to resolve reported outcomes, not to overwrite reliability evidence or repair lessons.

## 9. Source basis

- AERA, APA, and NCME, *Standards for Educational and Psychological Testing* (2014), for validity, reliability, and intended score interpretation.
- Airey and Linder (2009), DOI `10.1002/tea.20265`, for disciplinary discourse and representations.
- Kalyuga et al. (2003), DOI `10.1207/S15326985EP3801_4`, for prior-knowledge-dependent instructional effectiveness.
- Gentner (1983), DOI `10.1207/s15516709cog0702_3`, and Duit (1991), DOI `10.1002/sce.3730750606`, for analogy mapping and boundary risks.
- Doignon and Falmagne (2015), arXiv `1511.06757`, and Merrill (2002), DOI `10.1007/BF02505024`, for prerequisite-aware learning structures and instructional progression.
- Herrington and Oliver (2000), DOI `10.1007/BF02319856`, for authentic learning environments.
- McCullagh (1980), DOI `10.1111/j.2517-6161.1980.tb01109.x`, for ordinal-response modelling.
- Krippendorff (2013), *Computing Krippendorff's Alpha-Reliability*, for ordinal inter-rater reliability.
