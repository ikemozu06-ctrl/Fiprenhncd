import os
import sys

import plotly.graph_objects as go
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

st.set_page_config(page_title="Pillar comparison · AGOI™", page_icon="📊", layout="wide")
inject_css()
st.title("📊 Pillar comparison")

scores, audit, meta = get_data()
pillars = list(config.PILLAR_WEIGHTS.keys())
labels = [config.PILLAR_LABELS[p] for p in pillars]

default = scores["country"].head(3).tolist()
chosen = st.multiselect("Compare countries (up to 5)", scores["country"].tolist(),
                        default=default, max_selections=5)

if not chosen:
    st.info("Select at least one country.")
    st.stop()

radar = go.Figure()
palette = ["#1F3864", "#2E75B6", "#1B6B35", "#FFC000", "#C62828"]
for i, country in enumerate(chosen):
    row = scores[scores["country"] == country].iloc[0]
    vals = [row[f"pillar_{p}"] for p in pillars]
    radar.add_trace(go.Scatterpolar(
        r=vals + [vals[0]], theta=labels + [labels[0]],
        fill="toself", name=country, line_color=palette[i % len(palette)], opacity=0.6))
radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                    height=520, margin=dict(l=60, r=60, t=40, b=40))
st.plotly_chart(radar, use_container_width=True)

st.markdown("### Side-by-side")
comp = scores[scores["country"].isin(chosen)][
    ["country", "agoi_score"] + [f"pillar_{p}" for p in pillars]].copy()
comp.columns = ["Country", "AGOI"] + labels
st.dataframe(comp.set_index("Country").T, use_container_width=True)
