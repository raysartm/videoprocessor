import streamlit as st

# Define the CSS for the gradient background
page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #00FFFF, #008080);
    background-attachment: fixed;
}
</style>
'''

# Apply the CSS to the Streamlit app
st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("Video Processor App")
st.write("""
Welcome to VideoPro! 
Here's an app to perform your various video processing needs at one place.

You can choose from any of the following functionalities:
""")

st.markdown("### 1. Object Detection")
st.write("Detect and label objects within your video content automatically, providing insights on what appears in each frame.")

st.markdown("### 2. Video Summarization")
st.write("Generate a concise summary of your video, highlighting the most important scenes and moments.")

st.markdown("### 3. Automatic Number Plate Detection")
st.write("Identify and extract vehicle number plates from videos, useful for security and traffic monitoring.")

st.markdown("### 4. Transcribe Video ")
st.write("Convert the audio from your video into text for at the click of a button.")

st.markdown("### 5. Change Video Speed")
st.write("Adjust the playback speed of your video to either slow down or speed up the content as needed.")
