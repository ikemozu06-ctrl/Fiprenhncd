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

from _shared import inject_css                  # noqa: E402
from agoi.fipre import framework as F           # noqa: E402

st.set_page_config(page_title="FIPRE® Scorecard · AGESI", page_icon="📋", layout="wide")
inject_css()

st.title("📋 FIPRE® Scorecard")
st.caption("Score a project across the 25 criteria to generate a preliminary FIPRE® profile")

st.error("**Automation control.** This tool must never auto-approve a project from TIV alone. "
         "Integrity failures, pillar overrides, mandatory requirements, specialist judgement and "
         "accountable decision rights remain visible and with the accountable decision-maker. "
         "This produces a **preliminary profile**, not a decision.", icon="⚠️")

mode = st.radio("Assessment mode", ["Quick (pillar level)", "Full (25 criteria)", "FIPRE® Lite (10-min screen)"],
                horizontal=True)

# ══════════════════════════════════════════════════════════
# FIPRE LITE
# ══════════════════════════════════════════════════════════
if mode == "FIPRE® Lite (10-min screen)":
    st.markdown("#### Ten questions for early-stage concept screening")
    st.caption("Flags potential fatal flaws requiring immediate investigation. Not a substitute for full assessment.")
    answers = []
    for i, (pillar, q) in enumerate(F.LITE_QUESTIONS):
        c1, c2 = st.columns([3, 1])
        c1.markdown(f"**{i+1}.** {q}  \n<span style='font-size:11px;color:#5A6B60'>"
                    f"{F.PILLARS[pillar]['icon']} {F.PILLARS[pillar]['name']}</span>",
                    unsafe_allow_html=True)
        answers.append(c2.radio("", ["yes", "unsure", "no"], horizontal=True,
                                key=f"lite{i}", label_visibility="collapsed"))
    res = F.lite_screen(answers)
    st.markdown("---")
    st.markdown(f"<div style='background:{res['colour']};color:#fff;padding:22px;border-radius:12px;"
                f"text-align:center'><div style='font-size:13px;letter-spacing:2px;opacity:.85'>"
                f"SCREENING RESULT</div><div style='font-size:26px;font-weight:800;margin:6px 0'>"
                f"{res['level']}</div><div style='font-size:15px'>{res['message']}</div></div>",
                unsafe_allow_html=True)
    if res["flagged_pillars"]:
        st.markdown("##### Pillars with flagged questions")
        st.dataframe(pd.DataFrame([{"Pillar": F.PILLARS[p]["name"], "Questions flagged": n}
                                   for p, n in res["flagged_pillars"].items()]),
                     hide_index=True, use_container_width=True)
    st.stop()

# ══════════════════════════════════════════════════════════
# INTEGRITY GATE (both scoring modes)
# ══════════════════════════════════════════════════════════
st.markdown("### Step 1 — Institutional Integrity Gate")
st.caption(F.GATE_RULE)
gate = {}
gcols = st.columns(3)
for i, (k, (label, cond)) in enumerate(F.INTEGRITY_GATE.items()):
    gate[k] = gcols[i % 3].checkbox(label, value=True, help=cond, key=f"g_{k}")

# ══════════════════════════════════════════════════════════
# SCORING
# ══════════════════════════════════════════════════════════
st.markdown("### Step 2 — Score the pillars")
pillar_scores = {}

if mode == "Full (25 criteria)":
    for key in F.PILLAR_ORDER:
        p = F.PILLARS[key]
        with st.expander(f"{p['icon']} {p['name']} · {p['subtitle']}", expanded=(key == "function")):
            st.caption(p["question"])
            crit = {}
            for ck, cdesc in p["criteria"].items():
                crit[ck] = st.slider(f"**{ck}** — {cdesc}", 1.0, 5.0, 3.0, 0.5, key=f"c_{ck}")
            pillar_scores[key] = F.pillar_score(crit)
            st.metric(f"{p['name']} pillar score", f"{pillar_scores[key]:.2f}")
else:
    scols = st.columns(5)
    for col, key in zip(scols, F.PILLAR_ORDER):
        p = F.PILLARS[key]
        pillar_scores[key] = col.slider(f"{p['icon']} {p['name']}", 1.0, 5.0, 3.0, 0.5,
                                        key=f"q_{key}", help=p["question"])

st.markdown("### Step 3 — Evidence confidence")
conf = st.select_slider("Overall evidence confidence", options=["A", "B", "C", "D"], value="B",
                        format_func=lambda g: f"{g} — {F.CONFIDENCE[g][0]}")
st.caption(f"**{F.CONFIDENCE[conf][0]}:** {F.CONFIDENCE[conf][1]} → *{F.CONFIDENCE[conf][2]}*")

