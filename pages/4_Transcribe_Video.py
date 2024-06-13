import streamlit as st
import os
import moviepy.editor as mp
import speech_recognition as sr
from io import BytesIO

def video_to_text(video_file):
    # Load the uploaded video file
    video_bytes = video_file.read()

    # Save the video file temporarily
    temp_video_path = "temp_video.mp4"
    with open(temp_video_path, "wb") as f:
        f.write(video_bytes)

    # Load the video file using moviepy
    video = mp.VideoFileClip(temp_video_path)

    # Extract audio from the video
    audio = video.audio

    # Save the extracted audio to a file (optional)
    audio_file = "extracted_audio.wav"
    audio.write_audiofile(audio_file)

    # Perform speech recognition on the extracted audio
    recognizer = sr.Recognizer()

    # Load audio file
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

    # Recognize speech using Google Speech Recognition
    try:
        transcript = recognizer.recognize_google(audio_data)
        return transcript
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Error: {e}"
    finally:
        # Clean up: delete temporary video file
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

def main():
    st.title("Video Transcription App")
    st.markdown("Upload a video file")

    # File uploader for video
    uploaded_file = st.file_uploader("Drag and drop file here",
                                     type=['mp4', 'mov', 'mpeg4'],
                                     accept_multiple_files=False)

    if uploaded_file is not None:
        # Display uploaded video details
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.write(file_details)

        # Perform transcription when user clicks the button
        if st.button("Transcribe"):
            transcript = video_to_text(uploaded_file)
            st.subheader("Transcript:")
            st.write(transcript)

if __name__ == "__main__":
    main()
