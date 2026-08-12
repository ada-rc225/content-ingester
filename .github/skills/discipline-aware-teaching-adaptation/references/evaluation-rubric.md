# Internal adaptation review rubric

This rubric is formative quality control for the generating Agent. It is not the formal RQ1 outcome instrument and must not be used as blinded ground truth.

Score each dimension from 1 to 5 and cite section IDs, Contract item IDs, or validation evidence:

- source fidelity: definitions, equations, conditions, conclusions, and algorithm semantics remain source-consistent;
- source traceability: selected approved Contract items are covered by the plan and section provenance;
- learner-profile alignment: entry point, depth, implementation, and assessment match the recorded profile;
- disciplinary authenticity: representations and tasks reflect credible disciplinary reasoning rather than noun substitution;
- theory-to-implementation alignment: formulae, code operations, numerical behaviour, and checks are connected;
- pedagogical coherence: progression and prerequisite bridges are defensible, instructional content is completed before the final exercise chapter, and exercises assess already-taught material;
- learner readability: headings expose the conceptual structure, paragraphs have one main purpose, transitions are concise, and necessary caveats are not repeatedly restated;
- analogy safety: mappings have explicit limitations;
- exercise validity: tasks are solvable from stated data, objective-gradient-update quantities share one computation chain, visible derivation results agree with checked values, expected output agrees with executed stdout, and difficulty suits the learner;

Do not mark the artifact internally ready when `treatment_valid` is false, the Frozen Contract binding fails, the requested prose interval is missed, a required item is uncovered, a conditional item is unaccounted for, planned headings are missing, an exercise lacks its solution/RC mapping/configured check, a visible numeric/output claim disagrees with deterministic evidence, a substantial analogy has no boundary, or visible audit language and repeated caveats materially interrupt the lesson.

Do not turn this internal check into a post-generation approval stage. A high internal score cannot establish reduced drift or errors; compare C0, C1, and C2 later using the common RQ1 evaluator, common item definitions, blinded ordering, and repeated runs.
