import streamlit as st
import pandas as pd
import numpy as np
import cv2
import ast
from scipy.interpolate import interp1d
from ultralytics import YOLO
import sys
sys.path.append("pages/utils")
import easyocr
import util  # Assuming util.py is directly inside the utils folder
from sort import Sort
import os
from tempfile import NamedTemporaryFile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from utils import util
from utils.sort import *

def process_video(video_path, csv_path):
    results = {}
    mot_tracker = Sort()
    coco_model = YOLO('yolov8n')
    license_plate_detector = YOLO('/kaggle/working/yolov8n_license_plate.pt')
    cap = cv2.VideoCapture(video_path)

    vehicles = [2, 3, 5, 7]
    frame_nmr = -1
    ret = True
    while ret:
        frame_nmr += 1
        ret, frame = cap.read()
        if ret:
            results[frame_nmr] = {}
            detections = coco_model(frame)[0]
            detections_ = []
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in vehicles:
                    detections_.append([x1, y1, x2, y2, score])
            # Add your tracking and other processing logic here

    # Save results to CSV
    util.write_csv(csv_path, results)

def add_missing_data(input_csv, output_csv):
    # Logic to add missing data to CSV
    df = pd.read_csv(input_csv)
    # Example: Fill missing values with 0
    df.fillna(0, inplace=True)
    df.to_csv(output_csv, index=False)

def generate_edited_video(video_path, csv_path, output_video_path):
    cap = cv2.VideoCapture(video_path)
    df = pd.read_csv(csv_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Add your video editing logic here using data from df
        out.write(frame)
    cap.release()
    out.release()

# Streamlit App
st.title("Video Processing and Editing")

# Upload video
uploaded_video = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
if uploaded_video is not None:
    video_path = NamedTemporaryFile(delete=False, suffix=".mp4").name
    with open(video_path, "wb") as f:
        f.write(uploaded_video.getbuffer())

# Upload initial CSV file
uploaded_csv = st.file_uploader("Upload initial CSV file", type=["csv"])
if uploaded_csv is not None:
    csv_path = NamedTemporaryFile(delete=False, suffix=".csv").name
    with open(csv_path, "wb") as f:
        f.write(uploaded_csv.getbuffer())

if uploaded_video and uploaded_csv:
    st.write("Processing video and CSV file...")
    # Run main script
    process_video(video_path, csv_path)

    corrected_csv_path = NamedTemporaryFile(delete=False, suffix="_corrected.csv").name
    # Run add_missing_data script
    add_missing_data(csv_path, corrected_csv_path)

    output_video_path = NamedTemporaryFile(delete=False, suffix="_edited.mp4").name
    # Run visualize script
    generate_edited_video(video_path, corrected_csv_path, output_video_path)

    st.write("Video processing complete. Download the edited video below.")
    with open(output_video_path, "rb") as file:
        st.download_button(
            label="Download Edited Video",
            data=file,
            file_name="edited_video.mp4",
            mime="video/mp4"
        )


