import streamlit as st
from openai import OpenAI
import azure.cognitiveservices.speech as speechsdk
import time

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
speech_config.speech_synthesis_voice_name = "az-AZ-BabekNeural"

# === Streamlit UI ===
st.set_page_config(page_title="Azure Real-time Voice Assistant", page_icon="🎙️")
st.title("🎙️ Azərbaycan Dilli Səsli Köməkçi (Cümlə-cümlə səsli cavab)")

user_input = st.text_input("Sualını yaz:")

if st.button("Danış!"):
    if not user_input.strip():
        st.warning("Zəhmət olmasa, sualı yaz.")
    else:
        st.info("💭 GPT düşünür və danışacaq...")
        st_placeholder = st.empty()
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

        # Stream GPT answer sentence by sentence
        full_answer = ""
        current_sentence = ""
        with st.spinner("Axınla cavab yaradılır..."):
            stream = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "Sən Azərbaycan dilində, təbii və aydın tonda danışan asistentsən."},
                    {"role": "user", "content": user_input},
                ],
                stream=True
            )

            for chunk in stream:
                delta = chunk.choices[0].delta
                if "content" in delta:
                    token = delta["content"]
                    full_answer += token
                    current_sentence += token
                    st_placeholder.markdown(f"💬 **{full_answer}**")

                    # Hər cümlə bitəndə səsləndir
                    if any(p in token for p in [".", "!", "?"]):
                        synthesizer.speak_text_async(current_sentence.strip()).get()
                        current_sentence = ""
                        time.sleep(0.1)

        # Əgər son cümlə qalıbsa, onu da səsləndir
        if current_sentence.strip():
            synthesizer.speak_text_async(current_sentence.strip()).get()

        st.success("✅ Cavab tamlandı.")

