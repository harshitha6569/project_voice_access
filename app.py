import streamlit as st
from groq import Groq
import tempfile
from gtts import gTTS
from openai import OpenAI   # ✅ added

# Page config
st.set_page_config(page_title="Helper Voice AI", layout="wide")

st.title("🤖 Helper – Voice Assistant")
st.write("🎤 Click the mic and ask your question")

# Check API keys
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ API Key not found.")
    st.stop()

if "OPENAI_API_KEY" not in st.secrets:   # ✅ added
    st.error("❌ OPENAI API Key not found.")
    st.stop()

# Initialize
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
whisper_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])  # ✅ added

# 🎤 Mic input
audio_file = st.audio_input("Speak now")

if audio_file is not None:
    try:
        # Save audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.read())
            file_path = tmp.name

        # 🔥 REPLACED THIS PART (Speech → Text using Whisper)
        with open(file_path, "rb") as audio:
            transcript = whisper_client.audio.transcriptions.create(
                model="gpt-4o-mini-transcribe",
                file=audio
            )

        query = transcript.text

        st.subheader("🗣️ You asked:")
        st.write(query)

        # Generate AI response
        with st.spinner("Helper is thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Understand technical words correctly and give clear answers."
                    },
                    {"role": "user", "content": query}
                ]
            )

            answer = response.choices[0].message.content

        st.subheader("💡 Answer:")
        st.write(answer)

        # Convert answer to voice (safe temp file)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            tts = gTTS(answer)
            tts.save(tmp_audio.name)
            output_audio = tmp_audio.name

        # Play audio
        st.subheader("🔊 Voice Answer:")
        st.audio(output_audio)

        # Download option
        with open(output_audio, "rb") as f:
            st.download_button(
                label="⬇️ Download Voice",
                data=f,
                file_name="helper_voice.mp3",
                mime="audio/mp3"
            )

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Click the microphone above and ask your question")
