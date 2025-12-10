import streamlit as st
import os
import google.generativeai as genai  # <--- YEH LINE HONI CHAHIYE
from fpdf import FPDF
from gtts import gTTS
from PIL import Image
import io
import folium
from folium.plugins import LocateControl, MarkerCluster
from streamlit_folium import st_folium
from streamlit_lottie import st_lottie
import requests

# 1. CONFIGURATION
st.set_page_config(page_title="Shahab Smart Health", page_icon="🏥", layout="wide")

# CSS Styles
st.markdown("""
<style>
    .stApp {background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);}
    section[data-testid="stSidebar"] {background-color: #002b36; color: white;}
    .user-msg {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px; border-radius: 15px; margin: 5px 0; text-align: right;}
    .agent-msg {background: white; color: black; padding: 10px; border-radius: 15px; margin: 5px 0; border-left: 5px solid #00c6ff;}
</style>
""", unsafe_allow_html=True)

# 2. API SETUP
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("⚠️ API Key Missing. Add GEMINI_API_KEY to Streamlit Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Error: {e}")

# Session State
if "history" not in st.session_state: st.session_state.history = []
if "vision_analysis" not in st.session_state: st.session_state.vision_analysis = "No image."

# 3. HELPER FUNCTIONS
def load_lottieurl(url):
    try: return requests.get(url).json()
    except: return None

def text_to_speech(text):
    try:
        tts = gTTS(text=text[:200], lang='en', tld='co.uk')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except: return None

# 4. NAVIGATION
with st.sidebar:
    st.title("🏥 Shahab AI")
    page = st.radio("Go to:", ["Home", "Smart Doctor", "Map", "Report"])

# --- HOME ---
if page == "Home":
    col1, col2 = st.columns(2)
    with col1:
        st.title("Shahab Smart Health")
        st.write("Your Personal AI Doctor & Hospital Finder.")
        st.success("System Operational ✅")
    with col2:
        lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_cal1600b.json")
        if lottie: st_lottie(lottie, height=200)

# --- DOCTOR ---
elif page == "Smart Doctor":
    st.title("🤖 AI Consultation")
    
    # Image Upload
    img_file = st.file_uploader("Upload Medical Image", type=['png','jpg','jpeg'])
    if img_file and st.button("Analyze"):
        with st.spinner("Analyzing..."):
            img = Image.open(img_file)
            st.image(img, width=150)
            res = model.generate_content(["Analyze this medical image.", img])
            st.session_state.vision_analysis = res.text
            st.success("Analyzed!")

    # Chat
    for role, text in st.session_state.history:
        style = "user-msg" if role == "User" else "agent-msg"
        st.markdown(f'<div class="{style}">{text}</div>', unsafe_allow_html=True)

    user_in = st.chat_input("Type your symptoms...")
    if user_in:
        st.session_state.history.append(("User", user_in))
        st.rerun()

    # AI Logic (Runs after rerun)
    if st.session_state.history and st.session_state.history[-1][0] == "User":
        with st.spinner("Thinking..."):
            last_msg = st.session_state.history[-1][1]
            prompt = f"Context: {st.session_state.vision_analysis}. User: {last_msg}"
            response = model.generate_content(prompt)
            st.session_state.history.append(("AI", response.text))
            
            audio = text_to_speech(response.text)
            if audio: st.audio(audio, format='audio/mp3')
            st.rerun()

# --- MAP ---
elif page == "Map":
    st.title("🗺️ Live Map")
    city = st.selectbox("City", ["Islamabad", "Lahore", "Karachi"])
    coords = {"Islamabad": [33.68, 73.04], "Lahore": [31.52, 74.35], "Karachi": [24.86, 67.00]}
    
    m = folium.Map(location=coords[city], zoom_start=12)
    LocateControl().add_to(m)
    st_folium(m, width=800, height=400)

# --- REPORT ---
elif page == "Report":
    st.title("📄 Report")
    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="MEDICAL REPORT", ln=True, align='C')
        for r, t in st.session_state.history:
            clean = t.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, f"{r}: {clean}")
        
        st.download_button("Download", pdf.output(dest='S').encode('latin-1'), "report.pdf")
