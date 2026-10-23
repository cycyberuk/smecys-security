import os
import streamlit as st
from openai import OpenAI
# ... other imports

# --- START OF FIX ---
# Streamlit Cloud stores secrets in st.secrets, not as environment variables.
# This bridges them so os.environ.get() works on the cloud.
try:
    if "DEEPSEEK_API_KEY" in st.secrets:
        os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]
    if "VIRUSTOTAL_API_KEY" in st.secrets:
        os.environ["VIRUSTOTAL_API_KEY"] = st.secrets["VIRUSTOTAL_API_KEY"]
except Exception:
    pass # This allows local development with .env files to still work
# --- END OF FIX ---

# Now the rest of your code can stay the same
client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
