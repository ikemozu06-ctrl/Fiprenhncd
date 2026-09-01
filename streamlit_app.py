"""
AGESI · FIPRE® platform — home.

FIPRE® and the FIPRE Emblem are registered trademarks owned exclusively by
Eugene Itua and the Africa Green Economy and Sustainability Institute (AGESI).
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

import plotly.graph_objects as go
import streamlit as st

from agoi.fipre import framework as F

st.set_page_config(
    page_title="FIPRE® · AGESI",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.main .block-container{padding-top:2rem;max-width:1180px}
h1,h2,h3{color:#14231A}
.hero{background:linear-gradient(135deg,#0E5228 0%,#1B7A3E 65%,#2A9550 100%);
  padding:2.4rem 2.6rem;border-radius:16px;color:#fff;margin-bottom:1.4rem}
.hero h1{color:#fff;margin:0;font-size:2.6rem;font-weight:800;letter-spacing:-1px}
.hero .tag{color:#A8E5C0;font-size:.78rem;letter-spacing:2.6px;font-weight:700;
  text-transform:uppercase;margin-bottom:.5rem}
.hero .sub{color:#D6F0E0;font-size:1.15rem;font-weight:600;margin:.4rem 0 .1rem}
.hero p{color:#CFEBDB;font-size:1rem;margin:.6rem 0 0;max-width:720px}
.pcard{background:#F7FAF8;border:1px solid #DCE6DF;border-top:4px solid #1B7A3E;
  border-radius:10px;padding:1rem .8rem;text-align:center}
.pcard .ic{font-size:1.7rem}
.pcard b{color:#0E5228;font-size:.95rem;display:block;margin-top:.2rem}
.pcard span{font-size:.68rem;color:#5A6B60;text-transform:uppercase;letter-spacing:.6px}
.small{color:#5A6B60;font-size:.85rem}
</style>
""", unsafe_allow_html=True)

_LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo.png")
if os.path.isfile(_LOGO):
    try:
        st.logo(_LOGO, size="large")
    except Exception:
        st.sidebar.image(_LOGO, use_container_width=True)

st.markdown("""
<div class="hero">
  <div class="tag">Africa Green Economy &amp; Sustainability Institute</div>
  <h1>Engineering Beyond Function®</h1>
  <div class="sub">The FIPRE® Sustainability Framework</div>
  <p>Infrastructure that works, creates value, withstands shocks, and serves people fairly —
  a common language for turning sustainability commitments into better decisions.</p>
</div>
""", unsafe_allow_html=True)

cols = st.columns(5)
for col, key in zip(cols, F.PILLAR_ORDER):
    p = F.PILLARS[key]
    col.markdown(f"<div class='pcard'><div class='ic'>{p['icon']}</div>"
                 f"<b>{p['name']}</b><span>{p['subtitle']}</span></div>",
                 unsafe_allow_html=True)

st.markdown("")
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("#### Five tests. One integrated view.")
    st.markdown(
        "Existing appraisal systems fragment sustainability into separate engineering, "
        "environmental, economic, climate-risk and social workstreams — so decisions get made on "
        "incomplete or unverifiable evidence. Projects can look technically sound while remaining "
        "unaffordable to maintain, environmentally harmful, climate-vulnerable or inaccessible to "
        "the people they serve.\n\n"
        "**FIPRE®** replaces that with one integrated decision view, governed by a "
        "**non-compensation rule**: a material weakness in any pillar cannot be hidden by strength "
        "in another."
    )
with c2:
    st.markdown("#### Start here")
    st.page_link("pages/1_FIPRE_Framework.py", label="Explore the framework", icon="🏛️")
    st.page_link("pages/2_FIPRE_Scorecard.py", label="Score a project", icon="📋")
    st.markdown("<span class='small'>The 10-minute FIPRE® Lite screen is on the "
                "Scorecard page.</span>", unsafe_allow_html=True)

st.divider()

st.markdown("### Try it — move the sliders")
st.caption("A preliminary profile, not a decision. The non-compensatory rule is enforced.")

sc = {}
scols = st.columns(5)
for col, key in zip(scols, F.PILLAR_ORDER):
    p = F.PILLARS[key]
    sc[key] = col.slider(f"{p['icon']} {p['name']}", 1.0, 5.0, 3.0, 0.5,
                         key=f"h_{key}", help=p["question"])

r = F.assess(sc, gate={k: True for k in F.INTEGRITY_GATE}, confidence="B")

rc1, rc2 = st.columns([1, 1])
with rc1:
    st.markdown(
        f"<div style='background:{r['verdict_colour']};color:#fff;padding:1.5rem;border-radius:12px'>"
        f"<div style='font-size:.72rem;letter-spacing:2px;opacity:.85'>TOTAL INFRASTRUCTURE VALUE</div>"
        f"<div style='font-size:3rem;font-weight:800;line-height:1'>{r['tiv']}</div>"
        f"<div style='font-size:1.05rem;font-weight:700'>{r['classification']} · {r['band_signal']}</div>"
        f"<div style='margin-top:.7rem;padding-top:.6rem;border-top:1px solid rgba(255,255,255,.3);"
        f"font-size:.92rem'><b>{r['decision']}</b><br>{r['rationale']}</div></div>",
        unsafe_allow_html=True)

with rc2:
    labels = [F.PILLARS[k]["name"] for k in F.PILLAR_ORDER]
    vals = [sc[k] for k in F.PILLAR_ORDER]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=labels + [labels[0]],
                                  fill="toself", line_color=r["verdict_colour"], name="Score"))
    fig.add_trace(go.Scatterpolar(r=[3] * 6, theta=labels + [labels[0]], mode="lines",
                                  line=dict(color="#B0BEB5", dash="dot"), name="Minimum (3.0)"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                      height=330, margin=dict(l=55, r=55, t=20, b=20),
                      legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.markdown("### Also on this platform")
a, b, c = st.columns(3)
with a:
    st.markdown("**Africa ESG intelligence**")
    st.page_link("pages/3_Africa_Map.py", label="Africa map — 54 countries", icon="🗺️")
    st.page_link("pages/4_Country_Profile.py", label="Country profiles", icon="📋")
    st.page_link("pages/5_Nigeria_States.py", label="Nigeria — 36 states + FCT", icon="🇳🇬")
with b:
    st.markdown("**Natural capital & finance**")
    st.page_link("pages/6_Natural_Capital.py", label="Natural capital valuation", icon="🌿")
    st.page_link("pages/7_AGESI_Instruments.py", label="Guarantees & credits", icon="🏦")
with c:
    st.markdown("**Context & method**")
    st.page_link("pages/8_AfCFTA.py", label="AfCFTA trade readiness", icon="🌍")
    st.page_link("pages/9_Global_Index_Comparison.py", label="Global index comparison", icon="🌐")
    st.page_link("pages/10_Methodology.py", label="Methodology & exports", icon="📥")

st.divider()
st.caption(F.NOT_A_CLAIM)
st.caption(F.TRADEMARK)
