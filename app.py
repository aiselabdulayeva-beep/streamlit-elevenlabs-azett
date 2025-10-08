import streamlit as st
import requests
import openai
from pydub import AudioSegment
from pydub.playback import play
import io

# API açarları
openai.api_key = st.secrets["OPENAI_API_KEY"]
ELEVEN_API_KEY = st.secrets["ELEVEN_API_KEY"]
VOICE_ID = st.secrets["VOICE_ID"]

st.title("🎙️ Azərbaycan dilində Səsli Chatbot (LLM + ElevenLabs v3)")
st.write("LLM cavablarını real vaxtda Azərbaycan dilində səsləndirir.")

# İstifadəçi girişi
user_input = st.text_input("Mətni və ya sualını yaz:")

if st.button("Danış!"):
    if not user_input.strip():
        st.warning("Zəhmət olmasa, bir sual yaz.")
    else:
        with st.spinner("LLM düşünür..."):
            # LLM cavabı (Azərbaycan dilində)
            llm_response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Cavabları yalnız Azərbaycan dilində ver."},
                    {"role": "user", "content": user_input},
                ]
            )
            text = llm_response.choices[0].message.content.strip()
            st.success(f"💬 LLM cavabı: {text}")

        # ElevenLabs TTS (REST API)
        with st.spinner("Səsləndirilir..."):
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
            headers = {
                "xi-api-key": ELEVEN_API_KEY,
                "Content-Type": "application/json"
            }
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v3",
                "language_code": "AZE",
                "voice_settings": {"stability": 0.4, "similarity_boost": 0.8}
            }

            response = requests.post(url, headers=headers, json=data)
            audio_bytes = io.BytesIO(response.content)

            st.audio(audio_bytes, format="audio/mp3")

