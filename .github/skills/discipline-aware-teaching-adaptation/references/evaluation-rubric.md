# Internal adaptation review rubric

This rubric is formative quality control for the generating Agent. It is not the formal RQ1 outcome instrument and must not be used as blinded ground truth.

Score each dimension from 1 to 5 and cite section IDs, invariant IDs, or validation evidence:

- source fidelity: definitions, equations, conditions, conclusions, and algorithm semantics remain source-consistent;
- source traceability: high-risk mathematical content is covered by compact invariants and section provenance;
- learner-profile alignment: entry point, depth, implementation, and assessment match the recorded profile;
- disciplinary authenticity: representations and tasks reflect credible disciplinary reasoning rather than noun substitution;
- theory-to-implementation alignment: formulae, code operations, numerical behaviour, and checks are connected;
- pedagogical coherence: progression and prerequisite bridges are defensible;
- analogy safety: mappings have explicit limitations.

Do not mark the artifact internally ready when `treatment_valid` is false, a core source issue is unresolved, planned headings are missing, or a substantial analogy has no boundary.

Record source consistency and independent correctness separately. A high internal score cannot establish reduced drift or errors; compare C0, C1, and C2 using an independent evaluator, common item definitions, blinded ordering, and repeated runs.
