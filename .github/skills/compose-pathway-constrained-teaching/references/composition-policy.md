# Pathway-constrained composition policy

## Authority order

Use only `composition-input-view.json` after preflight. Its selected Contract
items are the mathematical authority. Its released bridge entries are authority
only for their bounded prerequisite content. The pathway controls selection,
unit grouping, prerequisites, and order. The learner profile controls wording,
representations, and bounded examples only when the condition permits it.

## Shared output

Produce one continuous English student-facing lesson, not Atomic Learning pages
and not one page per pathway unit. Use ordinary sections and transitions. A
mapped section may combine consecutive pathway units, but the flattened unit
order in `lesson-map.json` must exactly equal `instruction_sequence`.

Write one hidden anchor immediately before every mapped H2 heading:

```markdown
<!-- section: SEC-01 -->
## Descriptive student-facing heading
```

Do not show RC IDs, unit IDs, bridge IDs, compliance language, provenance
ledgers, or evaluator instructions to students.

## P0

Write a discipline-neutral lesson. Do not infer or mention a target discipline,
profession, learner profile, or field-specific scenario. Follow the complete
fixed pathway exactly.

## P1

Use the one supplied profile for local explanations, terminology, bounded
examples, and representational emphasis. Preserve every pathway unit, Contract
item, prerequisite relation, and the complete fixed instruction sequence. Do
not turn local adaptation into selection or sequencing adaptation.

## P2

Use the one supplied profile while following the already selected and ordered
pathway. Teach each released prerequisite bridge before its consuming unit.
Do not restore excluded Contract content, create a new bridge, or alter the
pathway because another organization seems preferable.

## Mathematical and code boundaries

- Preserve conditions and prohibited-drift constraints adjacent to the claims
  they constrain.
- Use notation consistently; a semantic notation change may not change the
  mathematical object or problem.
- Keep analogies explicitly bounded when their mechanics differ from the
  mathematics.
- Use disciplinary examples only within the profile's authentic-context
  boundary and do not claim unsupported domain behavior.
- Make fenced Python blocks self-contained. Do not depend on files, network
  access, randomness without a fixed seed, or state from another block.

## Audit mapping

Each `lesson-map.json` section must identify one or more consecutive pathway
units. Its Contract item IDs and bridge Contract IDs must equal exactly the
ordered union contributed by those units. Every pathway unit must occur once.
The map is an authorship claim checked structurally here and checked
semantically by the later independent evaluator.

## Validation boundary

Composer validation establishes input integrity, treatment isolation at the
provided-context level, declared coverage, sequence preservation, released
bridge use, executable Python, and word-count compliance. It must not describe
the lesson as mathematically correct or pedagogically superior. Preserve failed
runs under the experiment's frozen regeneration policy rather than silently
substituting successful samples.
