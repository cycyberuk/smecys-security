import streamlit as st
import os
import json
import time
from openai import OpenAI

@st.cache_resource
def get_openai_client():
    # 1. Try Streamlit Cloud secrets first
    # 2. Fall back to local environment variables (.env)
    try:
        api_key = st.secrets.get("DEEPSEEK_API_KEY")
    except Exception:
        api_key = None
        
    if not api_key:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not found in st.secrets or environment variables.")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

# Initialize the client
client = get_openai_client()

SYSTEM_PROMPT = """You are a cybersecurity analyst detecting phishing and social engineering in emails.

CRITICAL: Phishing emails often look like routine notifications. Do NOT assume an email is benign just because it is well-written, short, or professional. Many phishing emails imitate legitimate service notifications (account alerts, password resets, invoice attachments, delivery notices).

Analyze for these indicators:

1. LINK-BASED THREATS (highest priority):
   - Links to look-alike domains (e.g., paypa1.com, micros0ft.net)
   - URLs with suspicious TLDs (.xyz, .top, .club, .tk)
   - Links that do not match the claimed sender domain
   - URL shorteners hiding the real destination
   - Login or verification pages asking for credentials

2. URGENCY AND FEAR:
   - "Account suspended", "immediate action required", "within 24 hours"
   - Threats of account closure, legal action, or financial loss
   - Pressure to click a link or open an attachment quickly

3. AUTHORITY IMPERSONATION:
   - Claims to be from a bank, government agency, IT department, or executive
   - Mismatch between claimed sender identity and actual sender domain

4. CREDENTIAL OR DATA REQUESTS:
   - Requests for passwords, OTPs, PINs, credit card numbers, or bank details
   - Links to forms asking for personal information

5. CONTENT RED FLAGS:
   - Generic greetings ("Dear Customer") instead of your name
   - Grammar, spelling, or formatting errors
   - Unexpected attachments (invoices, receipts, shipping notices)

6. NIGERIAN-SPECIFIC PATTERNS (if present):
   - CBN grant offers, OTP harvesting, local bank impersonation

Return a JSON object with exactly these fields:
{
  "verdict": "benign" or "suspicious" or "malicious",
  "confidence": integer from 0 to 100,
  "red_flags": ["list of specific indicators found"],
  "reasoning": "one or two sentences explaining the verdict"
}"""

def analyze_email(email_text: str, language: str = 'en', retry_count: int = 3) -> str:
    """Analyze text using DeepSeek API with retry logic."""
    
    for attempt in range(retry_count):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": email_text[:4000]} # Truncate to control token limits
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
            
        except Exception as e:
            if attempt == retry_count - 1:
                raise e
            time.sleep(2 ** attempt) # Exponential backoff
