import streamlit as st
from moviepy.editor import VideoFileClip
import speech_recognition as sr

def extract_audio(video_file):
  """Extracts audio from a video file using moviepy (install moviepy separately)"""
  # You might need to adjust the output filename based on your needs
  audio_filename = "extracted_audio.wav"
  clip = VideoFileClip(video_file.name)
  clip.audio.write_audiofile(audio_filename)
  return audio_filename

def transcribe_audio(audio_filename):
  """Transcribes audio file using SpeechRecognition"""
  recognizer = sr.Recognizer()
  with sr.AudioFile(audio_filename) as source:
    audio_data = recognizer.record(source)
  try:
    text = recognizer.recognize_google(audio_data)
    return text
  except sr.UnknownValueError:
    return "Speech Recognition Could not understand audio"
  except sr.RequestError as e:
    return f"Could not request results from Google Speech Recognition service; {e}"

st.title("Video Audio Transcription (No External API)")

uploaded_file = st.file_uploader("Choose a video file")

if uploaded_file is not None:
  audio_filename = extract_audio(uploaded_file)
  if audio_filename:
    transcription = transcribe_audio(audio_filename)
    if transcription:
      st.success("Transcription completed!")
      st.write(transcription)
    else:
      st.error(transcription)
  else:
    st.error("Error extracting audio")
