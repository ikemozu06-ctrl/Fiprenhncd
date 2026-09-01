# AGOI™ ESG Platform — MVP

**Africa Green Opportunity Index** — an interactive ESG decision-support dashboard
that scores all 54 African countries 0–100 across six weighted pillars, with full
data provenance and confidence flags.

Built for **Natural Eco Capital**. This is the Phase 1–5 MVP described in the
*AGOI™ Technical Development Manual v2.0*: a faithful implementation of the
six-pillar scoring engine, served as a Streamlit web app.

---

## What it does

- **Continental ranking** of 54 African countries by AGOI score, coloured by opportunity band.
- **Country profile** — pillar radar, scores, and the full **audit trail** behind every number.
- **Africa map** — choropleth by AGOI score or data coverage.
- **Pillar comparison** — radar overlay of up to five countries.
- **Scenario tool** — adjust pillar weights and watch the ranking re-rank instantly (Tier 1 weight sensitivity).
- **Export centre** — download scores, the audit trail, and an Excel workbook; full methodology published in-app.

### Data modes (chosen in the sidebar)
| Mode | What it shows |
|------|---------------|
| **Mixed** (default) | Live World Bank data, with any gaps filled by clearly-flagged demo values. |
| **Live** | World Bank only. |
| **Demo** | Synthetic, deterministic sample data — always labelled, never presented as real. |

Every value carries a confidence flag (`measured` / `interpolated` / `proxy` / `default`)
and each country gets a **data-coverage score** so real data is always distinguishable
from fallbacks.

---

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py
```

Then open http://localhost:8501

---

## Deploy free on Streamlit Community Cloud

1. **Create a GitHub repo** and push this folder to it:
   ```bash
   git init
   git add .
   git commit -m "AGOI ESG Platform MVP"
   git branch -M main
   git remote add origin https://github.com/<your-username>/agoi-platform.git
   git push -u origin main
   ```
2. Go to **https://share.streamlit.io** and sign in with GitHub (free).
3. Click **New app** → pick your repo → set:
   - **Branch:** `main`
   - **Main file path:** `app/streamlit_app.py`
4. Click **Deploy**. First build takes a few minutes. You get a public URL like
   `https://<your-app>.streamlit.app` that you can share with the board / clients.

> Streamlit Cloud has open internet access, so **Live / Mixed modes will pull real
> World Bank data** once deployed (unlike a restricted local sandbox).

### Alternative free host: Render
- New → **Web Service** → connect repo.
- Build command: `pip install -r requirements.txt`
- Start command: `streamlit run app/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`

---

## Project structure

```
agoi-platform/
  agoi/                      # the scoring engine (importable package)
    config.py                # weights, bands, thresholds  (tune here, not in code)
    registry.py              # 54 countries (ISO alpha-3) + indicator registry
    pipeline.py              # orchestration: live → mix → demo fallback
    data_sources/
      worldbank.py           # live World Bank API pull (keyed on ISO alpha-3)
      demo.py                # deterministic, flagged synthetic data
    scoring/
      normalization.py       # direction → winsorize → min-max (0–100)
      engine.py              # pillar aggregation + AGOI + audit table + coverage
  app/
    streamlit_app.py         # home / continental ranking
    _shared.py               # shared data loader + helpers
    pages/
      1_Country_Profile.py
      2_Africa_Map.py
      3_Pillar_Comparison.py
      4_Scenario_Tool.py
      5_Export_and_Methodology.py
  requirements.txt
  README.md
```

---

## Methodology (summary)

Each indicator flows through one consistent pipeline:

```
raw value → direction alignment → winsorization (5th/95th pct)
          → min-max scale to 0–100 → weighted pillar aggregation
          → weighted AGOI score → opportunity band
```

**Pillar weights:** Sectoral 25% · Policy 20% · Finance 20% · Bankability 15% ·
Resilience 10% · Inclusive 10%.

