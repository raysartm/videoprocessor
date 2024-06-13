import streamlit as st
import moviepy.editor as mp
import requests
import os

# Function to extract audio and get transcript using AssemblyAI
def extract_transcript(video_file):
    # Load video file
    video = mp.VideoFileClip(video_file)

    # Extract audio
    audio_clip = video.audio

    # Export audio clip to WAV format (AssemblyAI supports WAV)
    audio_file = "temp_audio.wav"
    audio_clip.write_audiofile(audio_file)

    # Upload audio to AssemblyAI for transcription
    url = "https://api.assemblyai.com/v2/transcript"
    headers = {
        "authorization": "YOUR_ASSEMBLYAI_API_KEY",
        "content-type": "application/json"
    }
    files = {'file': open(audio_file, 'rb')}
    response = requests.post(url, headers=headers, files=files)

    # Check if request was successful
    if response.status_code == 201:
        transcript_id = response.json()['id']
        transcript_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
        
        # Poll AssemblyAI until transcription is complete
        while True:
            transcript_response = requests.get(transcript_url, headers=headers)
            transcript_status = transcript_response.json()['status']
            if transcript_status == "completed":
                transcript_text = transcript_response.json()['text']
                os.remove(audio_file)  # Remove temporary audio file
                return transcript_text
            elif transcript_status == "failed":
                st.error("Transcription failed.")
                return None
    else:
        st.error(f"Transcription request failed with status code {response.status_code}.")
        return None

# Streamlit app
def main():
    st.title('Video Transcription')

    # Upload video file
    video_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"])

    if video_file is not None:
        # Display video
        st.video(video_file)

        # Process video and extract transcript
        transcript = extract_transcript(video_file)

        if transcript:
            # Display transcript
            st.header('Transcript')
            st.text_area('Transcript', transcript, height=200)

            # Download button for transcript
            st.download_button(
                label="Download Transcript",
                data=transcript.encode('utf-8'),
                file_name='transcript.txt',
                mime='text/plain'
            )

if __name__ == "__main__":
    main()
