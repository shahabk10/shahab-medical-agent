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
    
    /* Card/Glassmorphism Effect */
    .css-1r6slb0, .stMarkdown, .stButton {
        border-radius: 15px;
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
    
    /* Headers */
    h1, h2, h3 {
        color: #2c3e50;
        font-family: 'Trebuchet MS', sans-serif;
        text-shadow: 1px 1px 2px #fff;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. API SETUP
# ---------------------------------------------------------
try:
    if "GEMINI_API_KEY" in st.secrets:
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
        tts = gTTS(text=text[:300], lang='en', tld='co.uk') # UK Accent
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
        st.success("✨ **New Feature:** Live Location Tracking Added!")
        st.info("✨ **New Feature:** Small Clinics & Dispensaries Added!")
    
    with col2:
        lottie_med = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_cal1600b.json")
        if lottie_med:
            st_lottie(lottie_med, height=300)

# ---------------------------------------------------------
# PAGE 2: SMART DOCTOR (FIXED)
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
        # Display User Message Immediately
        st.session_state.history.append(("User", user_input))
        st.markdown(f'<div class="user-msg">👤 {user_input}</div>', unsafe_allow_html=True)

        # Generate AI Response
        with st.spinner("Dr. AI is thinking..."):
            try:
                context = f"History: {st.session_state.history[-5:]}. Vision Data: {st.session_state.vision_analysis}. User: {user_input}"
                response = model.generate_content(context)
                reply = response.text
                
                st.session_state.history.append(("AI", reply))
                st.markdown(f'<div class="agent-msg">🩺 {reply}</div>', unsafe_allow_html=True)
                
                # Audio
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
    st.write("Click the **📍 button** on the map (top-left) to see your **Live Location**.")

    city = st.selectbox("Select City", ["Islamabad", "Lahore", "Karachi"])

    locations = {
        "Islamabad": [33.6844, 73.0479],
        "Lahore": [31.5204, 74.3587],
        "Karachi": [24.8607, 67.0011]
    }

    # Enhanced Data with Clinics
    medical_centers = {
        "Islamabad": [
            {"name": "PIMS Hospital (Govt)", "lat": 33.7077, "lon": 73.0501, "type": "Hospital", "color": "red"},
            {"name": "Shifa International", "lat": 33.6766, "lon": 73.1068, "type": "Hospital", "color": "red"},
            {"name": "Ali Medical Clinic", "lat": 33.6930, "lon": 73.0550, "type": "Clinic", "color": "green"},
            {"name": "Blue Area Dispensary", "lat": 33.7100, "lon": 73.0600, "type": "Clinic", "color": "green"},
            {"name": "G-9 Family Clinic", "lat": 33.6850, "lon": 73.0250, "type": "Clinic", "color": "green"}
        ],
        "Lahore": [
            {"name": "Jinnah Hospital", "lat": 31.4883, "lon": 74.2987, "type": "Hospital", "color": "red"},
            {"name": "Doctors Hospital", "lat": 31.4789, "lon": 74.2801, "type": "Hospital", "color": "red"},
            {"name": "Shaukat Khanum Clinic", "lat": 31.4500, "lon": 74.3000, "type": "Clinic", "color": "green"},
            {"name": "Model Town Clinic", "lat": 31.4900, "lon": 74.3200, "type": "Clinic", "color": "green"}
        ],
        "Karachi": [
            {"name": "Aga Khan Hospital", "lat": 24.8926, "lon": 67.0740, "type": "Hospital", "color": "red"},
            {"name": "Liaquat National", "lat": 24.8870, "lon": 67.0671, "type": "Hospital", "color": "red"},
            {"name": "Clifton Medical Clinic", "lat": 24.8200, "lon": 67.0300, "type": "Clinic", "color": "green"},
            {"name": "Gulshan e Iqbal Dispensary", "lat": 24.9000, "lon": 67.0900, "type": "Clinic", "color": "green"}
        ]
    }

    # Initialize Map
    m = folium.Map(location=locations[city], zoom_start=12)
    
    # 1. Add Live Location Button
    LocateControl(auto_start=False, strings={"title": "Show my location"}).add_to(m)

    # 2. Add Markers (Cluster for cleaner look)
    marker_cluster = MarkerCluster().add_to(m)

    for center in medical_centers[city]:
        icon_type = "user-md" if center['type'] == "Clinic" else "hospital-o"
        
        html = f"""
        <div style="font-family:sans-serif; width:150px">
            <h5 style="color:{center['color']}">{center['name']}</h5>
            <span style="background:{center['color']}; color:white; padding:2px 6px; border-radius:4px; font-size:10px;">
                {center['type']}
            </span>
            <br><br>
            <a href="https://www.google.com/maps/dir/?api=1&destination={center['lat']},{center['lon']}" target="_blank">
            🚗 Navigate Here
            </a>
        </div>
        """
        
        folium.Marker(
            [center['lat'], center['lon']],
            popup=html,
            tooltip=center['name'],
            icon=folium.Icon(color=center['color'], icon=icon_type, prefix='fa')
        ).add_to(marker_cluster)

    st_folium(m, width=1200, height=500)
    st.caption("🔴 Red = Major Hospitals | 🟢 Green = Local Clinics")

# ---------------------------------------------------------
# PAGE 4: REPORT
# ---------------------------------------------------------
elif page == "📄 Download Report":
    st.title("📄 Generate Medical Report")
    st.markdown("---")
    
    if st.session_state.history:
        if st.button("🖨️ Create PDF Report"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            
            pdf.cell(200, 10, txt="SHAHAB SMART HEALTH - AI REPORT", ln=True, align='C')
            pdf.ln(10)
            
            # Simple text dump for PDF (to avoid complexity)
            for role, text in st.session_state.history:
                clean_text = text.encode('latin-1', 'replace').decode('latin-1')
                pdf.multi_cell(0, 10, f"{role}: {clean_text}")
                pdf.ln(2)
            
            pdf_out = pdf.output(dest='S').encode('latin-1')
            
            st.download_button(
                label="📥 Download PDF",
                data=pdf_out,
                file_name="Medical_Report.pdf",
                mime="application/pdf"
            )
            st.success("Report Generated!")
    else:
        st.warning("No consultation history found to print.")