**Bands:** Core Green (80–100) · Growth Green (60–80) · Emerging (40–60) ·
High-Friction (20–40) · Red (0–20).

Full methodology, indicator registry and band readings are published on the
**Export & methodology** page inside the app.

---

## Data sources

| Source | Module | Feeds | Access |
|--------|--------|-------|--------|
| World Bank (WDI / WGI) | `data_sources/worldbank.py` | All six pillars | Free public JSON API, keyed on ISO alpha-3 |
| AfDB project/lending | `data_sources/afdb.py` | **Bankability pillar** | IATI Datastore (AfDB reporting-org `46002`), aggregated per country |
| Demo (synthetic) | `data_sources/demo.py` | Gap-fill / offline | Deterministic, always flagged `default` |

### ⚠️ One-time AfDB verification (do this after first deploy)

The AfDB connector targets the public **IATI Datastore**, but the live response
shape can vary and could not be reached from the build sandbox. After deploying:

1. Open the app on Streamlit Cloud in **Live** or **Mixed** mode.
2. Go to **Country profile → Nigeria → Audit trail** and look for the row
   *"AfDB active project commitments (proxy)"*.
   - If its **Source** reads `AfDB (IATI Datastore)` → live AfDB data is flowing. ✅
   - If it reads `DEMO (synthetic)` → the live pull returned nothing; the platform
     safely fell back. Paste me a sample of what the IATI endpoint returns and I'll
     adjust the parser in `_parse_activities()` (the single place that needs it).

AfDB values are flagged `confidence="proxy"` because project commitments are an
indirect signal of bankability, not a direct market measure.

## Notes & roadmap

- This MVP implements the **sovereign** scoring layer. The NGX corporate ESG module,
  public validation portal, monitoring/alerting engine and the AGOF™ fund layer are
  specified in the *AGOI™ ESG Platform — Full Product Specification v1.0* and are the
  next build phases.
- Some World Bank governance indicator codes (rule of law, regulatory quality) should
  be validated against the current WB catalogue; the engine degrades gracefully if a
  series returns empty.
- The scoring engine is in `agoi/` and is independent of the UI — it can be reused by
  a future FastAPI backend without change.

© Natural Eco Capital. Internal MVP build.

---

## AfCFTA Module (vertical slice)

Two new pages: **AfCFTA** (readiness + country policy scenarios) and
**Corridor Simulator** (Lagos–Abidjan, with the Lagos flood → trade-risk linkage).

```
agoi/afcfta/
  config.py       6 indicators, 5 levers, Lagos–Abidjan corridor, Lagos trade-risk
  elasticity.py   β matrix — EVERY coefficient carries provenance + uncertainty range
  engine.py       protocol equations, with uncertainty propagated to every output
  data.py         baseline values (all flagged confidence="proxy")
```

### ⚠️ Read this before showing anyone the numbers

All 47 elasticity coefficients are **structural placeholders** (`provenance="assumed"`).
They make the engine runnable end-to-end; they are **not findings**. Accordingly:

- Every simulator output is a **range**, never a point estimate.
- The UI shows a permanent "SCENARIO EXPLORER — NOT A FORECASTER" banner.
- The **Elasticity governance** tab shows the provenance counts and the research plan.

**The first substantive research task of this module is replacing those placeholders**
via (1) econometric estimation, (2) literature-derived priors, or (3) structured expert
elicitation — each of which sets a stronger `provenance` flag. See `ELASTICITY_ROADMAP`
in `agoi/afcfta/elasticity.py`.

The six AfCFTA indicators (GEX, DIV, GJOB, CIRC, LCMAN, GLCOR) are **not** standard World
Bank series and have no public API. Baselines are proxy estimates pending acquisition from
the AfCFTA Secretariat, UNCTAD, UNECA and AfDB.

---

## Natural Capital Module (Dr. Itua's valuation layer)

New page: **Natural Capital** — three tabs implementing spatial accounting →
monetary valuation → FIPRE screening.

