import streamlit as st
import streamlit as st
import requests
from openai import OpenAI
from io import BytesIO

# === Secrets-dən məlumatlar ===
API_KEY = st.secrets["AZURE_OPENAI_KEY"]
ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
DEPLOYMENT_NAME = st.secrets["AZURE_OPENAI_DEPLOYMENT"]

ELEVEN_API_KEY = st.secrets["ELEVEN_API_KEY"]
VOICE_ID = st.secrets["VOICE_ID"]

# === Azure OpenAI client yaradılır ===
client = OpenAI(
    base_url=f"{ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/extensions",
    api_key=API_KEY
)

# === Streamlit interfeysi ===
st.set_page_config(page_title="Azure + ElevenLabs Assistant", page_icon="🎙️")
st.title("🎙️ Azərbaycan Dilli Səsli Köməkçi (Azure OpenAI + ElevenLabs)")

user_input = st.text_input("Sualını yaz:")

if st.button("Danış!"):
    if not user_input.strip():
        st.warning("Zəhmət olmasa, sualı yaz.")
    else:
        # 1️⃣ Azure OpenAI cavabı
        with st.spinner("LLM düşünür..."):
            completion = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": "Sən Azərbaycan dilində, peşəkar və köməkçi tonda danışan asistentsən."},
                    {"role": "user", "content": user_input},
                ],
            )
            answer = completion.choices[0].message.content
            st.success(f"💬 Cavab: {answer}")

        # 2️⃣ ElevenLabs ilə səsləndiririk
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
