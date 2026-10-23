import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

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

def analyze_email(email_text: str) -> dict:
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": email_text[:4000]}  # truncate to control cost
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content