import streamlit as st
from groq import Groq
import speech_recognition as sr
import tempfile
from gtts import gTTS
import os

# Page config
st.set_page_config(page_title="Helper Voice AI", layout="wide")

st.title("🤖 Helper – Voice Assistant with Audio Output")

# API
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
recognizer = sr.Recognizer()

st.write("Upload your voice question and get both text + voice answer")

# Upload audio
uploaded_file = st.file_uploader("🎧 Upload your voice", type=["wav", "mp3"])

if uploaded_file is not None:
    try:
        # Save input audio
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(uploaded_file.read())
            input_path = tmp.name

        # Speech to text
        with sr.AudioFile(input_path) as source:
            audio = recognizer.record(source)

        query = recognizer.recognize_google(audio)
        st.success(f"🗣️ You asked: {query}")

        # Generate AI response
        with st.spinner("Helper is thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Answer clearly: {query}"}]
            )

            answer = response.choices[0].message.content
            st.subheader("💡 Answer (Text)")
            st.write(answer)

        # Convert text → speech
        tts = gTTS(answer)
        
        output_audio_path = "response.mp3"
        tts.save(output_audio_path)

        # Play audio
        st.subheader("🔊 Voice Output")
        audio_file = open(output_audio_path, "rb")
        st.audio(audio_file.read(), format="audio/mp3")

        # Download audio
        st.download_button(
            label="⬇️ Download Voice Answer",
            data=open(output_audio_path, "rb").read(),
            file_name="helper_voice.mp3",
            mime="audio/mp3"
        )

    except Exception as e:
        st.error(f"Error: {e}")

else:
    st.info("Upload a voice file to ask something")
