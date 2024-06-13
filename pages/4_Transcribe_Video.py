import os
import requests
import streamlit as st
import subprocess
import time

# Function to extract audio from video
def extract_audio(video_file, audio_file):
    command = f"ffmpeg -i {video_file} -ab 160k -ar 44100 -vn {audio_file}"
    subprocess.call(command, shell=True)

# Function to transcribe audio using AssemblyAI
def transcribe_audio(api_key, audio_file):
    headers = {
        'authorization': api_key,
        'content-type': 'application/json'
    }
    
    # Upload audio file
    with open(audio_file, 'rb') as f:
        response = requests.post('https://api.assemblyai.com/v2/upload', headers=headers, files={'file': f})
        upload_url = response.json()['upload_url']
    
    # Transcription request
    transcription_request = {
        'audio_url': upload_url
    }
    response = requests.post('https://api.assemblyai.com/v2/transcript', json=transcription_request, headers=headers)
    transcript_id = response.json()['id']
    
    # Polling for the transcription result
    while True:
        response = requests.get(f'https://api.assemblyai.com/v2/transcript/{transcript_id}', headers=headers)
        result = response.json()
        if result['status'] == 'completed':
            return result['text']
        elif result['status'] == 'failed':
            raise Exception('Transcription failed')
        else:
            st.write("Transcription in progress, please wait...")
            time.sleep(5)

# Streamlit app
def main():
    st.set_page_config(page_title="Video Transcription")

    st.title("Video Transcription")

    uploaded_file = st.file_uploader("Upload a video file...", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_file is not None:
        try:
            temp_dir = "temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            video_path = os.path.join(temp_dir, "video.mp4")
            uploaded_file.seek(0)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.read())

            audio_path = os.path.join(temp_dir, "audio.wav")
            extract_audio(video_path, audio_path)

            api_key = "78436d2aae7c4b26aa4d60f19cb28e05"  # Replace with your AssemblyAI API key
            
            if st.button("Transcribe"):
                transcript = transcribe_audio(api_key, audio_path)

                st.subheader("Transcript:")
                st.write(transcript)

                output_path = os.path.join(temp_dir, "transcript.txt")
                with open(output_path, "w") as out:
                    out.write(transcript)

                st.markdown("### Download Transcript")
                with open(output_path, "rb") as file:
                    st.download_button("Download", file.read(), file_name="transcript.txt", mime="text/plain")

        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            # Clean up temp directory
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, file)
                    os.remove(file_path)
                os.rmdir(temp_dir)

if __name__ == "__main__":
    main()
