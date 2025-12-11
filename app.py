# AI DOCTOR PRO - FINAL 100% WORKING (NO MORE ERRORS)
import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from gtts import gTTS
from PIL import Image
import io

# === API KEY WITH SAFETY OFF ===
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("GEMINI_API_KEY missing in Secrets!")
    st.stop()

st.set_page_config(page_title="AI Doctor Pro", page_icon="Doctor", layout="centered")

# === THEME ===
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .title {font-size: 4.5rem; text-align: center; font-weight: 900;
            background: linear-gradient(90deg, #00ffea, #ff00c8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
    .chat-box {background: rgba(255,255,255,0.12); padding: 20px; border-radius: 20px;
               backdrop-filter: blur(12px); margin: 15px 0;}
    .user {background: #00d4ff; color: white; padding: 16px; border-radius: 20px 20px 0 20px;
           max-width: 78%; margin-left: auto; margin-bottom: 12px;}
    .ai {background: #1e1e1e; color: #00ffea; padding: 16px; border-radius: 20px 20px 20px 0;
         max-width: 78%; margin-bottom: 12px;}
</style>
""", unsafe_allow_html=True)

# === MODEL WITH SAFETY OFF (IMPORTANT!) ===
@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        'gemini-1.5-flash',  # sabse stable
        generation_config={"temperature": 0.7},
        safety_settings=[
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        ]
    )

model = get_model()

# === VOICE ===
def speak(text):
    try:
        tts = gTTS(text=str(text)[:180], lang='en', tld='co.uk')
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        st.audio(audio, autoplay=True)
    except:
        pass

# === EMERGENCY ===
def is_emergency(text):
    words = ["heart attack","chest pain","can't breathe","bleeding","stroke","suicide","poison","unconscious"]
    return any(word in text.lower() for word in words)

# === SESSION ===
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.vision = "No image uploaded"
    st.session_state.chat_ended = False

if not st.session_state.messages:
    greet = "Hello! I'm your AI Doctor with a British accent. How can I help you today?"
    st.session_state.messages.append({"role": "ai", "content": greet})
    speak(greet)

# === SIDEBAR ===
page = st.sidebar.radio("Menu", ["Home", "Chat with Doctor", "Find Hospital", "Get Report"])

# === HOME ===
if page == "Home":
    st.markdown('<h1 class="title">AI DOCTOR PRO</h1>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:white'>Talk • Photo • Voice • Report</h3>", unsafe_allow_html=True)
    if st.button("START NOW", type="primary", use_container_width=True):
        st.rerun()

# === CHAT PAGE ===
elif page == "Chat with Doctor":
    st.header("Chat with AI Doctor")

    # Image Upload
    uploaded = st.file_uploader("Upload prescription or photo", type=["png","jpg","jpeg"])
    if uploaded:
        with st.spinner("Analyzing image..."):
            img = Image.open(uploaded)
            st.image(img, width=300)
            try:
                result = model.generate_content(["Analyze this medical image clearly and professionally.", img]).text
                st.session_state.vision = result
                st.success("Done!")
                st.info(result)
                speak("Image analyzed")
            except Exception as e:
                st.error("Image analysis failed. Continue chat.")

    # Chat Display
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="user">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai">Doctor: {msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Input
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        if is_emergency(prompt):
            alert = "EMERGENCY! CALL 1122 OR 15 NOW!"
            st.error(alert)
            speak("Emergency! Call 1122 immediately")
            st.session_state.messages.append({"role": "ai", "content": alert})
            st.rerun()

        with st.spinner("Doctor replying..."):
            try:
                history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
                response = model.generate_content(history)
                reply = response.text.strip()
                st.session_state.messages.append({"role": "ai", "content": reply})
                speak(reply)
            except Exception as e:
                reply = "Sorry, I'm having trouble connecting right now. Please try again."
                st.session_state.messages.append({"role": "ai", "content": reply})
                speak(reply)
        st.rerun()

    if st.button("End Chat & Generate Report"):
        st.session_state.chat_ended = True
        st.success("Report ready! Go to 'Get Report'")

# === HOSPITAL & REPORT (Same as before, working) ===
elif page == "Find Hospital":
    st.header("Nearby Hospitals")
    city = st.text_input("City", "Lahore")
    if st.button("Search"):
        url = f"https://maps.google.com/maps?q=hospital+near+{city}&output=embed"
        st.components.v1.iframe(url, height=500)

elif page == "Get Report":
    st.header("Your Medical Report")
    if not st.session_state.chat_ended:
        st.warning("Finish chat first")
    else:
        if st.button("Generate PDF"):
            chat = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            text = f"Chat:\n{chat}\n\nImage: {st.session_state.vision}"
            report = model.generate_content(f"Make a clean medical report:\n{text}").text

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in report.split("\n"):
                if line.strip():
                    pdf.multi_cell(0, 8, line)
            buf = io.BytesIO()
            pdf.output(buf)
            buf.seek(0)

            st.download_button("DOWNLOAD PDF", buf, "Report.pdf", "application/pdf", type="primary")

st.markdown("<p style='text-align:center;color:white'>© 2025 AI Doctor Pro - Pakistan</p>", unsafe_allow_html=True)
