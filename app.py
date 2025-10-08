import streamlit as st
import requests
import openai
from io import BytesIO

# === API açarları ===
openai.api_key = st.secrets["OPENAI_API_KEY"]
ELEVEN_API_KEY = st.secrets["ELEVEN_API_KEY"]
VOICE_ID = st.secrets["VOICE_ID"]

# === Streamlit interfeysi ===
st.set_page_config(page_title="AZETT Voice Assistant", page_icon="🎙️", layout="centered")
st.title("🎙️ Peşəkar Azərbaycan Səsli Köməkçi")
st.markdown(
    """
    Bu tətbiq **GPT-4o-mini** modelindən istifadə edərək suallara Azərbaycan dilində cavab verir  
    və **ElevenLabs v3** modeli ilə qadın səsində səsləndirir 🔊  
    """
)

user_input = st.text_input("Sualını və ya mətni yaz:")

if st.button("Danış!"):
    if not user_input.strip():
        st.warning("Zəhmət olmasa, bir mətni yaz.")
    else:
        # 1️⃣ LLM cavabı alırıq
        with st.spinner("LLM düşünür..."):
            completion = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Cavabları yalnız Azərbaycan dilində və peşəkar, köməkçi tonda ver."},
                    {"role": "user", "content": user_input},
                ]
            )
            answer = completion.choices[0].message.content.strip()
            st.success(f"💬 Cavab: {answer}")

        # 2️⃣ ElevenLabs TTS ilə səsi yaradırıq
        with st.spinner("Səsləndirilir..."):
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
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
            response = requests.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                audio_data = BytesIO(response.content)
                st.audio(audio_data, format="audio/mp3")
            else:
                st.error(f"Səs yaradıla bilmədi: {response.status_code}")

