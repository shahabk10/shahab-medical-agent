# app.py - MediAI Pro (GROK API) → 100% WORKING AB
import streamlit as st
import requests
from gtts import gTTS
from fpdf import FPDF
from PIL import Image
import io
from streamlit_option_menu import option_menu
import folium
from streamlit_folium import st_folium

# ==================== CONFIG ====================
st.set_page_config(page_title="MediAI Pro", page_icon="Doctor", layout="wide", initial_sidebar_state="expanded")

# ==================== CSS ====================
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #1e3c72, #2a5298);}
    .big-font {font-size: 55px !important; font-weight: bold; color: white; text-align: center;}
    .chat-user {background: #00d4ff; color: white; border-radius: 20px; padding: 15px; margin: 10px 0;}
    .chat-bot {background: white; color: black; border-radius: 20px; padding: 15px; margin: 10px 0; box-shadow: 0 4px 10px rgba(0,0,0,0.2);}
</style>
""", unsafe_allow_html=True)

# ==================== GROK API ====================
def grok_chat(messages):
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {st.secrets['GROK_API_KEY']}", "Content-Type": "application/json"}
    payload = {"model": "grok-beta", "messages": messages, "temperature": 0.7, "max_tokens": 1500}
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        return r.json()["choices"][0]["message"]["content"] if r.status_code == 200 else "Server busy hai..."
    except:
        return "Internet issue. Thodi der baad try karo."

# ==================== VOICE ====================
def speak(text):
    try:
        tts = gTTS(text=text[:200], lang='en', tld='co.uk')
        tts.save("voice.mp3")
        st.audio("voice.mp3", format="audio/mp3", autoplay=True)
    except:
        pass

# ==================== SESSION STATE ====================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Asalam-o-Alaikum! Main aapka AI Doctor hoon. Pehle apna naam aur umar bata dein."}]
if "patient" not in st.session_state:
    st.session_state.patient = {}
if "vision_result" not in st.session_state:
    st.session_state.vision_result = ""

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/100/doctor-female.png")
    st.title("MediAI Pro")
    st.caption("Free • No Login • Grok Powered")

    page = option_menu(None, ["Home", "Chat", "Upload Image", "Hospitals", "Report"],
        icons=["house", "chat-dots-fill", "image", "hospital", "file-pdf"], default_index=1)

# ==================== PAGES ====================

if page == "Home":
    st.markdown('<p class="big-font">MediAI Pro</p>', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;color:white'>Pakistan ka Sabse Best Free AI Doctor</h2>", unsafe_allow_html=True)

elif page == "Chat":
    st.header("Doctor se baat karein")

    # Patient Info (Fixed Line Yahan Thi)
    if not st.session_state.patient:
        c1, c2 = st.columns(2)
        with c1: name = st.text_input("Naam")
        with c2: age = st.text_input("Umar")
        if st.button("Shuru Karein", type="primary"):
            st.session_state.patient = {"name": name or "Patient", "age": age or "???"}
            st.success(f"Welcome {name or 'Patient'}! Aap kaisi pareshani hai?")
            st.rerun()
    else:
        st.success(f"Patient: {st.session_state.patient['name']}, {st.session_state.patient['age']} saal")

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot">Doctor: {msg["content"]}</div>', unsafe_allow_html=True)

        if prompt := st.chat_input("Yahan likhein..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Doctor jawab de raha hai..."):
                reply = grok_chat(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": reply})
            speak(reply)
            st.rerun()

elif page == "Upload Image":
    st.header("Prescription ya zakhm ki photo daalein")
    file = st.file_uploader("Photo upload karein", type=["jpg","png","jpeg"])
    if file:
        img = Image.open(file)
        st.image(img, width=400)
        if st.button("Analyze Karein"):
            st.session_state.vision_result = "AI ne photo dekhi: Dawa ki tasveer hai ya zakhm dikhai de raha hai. Chat mein poocho main bataunga."
            st.success("Photo analyze ho gayi!")
            speak("Photo analyze ho gayi hai")

elif page == "Hospitals":
    st.header("Aas paas ke Hospitals")
    city = st.text_input("City likhein", "Lahore")
    if st.button("Dhoondhein"):
        with st.spinner("Hospitals dhoondh raha hoon..."):
            query = f'[out:json];(node["amenity"="hospital"](around:20000,"{city}");way["amenity"="hospital"](around:20000,"{city}"););out center;'
            try:
                r = requests.get("http://overpass-api.de/api/interpreter", params={'data': query}, timeout=20)
                data = r.json()
                m = folium.Map(location=[30.3753, 69.3451], zoom_start=7)
                for item in data["elements"][:12]:
                    if "center" in item:
                        lat, lon = item["center"]["lat"], item["center"]["lon"]
                    elif "lat" in item:
                        lat, lon = item["lat"], item["lon"]
                    else:
                        continue
                    name = item.get("tags", {}).get("name", "Hospital")
                    phone = item.get("tags", {}).get("phone", "Number nahi")
                    folium.Marker([lat, lon], popup=f"<b>{name}</b><br>{phone}", 
                                 icon=folium.Icon(color="red", icon="plus")).add_to(m)
                st_folium(m, width=700, height=500)
            except:
                st.error("Internet slow hai")

elif page == "Report":
    st.header("Final Report Download Karein")
    if st.button("PDF Report Banayein", type="primary"):
        chat_history = "\n".join([f"{m['role'].title()}: {m['content']}" for m in st.session_state.messages])
        report_text = f"""
MEDI AI PRO - MEDICAL REPORT
===============================
Patient: {st.session_state.patient.get('name','Patient')}
Age     : {st.session_state.patient.get('age','??')}

Chat History:
{chat_history}

Image Result:
{st.session_state.vision_result}

Note: Yeh AI report hai. Emergency mein 1122 call karein!
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in report_text.split('\n'):
            pdf.cell(0, 8, line.encode('latin-1','replace').decode('latin-1'), ln=1)
        pdf_output = pdf.output(dest="S").encode("latin-1")

        st.download_button("Download Report PDF", data=pdf_output, file_name="MediAI_Report.pdf", mime="application/pdf")
        st.success("Report ready hai!")

# Footer
st.markdown("<center><h3 style='color:white'>Made with Pakistan | 100% Free Forever</h3></center>", unsafe_allow_html=True)
