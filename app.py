import streamlit as st
from openai import AzureOpenAI
import streamlit as st
import requests
from io import BytesIO

# === Azure OpenAI üçün dəyişənlər ===
AZURE_API_KEY = st.secrets["AZURE_OPENAI_KEY"]
AZURE_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
AZURE_DEPLOYMENT = st.secrets["AZURE_OPENAI_DEPLOYMENT"]

# === ElevenLabs üçün dəyişənlər ===
ELEVEN_API_KEY = st.secrets["ELEVEN_API_KEY"]
VOICE_ID = st.secrets["VOICE_ID"]

# === AzureOpenAI müştərisini yaradılırıq ===
client = AzureOpenAI(
    api_key=AZURE_API_KEY,
    api_version="2024-05-01-preview",
    azure_endpoint=AZURE_ENDPOINT
)

st.set_page_config(page_title="AZURE + ElevenLabs Assistant", page_icon="🎙️")
st.title("🎙️ Peşəkar Azərbaycan Dilli Köməkçi (Azure OpenAI versiyası)")

user_input = st.text_input("Sualını və ya mətni yaz:")

if st.button("Danış!"):
    if not user_input.strip():
        st.warning("Zəhmət olmasa, bir mətni yaz.")
    else:
        # 1️⃣ Azure OpenAI cavabı
        with st.spinner("LLM düşünür..."):
            response = client.chat.completions.create(
                model=AZURE_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "Cavabları Azərbaycan dilində, peşəkar və aydın tonda ver."},
                    {"role": "user", "content": user_input}
                ]
            )
            answer = response.choices[0].message.content
            st.success(f"💬 Cavab: {answer}")

        # 2️⃣ ElevenLabs TTS ilə səsləndiririk
        with st.spinner("Səsləndirilir..."):
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
            headers = {
                "xi-api-key": ELEVEN_API_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "text": answer,
                "model_id": "eleven_multilingual_v3",
                "language_code": "AZE",
                "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
            }

            tts_response = requests.post(tts_url, headers=headers, json=payload)

            if tts_response.status_code == 200:
                st.audio(BytesIO(tts_response.content), format="audio/mp3")
            else:
                st.error(f"Səs yaradıla bilmədi: {tts_response.status_code}")
