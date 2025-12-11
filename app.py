# app.py - MediAI Pro (GROK API – 100% FREE & NO BILLING)
import streamlit as st
import requests
import json
from gtts import gTTS
from fpdf import FPDF
from PIL import Image
import io
import base64
from streamlit_option_menu import option_menu
import folium
from streamlit_folium import st_folium

# ==================== PAGE CONFIG ====================
st.set_page_config(page_title="MediAI Pro", page_icon="Heart", layout="wide")

# ==================== CSS ====================
st.markdown("""
<style>
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);}
    .big-font {font-size: 50px !important; font-weight: bold; color: white; text-align: center;}
    .chat-user {background: #4facfe; color: white; border-radius: 20px; padding: 15px; margin: 10px 0;}
    .chat-bot {background: white; color: black; border-radius: 20px; padding: 15px; margin: 10px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

# ==================== GROK API CALL ====================
def grok_chat(message, history=[]):
    url = "https://api.grok.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {st.secrets['GROK_API_KEY']}",
        "Content-Type": "application/json"
    }
    # History ko Grok format mein convert karo
    messages = [{"role": "user" if i%2==0 else "assistant", "content": msg} for i, msg in enumerate(history)]
    messages.append({"role": "user", "content": message})
    
    payload = {
        "model": "grok-beta",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error {response.status_code}: {response.text}"
    except:
        return "Sorry, server issue hai. Thodi der baad try karo."

# ==================== VOICE ====================
def speak(text):
    try:
        tts = gTTS(text=text[:200], lang='en', tld='co.uk')
        tts.save("voice.mp3")
        audio_file = open("voice.mp3", "rb")
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    except:
        pass

# ==================== SESSION STATE ====================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "patient" not in st.session_state:
    st.session_state.patient = {}

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/doctor-female.png", width=100)
    st.title("MediAI Pro")
    st.markdown("### Powered by Grok (Free)")
    
    choice = option_menu(
        menu_title=None,
        options=["Home", "Chat", "Image", "Hospitals", "Report"],
        icons=["house", "chat", "camera", "hospital", "file-text"],
        default_index=0
    )

# ==================== PAGES ====================
if choice == "Home":
    st.markdown('<p class="big-font">MediAI Pro</p>', unsafe_allow_html=True)
    st.markdown("### 100% Free • No Login • No Card • Made in Pakistan")
    st.image("https://img.icons8.com/color/96/artificial-intelligence.png")

elif choice == "Chat":
    st.header("AI Doctor se baat karo")
    
    if not st.session_state.patient:
        name = st.text_input("Naam likho")
        age = st.text_input("Umar")
        if st.button("Start"):
            st.session_state.patient = {"name": name or "Patient", "age": age or "??"}
            st.rerun()
    
    else:
        st.success(f"{st.session_state.patient['name']}, {st.session_state.patient['age']} saal")
        
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bot">Doctor: {msg["content"]}</div>', unsafe_allow_html=True)
        
        if prompt := st.chat_input("Apna masla batao..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Doctor soch raha hai..."):
                reply = grok_chat(prompt, [m["content"] for m in st.session_state.messages[:-1]])
            st.session_state.messages.append({"role": "assistant", "content": reply})
            speak(reply)
            st.rerun()

# Baaki pages (Image, Hospitals, Report) same rakh sakte ho ya chahta hai full version?

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center;color:white'>Made with ❤️ Pakistan • 100% Free • Grok Powered</p>", unsafe_allow_html=True)
