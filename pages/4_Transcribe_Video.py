import streamlit as st
from pydub import AudioSegment
import speech_recognition as sr

# Function to extract audio from video and transcribe it
def transcribe_video(video_file):
    st.write("Transcribing video...")

    # Read video file and extract audio
    video_bytes = video_file.read()
    audio = AudioSegment.from_file(video_bytes, format='mp4').set_channels(1)

    # Export audio as WAV (Streamlit currently only supports WAV playback)
    audio_path = "temp_audio.wav"
    audio.export(audio_path, format="wav")

    # Perform speech recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)

    # Perform speech recognition
    try:
        transcript = recognizer.recognize_google(audio_data)
        st.write("Transcription:")
        st.write(transcript)
    except sr.UnknownValueError:
        st.write("Speech recognition could not understand audio")
    except sr.RequestError as e:
        st.write(f"Could not request results from Speech Recognition service; {e}")

# Streamlit UI
def main():
    st.title("Video Transcription without External APIs")

    # Upload video file
    video_file = st.file_uploader("Upload a video file", type=['mp4', 'avi'])

    if video_file is not None:
        st.video(video_file)
        st.write("Uploaded video file:", video_file.name)

        if st.button("Transcribe Video"):
            transcribe_video(video_file)

if __name__ == "__main__":
    main()
