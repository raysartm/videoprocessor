import streamlit as st

st.title("Video Processor App")
st.write("""
Welcome to the Video Processor App. This app allows you to perform various video processing tasks.
You can choose from the following functionalities:
""")

st.markdown("[Summarization](pages/2_video_sum.py)")
st.markdown("[Transcription](pages/4_transcription.py)")
st.markdown("[Slow Motion](pages/5_slow_motion.py)")