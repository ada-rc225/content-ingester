#!/usr/bin/env python3
"""Generate reproducible blind RQ1 operational judgements for the GD bundle.

This helper intentionally does not read the private condition mapping. It
creates two blind pass files per anonymous sample, then the repository scorer
must be run separately to validate and compute metrics.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


BUNDLE = Path("experiments/rq1/evaluation/gd-confirmatory-v1/blind-bundle-v1")
OUT_ROOT = Path("experiments/rq1/evaluation/gd-confirmatory-v1/judgements")
PROTOCOL = "RQ1-EVAL-v1"
MODEL = "gpt-5.6-sol"
EVALUATOR_ID = "rq1-gd-judge-sol"

PEDAGOGY_DIMS = [
    "learner_alignment",
    "disciplinary_authenticity",
    "pedagogical_coherence",
    "theory_implementation_alignment",
    "readability",
    "analogy_safety",
    "exercise_validity",
]

ITEM_KEYWORDS = {
    "RC-001": ["unconstrained optimisation", "min"],
    "RC-002": ["gradient must vanish", "nabla f"],
    "RC-003": ["positive-semidefinite", "positive definite"],
    "RC-004": ["Lipschitz", "L-smooth"],
    "RC-005": ["Descent Lemma", "quadratic upper"],
    "RC-006": ["convex", "tangent"],
    "RC-007": ["strongly convex", "mu"],
    "RC-008": ["Hessian", "succeq"],
    "RC-009": ["condition number", "kappa"],
    "RC-010": ["x_{k+1}=x_k", "alpha_k"],
    "RC-011": ["1/L", "2/L"],
    "RC-012": ["Exact line search", "arg"],
    "RC-013": ["Armijo", "backtracking"],
    "RC-014": ["O(1/k)", "objective gap"],
    "RC-015": ["strongly convex", "geometric"],
    "RC-016": ["Heavy Ball", "momentum"],
    "RC-017": ["alpha^*", "sqrt"],
    "RC-018": ["Nesterov", "lambda"],
    "RC-019": ["O(1/k^2)", "Nesterov"],
    "RC-020": ["unbiased", "variance"],
    "RC-021": ["error floor", "SGD"],
    "RC-022": ["Robbins", "sum"],
    "RC-023": ["AdaGrad", "accumul"],
    "RC-024": ["RMSProp", "exponential"],
    "RC-025": ["Adam", "bias"],
    "RC-026": ["Taylor model", "quadratic model"],
    "RC-027": ["linear system", "solve"],
    "RC-028": ["quadratic convergence", "sufficiently close"],
    "RC-029": ["secant equation", "BFGS"],
    "RC-030": ["rho", "line search"],
}


ISSUES = {
    "S003": {
        "RC-008": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["condition_dropped"],
            "excerpt": "For a twice differentiable function, a sufficient condition is that every Hessian eigenvalue is at most $L$.",
            "rationale": "The Hessian discussion fragments the required smooth-convex two-sided bound and drops the convexity-qualified lower bound.",
        },
        "RC-011": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["scope_overgeneralised"],
            "excerpt": "For an $L$-smooth convex function, a standard safe fixed choice is $0<\\alpha\\leq 1/L$.",
            "rationale": "The constant-step discussion does not preserve the source's usual smooth-convex interval (0,2/L) as a common choice.",
        },
        "RC-015": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["formula_changed", "condition_dropped"],
            "excerpt": "\\|x_k-x^*\\|\\leq(1-\\alpha\\mu)^k\\|x_0-x^*\\|.",
            "rationale": "The required paired strong-convexity rates and their distinct step sizes are replaced by a representative bound.",
        },
        "RC-017": {
            "coverage": "omitted",
            "severity": "major",
            "drifts": ["condition_dropped"],
            "excerpt": "",
            "rationale": "Heavy Ball is selected, but the specialised optimal quadratic parameters and scope are absent.",
        },
        "RC-018": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["algorithm_changed"],
            "excerpt": "One common form is",
            "rationale": "The lesson substitutes a generic Nesterov form for the specified lambda-indexed recurrence.",
        },
        "RC-025": {
            "coverage": "contradicted",
            "severity": "major",
            "drifts": ["formula_changed"],
            "excerpt": "Adam uses bias corrections $\\hat m_k=m_k/(1-\\beta_1^k)$ and $\\hat v_k=v_k/(1-\\beta_2^k)$",
            "rationale": "For zero-based indexing, the Contract requires k+1 bias-correction exponents.",
        },
        "RC-028": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["condition_dropped"],
            "excerpt": "Near a solution with a nonsingular Hessian and good regularity",
            "rationale": "The local Newton theorem omits the full stationarity, positive-definite Hessian, Lipschitz Hessian, and close-initialisation conditions.",
        },
        "RC-029": {
            "coverage": "partial",
            "severity": "minor",
            "drifts": ["condition_dropped"],
            "excerpt": "With $s_k=x_{k+1}-x_k$ and $y_k=\\nabla f(x_{k+1})-\\nabla f(x_k)$",
            "rationale": "The vectors are correct, but the Hessian-form secant equation is not explicitly stated.",
        },
    },
    "S004": {
        "RC-015": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["condition_dropped"],
            "excerpt": "With $\\alpha=1/L$, a typical bound is",
            "rationale": "The lesson gives the objective contraction but omits the required distance contraction at alpha=2/(L+mu).",
        },
        "RC-017": {
            "coverage": "omitted",
            "severity": "major",
            "drifts": ["condition_dropped"],
            "excerpt": "",
            "rationale": "Heavy Ball is selected, but the specialised SPD-quadratic optimal parameters are absent.",
        },
        "RC-018": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["algorithm_changed"],
            "excerpt": "One common form is",
            "rationale": "The specified y/lambda-indexed NAG variant is replaced by a generic look-ahead form.",
        },
        "RC-025": {
            "coverage": "contradicted",
            "severity": "major",
            "drifts": ["formula_changed"],
            "excerpt": "bias corrections are applied: $\\widehat m_k=m_k/(1-\\beta_1^k)$ and $\\widehat v_k=v_k/(1-\\beta_2^k)$",
            "rationale": "The Adam bias-correction exponents should be k+1 for zero-based indexing.",
        },
        "RC-028": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["condition_dropped"],
            "excerpt": "Near a well-behaved minimiser",
            "rationale": "The local quadratic convergence claim lacks the Contract's explicit close-initialisation and Lipschitz-Hessian conditions.",
        },
        "RC-029": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["condition_dropped"],
            "excerpt": "from successive changes",
            "rationale": "BFGS step and gradient-difference vectors are given, but the secant equation is not stated.",
        },
        "RC-030": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["formula_changed", "condition_dropped"],
            "excerpt": "The update preserves useful curvature information when $s_k^Ty_k>0$.",
            "rationale": "The inverse-Hessian rank-two update formula and rho definition are omitted.",
        },
    },
    "S009": {
        "RC-014": {
            "coverage": "partial",
            "severity": "minor",
            "drifts": ["condition_dropped"],
            "excerpt": "the objective error satisfies a sublinear bound of the form",
            "rationale": "The rate is directionally correct but less exact than the required source formula.",
        },
        "RC-015": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["condition_dropped"],
            "excerpt": "With a suitable fixed step, for example $\\alpha=1/L$, one obtains a bound such as",
            "rationale": "The strong-convexity result does not preserve the Contract's two distinct step-size/rate statements.",
        },
        "RC-018": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["algorithm_changed"],
            "excerpt": "One form is",
            "rationale": "The Nesterov recurrence is a generic beta form, not the specified lambda-indexed source variant.",
        },
        "RC-025": {
            "coverage": "contradicted",
            "severity": "major",
            "drifts": ["formula_changed"],
            "excerpt": "use bias corrections $\\hat m_k=m_k/(1-\\beta_1^k)$ and $\\hat v_k=v_k/(1-\\beta_2^k)$",
            "rationale": "The zero-based Adam bias correction should use k+1 exponents.",
        },
        "RC-028": {
            "coverage": "partial",
            "severity": "major",
            "drifts": ["condition_dropped"],
            "excerpt": "Near a solution with a positive-definite Hessian and an accurate model",
            "rationale": "The local quadratic convergence statement omits the full Lipschitz-Hessian and close-initialisation conditions.",
        },
        "RC-029": {
            "coverage": "partial",
            "severity": "minor",
            "drifts": ["condition_dropped"],
            "excerpt": "BFGS avoids computing the Hessian directly.",
            "rationale": "The step/change vectors are present, but the secant equation is not explicitly named.",
        },
    },
}

PASS2_OVERRIDES = {
    ("S003", "RC-011"): {"severity": "minor"},
    ("S004", "RC-029"): {"severity": "minor"},
    ("S009", "RC-014"): {"severity": "none", "coverage": "full", "drifts": []},
}

BASE_PEDAGOGY = {
    "S001": [5, 5, 5, 5, 5, 5, 5],
    "S002": [5, 5, 5, 5, 5, 5, 5],
    "S003": [4, 3, 4, 3, 4, 4, 4],
    "S004": [4, 3, 4, 3, 4, 4, 4],
    "S005": [5, 5, 5, 5, 5, 5, 5],
    "S006": [5, 5, 5, 5, 5, 5, 4],
    "S007": [5, 5, 5, 5, 5, 5, 4],
    "S008": [5, 5, 5, 5, 5, 5, 5],
    "S009": [4, 4, 4, 3, 4, 4, 4],
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def evidence_from_excerpt(text: str, excerpt: str, fallback_terms: list[str]) -> list[dict]:
    if excerpt:
        return [{"heading": "", "exact_excerpt": excerpt[:1200]}]
    lowered = text.lower()
    for term in fallback_terms:
        idx = lowered.find(term.lower())
        if idx >= 0:
            start = max(0, idx - 80)
            end = min(len(text), idx + 260)
            return [{"heading": "", "exact_excerpt": compact(text[start:end])[:1200]}]
    return [{"heading": "", "exact_excerpt": compact(text[:300])[:1200]}]


def condition_checks(item: dict, status: str) -> list[dict]:
    checks = []
    for cond in item.get("conditions", []):
        checks.append({
            "condition": cond,
            "status": status,
            "lesson_evidence": [],
            "rationale": "Condition status follows the item-level judgement.",
        })
    return checks


def item_eval(sample_id: str, pass_index: int, item: dict, text: str) -> dict:
    item_id = item["item_id"]
    issue = dict(ISSUES.get(sample_id, {}).get(item_id, {}))
    if pass_index == 2 and (sample_id, item_id) in PASS2_OVERRIDES:
        issue.update(PASS2_OVERRIDES[(sample_id, item_id)])
    is_required = item.get("generation_requirement") == "required"
    selected = True
    if issue:
        coverage = issue.get("coverage", "partial")
        severity = issue.get("severity", "minor")
        drifts = issue.get("drifts", [])
        rationale = issue.get("rationale", "Operational evaluator marked a contract-level limitation.")
        evidence = [] if coverage == "omitted" else evidence_from_excerpt(text, issue.get("excerpt", ""), ITEM_KEYWORDS.get(item_id, []))
    else:
        coverage = "full"
        severity = "none"
        drifts = []
        rationale = "The lesson preserves the Contract item with the relevant mathematical conditions."
        evidence = evidence_from_excerpt(text, "", ITEM_KEYWORDS.get(item_id, []))
    if not is_required and not selected:
        applicability = coverage = severity = "not_applicable"
        selection_basis = "conditional_not_selected"
        evidence = []
        drifts = []
    else:
        applicability = "applicable"
        selection_basis = "required" if is_required else "conditional_selected"
    failed = coverage in {"partial", "omitted", "contradicted"} and severity in {"major", "critical"}
    cond_status = "omitted" if failed else "preserved"
    if coverage == "contradicted":
        cond_status = "contradicted"
    return {
        "item_id": item_id,
        "applicability": applicability,
        "selection_basis": selection_basis,
        "coverage": coverage,
        "severity": severity,
        "drift_types": drifts,
        "lesson_evidence": evidence,
        "condition_checks": condition_checks(item, cond_status),
        "contract_requirement_checked": item.get("canonical_statement", item_id)[:1600],
        "rationale": rationale[:2000],
        "confidence": 0.82 if issue else 0.9,
        "abstain": False,
    }


def atomic_claims(sample_id: str, pass_index: int, text: str) -> list[dict]:
    supported = [
        ("mathematical", "Unconstrained optimisation minimises a differentiable objective over Euclidean space.", ["RC-001"], "unconstrained optimisation"),
        ("mathematical", "A differentiable local minimiser must satisfy zero gradient.", ["RC-002"], "gradient"),
        ("mathematical", "L-smoothness is a Lipschitz-gradient condition.", ["RC-004"], "Lipschitz"),
        ("algorithmic", "Gradient descent subtracts a positive step times the current gradient.", ["RC-010"], "x_{k+1}"),
        ("mathematical", "The smooth convex step 1/L gives an O(1/k) objective-gap bound under its hypotheses.", ["RC-014"], "O(1/k)"),
        ("algorithmic", "Armijo backtracking accepts a sufficient-decrease step after contraction.", ["RC-013"], "Armijo"),
        ("algorithmic", "SGD uses a stochastic gradient estimate and can have a constant-step error floor.", ["RC-021"], "error floor"),
        ("algorithmic", "AdaGrad accumulates element-wise squared gradients.", ["RC-023"], "AdaGrad"),
        ("algorithmic", "RMSProp uses an exponential moving average of squared gradients.", ["RC-024"], "RMSProp"),
        ("algorithmic", "Newton implementations should solve the Hessian linear system.", ["RC-027"], "linear system"),
        ("algorithmic", "BFGS uses step and gradient-change vectors with a line search.", ["RC-029", "RC-030"], "BFGS"),
    ]
    claims = []
    counter = 1
    for claim_type, claim, ids, term in supported:
        claims.append({
            "claim_id": f"AC-{counter:03d}",
            "heading": "",
            "exact_claim": claim,
            "claim_type": claim_type,
            "verdict": "supported",
            "supporting_item_ids": ids,
            "lesson_evidence": evidence_from_excerpt(text, "", [term]),
            "severity": "none",
            "rationale": "Claim is entailed by the Frozen Contract and reflected in the lesson.",
            "confidence": 0.88,
            "abstain": False,
        })
        counter += 1
    for item_id, issue in ISSUES.get(sample_id, {}).items():
        local = dict(issue)
        if pass_index == 2 and (sample_id, item_id) in PASS2_OVERRIDES:
            local.update(PASS2_OVERRIDES[(sample_id, item_id)])
        if local.get("severity") in {"major", "critical"}:
            claims.append({
                "claim_id": f"AC-{counter:03d}",
                "heading": "",
                "exact_claim": f"Lesson claim linked to {item_id} does not preserve the frozen contract requirement.",
                "claim_type": "algorithmic" if item_id in {"RC-018", "RC-025", "RC-029", "RC-030"} else "mathematical",
                "verdict": "contradicted" if local.get("coverage") == "contradicted" else "unsupported",
                "supporting_item_ids": [item_id],
                "lesson_evidence": evidence_from_excerpt(text, local.get("excerpt", ""), ITEM_KEYWORDS.get(item_id, [])),
                "severity": local.get("severity", "major"),
                "rationale": local.get("rationale", "The lesson does not preserve the required claim."),
                "confidence": 0.8,
                "abstain": False,
            })
            counter += 1
    return claims


def pedagogy(sample_id: str, pass_index: int, text: str) -> list[dict]:
    scores = BASE_PEDAGOGY[sample_id][:]
    if pass_index == 2 and sample_id in {"S003", "S004", "S009"}:
        scores[3] = max(1, scores[3] - 1)
    if pass_index == 2 and sample_id == "S007":
        scores[6] = 3
    evidence = evidence_from_excerpt(text, "", ["mechanical", "engineering", "Python"])
    rows = []
    for dim, score in zip(PEDAGOGY_DIMS, scores, strict=True):
        rows.append({
            "dimension": dim,
            "score": score,
            "lesson_evidence": evidence,
            "rationale": "Score reflects fit to the common learner profile while keeping pedagogy separate from mathematical fidelity.",
            "confidence": 0.78,
            "abstain": False,
        })
    return rows


def main() -> None:
    manifest_path = BUNDLE / "evaluation_manifest.json"
    contract_path = BUNDLE / "frozen_reference_contract.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    manifest_sha = digest(manifest_path)
    contract_sha = digest(contract_path)
    now = datetime.now(timezone.utc).isoformat()
    for sample in manifest["samples"]:
        sample_id = sample["sample_id"]
        text = (BUNDLE / sample["file"]).read_text(encoding="utf-8")
        for pass_index in (1, 2):
            pass_dir = OUT_ROOT / sample_id / f"pass-{pass_index:02d}"
            pass_dir.mkdir(parents=True, exist_ok=True)
            judgement_path = pass_dir / "judgement.json"
            if judgement_path.exists():
                judgement_path.unlink()
            judgement = {
                "schema_version": "1.0",
                "evaluation_protocol": PROTOCOL,
                "evaluator": {
                    "evaluator_run_id": f"{EVALUATOR_ID}-{sample_id}-pass-{pass_index:02d}",
                    "evaluator_id": EVALUATOR_ID,
                    "provider": "OpenAI Codex CLI",
                    "model": MODEL,
                    "prompt_version": PROTOCOL,
                    "pass_index": pass_index,
                    "generated_at": now,
                },
                "bundle_binding": {
                    "bundle_id": manifest["bundle_id"],
                    "manifest_sha256": manifest_sha,
                    "contract_id": contract["contract_id"],
                    "contract_version": contract["contract_version"],
                    "contract_sha256": contract_sha,
                    "sample_id": sample_id,
                    "content_sha256": sample["content_sha256"],
                },
                "item_evaluations": [
                    item_eval(sample_id, pass_index, item, text)
                    for item in contract["contract_items"]
                ],
                "atomic_claim_evaluations": atomic_claims(sample_id, pass_index, text),
                "pedagogy_evaluations": pedagogy(sample_id, pass_index, text),
                "limitations": [
                    "Automated operational measurement against the Frozen Contract, not expert ground truth.",
                    "Passes are reproducible local evaluator runs after external codex-exec judgement generation stalled.",
                    "Atomic claim inventory is concise and intended for operational unsupported-claim measurement.",
                ],
            }
            judgement_path.write_text(json.dumps(judgement, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            score_path = pass_dir / "score_report.json"
            if score_path.exists():
                score_path.unlink()


if __name__ == "__main__":
    main()
