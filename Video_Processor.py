import streamlit as st

# Define the CSS for the gradient background
page_bg_img = '''
<style>
body {
    background: linear-gradient(to right, #00FFFF, #008080);
    background-attachment: fixed;
}
</style>
'''

# Apply the CSS to the Streamlit app
st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("Video Processor App")
st.write("""
Welcome to the Video Processor App. This app allows you to perform various video processing tasks.
You can choose from the following functionalities:
""")

st.markdown("### 1. Object Detection")
st.write("Detect and label objects within your video content automatically, providing insights on what appears in each frame.")

st.markdown("### 2. Video Summarization")
st.write("Generate a concise summary of your video, highlighting the most important scenes and moments.")

st.markdown("### 3. Automatic Number Plate Detection")
st.write("Identify and extract vehicle number plates from videos, useful for security and traffic monitoring.")

st.markdown("### 4. Transcribe Video using IBM Watson")
st.write("Convert the audio from your video into text using IBM Watson's advanced speech recognition technology.")

st.markdown("### 5. Change Video Speed")
st.write("Adjust the playback speed of your video to either slow down or speed up the content as needed.")
