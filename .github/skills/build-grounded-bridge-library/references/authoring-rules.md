# Bridge authoring rules

1. Treat the Frozen Curriculum Model as authority for bridge identity,
   `supports_item_ids`, and `content_boundary`.
2. Treat only hash-bound P2 pathways with completed `approved` reviews as demand
   evidence. Collect requirements whose `resolution_status` is `candidate`.
3. Prefer official software documentation for implementation bridges and
   university course materials for mathematical bridges. Record stable HTTPS
   URLs, access dates, and useful evidence locators.
4. Write prerequisite-sized content: definitions, one operational procedure,
   and at most one small worked example when needed. Do not teach the Power
   Iteration, its convergence theorem, Rayleigh estimation, or stopping rule in
   a bridge.
5. Use one shared bridge for the same concept across profiles. Profile-specific
   explanation and placement belong to the later pathway-constrained composer.
6. Ensure every content block has a non-empty `source_ids` list and that every
   source declares the content blocks it supports.
7. Keep candidate lifecycle values as `candidate`. Human review and later
   release are separate operations.
