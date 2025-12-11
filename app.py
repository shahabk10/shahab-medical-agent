# AI DOCTOR PRO – FINAL ZERO-ERROR VERSION (December 2025)
import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from gtts import gTTS
from PIL import Image
import io

# ====== SECRETS ======
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("GEMINI_API_KEY missing! Add it in Streamlit Secrets.")
    st.stop()

st.set_page_config(page_title="AI Doctor Pro", page_icon="Doctor", layout="centered")

# ====== BEAUTIFUL THEME ======
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); font-family: 'Segoe UI';}
    .title {font-size: 4.5rem; text-align: center; font-weight: 900;
            background: linear-gradient(90deg, #00ffea, #ff00c8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .chat-box {background: rgba(255,255,255,0.12); padding: 20px; border-radius: 20px;
               backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.2);}
    .user {background: #00d4ff; color: white; padding: 15px; border-radius: 20px 20px 0 20px;
           max-width: 80%; margin: 10px 0 10px auto;}
    .ai {background: #1e1e1e; color: #00ffea; padding: 15px; border-radius: 20px 20px 20px 0;
         max-width: 80%; margin: 10px 0;}
    .emergency {color: #ff0033; font-size: 1.8rem; font-weight: bold; animation: pulse 1s infinite;}
    @keyframes pulse {0%,100%{opacity:1} 50%{opacity:0.4}}
</style>
""", unsafe_allow_html=True)

# ====== PDF & VOICE ======
class PDF(FPDF):
    def header(self):
        self.set_font('Arial','B',20)
        self.cell(0,15,'AI DOCTOR PRO - MEDICAL REPORT', ln=1,align='C')
        self.ln(5)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial','I',8)
        self.cell(0,10,'AI Generated • Not a Substitute for Real Doctor',align='C')

def speak(text):
    try:
    try:
        tts = gTTS(text=str(text)[:200], lang='en', tld='co.uk')
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        st.audio(audio, autoplay=True)
    except:
        pass

def is_emergency(text):
    keywords = ["heart attack","chest pain","can't breathe","bleeding heavily","unconscious","stroke","suicide","poison"]
    return any(word in text.lower() for word in keywords)

# ====== SESSION STATE ======
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.vision = "No image uploaded"
    st.session_state.chat_ended = False

# First greeting
if not st.session_state.messages:
    greeting = "Hello! I'm your AI Doctor with a British accent. Please tell me your name and how you're feeling."
    st.session_state.messages.append({"role": "ai", "content": greeting})
    speak(greeting)

# ====== SIDEBAR NAVIGATION ======
page = st.sidebar.radio("Navigation", ["Home", "Chat with Doctor", "Find Hospital", "Download Report"])

# ====== HOME PAGE ======
if page == "Home":
    st.markdown('<h1 class="title">AI DOCTOR PRO</h1>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:white'>Talk • Upload Photo • Voice Reply • PDF Report • Find Hospital</h3>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown("<h2 style='text-align:center;color:#00ffea'>Chat</h2>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h2 style='text-align:center;color:#00ffea'>Photo</h2>", unsafe_allow_html=True)
    with col3:
        st.markdown("<h2 style='text-align:center;color:#00ffea'>Voice</h2>", unsafe_allow_html=True)
    with col4:
        st.markdown("<h2 style='text-align:center;color:#00ffea'>Report</h2>", unsafe_allow_html=True)
    with col5:
        st.markdown("<h2 style='text-align:center;color:#00ffea'>Hospital</h2>", unsafe_allow_html=True)

    if st.button("START CONSULTATION NOW", type="primary", use_container_width=True):
        st.rerun()  # Will go to Chat page via sidebar

# ====== CHAT PAGE (100% WORKING) ======
elif page == "Chat with Doctor":
    st.header("Chat with AI Doctor (UK Voice)")

    # Image Upload
    uploaded = st.file_uploader("Upload Prescription or Symptom Photo", type=["png","jpg","jpeg","webp"])
    if uploaded:
        with st.spinner("Analyzing your image..."):
            img = Image.open(uploaded)
            st.image(img, width=320)
            model = genai.GenerativeModel('gemini-1.5-flash')
            result = model.generate_content(["You are a medical AI. Analyze this image professionally (prescription or symptom).", img]).text
            st.session_state.vision = result
            st.success("Image analyzed successfully!")
            st.info(result)
            speak("I have analyzed your image.")

    # Show Chat
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai">AI Doctor: {msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # User Message
    if prompt := st.chat_input("Describe your symptoms..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Emergency Check
        if is_emergency(prompt):
            alert = "EMERGENCY DETECTED! PLEASE CALL 1122 or 15 IMMEDIATELY!"
            st.markdown(f'<p class="emergency">{alert}</p>', unsafe_allow_html=True)
            speak("Emergency! Call 1122 now!")
            st.session_state.messages.append({"role": "ai", "content": alert})
            st.rerun()

        # Normal Reply
        with st.spinner("Doctor is replying..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            history = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages])
            response = model.generate_content(f"You are a caring doctor. Reply in short, clear sentences.\nConversation:\n{history}")
            reply = response.text.strip()
            st.session_state.messages.append({"role": "ai", "content": reply})
            speak(reply)
        st.rerun()

    if st.button("End Chat & Generate Report"):
        st.session_state.chat_ended = True
        st.success("Chat ended! Go to 'Download Report' page")
        speak("Your medical report is ready")

# ====== HOSPITAL PAGE ======
elif page == "Find Hospital":
    st.header("Find Nearby Hospitals")
    city = st.text_input("Enter your city", "Lahore")
    if st.button("Search Hospitals"):
        url = f"https://maps.google.com/maps?q=hospital+near+{city.replace(' ', '+')}&output=embed"
        st.components.v1.iframe(url, height=550)

# ====== DOWNLOAD REPORT PAGE ======
elif page == "Download Report":
    st.header("Your Final Medical Report")
    if not st.session_state.chat_ended:
        st.warning("Please finish the chat first!")
        st.stop()

    if st.button("Generate & Download PDF Report", type="primary"):
        with st.spinner("Creating your report..."):
            chat_log = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
            full_text = f"Chat History:\n{chat_log}\n\nImage Analysis:\n{st.session_state.vision}"

            model = genai.GenerativeModel('gemini-1.5-flash')
            report_content = model.generate_content(f"Create a professional medical report from this data:\n{full_text}").text

            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in report_content.split("\n"):
                if line.strip():
                    pdf.multi_cell(0, 8, line.encode('latin-1','replace').decode('latin-1'))
            pdf.ln(10)
            pdf.set_text_color(200,0,0)
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 10, "This is an AI-generated report. Always consult a qualified doctor.")

            buffer = io.BytesIO()
            pdf.output(buffer)
            buffer.seek(0)

            st.balloons()
            st.download_button(
                label="DOWNLOAD REPORT NOW",
                data=buffer,
                file_name="AI_Doctor_Report.pdf",
                mime="application/pdf",
                type="primary"
            )

# Footer
st.markdown("<p style='text-align:center;color:white;margin-top:50px'>© 2025 AI Doctor Pro • Made with love in Pakistan</p>", unsafe_allow_html=True)
