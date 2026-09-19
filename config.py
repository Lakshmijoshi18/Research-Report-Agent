"""
Shared config -- figures out where to get the Gemini API key from,
depending on whether the code is running locally or deployed on
Streamlit Community Cloud.
"""

import os

API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    # Not found as a local environment variable -- try Streamlit secrets
    # (this only works when running inside a Streamlit app / on Streamlit Cloud)
    try:
        import streamlit as st
        API_KEY = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY not found. Set it as an environment variable locally, "
        "or add it under 'Secrets' in your Streamlit Cloud app settings."
    )
