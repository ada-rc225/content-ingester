# Discipline-aware Teaching Path Guidance

When a learner's disciplinary background is known, the content should not be generated as a single generic explanation. Instead, the teaching page should be adapted so that the same conceptual topic is taught through a discipline-relevant lens.

## Core principle

A concept such as gradient descent, optimisation, modelling, or statistical inference is not taught in the same way across all disciplines. A credible teaching pathway should be informed by the typical progression used in that field, such as established course syllabi, standard textbooks, or foundational literature.

## Evidence-based generation requirement

When the user specifies a discipline context, create a discipline-specific teaching pathway that is grounded in a plausible domain-specific progression. The generator should:

1. Identify the discipline context.
2. Select a plausible teaching sequence that matches typical curriculum structure in that discipline.
3. Choose examples and terminology that are conventional in that field.
4. Adjust prerequisites to reflect the expected mathematical or conceptual background.
5. Explain the pedagogical rationale in a compact form.

This should not be a purely stylistic adaptation. The pathway should reflect a defensible teaching logic.

## Recommended discipline profiles

### Computer science
Typical progression:
- define convex and non-convex functions
- introduce loss in a multi-variable setting
- represent prediction error as MSE in vector or matrix form
- connect error to the Jacobian and first-order partial derivatives
- derive gradient descent as an iterative update rule
- discuss numerical issues such as step size, truncation error, and convergence criteria

### Engineering
Typical progression:
- represent a scalar field or potential-energy surface
- connect the problem to equilibrium and conservative force fields
- introduce a discrete relaxation or iterative update scheme
- discuss numerical stability, step-size limits, and convergence behaviour
- compare gradient descent with Newton-type approaches when appropriate

### Economics
Typical progression:
- represent a multi-asset or multi-constraint optimisation problem using a quadratic form or utility function
- analyse concavity or convexity
- express marginal conditions using first-order conditions and differentials
- introduce constrained optimisation using Lagrange multipliers
- interpret second-order conditions using Hessian definiteness

### Physics
Typical progression:
- frame the problem as an energy landscape or potential field
- identify stationary points and force directions
- use iterative relaxation toward equilibrium
- discuss stability and convergence under numerical discretisation

### Biology
Typical progression:
- frame the problem as parameter estimation or model fitting
- connect the objective function to biological data and uncertainty
- interpret optimisation as finding values that best explain observations
- discuss overfitting, regularisation, and interpretability

## Required output structure

For each teaching pathway, the generator should produce:

- discipline_context: the audience or subject area being taught to
- pedagogical_basis: a short rationale explaining why this sequence is appropriate for the discipline
- canonical_sequence: the core conceptual sequence that reflects a credible teaching order
- case_examples: one or more examples grounded in that discipline
- recommended_teaching_sequence: the order in which concepts should be introduced
- prerequisite_adjustments: any changes to the assumed prior knowledge or prerequisite set
- evidence_sources: a short note indicating the kind of curricular or scholarly basis used, such as a common syllabus, textbook progression, or established domain practice

## Generation rules

- The teaching sequence should be plausible for the selected discipline.
- Prefer domain-relevant examples and vocabulary.
- Do not use the same prerequisite ordering for all disciplines.
- When the user provides multiple disciplines, generate a separate pathway for each one.
- If the content is intended for pedagogy rather than a general summary, include a concise explanation of why the sequence is appropriate.
