import streamlit as st
import speech_recognition as sr

def transcribe_audio(uploaded_file, max_bytes=10 * 1024 * 1024):
  """Attempts audio transcription with user confirmation for spoken content,
  limiting memory usage by reading a maximum number of bytes."""
  recognizer = sr.Recognizer()
  confirmation_message = st.checkbox("This video appears to be a static image or doesn't contain spoken content. Continue with transcription?")
  if not confirmation_message:
    return None
  try:
    # Read a limited number of bytes from the video
    video_bytes = uploaded_file.read(max_bytes)
    # Open the video content in memory using AudioFile
    with sr.AudioFile(sr.AudioData(video_bytes)) as source:
      audio_data = recognizer.record(source)
    text = recognizer.recognize_google(audio_data)
    return text
  except sr.UnknownValueError:
    return "Speech Recognition Could not understand audio"
  except sr.RequestError as e:
    return f"Could not request results from Google Speech Recognition service; {e}"
  except Exception as e:  # Catch potential general exceptions
    return f"An error occurred during transcription: {e}"

st.title("Video Audio Transcription (No External Dependencies)")

uploaded_file = st.file_uploader("Choose a video file")

if uploaded_file is not None:
  transcription = transcribe_audio(uploaded_file)
  if transcription:
    st.success("Transcription completed!")
    st.write(transcription)
  else:
    if not transcription:
      st.info("User opted not to transcribe.")
    else:
      st.error(transcription)
