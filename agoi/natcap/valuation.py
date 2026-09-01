"""
Natural Capital — monetary valuation (Part 2).

Translates physical ecosystem-service accounts into the financial metrics DFIs
and private investors can actually underwrite: carbon-credit value, avoided-cost
value (e.g. a wetland priced as the water-treatment / flood-wall plant it makes
unnecessary), resource rents, and ecotourism revenue potential.

═══════════════════════════════════════════════════════════════════════════════
THIS IS A VALUATION FRAMEWORK, NOT A PRICE QUOTE
Every price driver below (carbon price, avoided-cost unit rates, resource rents)
is a POLICY ASSUMPTION with an explicit range. The engine propagates the range,
so every valuation is reported as a BAND, never a single figure. A wetland
"worth USD 40–120 M on an avoided-cost basis" is a defensible planning figure;
"worth USD 78.4 M" is false precision that an investor's analyst will dismiss.

All unit prices live here in one place so they can be updated as a policy input
rather than edited in code throughout.
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Dict

from agoi.natcap import assets as A

# ──────────────────────────────────────────────────────────────────────────────
# Price drivers — (low, central, high). Update as policy inputs.
# ──────────────────────────────────────────────────────────────────────────────
PRICE_DRIVERS = {
    # Carbon price, USD per tonne CO2e. Voluntary vs compliance spread is wide.
    "carbon_usd_per_tco2e": (5.0, 15.0, 50.0),
    # Avoided-cost: USD per hectare-year of regulating service (flood/water/soil).
    "avoided_cost_usd_per_ha_yr": (150.0, 600.0, 2000.0),
    # Ecotourism: USD per year per point of cultural-service score, per major asset.
    "ecotourism_usd_per_point_yr": (50_000.0, 250_000.0, 900_000.0),
    # Resource rent capture: fraction of provisioning value realised locally.
    "resource_rent_capture": (0.10, 0.25, 0.45),
    # Discount rate for capitalising annual flows into an asset value.
    "discount_rate": (0.06, 0.09, 0.12),
}

SERVICE_VALUE_LABELS = {
    "carbon_value":     "Carbon sequestration value",
    "avoided_cost":     "Avoided-cost (regulating services)",
    "ecotourism_value": "Ecotourism revenue potential",
    "provisioning_rent":"Provisioning resource rent",
}


def _band(lo, mid, hi):
    return {"low": round(lo, 1), "value": round(mid, 1), "high": round(hi, 1)}


def _capitalise(annual_lo, annual_mid, annual_hi) -> Dict:
    """Turn an annual flow band into a capitalised asset-value band (flow / r)."""
    r_lo, r_mid, r_hi = PRICE_DRIVERS["discount_rate"]
    # Lowest value = lowest flow at highest discount; highest = highest flow / lowest r.
    return _band(annual_lo / r_hi, annual_mid / r_mid, annual_hi / r_lo)


def value_asset(asset: Dict) -> Dict:
    """
    Produce a monetary valuation for one asset. Returns annual-flow bands per
    service stream plus a capitalised total-value band. All figures in USD.
    Magnitudes are illustrative planning figures driven by the asset's 0–100
    service-capacity scores and the PRICE_DRIVERS ranges.
    """
    services = asset["services"]

    # --- Carbon value (annual) — scales with regulating capacity ---
    c_lo, c_mid, c_hi = PRICE_DRIVERS["carbon_usd_per_tco2e"]
    # Proxy: regulating score -> notional annual sequestration units (1 pt = 100k tCO2e/yr).
    seq_units = services["regulating"] * 100_000
    carbon = _band(seq_units * c_lo, seq_units * c_mid, seq_units * c_hi)

    # --- Avoided cost (annual) — regulating capacity as hectare-equivalent buffer ---
    a_lo, a_mid, a_hi = PRICE_DRIVERS["avoided_cost_usd_per_ha_yr"]
    ha_equiv = services["regulating"] * 10_000   # 1 pt = 10k ha-equivalent of buffer
    avoided = _band(ha_equiv * a_lo, ha_equiv * a_mid, ha_equiv * a_hi)

    # --- Ecotourism (annual) — scales with cultural capacity ---
    e_lo, e_mid, e_hi = PRICE_DRIVERS["ecotourism_usd_per_point_yr"]
    eco = _band(services["cultural"] * e_lo, services["cultural"] * e_mid,
                services["cultural"] * e_hi)

    # --- Provisioning rent (annual) — provisioning capacity x captured rent ---
    rr_lo, rr_mid, rr_hi = PRICE_DRIVERS["resource_rent_capture"]
    # 1 provisioning pt = USD 2M gross provisioning value (proxy), rent-captured.
    gross = services["provisioning"] * 2_000_000
    rent = _band(gross * rr_lo, gross * rr_mid, gross * rr_hi)

    annual_lo = carbon["low"] + avoided["low"] + eco["low"] + rent["low"]
    annual_mid = carbon["value"] + avoided["value"] + eco["value"] + rent["value"]
    annual_hi = carbon["high"] + avoided["high"] + eco["high"] + rent["high"]

    return {
        "asset_id": asset["id"],
        "streams": {
            "carbon_value": carbon,
            "avoided_cost": avoided,
            "ecotourism_value": eco,
            "provisioning_rent": rent,
        },
        "annual_total": _band(annual_lo, annual_mid, annual_hi),
        "capitalised_value": _capitalise(annual_lo, annual_mid, annual_hi),
        "confidence": asset.get("confidence", A.CONF_PROXY),
    }


def fmt_usd(x: float) -> str:
    """Human-readable USD with magnitude suffix."""
    if x >= 1e9:
        return f"${x/1e9:,.1f}B"
    if x >= 1e6:
        return f"${x/1e6:,.1f}M"
    if x >= 1e3:
        return f"${x/1e3:,.0f}K"
    return f"${x:,.0f}"


def instrument_map() -> Dict[str, str]:
    """How each valuation stream maps to an investable instrument (for the UI)."""
    return {
        "carbon_value":      "Carbon credits / REDD+ / Article 6 ITMOs",
        "avoided_cost":      "Resilience bonds / blended-finance guarantees",
        "ecotourism_value":  "Concession revenue / conservation-linked notes",
        "provisioning_rent": "Sustainable resource royalties / green bonds",
    }
