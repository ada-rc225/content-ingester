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

For a Markdown source, the pipeline produces four review artifacts:

1. `source_manifest.json`: authoritative file identity and SHA-256.
2. `grounding_inventory.json`: deterministic source units and exact formula blocks, classified as core material, derivation, or exercise.
3. `contract_plan.json`: compact semantic item proposals containing source-unit and formula IDs.
4. `reference_contract.json`: materialized evidence and source-exact LaTeX for human review.

Build and validate them with:

```bash
python3 .github/scripts/build_grounding_inventory.py --workspace-root . --source <source.md> --source-id <source-id> --output <contract-dir>/grounding_inventory.json
python3 .github/scripts/materialize_reference_contract.py --workspace-root . --plan <contract-dir>/contract_plan.json --inventory <contract-dir>/grounding_inventory.json --source-manifest <contract-dir>/source_manifest.json --output <contract-dir>/reference_contract.json
python3 .github/scripts/validate_reference_contract.py --workspace-root . --contract <contract-dir>/reference_contract.json --source-manifest <contract-dir>/source_manifest.json --grounding-inventory <contract-dir>/grounding_inventory.json --report <contract-dir>/contract_validation_report.json
```

The deterministic validator requires every core formula to map to a contract item, preserves derivation formulas as reference-only, excludes exercise formulas from the denominator, and requires complete inventory source units rather than short evidence fragments. A passing report establishes provenance and coverage, not mathematical approval: an expert must still review the candidate before changing its lifecycle to `frozen`.

## Minimal Checklist

1. Approve proposed_structure.json and dependency_graph.md.
2. Approve generated page files and metadata quality.
3. Approve final consistency pass and recommendations.
4. Approve publish results and final upload summary.
