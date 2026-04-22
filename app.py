import streamlit as st
from groq import Groq
import speech_recognition as sr
import tempfile
from gtts import gTTS

# Page config
st.set_page_config(page_title="Helper Voice AI", layout="wide")

st.title("🤖 Helper – Voice Assistant")
st.write("🎤 Click the mic and ask your question")

# Check API key
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ API Key not found. Add it in Streamlit Secrets.")
    st.stop()

# Initialize
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
recognizer = sr.Recognizer()

# 🎤 Built-in mic input (Streamlit)
audio_file = st.audio_input("Speak now")

if audio_file is not None:
    try:
        # Save audio temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.read())
            file_path = tmp.name

        # Convert speech to text
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)

        query = recognizer.recognize_google(audio)

        st.subheader("🗣️ You asked:")
        st.write(query)

        # Generate AI response
        with st.spinner("Helper is thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": query}]
            )

            answer = response.choices[0].message.content

        st.subheader("💡 Answer:")
        st.write(answer)

        # Convert answer to voice
        tts = gTTS(answer)
        output_audio = "response.mp3"
        tts.save(output_audio)

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
