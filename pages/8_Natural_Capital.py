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
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from _shared import inject_css                       # noqa: E402
from agoi.natcap import assets as A                   # noqa: E402
from agoi.natcap import valuation as V                # noqa: E402
from agoi.natcap import fipre as F                     # noqa: E402

st.set_page_config(page_title="Natural Capital · AGOI™", page_icon="🌿", layout="wide")
inject_css()

st.title("🌿 Natural Capital — Map, Value, Screen")
st.caption("Locate ecological assets → price their ecosystem services → screen projects with FIPRE")

st.warning("🔬 **Framework with proxy data.** Asset magnitudes and valuations are "
           "order-of-magnitude figures from public literature, reported as **ranges**. "
           "They are honest planning figures, not audited reserves or price quotes. "
           "Replace with primary survey / biomass / geothermal-atlas data before "
           "underwriting. Every asset carries a provenance note.")

tab1, tab2, tab3 = st.tabs(["🗺️ Asset map", "💰 Valuation", "🎯 FIPRE screen"])

# ══════════════════════════════════════════════════════════
# TAB 1 — Spatial mapping & physical accounting
# ══════════════════════════════════════════════════════════
with tab1:
    st.markdown("#### Africa's ecological assets by ecosystem service")

    svc = st.radio("Colour the map by dominant service capacity",
                   ["regulating", "provisioning", "cultural"], horizontal=True,
                   format_func=lambda s: A.SERVICE_CATEGORIES[s]["label"])

    rows = []
    for a in A.ASSETS:
        rows.append({
            "Asset": a["name"], "Type": A.ASSET_TYPES[a["asset_type"]],
            "lat": a["lat"], "lon": a["lon"],
            "Service": a["services"][svc],
            "Countries": ", ".join(a["countries"]),
            "id": a["id"],
        })
    dfm = pd.DataFrame(rows)

    fig = px.scatter_geo(
        dfm, lat="lat", lon="lon", size="Service", color="Service",
        hover_name="Asset", scope="africa",
        color_continuous_scale=[[0, "#E0E0E0"], [0.5, A.SERVICE_CATEGORIES[svc]["color"]],
                                [1, "#0C2B2A"]],
        size_max=38, custom_data=["Type", "Countries"],
    )
    fig.update_traces(hovertemplate="<b>%{hovertext}</b><br>%{customdata[0]}<br>"
                                    "%{customdata[1]}<br>Service capacity: %{marker.size}<extra></extra>")
    fig.update_geos(showcountries=True, countrycolor="#D5E3E0", landcolor="#F5FAF9",
                    showframe=False)
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=0, b=0),
                      coloraxis_colorbar=dict(title=f"{A.SERVICE_CATEGORIES[svc]['label']}<br>capacity"))
    st.plotly_chart(fig, use_container_width=True)

    st.caption(f"**{A.SERVICE_CATEGORIES[svc]['label']} services** — "
               f"{A.SERVICE_CATEGORIES[svc]['examples']}")

    st.markdown("#### Asset register")
    reg = pd.DataFrame([{
        "Asset": a["name"], "Type": A.ASSET_TYPES[a["asset_type"]],
        "Countries": ", ".join(a["countries"]),
        "Provisioning": a["services"]["provisioning"],
        "Regulating": a["services"]["regulating"],
        "Cultural": a["services"]["cultural"],
        "Confidence": a["confidence"],
    } for a in A.ASSETS])
    st.dataframe(reg, hide_index=True, use_container_width=True)

    with st.expander("📋 Physical accounts & provenance (per asset)"):
        for a in A.ASSETS:
            phys = " · ".join(f"{k}: {v}" for k, v in a["physical"].items())
            st.markdown(f"**{a['name']}** — {phys}  \n"
                        f"<span style='color:#6A7B79;font-size:0.85rem'>Source: {a['source']}</span>",
                        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — Monetary valuation
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### From ecosystem services to investable value")
    st.caption("Shadow pricing + avoided-cost. Every figure is a **range** driven by the "
               "price assumptions below. Move them to test sensitivity.")

    with st.expander("⚙️ Price assumptions (policy inputs)"):
        cc = st.columns(3)
        carbon_mid = cc[0].slider("Carbon price (USD/tCO2e)", 5, 100, 15, 5)
        avoided_mid = cc[1].slider("Avoided cost (USD/ha-yr)", 100, 2000, 600, 100)
        disc = cc[2].slider("Discount rate (%)", 4, 15, 9, 1)
        # Apply overrides (keep the low/high spread proportional)
        V.PRICE_DRIVERS["carbon_usd_per_tco2e"] = (carbon_mid * 0.4, float(carbon_mid), carbon_mid * 2.5)
        V.PRICE_DRIVERS["avoided_cost_usd_per_ha_yr"] = (avoided_mid * 0.4, float(avoided_mid), avoided_mid * 2.5)
        V.PRICE_DRIVERS["discount_rate"] = (disc/100 * 0.7, disc/100, disc/100 * 1.3)

    asset_name = st.selectbox("Select an asset", [a["name"] for a in A.ASSETS])
    asset = next(a for a in A.ASSETS if a["name"] == asset_name)
    val = V.value_asset(asset)
    instruments = V.instrument_map()

    c1, c2 = st.columns(2)
    at, cap = val["annual_total"], val["capitalised_value"]
    c1.metric("Annual ecosystem-service value",
              f"{V.fmt_usd(at['low'])} – {V.fmt_usd(at['high'])}",
              help=f"Central estimate {V.fmt_usd(at['value'])}")
    c2.metric("Capitalised asset value",
              f"{V.fmt_usd(cap['low'])} – {V.fmt_usd(cap['high'])}",
              help="Annual flows capitalised at the discount rate")

    st.markdown("#### Value by service stream → investable instrument")
    stream_rows = []
    for key, band in val["streams"].items():
        stream_rows.append({
            "Service stream": V.SERVICE_VALUE_LABELS[key],
            "Annual value range": f"{V.fmt_usd(band['low'])} – {V.fmt_usd(band['high'])}",
            "Investable instrument": instruments[key],
        })
    st.dataframe(pd.DataFrame(stream_rows), hide_index=True, use_container_width=True)

    # Stacked range bar
    streams = val["streams"]
    labels = [V.SERVICE_VALUE_LABELS[k] for k in streams]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Low", y=labels, x=[streams[k]["low"] for k in streams],
                         orientation="h", marker_color="#B9CBC8"))
    fig.add_trace(go.Bar(name="Range to high", y=labels,
                         x=[streams[k]["high"] - streams[k]["low"] for k in streams],
                         base=[streams[k]["low"] for k in streams],
                         orientation="h", marker_color="#2E7D32", opacity=0.75))
    fig.update_layout(barmode="overlay", height=300, plot_bgcolor="white",
                      xaxis_title="Annual value (USD)", margin=dict(l=0, r=0, t=10, b=0),
                      showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════
# TAB 3 — FIPRE non-compensatory screen
# ══════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### FIPRE — non-compensatory project screen")
    st.info("**Non-compensatory:** a project must clear the threshold on **every** dimension. "
            "A strong score on one dimension cannot rescue a failing score on another — "
            "fail any one, and the project is screened out.")

    threshold = st.slider("Pass threshold (applies to every dimension)", 30, 80,
                          int(F.PASS_THRESHOLD), 5)

    src = st.radio("Score source", ["Derive from an asset", "Enter project scores"],
                   horizontal=True)

    if src == "Derive from an asset":
        an = st.selectbox("Asset", [a["name"] for a in A.ASSETS], key="fipre_asset")
        asset = next(a for a in A.ASSETS if a["name"] == an)
        scores = F.derive_from_asset(asset)
        st.caption("Proxy scores derived from the asset's service profile — override with "
                   "real project data in a live assessment.")
    else:
        scores = {}
        cols = st.columns(5)
        for col, dim in zip(cols, F.DIM_ORDER):
            scores[dim] = col.slider(F.FIPRE_DIMENSIONS[dim]["label"], 0, 100, 60, 5,
                                     key=f"f_{dim}", help=F.FIPRE_DIMENSIONS[dim]["guiding_q"])

    result = F.evaluate(scores, threshold=float(threshold))

    # Verdict banner
    if result["passed"]:
        st.success(f"✅ **PASS** — clears all five dimensions at ≥{threshold}. {result['note']}")
    else:
        st.error(f"⛔ **REJECTED** — {result['note']}")

    # Dimension bars, coloured by pass/fail
    dims = F.DIM_ORDER
    vals = [result["per_dim"][d]["score"] for d in dims]
    colors = ["#2E7D32" if result["per_dim"][d]["pass"] else "#C62828" for d in dims]
    fig = go.Figure(go.Bar(
        x=[F.FIPRE_DIMENSIONS[d]["label"] for d in dims], y=vals,
        marker_color=colors,
        text=[f"{v:.0f}" for v in vals], textposition="outside"))
    fig.add_hline(y=threshold, line_dash="dash", line_color="#0C2B2A",
                  annotation_text=f"Pass threshold ({threshold})", annotation_position="top left")
    fig.update_layout(height=360, plot_bgcolor="white", yaxis_range=[0, 105],
                      yaxis_title="Score (0–100)", margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # The five dimensions explained
    st.markdown("#### The five FIPRE dimensions")
    for d in dims:
        meta = F.FIPRE_DIMENSIONS[d]
        mark = "✅" if result["per_dim"][d]["pass"] else "⛔"
        st.markdown(f"{mark} **{meta['label']}** ({result['per_dim'][d]['score']:.0f}) — "
                    f"{meta['desc']}  \n"
                    f"<span style='color:#6A7B79;font-size:0.85rem'>{meta['guiding_q']}</span>",
                    unsafe_allow_html=True)
