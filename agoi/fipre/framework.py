"""
FIPRE® Sustainability Framework — decision engine.

Implements the framework as specified in the AGESI FIPRE® documentation:
integrity gate → 25-criterion scoring → pillar scores → TIV → non-compensatory
override → evidence confidence → decision outcome.

TRADEMARK NOTICE
FIPRE® and the FIPRE Emblem are registered trademarks owned exclusively by
Eugene Itua and the Africa Green Economy and Sustainability Institute (AGESI).

FIPRE® is a structured decision-support framework. It is NOT a law, engineering
code, safeguard system, investment rating, certification scheme, financial
recommendation, or institutional endorsement.

AUTOMATION CONTROL (from the framework, section 5.2)
Software must never auto-approve a project from TIV alone. Integrity failures,
pillar overrides, mandatory requirements, specialist judgement and accountable
decision rights must remain visible. This module returns a PRELIMINARY PROFILE,
never a decision.
"""
from __future__ import annotations
from typing import Dict, List

# ──────────────────────────────────────────────────────────────────────────────
# The five pillars
# ──────────────────────────────────────────────────────────────────────────────
PILLARS = {
    "function": {
        "key": "F", "icon": "⚙️", "name": "FUNCTION", "subtitle": "Operational Continuity",
        "question": "Will the service work safely, reliably and durably?",
        "tests": "Whether the intervention can reliably deliver the required service over its "
                 "design life — need, engineering quality, safety, reliability, constructability, "
                 "commissioning, operations and maintenance.",
        "criteria": {
            "F1": "Need and service logic — defined service need; demand and options analysis; measurable service levels",
            "F2": "Design quality and compliance — applicable codes and standards; constructability; design verification; interfaces",
            "F3": "Safety, reliability and quality — safety-in-design; reliability targets; quality assurance; failure-mode controls",
            "F4": "Lifecycle cost and durability — whole-life cost; design life; material durability; maintainability; replacement strategy",
            "F5": "Operations and delivery readiness — O&M model; competent operator; budget, spares, skills, commissioning and handover",
        },
        "anchors": {
            1: "Service logic or technical feasibility is absent; critical safety or compliance failure exists",
            2: "Concept may work, but major design, reliability, constructability, durability or O&M gaps remain",
            3: "Applicable requirements are addressed; design is feasible; O&M roles and minimum lifecycle resources identified",
            4: "Design is verified and optimised for safety, reliability, maintainability and lifecycle cost; delivery and operations resourced",
            5: "Independent verification, high reliability, adaptive asset management and measurable performance learning are embedded",
        },
        "red_flags": ["Unclear service need", "Unresolved design interfaces", "Safety-critical assumptions",
                      "Single-point failure", "No competent operator", "O&M budget omitted",
                      "Design life inconsistent with materials or climate"],
        "levers": ["Revisit options", "Undertake independent design/safety review", "Specify service levels",
                   "Complete lifecycle costing", "Secure operator, skills, spares and O&M funding",
                   "Stage commissioning and performance testing"],
    },
    "impact": {
        "key": "I", "icon": "🌍", "name": "IMPACT", "subtitle": "Consequence Assessment",
        "question": "Does it improve lives and protect the environment?",
        "tests": "Net environmental, social, health and development consequences. Applies the mitigation "
                 "hierarchy and distinguishes claimed outputs from measurable outcomes for people and nature.",
        "criteria": {
            "I1": "Baseline and scope — current, relevant baseline; direct, indirect and cumulative effects",
            "I2": "Mitigation hierarchy — avoid, minimise, restore, then compensate as last resort",
            "I3": "Environmental outcomes — measurable effects on air, water, land, biodiversity and climate",
            "I4": "Social and health outcomes — measurable effects on communities, health and wellbeing",
            "I5": "Grievance, remedy and monitoring — accessible mechanism; outcome indicators; transparent learning",
        },
        "anchors": {
            1: "Material harm is likely or unassessed; mitigation hierarchy and remedy are absent",
            2: "Some assessment exists, but material gaps in baseline, mitigation or remedy remain",
            3: "Material risks are assessed and manageable; core plans are in place",
            4: "Well-evidenced mitigation, monitored outcomes, and a functioning grievance and remedy mechanism",
            5: "Verified net-positive outcomes; innovation; transparent learning; durable institutional or ecosystem gains",
        },
        "red_flags": ["Baseline too narrow or outdated", "Indirect/cumulative impacts omitted",
                      "Compensation used before avoidance", "Consultation without feedback",
                      "Benefits not attributable"],
        "levers": ["Re-run alternatives and mitigation hierarchy", "Strengthen baseline and cumulative assessment",
                   "Establish accessible grievance and remedy", "Add outcome indicators"],
    },
    "prosperity": {
        "key": "P", "icon": "💹", "name": "PROSPERITY", "subtitle": "Sustainable Growth",
        "question": "Does it create shared and durable economic value?",
        "tests": "Whether the intervention creates shared and durable economic value without imposing "
                 "unsustainable financial or fiscal burdens — productivity, affordability, jobs, enterprise, "
                 "value chains, innovation and regional integration.",
        "criteria": {
            "P1": "Economic rationale — credible economic case; benefits exceed whole-life costs",
            "P2": "Affordability and fiscal exposure — tariffs, subsidies, contingent liabilities, public obligation",
            "P3": "Jobs and decent work — duration, quality, safety and inclusiveness of employment created",
            "P4": "Enterprise and value chains — local supplier development, skills, innovation, regional integration",
            "P5": "Lifecycle funding — ring-fenced O&M and replacement funding across the asset life",
        },
        "anchors": {
            1: "Economic rationale is absent or negative; affordability, fiscal exposure or value capture is unacceptable",
            2: "Economic case is partial; affordability, lifecycle funding or value capture is uncertain",
            3: "Economic case is credible; lifecycle funding and affordability are manageable",
            4: "Strong, well-evidenced economic value with protected decent work and funded lifecycle",
            5: "Transformative, inclusive and durable economic value is independently verified",
        },
        "red_flags": ["Headline jobs without duration or quality", "Financial viability confused with economic value",
                      "Tariffs unaffordable", "O&M unfunded", "Public liabilities hidden"],
        "levers": ["Test affordability and fiscal exposure", "Model downside cases",
                   "Design supplier/skills actions", "Protect decent work", "Ring-fence lifecycle funding"],
    },
    "resilience": {
        "key": "R", "icon": "🔄", "name": "RESILIENCE", "subtitle": "Shock Absorption & Recovery",
        "question": "Can it withstand climate and systemic shocks?",
        "tests": "Whether the asset, service, operator and affected communities can anticipate, absorb, "
                 "adapt to and recover from climate, disaster, market, institutional and systemic shocks.",
        "criteria": {
            "R1": "Hazard and scenario basis — forward-looking climate scenarios, not historical data alone",
            "R2": "Design response — robustness, flexibility, redundancy, failure thresholds",
            "R3": "Residual risk ownership — who carries what risk; adaptation funded",
            "R4": "GHG and transition alignment — material emissions quantified; lock-in avoided",
            "R5": "Recovery and continuity — service continuity planning; operator and community capacity",
        },
        "anchors": {
            1: "Material climate/system hazards are ignored; design could fail under foreseeable conditions or cause lock-in",
            2: "Hazards partly considered; adaptation measures or residual-risk ownership incomplete",
            3: "Proportionate scenarios, adaptation measures, residual-risk ownership and core GHG information are in place",
            4: "Stress-tested critical service, funded adaptation, redundancy and low-carbon alignment",
            5: "Verified adaptive performance, low-carbon alignment, redundancy and learning are demonstrated",
        },
        "red_flags": ["Historical climate used as future design basis", "Hazards treated independently",
                      "No failure thresholds", "Adaptation unfunded", "High-carbon lock-in"],
        "levers": ["Use fit-for-purpose scenarios", "Stress-test critical service",
                   "Compare robust and flexible options", "Allocate residual risk",
                   "Quantify material GHG sources"],
    },
    "equity": {
        "key": "E", "icon": "⚖️", "name": "EQUITY", "subtitle": "Fairness & Protection",
        "question": "Are benefits, burdens and voice fairly distributed?",
        "tests": "Who benefits, who pays, who bears risk and who has influence. Requires disaggregated "
                 "evidence on access, affordability, vulnerable groups, gender, disability, land and "
                 "livelihood rights, voice, remedy and benefit sharing.",
        "criteria": {
            "E1": "Disaggregated analysis — who benefits, who pays, who bears risk, by group",
            "E2": "Access and universal design — physical, digital and economic accessibility",
            "E3": "Affordability — connection costs, tariffs and targeted support for vulnerable users",
            "E4": "Rights, land and livelihoods — secure rights; resettlement and livelihood restoration",
            "E5": "Voice, representation and benefit sharing — meaningful influence, not tokenistic",
        },
        "anchors": {
            1: "Rights or access are materially harmed; exclusion, discrimination or uncompensated burden is likely",
            2: "Some analysis, but disaggregation, accessibility or affordability measures are incomplete",
            3: "Disaggregated analysis, minimum accessibility, affordability, engagement and grievance measures in place",
            4: "Well-evidenced fair access, funded affordability measures and meaningful engagement",
            5: "Verified fair outcomes, meaningful influence, universal design and durable benefit-sharing",
        },
        "red_flags": ["Average benefits hide excluded groups", "Inaccessible design",
                      "Connection costs omitted", "Land/livelihood impacts unresolved",
                      "Representation tokenistic"],
        "levers": ["Disaggregate baseline and outcomes", "Apply universal design",
                   "Fund targeted access/affordability measures", "Secure rights and remedy",
                   "Strengthen representation"],
    },
}

