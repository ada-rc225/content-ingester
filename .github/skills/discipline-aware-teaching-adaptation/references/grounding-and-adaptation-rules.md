# Grounding and adaptation rules

## Authority hierarchy

1. Supplied institutional teaching material
2. User-provided learner profile and teaching requirements
3. Explicitly identified supplementary material
4. Model-generated pedagogical bridges

Never use a lower level to silently override a higher level.

## Mathematical invariants

Preserve:

- definitions and notation;
- formulae;
- theorem assumptions and conclusions;
- algorithm update rules;
- convergence conditions;
- logical dependencies;
- mathematical meaning of code.

If notation is normalised, record the old and new notation in provenance.

## Adaptable dimensions

Adapt:

- entry point;
- chapter order;
- vocabulary;
- examples and applications;
- prerequisite refreshers;
- derivation and proof depth;
- code language and implementation emphasis;
- visual explanations;
- exercises and assessment context.

An adaptation must change teaching logic where the profile requires it, not merely replace nouns.

## Domain bridges

Use a domain bridge only when the mapping is mathematically defensible.

For every substantial analogy:

1. identify the core mathematical concept;
2. explain the familiar domain representation;
3. state the canonical mathematical form;
4. state where the analogy stops being exact.

## Coverage decisions

Classify every meaningful source section as:

- retained;
- reordered;
- summarised;
- deferred;
- omitted.

Do not silently omit source content. Deferral and omission require profile-based or scope-based reasons.

## Source defects

When the source appears malformed or incorrect:

- quote only the minimal locator and description needed to identify the issue;
- mark it as `source_issue`;
- do not silently correct the authoritative record;
- provide a clearly labelled proposed interpretation only when needed to continue;
- request review if the defect affects a core result.

## Added content

Added examples, explanations, code, and exercises must be labelled as adaptations in provenance. Do not attribute them to the institutional source.
