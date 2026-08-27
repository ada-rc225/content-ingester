# Structured exercise checkers

Use one checker whose inputs represent the mathematical operation actually asked for. A deterministic `hand_calculation` must have exactly one unified checker, its `expected_value` must equal the verification-level `expected_value`, and `python_expression` must be `null`. The visible `Result from the derivation` and `Checked answer` must be the same JSON value.

## Checker selection

| Exercise operation | Checker | Unified result |
|---|---|---|
| Evaluate a gradient | `objective_gradient` | Gradient vector |
| Evaluate a gradient and take one update | `objective_gradient_update` | Updated point |
| Take one power-iteration step and diagnose it | `power_iteration_step` | Structured iteration result |
| Check an ancillary scalar or vector expression | `expression_values` | None; not a primary hand-calculation chain |

If no checker represents the requested hand calculation, stop C2 generation and report the unsupported operation. Do not replace it with constants, a free `python_expression`, or an unrelated checker.

## Gradient checkers

`objective_gradient` records `objective_expression`, ordered `variables`, `point`, the expected gradient vector, and `absolute_tolerance`. `objective_gradient_update` additionally records a positive `step_size` and `expected_gradient`; its `expected_value` is the updated point. Expressions use the supported Python subset: arithmetic, `**`, `sin`, `cos`, `exp`, `log`, and `sqrt`.

## Power iteration

`power_iteration_step` records a finite numeric square `matrix`, a dimension-matched nonzero `initial_vector`, `normalize_initial`, one structured `expected_value`, and `absolute_tolerance`. If `normalize_initial` is true, the checker normalizes the supplied vector before multiplying; otherwise it uses the supplied vector directly. It then independently computes the product, normalized next vector, Rayleigh quotient, residual, and residual norm. A zero product is a breakdown and must fail validation.

The expected result has exactly this shape:

```json
{
  "initial_vector_used": [3.0, 1.0],
  "product": [12.0, 1.0],
  "next_vector": [0.9965457582448796, 0.08304547985373997],
  "rayleigh_quotient": 3.979310344827586,
  "residual": [0.02061818810161853, -0.24741825721941837],
  "residual_norm": 0.24827586206896554
}
```

This example uses `matrix=[[4,0],[0,1]]`, `initial_vector=[3,1]`, and `normalize_initial=false`. The visible derivation should show enough intermediate work for a reader to connect all fields to the same calculation chain.

## Ancillary expression checks

`expression_values` records one or more expressions, ordered variables, a point, and an expected scalar or vector. Every expression must reference at least one declared variable. It cannot consist only of the answer's numeric constants and cannot serve as the unified checker for a deterministic hand calculation.

## Adding another topic

Add a type-specific `oneOf` branch to `adaptation-plan.schema.json`, implement a handler in the `CHECKERS` registry, return `passed`, `derived_value`, `is_unified_chain`, and `details`, and add positive, wrong-answer, invalid-shape, breakdown, and visible-answer consistency tests. Keep common marker, solution, Contract-binding, and stdout validation outside topic-specific handlers.
