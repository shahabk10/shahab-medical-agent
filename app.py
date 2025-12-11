# app.py - Ultimate AI Medical Assistant (International Version)
import streamlit as st
import google.generativeai as genai
from gtts import gTTS
from fpdf import FPDF
from PIL import Image
import io
import os
import time
import base64
from streamlit_option_menu import option_menu
import folium
from streamlit_folium import st_folium
import requests

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="MediAI Pro - Your 24/7 AI Doctor",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CUSTOM CSS FOR BEAUTIFUL UI =====================
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .stApp {background: transparent;}
    .big-font {font-size: 50px !important; font-weight: bold; color: white; text-align: center;}
    .medium-font {font-size: 24px !important; color: #ffffff;}
    .chat-bubble-user {background-color: #4facfe; color: white; border-radius: 20px; padding: 15px; margin: 10px 0; max-width: 80%; align-self: flex-end;}
    .chat-bubble-agent {background-color: #ffffff; color: black; border-radius: 20px; padding: 15px; margin: 10px 0; max-width: 80%; box-shadow: 0 2px 5px rgba(0,0,0,0.1);}
    .hospital-card {background: white; padding: 15px; border-radius: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); margin: 10px;}
</style>
""", unsafe_allow_html=True)

# ===================== SIDEBAR =====================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/doctor-female.png", width=100)
    st.title("MediAI Pro")
    st.markdown("### Your Personal AI Health Assistant")
    
    selected = option_menu(
        menu_title=None,
        options=["Home", "AI Doctor Chat", "Upload Image", "Nearby Hospitals", "Download Report"],
        icons=["house", "chat-dots", "camera", "hospital", "file-medical"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#667eea", "font-size": "20px"},
            "nav-link": {"font-size": "18px", "text-align": "left", "margin":"0px"},
            "nav-link-selected": {"background-color": "#667eea"},
        }
    )

# ===================== API SETUP =====================
@st.cache_resource
def get_gemini_client():
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

model = get_gemini_client()

# ===================== SESSION STATE =====================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "vision_data" not in st.session_state:
    st.session_state.vision_data = "No image analyzed yet."
if "patient_info" not in st.session_state:
    st.session_state.patient_info = {}
if "report_generated" not in st.session_state:
    st.session_state.report_generated = False

# ===================== FUNCTIONS =====================
def speak(text):
    try:
        tts = gTTS(text=text[:200], lang='en', tld='co.uk')
        audio_file = "agent_voice.mp3"
        tts.save(audio_file)
        audio_bytes = open(audio_file, "rb").read()
        audio_base64 = base64.b64encode(audio_bytes).decode()
        audio_html = f"""
        <audio autoplay>
          <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except:
        pass

def check_emergency(text):
    keywords = ["heart attack","chest pain","can't breathe","unconscious","stroke","suicide","bleeding heavily","poison"]
    return any(k in text.lower() for k in keywords)

def analyze_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    prompt = "Analyze this medical image. If it's a prescription, list medicines. If it's a symptom (rash, swelling, injury), describe clearly. Keep it short and professional."
    response = model.generate_content([prompt, img])
    return response.text

def generate_report():
    chat_log = "\n".join([f"User: {msg[0]}\nAgent: {msg[1]}" for msg in st.session_state.chat_history])
    prompt = f"""
    Create a professional medical report in UK NHS style:
    
    Patient: {st.session_state.patient_info.get('name','Unknown')}, Age: {st.session_state.patient_info.get('age','Unknown')}, Gender: {st.session_state.patient_info.get('gender','Unknown')}
    
    Chat History: {chat_log}
    Image Analysis: {st.session_state.vision_data}
    
    Structure (Plain Text):
    SECTION 1: PATIENT DETAILS
    SECTION 2: SYMPTOM SUMMARY
    SECTION 3: POSSIBLE CAUSES (Non-diagnostic)
    SECTION 4: LIFESTYLE RECOMMENDATIONS
    SECTION 5: DAILY ROUTINE CHECKLIST
    """
    response = model.generate_content(prompt)
    return response.text

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'MediAI Pro - AI Health Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, 'International AI Healthcare Assistant', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'CONFIDENTIAL | AI Report | Not a substitute for medical advice', 0, 0, 'C')

def create_pdf(report_text):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    for line in report_text.split('\n'):
        if line.strip():
            if "SECTION" in line.upper():
                pdf.set_font("Arial", 'B', 13)
                pdf.set_fill_color(230, 240, 255)
                pdf.cell(0, 10, line.strip(), 0, 1, 'L', 1)
                pdf.ln(3)
            else:
                pdf.set_font("Arial", size=11)
                pdf.multi_cell(0, 7, line.strip())
    return pdf.output(dest="S").encode("latin-1")

# ===================== PAGES =====================

if selected == "Home":
    st.markdown('<p class="big-font">MediAI Pro</p>', unsafe_allow_html=True)
    st.markdown('<p class="medium-font">Your 24/7 AI Health Companion</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("https://img.icons8.com/fluency/96/000000/stethoscope.png")
        st.write("AI Doctor Chat")
    with col2:
        st.image("https://img.icons8.com/fluency/96/000000/hospital.png")
        st.write("Nearby Hospitals")
    with col3:
        st.image("https://img.icons8.com/fluency/96/000000/report.png")
        st.write("PDF Report")
    
    st.markdown("### Features")
    st.write("• Voice Response (UK Accent)")
    st.write("• Image Analysis (Prescriptions & Symptoms)")
    st.write("• Live Hospital Finder with Contact")
    st.write("• Emergency Detection & Alert")
    st.write("• Professional PDF Report")

elif selected == "AI Doctor Chat":
    st.header("Talk to Your AI Doctor")
    
    # Patient Info
    if not st.session_state.patient_info:
        name = st.text_input("Your Name")
        age = st.text_input("Your Age")
        gender = st.selectbox("Gender", ["Male", "Female", "Other", "Prefer not to say"])
        if st.button("Start Consultation"):
            st.session_state.patient_info = {"name": name, "age": age, "gender": gender}
            st.success("Welcome! How can I help you today?")
            speak("Hello, how can I assist you today?")
    
    else:
        st.success(f"Patient: {st.session_state.patient_info['name']}, {st.session_state.patient_info['age']} years old")
        
        # Chat Display
        for msg in st.session_state.chat_history:
            if msg[2] == "user":
                st.markdown(f'<div class="chat-bubble-user">{msg[0]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble-agent">Doctor: {msg[1]}</div>', unsafe_allow_html=True)
        
        user_input = st.chat_input("Describe your symptoms...")
        
        if user_input:
            if check_emergency(user_input):
                st.error("EMERGENCY DETECTED! CALL 1122 or 999 IMMEDIATELY!")
                speak("This is an emergency. Please call emergency services now.")
                st.stop()
            
            with st.spinner("Doctor is thinking..."):
                response = model.generate_content(user_input)
                reply = response.text
            
            st.session_state.chat_history.append((user_input, reply, "user"))
            st.session_state.chat_message("assistant").write(reply)
            speak(reply)
            st.rerun()

elif selected == "Upload Image":
    st.header("Upload Prescription or Symptom Photo")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        :
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=400)
        
        if st.button("Analyze Image"):
            with st.spinner("Analyzing..."):
                result = analyze_image(uploaded_file.getvalue())
                st.session_state.vision_data = result
                st.success("Analysis Complete!")
                st.write(result)
                speak("I have analyzed the image.")

elif selected == "Nearby Hospitals":
    st.header("Nearby Hospitals (Live Google Maps)")
    
    location = st.text_input("Enter your city or area (e.g., Lahore, Karachi, London)", "Lahore")
    
    if st.button("Find Hospitals"):
        # Using Google Places API via a free proxy (you can replace with your own key later)
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=hospitals+in+{location}&key=YOUR_GOOGLE_MAPS_KEY"
        
        # Free alternative using Overpass API (OpenStreetMap)
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        (
          node["amenity"="hospital"](around:10000, "{location}");
          way["amenity"="hospital"](around:10000, "{location}");
        );
        out center;
        """
        try:
            response = requests.get(overpass_url, params={'data': overpass_query})
            data = response.json()
            
            m = folium.Map(location=[31.5204, 74.3587], zoom_start=12)
            
            for element in data['elements'][:10]:
                if 'lat' in element:
                    lat, lon = element['lat'], element['lon']
                elif 'center' in element:
                    lat, lon = element['center']['lat'], element['center']['lon']
                else:
                    continue
                
                name = element.get('tags', {}).get('name', 'Hospital')
                phone = element.get('tags', {}).get('phone', 'Not available')
                folium.Marker(
                    [lat, lon],
                    popup=f"<b>{name}</b><br>Phone: {phone}",
                    icon=folium.Icon(color="red", icon="plus")
                ).add_to(m)
            
            st_folium(m, width=700, height=500)
        
        except:
            st.error("Map loading failed. Try again later.")

elif selected == "Download Report":
    st.header("Generate & Download Report")
    
    if st.button("Generate Final Report"):
        with st.spinner("Creating professional report..."):
            report_text = generate_report()
            pdf_bytes = create_pdf(report_text)
            st.session_state.report_generated = True
            st.session_state.final_report = pdf_bytes
        
        st.success("Report Generated!")
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"MediAI_Report_{st.session_state.patient_info.get('name','Patient')}.pdf",
            mime="application/pdf"
        )
        st.text_area("Report Preview", report_text, height=400)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: white;'>© 2025 MediAI Pro | Made with ❤️ for Pakistan & World</p>", unsafe_allow_html=True)
