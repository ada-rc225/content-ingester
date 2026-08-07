# Output contract

## Required run directory

```text
<run-dir>/
├── run_manifest.json
├── source_manifest.json
├── learner_profile.json
├── source_claims.json
├── adaptation_plan.json
├── adapted_content.md
├── claim_ledger.json
├── provenance.json
├── code_validation.json
├── validation_report.json
└── adaptation_summary.md
```

Create `resources/` only for required source-derived assets or data. Validate each JSON artifact against its same-named schema where present.

## Evidence roles

- `run_manifest.json`: records the experimental condition and generation configuration.
- `source_manifest.json`: freezes source identity with SHA-256 hashes.
- `learner_profile.json`: records the actual adaptation target and inferred assumptions.
- `source_claims.json`: enumerates authoritative claims, conditions, locators, and coverage decisions before generation.
- `adaptation_plan.json`: records pedagogical design before prose generation.
- `adapted_content.md`: contains one coherent lesson and machine-readable `<!-- claim-GEN-* -->` anchors.
- `claim_ledger.json`: classifies every generated claim and its evidence status.
- `provenance.json`: maps generated claims and anchors back to source claims.
- `code_validation.json`: records actual Python-block execution results.
- `validation_report.json`: records deterministic treatment-integrity checks; it never certifies content correctness.
- `adaptation_summary.md`: gives a human-readable internal review, not the formal RQ1 score.

## Cross-file invariants

Use unique IDs. Every `source_id` must exist in `source_manifest.json`; every `SRC-*` reference must exist in `source_claims.json`; every `GEN-*` reference must exist in `claim_ledger.json`; every generated claim must have exactly one provenance record and one content anchor. Cover every non-deferred and non-omitted source claim through provenance.

For reproducibility, do not rely on the chat prompt as the sole record of learner profile, source version, model identity, or treatment condition.
