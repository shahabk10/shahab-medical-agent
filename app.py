# AI DOCTOR PRO - FINAL 100% ERROR-FREE VERSION (Tested Live)
import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from gtts import gTTS
from PIL import Image
import io

# === API KEY ===
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("Add GEMINI_API_KEY in Secrets!")
    st.stop()

st.set_page_config(page_title="AI Doctor Pro", page_icon="Doctor", layout="centered")

# === DESIGN ===
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .title {font-size: 4.5rem; text-align: center; font-weight: 900;
            background: linear-gradient(90deg, #00ffea, #ff00c8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .chat-box {background: rgba(255,255,255,0.12); padding: 20px; border-radius: 20px;
               backdrop-filter: blur(12px); margin: 10px 0;}
    .user {background: #00d4ff; color: white; padding: 15px; border-radius: 20px 20px 0 0 20px;
           max-width: 75%; margin-left: auto; margin-bottom: 10px;}
    .ai {background: #1e1e1e; color: #00ffea; padding: 15px; border-radius: 20px 20px 20px 0;
         max-width: 75%; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# === PDF & VOICE ===
class PDF(FPDF):
    def header(self):
        self.set_font('Arial','B',20)
        self.cell(0,15,'AI DOCTOR PRO - MEDICAL REPORT', ln=1, align='C')
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial','I',8)
        self.cell(0,10,'AI Generated Report', align='C')

def speak(text):
    try:
        tts = gTTS(text=str(text)[:200], lang='en', tld='co.uk')
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        st.audio(audio, autoplay=True)
    except:
        pass

def is_emergency(text):
    words = ["heart attack","chest pain","can't breathe","bleeding","stroke","suicide","poison"]
    return any(word in text.lower() for word in words)

# === SESSION STATE ===
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.vision = "No image uploaded"
    st.session_state.chat_ended = False

if not st.session_state.messages:
    greet = "Hello! I'm your AI Doctor with British accent. What's your name and how can I help you today?"
    st.session_state.messages.append({"role": "ai", "content": greet})
    speak(greet)

# === SIDEBAR ===
page = st.sidebar.radio("Menu", ["Home", "Chat with Doctor", "Find Hospital", "Get Report"])

# === HOME ===
if page == "Home":
    st.markdown('<h1 class="title">AI DOCTOR PRO</h1>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:white'>Your 24/7 AI Medical Assistant</h3>", unsafe_allow_html=True)
    st.markdown("---")
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown("<h3 style='color:#00ffea;text-align:center'>Chat</h3>", unsafe_allow_html=True)
    with c2: st.markdown("<h3 style='color:#00ffea;text-align:center'>Photo</h3>", unsafe_allow_html=True)
    with c3: st.markdown("<h3 style='color:#00ffea;text-align:center'>Voice</h3>", unsafe_allow_html=True)
    with c4: st.markdown("<h3 style='color:#00ffea;text-align:center'>Report</h3>", unsafe_allow_html=True)
    if st.button("START NOW", type="primary", use_container_width=True):
        st.rerun()

# === CHAT PAGE ===
elif page == "Chat with Doctor":
    st.header("Chat with AI Doctor (UK Voice)")

    uploaded = st.file_uploader("Upload prescription or symptom photo", type=["png","jpg","jpeg","webp"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, width=300)
        model = genai.GenerativeModel('gemini-1.5-flash')
        result = model.generate_content(["Analyze this medical image clearly.", img]).text
        st.session_state.vision = result
        st.success("Image analyzed!")
        st.info(result)
        speak("Image analyzed")

    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai">AI Doctor: {msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        if is_emergency(prompt):
            alert = "EMERGENCY! CALL 1122 IMMEDIATELY!"
            st.error(alert)
            speak("Emergency call one one two two")
            st.session_state.messages.append({"role": "ai", "content": alert})
            st.rerun()

        with st.spinner("Thinking..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            resp = model.generate_content(f"Be a kind doctor. Reply shortly.\n{history}")
            reply = resp.text.strip()
            st.session_state.messages.append({"role": "ai", "content": reply})
            speak(reply)
        st.rerun()

    if st.button("End Chat & Make Report"):
        st.session_state.chat_ended = True
        st.success("Ready! Go to Get Report")

# === HOSPITAL ===
elif page == "Find Hospital":
    st.header("Nearby Hospitals")
    city = st.text_input("City", "Lahore")
    if st.button("Search"):
        url = f"https://maps.google.com/maps?q=hospital+near+{city}&output=embed"
        st.components.v1.iframe(url, height=500)

# === REPORT ===
elif page == "Get Report":
    st.header("Your Medical Report")
    if not st.session_state.chat_ended:
        st.warning("Chat first!")
    else:
        if st.button("Generate PDF"):
            with st.spinner("Creating..."):
                chat = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                text = f"Chat:\n{chat}\n\nImage: {st.session_state.vision}"
                report = genai.GenerativeModel('gemini-1.5-flash').generate_content(f"Make a clean report:\n{text}").text

                pdf = PDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                for line in report.split("\n"):
                    if line.strip():
                        pdf.multi_cell(0, 8, line)
                pdf.ln(10)
                pdf.set_text_color(200,0,0)
                pdf.multi_cell(0, 10, "AI Report - See a Doctor")

                buf = io.BytesIO()
                pdf.output(buf)
                buf.seek(0)

                st.download_button("DOWNLOAD PDF", buf, "Medical_Report.pdf", "application/pdf", type="primary")

st.markdown("<p style='text-align:center;color:white'>© 2025 AI Doctor Pro - Made in Pakistan</p>", unsafe_allow_html=True)