PILLAR_ORDER = ["function", "impact", "prosperity", "resilience", "equity"]

# ──────────────────────────────────────────────────────────────────────────────
# Integrity gate — a prior condition, not another score
# ──────────────────────────────────────────────────────────────────────────────
INTEGRITY_GATE = {
    "legality": ("Legality and mandate",
                 "The intervention and decision process are lawful, authorised and consistent with binding obligations"),
    "prohibited": ("Prohibited or unacceptable activity",
                   "No applicable exclusion, sanction, prohibited practice or unmanageable rights/safety issue is triggered"),
    "life_safety": ("Life safety and irreversible harm",
                    "No known critical safety defect or unavoidable catastrophic/irreversible harm remains unaddressed"),
    "integrity": ("Integrity and conflict of interest",
                  "Material conflicts, fraud, corruption, coercion, retaliation and data manipulation risks are disclosed and managed"),
    "evidence": ("Evidence admissibility",
                 "Key claims can be traced to current, relevant and sufficiently reliable evidence; uncertainty is disclosed"),
    "authority": ("Decision authority",
                  "The body using FIPRE® has authority to make or recommend the stated decision"),
}

GATE_RULE = "No pillar score can cure a mandatory legal, safeguard, or integrity failure."

# ──────────────────────────────────────────────────────────────────────────────
# Performance scale
# ──────────────────────────────────────────────────────────────────────────────
SCALE = {
    1: ("Critical weakness", "Need or performance not demonstrated; serious non-compliance, harm, infeasibility or evidence failure", "Stop or fundamentally redesign"),
    2: ("Material gap", "Some elements exist, but material design, management, resourcing or evidence gaps remain", "Do not commit; return for corrective action"),
    3: ("Minimum acceptable", "Core requirements credibly addressed; responsibilities assigned; residual gaps closable through conditions", "Eligible, subject to conditions and monitoring"),
    4: ("Strong", "Requirements integrated, well-evidenced, resourced and monitored across the lifecycle", "Proceed and preserve commitments contractually"),
    5: ("Exemplary", "Independently verified, adaptive, innovative; creates additional, durable, transferable value", "Proceed and document transferable learning"),
}

