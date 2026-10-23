import streamlit as st
import os

# Bridge Streamlit secrets to environment variables FIRST
# This must run before any imports that initialize the OpenAI client
try:
    if "DEEPSEEK_API_KEY" in st.secrets:
        os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
    if "VIRUSTOTAL_API_KEY" in st.secrets:
        os.environ["VIRUSTOTAL_API_KEY"] = st.secrets["VIRUSTOTAL_API_KEY"]
except Exception:
    pass  # Falls back to local .env

# Now import the client (which reads from os.environ)
from src.deepseek_client import analyze_email
# ... rest of your app
