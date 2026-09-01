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
import plotly.graph_objects as go
import streamlit as st

from _shared import inject_css                    # noqa: E402
from agoi.agesi import instruments as ins          # noqa: E402
from agoi.natcap import fipre as F                 # noqa: E402

st.set_page_config(page_title="AGESI Instruments · AGOI™", page_icon="🏦", layout="wide")
inject_css()

st.title("🏦 AGESI Instruments — CGV & NEAI")
st.caption("Credit Guarantee Vehicle · Environmental credit issuance · Transaction integrity")

tab1, tab2 = st.tabs(["💳 CGV Guarantee Calculator", "🌱 NEAI Environmental Credits"])

# ══════════════════════════════════════════════════════
# CGV
# ══════════════════════════════════════════════════════
with tab1:
    st.markdown("#### How a partial guarantee makes a project bankable")
    st.caption("A guarantee shifts default risk to the guarantor, so the lender prices the loan "
               "closer to the guarantor's risk. Lower rate → lower debt service → projects that "
               "were marginal become viable.")

    c1, c2 = st.columns([1, 2])
    with c1:
        principal = st.number_input("Loan principal (₦)", min_value=1_000_000,
                                    value=500_000_000, step=50_000_000, format="%d")
        base_rate = st.slider("Base interest rate (no guarantee) %", 5.0, 35.0, 22.0, 0.5)
        years     = st.slider("Tenor (years)", 1, 25, 10)
        coverage  = st.slider("Guarantee coverage %", 0, 100, 60, 5)
        max_red   = st.slider("Max spread a full guarantee removes (pts)", 1.0, 12.0, 6.0, 0.5,
                              help="POLICY PARAMETER — the spread reduction at 100% coverage. "
                                   "Not an empirical constant; set to your market's observed spread.")

    r = ins.cgv_analysis(principal, base_rate, years, coverage, max_red)

    with c2:
        a,b,c = st.columns(3)
        a.metric("Interest rate", f"{r['rate_with']}%", delta=f"-{r['rate_saving_pts']} pts",
                 delta_color="inverse")
        b.metric("Monthly payment", ins.fmt_ngn(r["monthly_with"]),
                 delta=f"-{ins.fmt_ngn(r['monthly_saving'])}", delta_color="inverse")
        c.metric("Lifetime saving", ins.fmt_ngn(r["lifetime_saving"]),
                 help=f"{r['saving_pct']}% lower debt service over {years} years")

        fig = go.Figure(go.Bar(
            x=["Monthly payment<br>WITHOUT guarantee", "Monthly payment<br>WITH guarantee"],
            y=[r["monthly_without"], r["monthly_with"]],
            marker_color=["#94A3A1", "#0F766E"],
            text=[ins.fmt_ngn(r["monthly_without"]), ins.fmt_ngn(r["monthly_with"])],
            textposition="outside"))
        fig.update_layout(height=340, plot_bgcolor="white", yaxis_title="₦ per month",
                          margin=dict(l=0,r=0,t=20,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Terms")
    st.dataframe(pd.DataFrame([
        {"Item":"Principal","Without guarantee":ins.fmt_ngn(r["principal"]),"With guarantee":ins.fmt_ngn(r["principal"])},
        {"Item":"Interest rate","Without guarantee":f"{r['rate_without']}%","With guarantee":f"{r['rate_with']}%"},
        {"Item":"Monthly payment","Without guarantee":ins.fmt_ngn(r["monthly_without"]),"With guarantee":ins.fmt_ngn(r["monthly_with"])},
        {"Item":f"Total over {years} yrs","Without guarantee":ins.fmt_ngn(r["total_without"]),"With guarantee":ins.fmt_ngn(r["total_with"])},
        {"Item":"Guarantor exposure","Without guarantee":"—","With guarantee":ins.fmt_ngn(r["guarantee_exposure"])},
    ]), hide_index=True, use_container_width=True)
    st.caption("Amortisation maths is exact. The rate reduction depends on the policy parameter "
               "above — it is a modelling assumption, not a market quote.")

# ══════════════════════════════════════════════════════
# NEAI
# ══════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Environmental credit issuance — gated on integrity")
    st.caption("Credits may only be issued if the project clears BOTH gates: the FIPRE "
               "non-compensatory screen (including an Impact floor), and the ETIV transaction "
               "integrity floor.")

    left, right = st.columns([1, 1.35])

    with left:
        st.markdown("**Credit definition**")
        ctype = st.text_input("Credit type", "Lagos Environmental Credit")
        units = st.number_input("Units (1 credit = 1 tonne CO₂e)", min_value=1, value=100, step=10)
        price = st.number_input("Price per credit (₦)", min_value=1000, value=1_000_000, step=100_000)

        st.markdown("**Gate 1 — FIPRE**")
        fip_pass = st.checkbox("Project passed the FIPRE screen", value=True)
        fip_impact = st.slider("FIPRE Impact dimension score", 0.0, 5.0, 4.0, 0.5)
        impact_floor = st.slider("Impact floor for issuance", 0.0, 5.0, 3.0, 0.5)

    with right:
        st.markdown("**Gate 2 — ETIV (Environmental Transaction Integrity Value)**")
        comps = {}
        for k, desc in ins.ETIV_COMPONENTS.items():
            comps[k] = st.slider(f"{k.replace('_',' ').title()} (weight {ins.ETIV_WEIGHTS[k]:.0%})",
                                 0.0, 1.0, 0.75, 0.05, help=desc, key=f"etiv_{k}")
        e = ins.etiv_score(comps)

        gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=e["etiv"],
            number={"valueformat":".2f"},
            gauge={"axis":{"range":[0,1]},
                   "bar":{"color":"#0F766E"},
                   "steps":[{"range":[0, ins.ETIV_ISSUANCE_FLOOR],"color":"#F5D6D6"},
                            {"range":[ins.ETIV_ISSUANCE_FLOOR,1],"color":"#DCEFE9"}],
                   "threshold":{"line":{"color":"#C62828","width":3},"value":ins.ETIV_ISSUANCE_FLOOR}},
            title={"text":f"ETIV (floor {ins.ETIV_ISSUANCE_FLOOR})"}))
        gauge.update_layout(height=250, margin=dict(l=20,r=20,t=50,b=10))
        st.plotly_chart(gauge, use_container_width=True)

    iss = ins.issue_credits(ctype, units, price, e["etiv"], fip_pass, fip_impact, impact_floor)

    st.markdown("---")
    if iss["issuable"]:
        st.success(f"✅ **ISSUABLE** — {iss['integrity_statement']}")
    else:
        st.error(f"⛔ **NOT ISSUABLE** — blocked by: {', '.join(iss['blockers'])}")

    k1,k2,k3 = st.columns(3)
    k1.metric("Credits", f"{iss['units']:,.0f}", help=iss["unit_definition"])
    k2.metric("Price per credit", ins.fmt_ngn(iss["price_per_credit"]))
    k3.metric("Gross value", ins.fmt_ngn(iss["gross_value"]))

    st.markdown("#### Issuance record")
    st.dataframe(pd.DataFrame([
        {"Field":"Credit type","Value":iss["credit_type"]},
        {"Field":"Units","Value":f"{iss['units']:,.0f}  ({iss['unit_definition']})"},
        {"Field":"Price per credit","Value":ins.fmt_ngn(iss["price_per_credit"])},
        {"Field":"Gross value","Value":ins.fmt_ngn(iss["gross_value"])},
        {"Field":"ETIV","Value":f"{iss['etiv']:.3f} (floor {ins.ETIV_ISSUANCE_FLOOR})"},
        {"Field":"FIPRE screen","Value":"Passed" if iss["fipre_passed"] else "Not passed"},
        {"Field":"FIPRE Impact","Value":f"{iss['fipre_impact']:.1f} (floor {impact_floor})"},
        {"Field":"Integrity statement","Value":iss["integrity_statement"]},
    ]), hide_index=True, use_container_width=True)

    if not e["issuable"]:
        st.warning(f"ETIV note — {e['note']}")
