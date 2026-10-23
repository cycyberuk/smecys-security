import streamlit as st
import os

# Set page config MUST be the first Streamlit command
st.set_page_config(page_title="AI Incident Response Dashboard", page_icon="🔐", layout="wide")

# Import the client. 
# Note: The new src/deepseek_client.py handles st.secrets internally.
from src.deepseek_client import analyze_email

# --- UI Setup ---
st.title("🔐 AI Incident Response Dashboard")
st.markdown("*(Nigerian SME Edition)*")
st.markdown("---")

# Create Tabs
tab1, tab2, tab3 = st.tabs(["🔍 Analysis", "📜 History", "⚙️ Settings"])

with tab1:
    st.subheader("Analyze Threat Indicators")
    
    # Input Type Selection
    input_type = st.radio("Select Input Type:", ["Email Text", "URL", "File Hash"], horizontal=True)
    
    # Text Area for Input
    if input_type == "Email Text":
        user_input = st.text_area("Paste email content here:", height=200, placeholder="Dear customer, your account has been suspended...")
    elif input_type == "URL":
        user_input = st.text_area("Enter URL(s) to analyze (one per line):", height=100, placeholder="http://suspicious-link.xyz/login")
    else:
        user_input = st.text_area("Enter File Hash (MD5/SHA256):", height=100, placeholder="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

    # Language Selection
    language = st.selectbox("Output Language:", ["English", "Pidgin", "Yoruba", "Hausa", "Igbo"])
    
    # Analyze Button
    if st.button("Analyze 🔍", type="primary"):
        if not user_input.strip():
            st.warning("Please enter some text to analyze.")
        else:
            with st.spinner("Analyzing threat indicators via DeepSeek..."):
                try:
                    # Prepare input for the LLM
                    prompt_input = f"Input Type: {input_type}\nLanguage: {language}\n\nContent:\n{user_input}"
                    
                    # Call the API
                    result_json = analyze_email(prompt_input)
                    
                    # Parse the JSON result
                    import json
                    result = json.loads(result_json)
                    
                    # --- Display Results ---
                    st.markdown("### Analysis Results")
                    
                    verdict = result.get("verdict", "unknown").lower()
                    confidence = result.get("confidence", 0)
                    red_flags = result.get("red_flags", [])
                    reasoning = result.get("reasoning", "No reasoning provided.")
                    
                    # Color-coded verdict
                    if verdict == "malicious":
                        st.error(f"🛑 **VERDICT: MALICIOUS** (Confidence: {confidence}%)")
                    elif verdict == "suspicious":
                        st.warning(f"⚠️ **VERDICT: SUSPICIOUS** (Confidence: {confidence}%)")
                    else:
                        st.success(f"✅ **VERDICT: BENIGN** (Confidence: {confidence}%)")
                    
                    st.markdown("#### 📋 Reasoning")
                    st.info(reasoning)
                    
                    if red_flags:
                        st.markdown("#### 🚩 Red Flags Found")
                        for flag in red_flags:
                            st.markdown(f"- {flag}")
                            
                    st.markdown("#### 🛡️ Recommended Actions")
                    if verdict in ["malicious", "suspicious"]:
                        st.markdown("- **Do not click any links or download attachments.**")
                        st.markdown("- Report to ngCERT via their portal.")
                        st.markdown("- Block the sender domain or IP.")
                    else:
                        st.markdown("- No immediate action required, but remain vigilant.")

                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")

with tab2:
    st.subheader("Analysis History")
    st.info("History logging is currently disabled in the cloud deployment to protect user privacy and manage database limits. In a production environment, this would query the SQLite/PostgreSQL database.")

with tab3:
    st.subheader("Settings & Information")
    st.markdown("""
    **System Information:**
    - **LLM Engine:** DeepSeek (deepseek-chat)
    - **Threat Intel:** VirusTotal API v3 (Live enrichment in progress)
    - **Cost per analysis:** ~ ₦105 (USD $0.07)
    
    **About this project:**
    This dashboard is part of an empirical evaluation of LLM-assisted incident triage for resource-constrained SMEs.
    """)
    
    if st.button("Clear Cache & Reload"):
        st.cache_resource.clear()
        st.rerun()
