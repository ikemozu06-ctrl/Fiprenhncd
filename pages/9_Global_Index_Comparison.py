"""
AGOI in the Global Sustainability Landscape.

Implements the Global Index View / Africa-Centric View toggle.

IMPORTANT — SCOPE OF THIS PAGE
This is a QUALITATIVE POSITIONING page. It describes how AGOI relates
conceptually to other global indices (scope, focus, method style). It deliberately
contains NO numeric scores from GGGI, EPI, ND-GAIN, SDG Index or any other index.

That is a deliberate compliance choice: reproducing or deriving other indices'
scores requires licensed source data, attribution and an approved normalization
method. Until those approvals exist, this page compares FRAMEWORKS, not numbers.
Descriptions of other indices are drawn from their own public descriptions of
their scope and methodology.
"""
import os
import sys

def _bootstrap_agoi_path():
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        if os.path.isdir(os.path.join(here, "agoi")) and \
           os.path.isfile(os.path.join(here, "agoi", "__init__.py")):
            if here not in sys.path:
                sys.path.insert(0, here)
            return
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    for extra in (os.path.dirname(os.path.abspath(__file__)),
                  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
        if extra not in sys.path:
            sys.path.insert(0, extra)

_bootstrap_agoi_path()

import pandas as pd
import streamlit as st

from _shared import inject_css   # noqa: E402

st.set_page_config(page_title="Global Index Comparison · AGOI™", page_icon="🌐", layout="wide")
inject_css()

st.title("🌐 AGOI in the Global Sustainability Landscape")

view = st.radio(
    "Select view",
    ("Global Index View", "Africa-Centric View", "Plain-language explainer"),
    index=0,
    horizontal=True,
    help="Global view: how AGOI relates to international indices. "
         "Africa-Centric view: what makes AGOI distinct. "
         "Plain-language: a non-technical explanation.",
)

st.caption("This page compares **frameworks, not scores**. It contains no numeric values "
           "from other indices — those require licensed data and an approved normalization "
           "method before they could be shown.")

# ──────────────────────────────────────────────────────────────────────────────
# The comparison matrix — qualitative only.
# ──────────────────────────────────────────────────────────────────────────────
MATRIX = [
    {"Index": "GGGI Green Growth Index", "Scope": "Global",
     "Primary focus": "Green growth performance & enabling conditions",
     "Method style": "Composite index, normalized indicators",
     "Relation to AGOI": "High — closest conceptual counterpart",
     "Africa relevance": "Used by African governments; aligns with AGOI's policy-readiness signals"},
    {"Index": "Commonwealth Green Growth Index", "Scope": "Commonwealth countries",
     "Primary focus": "Enabling environment for green growth",
     "Method style": "Composite; governance & policy emphasis",
     "Relation to AGOI": "Medium–High — enabling-environment overlap",
     "Africa relevance": "Supports Africa–Asia benchmarking and the investibility narrative"},
    {"Index": "SDG Index (SDSN)", "Scope": "Global",
     "Primary focus": "SDG progress",
     "Method style": "Goal-based scoring",
     "Relation to AGOI": "Medium — AGOI uses SDG-aligned indicators",
     "Africa relevance": "Strong for civil society & academia; AGOI adds investment readiness"},
    {"Index": "Environmental Performance Index (EPI)", "Scope": "Global",
     "Primary focus": "Environmental outcomes",
     "Method style": "Outcome-based environmental metrics",
     "Relation to AGOI": "Medium — overlaps AGOI resilience & natural capital",
     "Africa relevance": "Useful to environment ministries; AGOI adds finance, policy, inclusion"},
    {"Index": "Global Green Finance Index (GGFI)", "Scope": "Global financial centres",
     "Primary focus": "Green finance depth & quality",
     "Method style": "Survey + data",
     "Relation to AGOI": "Medium–Low — AGOI is sovereign/subnational, not centre-based",
     "Africa relevance": "Useful to DFIs; AGOI provides sovereign-level de-risking signals"},
    {"Index": "Sovereign ESG ratings (e.g. MSCI, Sustainalytics)", "Scope": "Global",
     "Primary focus": "Sovereign ESG risk",
     "Method style": "Proprietary ESG scoring",
     "Relation to AGOI": "High (conceptual) — same ESG lens",
     "Africa relevance": "AGOI is open and Africa-specific; adds natural capital + AfCFTA corridors"},
    {"Index": "ND-GAIN Climate Vulnerability Index", "Scope": "Global",
     "Primary focus": "Climate vulnerability & readiness",
     "Method style": "Composite vulnerability metrics",
     "Relation to AGOI": "Medium — overlaps AGOI's resilience pillar",
     "Africa relevance": "Strong for climate ministries; AGOI adds opportunity & investibility"},
    {"Index": "Human Development Index (HDI)", "Scope": "Global",
     "Primary focus": "Human development",
     "Method style": "Simple composite",
     "Relation to AGOI": "Low–Medium — feeds the inclusion pillar",
     "Africa relevance": "AGOI integrates HDI-type signals into an ESG frame"},
    {"Index": "WEF Global Competitiveness Index", "Scope": "Global",
     "Primary focus": "Economic competitiveness",
     "Method style": "Multi-pillar composite",
     "Relation to AGOI": "Medium–Low — competitiveness enters indirectly",
     "Africa relevance": "Useful to investment promotion agencies; AGOI adds sustainability"},
    {"Index": "IMF Financial Development Index", "Scope": "Global",
     "Primary focus": "Financial system depth & access",
     "Method style": "Composite",
     "Relation to AGOI": "Medium–Low — overlaps AGOI's finance pillar",
     "Africa relevance": "Useful to DFIs; AGOI adds ESG and natural capital"},
    {"Index": "OECD Green Growth Indicators", "Scope": "OECD countries",
     "Primary focus": "Green growth",
     "Method style": "Indicator set",
     "Relation to AGOI": "Medium — conceptual alignment",
     "Africa relevance": "Benchmarking Africa vs OECD; AGOI is Africa-specific"},
    {"Index": "UNEP Inclusive Wealth Index", "Scope": "Global",
     "Primary focus": "Natural & produced capital",
     "Method style": "Wealth accounting",
     "Relation to AGOI": "Medium–High — aligns with AGOI's natural-capital module",
     "Africa relevance": "AGOI operationalizes natural capital for investment decisions"},
]

GAPS = [
    ("Natural capital value", "Africa's ecological assets priced as investable service flows"),
    ("AfCFTA corridor dynamics", "How continental trade policy reshapes green opportunity"),
    ("Subnational ESG realities", "State-level variation within countries, not just national averages"),
    ("Investment readiness", "Whether capital can actually be deployed, not just performance"),
    ("Bankable opportunity signals", "Where a specific, financeable project exists"),
]

# ──────────────────────────────────────────────────────────────────────────────
if view == "Global Index View":
    st.subheader("Global Index Comparison Matrix")
    st.markdown(
        "AGOI sits within a family of international indices — GGGI, the SDG Index, EPI, "
        "ND-GAIN, sovereign ESG ratings and others — that measure how countries perform on "
        "climate, development and governance. AGOI is **conceptually aligned** with these "
        "frameworks but is **Africa-specific and investment-focused**. It is designed to "
        "complement them, not replace them."
    )
    df = pd.DataFrame(MATRIX)
    st.dataframe(df, hide_index=True, use_container_width=True,
                 column_config={
                     "Index": st.column_config.TextColumn(width="medium"),
                     "Africa relevance": st.column_config.TextColumn(width="large"),
                 })
    st.caption("Descriptions summarise each index's own published scope and method. "
               "No scores from these indices are reproduced or derived here.")

elif view == "Africa-Centric View":
    st.subheader("Why Africa needs its own lens")
    st.markdown(
        "Global indices are valuable, but none capture Africa's full story. AGOI exists to "
        "fill that gap — reframing the continent's green economy narrative from "
        "**vulnerability to investibility**."
    )
    st.markdown("#### What global indices do not reflect")
    for title, desc in GAPS:
        st.markdown(f"- **{title}** — {desc}")

    st.markdown("#### What AGOI adds")
    c1, c2, c3 = st.columns(3)
    c1.metric("Countries scored", "54", help="Every African sovereign")
    c2.metric("Nigeria subnational", "36 + FCT", help="State-level ESG scoring")
    c3.metric("Analytical pillars", "6", help="Policy, Sectoral, Finance, Bankability, Resilience, Inclusion")

    st.markdown(
        "AGOI supports investors, DFIs, governments, corporates, civil society and academia "
        "with a continent-specific, multi-layered ESG intelligence engine — helping translate "
        "global climate finance commitments into bankable African projects."
    )
    st.info("**On the $1.3 trillion figure:** the goal of scaling climate finance to "
            "USD 1.3 trillion per year by 2035 originates in the COP29 New Collective "
            "Quantified Goal and the associated Baku-to-Belém roadmap, carried forward at "
            "COP30. Cite it with that attribution rather than to a single COP.", icon="ℹ️")

else:  # Plain-language explainer
    st.subheader("Understanding the two views")
    st.markdown("""
**🌍 Global Index View** — shows how AGOI relates to major international indices. Useful if
you want to understand how Africa compares with other regions, how global institutions
measure progress, and where AGOI aligns with international practice.

**🌍 Africa-Centric View** — focuses on what matters most for Africa: shifting the story from
**vulnerability** to **investibility**, highlighting Africa's natural wealth, people and
opportunities, and showing where real investment can make a difference.

**Why both matter** — global indices help us understand the world; Africa-centric insight
helps Africa understand and present itself. AGOI brings both together so Africa can speak
confidently in global forums while focusing on the opportunities that matter most at home.
    """)
    st.caption("This view is written for citizens, students, journalists and policymakers.")
