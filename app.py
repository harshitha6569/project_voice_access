import streamlit as st
from groq import Groq
import speech_recognition as sr
import tempfile
from gtts import gTTS

st.set_page_config(page_title="Helper Voice AI", layout="wide")

st.title("🤖 Helper – Voice Assistant")
st.write("🎤 Ask your question by voice")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
recognizer = sr.Recognizer()

# 🎤 BUILT-IN VOICE INPUT (NO ERRORS)
audio_file = st.audio_input("Speak now")

if audio_file is not None:
    try:
        # Save audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.read())
            file_path = tmp.name

        # Convert speech → text
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)

        query = recognizer.recognize_google(audio)
        st.success(f"🗣️ You asked: {query}")

        # AI response
        with st.spinner("Helper is thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": query}]
            )

            answer = response.choices[0].message.content
            st.subheader("💡 Answer")
            st.write(answer)

        # Text → voice
        tts = gTTS(answer)
        tts.save("response.mp3")

        st.subheader("🔊 Voice Answer")
        st.audio("response.mp3")

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Click the mic and ask your question")
