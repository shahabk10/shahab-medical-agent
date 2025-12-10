# streamlit_app.py

import os
import base64
import io
import time
from PIL import Image
import requests
import streamlit as st
from google import genai
from fpdf import FPDF
from gtts import gTTS

# -------------------------------------------------------------
# STRICT FREE DEPLOY PATH
# Deploy on Streamlit Cloud (free) → share link to anyone.
# Put GEMINI_API_KEY inside st.secrets
# -------------------------------------------------------------

API_KEY = st.secrets["GEMINI_API_KEY"]
os.environ["GEMINI_API_KEY"] = API_KEY
client = genai.Client()
model_name = "gemini-2.5-flash"

# -------------------------------------------------------------
# NEARBY HOSPITAL SEARCH USING GOOGLE MAPS STATIC → FREE
# (Fully free, does not require Google Maps API)
# -------------------------------------------------------------

def get_static_map(lat, lon, zoom=14, size="600x400"):
    url = f"https://static-maps.yandex.ru/1.x/?ll={lon},{lat}&z={zoom}&size={size}&l=map"
    return url

# Pre-loaded global hospital list (manual safe offline version)
# Will always work and never require paid API.
HOSPITALS = [
    {
        "name": "Shifa International Hospital",
        "lat": 33.6775,
        "lon": 73.0499,
        "phone": "+92-51-8464646",
        "email": "info@shifa.com.pk"
    },
    {
        "name": "PIMS Hospital Islamabad",
        "lat": 33.7080,
        "lon": 73.0653,
        "phone": "+92-51-9261170",
        "email": "support@pims.gov.pk"
    },
    {
        "name": "Maroof International Hospital",
        "lat": 33.7193,
        "lon": 73.0555,
        "phone": "+92-51-111-644-911",
        "email": "info@maroof.com.pk"
    }
]

# -------------------------------------------------------------
# EMERGENCY DETECTOR
# -------------------------------------------------------------

def check_emergency(text):
    keys = ["heart attack", "chest pain", "cannot breathe", "can't breathe", "bleeding", "stroke", "unconscious"]
    t = text.lower()
    return any(k in t for k in keys)

# -------------------------------------------------------------
# REPORT PDF
# -------------------------------------------------------------

class UltimateHealthReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Shahab Medical Hospital', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'AI Hospital, Pakistan', 0, 1, 'C')
        self.set_draw_color(0, 50, 150)
        self.set_line_width(1)
        self.line(10, 30, 200, 30)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'CONFIDENTIAL | AI Generated | Not for Medical Use', 0, 0, 'C')

    def chapter(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 240, 255)
        self.cell(0, 8, title, 0, 1, 'L', 1)
        self.ln(2)

    def text_body(self, txt):
        safe = txt.encode('latin-1', 'replace').decode('latin-1')
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, safe)
        self.ln(1)

# -------------------------------------------------------------
# IMAGE ANALYSIS
# -------------------------------------------------------------

def analyze_image(file_bytes):
    img = Image.open(io.BytesIO(file_bytes))
    prompt = "Describe medical findings in this image. Short professional output."
    r = client.models.generate_content(model=model_name, contents=[prompt, img])
    return r.text

# -------------------------------------------------------------
# FINAL REPORT
# -------------------------------------------------------------

def generate_final_report(chat, vision):
    prompt = f"""
Create a structured medical-style report.
CHAT: {chat}
IMAGE: {vision}

Sections:
- Patient Details
- Symptoms Summary
- AI Triage Analysis
- Recommendations
- Routine
"""
    r = client.models.generate_content(model=model_name, contents=[prompt])
    return r.text

# -------------------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------------------

st.set_page_config(page_title="Ultimate Medical Agent", layout="wide")
st.markdown("""
<style>
body {background: linear-gradient(to bottom right, #d3e2ff, #ffffff);} 
</style>
""", unsafe_allow_html=True)

st.title("Ultimate AI Medical Agent — International Prototype")

# Sidebar Navigation
page = st.sidebar.radio("Navigate", ["Agent", "Nearby Hospitals", "Reports"])

# =============================================================
# PAGE 1 — MEDICAL AGENT
# =============================================================

if page == "Agent":
    st.header("AI Medical Consultation")

    chat_history = st.session_state.get("chat", [])
    vision_log = st.session_state.get("vision", "None")

    user_text = st.text_input("Your Message")
    uploaded_img = st.file_uploader("Upload Symptom/Prescription Image", type=["jpg", "png", "jpeg"])

    if uploaded_img:
        vision_log = analyze_image(uploaded_img.read())
        st.session_state["vision"] = vision_log
        st.success("Image analyzed.")

    if user_text:
        if check_emergency(user_text):
            st.error("Emergency Detected. Immediately go to hospital or call 1122.")
        else:
            r = client.models.generate_content(model=model_name, contents=[user_text])
            reply = r.text
            chat_history.append("You: " + user_text)
            chat_history.append("Agent: " + reply)
            st.session_state["chat"] = chat_history

    st.subheader("Conversation")
    for c in chat_history[-12:]:
        st.write(c)

# =============================================================
# PAGE 2 — HOSPITALS
# =============================================================

if page == "Nearby Hospitals":
    st.header("Nearby Hospital Directory (Always Free)")

    for h in HOSPITALS:
        st.subheader(h["name"])
        st.write("Phone:", h["phone"])
        st.write("Email:", h["email"])

        map_url = get_static_map(h["lat"], h["lon"])
        st.image(map_url, caption=h["name"])
        st.markdown("---")

# =============================================================
# PAGE 3 — REPORT
# =============================================================

if page == "Reports":
    st.header("Generate Full Medical PDF Report")

    if st.button("Generate Report"):
        chat = "\n".join(st.session_state.get("chat", []))
        vision = st.session_state.get("vision", "None")

        final_text = generate_final_report(chat, vision)

        pdf = UltimateHealthReport()
        pdf.add_page()

        for line in final_text.split("\n"):
            if line.strip().upper().startswith("PATIENT"):
                pdf.chapter("Patient Details")
            pdf.text_body(line)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")
        st.download_button("Download PDF", data=pdf_bytes, file_name="Medical_Report.pdf")
