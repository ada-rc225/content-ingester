import argparse
import json
import sys
from pathlib import Path
from jsonschema import Draft202012Validator

# Schema lives at .github/instructions/ — two directories up from this skill folder.
DEFAULT_SCHEMA_FILE = (
    Path(__file__).resolve().parents[2] / "instructions" / "proposed-structure.schema.json"
)


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate proposed_structure.json against proposed-structure.schema.json.",
    )
    parser.add_argument(
        "--proposed-file",
        type=Path,
        required=True,
        help="Path to the proposed_structure JSON file to validate.",
    )
    return parser.parse_args()


def semantic_errors(instance: object) -> list[str]:
    """Validate traceability rules that JSON Schema cannot express clearly."""
    if not isinstance(instance, dict):
        return []

    errors: list[str] = []
    pages = instance.get("pages", [])
    page_slugs = {
        page.get("slug")
        for page in pages
        if isinstance(page, dict) and isinstance(page.get("slug"), str)
    }
    reviewed_paths = {
        item.get("path")
        for item in instance.get("inputs_reviewed", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    page_prerequisites = {
        page.get("slug"): page.get("prerequisites", [])
        for page in pages
        if isinstance(page, dict) and isinstance(page.get("slug"), str)
    }

    def collect_unique_ids(items: object, key: str, path: str) -> set[str]:
        identifiers: set[str] = set()
        if not isinstance(items, list):
            return identifiers
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            identifier = item.get(key)
            if not isinstance(identifier, str):
                continue
            if identifier in identifiers:
                errors.append(f"{path}/{index}/{key}: duplicate {key} {identifier!r}")
            identifiers.add(identifier)
        return identifiers

    profile_ids = collect_unique_ids(
        instance.get("generation_context", {}).get("profiles", []),
        "profile_id",
        "generation_context/profiles",
    )
    concept_items = instance.get("core_concept_model", {}).get("concepts", [])
    concept_ids = collect_unique_ids(
        concept_items,
        "concept_id",
        "core_concept_model/concepts",
    )
    pathway_ids = collect_unique_ids(
        instance.get("learning_pathways", []),
        "pathway_id",
        "learning_pathways",
    )
    collect_unique_ids(pages, "slug", "pages")

    seen_unit_ids: set[str] = set()
    for source_index, source in enumerate(instance.get("source_analysis", [])):
        if not isinstance(source, dict):
            continue

        source_path = source.get("source_path")
        if source_path not in reviewed_paths:
            errors.append(
                f"source_analysis/{source_index}/source_path: "
                "must also appear in inputs_reviewed"
            )

        for unit_index, unit in enumerate(source.get("candidate_units", [])):
            if not isinstance(unit, dict):
                continue

            prefix = (
                f"source_analysis/{source_index}/candidate_units/{unit_index}"
            )
            unit_id = unit.get("unit_id")
            if isinstance(unit_id, str):
                if unit_id in seen_unit_ids:
                    errors.append(f"{prefix}/unit_id: duplicate unit_id {unit_id!r}")
                seen_unit_ids.add(unit_id)

            decision = unit.get("decision")
            targets = unit.get("target_page_slugs", [])
            if decision in {"new_page", "merge_into_page"}:
                unknown_targets = [
                    target for target in targets if target not in page_slugs
                ]
                if unknown_targets:
                    errors.append(
                        f"{prefix}/target_page_slugs: proposed target(s) missing "
                        f"from pages: {', '.join(unknown_targets)}"
                    )

    for concept_index, concept in enumerate(concept_items):
        if not isinstance(concept, dict):
            continue
        prefix = f"core_concept_model/concepts/{concept_index}"
        unknown_units = [
            unit_id
            for unit_id in concept.get("source_unit_ids", [])
            if unit_id not in seen_unit_ids
        ]
        if unknown_units:
            errors.append(
                f"{prefix}/source_unit_ids: unknown source unit(s): "
                f"{', '.join(unknown_units)}"
            )

        concept_id = concept.get("concept_id")
        dependencies = concept.get("depends_on", [])
        if concept_id in dependencies:
            errors.append(f"{prefix}/depends_on: concept cannot depend on itself")
        unknown_dependencies = [
            dependency for dependency in dependencies if dependency not in concept_ids
        ]
        if unknown_dependencies:
            errors.append(
                f"{prefix}/depends_on: unknown concept(s): "
                f"{', '.join(unknown_dependencies)}"
            )

    concept_dependencies = {
        concept.get("concept_id"): concept.get("depends_on", [])
        for concept in concept_items
        if isinstance(concept, dict) and isinstance(concept.get("concept_id"), str)
    }
    concept_state: dict[str, int] = {}

    def visit_concept(concept_id: str) -> bool:
        state = concept_state.get(concept_id, 0)
        if state == 1:
            return True
        if state == 2:
            return False
        concept_state[concept_id] = 1
        for dependency in concept_dependencies.get(concept_id, []):
            if dependency in concept_dependencies and visit_concept(dependency):
                return True
        concept_state[concept_id] = 2
        return False

    if any(visit_concept(concept_id) for concept_id in concept_dependencies):
        errors.append("core_concept_model/concepts: concept dependency cycle detected")

    page_concepts: dict[str, list[str]] = {}
    for page_index, page in enumerate(pages):
        if not isinstance(page, dict):
            continue
        prefix = f"pages/{page_index}"
        slug = page.get("slug")
        source_unit_ids = page.get("source_unit_ids", [])
        core_concept_ids = page.get("core_concept_ids", [])
        if isinstance(slug, str):
            page_concepts[slug] = core_concept_ids

        unknown_units = [
            unit_id for unit_id in source_unit_ids if unit_id not in seen_unit_ids
        ]
        if unknown_units:
            errors.append(
                f"{prefix}/source_unit_ids: unknown source unit(s): "
                f"{', '.join(unknown_units)}"
            )
        unknown_page_concepts = [
            concept_id
            for concept_id in core_concept_ids
            if concept_id not in concept_ids
        ]
        if unknown_page_concepts:
            errors.append(
                f"{prefix}/core_concept_ids: unknown concept(s): "
                f"{', '.join(unknown_page_concepts)}"
            )
        if page.get("status") == "new" and not source_unit_ids:
            errors.append(
                f"{prefix}/source_unit_ids: new page must cite at least one source unit"
            )
        if page.get("status") == "new" and not core_concept_ids:
            errors.append(
                f"{prefix}/core_concept_ids: new page must teach or assess "
                "at least one core concept"
            )

    for pathway_index, pathway in enumerate(instance.get("learning_pathways", [])):
        if not isinstance(pathway, dict):
            continue
        prefix = f"learning_pathways/{pathway_index}"
        profile_id = pathway.get("profile_id")
        if profile_id not in profile_ids:
            errors.append(f"{prefix}/profile_id: unknown profile {profile_id!r}")

        entry_concept = pathway.get("entry_point", {}).get("core_concept_id")
        if entry_concept not in concept_ids:
            errors.append(
                f"{prefix}/entry_point/core_concept_id: "
                f"unknown concept {entry_concept!r}"
            )

        required_concepts = pathway.get("required_core_concepts", [])
        optional_concepts = pathway.get("optional_core_concepts", [])
        overlap = sorted(set(required_concepts) & set(optional_concepts))
        if overlap:
            errors.append(
                f"{prefix}: concepts cannot be both required and optional: "
                f"{', '.join(overlap)}"
            )
        unknown_concepts = sorted(
            {
                concept_id
                for concept_id in required_concepts + optional_concepts
                if concept_id not in concept_ids
            }
        )
        if unknown_concepts:
            errors.append(
                f"{prefix}: unknown core concept(s): {', '.join(unknown_concepts)}"
            )

        steps = pathway.get("ordered_steps", [])
        orders = [step.get("order") for step in steps if isinstance(step, dict)]
        if len(orders) != len(set(orders)):
            errors.append(f"{prefix}/ordered_steps: duplicate order values")
        if orders and sorted(orders) != list(range(1, len(orders) + 1)):
            errors.append(
                f"{prefix}/ordered_steps: order values must be contiguous from 1"
            )

        ordered_slugs = [
            step.get("page_slug") for step in steps if isinstance(step, dict)
        ]
        if len(ordered_slugs) != len(set(ordered_slugs)):
            errors.append(f"{prefix}/ordered_steps: duplicate page_slug values")
        unknown_pages = [
            slug for slug in ordered_slugs if slug not in page_slugs
        ]
        if unknown_pages:
            errors.append(
                f"{prefix}/ordered_steps: unknown page(s): "
                f"{', '.join(unknown_pages)}"
            )

        covered_concepts = {
            concept_id
            for slug in ordered_slugs
            for concept_id in page_concepts.get(slug, [])
        }
        uncovered_required = sorted(set(required_concepts) - covered_concepts)
        if uncovered_required:
            errors.append(
                f"{prefix}/required_core_concepts: required concept(s) not covered "
                f"by any pathway page: {', '.join(uncovered_required)}"
            )

        position = {slug: index for index, slug in enumerate(ordered_slugs)}
        step_requirements = {
            step.get("page_slug"): step.get("requirement")
            for step in steps
            if isinstance(step, dict)
        }
        for step_index, slug in enumerate(ordered_slugs):
            if slug not in page_prerequisites:
                continue
            for prerequisite in page_prerequisites[slug]:
                if prerequisite in page_slugs and prerequisite not in position:
                    errors.append(
                        f"{prefix}/ordered_steps/{step_index}: proposed prerequisite "
                        f"{prerequisite!r} is missing from this pathway"
                    )
                elif prerequisite in position and position[prerequisite] >= step_index:
                    errors.append(
                        f"{prefix}/ordered_steps/{step_index}: prerequisite "
                        f"{prerequisite!r} must appear before {slug!r}"
                    )
                elif (
                    step_requirements.get(slug) == "required"
                    and step_requirements.get(prerequisite) == "optional"
                ):
                    errors.append(
                        f"{prefix}/ordered_steps/{step_index}: required page {slug!r} "
                        f"cannot depend on optional page {prerequisite!r}"
                    )

    if not pathway_ids:
        errors.append("learning_pathways: at least one pathway is required")

    return errors


def main() -> int:
    args = parse_args()

    if not DEFAULT_SCHEMA_FILE.exists():
        print(f"Schema file not found: {DEFAULT_SCHEMA_FILE}", file=sys.stderr)
        return 2
    if not args.proposed_file.exists():
        print(f"Proposed structure file not found: {args.proposed_file}", file=sys.stderr)
        return 2

    try:
        schema = load_json(DEFAULT_SCHEMA_FILE)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Unable to load schema {DEFAULT_SCHEMA_FILE}: {exc}", file=sys.stderr)
        return 2

    try:
        instance = load_json(args.proposed_file)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in {args.proposed_file}: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"Unable to read {args.proposed_file}: {exc}", file=sys.stderr)
        return 2

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    traceability_errors = semantic_errors(instance) if not errors else []

    if not errors and not traceability_errors:
        print(f"✓ {args.proposed_file} is valid against {DEFAULT_SCHEMA_FILE.name}")
        return 0

    total_errors = len(errors) + len(traceability_errors)
    print(f"✗ {total_errors} validation error(s) in {args.proposed_file}:")
    for error in errors:
        print(f"  - {'/'.join(str(p) for p in error.absolute_path) or '<root>'}: {error.message}")
    for error in traceability_errors:
        print(f"  - {error}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
