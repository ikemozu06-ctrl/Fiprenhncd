"""
AGOI™ ESG Platform — Streamlit MVP
Natural Eco Capital

Run locally:   streamlit run app/streamlit_app.py
"""
import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# Make the agoi package importable no matter where this file ends up in the repo.
# Walk upward from this file until we find a directory containing the `agoi` package.
def _bootstrap_agoi_path():
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):  # search up to 6 levels up
        if os.path.isdir(os.path.join(here, "agoi")) and \
           os.path.isfile(os.path.join(here, "agoi", "__init__.py")):
            if here not in sys.path:
                sys.path.insert(0, here)
            return
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    # Fallback: also add the immediate parent (original behaviour).
    fallback = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if fallback not in sys.path:
        sys.path.insert(0, fallback)

_bootstrap_agoi_path()

from agoi import config
from agoi.pipeline import run

# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AGOI™ ESG Platform — Natural Eco Capital",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#1F3864"
BLUE = "#2E75B6"
GREEN = "#1B6B35"

st.markdown(f"""
<style>
.main .block-container {{padding-top: 2rem; max-width: 1200px;}}
h1, h2, h3 {{color: {NAVY};}}
.agoi-hero {{
  background: linear-gradient(110deg, {NAVY} 0%, {BLUE} 100%);
  padding: 1.6rem 2rem; border-radius: 14px; color: #fff; margin-bottom: 1.2rem;
}}
.agoi-hero h1 {{color:#fff; margin:0; font-size:2.0rem;}}
.agoi-hero p {{color:#dce6f5; margin:.3rem 0 0 0;}}
.metric-card {{background:#f5f8fc; border-radius:12px; padding:1rem 1.2rem; border:1px solid #e1e8f2;}}
.band-pill {{display:inline-block; padding:.18rem .7rem; border-radius:999px; color:#fff; font-weight:600; font-size:.82rem;}}
.small-note {{color:#666; font-size:.83rem;}}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Data loading (cached). The mode is chosen in the sidebar.
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False, ttl=60 * 60)
def load_data(mode: str):
    scores, audit, meta = run(mode=mode)
    return scores, audit, meta


def band_pill(label: str) -> str:
    return f'<span class="band-pill" style="background:{config.band_colour(label)}">{label}</span>'


def data_badge(meta: dict):
    """
    Headline data-status banner. Demo and proxy data must be unmistakable (P1.1).
    Technical provenance sits in a collapsed expander.
    """
    mode = meta["data_mode"]
    if mode == "live":
        st.success(f"Live World Bank data · {meta['n_countries']} countries · "
                   f"{meta['n_indicators']} indicators", icon="✅")
    elif mode == "mix":
        st.error(
            "DEMONSTRATION DATA ACTIVE — some missing observations are filled with demo "
            "values. Do not use these results for investment or policy decisions.",
            icon="🚨")
    else:
        st.error(
            "OFFLINE DEMO ACTIVE — results are for demonstration only and are not real "
            "measurements. Do not use for investment or policy decisions.",
            icon="🚨")

    # Technical provenance — collapsed by default.
    with st.expander("🔎 Data provenance & technical details"):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**This scoring run**")
            st.markdown(
                f"- Run ID: `{meta.get('run_id','—')}`\n"
                f"- Run date: {meta.get('run_date','—')}\n"
                f"- Data mode: {mode}\n"
                f"- Countries scored: {meta.get('n_countries','—')}\n"
                f"- Indicators used: {meta.get('n_indicators','—')}"
            )
            st.caption("The run ID ties every score on this page to the exact data pull "
                       "behind it — quote it when citing a figure.")
        with c2:
            st.markdown("**Data connectors**")
            st.markdown("- World Bank (WDI / WGI): live public API, no key required")
            afdb_status = meta.get("afdb_status", "not run")
            if "live" in str(afdb_status).lower():
                st.markdown(f"- AfDB (IATI): ✅ {afdb_status}")
            else:
                st.markdown("- AfDB (IATI): ⚪ optional — not yet enabled")
                st.caption("AfDB project data is an optional enhancement to the Bankability "
                           "pillar. Everything else runs fully without it. "
                           "See 'Enabling AfDB data' in the README to switch it on.")
        if meta.get("note"):
            st.caption(f"Note: {meta['note']}")


# ──────────────────────────────────────────────────────────────────────────────
# Sidebar — data mode control, shared across pages via session_state.
# ──────────────────────────────────────────────────────────────────────────────
st.sidebar.markdown("### ⚙️ Data source")
MODE_LABELS = {
    "live": "Live World Bank only",
    "mixed": "Mixed — live data with demo-filled gaps",
    "demo": "Demo / offline",
}
mode = st.sidebar.radio(
    "Mode",
    options=list(MODE_LABELS),
    index=0,                       # LIVE IS THE DEFAULT (P1.1)
    format_func=MODE_LABELS.get,
    key="data_mode_choice",
    help="Live mode excludes synthetic and demo-filled values.",
)
# The pipeline still uses the internal name "mix"; map the UI value to it.
mode = "mix" if mode == "mixed" else mode
st.session_state["data_mode"] = mode

if st.sidebar.button("🔄 Refresh data (clear cache)"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<span class='small-note'>AGOI™ — Africa Green Opportunity Index<br>"
    "Natural Eco Capital · MVP build</span>", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# Hero
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="agoi-hero">
  <h1>🌍 AGOI™ ESG Platform</h1>
  <p>Africa Green Opportunity Index — investment-readiness scoring across 54 African countries,
  with full data provenance and confidence flags.</p>
</div>
""", unsafe_allow_html=True)

