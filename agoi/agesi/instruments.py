"""
AGESI instrument layer — the financial machinery from the MVP architecture.

Three components, per the AGESI Integrated Minimum Viable Architecture:

  CGV   Credit Guarantee Vehicle — quantifies how a partial guarantee lowers a
        project's borrowing cost, and therefore its monthly debt service. This is
        the mechanism that turns a marginal green project into a bankable one.

  NEAI  Environmental credit issuance — converts a FIPRE-screened project's
        verified abatement into a priced, issuable credit instrument.

  ETIV  Environmental Transaction Integrity Value — a single 0–1 integrity score
        gating whether credits may be issued at all.

═══════════════════════════════════════════════════════════════════════════════
The CGV maths is exact (standard amortisation — no assumptions). The RISK-TO-RATE
mapping and the ETIV weights are POLICY PARAMETERS, adjustable in the UI and
labelled as such. Credit prices are user inputs, not platform estimates.
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Dict

# ──────────────────────────────────────────────────────────────────────────────
# CGV — Credit Guarantee Vehicle
# ──────────────────────────────────────────────────────────────────────────────

def monthly_payment(principal: float, annual_rate_pct: float, years: int) -> float:
    """Standard amortising loan payment. Exact formula — no assumptions."""
    n = years * 12
    r = annual_rate_pct / 100.0 / 12.0
    if n <= 0:
        return 0.0
    if r == 0:
        return principal / n
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)


def guaranteed_rate(base_rate_pct: float, coverage_pct: float,
                    max_reduction_pts: float = 6.0) -> float:
    """
    Rate after a partial credit guarantee.

    A guarantee transfers default risk to the guarantor, so the lender prices the
    loan closer to the guarantor's risk than the borrower's. We model the spread
    reduction as proportional to coverage:

        new_rate = base_rate - (coverage_fraction x max_reduction_pts)

    `max_reduction_pts` is a POLICY PARAMETER (the spread a full guarantee could
    remove, in percentage points), not an empirical constant. Default 6.0 pts
    reflects a typical Nigerian sub-sovereign green-project spread; adjust in UI.
    """
    reduction = (coverage_pct / 100.0) * max_reduction_pts
    return max(0.5, base_rate_pct - reduction)


def cgv_analysis(principal: float, base_rate_pct: float, years: int,
                 coverage_pct: float, max_reduction_pts: float = 6.0) -> Dict:
    """Full before/after comparison for a guarantee."""
    g_rate = guaranteed_rate(base_rate_pct, coverage_pct, max_reduction_pts)
    pay_without = monthly_payment(principal, base_rate_pct, years)
    pay_with    = monthly_payment(principal, g_rate, years)
    n = years * 12
    total_without = pay_without * n
    total_with    = pay_with * n
    return {
        "principal": principal,
        "years": years,
        "rate_without": round(base_rate_pct, 2),
        "rate_with": round(g_rate, 2),
        "rate_saving_pts": round(base_rate_pct - g_rate, 2),
        "coverage_pct": coverage_pct,
        "guarantee_exposure": round(principal * coverage_pct / 100.0, 2),
        "monthly_without": round(pay_without, 2),
        "monthly_with": round(pay_with, 2),
        "monthly_saving": round(pay_without - pay_with, 2),
        "total_without": round(total_without, 2),
        "total_with": round(total_with, 2),
        "lifetime_saving": round(total_without - total_with, 2),
        "saving_pct": round((pay_without - pay_with) / pay_without * 100, 1) if pay_without else 0.0,
    }


# ──────────────────────────────────────────────────────────────────────────────
# ETIV — Environmental Transaction Integrity Value (0–1)
# ──────────────────────────────────────────────────────────────────────────────

ETIV_COMPONENTS = {
    "additionality":  "Would the abatement have happened anyway? (higher = more additional)",
    "permanence":     "How durable is the abatement? (reversal risk)",
    "verification":   "Strength of measurement, reporting and third-party verification",
    "leakage":        "Freedom from emissions displaced elsewhere (higher = less leakage)",
    "co_benefits":    "Social and biodiversity co-benefits delivered",
}
ETIV_WEIGHTS = {"additionality":0.30, "permanence":0.25, "verification":0.25,
                "leakage":0.10, "co_benefits":0.10}

# Minimum ETIV for credits to be issuable.
ETIV_ISSUANCE_FLOOR = 0.60


def etiv_score(components: Dict[str, float]) -> Dict:
    """
    components: {name: 0–1}. Returns the weighted ETIV plus an issuance verdict.
    """
    score = sum(components.get(k, 0.0) * w for k, w in ETIV_WEIGHTS.items())
    score = round(min(1.0, max(0.0, score)), 3)
    weakest = min(ETIV_COMPONENTS, key=lambda k: components.get(k, 0.0))
    return {
        "etiv": score,
        "issuable": score >= ETIV_ISSUANCE_FLOOR,
        "floor": ETIV_ISSUANCE_FLOOR,
        "weakest": weakest,
        "note": ("Meets the integrity floor — credits may be issued."
                 if score >= ETIV_ISSUANCE_FLOOR else
                 f"Below the {ETIV_ISSUANCE_FLOOR} integrity floor — issuance blocked. "
                 f"Weakest component: {weakest}."),
    }


# ──────────────────────────────────────────────────────────────────────────────
# NEAI — environmental credit issuance
# ──────────────────────────────────────────────────────────────────────────────

def issue_credits(credit_type: str, tonnes_co2e: float, price_per_credit: float,
                  etiv: float, fipre_passed: bool,
                  fipre_impact_score: float = 0.0,
                  impact_floor: float = 3.0) -> Dict:
    """
    Build a credit issuance record.

    Two gates must BOTH clear before credits are issuable:
      1. FIPRE  — the project passed the non-compensatory screen, AND its Impact
                  dimension clears the integrity floor (the sheet's "E >= 3.0").
      2. ETIV   — transaction integrity at or above the issuance floor.

    Gross value is simply tonnes x price (a user input, not a platform estimate).
    """
    impact_ok = fipre_impact_score >= impact_floor
    etiv_ok = etiv >= ETIV_ISSUANCE_FLOOR
    issuable = bool(fipre_passed and impact_ok and etiv_ok)

    blockers = []
    if not fipre_passed:
        blockers.append("FIPRE screen not passed")
    if not impact_ok:
        blockers.append(f"FIPRE Impact below {impact_floor}")
    if not etiv_ok:
        blockers.append(f"ETIV below {ETIV_ISSUANCE_FLOOR}")

    gross = tonnes_co2e * price_per_credit
    return {
        "credit_type": credit_type,
        "units": tonnes_co2e,
        "unit_definition": "1 credit = 1 tonne CO₂ equivalent",
        "price_per_credit": price_per_credit,
        "gross_value": gross,
        "etiv": etiv,
        "fipre_passed": fipre_passed,
        "fipre_impact": fipre_impact_score,
        "issuable": issuable,
        "blockers": blockers,
        "integrity_statement": (
            f"FIPRE-scored (Impact ≥ {impact_floor}) · ETIV {etiv:.2f} ≥ {ETIV_ISSUANCE_FLOOR}"
            if issuable else "NOT ISSUABLE — integrity gates not met"),
    }


def fmt_ngn(x: float) -> str:
    if x >= 1e12: return f"₦{x/1e12:,.2f}T"
    if x >= 1e9:  return f"₦{x/1e9:,.1f}B"
    if x >= 1e6:  return f"₦{x/1e6:,.1f}M"
    if x >= 1e3:  return f"₦{x/1e3:,.0f}K"
    return f"₦{x:,.0f}"
