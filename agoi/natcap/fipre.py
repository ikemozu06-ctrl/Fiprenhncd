"""
Natural Capital — FIPRE diagnostic lens (Part 3).

A NON-COMPENSATORY upstream screen across five dimensions. Non-compensatory is
the defining property: a strong score on one dimension CANNOT rescue a failing
score on another. A project that fails ANY single dimension is REJECTED outright
— you cannot buy your way past a fatal Equity or Impact flaw with a great
Function score. This is deliberately stricter than a weighted average and is what
makes FIPRE a genuine screen rather than a scorecard.

FIPRE dimensions:
  Function   — does the project practically utilise the mapped natural capital
               efficiently (e.g. solar yield, geothermal head, soil productivity)?
  Impact     — net-positive environmental & carbon effect?
  Prosperity — does the monetary valuation translate into localised economic growth?
  Resilience — how well does the asset withstand climate shocks?
  Equity     — are benefits (the "Green Dividend") fairly distributed — youth
               employment, community land rights, benefit-sharing?

Each dimension is scored 0–100. A single PASS_THRESHOLD applies to all five
(non-compensatory). The overall result is PASS only if EVERY dimension clears it.
"""
from __future__ import annotations
from typing import Dict, List

# The non-compensatory bar. A project must clear this on EVERY dimension.
PASS_THRESHOLD = 50.0

FIPRE_DIMENSIONS = {
    "function":   {"label": "Function",
                   "desc": "Practical, efficient use of the mapped natural capital.",
                   "guiding_q": "Does the project efficiently utilise the asset's service (yield, head, productivity)?"},
    "impact":     {"label": "Impact",
                   "desc": "Net-positive environmental and carbon effect.",
                   "guiding_q": "Is the net environmental/carbon effect positive and additional?"},
    "prosperity": {"label": "Prosperity",
                   "desc": "Localised economic growth from the valuation.",
                   "guiding_q": "Does the monetary value translate into local economic growth?"},
    "resilience": {"label": "Resilience",
                   "desc": "Ability to withstand climate shocks.",
                   "guiding_q": "How well does the asset/project withstand climate shocks?"},
    "equity":     {"label": "Equity",
                   "desc": "Fair distribution of the Green Dividend.",
                   "guiding_q": "Are benefits fairly shared — youth jobs, community rights, benefit-sharing?"},
}

DIM_ORDER = ["function", "impact", "prosperity", "resilience", "equity"]


def evaluate(scores: Dict[str, float], threshold: float = PASS_THRESHOLD) -> Dict:
    """
    Apply the non-compensatory FIPRE screen.

    scores: {dimension: 0–100}
    Returns:
      passed        overall PASS/FAIL (True only if EVERY dimension >= threshold)
      failed_dims   list of dimensions below threshold (the reason for any FAIL)
      binding       the single weakest dimension (the binding constraint)
      per_dim       {dim: {score, pass}}
      note          human-readable verdict
    """
    per_dim = {}
    failed = []
    for dim in DIM_ORDER:
        sc = float(scores.get(dim, 0.0))
        ok = sc >= threshold
        per_dim[dim] = {"score": round(sc, 1), "pass": ok}
        if not ok:
            failed.append(dim)

    passed = len(failed) == 0
    binding = min(DIM_ORDER, key=lambda d: scores.get(d, 0.0))

    if passed:
        note = ("PASS — clears the non-compensatory screen on all five dimensions. "
                "Eligible to proceed to structuring.")
    else:
        names = ", ".join(FIPRE_DIMENSIONS[d]["label"] for d in failed)
        note = (f"REJECTED — fails the non-compensatory screen on: {names}. "
                "A strong score elsewhere cannot compensate; the project is "
                "screened out upstream until the failing dimension(s) are remedied.")

    return {
        "passed": passed,
        "failed_dims": failed,
        "binding": binding,
        "per_dim": per_dim,
        "threshold": threshold,
        "min_score": round(min(scores.get(d, 0.0) for d in DIM_ORDER), 1),
        "note": note,
    }


def derive_from_asset(asset: Dict) -> Dict[str, float]:
    """
    Provide DEFAULT FIPRE scores for a natural-capital asset, so the screen can be
    demonstrated without a specific project. These are PROXIES derived from the
    asset's service-capacity profile — a starting point a user overrides with
    real project data. They are not project assessments.
    """
    s = asset["services"]
    return {
        "function":   round(s["provisioning"] * 0.6 + s["regulating"] * 0.4, 1),
        "impact":     round(s["regulating"] * 0.8 + s["cultural"] * 0.2, 1),
        "prosperity": round(s["provisioning"] * 0.7 + s["cultural"] * 0.3, 1),
        "resilience": round(s["regulating"] * 0.5 + s["provisioning"] * 0.5, 1),
        "equity":     round(s["cultural"] * 0.6 + s["provisioning"] * 0.4, 1),
    }


def summary_stats(evaluations: List[Dict]) -> Dict:
    """Portfolio-level pass/fail counts for a set of evaluations."""
    total = len(evaluations)
    passed = sum(1 for e in evaluations if e["passed"])
    return {"total": total, "passed": passed, "rejected": total - passed}
