import streamlit as st
import moviepy.editor as mp
import speech_recognition as sr

# Function to transcribe video using SpeechRecognition library
def transcribe_video(video_file):
    st.write("Transcribing video...")

    # Load the video file
    clip = mp.VideoFileClip(video_file)
    audio = clip.audio

    # Save audio as a temporary file
    audio_file = "temp.wav"
    audio.write_audiofile(audio_file)

    # Use SpeechRecognition library to recognize speech
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
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
    st.title("Video Transcription")

    # Upload video file
    video_file = st.file_uploader("Upload a video file", type=['mp4', 'avi'])

    if video_file is not None:
        st.video(video_file)
        st.write("Uploaded video file:", video_file.name)

        if st.button("Transcribe Video"):
            transcribe_video(video_file)

if __name__ == "__main__":
    main()
