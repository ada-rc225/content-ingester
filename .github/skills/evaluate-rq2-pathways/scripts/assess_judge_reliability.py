#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from rq2_eval_common import PRIMARY_DIMENSIONS, PROTOCOL_ID, EvaluationError, load_json, write_json


def ordinal_alpha(units: list[list[int]]) -> float | None:
    usable = [values for values in units if len(values) >= 2]
    if not usable:
        return None
    coincidences: dict[tuple[int, int], float] = defaultdict(float)
    for values in usable:
        denominator = len(values) - 1
        for left_index, left in enumerate(values):
            for right_index, right in enumerate(values):
                if left_index != right_index:
                    coincidences[(left, right)] += 1 / denominator
    marginals: Counter[int] = Counter()
    for (left, _), value in coincidences.items():
        marginals[left] += value
    total = sum(marginals.values())
    if total <= 1:
        return None

    def distance(left: int, right: int) -> float:
        if left == right:
            return 0.0
        low, high = sorted((left, right))
        between = sum(marginals[value] for value in range(low, high + 1))
        adjusted = between - (marginals[low] + marginals[high]) / 2
        return adjusted * adjusted

    observed = sum(value * distance(left, right) for (left, right), value in coincidences.items()) / total
    expected = sum(
        marginals[left] * marginals[right] * distance(left, right)
        for left in marginals for right in marginals
    ) / (total * (total - 1))
    if expected == 0:
        return 1.0 if observed == 0 else None
    return round(1 - observed / expected, 6)


def main() -> int:
    parser = argparse.ArgumentParser(description="Assess blind RQ2 judge agreement across samples.")
    parser.add_argument("--judgement", action="append", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = Path(args.output).resolve()
    try:
        if output.exists():
            raise EvaluationError(f"refusing to overwrite reliability report: {output}")
        records: list[dict[str, Any]] = []
        identities: set[tuple[str, str, int]] = set()
        for raw_path in args.judgement:
            path = Path(raw_path).resolve()
            judgement = load_json(path)
            if judgement.get("protocol_id") != PROTOCOL_ID:
                raise EvaluationError(f"unexpected protocol in {path}")
            sample_id = judgement.get("sample_id")
            evaluator = judgement.get("evaluator", {})
            identity = (sample_id, evaluator.get("evaluator_id"), evaluator.get("pass_index"))
            if identity in identities:
                raise EvaluationError(f"duplicate sample/evaluator/pass: {identity}")
            identities.add(identity)
            scores = {
                item.get("dimension"): item.get("score")
                for item in judgement.get("primary_pedagogy_judgements", [])
                if isinstance(item, dict)
            }
            records.append({"sample_id": sample_id, "identity": identity, "scores": scores, "file": str(path)})

        results: dict[str, Any] = {}
        for dimension in PRIMARY_DIMENSIONS:
            by_sample: dict[str, list[int]] = defaultdict(list)
            for record in records:
                score = record["scores"].get(dimension)
                if isinstance(score, int) and 1 <= score <= 5:
                    by_sample[record["sample_id"]].append(score)
            pairs: list[tuple[int, int]] = []
            for values in by_sample.values():
                pairs.extend(itertools.combinations(values, 2))
            exact = ratio = None
            mean_abs = None
            large = 0
            if pairs:
                exact = sum(left == right for left, right in pairs) / len(pairs)
                ratio = sum(1 - ((left - right) / 4) ** 2 for left, right in pairs) / len(pairs)
                mean_abs = mean(abs(left - right) for left, right in pairs)
                large = sum(abs(left - right) >= 2 for left, right in pairs)
            results[dimension] = {
                "sample_count_with_two_or_more_ratings": sum(len(values) >= 2 for values in by_sample.values()),
                "rating_count": sum(len(values) for values in by_sample.values()),
                "pair_count": len(pairs),
                "exact_agreement": round(exact, 6) if exact is not None else None,
                "quadratic_weighted_pair_agreement": round(ratio, 6) if ratio is not None else None,
                "mean_absolute_difference": round(mean_abs, 6) if mean_abs is not None else None,
                "disagreement_at_least_two_count": large,
                "krippendorff_alpha_ordinal": ordinal_alpha(list(by_sample.values())),
            }

        report = {
            "schema_version": "1.0",
            "protocol_id": PROTOCOL_ID,
            "judgement_count": len(records),
            "sample_count": len({record["sample_id"] for record in records}),
            "dimensions": results,
            "interpretation": "Reliability is computed across blind raw judgements before adjudication. Judge passes are repeated measurements, not generated-lesson sample size.",
        }
        write_json(output, report)
        print(f"PASS: RQ2 reliability report created at {output}")
        return 0
    except (EvaluationError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
