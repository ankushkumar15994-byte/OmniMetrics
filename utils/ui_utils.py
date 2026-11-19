import html
import os
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(__file__))


def load_css():
    """Load the shared Midnight Pro theme."""
    css_path = os.path.join(ROOT, "assets", "style.css")
    try:
        with open(css_path, "r", encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    except OSError:
        st.warning("The application stylesheet could not be loaded.")


def page_header(title: str, subtitle: str, eyebrow: str = "OMNIMETRICS WORKSPACE"):
    """Render a consistent page title block (arguments are trusted page copy)."""
    st.markdown(
        f'<div class="om-eyebrow">{html.escape(eyebrow)}</div>'
        f'<div class="om-page-title">{html.escape(title)}</div>'
        f'<div class="om-page-subtitle">{html.escape(subtitle)}</div>',
        unsafe_allow_html=True,
    )


def brand():
    """Render sidebar product identity."""
    st.sidebar.markdown(
        '<div class="om-brand"><div class="om-mark">O</div>'
        '<div><div class="om-brand-name">OmniMetrics</div>'
        '<div class="om-brand-sub">Intelligence workspace</div></div></div>',
        unsafe_allow_html=True,
    )


def require_login():
    """Stop access to protected pages when no user session exists."""
    if "user_id" not in st.session_state:
        st.warning("Please log in to access this workspace.")
        st.page_link("pages/01_Login.py", label="Go to Login", icon="🔐")
        st.stop()
