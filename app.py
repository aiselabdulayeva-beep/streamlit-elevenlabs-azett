import streamlit as st
import requests
from openai import OpenAI  # note: not AzureOpenAI here
from io import BytesIO

# === Secrets ===
AZURE_OPENAI_KEY = st.secrets["AZURE_OPENAI_KEY"]
AZURE_OPENAI_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]  # e.g. "https://kapitalbank-ai.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT = st.secrets["AZURE_OPENAI_DEPLOYMENT"]  # e.g. "gpt-4o-mini"
ELEVEN_API_KEY = st.secrets["ELEVEN_API_KEY"]
VOICE_ID = st.secrets["VOICE_ID"]

# === Azure client (generic version) ===
# Construct correct Azure Chat Completions endpoint:
# Azure's format: https://{resource}.openai.azure.com/openai/deployments/{deployment_name}
client = OpenAI(
    base_url=f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_OPENAI_DEPLOYMENT}",
    api_key=AZURE_OPENAI_KEY
)

# === Streamlit interface ===
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
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "Sən Azərbaycan dilində, peşəkar və köməkçi tonda danışan asistentsən."},
                    {"role": "user", "content": user_input},
                ]
            )

            answer = completion.choices[0].message.content
            st.success(f"💬 Cavab: {answer}")

        # 2️⃣ ElevenLabs TTS
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

