import streamlit as st
import os
import google.generativeai as genai
from fpdf import FPDF
from gtts import gTTS
from PIL import Image
import io
import folium
from folium.plugins import LocateControl, MarkerCluster
from streamlit_folium import st_folium
from streamlit_lottie import st_lottie
import requests

# ---------------------------------------------------------
# 1. CONFIGURATION & THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="Shahab Smart Health",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);}
    section[data-testid="stSidebar"] {background-color: #002b36; color: white;}
    .user-msg {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px; border-radius: 15px; margin: 5px 0; text-align: right;}
    .agent-msg {background: white; color: black; padding: 12px; border-radius: 15px; margin: 5px 0; border-left: 5px solid #00c6ff;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. API SETUP (MODEL FIX)
# ---------------------------------------------------------
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # --- FIX IS HERE: Using 'gemini-pro' instead of 'flash' ---
        # 'gemini-pro' is the most stable model for free tier keys
        model = genai.GenerativeModel('gemini-pro') 
        vision_model = genai.GenerativeModel('gemini-pro-vision') # Separate model for images in Pro version
        
    else:
        st.error("⚠️ API Key Missing. Please check Streamlit Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Setup Error: {e}")

if "history" not in st.session_state: st.session_state.history = []
if "vision_analysis" not in st.session_state: st.session_state.vision_analysis = "No image uploaded."

# ---------------------------------------------------------
# 3. HELPER FUNCTIONS
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 4. NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.title("🏥 Shahab AI")
    page = st.radio("Navigate:", ["Home", "Smart Doctor", "Map", "Report"])

# --- PAGE: HOME ---
if page == "Home":
    col1, col2 = st.columns(2)
    with col1:
        st.title("Shahab Smart Health")
        st.success("System Online ✅")
        st.write("Welcome to your AI Medical Assistant. We use Google Gemini Pro for high accuracy.")
    with col2:
        lottie = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_cal1600b.json")
        if lottie: st_lottie(lottie, height=250)

# --- PAGE: SMART DOCTOR ---
elif page == "Smart Doctor":
    st.title("🤖 Dr. AI Consultant")
    
    # Image Upload Section
    with st.expander("📸 Upload Medical Image"):
        img_file = st.file_uploader("Upload X-Ray/Report", type=['png','jpg','jpeg'])
        if img_file and st.button("Analyze Image"):
            with st.spinner("Analyzing..."):
                try:
                    image = Image.open(img_file)
                    st.image(image, width=200)
                    # Using Vision Model specifically for images
                    response = vision_model.generate_content(["Describe this medical image briefly.", image])
                    st.session_state.vision_analysis = response.text
                    st.success("Image Analyzed!")
                    st.session_state.history.append(("AI", f"**[Image Findings]:** {response.text}"))
                except Exception as e:
                    st.error(f"Image Error: {e}")

    # Chat Section
    for role, text in st.session_state.history:
        style = "user-msg" if role == "User" else "agent-msg"
        st.markdown(f'<div class="{style}">{text}</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Type your symptoms...")
    
    if user_input:
        st.session_state.history.append(("User", user_input))
        st.markdown(f'<div class="user-msg">{user_input}</div>', unsafe_allow_html=True)
        
        with st.spinner("Thinking..."):
            try:
                # Text-only model for chat
                context = f"Previous Image Context: {st.session_state.vision_analysis}. User Question: {user_input}"
                response = model.generate_content(context)
                reply = response.text
                
                st.session_state.history.append(("AI", reply))
                st.markdown(f'<div class="agent-msg">{reply}</div>', unsafe_allow_html=True)
                
                audio = text_to_speech(reply)
                if audio: st.audio(audio, format='audio/mp3')
            except Exception as e:
                st.error(f"AI Error: {e}")

# --- PAGE: MAP ---
elif page == "Map":
    st.title("🗺️ Live Hospital Map")
    city = st.selectbox("City", ["Islamabad", "Lahore", "Karachi"])
    
    # Coordinates
    coords = {"Islamabad": [33.68, 73.04], "Lahore": [31.52, 74.35], "Karachi": [24.86, 67.00]}
    
    # Map Setup
    m = folium.Map(location=coords[city], zoom_start=12)
    LocateControl().add_to(m)
    
    # Dummy Markers
    folium.Marker(coords[city], popup="Central Hospital", icon=folium.Icon(color="red")).add_to(m)
    
    st_folium(m, width=1200, height=500)

# --- PAGE: REPORT ---
elif page == "Report":
    st.title("📄 Medical Report")
    if st.button("Download PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="MEDICAL REPORT", ln=True, align='C')
        
        for role, text in st.session_state.history:
            clean = text.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, f"{role}: {clean}")
            
        st.download_button("Download", pdf.output(dest='S').encode('latin-1'), "report.pdf")