# ══════════════════════════════════════════════════════════
# RESULT
# ══════════════════════════════════════════════════════════
r = F.assess(pillar_scores, gate=gate, confidence=conf)

st.markdown("---")
st.markdown("## Preliminary FIPRE® profile")

left, right = st.columns([1, 1])

with left:
    st.markdown(
        f"<div style='background:{r['verdict_colour']};color:#fff;padding:26px;border-radius:14px'>"
        f"<div style='font-size:12px;letter-spacing:2px;opacity:.85'>TOTAL INFRASTRUCTURE VALUE</div>"
        f"<div style='font-size:52px;font-weight:800;line-height:1'>{r['tiv']}</div>"
        f"<div style='font-size:18px;font-weight:700;margin-top:4px'>"
        f"{r['classification']} · {r['band_signal']}</div>"
        f"<div style='margin-top:14px;padding-top:12px;border-top:1px solid rgba(255,255,255,.3)'>"
        f"<b>DECISION: {r['decision']}</b><br><span style='font-size:14px'>{r['rationale']}</span></div>"
        f"</div>", unsafe_allow_html=True)

    if not r["gate_passed"]:
        st.error(f"🚫 **Integrity gate failed:** {', '.join(r['gate_failures'])}. {F.GATE_RULE}")
    if r["non_compensatory_override"]:
        st.error(f"⛔ **Non-compensatory override active** — "
                 f"{', '.join(F.PILLARS[p]['name'] for p in r['failing_pillars'])} at or below 2.0.")

    st.markdown("##### Pillar scores")
    st.dataframe(pd.DataFrame([
        {"Pillar": f"{F.PILLARS[k]['icon']} {F.PILLARS[k]['name']}",
         "Score": r["pillar_scores"][k],
         "Status": "⛔ FAIL" if r["pillar_scores"][k] <= 2.0
                   else ("✅ Strong" if r["pillar_scores"][k] >= 4.0 else "🟠 Acceptable")}
        for k in F.PILLAR_ORDER]), hide_index=True, use_container_width=True)

with right:
    st.markdown("##### Pillar balance")
    st.caption("A sharp inward point reveals a weak pillar. Do not use the polygon area as an alternative score.")
    labels = [F.PILLARS[k]["name"] for k in F.PILLAR_ORDER]
    vals = [r["pillar_scores"][k] for k in F.PILLAR_ORDER]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=labels + [labels[0]],
                                  fill="toself", line_color=r["verdict_colour"], name="Score"))
    fig.add_trace(go.Scatterpolar(r=[3]*6, theta=labels + [labels[0]], mode="lines",
                                  line=dict(color="#B0BEB5", dash="dot"), name="Minimum acceptable (3.0)"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                      height=400, margin=dict(l=60, r=60, t=30, b=30),
                      legend=dict(orientation="h", y=-0.12))
    st.plotly_chart(fig, use_container_width=True)

    st.metric("Evidence confidence", f"{conf} — {r['confidence_label']}", help=r["confidence_use"])

# Improvement guidance for the weakest pillar
weak = r["weakest_pillar"]
st.markdown(f"##### Improvement levers — {F.PILLARS[weak]['icon']} {F.PILLARS[weak]['name']} "
            f"(weakest at {r['pillar_scores'][weak]:.2f})")
lc1, lc2 = st.columns(2)
with lc1:
    st.markdown("**🚩 Red flags to check**")
    for f in F.PILLARS[weak]["red_flags"]:
        st.markdown(f"- {f}")
with lc2:
    st.markdown("**⚡ Improvement levers**")
    for l in F.PILLARS[weak]["levers"]:
        st.markdown(f"- {l}")

# Export
st.markdown("---")
export = pd.DataFrame([{"Field": "TIV", "Value": r["tiv"]},
                       {"Field": "Classification", "Value": r["classification"]},
                       {"Field": "Decision", "Value": r["decision"]},
                       {"Field": "Rationale", "Value": r["rationale"]},
                       {"Field": "Integrity gate", "Value": "PASS" if r["gate_passed"] else "FAIL: " + "; ".join(r["gate_failures"])},
                       {"Field": "Non-compensatory override", "Value": r["non_compensatory_override"]},
                       {"Field": "Evidence confidence", "Value": f"{conf} — {r['confidence_label']}"}]
                      + [{"Field": F.PILLARS[k]["name"], "Value": r["pillar_scores"][k]} for k in F.PILLAR_ORDER])
st.download_button("⬇️ Download this profile (CSV)", export.to_csv(index=False).encode("utf-8"),
                   "fipre_profile.csv", "text/csv")

st.caption(r["disclaimer"])
st.caption(F.TRADEMARK)
