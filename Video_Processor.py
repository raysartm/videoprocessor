import streamlit as st
import base64

# Function to set the background image
def set_bg_image(image_file):
    with open(image_file, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    page_bg_img = f'''
    <style>
    [data-testid="stAppViewContainer"] {{
        background: url("data:image/png;base64,{b64}") no-repeat center center fixed;
        background-size: cover;
    }}
    h1, h2, h3, h4, h5, h6, p {{
        color: black;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Set the background image
set_bg_image("background.png")

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

st.markdown("### 4. Transcribe Video")
st.write("Convert the audio from your video into text with a click of a button.")

st.markdown("### 5. Change Video Speed")
st.write("Adjust the playback speed of your video to either slow down or speed up the content as needed.")
