#!/usr/bin/env python3
"""Unblind completed RQ1 score reports and aggregate run-level metrics by condition."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


METRICS = (
    ("primary_outcome", "major_critical_error_rate"),
    ("fidelity_outcomes", "semantic_drift_rate"),
    ("fidelity_outcomes", "required_item_omission_rate"),
    ("fidelity_outcomes", "unsupported_claim_rate"),
    ("fidelity_outcomes", "formula_item_accuracy"),
    ("fidelity_outcomes", "algorithm_item_accuracy"),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", type=Path, required=True)
    parser.add_argument("--report", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite: {args.output}")
    mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
    labels = {entry["sample_id"]: entry["condition_label"] for entry in mapping["samples"]}
    rows = []
    seen_passes = set()
    for report_path in args.report:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("status") != "passed" or report.get("input", {}).get("sample_id") not in labels:
            parser.error(f"invalid or unmapped score report: {report_path}")
        key = (report["input"]["sample_id"], report["input"]["evaluator_run_id"])
        if key in seen_passes:
            parser.error(f"duplicate evaluator pass: {key}")
        seen_passes.add(key)
        row = {"sample_id": key[0], "condition_label": labels[key[0]], "evaluator_run_id": key[1]}
        for section, metric in METRICS:
            row[metric] = report[section].get(metric)
        rows.append(row)

    by_sample: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_sample[row["sample_id"]].append(row)
    sample_rows = []
    for sample_id, passes in sorted(by_sample.items()):
        sample_row = {
            "sample_id": sample_id,
            "condition_label": passes[0]["condition_label"],
            "evaluator_pass_count": len(passes),
        }
        for _, metric in METRICS:
            values = [row[metric] for row in passes if isinstance(row[metric], (int, float))]
            sample_row[metric] = round(statistics.fmean(values), 6) if values else None
        sample_rows.append(sample_row)

    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in sample_rows:
        grouped[row["condition_label"]].append(row)
    summaries = {}
    for label, group in sorted(grouped.items()):
        summary = {
            "lesson_sample_count": len(group),
            "evaluation_pass_count": sum(row["evaluator_pass_count"] for row in group),
            "sample_ids": sorted(row["sample_id"] for row in group),
            "metrics": {},
        }
        for _, metric in METRICS:
            values = [row[metric] for row in group if isinstance(row[metric], (int, float))]
            summary["metrics"][metric] = {
                "n": len(values),
                "mean": round(statistics.fmean(values), 6) if values else None,
                "median": round(statistics.median(values), 6) if values else None,
                "minimum": min(values) if values else None,
                "maximum": max(values) if values else None,
            }
        summaries[label] = summary
    output = {
        "schema_version": "1.0",
        "evaluation_protocol": "RQ1-EVAL-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "bundle_id": mapping["bundle_id"],
        "condition_summaries": summaries,
        "sample_rows": sample_rows,
        "pass_rows": rows,
        "warnings": [
            "Condition summaries first average evaluator passes within each lesson, then summarise independent lesson samples.",
            "Use topic/run-aware statistical modelling or clustered bootstrap for confirmatory inference."
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Aggregated {len(rows)} reports across {len(summaries)} condition labels: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
