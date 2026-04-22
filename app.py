import streamlit as st
from groq import Groq
import speech_recognition as sr
import tempfile
from gtts import gTTS
from audiorecorder import audiorecorder

# Page setup
st.set_page_config(page_title="Helper Voice AI", layout="wide")

st.title("🤖 Helper – Voice Assistant")
st.write("🎤 Click and speak your question")

# API
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
recognizer = sr.Recognizer()

# 🎤 Voice Recorder (THIS IS WHAT YOU NEED)
audio = audiorecorder("🎤 Click to record", "⏹️ Recording... Click to stop")

if len(audio) > 0:
    st.success("✅ Voice recorded")

    # Save audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio.export(tmp.name, format="wav")
        file_path = tmp.name

    try:
        # Convert speech → text
        with sr.AudioFile(file_path) as source:
            recorded_audio = recognizer.record(source)

        query = recognizer.recognize_google(recorded_audio)

        st.subheader("🗣️ You asked:")
        st.write(query)

        # AI Response
        with st.spinner("Helper is thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": query}]
            )

            answer = response.choices[0].message.content

        st.subheader("💡 Answer:")
        st.write(answer)

        # Convert to voice
        tts = gTTS(answer)
        tts.save("response.mp3")

        st.subheader("🔊 Voice Answer")
        st.audio("response.mp3")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Click the button and speak your question")
