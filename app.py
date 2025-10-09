import streamlit as st
from openai import OpenAI
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import soundfile as sf
from io import BytesIO

# === Secrets ===
AZURE_OPENAI_KEY = st.secrets["AZURE_OPENAI_KEY"]
AZURE_OPENAI_ENDPOINT = st.secrets["AZURE_OPENAI_ENDPOINT"]
AZURE_OPENAI_DEPLOYMENT = st.secrets["AZURE_OPENAI_DEPLOYMENT"]

# === Azure client ===
client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_KEY,
    default_headers={"api-key": AZURE_OPENAI_KEY}
)

# === Load Hugging Face TTS model (Azerbaijani) ===
@st.cache_resource
def load_tts_model():
    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-aze")
    model = AutoModelForSeq2SeqLM.from_pretrained("facebook/mms-tts-aze")
    return tokenizer, model

tokenizer, model = load_tts_model()

# === Streamlit UI ===
st.set_page_config(page_title="Azure + HuggingFace TTS", page_icon="🎙️")
st.title("🎙️ Azərbaycan Dilli Səsli Köməkçi (Azure OpenAI + HuggingFace TTS)")

user_input = st.text_input("Sualını yaz:")

if st.button("Danış!"):
    if not user_input.strip():
        st.warning("Zəhmət olmasa, sualı yaz.")
    else:
        # 1️⃣ Azure LLM cavabı
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

        # 2️⃣ Hugging Face TTS (Azerbaijani)
        with st.spinner("Səsləndirilir..."):
            inputs = tokenizer(answer, return_tensors="pt")
            with torch.no_grad():
                speech = model.generate(**inputs)
            speech_array = speech[0].cpu().numpy()

            # Save to buffer as WAV and play
            wav_bytes = BytesIO()
            sf.write(wav_bytes, speech_array, samplerate=16000, format="WAV")
            wav_bytes.seek(0)
            st.audio(wav_bytes, format="audio/wav")
