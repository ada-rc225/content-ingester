# Compact v2.1 output contract

```text
<run-dir>/
├── run_manifest.json
├── source_manifest.json
├── learner_profile.json
├── core_invariants.json
├── adaptation_plan.json
├── adapted_content.md
├── provenance.json
├── code_validation.json
├── validation_report.json
└── adaptation_summary.md
```

`source_manifest.json` freezes source identity but stays outside the narrative prompt. `core_invariants.json` contains 6–10 concise high-risk mathematical items, with an absolute maximum of 12. `adaptation_plan.json` defines readable sections. `adapted_content.md` must place `<!-- section: SEC-NN -->` directly before each matching H2 heading. `provenance.json` contains one short record per section and must not repeat lesson prose.

The removed v2.0 artifacts `source_claims.json` and `claim_ledger.json` are not required in new runs. Keep them only inside historical v2.0 run directories.

Every source ID must exist in the manifest. Every invariant ID must exist in `core_invariants.json`, appear in the plan, and be covered by section provenance. Plan, content, and provenance must contain the same section IDs in the same order.