with st.spinner("Loading scores…"):
    scores, audit, meta = load_data(mode)

data_badge(meta)

# ── Headline metrics ──
c1, c2, c3, c4 = st.columns(4)
top = scores.iloc[0]
core_green = (scores["band"] == "Core Green Zone").sum()
growth_green = (scores["band"] == "Growth Green Zone").sum()
avg_cov = scores["data_coverage"].mean()

with c1:
    st.markdown(f"<div class='metric-card'><b>Top-ranked</b><br><span style='font-size:1.3rem;color:{GREEN}'>"
                f"{top['country']}</span><br>{top['agoi_score']:.1f} / 100</div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><b>Core Green Zone</b><br>"
                f"<span style='font-size:1.6rem;color:{GREEN}'>{core_green}</span> countries</div>",
                unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><b>Growth Green Zone</b><br>"
                f"<span style='font-size:1.6rem;color:{BLUE}'>{growth_green}</span> countries</div>",
                unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='metric-card'><b>Avg data coverage</b><br>"
                f"<span style='font-size:1.6rem;color:{NAVY}'>{avg_cov:.0f}%</span></div>",
                unsafe_allow_html=True)

st.markdown("### Continental ranking")

# ── Band filter ──
bands_present = [b[2] for b in config.BANDS if b[2] in scores["band"].unique()]
sel_bands = st.multiselect("Filter by opportunity band", bands_present, default=bands_present)
if sel_bands:
    view = scores[scores["band"].isin(sel_bands)].copy()
else:
    view = scores.copy()
    st.caption("No opportunity-band filter applied — showing all countries.")

if view.empty:
    st.warning("No countries match the selected opportunity bands.")
    st.stop()

# ── Ranking bar chart ──
fig = px.bar(
    view.sort_values("agoi_score"),
    x="agoi_score", y="country", orientation="h",
    color="band",
    color_discrete_map={b[2]: b[3] for b in config.BANDS},
    labels={"agoi_score": "AGOI score", "country": ""},
    height=max(400, 18 * len(view)),
)
fig.update_layout(margin=dict(l=0, r=10, t=10, b=0), legend_title="Band",
                  plot_bgcolor="white", yaxis=dict(tickfont=dict(size=11)))
st.plotly_chart(fig, use_container_width=True)

# ── Ranking table ──
st.markdown("#### Score table")
show = view[["rank", "country", "agoi_score", "band", "data_coverage"]].copy()
show.columns = ["Rank", "Country", "AGOI score", "Band", "Coverage %"]
st.dataframe(show, use_container_width=True, hide_index=True,
             column_config={
                 "AGOI score": st.column_config.ProgressColumn(
                     "AGOI score", min_value=0, max_value=100, format="%.1f"),
                 "Coverage %": st.column_config.NumberColumn("Coverage %", format="%.0f%%"),
             })

st.markdown("<span class='small-note'>Use the pages in the sidebar for country profiles, "
            "the Africa map, pillar comparison, the scenario tool and the audit trail.</span>",
            unsafe_allow_html=True)
