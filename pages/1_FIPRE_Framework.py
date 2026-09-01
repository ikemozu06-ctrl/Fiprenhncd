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

from _shared import inject_css                  # noqa: E402
from agoi.fipre import framework as F           # noqa: E402

st.set_page_config(page_title="FIPRE® Framework · AGESI", page_icon="🏛️", layout="wide")
inject_css()

st.title("🏛️ The FIPRE® Sustainability Framework")
st.markdown("### *Engineering Beyond Function®*")
st.caption("A common language for turning sustainability commitments into better decisions · "
           "Africa Green Economy and Sustainability Institute (AGESI)")

st.info(f"**{F.NOT_A_CLAIM}**", icon="ℹ️")

tabs = st.tabs(["🔷 The Five Pillars", "🚪 Integrity Gate", "📊 Scoring & TIV",
                "🔍 Evidence Confidence", "⚖️ Decision Outcomes", "™ Trademark"])

# ══════════════════════════════════════════════════
with tabs[0]:
    st.markdown("#### Five distinct tests, governed by a non-compensation rule")
    st.markdown("A material weakness in any pillar cannot be hidden by strength in another.")

    cols = st.columns(5)
    for col, key in zip(cols, F.PILLAR_ORDER):
        p = F.PILLARS[key]
        col.markdown(f"<div style='text-align:center;padding:14px;border-top:4px solid #1B7A3E;"
                     f"background:#F7FAF8;border-radius:8px;min-height:150px'>"
                     f"<div style='font-size:28px'>{p['icon']}</div>"
                     f"<b style='color:#0E5228'>{p['name']}</b><br>"
                     f"<span style='font-size:11px;color:#5A6B60;text-transform:uppercase;"
                     f"letter-spacing:.5px'>{p['subtitle']}</span></div>",
                     unsafe_allow_html=True)

    st.warning("**None of the five works alone.** Strong Resilience without Equity just protects "
               "wealthy neighbourhoods better — the pillars must move together.", icon="🔗")

    st.markdown("---")
    sel = st.selectbox("Explore a pillar",
                       F.PILLAR_ORDER,
                       format_func=lambda k: f"{F.PILLARS[k]['icon']}  {F.PILLARS[k]['name']} · {F.PILLARS[k]['subtitle']}")
    p = F.PILLARS[sel]

    st.markdown(f"## {p['icon']} {p['name']} · {p['subtitle']}")
    st.markdown(f"*{p['question']}*")
    st.write(p["tests"])

    st.markdown("##### The five criteria")
    st.dataframe(pd.DataFrame([{"Criterion": k, "What to test": v} for k, v in p["criteria"].items()]),
                 hide_index=True, use_container_width=True)

    st.markdown("##### Score anchors")
    st.dataframe(pd.DataFrame([{"Score": s, "Level": F.SCALE[s][0], "Anchor": a}
                               for s, a in p["anchors"].items()]),
                 hide_index=True, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("##### 🚩 Red flags")
        for f in p["red_flags"]:
            st.markdown(f"- 🚩 {f}")
    with c2:
        st.markdown("##### ⚡ Improvement levers")
        for l in p["levers"]:
            st.markdown(f"- ⚡ {l}")

# ══════════════════════════════════════════════════
with tabs[1]:
    st.markdown("#### The Institutional Integrity Gate")
    st.markdown("Before any project receives a sustainability profile, it must pass this pre-screen.")
    st.dataframe(pd.DataFrame([{"Gate test": v[0], "Pass condition": v[1]}
                               for v in F.INTEGRITY_GATE.values()]),
                 hide_index=True, use_container_width=True)
    st.error(f"**Gate Rule.** {F.GATE_RULE}", icon="🚫")

# ══════════════════════════════════════════════════
with tabs[2]:
    st.markdown("#### The five-point performance scale")
    st.caption("Use the anchor that best describes **verified current performance** — not the intended future state.")
    st.dataframe(pd.DataFrame([{"Score": s, "Level": v[0], "Common anchor": v[1],
                                "Decision implication": v[2]} for s, v in F.SCALE.items()]),
                 hide_index=True, use_container_width=True)

    st.markdown("#### Total Infrastructure Value (TIV)")
    st.code("TIV = Function + Impact + Prosperity + Resilience + Equity", language=None)
    st.dataframe(pd.DataFrame([
        {"TIV range": "5.0 – 12.9", "Classification": "Weak", "Signal": "🔴 Red",
         "Decision meaning": "Stop or fundamentally redesign. Evidence and value case are insufficient."},
        {"TIV range": "13.0 – 17.9", "Classification": "Acceptable", "Signal": "🟠 Orange",
         "Decision meaning": "Conditional only if every pillar is at least 3.0; close defined gaps before the next gate."},
        {"TIV range": "18.0 – 25.0", "Classification": "Strong", "Signal": "🟢 Green",
         "Decision meaning": "Proceed subject to conditions and verification; inspect pillar balance and evidence confidence."},
        {"TIV range": "≥ 21.0 and every pillar ≥ 4.0", "Classification": "Balanced Excellence",
         "Signal": "🟢 Deep Green",
         "Decision meaning": "High, balanced and well-evidenced value; maintain assurance and outcome monitoring."},
    ]), hide_index=True, use_container_width=True)

    st.info("**Interpretation rule.** The TIV band is descriptive. The integrity gate, the "
            "non-compensatory rule, mandatory law/standard and evidence confidence always take precedence.",
            icon="ℹ️")

    st.error("**The Non-Compensatory Rule — mandatory override.** Any pillar score of 2.0 or below "
             "triggers redesign, regardless of TIV. A project rated 5, 5, 5, 5 and 2 has four "
             "exceptional results and a failed Equity pillar. The correct response is not to praise "
             "the apparent overall strength — it is to identify the weakness and decide whether "
             "redesign can resolve it.", icon="⛔")

# ══════════════════════════════════════════════════
with tabs[3]:
    st.markdown("#### Evidence confidence")
    st.caption("Score performance and evidence confidence separately. Confidence does not increase a "
               "score; it qualifies how much reliance the decision-maker should place on it.")
    st.dataframe(pd.DataFrame([{"Grade": k, "Level": v[0], "Evidence condition": v[1], "Use": v[2]}
                               for k, v in F.CONFIDENCE.items()]),
                 hide_index=True, use_container_width=True)
    st.warning("**Key distinction.** A score of **1** means evidence demonstrates failure. "
               "**NS (Not Scorable)** means the project has not provided enough evidence to know. "
               "Both may prevent commitment, but for different reasons and with different remedies.",
               icon="⚠️")

# ══════════════════════════════════════════════════
with tabs[4]:
    st.markdown("#### Four decision outcomes")
    st.dataframe(pd.DataFrame([
        {"Decision": "Commit", "Meaning": "All gates and thresholds pass with evidence confidence appropriate to the decision stage, and no material condition remains outside normal monitoring"},
        {"Decision": "Conditional Commit", "Meaning": "Thresholds are met, but specific evidence, mitigation, financing or institutional actions must be completed. Conditions must be enforceable, owned, funded and time-bound"},
        {"Decision": "Redesign", "Meaning": "One or more pillars or essential indicators fail, or material uncertainty prevents a responsible commitment, but a credible corrective path exists"},
        {"Decision": "Decline", "Meaning": "A mandatory gate fails without a lawful remedy, the public need or strategic fit is not credible, or the project remains fundamentally unacceptable after alternatives are considered"},
    ]), hide_index=True, use_container_width=True)
    st.info("**Decision rule.** A condition without an owner, deadline, budget and enforcement route "
            "is not a condition; it is an aspiration.", icon="📌")

# ══════════════════════════════════════════════════
with tabs[5]:
    st.markdown("#### Trademark notice")
    st.warning(F.TRADEMARK, icon="™")
    st.markdown("#### What FIPRE® is not")
    st.info(F.NOT_A_CLAIM, icon="ℹ️")
    st.markdown("#### Origin")
    st.write("FIPRE® was developed through structured conceptual synthesis — framing recurring public "
             "investment failure modes as decision problems; organising them into five conceptually "
             "distinct pillars with institutional integrity as a prior condition; cross-checking against "
             "major lifecycle, safeguards, quality-infrastructure, resilience and assurance frameworks; "
             "designing explicit decision rules; and testing through a worked demonstration.")
    st.caption("Born from an ITCILO learning experience, co-authored by Eugene Itua and Hon. David Umahi.")
