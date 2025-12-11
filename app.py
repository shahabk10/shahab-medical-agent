# AI DOCTOR PRO – 100% WORKING FINAL VERSION (Tested Live on Streamlit Cloud)
import streamlit as st
import google.generativeai as genai
from fpdf import FPDF
from gtts import gTTS
from PIL import Image
import io

# ==================== API KEY ====================
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.error("GEMINI_API_KEY not found! Add it in Secrets.")
    st.stop()

st.set_page_config(page_title="AI Doctor Pro", page_icon="Doctor", layout="centered")

# ==================== DESIGN ====================
st.markdown("""
<style>
    .stApp {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .title {font-size:4.5rem; text-align:center; font-weight:900;
            background:linear-gradient(90deg,#00ffea,#ff00c8);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;}
    .chat-box {background:rgba(255,255,255,0.12); padding:20px; border-radius:20px;
               backdrop-filter:blur(12px); margin:15px 0;}
    .user {background:#00d4ff; color:white; padding:16px; border-radius:20px 20px 0 20px;
           max-width:75%; margin-left:auto; margin-bottom:12px;}
    .ai {background:#1e1e1e; color:#00ffea; padding:16px; border-radius:20px 20px 20px 0;
         max-width:75%; margin-bottom:12px;}
</style>
""", unsafe_allow_html=True)

# ==================== MODEL (WORKING EVERYWHERE) ====================
@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        "gemini-1.5-flash",  # yeh sabke liye kaam karta hai
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    )

model = get_model()

# ==================== VOICE ====================
def speak(text):
    try:
        tts = gTTS(text=str(text)[:180], lang='en', tld='co.uk')
        audio = io.BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)
        st.audio(audio, autoplay=True)
    except:
        pass

# ==================== EMERGENCY ====================
def is_emergency(text):
    return any(x in text.lower() for x in ["heart attack","chest pain","can't breathe","bleeding","stroke","suicide","poison"])

# ==================== SESSION STATE ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.vision = "No image uploaded"
    st.session_state.chat_ended = False

if not st.session_state.messages:
    hello = "Hello! I'm your AI Doctor with a British accent. How may I help you today?"
    st.session_state.messages.append({"role": "ai", "content": hello})
    speak(hello)

# ==================== SIDEBAR ====================
page = st.sidebar.radio("Menu", ["Home", "Chat with Doctor", "Find Hospital", "Get Report"])

# ==================== HOME ====================
if page == "Home":
    st.markdown('<h1 class="title">AI DOCTOR PRO</h1>', unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;color:white'>Your Personal AI Medical Assistant</h3>", unsafe_allow_html=True)
    if st.button("START CONSULTATION", type="primary", use_container_width=True):
        st.rerun()

# ==================== CHAT PAGE ====================
elif page == "Chat with Doctor":
    st.header("Chat with AI Doctor")

    # Image Upload
    uploaded = st.file_uploader("Upload prescription/symptom photo", type=["png","jpg","jpeg","webp"])
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, width=300)
        with st.spinner("Analyzing image..."):
            try:
                res = model.generate_content(["Analyze this medical image clearly.", img])
                st.session_state.vision = res.text
                st.success("Image analyzed!")
                st.info(res.text)
                speak("Image analyzed")
            except:
                st.error("Image analysis failed this time.")

    # Show messages
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f'<div class="user">{m["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="ai">Doctor: {m["content"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # User input
    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        if is_emergency(prompt):
            alert = "EMERGENCY! CALL 1122 OR 15 IMMEDIATELY!"
            st.error(alert)
            speak("Emergency! Call 1122 now")
            st.session_state.messages.append({"role": "ai", "content": alert})
            st.rerun()

        # AI REPLY (with error handling)
        with st.spinner("Doctor is replying..."):
            try:
                # Simple prompt without history overload
                response = model.generate_content(f"You are a kind doctor. Patient said: " + prompt)
                reply = response.text
            except Exception as e:
                reply = "I'm having connection issues. Please try again in a moment."
            st.session_state.messages.append({"role": "ai", "content": reply})
            speak(reply)
        st.rerun()

    if st.button("End Chat & Generate Report"):
        st.session_state.chat_ended = True
        st.success("Chat ended → Go to 'Get Report'")

# ==================== HOSPITAL ====================
elif page == "Find Hospital":
    st.header("Nearby Hospitals")
    city = st.text_input("Enter city", "Lahore")
    if st.button("Search"):
        url = f"https://maps.google.com/maps?q=hospital+near+{city}&output=embed"
        st.components.v1.iframe(url, height=550)

# ==================== REPORT (NOW WORKING) ====================
elif page == "Get Report":
    st.header("Your Medical Report")
    if not st.session_state.chat_ended:
        st.warning("Please finish the chat first")
    else:
        if st.button("Generate & Download PDF", type="primary"):
            with st.spinner("Creating report..."):
                # Simple text without overloading Gemini
                chat_text = "\n".join([f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages])
                full = f"Chat:\n{chat_text}\n\nImage Analysis:\n{st.session_state.vision}"

                try:
                    report = model.generate_content("Create a short clean medical report from this:\n" + full).text
                except:
                    report = full  # fallback

                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 8, report)
                pdf.ln(10)
                pdf.set_text_color(200,0,0)
                pdf.multi_cell(0, 10, "This is AI generated. Consult a real doctor.")

                buf = io.BytesIO()
                pdf.output(buf)
                buf.seek(0)

                st.balloons()
                st.download_button(
                    "DOWNLOAD MEDICAL REPORT",
                    data=buf,
                    file_name="AI_Doctor_Report.pdf",
                    mime="application/pdf",
                    type="primary"
                )

st.markdown("<p style='text-align:center;color:white'>© 2025 AI Doctor Pro • Made with love in Pakistan</p>", unsafe_allow_html=True)
