# ═══════════════════════════════════════════════════════════════
# AI HEALTH PLATFORM – INTERNATIONAL EDITION (2025)
# Features: Chat + Voice + Image Analysis + PDF Report + Nearby Hospitals Map
# Works with or WITHOUT Google Maps API Key (Graceful fallback)
# ═══════════════════════════════════════════════════════════════

import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from gtts import gTTS
from PIL import Image
import io
import time
import base64

# ───── API KEYS (from Streamlit Secrets) ───────────────────────
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    st.success("Gemini API Connected")
except:
    st.error("GEMINI_API_KEY not found! Add it in Secrets → https://share.streamlit.io/settings/secrets")
    st.stop()

# Optional Google Maps Key (won't crash if missing)
GOOGLE_MAPS_KEY = st.secrets.get("GOOGLE_MAPS_API_KEY", None)
if GOOGLE_MAPS_KEY:
    st.success("Google Maps API Ready")

# ───── Beautiful UI & Animations ─────────────────────────────────
st.set_page_config(page_title="AI Health Assistant", page_icon="Doctor", layout="centered")

st.markdown("""
<style>
    .big-title {font-size: 3.5rem !important; font-weight: bold; color: #0D47A1; text-align: center;}
    .stApp {background: linear-gradient(135deg, #e0f7fa, #fff3e0); animation: fadein 2s;}
    @keyframes fadein {from {opacity:0;} to {opacity:1;}}
    .emergency {color:red; font-size:1.4rem; font-weight:bold; animation: blink 1s infinite;}
    @keyframes blink {50% {opacity:0.4;}}
    .chat-bubble {padding: 12px; border-radius: 15px; margin: 10px 0;}
    .user-bubble {background:#2196F3; color:white; text-align:right;}
    .agent-bubble {background:#E3F2FD; color:#000;}
</style>
""", unsafe_allow_html=True)

