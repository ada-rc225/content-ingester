# Grounding and adaptation rules

## Authority and claims

Use this hierarchy: supplied teaching material; user-specified learner requirements; explicitly identified supplementary sources; model-generated bridges. Never let a lower level silently override a higher level.

Grounding means that a generated claim has a recorded evidence relationship. It does not mean the supplied source is universally correct. Report these separately:

- `source_consistent`: meaning is supported by the supplied source;
- `mathematically_verified`: equivalence or correctness was checked by an independent mechanism or evaluator.

Never turn an LLM's self-assessment into `expert_verified`, `symbolically_equivalent`, or `execution_verified` evidence.

## Invariants

Preserve definitions, notation, equations, theorem assumptions and conclusions, update rules, convergence conditions, logical dependencies, and code semantics. Record notation normalisation explicitly.

## Support classes

- `directly_supported`: restates one or more source claims.
- `derived_from_source`: follows from cited source claims; state the derivation.
- `pedagogical_adaptation`: added explanation or scaffold.
- `domain_bridge`: added disciplinary mapping with an explicit boundary.
- `implementation_bridge`: added theory-to-code connection.
- `unsupported`: lacks sufficient source support.
- `contradicted`: conflicts with the supplied source.

Added content is allowed, but its status must remain visible. A citation to a related source claim does not automatically make a new domain fact supported.

## Adaptation

Adapt entry point, chapter order, vocabulary, examples, prerequisite refreshers, proof depth, implementation emphasis, visuals, and assessment. Change teaching logic where the learner profile requires it; do not merely replace nouns.

For every substantial analogy, identify the core concept, give the familiar representation, return to canonical mathematics, and state where the analogy stops being exact.

## Coverage and defects

Classify each meaningful source item as retained, reordered, summarised, deferred, or omitted. Give a scope- or profile-based reason for deferral and omission.

When a source appears malformed or incorrect, preserve the locator, mark the issue, avoid silent correction, label any proposed interpretation, and request review when it affects a core result.
