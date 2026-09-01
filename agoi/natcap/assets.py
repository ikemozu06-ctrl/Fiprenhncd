"""
Natural Capital — asset registry (spatial mapping & physical accounting).

Part 1 of Dr. Itua's natural-capital layer: locate and quantify Africa's
ecological assets, then classify what ECOSYSTEM SERVICES each provides
(provisioning / regulating / cultural) rather than just raw stock.

═══════════════════════════════════════════════════════════════════════════════
PROVENANCE DISCIPLINE (carried from the rest of the platform)
The physical quantities below (carbon stock, geothermal potential, mineral
reserves, water yield) are REAL in the sense that they name real assets at real
locations, but the numeric magnitudes are PROXY / order-of-magnitude figures
drawn from public literature, not live measurement. Every asset carries a
`confidence` flag and a `source` note. They are honest starting points for a
map and a valuation engine — they are NOT audited reserve figures and must not
be presented as such to an investor without replacement by primary data
(national geological surveys, GEDI/biomass products, IRENA geothermal atlases,
Ramsar wetland inventories, etc.).
═══════════════════════════════════════════════════════════════════════════════

Ecosystem-service taxonomy (Millennium Ecosystem Assessment style):
  provisioning : timber, critical minerals, fresh water, food
  regulating   : carbon sequestration, flood mitigation, soil retention
  cultural     : ecotourism, biodiversity/heritage value
"""
from __future__ import annotations
from typing import Dict, List

# Confidence flags (shared vocabulary with the core platform).
CONF_MEASURED = "measured"
CONF_PROXY    = "proxy"
CONF_DEFAULT  = "default"

# Ecosystem-service categories.
SERVICE_CATEGORIES = {
    "provisioning": {"label": "Provisioning", "examples": "Timber, critical minerals, fresh water, food",
                     "color": "#2E7D32"},
    "regulating":   {"label": "Regulating", "examples": "Carbon sequestration, flood mitigation, soil retention",
                     "color": "#1565C0"},
    "cultural":     {"label": "Cultural", "examples": "Ecotourism, biodiversity & heritage value",
                     "color": "#B7791F"},
}

# Asset types.
ASSET_TYPES = {
    "forest":     "Forest / carbon sink",
    "geothermal": "Geothermal corridor",
    "mineral":    "Critical-mineral reserve",
    "wetland":    "Wetland / water regulation",
    "watershed":  "Watershed / freshwater",
    "marine":     "Coastal / marine",
}