# Evidence confidence
CONFIDENCE = {
    "A": ("High", "Current, relevant, traceable, quality-assured and independently verified or triangulated", "Decision-grade"),
    "B": ("Medium", "Credible primary evidence with limited gaps, partial verification or manageable uncertainty", "Usable with conditions"),
    "C": ("Low", "Proxies, incomplete coverage, old data, weak disaggregation or significant model uncertainty", "Provisional only; improve before approval"),
    "D": ("Insufficient", "Assertion, missing source, unverifiable claim or evidence inconsistent with the decision boundary", "Do not score as achieved"),
}

# TIV bands
TIV_BANDS = [
    (18.0, 25.01, "Strong", "🟢 Green", "#1B7A3E",
     "Proceed subject to conditions and verification; inspect pillar balance and evidence confidence."),
    (13.0, 18.0, "Acceptable", "🟠 Orange", "#E58A00",
     "Conditional only if every pillar is at least 3.0; close defined gaps before the next gate."),
    (5.0, 13.0, "Weak", "🔴 Red", "#C62828",
     "Stop or fundamentally redesign. Evidence and value case are insufficient."),
]

NON_COMPENSATORY_THRESHOLD = 2.0


def pillar_score(criterion_scores: Dict[str, float]) -> float:
    """Mean of a pillar's criterion scores."""
    vals = [v for v in criterion_scores.values() if v is not None]
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def assess(pillar_scores: Dict[str, float], gate: Dict[str, bool] | None = None,
           confidence: str = "B") -> Dict:
    """
    Produce a preliminary FIPRE® profile.

    pillar_scores: {'function': 3.4, 'impact': 2.0, ...}
    gate:          {'legality': True, ...} — all must pass
    confidence:    'A' | 'B' | 'C' | 'D'

    Returns a profile dict. This is NOT a decision — see the automation-control
    note in the module docstring.
    """
    vals = [float(pillar_scores.get(p, 0.0)) for p in PILLAR_ORDER]
    tiv = round(sum(vals), 1)
    weakest = min(PILLAR_ORDER, key=lambda p: pillar_scores.get(p, 0.0))
    min_score = min(vals) if vals else 0.0

    # 1. Integrity gate — precedes everything
    gate = gate or {}
    gate_failures = [INTEGRITY_GATE[k][0] for k in INTEGRITY_GATE if gate.get(k) is False]
    gate_passed = len(gate_failures) == 0

    # 2. Non-compensatory override
    failing = [p for p in PILLAR_ORDER
               if pillar_scores.get(p, 0.0) <= NON_COMPENSATORY_THRESHOLD]
    override = len(failing) > 0

    # 3. TIV band (descriptive only)
    band = classification = colour = band_meaning = ""
    for lo, hi, label, sig, col, meaning in TIV_BANDS:
        if lo <= tiv < hi:
            classification, band, colour, band_meaning = label, sig, col, meaning
            break
    balanced_excellence = tiv >= 21.0 and all(v >= 4.0 for v in vals)
    if balanced_excellence:
        classification, band, colour = "Balanced Excellence", "🟢 Deep Green", "#0E5228"
        band_meaning = "High, balanced and well-evidenced value; maintain assurance and outcome monitoring."

    all_above_3 = all(v >= 3.0 for v in vals)

    # 4. Decision outcome
    if not gate_passed:
        decision = "DECLINE / REMEDIATE"
        rationale = ("Integrity gate failure: " + "; ".join(gate_failures) +
                     ". " + GATE_RULE + " Remediate before any scoring is relied upon.")
        verdict_colour = "#C62828"
    elif override:
        names = ", ".join(PILLARS[p]["name"] for p in failing)
        decision = "REDESIGN"
        rationale = (f"Non-compensatory override: {names} scored at or below "
                     f"{NON_COMPENSATORY_THRESHOLD}. A high total cannot compensate for a material "
                     f"failure — regardless of TIV ({tiv}).")
        verdict_colour = "#C62828"
    elif confidence == "D":
        decision = "NOT SCORABLE"
        rationale = ("Evidence confidence is Insufficient (D). Do not score as achieved; "
                     "obtain admissible evidence before any commitment decision.")
        verdict_colour = "#C62828"
    elif classification in ("Strong", "Balanced Excellence"):
        decision = "COMMIT (conditional on verification)" if confidence in ("A", "B") else "CONDITIONAL COMMIT"
        rationale = band_meaning + (
            "" if confidence == "A" else
            f" Evidence confidence {confidence} — {CONFIDENCE[confidence][2].lower()}.")
        verdict_colour = colour
    elif classification == "Acceptable":
        if all_above_3:
            decision = "CONDITIONAL COMMIT"
            rationale = band_meaning
        else:
            decision = "REDESIGN"
            rationale = ("The Acceptable band requires every pillar at 3.0 or above. "
                         f"{PILLARS[weakest]['name']} is below that threshold.")
        verdict_colour = colour
    else:
        decision = "DECLINE / REDESIGN"
        rationale = band_meaning
        verdict_colour = colour

    return {
        "tiv": tiv,
        "pillar_scores": {p: round(float(pillar_scores.get(p, 0.0)), 2) for p in PILLAR_ORDER},
        "classification": classification,
        "band_signal": band,
        "band_colour": colour,
        "band_meaning": band_meaning,
        "balanced_excellence": balanced_excellence,
        "gate_passed": gate_passed,
        "gate_failures": gate_failures,
        "non_compensatory_override": override,
        "failing_pillars": failing,
        "weakest_pillar": weakest,
        "min_score": round(min_score, 2),
        "all_pillars_above_3": all_above_3,
        "confidence": confidence,
        "confidence_label": CONFIDENCE[confidence][0],
        "confidence_use": CONFIDENCE[confidence][2],
        "decision": decision,
        "rationale": rationale,
        "verdict_colour": verdict_colour,
        "disclaimer": ("Preliminary profile only. FIPRE® is a decision-support framework, not a "
                       "decision, approval, rating or assurance opinion. Integrity failures, pillar "
                       "overrides, mandatory requirements and specialist judgement remain with the "
                       "accountable decision-maker."),
    }


