import streamlit as st
import speech_recognition as sr
from moviepy.editor import VideoFileClip  # Import moviepy for basic video analysis

def transcribe_audio(uploaded_file, max_bytes=10 * 1024 * 1024):
  """Attempts audio transcription with user confirmation for spoken content,
  limiting memory usage by reading a maximum number of bytes and extracting
  sample rate and sample width from the video."""
  recognizer = sr.Recognizer()
  confirmation_message = st.checkbox("This video appears to be a static image or doesn't contain spoken content. Continue with transcription?")
  if not confirmation_message:
    return None
  try:
    # Extract a small clip (first frame) for audio format information
    clip = VideoFileClip(uploaded_file.name).subclip(0, 0.01)  # Extract first frame
    sample_rate, sample_width = clip.audio.read_audio_samples(clip.audio.duration)[0]
    clip.close()  # Close the clip to release resources

    # Read a limited number of bytes from the video
    video_bytes = uploaded_file.read(max_bytes)

    # Create AudioData object with extracted format information
    audio_data = sr.AudioData(video_bytes, sample_rate=sample_rate, sample_width=sample_width)
    
    with sr.AudioFile(audio_data) as source:
      audio_data = recognizer.record(source)
    text = recognizer.recognize_google(audio_data)
    return text
  except sr.UnknownValueError:
    return "Speech Recognition Could not understand audio"
  except sr.RequestError as e:
    return f"Could not request results from Google Speech Recognition service; {e}"
  except Exception as e:  # Catch potential general exceptions
    return f"An error occurred during transcription: {e}"