# ──────────────────────────────────────────────────────────────────────────────
# The asset registry. Each asset:
#   id, name, country_iso3(s), asset_type, lat, lon,
#   services: {provisioning, regulating, cultural}  each 0–100 service-capacity
#   physical: dict of headline physical quantities (with units in the value string)
#   confidence, source
# Service-capacity scores are 0–100 relative indices, NOT physical units — they
# feed the valuation and FIPRE layers. Physical quantities are kept separately.
# ──────────────────────────────────────────────────────────────────────────────
ASSETS: List[Dict] = [
    # ---- Flagship: Congo Basin ----
    {"id": "CONGO_BASIN", "name": "Congo Basin Rainforest",
     "countries": ["COD", "COG", "CMR", "GAB", "CAF", "GNQ"], "asset_type": "forest",
     "lat": -0.5, "lon": 22.0,
     "services": {"provisioning": 78, "regulating": 96, "cultural": 88},
     "physical": {"area": "~180 million ha", "carbon_stock": "~30 Gt C (proxy)",
                  "annual_sequestration": "~0.6 Gt CO2e/yr (proxy)"},
     "confidence": CONF_PROXY,
     "source": "Order-of-magnitude from published Congo Basin carbon literature. "
               "Replace with GEDI/biomass products + national forest inventories."},

    # ---- Flagship: East African Rift geothermal ----
    {"id": "RIFT_GEOTHERMAL", "name": "East African Rift Geothermal Corridor",
     "countries": ["KEN", "ETH", "TZA", "RWA", "DJI"], "asset_type": "geothermal",
     "lat": 0.5, "lon": 36.0,
     "services": {"provisioning": 92, "regulating": 40, "cultural": 35},
     "physical": {"estimated_potential": "~15,000 MW (proxy)",
                  "installed_capacity": "~0.9 GW (Kenya-led, proxy)"},
     "confidence": CONF_PROXY,
     "source": "Rift geothermal potential from IRENA/regional estimates. "
               "Replace with national geothermal resource assessments."},

    # ---- Nigeria assets (ties to existing sub-national work) ----
    {"id": "NIGER_DELTA", "name": "Niger Delta Wetlands & Mangroves",
     "countries": ["NGA"], "asset_type": "wetland", "lat": 4.8, "lon": 6.0,
     "services": {"provisioning": 70, "regulating": 90, "cultural": 62},
     "physical": {"mangrove_area": "~10,000 km² (proxy)",
                  "flood_buffer_value": "high (avoided-cost basis)"},
     "confidence": CONF_PROXY,
     "source": "Niger Delta mangrove extent from Ramsar/NEMA-style sources. "
               "Replace with primary wetland inventory."},

    {"id": "LAKE_CHAD", "name": "Lake Chad Basin",
     "countries": ["NGA", "TCD", "NER", "CMR"], "asset_type": "watershed",
     "lat": 13.0, "lon": 14.0,
     "services": {"provisioning": 66, "regulating": 72, "cultural": 45},
     "physical": {"basin_area": "~2.4 million km² (proxy)",
                  "note": "Severe shrinkage since 1960s — climate-stressed"},
     "confidence": CONF_PROXY,
     "source": "Lake Chad basin figures from LCBC/UNEP literature (proxy)."},

    # ---- Critical minerals ----
    {"id": "DRC_COBALT", "name": "DRC Copper–Cobalt Belt",
     "countries": ["COD", "ZMB"], "asset_type": "mineral", "lat": -10.7, "lon": 26.5,
     "services": {"provisioning": 98, "regulating": 20, "cultural": 15},
     "physical": {"cobalt_share": "~70% of global cobalt supply (proxy)",
                  "transition_relevance": "battery / EV supply chain"},
     "confidence": CONF_PROXY,
     "source": "Global cobalt share widely reported; reserve tonnage requires "
               "national geological survey data to state precisely."},

    {"id": "SA_PGM", "name": "Bushveld Platinum-Group Metals Complex",
     "countries": ["ZAF"], "asset_type": "mineral", "lat": -25.0, "lon": 27.5,
     "services": {"provisioning": 95, "regulating": 22, "cultural": 18},
     "physical": {"pgm_share": "~75% of global PGM reserves (proxy)",
                  "transition_relevance": "hydrogen / fuel-cell catalysts"},
     "confidence": CONF_PROXY,
     "source": "Bushveld PGM dominance widely reported (proxy magnitude)."},

    # ---- West / ECOWAS slice assets ----
    {"id": "UPPER_GUINEA", "name": "Upper Guinean Forests",
     "countries": ["CIV", "GHA", "LBR", "GIN"], "asset_type": "forest",
     "lat": 6.5, "lon": -6.0,
     "services": {"provisioning": 68, "regulating": 80, "cultural": 74},
     "physical": {"status": "biodiversity hotspot, heavily fragmented",
                  "carbon_relevance": "moderate-high (proxy)"},
     "confidence": CONF_PROXY,
     "source": "Upper Guinean forest hotspot status from CEPF/IUCN (proxy)."},

    {"id": "VOLTA_BASIN", "name": "Volta River Basin",
     "countries": ["GHA", "BFA", "TGO", "BEN", "CIV", "MLI"], "asset_type": "watershed",
     "lat": 9.0, "lon": -1.0,
     "services": {"provisioning": 72, "regulating": 68, "cultural": 40},
     "physical": {"basin_area": "~400,000 km² (proxy)",
                  "hydropower_relevance": "Akosombo / regional hydro"},
     "confidence": CONF_PROXY,
     "source": "Volta basin figures from VBA/literature (proxy)."},

    # ---- Coastal / marine ----
    {"id": "BENGUELA", "name": "Benguela Current Marine Ecosystem",
     "countries": ["NAM", "ZAF", "AGO"], "asset_type": "marine",
     "lat": -25.0, "lon": 13.5,
     "services": {"provisioning": 85, "regulating": 60, "cultural": 55},
     "physical": {"fishery_value": "major upwelling fishery (proxy)",
                  "blue_carbon_relevance": "moderate"},
     "confidence": CONF_PROXY,
     "source": "Benguela upwelling productivity from BCC/FAO literature (proxy)."},

    {"id": "OKAVANGO", "name": "Okavango Delta",
     "countries": ["BWA", "NAM", "AGO"], "asset_type": "wetland",
     "lat": -19.3, "lon": 22.8,
     "services": {"provisioning": 55, "regulating": 82, "cultural": 95},
     "physical": {"status": "UNESCO World Heritage, premier ecotourism asset",
                  "area": "~15,000 km² seasonal (proxy)"},
     "confidence": CONF_PROXY,
     "source": "Okavango ecotourism/heritage status well established (proxy)."},
]


def assets_by_country(iso3: str) -> List[Dict]:
    return [a for a in ASSETS if iso3 in a["countries"]]


def get_asset(asset_id: str) -> Dict:
    for a in ASSETS:
        if a["id"] == asset_id:
            return a
    return {}


def all_countries_with_assets() -> List[str]:
    s = set()
    for a in ASSETS:
        s.update(a["countries"])
    return sorted(s)
