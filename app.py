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
# 1. CONFIGURATION & COLORFUL THEME
# ---------------------------------------------------------
st.set_page_config(
    page_title="Shahab Smart Health",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN COLORFUL CSS ---
st.markdown("""
<style>
    /* Gradient Background */
    .stApp {
        background: linear-gradient(120deg, #a1c4fd 0%, #c2e9fb 100%);
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #002b36;
        color: white;
    }
    
    /* Chat Bubbles */
    .user-msg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 18px;
        border-radius: 20px 20px 5px 20px;
        margin-bottom: 10px;
        text-align: right;
        font-weight: 500;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .agent-msg {
        background: #ffffff;
        color: #333;
        padding: 12px 18px;
        border-radius: 20px 20px 20px 5px;
        margin-bottom: 10px;
        text-align: left;
        border-left: 5px solid #00c6ff;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(to right, #11998e, #38ef7d); 
        color: white;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0px 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. API SETUP (CORRECTED IMPORT)
# ---------------------------------------------------------
try:
    if "GEMINI_API_KEY" in st.secrets:
        # Yahan hum purana lekin stable tareeqa use kar rahay hain
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.error("⚠️ API Key Not Found! Please check Streamlit Secrets.")
        st.stop()
except Exception as e:
    st.error(f"Setup Error: {e}")

# Session States
if "history" not in st.session_state:
    st.session_state.history = []
if "vision_analysis" not in st.session_state:
    st.session_state.vision_analysis = "No image uploaded yet."

# ---------------------------------------------------------
# 3. FUNCTIONS
# ---------------------------------------------------------
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def text_to_speech(text):
    try:
        tts = gTTS(text=text[:300], lang='en', tld='co.uk')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

# ---------------------------------------------------------
# 4. NAVIGATION
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=100)
    st.markdown("### 🏥 Shahab Medical AI")
    st.markdown("---")
    page = st.radio("Navigate:", ["🏠 Home Dashboard", "🤖 Smart Doctor", "🗺️ Live Hospital Map", "📄 Download Report"])
    st.markdown("---")
    st.info("🚑 **Emergency: Call 1122**")

# ---------------------------------------------------------
# PAGE 1: HOME
# ---------------------------------------------------------
if page == "🏠 Home Dashboard":
    st.title("🌟 Shahab Smart Health System")
    st.markdown("#### The Future of AI Healthcare in Pakistan")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("")
        st.write("Welcome to the most advanced AI medical assistant. We combine **Google Gemini AI** with **Real-time Mapping** to ensure you get the best care.")
        st.success("✨ **Features:** Live Location, Clinic Finder, & AI Diagnosis")
    
    with col2:
        lottie_med = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_cal1600b.json")
        if lottie_med:
            st_lottie(lottie_med, height=300)

# ---------------------------------------------------------
# PAGE 2: SMART DOCTOR
# ---------------------------------------------------------
elif page == "🤖 Smart Doctor":
    st.title("🤖 Dr. AI Consultant")
    st.caption("Discuss your symptoms or upload a prescription.")

    # Image Upload
    with st.expander("📸 Upload Medical Record / X-Ray"):
        uploaded_file = st.file_uploader("Choose Image", type=['png', 'jpg', 'jpeg'])
        if uploaded_file and st.button("Analyze Image"):
            with st.spinner("Dr. AI is reading the image..."):
                image = Image.open(uploaded_file)
                st.image(image, width=200)
                try:
                    # Correct method for gemini-1.5-flash
                    response = model.generate_content(["Describe this medical image and list any medicines.", image])
                    st.session_state.vision_analysis = response.text
                    st.session_state.history.append(("AI", f"**Image Analysis:** {response.text}"))
                    st.success("Image Analyzed!")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Chat History
    for role, text in st.session_state.history:
        if role == "User":
            st.markdown(f'<div class="user-msg">👤 {text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="agent-msg">🩺 {text}</div>', unsafe_allow_html=True)

    # Chat Input
    user_input = st.chat_input("Type your problem here...")
    
    if user_input:
        st.session_state.history.append(("User", user_input))
        st.markdown(f'<div class="user-msg">👤 {user_input}</div>', unsafe_allow_html=True)

        with st.spinner("Dr. AI is thinking..."):
            try:
                context = f"History: {st.session_state.history[-5:]}. Vision Data: {st.session_state.vision_analysis}. User: {user_input}"
                response = model.generate_content(context)
                reply = response.text
                
                st.session_state.history.append(("AI", reply))
                st.markdown(f'<div class="agent-msg">🩺 {reply}</div>', unsafe_allow_html=True)
                
                audio = text_to_speech(reply)
                if audio:
                    st.audio(audio, format='audio/mp3')
                    
            except Exception as e:
                st.error(f"Connection Error: {e}")

# ---------------------------------------------------------
# PAGE 3: LIVE MAP (CLINICS + LOCATION)
# ---------------------------------------------------------
elif page == "🗺️ Live Hospital Map":
    st.title("🏥 Hospitals & Clinics Finder")
    st.write("Click the **📍 Black Box Button** (top-left of map) to find your location.")

    city = st.selectbox("Select City", ["Islamabad", "Lahore", "Karachi"])

    locations = {
        "Islamabad": [33.6844, 73.0479],
        "Lahore": [31.5204, 74.3587],
        "Karachi": [24.8607, 67.0011]
    }

    medical_centers = {
        "Islamabad": [
            {"name": "PIMS Hospital (Govt)", "lat": 33.7077, "lon": 73.0501, "type": "Hospital", "color": "red"},
            {"name": "Shifa International", "lat": 33.6766, "lon": 73.1068, "type": "Hospital", "color": "red"},
            {"name": "Ali Medical Clinic", "lat": 33.6930, "lon": 73.0550, "type": "Clinic", "color": "green"}
        ],
        "Lahore": [
            {"name": "Jinnah Hospital", "lat": 31.4883, "lon": 74.2987, "type": "Hospital", "color": "red"},
            {"name": "Doctors Hospital", "lat": 31.4789, "lon": 74.2801, "type": "Hospital", "color": "red"}
        ],
        "Karachi": [
            {"name": "Aga Khan Hospital", "lat": 24.8926, "lon": 67.0740, "type": "Hospital", "color": "red"}
        ]
    }

    m = folium.Map(location=locations[city], zoom_start=12)
    LocateControl(auto_start=False, strings={"title": "Show my location"}).add_to(m)
    marker_cluster = MarkerCluster().add_to(m)

    for center in medical_centers[city]:
        folium.Marker(
            [center['lat'], center['lon']],
            popup=f"<b>{center['name']}</b>",
            tooltip=center['name'],
            icon=folium.Icon(color=center['color'], icon="info-sign")
        ).add_to(marker_cluster)

    st_folium(m, width=1200, height=500)

# ---------------------------------------------------------
# PAGE 4: REPORT
# ---------------------------------------------------------
elif page == "📄 Download Report":
    st.title("📄 Generate Medical Report")
    
    if st.session_state.history:
        if st.button("🖨️ Create PDF Report"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="SHAHAB SMART HEALTH - AI REPORT", ln=True, align='C')
            
            for role, text in st.session_state.history:
                clean_text = text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, f"{role}: {clean_text}")
                pdf.ln(2)
            
            pdf_out = pdf.output(dest='S').encode('latin-1')
            st.download_button(label="📥 Download PDF", data=pdf_out, file_name="Medical_Report.pdf", mime="application/pdf")
            st.success("Report Generated!")
    else:
        st.warning("No consultation history found.")
