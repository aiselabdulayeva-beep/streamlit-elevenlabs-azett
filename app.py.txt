import streamlit as st
import requests
import openai
from io import BytesIO

# === API açarları ===
openai.api_key = st.secrets["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"]
ELEVEN_API_KEY = st.secrets["sk_291679d6e692fce76cc3e455e23a3268e2f2ccefd4ad4f11"]
VOICE_ID = st.secrets["t8kSqGbUxd45SW56awYR"]

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
