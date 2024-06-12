import os
import streamlit as st
import cv2
import tempfile

st.set_page_config(page_title="Speed Control Video")

st.title("Speed Control Video")

uploaded_file = st.file_uploader("Upload a video file...", type=["mp4", "mov", "avi", "mkv"])

if uploaded_file is not None:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        cap = cv2.VideoCapture(temp_file_path)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        fps = cap.get(cv2.CAP_PROP_FPS)

        speed_factor = st.slider("Select speed factor", 0.1, 10.0, 1.0, 0.1)

        output_path = temp_file_path.replace(".mp4", f"_speed_{speed_factor:.1f}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output = cv2.VideoWriter(output_path, fourcc, fps * speed_factor, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            output.write(frame)

        cap.release()
        output.release()

        st.markdown("### Download Speed Adjusted Video")
        with open(output_path, "rb") as file:
            st.download_button("Download", file.read(), file_name=f"speed_adjusted_video_{speed_factor:.1f}.mp4", mime="video/mp4")

        os.remove(output_path)  # Delete temporary file
    except Exception as e:
        st.error(f"An error occurred: {e}")
