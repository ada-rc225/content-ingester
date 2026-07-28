# Updating Proposed Structure

Use this guide when creating or editing `outputs/proposed_structure.json`.

## Source of truth

- Structure and required fields are defined in `.github/instructions/proposed-structure.schema.json`.
- A concrete reference payload is available in `workflow-validation/what-is-numpy-scipy/expected-outputs/proposed_structure.json`.

## Required workflow after any update

1. Confirm `source_analysis` inventories all meaningful source sections and gives every candidate learning unit an explicit decision.

2. Confirm the proposed `pages` can be traced back to the candidate units and that no unit was silently discarded.

3. Confirm learner profiles, core concepts, and pathways are complete. Required pathway steps must include their proposed prerequisites earlier in the same pathway.

4. Validate JSON structure and cross-references:

```bash
python .github/skills/input-to-proposed-structure/validate_proposed_structure.py --proposed-file <output-dir>/proposed_structure.json
```

5. Regenerate the global dependency graph and per-profile pathway graphs from proposed structure:

```bash
python .github/skills/input-to-proposed-structure/generate_prerequisite_graph.py --source proposed_structure --inputs-dir <input-dir> --proposed-file <output-dir>/proposed_structure.json --output-dir <output-dir>
```

## Notes

- Resolve `<input-dir>` and `<output-dir>` from `.env` when present:
  - `CONTENT_INGESTER_INPUTS_DIR` (default: `inputs`)
  - `CONTENT_INGESTER_OUTPUTS_DIR` (default: `outputs`)
- Keep valid JSON only (double quotes, no trailing commas, no markdown fencing).
- Keep `pages[*].status` as either `new` or `missing`.
- Treat `source_analysis` as analysis of the supplied material, not as the final page list. Several source units may map to separate pages, or genuinely inseparable units may map to one page with a recorded rationale.
- "One learning objective per page" never means "one page per input file".
- When a topic may be taught to different disciplinary audiences, capture the relevant adaptation guidance in the proposed structure. Use the optional `discipline_mapping` field (when present) to note the discipline context, recommended content adaptation, suitable case examples, and the preferred teaching sequence.
