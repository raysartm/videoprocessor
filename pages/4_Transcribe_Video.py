import streamlit as st
import speech_recognition as sr

def transcribe_audio(video_file):
  """Attempts audio transcription with user confirmation for spoken content"""
  recognizer = sr.Recognizer()
  confirmation_message = st.checkbox("This video appears to be a static image or doesn't contain spoken content. Continue with transcription?")
  if not confirmation_message:
    return None
  try:
    with sr.AudioFile(video_file.name) as source:
      audio_data = recognizer.record(source)
    text = recognizer.recognize_google(audio_data)
    return text
  except sr.UnknownValueError:
    return "Speech Recognition Could not understand audio"
  except sr.RequestError as e:
    return f"Could not request results from Google Speech Recognition service; {e}"

st.title("Video Audio Transcription (No FFmpeg or External API)")

uploaded_file = st.file_uploader("Choose a video file")

if uploaded_file is not None:
  transcription = transcribe_audio(uploaded_file.name)
  if transcription:
    st.success("Transcription completed!")
    st.write(transcription)
  else:
    if not transcription:
      st.info("User opted not to transcribe.")
    else:
      st.error(transcription)
