"""Shared helpers for AGOI Streamlit pages."""
import os
import sys

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

from agoi import config            # noqa: E402
from agoi.pipeline import run      # noqa: E402


@st.cache_data(show_spinner=False, ttl=60 * 60)
def load_data(mode: str):
    return run(mode=mode)


def get_data():
    """Load data using the mode chosen on the main page (defaults to mix)."""
    mode = st.session_state.get("data_mode", "mix")
    return load_data(mode)


def band_pill(label: str) -> str:
    return (f'<span style="display:inline-block;padding:.18rem .7rem;border-radius:999px;'
            f'color:#fff;font-weight:600;font-size:.82rem;background:{config.band_colour(label)}">'
            f'{label}</span>')


def inject_css():
    st.markdown("""
    <style>
    .main .block-container {padding-top: 2rem; max-width: 1200px;}
    h1, h2, h3 {color:#1F3864;}
    .small-note {color:#666; font-size:.83rem;}
    </style>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# BRANDING — AGESI / NEC logo
# ══════════════════════════════════════════════════════════════════════════════
# Drop your logo into the assets/ folder. No code changes needed.
#
#   assets/logo.png        ← main logo (sidebar + hero).  PNG or SVG.
#   assets/icon.png        ← optional small square icon for the browser tab.
#                            If absent, logo.png is used; if that's absent too,
#                            the app falls back to the 🌍 emoji.
#
# Recommended: logo.png roughly 400x120 px (wide), icon.png square 128x128 px,
# transparent background so it sits cleanly on the dark sidebar.
# ══════════════════════════════════════════════════════════════════════════════

_ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

_LOGO_CANDIDATES = ["logo.png", "logo.svg", "logo.jpg", "logo.jpeg", "logo.webp"]
_ICON_CANDIDATES = ["icon.png", "icon.svg", "icon.jpg", "favicon.png"]


def _find_asset(candidates):
    """Return the path of the first asset that exists, else None."""
    for name in candidates:
        p = os.path.join(_ASSET_DIR, name)
        if os.path.isfile(p):
            return p
    return None


def logo_path():
    """Path to the main logo, or None if not supplied yet."""
    return _find_asset(_LOGO_CANDIDATES)


def page_icon(default="🌍"):
    """
    Browser-tab icon. Uses assets/icon.* if present, else assets/logo.*,
    else the emoji default. Safe to pass straight to st.set_page_config().
    """
    return _find_asset(_ICON_CANDIDATES) or logo_path() or default


def show_logo():
    """
    Put the logo at the top of the sidebar on every page.
    Silently does nothing if no logo file has been added yet.
    Call once per page, immediately after st.set_page_config().
    """
    p = logo_path()
    if not p:
        return
    try:
        # Streamlit >= 1.35 renders this above the page nav on every page.
        st.logo(p, size="large")
    except Exception:
        # Older Streamlit: fall back to a sidebar image.
        try:
            st.sidebar.image(p, use_container_width=True)
        except Exception:
            pass


def hero_logo(width=150):
    """
    Render the logo inline in the main body (used in the home-page hero).
    Returns True if a logo was drawn, False if none is available.
    """
    p = logo_path()
    if not p:
        return False
    try:
        st.image(p, width=width)
        return True
    except Exception:
        return False
