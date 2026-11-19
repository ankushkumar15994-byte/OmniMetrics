import streamlit as st
import os

def load_css():
    """Loads the global CSS file and injects sidebar branding into Streamlit."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
    # Inject high-performance sidebar branding
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 4px 14px 4px; border-bottom: 1px solid #1e293b; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 34px; height: 34px; border-radius: 8px; background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%); display: flex; align-items: center; justify-content: center; font-size: 18px; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.45); flex-shrink: 0;">
                    📊
                </div>
                <div style="min-width: 0;">
                    <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc; letter-spacing: -0.025em; line-height: 1.2;">
                        Omni<span style="color: #6366f1;">Metrics</span>
                    </div>
                    <div style="font-size: 0.72rem; color: #908fa0; letter-spacing: 0.04em; text-transform: uppercase; font-weight: 600;">
                        Enterprise AI Studio
                    </div>
                </div>
            </div>
            <div style="margin-top: 10px; display: inline-flex; align-items: center; gap: 6px; padding: 3px 8px; border-radius: 9999px; background: rgba(69, 223, 164, 0.1); border: 1px solid rgba(69, 223, 164, 0.25); font-size: 0.72rem; color: #45dfa4; font-weight: 600;">
                <span class="pulse-dot"></span> Telemetry Active • 99.98%
            </div>
        </div>
        """, unsafe_allow_html=True)