# ───── PDF Report Class (Same Professional Look) ─────────────────
class UltimateHealthReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 18)
        self.cell(0, 15, 'MYU AI MEDICAL HOSPITAL', ln=1, align='C')
        self.set_font('Arial', 'I', 11)
        self.cell(0, 8, 'International AI Health Platform', ln=1, align='C')
        self.set_draw_color(0, 102, 204)
        self.line(10, 35, 200, 35)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'AI-Generated Report | Not a Substitute for Professional Medical Care', align='C')

    def chapter(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(0, 102, 204)
        self.set_text_color(255)
        self.cell(0, 10, title.upper(), ln=1, fill=True)
        self.ln(5)

    def body(self, txt):
        self.set_font('Arial', '', 11)
        self.set_text_color(0)
        self.multi_cell(0, 7, txt.encode('latin-1', 'replace').decode('latin-1'))
        self.ln(3)

# ───── Helper Functions ────────────────────────────────────────
def speak(text):
    try:
        tts = gTTS(text=text[:200], lang='en', tld='co.uk', slow=False)
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        st.audio(audio, format="audio/mp3", autoplay=True)
    except:
        pass

def check_emergency(text):
    keywords = ["heart attack","chest pain","can't breathe","bleeding heavily","unconscious","stroke","suicide","poison"]
    return any(k in text.lower() for k in keywords)

def analyze_image(img_bytes):
    model = genai.GenerativeModel('gemini-1.5-flash')
    img = Image.open(io.BytesIO(img_bytes))
    response = model.generate_content([
        "Analyze this medical image. If it's a prescription → list medicines. If it's a symptom → describe it clearly.",
        img
    ], stream=False)
    return response.text

def generate_report(chat, vision):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Create a professional medical report in plain text with these sections:
    SECTION 1: PATIENT DETAILS
    SECTION 2: SYMPTOM SUMMARY
    SECTION 3: POSSIBLE CAUSES (General info only)
    SECTION 4: LIFESTYLE RECOMMENDATIONS
    SECTION 5: DAILY ROUTINE

    Chat history: {chat}
    Image analysis: {vision}
    """
    resp = model.generate_content(prompt)
    return resp.text

# ───── Nearby Hospitals (Works even without API key) ─────────────
def show_hospitals():
    st.subheader("Nearby Hospitals & Clinics")
    location = st.text_input("Enter city or area (e.g., Lahore, Karachi, London, New York)", "Lahore")

    if st.button("Search Hospitals Near Me"):
        with st.spinner("Searching..."):
            if GOOGLE_MAPS_KEY:
                # Full interactive map with real data
                url = f"https://www.google.com/maps/embed/v1/search?key={GOOGLE_MAPS_KEY}&q=hospital+near+{location.replace(' ', '+')}"
                st.components.v1.iframe(url, height=500)
            else:
                # Fallback: Static Google Maps link + list of emergency numbers
                st.info("Google Maps API not connected → Showing fallback map + emergency contacts")
                map_url = f"https://maps.google.com/maps?q=hospital+near+{location.replace(' ', '+')}&z=13&output=embed"
                st.components.v1.iframe(map_url, height=500)

            # Always show emergency numbers (very useful!)
            st.markdown("### Emergency Contacts")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Pakistan** → 1122 / 15  \n**UK** → 999  \n**USA/Canada** → 911")
            with col2:
                st.markdown("**India** → 108  \n**Australia** → 000  \n**UAE** → 998/999")

# ───── Main App (Multi-page Style) ─────────────────────────────
page = st.sidebar.radio("Navigation", ["Home", "Chat with Doctor AI", "Find Hospitals", "Download Report"])

if page == "Home":
    st.markdown("<h1 class='big-title'>AI Doctor Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;font-size:1.3rem;'>Talk • Upload Image • Get Report • Find Hospital</p>", unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=0_4qMhV9Yb0")  # Replace with your intro video
    st.balloons()

elif page == "Chat with Doctor AI":
    st.header("Chat with Your AI Doctor (UK Accent)")

    if "messages" not in st.session_state:
        st.session_state.messages = []
        intro = "Hello! I'm your AI medical assistant. Please tell me your name and age."
        st.session_state.messages.append({"role": "agent", "content": intro})
        speak(intro)

    # Display chat
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div class='chat-bubble user-bubble'>You: {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble agent-bubble'>Doctor AI: {msg['content']}</div>", unsafe_allow_html=True)

    # User input
    if prompt := st.chat_input("Type your symptoms or message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

        # Emergency check
        if check_emergency(prompt):
            emergency = "EMERGENCY! This sounds serious. CALL 999 or 1122 IMMEDIATELY!"
            st.markdown(f"<p class='emergency'>{emergency}</p>", unsafe_allow_html=True)
            speak("Emergency! Call 1122 now!")
            st.session_state.messages.append({"role": "agent", "content": emergency})
            st.stop()

        # Image upload trigger
        if any(x in prompt.lower() for x in ["image", "photo", "prescription", "upload"]):
            uploaded = st.file_uploader("Upload prescription or symptom photo", type=["png","jpg","jpeg"])
            if uploaded:
                with st.spinner("Analyzing image..."):
                    result = analyze_image(uploaded.getvalue())
                    st.success("Image analyzed!")
                    st.session_state.vision = result
                    st.session_state.messages.append({"role": "agent", "content": f"Image result: {result}"})
                    speak("Image analyzed.")
                st.rerun()

        # Normal Gemini response
        model = genai.GenerativeModel('gemini-1.5-flash')
        history = [m["content"] for m in st.session_state.messages]
        response = model.generate_content(history, stream=True)
        full_reply = ""
        placeholder = st.empty()
        for chunk in response:
            full_reply += chunk.text
            placeholder.markdown(f"<div class='chat-bubble agent-bubble'>Doctor AI: {full_reply}</div>", unsafe_allow_html=True)
        st.session_state.messages.append({"role": "agent", "content": full_reply})
        speak(full_reply)

    if st.button("End Chat & Generate Report"):
        st.success("Chat ended! Go to 'Download Report' page.")
        st.session_state.chat_ended = True

elif page == "Find Hospitals":
    show_hospitals()

elif page == "Download Report":
    st.header("Your Final Medical Report")
    if not st.session_state.get("chat_ended", False):
        st.warning("Please complete the chat first!")
        st.stop()

    vision_text = st.session_state.get("vision", "No image uploaded")
    chat_text = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])

    if st.button("Generate & Download PDF"):
        with st.spinner("Creating professional report..."):
            report_text = generate_report(chat_text, vision_text)

            pdf = UltimateHealthReport()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for line in report_text.split("\n"):
                if line.strip() == "":
                    continue
                if any(x in line.upper() for x in ["SECTION", "PATIENT", "SUMMARY", "RECOMMENDATION", "ROUTINE"]):
                    pdf.chapter(line.strip())
                else:
                    pdf.body(line.strip())

            pdf.ln(10)
            pdf.set_font("Arial", "B", 12)
            pdf.set_text_color(200, 0, 0)
            pdf.multi_cell(0, 8, "DISCLAIMER: This is AI-generated advice. Always consult a qualified doctor.")

            # Save & offer download
            output = io.BytesIO()
            pdf.output(output)
            output.seek(0)
            b64 = base64.b64encode(output.read()).decode()

            st.success("Report Ready!")
            st.download_button(
                label="Download Final_Medical_Report.pdf",
                data=output,
                file_name="AI_Medical_Report.pdf",
                mime="application/pdf"
            )
            st.balloons()

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center'>© 2025 AI Health Platform – Made with ❤️ for everyone</p>", unsafe_allow_html=True)
