"""
Nigeria subnational data — REAL, SOURCED (36 states + FCT).

This module replaces the synthetic state model that was flagged as a defect in
Technical Manual v1.0 (Appendix B, item 4). Every column below comes from a
named, citable source supplied in the NEC "FIPRE Dashboard WIP" workbook.

SOURCES
  policy_gov      Subnational Climate Governance Performance Ranking — SPP Nigeria
                  https://sppnigeria.org/subnational-climate-governance-performance-ranking-report/
  pv_min/pv_max   Specific photovoltaic power output (kWh/kWp) — Global Solar Atlas
  dni_min/dni_max Direct normal irradiation (kWh/m2) — Global Solar Atlas
  ghi_min/ghi_max Global horizontal irradiation (kWh/m2) — Global Solar Atlas
  climate_budget  State coverage on climate budgeting/finance — SPP Nigeria
  flood_risk      Flood risk indicator, 1–3 (3 = highest risk) — Longdom
  hdi_gdl         Subnational HDI — Global Data Lab
  hdi_undp        Subnational HDI — UNDP Nigeria HDR 2018
  women_health    Women's investment in reproductive decision-making — Invictus Africa
  womanity_1/2/3  Womanity Index 2025 — Invictus Africa
  infracredit     Climate facility projects — InfraCredit
  state_budget    State budget (NGN)

═══════════════════════════════════════════════════════════════════════════════
DATA-QUALITY EXCLUSION — READ THIS
The workbook's two "Bankability – Fiscal Performance Ranking" columns (BudgIT
2022 and 2023) are NOT used. Their values rise strictly monotonically in
alphabetical order of state (Abia 0.474 → Zamfara 2.561). Fiscal performance has
no relationship to the alphabet, so the column was evidently sorted independently
of the state labels and the values are misaligned with their states. Wiring them
in would have made Zamfara Nigeria's best-run state and Abia its worst.

They are therefore EXCLUDED pending a corrected source. Bankability is proxied by
InfraCredit climate-facility project counts, flagged confidence="proxy".
Re-enable the fiscal columns only once a correctly-aligned source is supplied.
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations
from typing import Dict, List

CONF_MEASURED = "measured"
CONF_PROXY    = "proxy"

# state: (policy_gov, pv_min, pv_max, dni_min, dni_max, ghi_min, ghi_max,
#         climate_budget, flood_risk, hdi_gdl, hdi_undp, women_health,
#         womanity_1, womanity_2, womanity_3, infracredit, state_budget_ngn)
_RAW = {
"Abia":       (106,3.44,3.75,1.98,2.39,4.35,4.74,15,2,0.674,0.541,66.1,59.8,60.4,52.9,3,1.02e12),
"Adamawa":    (98,4.29,4.79,3.63,4.74,5.43,5.96,5,3,0.539,0.429,55.2,59.5,70.0,58.8,6,583.3e9),
"Akwa Ibom":  (64,3.38,3.64,1.92,2.28,4.26,4.61,5,2,0.602,0.564,64.1,71.8,72.9,80.0,23.7,1.58e12),
"Anambra":    (101,3.66,3.81,2.22,2.53,4.64,4.84,5,1,0.706,0.471,55.2,61.4,50.0,53.3,5,757.9e9),
"Bauchi":     (79,4.40,4.77,3.78,4.46,5.60,6.00,15,1,0.372,0.323,9.4,56.1,55.4,58.8,20,877e9),
"Bayelsa":    (100,3.33,3.69,1.81,2.34,4.18,4.67,5,1,0.573,0.591,50.5,64.2,56.7,65.8,3,1.02e12),
"Benue":      (60,3.82,4.18,2.54,3.22,4.85,5.31,5,1,0.582,0.462,34.5,36.9,50.0,54.2,30,695e9),
"Borno":      (115,4.51,4.76,4.10,4.57,5.76,6.05,15,1,0.464,0.328,34.9,56.4,59.2,67.5,2,892.4e9),
"Cross River":(67,3.49,4.13,2.00,3.13,4.40,5.19,15,1,0.675,0.551,66.2,50.4,59.2,68.8,51,961.6e9),
"Delta":      (100,3.44,3.77,1.96,2.45,4.33,4.79,15,1,0.607,0.556,73.8,66.4,72.1,66.3,3,1.73e12),
"Ebonyi":     (125,3.65,3.86,2.26,2.61,4.64,4.91,15,2,0.622,0.434,43.9,50.1,66.7,65.8,8,884.9e9),
"Edo":        (112,3.55,3.94,2.06,2.68,4.47,4.97,15,1,0.633,0.530,78.3,66.8,72.5,66.3,6,939.9e9),
"Ekiti":      (115,3.78,4.05,2.40,2.88,4.75,5.11,5,2,0.612,0.561,66.2,74.8,75.4,72.1,5,415.6e9),
"Enugu":      (85,3.67,3.89,2.26,2.63,4.66,4.92,15,2,0.667,0.541,70.7,56.8,45.8,60.8,2,1.62e12),
"Gombe":      (128,4.45,4.73,3.92,4.42,5.65,5.95,22,1,0.466,0.401,13.9,39.5,49.6,65.0,23,618e9),
"Imo":        (65,3.59,3.72,2.13,2.33,4.54,4.70,5,1,0.693,0.518,59.4,52.5,51.7,50.0,4,1.44e12),
"Jigawa":     (52,4.66,4.79,4.20,4.45,5.89,6.05,15,3,0.371,0.360,8.0,36.9,62.9,60.8,75,901.8e9),
"Kaduna":     (93,4.17,4.72,3.21,4.26,5.25,5.92,15,1,0.545,0.404,10.0,51.4,65.4,62.1,102,985.9e9),
"Kano":       (45,4.63,4.77,4.14,4.40,5.83,6.00,15,3,0.482,0.359,6.6,39.5,50.4,55.0,94,1.48e12),
"Katsina":    (64,4.63,4.81,4.08,4.52,5.81,6.07,5,2,0.431,0.303,6.0,32.3,55.0,50.0,44,897.9e9),
"Kebbi":      (56,4.29,4.66,3.32,4.25,5.42,5.92,15,2,0.366,0.382,2.5,29.7,64.2,57.9,8,642.9e9),
"Kogi":       (83,3.74,4.08,2.39,2.98,4.76,5.19,15,2,0.625,0.451,47.1,53.3,65.0,54.6,57,820.5e9),
"Kwara":      (103,3.86,4.29,2.54,3.37,4.88,5.44,15,1,0.597,0.511,35.1,56.8,70.8,69.6,24,656.6e9),
"Lagos":      (182,3.49,3.92,2.00,2.75,4.40,4.93,15,3,0.721,0.652,60.3,82.4,90.8,91.2,7,4.24e12),
"Nasarawa":   (53,3.97,4.26,2.80,3.37,5.05,5.37,5,1,0.549,0.506,24.4,53.3,54.2,52.1,41,545.2e9),
"Niger":      (112,4.02,4.46,2.88,3.75,5.12,5.65,15,3,0.523,0.399,5.8,52.9,72.5,67.1,43,1.07e12),
"Ogun":       (104,3.52,3.77,2.05,2.43,4.45,4.77,15,2,0.569,0.549,64.5,66.8,71.7,65.0,10,1.67e12),
"Ondo":       (72,3.56,3.97,2.07,2.73,4.48,5.01,5,2,0.611,0.500,40.5,56.8,68.3,62.1,22,524.4e9),
"Osun":       (57,3.62,3.92,2.13,2.62,4.56,4.93,5,2,0.607,0.512,71.2,53.3,58.8,58.3,1,723.4e9),
"Oyo":        (46,3.63,4.12,2.15,3.02,4.58,5.21,5,1,0.603,0.440,59.9,53.3,50.0,50.0,10,892e9),
"Plateau":    (60,4.14,4.80,3.20,4.54,5.26,5.93,5,1,0.563,0.463,44.0,42.3,51.7,57.1,4,914.9e9),
"Rivers":     (59,3.38,3.75,1.91,2.42,4.26,4.76,5,2,0.601,0.542,80.9,64.6,74.2,65.0,51,1.85e12),
"Sokoto":     (87,4.47,4.74,3.82,4.41,5.69,6.01,15,1,0.397,0.291,5.1,64.5,56.3,63.3,17,758.7e9),
"Taraba":     (85,4.08,4.63,3.07,4.29,5.18,5.80,15,1,0.527,0.461,20.8,54.2,55.8,56.7,14,653.5e9),
"Yobe":       (100,4.57,4.79,4.15,4.54,5.82,6.08,15,1,0.439,0.325,7.9,56.4,71.7,67.5,4,515.5e9),
"Zamfara":    (35,4.43,4.74,3.68,4.37,5.59,5.99,5,2,0.392,0.339,5.9,32.3,49.2,47.5,10,871.3e9),
"FCT":        (85.2,3.98,4.25,2.81,3.28,5.04,5.32,11.0,2,0.678,0.629,51.4,64.3,42.1,55.8,45,2.29e12),
}

FIELDS = ["policy_gov","pv_min","pv_max","dni_min","dni_max","ghi_min","ghi_max",
          "climate_budget","flood_risk","hdi_gdl","hdi_undp","women_health",
          "womanity_1","womanity_2","womanity_3","infracredit","state_budget"]

# Approximate state centroids for mapping.
CENTROIDS = {
"Abia":(5.45,7.52),"Adamawa":(9.33,12.40),"Akwa Ibom":(5.01,7.85),"Anambra":(6.22,6.94),
"Bauchi":(10.31,9.84),"Bayelsa":(4.77,6.07),"Benue":(7.33,8.75),"Borno":(11.88,13.15),
"Cross River":(5.87,8.60),"Delta":(5.71,5.93),"Ebonyi":(6.26,8.09),"Edo":(6.63,5.93),
"Ekiti":(7.72,5.31),"Enugu":(6.53,7.51),"Gombe":(10.29,11.17),"Imo":(5.57,7.06),
"Jigawa":(12.23,9.56),"Kaduna":(10.37,7.71),"Kano":(11.75,8.52),"Katsina":(12.38,7.62),
"Kebbi":(11.49,4.24),"Kogi":(7.73,6.69),"Kwara":(8.97,4.39),"Lagos":(6.52,3.38),
"Nasarawa":(8.50,8.20),"Niger":(9.93,5.60),"Ogun":(6.99,3.47),"Ondo":(7.10,4.84),
"Osun":(7.56,4.52),"Oyo":(8.16,3.61),"Plateau":(9.22,9.52),"Rivers":(4.86,6.92),
"Sokoto":(13.06,5.24),"Taraba":(7.99,10.77),"Yobe":(12.29,11.44),"Zamfara":(12.17,6.66),
"FCT":(9.06,7.49),
}

STATES: Dict[str, Dict] = {
    name: dict(zip(FIELDS, vals)) for name, vals in _RAW.items()
}
for _n, _d in STATES.items():
    _d["lat"], _d["lon"] = CENTROIDS[_n]

# Source citations surfaced in the UI.
SOURCES = {
 "policy_gov":     ("Subnational Climate Governance Performance Ranking", "SPP Nigeria", CONF_MEASURED),
 "solar":          ("Specific PV output / DNI / GHI", "Global Solar Atlas", CONF_MEASURED),
 "climate_budget": ("State coverage on climate budgeting & finance", "SPP Nigeria", CONF_MEASURED),
 "flood_risk":     ("Flood risk indicator (1–3, 3 = highest)", "Longdom flood-risk study", CONF_MEASURED),
 "hdi":            ("Subnational Human Development Index", "Global Data Lab / UNDP HDR 2018", CONF_MEASURED),
 "womanity":       ("Womanity Index 2025 & women's health index", "Invictus Africa", CONF_MEASURED),
 "infracredit":    ("Climate-facility project count (Bankability proxy)", "InfraCredit", CONF_PROXY),
 "state_budget":   ("State budget (NGN)", "State appropriation records", CONF_MEASURED),
}

EXCLUDED_COLUMNS = [
 ("Bankability – Fiscal Performance Ranking 2022 (BudgIT)",
  "EXCLUDED: values rise monotonically in alphabetical order of state, indicating "
  "the column was sorted independently of the state labels and is misaligned."),
 ("Bankability – Fiscal Performance Ranking 2023 (BudgIT)",
  "EXCLUDED: same misalignment as the 2022 column."),
]


def state_names() -> List[str]:
    return sorted(STATES.keys())
