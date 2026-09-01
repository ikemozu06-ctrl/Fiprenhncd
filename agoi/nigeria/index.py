"""
Nigeria state-level AGOI index.

Maps the real sourced indicators (states.py) onto the same six AGOI pillars used
at sovereign level, so a state score is conceptually comparable to a country
score. Uses the platform's standard pipeline: direction alignment → min-max
normalization to 0–100 → weighted pillar aggregation → band classification.

PILLAR MAPPING (and why)
  Policy       climate governance performance ranking (SPP)          higher better
  Sectoral     solar resource: PV output, DNI, GHI (Global Solar Atlas) higher better
  Finance      climate-budget coverage + state budget size            higher better
  Bankability  InfraCredit climate-facility project count  [PROXY]    higher better
  Resilience   flood-risk indicator (inverted)                        LOWER better
  Inclusive    HDI + Womanity Index + women's health index            higher better

Bankability is the weakest pillar here: the workbook's fiscal-performance columns
were excluded for misalignment (see states.py), so project count stands in. It is
flagged proxy throughout and the UI says so.
"""
from __future__ import annotations
from typing import Dict, List

from agoi import config
from agoi.nigeria.states import STATES, state_names

PILLARS = ["policy", "sectoral", "finance", "bankability", "resilience", "inclusive"]


def _minmax(vals: Dict[str, float], invert: bool = False) -> Dict[str, float]:
    """Scale a {state: value} dict to 0–100. invert=True for lower-is-better."""
    xs = [v for v in vals.values() if v is not None]
    lo, hi = min(xs), max(xs)
    out = {}
    for k, v in vals.items():
        if v is None or hi == lo:
            out[k] = 50.0
        else:
            s = (v - lo) / (hi - lo) * 100.0
            out[k] = 100.0 - s if invert else s
    return out


def compute() -> Dict[str, Dict]:
    """Return {state: {pillar scores, agoi_score, band, ...}} for all 37 regions."""
    names = state_names()

    # --- build each pillar's raw signal ---
    policy_raw    = {s: STATES[s]["policy_gov"] for s in names}
    # solar: mean of the six solar columns gives a single resource signal
    sectoral_raw  = {s: (STATES[s]["pv_min"] + STATES[s]["pv_max"] +
                         STATES[s]["dni_min"] + STATES[s]["dni_max"] +
                         STATES[s]["ghi_min"] + STATES[s]["ghi_max"]) / 6 for s in names}
    # finance: climate-budget coverage (normalized) + budget size (normalized), equal weight
    cb_n  = _minmax({s: STATES[s]["climate_budget"] for s in names})
    bud_n = _minmax({s: STATES[s]["state_budget"] for s in names})
    finance_score = {s: (cb_n[s] + bud_n[s]) / 2 for s in names}

    bank_raw      = {s: STATES[s]["infracredit"] for s in names}
    flood_raw     = {s: STATES[s]["flood_risk"] for s in names}
    # inclusive: HDI (mean of two sources) + womanity (mean of three) + women's health
    hdi_n  = _minmax({s: (STATES[s]["hdi_gdl"] + STATES[s]["hdi_undp"]) / 2 for s in names})
    wom_n  = _minmax({s: (STATES[s]["womanity_1"] + STATES[s]["womanity_2"] +
                          STATES[s]["womanity_3"]) / 3 for s in names})
    wh_n   = _minmax({s: STATES[s]["women_health"] for s in names})
    inclusive_score = {s: (hdi_n[s] + wom_n[s] + wh_n[s]) / 3 for s in names}

    policy_score     = _minmax(policy_raw)
    sectoral_score   = _minmax(sectoral_raw)
    bank_score       = _minmax(bank_raw)
    resilience_score = _minmax(flood_raw, invert=True)   # higher flood risk = worse

    results: Dict[str, Dict] = {}
    for s in names:
        p = {
            "policy":      round(policy_score[s], 1),
            "sectoral":    round(sectoral_score[s], 1),
            "finance":     round(finance_score[s], 1),
            "bankability": round(bank_score[s], 1),
            "resilience":  round(resilience_score[s], 1),
            "inclusive":   round(inclusive_score[s], 1),
        }
        agoi = sum(p[k] * config.PILLAR_WEIGHTS[k] for k in PILLARS)
        agoi = round(max(0.0, min(100.0, agoi)), 1)
        results[s] = {
            "state": s,
            **{f"pillar_{k}": v for k, v in p.items()},
            "agoi_score": agoi,
            "band": config.classify_band(agoi),
            "lat": STATES[s]["lat"], "lon": STATES[s]["lon"],
            "flood_risk": STATES[s]["flood_risk"],
            "solar_mean": round(sectoral_raw[s], 2),
            "infracredit": STATES[s]["infracredit"],
            "state_budget": STATES[s]["state_budget"],
        }

    # rank
    for i, s in enumerate(sorted(results, key=lambda x: -results[x]["agoi_score"]), start=1):
        results[s]["rank"] = i
    return results


def as_rows() -> List[Dict]:
    r = compute()
    return sorted(r.values(), key=lambda d: d["rank"])
