#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean, median
from typing import Any

from rq2_eval_common import PRIMARY_DIMENSIONS, PROTOCOL_ID, EvaluationError, load_json, write_json

RUN_RE = re.compile(r"run[-_ ]?(\d+)", re.IGNORECASE)


def run_index(run_id: Any) -> int:
    match = RUN_RE.search(str(run_id))
    if not match:
        raise EvaluationError(f"cannot extract run index from {run_id!r}")
    return int(match.group(1))


def rounded(value: float) -> float:
    return round(value, 6)


def main() -> int:
    parser = argparse.ArgumentParser(description="Unblind and aggregate completed RQ2 score reports.")
    parser.add_argument("--score-report", action="append", required=True)
    parser.add_argument("--mapping", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    try:
        if output.exists():
            raise EvaluationError(f"refusing to overwrite aggregate report: {output}")
        mappings: dict[str, dict[str, Any]] = {}
        for raw_path in args.mapping:
            mapping = load_json(Path(raw_path).resolve())
            if mapping.get("protocol_id") != PROTOCOL_ID:
                raise EvaluationError(f"unexpected mapping protocol: {raw_path}")
            sample_id = mapping.get("sample_id")
            if sample_id in mappings:
                raise EvaluationError(f"duplicate mapping for {sample_id}")
            if mapping.get("condition") not in {"P0", "P1", "P2"}:
                raise EvaluationError(f"invalid condition mapping for {sample_id}")
            mappings[sample_id] = mapping

        reports_by_sample: dict[str, list[dict[str, Any]]] = defaultdict(list)
        report_identities: set[tuple[str, str, int]] = set()
        for raw_path in args.score_report:
            report = load_json(Path(raw_path).resolve())
            if report.get("protocol_id") != PROTOCOL_ID or report.get("valid") is not True:
                raise EvaluationError(f"invalid score report: {raw_path}")
            sample_id = report.get("sample_id")
            if sample_id not in mappings:
                raise EvaluationError(f"missing condition mapping for {sample_id}")
            evaluator = report.get("evaluator", {})
            identity = (sample_id, evaluator.get("evaluator_id"), evaluator.get("pass_index"))
            if identity in report_identities:
                raise EvaluationError(f"duplicate score report {identity}")
            report_identities.add(identity)
            reports_by_sample[sample_id].append(report)

        sample_scores: dict[str, dict[str, Any]] = {}
        for sample_id, reports in reports_by_sample.items():
            dimension_scores = {}
            for dimension in PRIMARY_DIMENSIONS:
                values = [
                    report.get("primary_pedagogy_scores", {}).get(dimension)
                    for report in reports
                ]
                values = [value for value in values if isinstance(value, int)]
                dimension_scores[dimension] = median(values) if values else None
            safety = [report.get("selected_content_safety", {}).get("gate_pass") is True for report in reports]
            sample_scores[sample_id] = {
                "primary_scores": dimension_scores,
                "judge_pass_count": len(reports),
                "all_judge_safety_gates_pass": all(safety),
            }

        condition_summary: dict[str, Any] = {}
        for condition in ("P0", "P1", "P2"):
            sample_ids = [sample_id for sample_id in sample_scores if mappings[sample_id].get("condition") == condition]
            dimensions = {}
            for dimension in PRIMARY_DIMENSIONS:
                values = [sample_scores[sample_id]["primary_scores"][dimension] for sample_id in sample_ids]
                values = [value for value in values if value is not None]
                dimensions[dimension] = {
                    "n_generated_lessons": len(values),
                    "median": median(values) if values else None,
                    "mean_descriptive": rounded(mean(values)) if values else None,
                    "minimum": min(values) if values else None,
                    "maximum": max(values) if values else None,
                }
            condition_summary[condition] = {
                "sample_count": len(sample_ids),
                "safety_gate_pass_count": sum(sample_scores[sample_id]["all_judge_safety_gates_pass"] for sample_id in sample_ids),
                "dimensions": dimensions,
            }

        keyed: dict[tuple[str, str, int, str], str] = {}
        for sample_id in sample_scores:
            mapping = mappings[sample_id]
            key = (
                str(mapping.get("topic")),
                str(mapping.get("profile_id")),
                run_index(mapping.get("run_id")),
                str(mapping.get("condition")),
            )
            if key in keyed:
                raise EvaluationError(f"duplicate matched cell: {key}")
            keyed[key] = sample_id

        contrasts: dict[str, Any] = {}
        for baseline in ("P1", "P0"):
            contrast_name = f"P2-{baseline}"
            dimension_results = {}
            for dimension in PRIMARY_DIMENSIONS:
                differences: list[float] = []
                wins = ties = losses = 0
                for (topic, profile, run, condition), p2_id in keyed.items():
                    if condition != "P2":
                        continue
                    baseline_id = keyed.get((topic, profile, run, baseline))
                    if not baseline_id:
                        continue
                    p2_value = sample_scores[p2_id]["primary_scores"][dimension]
                    baseline_value = sample_scores[baseline_id]["primary_scores"][dimension]
                    if p2_value is None or baseline_value is None:
                        continue
                    difference = p2_value - baseline_value
                    differences.append(difference)
                    wins += difference > 0
                    ties += difference == 0
                    losses += difference < 0
                count = len(differences)
                dimension_results[dimension] = {
                    "matched_pair_count": count,
                    "wins": wins,
                    "ties": ties,
                    "losses": losses,
                    "probability_of_superiority": rounded((wins + 0.5 * ties) / count) if count else None,
                    "median_paired_difference": median(differences) if differences else None,
                    "mean_paired_difference_descriptive": rounded(mean(differences)) if differences else None,
                }
            contrasts[contrast_name] = dimension_results

        report = {
            "schema_version": "1.0",
            "protocol_id": PROTOCOL_ID,
            "analysis_level": "generated_lesson_with_judge_passes_collapsed_by_sample_median",
            "condition_summary": condition_summary,
            "paired_contrasts": contrasts,
            "warnings": [
                "The four primary dimensions are not combined into a composite score.",
                "P0 reuse across profiles must be retained in any later uncertainty model; duplicated profile-relative P0 ratings are not independent generated lessons.",
                "No student outcome or learner-reported comprehensibility is estimated.",
            ],
        }
        write_json(output, report)
        print(f"PASS: RQ2 aggregate report created at {output}")
        return 0
    except (EvaluationError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
