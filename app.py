# AI DOCTOR PRO – INTERNATIONAL 2025 EDITION
import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from gtts import gTTS
from PIL import Image
import io
import base64
import time

# ───── CONFIG & SECRETS ─────
st.set_page_config(page_title="AI Doctor Pro", page_icon="Doctor", layout="centered")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Add GEMINI_API_KEY in Secrets!")
    st.stop()

# ───── ULTRA BEAUTIFUL THEME (Medical Neon Style) ─────
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Segoe UI', sans-serif;
    }
    .big-title {
        font-size: 4.5rem !important;
        font-weight: 900;
        background: -webkit-linear-gradient(#fff, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        text-shadow: 0 0 20px rgba(0,212,255,0.5);
    }
    .feature-card {
        background: rgba(255,255,255,0.15);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        transition: all 0.3s;
        margin: 10px;
    }
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
    }
    .chat-container {
        background: rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 20px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.3);
    }
    .emergency {color: #ff0033; font-size:1.5rem; font-weight:bold; animation: pulse 1s infinite;}
    @keyframes pulse {0%,100%{opacity:1} 50%{opacity:0.5}}
</style>
""", unsafe_allow_html=True)

# ───── PDF CLASS (Professional) ─────
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 20)
        self.cell(0, 15, 'AI DOCTOR PRO - MEDICAL REPORT', ln=1, align='C')
        self.set_font('Arial', 'I', 12)
        self.cell(0, 10, 'International AI Health Assistant', ln=1, align='C')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 9)
        self.cell(0, 10, 'AI Generated | Consult Doctor | Not for Legal Use', align='C')

# ───── HELPER FUNCTIONS ─────
def speak(text):
    try:
        tts = gTTS(text=str(text)[:200], lang='en', tld='co.uk')
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        st.audio(audio, format='audio/mp3', autoplay=True)
    except:
        pass

def check_emergency(text):
    words = ["heart attack", "chest pain", "can't breathe", "bleeding", "unconscious", "stroke", "suicide"]
    return any(word in text.lower() for word in words)

def analyze_image(img):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(["Analyze this medical image (prescription or symptom). Be clear and professional.", img])
    return response.text

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.vision = "No image uploaded"
    st.session_state.chat_ended = False

# ───── SIDEBAR NAVIGATION ─────
page = st.sidebar.radio("Menu", ["Home Dashboard", "Chat with AI Doctor", "Nearby Hospitals", "Download Report"])

# ───── HOME DASHBOARD (Zabardast Design) ─────
if page == "Home Dashboard":
    st.markdown('<h1 class="big-title">AI DOCTOR PRO</h1>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center; color:#fff;'>Your 24/7 AI Medical Assistant</h3>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="feature-card"><h2>Chat</h2><p>Talk to AI Doctor</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="feature-card"><h2>Image</h2><p>Upload Prescription/Symptom</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="feature-card"><h2>Report</h2><p>Get PDF Report</p></div>', unsafe_allow_html=True)

    col4, col5 = st.columns(2)
    with col4:
        st.markdown('<div class="feature-card"><h2>Hospital</h2><p>Find Nearby Hospitals</p></div>', unsafe_allow_html=True)
    with col5:
        st.markdown('<div class="feature-card"><h2>Emergency</h2><p>Instant Alert System</p></div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Start Consultation Now", type="primary", use_container_width=True):
        st.switch_page("Chat with AI Doctor")

# ───── CHAT PAGE (Fully Working) ─────
elif page == "Chat with AI Doctor":
    st.header("Chat with AI Doctor (UK Voice)")

    # Always show image upload
    uploaded_file = st.file_uploader("Upload Prescription or Symptom Photo", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        with st.spinner("Analyzing your image..."):
            img = Image.open(uploaded_file)
            st.image(img, width=300)
            result = analyze_image(img)
            st.success("Image Analyzed!")
            st.session_state.vision = result
            st.info(result)
            speak("Image analyzed successfully")

    # Chat messages
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"<div style='text-align:right; background:#00d4ff; color:white; padding:15px; border-radius:20px; margin:10px; max-width:80%'; display:inline-block'>{msg['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:#1e1e1e; color:#00ff9d; padding:15px; border-radius:20px; margin:10px; max-width:80%'; display:inline-block>{msg['content']}</div>", unsafe_allow_html=True)

    # User input
    if prompt := st.chat_input("Describe your symptoms..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

        if check_emergency(prompt):
            alert = "EMERGENCY DETECTED! CALL 1122 or 15 IMMEDIATELY!"
            st.markdown(f"<p class='emergency'>{alert}</p>", unsafe_allow_html=True)
            speak("Emergency! Call 1122 now!")
            st.session_state.messages.append({"role": "agent", "content": alert})
            st.stop()

        with st.spinner("Doctor is thinking..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            response = model.generate_content(f"Act as a kind medical doctor. Patient said: {prompt}\nPrevious chat: {history}")
            reply = response.text.replace("*", "").replace("#", "")
            st.session_state.messages.append({"role": "agent", "content": reply})
            speak(reply)
        st.rerun()

    if st.button("End Chat & Generate Report"):
        st.session_state.chat_ended = True
        st.success("Chat ended! Go to Download Report")
        speak("Chat ended. Generating your report.")

# ───── HOSPITAL PAGE (Fallback + Real Map) ─────
elif page == "Nearby Hospitals":
    st.header("Find Hospitals Near You")
    location = st.text_input("Enter city/area", "Lahore")
    if st.button("Search"):
        map_url = f"https://maps.google.com/maps?q=hospital+near+{location}&output=embed"
        st.components.v1.iframe(map_url, height=500)

# ───── DOWNLOAD REPORT (100% Working) ─────
elif page == "Download Report":
    st.header("Your Medical Report")
    if not st.session_state.chat_ended:
        st.warning("Please complete the chat first!")
    else:
        if st.button("Generate PDF Report"):
            with st.spinner("Creating your professional report..."):
                chat_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
                full_text = f"Patient Chat:\n{chat_text}\n\nImage Analysis:\n{st.session_state.vision}"

                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"Create a beautiful medical report from this:\n{full_text}"
                report = model.generate_content(prompt).text

                pdf = PDFReport()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in report.split("\n"):
                    if line.strip():
                        pdf.multi_cell(0, 8, line.encode('latin-1', 'replace').decode('latin-1'))
                pdf.ln(10)
                pdf.set_text_color(255, 0, 0)
                pdf.multi_cell(0, 10, "This is AI-generated. Always consult a real doctor.")

                output = io.BytesIO()
                pdf.output(output)
                output.seek(0)

                st.balloons()
                st.download_button(
                    label="DOWNLOAD YOUR REPORT",
                    data=output,
                    file_name="AI_Doctor_Report.pdf",
                    mime="application/pdf",
                    type="primary"
                )

# Footer
st.markdown("<br><hr><p style='text-align:center; color:white;'>© 2025 AI Doctor Pro - Made with ❤️ in Pakistan</p>", unsafe_allow_html=True)