# ──────────────────────────────────────────────────────────────────────────────
# FIPRE® Lite — 10-question concept screen
# ──────────────────────────────────────────────────────────────────────────────
LITE_QUESTIONS = [
    ("function", "Is the service need clearly defined, with demand evidence and options analysis?"),
    ("function", "Are applicable codes, standards and safety requirements identified and addressed?"),
    ("function", "Is there a funded operations and maintenance model with a competent operator?"),
    ("impact", "Have environmental and social impacts been assessed using the mitigation hierarchy?"),
    ("impact", "Is there an accessible grievance and remedy mechanism?"),
    ("prosperity", "Is the economic case credible, with affordability and fiscal exposure tested?"),
    ("resilience", "Has the design been tested against forward-looking climate scenarios, not historical data?"),
    ("resilience", "Is residual risk explicitly owned and adaptation funded?"),
    ("equity", "Is there disaggregated evidence on who benefits, who pays and who bears risk?"),
    ("equity", "Do affected groups have meaningful influence, rather than tokenistic representation?"),
]


def lite_screen(answers: List[str]) -> Dict:
    """answers: list of 'yes' | 'unsure' | 'no'. Returns a screening result."""
    no = answers.count("no")
    unsure = answers.count("unsure")
    flagged = {}
    for (pillar, _), a in zip(LITE_QUESTIONS, answers):
        if a in ("no", "unsure"):
            flagged.setdefault(pillar, 0)
            flagged[pillar] += 1

    if no >= 3:
        level, colour = "POTENTIAL FATAL FLAWS", "#C62828"
        msg = (f"{no} potential fatal flaws flagged. These require immediate investigation "
               "before the concept proceeds to appraisal.")
    elif no > 0:
        level, colour = "AREAS FLAGGED", "#E58A00"
        msg = (f"{no} area(s) flagged and {unsure} uncertain. Investigate the flagged areas "
               "before committing resources to full appraisal.")
    elif unsure >= 3:
        level, colour = "EVIDENCE GAPS", "#E58A00"
        msg = (f"{unsure} areas uncertain. Evidence gaps mean the concept is not yet screenable — "
               "gather evidence before appraisal.")
    else:
        level, colour = "NO FATAL FLAWS FLAGGED", "#1B7A3E"
        msg = ("No fatal flaws flagged at concept stage. Proceed to full FIPRE® assessment. "
               "This screen is not an approval.")
    return {"level": level, "colour": colour, "message": msg,
            "no_count": no, "unsure_count": unsure, "flagged_pillars": flagged}


TRADEMARK = ("FIPRE® and the FIPRE Emblem are registered trademarks owned exclusively by "
             "Eugene Itua and the Africa Green Economy and Sustainability Institute (AGESI). "
             "Unauthorized use, duplication, modification or distribution is prohibited.")

NOT_A_CLAIM = ("FIPRE™ is a structured decision-support framework. It is not a law, engineering "
               "code, safeguard system, investment rating, certification scheme, financial "
               "recommendation, or institutional endorsement.")
