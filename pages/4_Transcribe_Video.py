import streamlit as st
import speech_recognition as sr
import subprocess

def extract_frames(video_file, num_frames=10):
  """Extracts a small number of video frames for basic motion detection"""
  # Adjust num_frames based on your needs (consider performance impact)
  command = f"ffmpeg -i {video_file} -vf select=eq(scene\,{num_frames-1}) -vsync 0 -f image2 out%d.jpg"
  try:
    subprocess.run(command, shell=True, check=True)
    return True
  except subprocess.CalledProcessError:
    st.error("Error extracting video frames (consider installing ffmpeg)")
    return False

def check_video_content(video_file):
  """Basic video content check using frame extraction (not foolproof)"""
  success = extract_frames(video_file)
  if success:
    # You can implement basic image processing on extracted frames
    # to check for presence of movement (e.g., using OpenCV)
    # This is a simplified approach and might not be reliable
    # Consider using a library specifically designed for video analysis
    # if you need more robust content detection.
    st.info("Video appears to contain moving content (basic check).")
  return success

def transcribe_audio(video_file):
  """Attempts audio transcription assuming video contains spoken content"""
  recognizer = sr.Recognizer()
  # This approach assumes the video has spoken content.
  # It might not work well for videos without speech. 
  if not check_video_content(video_file):
    st.warning("Video might not contain spoken content. Transcription might be inaccurate.")
  try:
    # Consider using a library like moviepy to extract the audio track
    # if the video might not have spoken content throughout.
    with sr.AudioFile(video_file) as source:
      audio_data = recognizer.record(source)
    text = recognizer.recognize_google(audio_data)
    return text
  except sr.UnknownValueError:
    return "Speech Recognition Could not understand audio"
  except sr.RequestError as e:
    return f"Could not request results from Google Speech Recognition service; {e}"

st.title("Video Audio Transcription (No FFmpeg or External API)")

uploaded_file = st.file_uploader("Choose a video file (assumes spoken content)")

if uploaded_file is not None:
  transcription = transcribe_audio(uploaded_file.name)
  if transcription:
    st.success("Transcription completed!")
    st.write(transcription)
  else:
    st.error(transcription)
