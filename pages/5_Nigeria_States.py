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

from _shared import inject_css                        # noqa: E402
from agoi import config                                # noqa: E402
from agoi.nigeria import states as NS                  # noqa: E402
from agoi.nigeria.index import as_rows, PILLARS        # noqa: E402

st.set_page_config(page_title="Nigeria States · AGOI™", page_icon="🇳🇬", layout="wide")
inject_css()

st.title("🇳🇬 AGOI State Dashboard")
st.caption("36 states + FCT scored on the six AGOI pillars — from real, cited subnational data")

st.success("Real sourced data — SPP Nigeria, Global Solar Atlas, Global Data Lab/UNDP, "
           "Invictus Africa, InfraCredit.", icon="✅")

rows = as_rows()
df = pd.DataFrame(rows)

tab1, tab2, tab3 = st.tabs(["🗺️ Map & ranking", "🏛️ State profile", "📋 Sources & data quality"])

# ══════════════════════════════════════════════════════
with tab1:
    metric = st.radio("Colour by", ["agoi_score"] + [f"pillar_{p}" for p in PILLARS],
                      horizontal=True,
                      format_func=lambda m: "AGOI score" if m == "agoi_score"
                      else config.PILLAR_LABELS[m.replace("pillar_", "")])

    c1, c2 = st.columns([1.15, 1])
    with c1:
        fig = px.scatter_geo(
            df, lat="lat", lon="lon", color=metric, size="agoi_score",
            hover_name="state", scope="africa", size_max=26,
            color_continuous_scale=[[0,"#C62828"],[0.35,"#E58A00"],[0.6,"#FFC000"],
                                    [0.8,"#4CAF72"],[1,"#1B6B35"]],
            hover_data={"agoi_score":":.1f","band":True,"flood_risk":True,
                        "lat":False,"lon":False},
        )
        fig.update_geos(lataxis_range=[3.5,14.5], lonaxis_range=[2,15],
                        showcountries=True, countrycolor="#C9DAD7",
                        landcolor="#F5FAF9", showframe=False)
        fig.update_layout(height=520, margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Ranking")
        show = df[["rank","state","agoi_score","band"]].copy()
        show.columns = ["#","State","AGOI","Band"]
        st.dataframe(show, hide_index=True, use_container_width=True, height=500,
                     column_config={"AGOI": st.column_config.ProgressColumn(
                         "AGOI", min_value=0, max_value=100, format="%.1f")})

    b1,b2,b3,b4 = st.columns(4)
    b1.metric("Regions scored", len(df))
    b2.metric("Highest", f"{df.iloc[0]['state']} ({df.iloc[0]['agoi_score']:.1f})")
    b3.metric("Median AGOI", f"{df['agoi_score'].median():.1f}")
    b4.metric("High flood-risk states", int((df["flood_risk"] == 3).sum()))

# ══════════════════════════════════════════════════════
with tab2:
    sname = st.selectbox("State", df["state"].tolist())
    row = df[df["state"] == sname].iloc[0]
    raw = NS.STATES[sname]

    m1,m2,m3 = st.columns(3)
    m1.metric("AGOI score", f"{row['agoi_score']:.1f} / 100")
    m2.metric("National rank", f"#{int(row['rank'])} of {len(df)}")
    m3.metric("Band", row["band"])

    labels = [config.PILLAR_LABELS[p] for p in PILLARS]
    vals = [row[f"pillar_{p}"] for p in PILLARS]
    radar = go.Figure(go.Scatterpolar(r=vals+[vals[0]], theta=labels+[labels[0]],
                                      fill="toself", line_color="#0F766E"))
    radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                        height=400, showlegend=False, margin=dict(l=60,r=60,t=30,b=30))
    st.plotly_chart(radar, use_container_width=True)

    st.markdown("#### Underlying indicators")
    ind = pd.DataFrame([
        {"Indicator":"Climate governance score","Value":raw["policy_gov"],"Source":"SPP Nigeria"},
        {"Indicator":"Solar PV output (kWh/kWp, min–max)","Value":f"{raw['pv_min']}–{raw['pv_max']}","Source":"Global Solar Atlas"},
        {"Indicator":"Global horizontal irradiation (kWh/m²)","Value":f"{raw['ghi_min']}–{raw['ghi_max']}","Source":"Global Solar Atlas"},
        {"Indicator":"Climate budget coverage","Value":raw["climate_budget"],"Source":"SPP Nigeria"},
        {"Indicator":"State budget (₦)","Value":f"₦{raw['state_budget']/1e9:,.1f}B","Source":"Appropriation records"},
        {"Indicator":"Flood risk (1–3, 3 = highest)","Value":raw["flood_risk"],"Source":"Longdom"},
        {"Indicator":"HDI (Global Data Lab)","Value":raw["hdi_gdl"],"Source":"Global Data Lab"},
        {"Indicator":"HDI (UNDP 2018)","Value":raw["hdi_undp"],"Source":"UNDP HDR"},
        {"Indicator":"Womanity Index (3 measures)","Value":f"{raw['womanity_1']}, {raw['womanity_2']}, {raw['womanity_3']}","Source":"Invictus Africa"},
        {"Indicator":"InfraCredit projects (Bankability proxy)","Value":raw["infracredit"],"Source":"InfraCredit"},
    ])
    st.dataframe(ind, hide_index=True, use_container_width=True)

# ══════════════════════════════════════════════════════
with tab3:
    st.markdown("#### Sources")
    src = pd.DataFrame([{"Indicator group":k, "Measure":v[0], "Source":v[1], "Confidence":v[2]}
                        for k, v in NS.SOURCES.items()])
    st.dataframe(src, hide_index=True, use_container_width=True)

    st.markdown("#### ⚠️ Excluded columns — data quality")
    st.error("Two columns from the source workbook were **excluded** after a data-quality check. "
             "They are not used anywhere in the scoring.")
    for name, reason in NS.EXCLUDED_COLUMNS:
        st.markdown(f"**{name}**  \n{reason}")
    st.info("**Why this matters:** those values rise perfectly in step with alphabetical order "
            "(Abia lowest → Zamfara highest). Fiscal performance has no relationship to the "
            "alphabet, so the column was sorted independently of its state labels. Using it "
            "would have made Zamfara Nigeria's best-run state and Abia its worst. Bankability "
            "is instead proxied by InfraCredit project counts, flagged as a proxy.")
