import streamlit as st
from openai import OpenAI
import azure.cognitiveservices.speech as speechsdk
from io import BytesIO

# === Secrets ===
AZURE_OPENAI_KEY = st.secrets["AZURE_OPENAI_KEY"]
AZURE_OPENAI_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_DEPLOYMENT = st.secrets["AZURE_OPENAI_DEPLOYMENT"]
AZURE_SPEECH_KEY = st.secrets["AZURE_SPEECH_KEY"]
AZURE_SPEECH_REGION = st.secrets["AZURE_SPEECH_REGION"]

# === Azure OpenAI client ===
client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    default_headers={"api-key": AZURE_OPENAI_KEY}
)

# === Azure Speech config ===
speech_config = speechsdk.SpeechConfig(subscription=AZURE_SPEECH_KEY, region=AZURE_SPEECH_REGION)
speech_config.speech_synthesis_language = "az-AZ"
speech_config.speech_synthesis_voice_name = "az-AZ-BabekNeural"  # ✅ Azerbaijani male neural voice

# === Streamlit UI ===
st.set_page_config(page_title="Azure Realtime Voice Assistant", page_icon="🎙️")
st.title("🎙️ Azərbaycan Dilli Səsli Köməkçi (Azure OpenAI + Azure Speech)")

user_input = st.text_input("Sualını yaz:")

if st.button("Danış!"):
    if not user_input.strip():
        st.warning("Zəhmət olmasa, sualı yaz.")
    else:
        # 1️⃣ LLM cavabı
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

        # 2️⃣ Azure Speech realtime TTS
        with st.spinner("Səsləndirilir (real-time)..."):
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            result = synthesizer.speak_text_async(answer).get()
            audio_data = result.audio_data
            st.audio(BytesIO(audio_data), format="audio/wav")