```
agoi/natcap/
  assets.py      10 flagship African assets (Congo Basin, Rift geothermal, DRC
                 cobalt, Niger Delta, Okavango…) classified by ecosystem service
                 (provisioning / regulating / cultural). All values proxy-flagged.
  valuation.py   Shadow-pricing & avoided-cost engine. Maps each service stream to
                 an investable instrument (carbon credits, resilience bonds, etc.).
                 Every figure is a RANGE driven by adjustable price assumptions.
  fipre.py       Function · Impact · Prosperity · Resilience · Equity.
                 NON-COMPENSATORY: fail ANY dimension below threshold → project
                 REJECTED. A strong score cannot rescue a failing one.
```

**Honesty carried through:** asset magnitudes and valuations are order-of-magnitude
proxies from public literature, reported as ranges, each with a provenance note.
They are planning figures, not audited reserves or price quotes — replace with
primary survey / biomass / geothermal-atlas data before underwriting.

---

## Nigeria State Dashboard + AGESI Instruments (v3)

**New pages:** `9_Nigeria_States.py`, `10_AGESI_Instruments.py`
**New engines:** `agoi/nigeria/` (states.py, index.py), `agoi/agesi/` (instruments.py)

### Real subnational data
The 36 states + FCT are now scored on **real, cited data** — SPP Nigeria climate
governance, Global Solar Atlas irradiation, flood risk, Global Data Lab/UNDP HDI,
Invictus Africa Womanity Index, InfraCredit projects, state budgets. This replaces
the synthetic state model flagged as a defect in Technical Manual v1.0.

### ⚠️ Two columns excluded for data quality
The source workbook's "Bankability – Fiscal Performance Ranking" columns (BudgIT
2022 & 2023) are **excluded**: their values rise strictly monotonically in
alphabetical order of state (Abia 0.474 → Zamfara 2.561), showing the column was
sorted independently of the state labels and is misaligned. Using them would have
made Zamfara Nigeria's best-run state. Bankability is proxied by InfraCredit
project counts (flagged proxy) pending a corrected source.

### AGESI instruments
- **CGV** — guarantee calculator; exact amortisation maths, with the rate-reduction
  spread as an adjustable policy parameter (not a market quote).
- **ETIV** — Environmental Transaction Integrity Value (0–1), weighted across
  additionality, permanence, verification, leakage, co-benefits.
- **NEAI** — credit issuance gated on BOTH the FIPRE screen (incl. Impact floor)
  and the ETIV floor. Blocked issuance states the exact blockers.

---

## Adding your logo

Drop your logo into the **`assets/`** folder — no code changes needed:

| File | Where it appears | Recommended |
|---|---|---|
| `assets/logo.png` | Sidebar (every page) **and** beside the home-page title | ~400×120 px, transparent PNG |
| `assets/icon.png` | Browser tab icon (optional) | 128×128 px square |

`.svg`, `.jpg` and `.webp` also work. If no logo is present the app falls back to
the 🌍 emoji with no broken images.

---

## Enabling AfDB data (optional)

The platform runs fully without this. AfDB project data is an **optional enhancement**
to the Bankability pillar — it adds a signal for where the African Development Bank is
actually deploying capital.

**Setup (~5 minutes, free):**

1. Go to **https://developer.iatistandard.org** and create a free account.
   (AfDB publishes its project pipeline to the IATI standard; the IATI Datastore
   serves it, and it requires a free key.)
2. Once signed in, go to **Products → Datastore API → Subscribe**.
3. Open your **Profile** and copy your **Primary subscription key**.
4. In your Streamlit app: **Manage app → Settings → Secrets**, and paste:

   ```
   IATI_API_KEY = "paste-your-key-here"
   ```

5. **Save.** The app reboots and AfDB data flows. Confirm under
   *"Data provenance & technical details"* on the home page — AfDB should show
   ✅ with a count of activities fetched.

If the key is wrong or the service is down, the app degrades gracefully: AfDB is
simply omitted and every other pillar is unaffected.
