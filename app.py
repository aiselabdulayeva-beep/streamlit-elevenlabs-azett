import streamlit as st
from openai import OpenAI
import azure.cognitiveservices.speech as speechsdk
import time, base64

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
speech_config = speechsdk.SpeechConfig(
    subscription=AZURE_SPEECH_KEY,
    region=AZURE_SPEECH_REGION
)
speech_config.speech_synthesis_language = "az-AZ"
speech_config.speech_synthesis_voice_name = "az-AZ-BabekNeural"

# === Streamlit UI ===
st.set_page_config(page_title="Azure Voice Assistant", page_icon="🎙️")
st.title("🎙️ Azərbaycan Dilli Səsli Köməkçi (Canlı cavab və səsli oxu)")

user_input = st.text_input("Sualını yaz:")

if st.button("Danış!"):
    if not user_input.strip():
        st.warning("Zəhmət olmasa, sualı yaz.")
    else:
        st.info("💭 GPT yazır və eyni anda danışacaq...")
        st_placeholder = st.empty()
        full_answer = ""
        current_sentence = ""

        # GPT streaming cavabı
        with st.spinner("Cavab hazırlanır..."):
            stream = client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "Sən Azərbaycan dilində, təbii, aydın və mehriban tonda danışan asistentsən."},
                    {"role": "user", "content": user_input},
                ],
                stream=True
            )

            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

            for chunk in stream:
                # Boş və ya bitmə mesajlarını keç
                if not chunk.choices or not hasattr(chunk.choices[0], "delta"):
                    continue
                delta = chunk.choices[0].delta
                if "content" not in delta:
                    continue

                token = delta["content"]
                full_answer += token
                current_sentence += token
                st_placeholder.markdown(f"💬 **{full_answer}**")

                # Cümlə bitəndə səsi oynat
                if any(p in token for p in [".", "!", "?"]):
                    result = synthesizer.speak_text_async(current_sentence.strip()).get()
                    audio_data = result.audio_data
                    audio_base64 = base64.b64encode(audio_data).decode()
                    audio_html = f"""
                        <audio autoplay>
                            <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                        </audio>
                    """
                    st.markdown(audio_html, unsafe_allow_html=True)
                    current_sentence = ""
                    time.sleep(0.05)

            # Son cümlə qalıbsa
            if current_sentence.strip():
                result = synthesizer.speak_text_async(current_sentence.strip()).get()
                audio_data = result.audio_data
                audio_base64 = base64.b64encode(audio_data).decode()
                audio_html = f"""
                    <audio autoplay>
                        <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                    </audio>
                """
                st.markdown(audio_html, unsafe_allow_html=True)

        st.success("✅ Cavab tamlandı.")

