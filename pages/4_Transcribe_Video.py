import os
import requests
import streamlit as st
from moviepy.editor import VideoFileClip
import tempfile

# Function to extract audio from video using MoviePy
def extract_audio(video_file):
    video_clip = VideoFileClip(video_file)
    audio_clip = video_clip.audio

    # Create temporary directory and audio path relative to it
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = os.path.join(temp_dir, "audio.wav")
        audio_clip.write_audiofile(audio_path, codec='pcm_s16le')

    audio_clip.close()
    video_clip.close()
    return audio_path  # Return the audio file path

# Function to transcribe audio using AssemblyAI
def transcribe_audio(api_key, audio_file):
    url = "https://api.assemblyai.com/v2/transcript"
    headers = {
        "authorization": api_key,
        "content-type": "application/json"
    }
    data = {
        "audio_url": audio_file
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    transcript_id = response.json()["id"]

    # Wait for transcription to complete
    while True:
        response = requests.get(f"{url}/{transcript_id}", headers=headers)
        status = response.json()["status"]
        if status == "completed":
            break
        time.sleep(2)

    return response.json()["text"]

# Streamlit app
def main():
    st.set_page_config(page_title="Video Transcription")
    st.title("Video Transcription")

    uploaded_file = st.file_uploader("Upload a video file...", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_file is not None:
        try:
            # Use temporary directory for audio file
            audio_path = extract_audio(uploaded_file)

            api_key = st.secrets["ASSEMBLYAI_API_KEY"]  # Retrieve AssemblyAI API key from Streamlit secrets

            if st.button("Transcribe"):
                transcript = transcribe_audio(api_key, audio_path)

                st.subheader("Transcript:")
                st.write(transcript)

                output_path = os.path.join(tempfile.gettempdir(), "transcript.txt")  # Use system temp dir
                with open(output_path, "w") as out:
                    out.write(transcript)

                st.markdown("### Download Transcript")
                with open(output_path, "rb") as file:
                    st.download_button("Download", file.read(), file_name="transcript.txt", mime="text/plain")

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
