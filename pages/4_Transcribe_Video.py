import os
import streamlit as st
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import subprocess

# Function to extract audio from video
def extract_audio(video_file, audio_file):
    command = f"ffmpeg -i {video_file} -ab 160k -ar 44100 -vn {audio_file}"
    subprocess.call(command, shell=True)

# Function to setup STT service
def setup_stt_service(apikey, url):
    authenticator = IAMAuthenticator(apikey)
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url(url)
    return stt

# Function to transcribe audio
def transcribe_audio(audio_file, stt_service):
    with open(audio_file, 'rb') as f:
        res = stt_service.recognize(audio=f, content_type='audio/wav', model='en-AU_NarrowbandModel', continuous=True).get_result()
    return res

# Function to process results and output text
def process_results(results):
    text = [result['alternatives'][0]['transcript'].rstrip() + '.\n' for result in results['results']]
    text = [para[0].title() + para[1:] for para in text]
    transcript = ''.join(text)
    return transcript

# Streamlit app
def main():
    st.set_page_config(page_title="Video Transcription")

    st.title("Video Transcription")

    uploaded_file = st.file_uploader("Upload a video file...", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_file is not None:
        try:
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            video_path = os.path.join(temp_dir, "video.mp4")
            uploaded_file.seek(0)
            with open(video_path, "wb") as f:
                f.write(uploaded_file.read())

            audio_path = os.path.join(temp_dir, "audio.wav")
            extract_audio(video_path, audio_path)

            stt_apikey = st.text_input("Enter your IBM Watson Speech to Text API key:")
            stt_url = st.text_input("Enter the service URL:")
            stt_service = setup_stt_service(stt_apikey, stt_url)

            if st.button("Transcribe"):
                results = transcribe_audio(audio_path, stt_service)
                transcript = process_results(results)

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
