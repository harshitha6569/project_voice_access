import streamlit as st
from groq import Groq
import tempfile
from gtts import gTTS
import io

# Page config
st.set_page_config(page_title="Helper Voice AI", layout="wide")

st.title("🤖 Helper – Voice Assistant")
st.write("🎤 Click the mic and ask your question")

# Check API key
if "GROQ_API_KEY" not in st.secrets:
    st.error("❌ GROQ API Key not found. Add it in Streamlit Secrets.")
    st.stop()

# Initialize Groq client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Store conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Reset button
if st.button("🔄 Reset Conversation"):
    st.session_state.messages = []

# 🎤 Voice input
audio_file = st.audio_input("Speak now")

if audio_file is not None:
    try:
        # Save temp audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.read())
            file_path = tmp.name

        # 🎧 Speech-to-Text using Groq Whisper
        with open(file_path, "rb") as f:
            transcription = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3"
            )

        query = transcription.text.strip()

        if not query:
            st.warning("⚠️ Could not understand audio. Try again.")
            st.stop()

        st.subheader("🗣️ You asked:")
        st.write(query)

        # Store user message
        st.session_state.messages.append({"role": "user", "content": query})

        # 🤖 LLM response
        with st.spinner("Helper is thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages
            )

        answer = response.choices[0].message.content

        # Store assistant reply
        st.session_state.messages.append({"role": "assistant", "content": answer})

        # 💡 Show text output
        st.subheader("💡 Answer:")
        st.write(answer)

        # 🔊 Convert text → voice
        tts = gTTS(answer)

        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        st.subheader("🔊 Voice Answer:")
        st.audio(audio_buffer)

        # Download option
        st.download_button(
            label="⬇️ Download Voice",
            data=audio_buffer,
            file_name="helper_voice.mp3",
            mime="audio/mp3"
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("Click the microphone above and ask your question")
