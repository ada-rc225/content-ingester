#!/usr/bin/env python3
"""Measure blind test-retest agreement across repeated RQ1 evaluator judgements."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


def ratio(matches: int, total: int) -> float | None:
    return round(matches / total, 6) if total else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--judgement", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"refusing to overwrite: {args.output}")

    grouped: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for path in args.judgement:
        value = json.loads(path.read_text(encoding="utf-8"))
        binding = value.get("bundle_binding", {})
        key = (binding.get("bundle_id"), binding.get("contract_sha256"), binding.get("sample_id"))
        if not all(key):
            parser.error(f"judgement lacks a complete blind binding: {path}")
        grouped[key].append(value)

    sample_reports = []
    total_pairs = 0
    total_item_comparisons = 0
    severity_matches = coverage_matches = drift_matches = 0
    pedagogy_differences: list[float] = []
    for (bundle_id, contract_sha, sample_id), judgements in sorted(grouped.items()):
        if len(judgements) < 2:
            parser.error(f"sample {sample_id} has fewer than two independent passes")
        run_ids = [value["evaluator"]["evaluator_run_id"] for value in judgements]
        if len(run_ids) != len(set(run_ids)):
            parser.error(f"sample {sample_id} contains duplicate evaluator_run_id values")
        sample_pair_count = 0
        sample_items = sample_severity = sample_coverage = sample_drift = 0
        sample_pedagogy_diff: list[float] = []
        for left, right in itertools.combinations(judgements, 2):
            sample_pair_count += 1
            left_items = {entry["item_id"]: entry for entry in left["item_evaluations"]}
            right_items = {entry["item_id"]: entry for entry in right["item_evaluations"]}
            if set(left_items) != set(right_items):
                parser.error(f"sample {sample_id} passes do not judge identical Contract items")
            for item_id in left_items:
                a, b = left_items[item_id], right_items[item_id]
                sample_items += 1
                sample_severity += a["severity"] == b["severity"]
                sample_coverage += a["coverage"] == b["coverage"]
                sample_drift += set(a["drift_types"]) == set(b["drift_types"])
            left_pedagogy = {entry["dimension"]: entry["score"] for entry in left["pedagogy_evaluations"]}
            right_pedagogy = {entry["dimension"]: entry["score"] for entry in right["pedagogy_evaluations"]}
            if set(left_pedagogy) != set(right_pedagogy):
                parser.error(f"sample {sample_id} passes do not score identical pedagogy dimensions")
            for dimension in left_pedagogy:
                a, b = left_pedagogy[dimension], right_pedagogy[dimension]
                if isinstance(a, int) and isinstance(b, int):
                    sample_pedagogy_diff.append(abs(a - b))
        total_pairs += sample_pair_count
        total_item_comparisons += sample_items
        severity_matches += sample_severity
        coverage_matches += sample_coverage
        drift_matches += sample_drift
        pedagogy_differences.extend(sample_pedagogy_diff)
        sample_reports.append({
            "bundle_id": bundle_id,
            "contract_sha256": contract_sha,
            "sample_id": sample_id,
            "pass_count": len(judgements),
            "pass_pair_count": sample_pair_count,
            "severity_exact_agreement": ratio(sample_severity, sample_items),
            "coverage_exact_agreement": ratio(sample_coverage, sample_items),
            "drift_set_exact_agreement": ratio(sample_drift, sample_items),
            "pedagogy_mean_absolute_difference": round(sum(sample_pedagogy_diff) / len(sample_pedagogy_diff), 6) if sample_pedagogy_diff else None,
        })

    output = {
        "schema_version": "1.0",
        "evaluation_protocol": "RQ1-EVAL-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_count": len(sample_reports),
        "pass_pair_count": total_pairs,
        "overall": {
            "severity_exact_agreement": ratio(severity_matches, total_item_comparisons),
            "coverage_exact_agreement": ratio(coverage_matches, total_item_comparisons),
            "drift_set_exact_agreement": ratio(drift_matches, total_item_comparisons),
            "pedagogy_mean_absolute_difference": round(sum(pedagogy_differences) / len(pedagogy_differences), 6) if pedagogy_differences else None,
        },
        "samples": sample_reports,
        "warnings": [
            "Exact agreement measures repeatability, not correctness or expert validity.",
            "Use a known-label mutation benchmark to measure error-detection sensitivity and specificity."
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Reliability report written for {len(sample_reports)} samples: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
