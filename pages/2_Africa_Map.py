import os
import sys

import plotly.express as px
import streamlit as st

def _bootstrap_agoi_path():
    import os, sys
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
from _shared import get_data, inject_css   # noqa: E402
from agoi import config                     # noqa: E402

st.set_page_config(page_title="Africa map · AGOI™", page_icon="🗺️", layout="wide")
inject_css()
st.title("🗺️ Africa map")

scores, audit, meta = get_data()

metric = st.radio("Colour by", ["AGOI score", "Data coverage"], horizontal=True)
col = "agoi_score" if metric == "AGOI score" else "data_coverage"

fig = px.choropleth(
    scores,
    locations="country_iso3",
    color=col,
    hover_name="country",
    hover_data={"agoi_score": ":.1f", "band": True, "data_coverage": ":.0f",
                "country_iso3": False},
    color_continuous_scale=["#C62828", "#E58A00", "#FFC000", "#4CAF72", "#1B6B35"],
    range_color=(0, 100),
    scope="africa",
)
fig.update_geos(showframe=False, showcoastlines=False, projection_type="mercator",
                lataxis_range=[-37, 38], lonaxis_range=[-20, 55])
fig.update_layout(height=640, margin=dict(l=0, r=0, t=10, b=0),
                  coloraxis_colorbar=dict(title=metric))
st.plotly_chart(fig, use_container_width=True)

if meta["data_mode"] == "demo":
    st.warning("🟡 Showing DEMO data — not real measurements.")

st.markdown("<span class='small-note'>Hover a country for its score, band and data coverage. "
            "Use the Country profile page for the full breakdown and audit trail.</span>",
            unsafe_allow_html=True)
