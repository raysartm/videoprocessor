import streamlit as st
import cv2
import numpy as np
import tempfile
import os

# Load the pre-trained MobileNet SSD model
net = cv2.dnn.readNetFromCaffe('pages/MobileNetSSD_deploy.prototxt.txt' , 'pages/MobileNetSSD_deploy.caffemodel')


# List of class labels
classes = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# Function to perform object detection on a frame
def detect_objects(frame):
    # Resize input frame to a fixed size (300x300) and normalize it
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
    
    # Set the input to the network
    net.setInput(blob)
    
    # Forward pass through the network to get detections
    detections = net.forward()
    
    # Loop over the detections
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        
        # If confidence is above a certain threshold, draw bounding box
        if confidence > 0.5:
            class_id = int(detections[0, 0, i, 1])
            label = classes[class_id]
            box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
            (startX, startY, endX, endY) = box.astype("int")
            
            # Draw the bounding box and label on the frame
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(frame, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    return frame

# Streamlit app
st.title("Object Detection using MobileNet SSD")
st.write("Upload a video file to perform object detection.")

# Upload video file
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "avi", "mkv"])

if uploaded_file is not None:
    # Save the uploaded video to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
        temp_video_file.write(uploaded_file.read())
        temp_video_path = temp_video_file.name

    # Open video capture
    cap = cv2.VideoCapture(temp_video_path)

    # Check if the video file opened successfully
    if not cap.isOpened():
        st.error("Error: Could not open video file.")
    else:
        # Get the original width and height of the video
        original_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Define the target width and height for resizing
        target_width = 1600  # Adjust according to your preference
        target_height = int(original_height * (target_width / original_width))

        # Define the codec and create a VideoWriter object to save the processed video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        output_path = "processed_video.mp4"
        out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (target_width, target_height))

        # Display the video
        stframe = st.empty()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Resize the frame to the target width and height
            frame = cv2.resize(frame, (target_width, target_height))

            # Perform object detection on the current frame
            output_frame = detect_objects(frame)

            # Convert the frame to RGB format
            output_frame = cv2.cvtColor(output_frame, cv2.COLOR_BGR2RGB)

            # Write the frame to the output video file
            out.write(cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR))

            # Display the frame in Streamlit
            stframe.image(output_frame, channels="RGB")

        # Release video capture and writer
        cap.release()
        out.release()

        # Provide a download button for the processed video
        with open(output_path, "rb") as file:
            btn = st.download_button(
                label="Download Processed Video",
                data=file,
                file_name="processed_video.mp4",
                mime="video/mp4"
            )

    st.success("Video processing complete.")
else:
    st.info("Please upload a video file.")
