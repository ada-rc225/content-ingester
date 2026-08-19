# Content Ingester

This repository supports the Atomic Learning content-ingestion workflow:

1. Start from source teaching material in inputs.
2. Propose atomic pages and their prerequisite structure.
3. Build page folders with metadata and HTML content.
4. Validate structure and consistency.
5. Publish pages as one GitHub repository per page.

The process is designed so a human editor can run it end-to-end with clear checkpoints.

## Set up environment

It is recommended to open this repository in Visual Studio Code [locally](#local-setup) on your machine with GitHub Copilot agent or [remotely](#github-codespaces-setup) in GitHub Codespaces.

### GitHub Codespaces setup

This repository includes a dev container configuration in `.devcontainer/` for Codespaces.

1. Open the repository on GitHub.
2. Select **Code** -> **Codespaces** -> **Create codespace on main** (or your working branch).
3. Wait for container build and `postCreateCommand` to finish.

### Local setup

Python 3.10 or higher is required. Create and activate a virtual environment, then install dependencies. The agent will attempt
to perform the local setup automatically if a venv is not detected.

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS (bash):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### GitHub API access

A GitHub Personal Access Token (PAT) with repo permissions is required to publish content.
Add your token to a `.env` file `GITHUB_PAT=your_github_pat_here`.

## Workflow

The agent instructions provided in this repository contain the full process of content ingestion and should be able to produce sensible output from input content without human intervention. Nevertheless, it is recommended to guide the agent using the checkpoints below to ensure high-quality output.

### Before you start

The ingestion agent resolves these directories at run start:

- Input directory: `CONTENT_INGESTER_INPUTS_DIR` (default `inputs/`)
- Output directory: `CONTENT_INGESTER_OUTPUTS_DIR` (default `outputs/`)

Place files in:

- `CONTENT_INGESTER_INPUTS_DIR` (for example `inputs/`):
  - `live-website-export/` subfolder:
    - current_content.md (or similarly named existing content export)
      - Should list existing page slugs with brief descriptions and prerequisite/related links where available.
      - Used by the agent to avoid duplicating already-published content and to validate prerequisite references.
    - tags_current.md (or similar tags export)
      - Should list the current platform tag names (one per line or simple grouped lists).
      - Used by the agent to reuse existing tags and only propose new tags when necessary.
  - `content-to-ingest/` subfolder:
    - new source material in .md, .ipynb, .pdf, or .pptx format

PDF files are supported. For PDFs, the agent should use `tools/extract_pdf_assets.py` (documented in `.github/instructions/pdf-data-extraction.md`) before proposing structure or generating page content. By default, the extractor reads PDFs from `<input-dir>/content-to-ingest/` and writes artifacts to `<output-dir>/pdf-processing/`, creating suffixed output folders unless overwrite is explicitly requested.

PPTX files are supported. For PPTX files, the agent should use `tools/extract_pptx_assets.py` (documented in `.github/instructions/pptx-data-extraction.md`) before proposing structure or generating page content. The agent should do this without prompting from you. By default, the extractor reads PPTX files from `<input-dir>/content-to-ingest/` and writes artifacts to `<output-dir>/pptx-processing/`, creating suffixed output folders unless overwrite is explicitly requested.

Outputs will be created in the configured output directory (default `outputs/`). Template assets may be downloaded to `templates/`.

### Checkpoint 1: Structure proposal

Prompt the agent to create the proposed structure from the input files, for example:

`Create <output-dir>/proposed_structure.json from <input-dir>/, then generate <output-dir>/dependency_graph.md and summarise key risks.`

Review before approval:

1. `<output-dir>/proposed_structure.json` has required keys and complete page entries.
2. Page slugs and prerequisites make sense for your curriculum.
3. status is used correctly (new vs missing prerequisites).
4. `<output-dir>/dependency_graph.md` has no obvious circular dependencies.
5. Proposed tags align with current tags, with any new tags clearly justified.

### Checkpoint 2: Page generation

Prompt the agent to generate the next page folder and content, for example:

`Using approved <output-dir>/proposed_structure.json, generate the next page at <output-dir>/<slug>/ with all required files.`

Repeat this for each page. The agent will determine the next page based on which pages in proposed_structure.json do not yet have a folder in the configured output directory. You can delete a page folder and revisit it, or ask the agent to skip a page and return to it later.

1. Each page folder contains all required files.
2. metadata.json slug matches folder name.
3. content.html follows house rules (no h1, UK English, clean HTML).
4. Prerequisites and related content are plausible and consistent.
5. Spot-check 3 to 5 pages for quality and scope (single learning objective).

### Checkpoint 3: Consistency and recommendations

Prompt the agent to run a consistency pass and generate recommendations, for example:

`Run a full consistency pass on <output-dir>/, fix metadata/linking issues, regenerate dependency_graph.md, and create related_content_recommendations.md.`

Review before approval:

1. Final graph still has no circular dependencies.
2. No broken or unknown prerequisite slugs remain.
3. `related_content_recommendations.md` is specific and actionable.

### Checkpoint 4: Publish

Prompt the agent to run the publish workflow for one page at a time, for example:

`Run Stage 5 (upload-and-check) for <output-dir>/<slug>/.`

Review before approving each page:

1. The correct repository was created on GitHub.
2. `<output-dir>/upload_summary.txt` has been updated to reflect all uploads so far.
3. The page appears correctly on the live site.
4. Prerequisites and related content resolve to valid pages on the site.

Once all pages have been published, prompt the agent to generate the final upload summary:

`Write <output-dir>/upload_summary.txt with created, skipped, and failed repositories.`

### Validation workflow prompt

Use the Workflow Validation Assistant for regression checks.

Prompt:

`Run validate-workflow for all cases in workflow-validation/.`

## Grounded teaching-contract workflow

The Grounding Contract Builder creates a candidate mathematical source of truth before discipline-aware adaptation. Exercises are excluded by default because they may be regenerated for each learner profile; definitions, assumptions, theorem statements, convergence bounds, and algorithm updates remain in scope.

For a Markdown source, the pipeline produces five review artifacts:

1. `source_manifest.json`: authoritative file identity and SHA-256.
2. `grounding_inventory.json`: deterministic source units and exact formula blocks, classified as core material, derivation, or exercise.
3. `contract_plan.json`: compact semantic item proposals containing source-unit and formula IDs.
4. `reference_contract.json`: materialized evidence and source-exact LaTeX for human review.
5. `human_review.json`: a separately persisted review record bound to the immutable generation content.

Build and validate them with:

```bash
python3 .github/scripts/build_grounding_inventory.py --workspace-root . --source <source.md> --source-id <source-id> --output <contract-dir>/grounding_inventory.json
python3 .github/scripts/materialize_reference_contract.py --workspace-root . --plan <contract-dir>/contract_plan.json --inventory <contract-dir>/grounding_inventory.json --source-manifest <contract-dir>/source_manifest.json --output <contract-dir>/reference_contract.json
python3 .github/scripts/validate_reference_contract.py --workspace-root . --contract <contract-dir>/reference_contract.json --source-manifest <contract-dir>/source_manifest.json --grounding-inventory <contract-dir>/grounding_inventory.json --report <contract-dir>/contract_validation_report.json
```

Capture completed or in-progress item reviews without rerunning the materializer:

```bash
python3 .github/scripts/manage_human_review.py capture --contract <contract-dir>/reference_contract.json --output <contract-dir>/human_review.json
```

To restore the review onto matching generation content, always write a separate output file:

```bash
python3 .github/scripts/manage_human_review.py apply --contract <contract-dir>/reference_contract.json --review <contract-dir>/human_review.json --output <contract-dir>/reviewed_reference_contract.json
```

The review record is bound through a SHA-256 computed after removing mutable review decisions. It can therefore survive regeneration of review fields, but it refuses to apply if a mathematical statement, formula, evidence unit, source fingerprint, or other generation content has changed.

After an authorised reviewer changes `human_review.review_status` to `approved` and completes `reviewer` and `final_approval`, select the `Grounding Release Gate` agent or run its deterministic command directly:

```bash
python3 .github/scripts/release_grounding_contract.py \
  --workspace-root . \
  --contract <contract-dir>/reference_contract.json \
  --review <contract-dir>/human_review.json \
  --source-manifest <contract-dir>/source_manifest.json \
  --grounding-inventory <contract-dir>/grounding_inventory.json \
  --output-dir <new-release-dir>
```

The release gate never runs the materializer and never edits approval data. It refuses incomplete or mismatched reviews and refuses to overwrite an existing release. A successful run atomically produces `frozen_reference_contract.json`, `frozen_contract_validation_report.json`, `frozen_contract.sha256`, and `release_gate_report.json`.

### Run the C2 Frozen Contract adapter

Give the `Discipline-aware Teaching Adapter` the `frozen_reference_contract.json` inside the successful release directory, not an earlier candidate or a similarly named pre-release artifact. The adapter first runs:

```bash
python3 .github/skills/discipline-aware-teaching-adaptation/scripts/prepare_frozen_grounding.py \
  --workspace-root . \
  --contract <release-dir>/frozen_reference_contract.json \
  --output <run-dir>/grounding_receipt.json
```

This preflight refuses an incomplete release and creates a fingerprinted `grounding_receipt.json` plus a compact `grounding_view.json`. C2 version 3.6 generates only from that approved view, covers every required Contract item, records a decision for every conditional item, enforces the structured `word_count_protocol`, and keeps Contract IDs out of student-facing prose.

When exercises are enabled, record their common experimental protocol in `run_manifest.json`. Each exercise is generated for the learner rather than copied into the Frozen Contract, but its mathematical meaning and worked solution must map to selected Contract items. Numeric exercises use hidden `derived-answer` and `answer` markers with visible JSON results; code exercises use `expected-stdout` markers with visible JSON strings. Then run:

```bash
python3 .github/skills/discipline-aware-teaching-adaptation/scripts/execute_code_blocks.py \
  --content <run-dir>/adapted_content.md \
  --output <run-dir>/code_validation.json
python3 .github/skills/discipline-aware-teaching-adaptation/scripts/validate_exercises.py \
  --content <run-dir>/adapted_content.md \
  --plan <run-dir>/adaptation_plan.json \
  --code-validation <run-dir>/code_validation.json \
  --output <run-dir>/exercise_validation.json
python3 .github/skills/discipline-aware-teaching-adaptation/scripts/validate_adapter_outputs.py \
  --workspace-root . \
  --run-dir <run-dir>
```

The exercise validator checks that all exercises occur in the final planned chapter, then checks reading-order IDs, worked-solution presence, RC bindings, topic-matched unified calculations, agreement among computed, visibly derived, and Checked answers, and agreement between visible expected output and executed stdout. Gradient and power-iteration hand calculations have separate structured checkers; unsupported hand-calculation topics stop instead of falling back to self-confirming constants. Conceptual, derivational, and transfer exercises use `contract_binding`, which validates their structure, solution presence, and selected RC-item binding without creating a post-generation human-review task or claiming semantic proof. Historical C2 runs before v3.5 remain pilot artifacts; keep v3.5 artifacts as historical evidence rather than revalidating them as v3.6 runs.

The deterministic validator requires every core formula to map to a contract item, preserves derivation formulas as reference-only, excludes exercise formulas from the denominator, and requires complete inventory source units rather than short evidence fragments. A passing report establishes provenance and coverage, not mathematical approval: an expert must still review the candidate before changing its lifecycle to `frozen`.

### Build a curriculum dependency candidate

After the Grounding Release Gate produces a released
`frozen_reference_contract.json`, use the `Grounded Curriculum Dependency
Builder` agent to propose topic-level RC-item dependencies before learner-pathway
planning. The builder verifies the release, classifies hard, explanatory,
implementation, co-requisite, neighbour, fallback, and external-prerequisite
relationships, and then runs:

```bash
python3 .github/skills/build-curriculum-dependencies/scripts/validate_dependency_model.py \
  --workspace-root . \
  --contract <release-dir>/frozen_reference_contract.json \
  --candidate <curriculum-model-candidate-dir>/contract-dependencies.json \
  --output <curriculum-model-candidate-dir>/dependency-validation-report.json
```

The resulting model is a candidate only. Deterministic validation checks the
Frozen Contract binding, complete RC-item coverage, relationship integrity,
acyclic directed dependencies, fallback rules, and prerequisite-candidate
bindings. It does not approve pedagogical dependency judgements or release
prerequisite bridges. After validation passes, the same agent also generates
`curriculum-dependency-review.json`. That file is hash-bound to the candidate
and validation report and starts with every decision `pending`; it is a review
form, not evidence of approval.

When a completed review has `revision_required`, invoke the same Builder in
`revision` mode with the released Contract, parent candidate, parent review, and
a new output directory. It verifies the review binding, creates
`dependency-revision-receipt.json`, permits changes only to fields explicitly
marked `revision_required`, requires the next model version, runs both base and
revision-scope validators, and creates a fresh all-pending review. Parent
artifacts are never overwritten and prior approvals are never inherited. A
Curriculum Model Release Gate must reject pending or revision-required reviews;
it validates and freezes but never rebuilds candidates.

### Release an approved curriculum dependency model

After the dependency review is independently completed and every populated field
is explicitly approved, select the `Curriculum Model Release Gate` agent or run:

```bash
python3 .github/skills/release-curriculum-model/scripts/release_curriculum_model.py \
  --workspace-root . \
  --contract <release-dir>/frozen_reference_contract.json \
  --candidate <candidate-dir>/contract-dependencies.json \
  --validation-report <candidate-dir>/dependency-validation-report.json \
  --review <candidate-dir>/curriculum-dependency-review.json \
  --output-dir <new-curriculum-release-dir>
```

The gate reruns the base validator and, for a revised candidate, the revision-
scope validator. It rejects stale hashes, missing records, incomplete decisions,
and existing output directories. Success atomically creates
`frozen-contract-dependencies.json`, `frozen-curriculum-review.json`,
`frozen-curriculum-validation-report.json`,
`frozen-curriculum-model.sha256`, and `curriculum-release-report.json`.
Dependency content is preserved; external prerequisite bridges remain candidates
and require a separate review and release process before pathway generation may
insert their teaching content.

### Release an approved bridge library

After `Grounded Bridge Library Builder` produces a valid candidate and its
complete review is approved, select `Bridge Library Release Gate` or run:

```bash
python3 .github/skills/release-bridge-library/scripts/release_bridge_library.py \
  --workspace-root . \
  --candidate <candidate-dir>/bridge-library-candidate.json \
  --validation-report <candidate-dir>/bridge-library-validation-report.json \
  --review <candidate-dir>/bridge-library-review.json \
  --output-dir <new-bridge-release-dir>
```

The simplified library-level gate reruns bridge validation against the recorded
Curriculum Model and approved P2 pathways, verifies all review decisions and
SHA-256 bindings, and atomically publishes `released-bridge-catalog.json` plus
its frozen review, release validation, checksum, and release report. It changes
only release-state metadata. Supply the released catalog to downstream pathway
validation with `--bridge-catalog`.

Use `Released Bridge Pathway Materializer` after release to create a new
bridge-resolved P2 run. The deterministic materializer binds the approved parent
pathway/review and released catalog/report, inserts each bridge immediately
before its first consuming Contract unit, and writes
`bridge-resolution-receipt.json`. It never edits the approved parent run or
re-enters adaptive Planner revision mode.

### Compose a frozen RQ2 pathway into a lesson

Select `Pathway-Constrained Teaching Composer` after the final P0, P1, or P2
pathway validates. Its shared workflow prepares a hash-bound, condition-isolated
input view, renders one continuous lesson, executes Python blocks, and validates
the lesson map, pathway order, selected-item scope, released bridges, and shared
word-count protocol. See `experiments/rq2/README.md` for the P0/P1/P2 commands.

## Minimal Checklist

1. Approve proposed_structure.json and dependency_graph.md.
2. Approve generated page files and metadata quality.
3. Approve final consistency pass and recommendations.
4. Approve publish results and final upload summary.
