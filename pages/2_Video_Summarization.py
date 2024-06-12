import os
import cv2
import numpy as np
import gc
from moviepy.editor import VideoFileClip, concatenate_videoclips
import streamlit as st

# Load the pre-trained MobileNet SSD model
net = cv2.dnn.readNetFromCaffe('pages/MobileNetSSD_deploy.prototxt.txt' , 'pages/MobileNetSSD_deploy.caffemodel')

# List of class labels
classes = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# Function to perform object detection on a frame
def detect_objects(frame, confidence_threshold=0.3):  # Lowered threshold to 0.3
    try:
        # Resize input frame to a fixed size (300x300) and normalize it
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        # Set the input to the network
        net.setInput(blob)
        # Forward pass through the network to get detections
        detections = net.forward()
        detected_objects = []
        # Loop over the detections
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            # If confidence is above the threshold, consider it a valid detection
            if confidence > confidence_threshold:
                class_id = int(detections[0, 0, i, 1])
                label = classes[class_id]
                box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                detected_objects.append((label, box.astype("int")))
        return detected_objects
    except Exception as e:
        print(f"Error in detect_objects: {e}")
        return []

# Function to extract frames from the video in batches
def extract_and_process_frames(video_path, fps=2, batch_size=10, downscale_factor=0.5):  # Adjusted batch_size and downscale_factor
    try:
        cap = cv2.VideoCapture(video_path)
        key_frames = []
        count = 0
        frames = []
        last_seen_objects = {}  # Track last seen objects with bounding boxes

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Downscale the frame
            frame = cv2.resize(frame, (int(frame.shape[1] * downscale_factor), int(frame.shape[0] * downscale_factor)))

            if count % fps == 0:
                frames.append((count, frame))
                if len(frames) >= batch_size:  # Process in smaller batches
                    key_frames += get_key_frames(frames, last_seen_objects)
                    frames = []
                    gc.collect()  # Force garbage collection to free up memory
            count += 1

        if frames:  # Process any remaining frames
            key_frames += get_key_frames(frames, last_seen_objects)

        cap.release()
        return key_frames
    except Exception as e:
        print(f"Error in extract_and_process_frames: {e}")
        return []

# Function to get key frames based on object detection
def get_key_frames(frames, last_seen_objects):
    key_frames = []
    for i, frame in frames:
        detected_objects = detect_objects(frame)
        new_objects = []
        for label, box in detected_objects:
            if label not in last_seen_objects or not np.array_equal(box, last_seen_objects[label]):
                new_objects.append((label, box))
                last_seen_objects[label] = box
        if new_objects:
            key_frames.append((i, frame))
            print(f"Detected new objects at frame {i}: {new_objects}")  # Debug information
    return key_frames

# Function to create summary video from key frames
def create_summary_video(key_frames, video_path, fps=2):
    try:
        if not key_frames:
            print("No key frames detected.")
            return None

        # Sort key frames by their indices
        key_frames.sort(key=lambda x: x[0])

        video = VideoFileClip(video_path)
        video_duration = video.duration
        key_clips = []
        for i, _ in key_frames:
            start_time = i / fps
            end_time = min((i + 1) / fps, video_duration)
            if start_time < video_duration:
                key_clips.append(video.subclip(start_time, end_time))

        summary_video = concatenate_videoclips(key_clips)
        return summary_video
    except Exception as e:
        print(f"Error in create_summary_video: {e}")
        return None

# Streamlit app
def main():
    st.title("Video Object Detection and Summarization")

    uploaded_file = st.file_uploader("Upload a video file...", type=["mp4", "mov", "avi", "mkv"])

    if uploaded_file is not None:
        try:
            with open("temp_video.mp4", "wb") as f:
                f.write(uploaded_file.read())

            # Extract frames from the video
            st.write("Extracting and processing frames...")
            key_frames = extract_and_process_frames("temp_video.mp4", fps=2, batch_size=10, downscale_factor=0.5)
            st.write(f"Total key frames detected: {len(key_frames)}")

            # Create summary video from key frames
            st.write("Creating summary video...")
            summary_video = create_summary_video(key_frames, "temp_video.mp4")
            if summary_video:
                # Save the summary video
                summary_video.write_videofile("summary_video.mp4", codec='libx264')
                st.write("Summary video created successfully.")
                st.video("summary_video.mp4")
            else:
                st.write("Failed to create summary video.")

        except Exception as e:
            st.error(f"An error occurred: {e}")

        finally:
            # Clean up temp video file
            os.remove("temp_video.mp4")

if __name__ == '__main__':
    main()
