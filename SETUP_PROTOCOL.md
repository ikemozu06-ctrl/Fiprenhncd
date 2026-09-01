# AGOI™ Platform — Setup (flat layout)

This build is **flattened on purpose** to fix the `ModuleNotFoundError: No module
named 'agoi'` you saw. Everything sits at the top level — no `app/` subfolder.

## Why the last deploy failed

Your log showed the app running from `streamlit_app.py` at the repo root, but the
`agoi/` folder wasn't beside it, so `from agoi import config` failed. This version
puts `streamlit_app.py`, `agoi/`, and `pages/` ALL at the same level — exactly what
your repo expects.

## Most reliable upload: GitHub Desktop (no command line)

1. Install GitHub Desktop -> https://desktop.github.com (free).
2. Sign in. File -> New Repository -> name it -> Create.
3. Click "Show in Explorer/Finder" to open that folder.
4. Unzip this download. Copy EVERYTHING from inside the unzipped folder into the
   repo folder: streamlit_app.py, the agoi folder, the pages folder,
   requirements.txt, all of it. Copy the CONTENTS, not the outer folder.
5. In GitHub Desktop: type a summary -> Commit to main -> Publish repository
   (uncheck "private" for the free tier).

Uploads every file and folder atomically. Nothing gets dropped.

## Deploy on Streamlit Cloud

share.streamlit.io -> New app -> three inputs:
- Repository: your repo
- Branch: main
- Main file path: streamlit_app.py    <- just this, NO app/ prefix

Deploy. Sidebar shows all 7 pages including AfCFTA and Corridor Simulator.

## Verify repo before deploying (30 sec)

Repo root must show, side by side:
    streamlit_app.py
    _shared.py
    agoi/          <- engine, must sit next to streamlit_app.py
    pages/         <- 7 files
    requirements.txt
    runtime.txt
    .streamlit/
Click agoi/ -> must contain afcfta/, data_sources/, scoring/.
Click pages/ -> must contain 7 files.

## Live data (optional)

- World Bank: automatic in Live/Mixed mode once deployed. No key.
- AfDB: free key from developer.iatistandard.org (subscribe to Datastore API),
  then app Settings -> Secrets:  IATI_API_KEY = "your-key-here"
- AfCFTA: works immediately (scenario explorer, placeholder elasticities, labelled).

## If it still errors

Manage app -> log panel shows the real error. If still "No module named 'agoi'",
the agoi folder didn't upload — confirm on github.com that agoi/ sits directly
next to streamlit_app.py.
