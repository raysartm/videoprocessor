import streamlit as st
import requests

# Replace with your AssemblyAI API key
assemblyai_api_key = "78436d2aae7c4b26aa4d60f19cb28e05"

def upload_video(video_file):
  """Uploads video file directly to AssemblyAI for transcription"""
  url = "https://api.assemblyai.com/v2/upload"
  headers = {"Authorization": f"Bearer {assemblyai_api_key}"}
  files = {"video": video_file.read()}  # Read the video content
  response = requests.post(url, headers=headers, files=files)
  if response.status_code == 200:
    return response.json()["upload_url"]
  else:
    st.error(f"Error uploading video: {response.text}")
    return None


def start_transcription(upload_url):
  """Starts transcription job on AssemblyAI"""
  url = "https://api.assemblyai.com/v2/transcript"
  headers = {"Authorization": f"Bearer {assemblyai_api_key}"}
  data = {"audio_url": upload_url}
  response = requests.post(url, headers=headers, json=data)
  if response.status_code == 201:
    return response.json()["id"]
  else:
    st.error(f"Error starting transcription: {response.text}")
    return None

def get_transcription(transcript_id):
  """Polls AssemblyAI for completed transcription and returns text"""
  url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
  headers = {"Authorization": f"Bearer {assemblyai_api_key}"}
  while True:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
      data = response.json()
      if data["status"] == "completed":
        return data["text"]
      else:
        st.info("Transcription in progress...")
    else:
      st.error(f"Error getting transcription: {response.text}")
    # Adjust polling interval based on your needs (seconds)
    time.sleep(5)

st.title("Video Audio Transcription with AssemblyAI (No ffmpeg)")

uploaded_file = st.file_uploader("Choose a video file (Ensure AssemblyAI supports format)")

if uploaded_file is not None:
  upload_url = upload_video(uploaded_file)
  if upload_url:
    transcript_id = start_transcription(upload_url)
    if transcript_id:
      transcription = get_transcription(transcript_id)
      if transcription:
        st.success("Transcription completed!")
        st.write(transcription)
      else:
        st.error("Error retrieving transcription")
  else:
    st.warning("AssemblyAI might not support the uploaded video format. Check their documentation.")
