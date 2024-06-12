import streamlit as st
import pandas as pd
import numpy as np
import cv2
import ast
from scipy.interpolate import interp1d
from ultralytics import YOLO
import sys
sys.path.append("pages/utils")

import util  # Assuming util.py is directly inside the utils folder
from sort import Sort
import os

# Function to interpolate bounding boxes
def interpolate_bounding_boxes(data):
    interpolated_data = []

    # Extract necessary data columns from input data
    frame_numbers = np.array([int(row['frame_nmr']) for row in data])
    car_ids = np.array([int(float(row['car_id'])) for row in data])
    car_bboxes = np.array([list(map(float, row['car_bbox'][1:-1].split())) for row in data])
    license_plate_bboxes = np.array([list(map(float, row['license_plate_bbox'][1:-1].split())) for row in data])

    unique_car_ids = np.unique(car_ids)
    for car_id in unique_car_ids:
        frame_numbers_ = [p['frame_nmr'] for p in data if int(float(p['car_id'])) == int(float(car_id))]

        # Filter data for a specific car ID
        car_mask = car_ids == car_id
        car_frame_numbers = frame_numbers[car_mask]
        car_bboxes_interpolated = []
        license_plate_bboxes_interpolated = []

        first_frame_number = car_frame_numbers[0]
        last_frame_number = car_frame_numbers[-1]

        for i in range(len(car_bboxes[car_mask])):
            frame_number = car_frame_numbers[i]
            car_bbox = car_bboxes[car_mask][i]
            license_plate_bbox = license_plate_bboxes[car_mask][i]

            if i > 0:
                prev_frame_number = car_frame_numbers[i - 1]
                prev_car_bbox = car_bboxes_interpolated[-1]
                prev_license_plate_bbox = license_plate_bboxes_interpolated[-1]

                if frame_number - prev_frame_number > 1:
                    # Interpolate missing frames' bounding boxes
                    frames_gap = frame_number - prev_frame_number
                    x = np.array([prev_frame_number, frame_number])
                    x_new = np.linspace(prev_frame_number, frame_number, num=frames_gap, endpoint=False)
                    interp_func = interp1d(x, np.vstack((prev_car_bbox, car_bbox)), axis=0, kind='linear')
                    interpolated_car_bboxes = interp_func(x_new)
                    interp_func = interp1d(x, np.vstack((prev_license_plate_bbox, license_plate_bbox)), axis=0, kind='linear')
                    interpolated_license_plate_bboxes = interp_func(x_new)

                    car_bboxes_interpolated.extend(interpolated_car_bboxes[1:])
                    license_plate_bboxes_interpolated.extend(interpolated_license_plate_bboxes[1:])

            car_bboxes_interpolated.append(car_bbox)
            license_plate_bboxes_interpolated.append(license_plate_bbox)

        for i in range(len(car_bboxes_interpolated)):
            frame_number = first_frame_number + i
            row = {}
            row['frame_nmr'] = str(frame_number)
            row['car_id'] = str(car_id)
            row['car_bbox'] = ' '.join(map(str, car_bboxes_interpolated[i]))
            row['license_plate_bbox'] = ' '.join(map(str, license_plate_bboxes_interpolated[i]))

            if str(frame_number) not in frame_numbers_:
                # Imputed row, set the following fields to '0'
                row['license_plate_bbox_score'] = '0'
                row['license_number'] = '0'
                row['license_number_score'] = '0'
            else:
                # Original row, retrieve values from the input data if available
                original_row = [p for p in data if int(p['frame_nmr']) == frame_number and int(float(p['car_id'])) == int(float(car_id))][0]
                row['license_plate_bbox_score'] = original_row['license_plate_bbox_score'] if 'license_plate_bbox_score' in original_row else '0'
                row['license_number'] = original_row['license_number'] if 'license_number' in original_row else '0'
                row['license_number_score'] = original_row['license_number_score'] if 'license_number_score' in original_row else '0'

            interpolated_data.append(row)

    return interpolated_data

def draw_border(img, top_left, bottom_right, color=(0, 255, 0), thickness=10, line_length_x=200, line_length_y=200):
    x1, y1 = top_left
    x2, y2 = bottom_right

    cv2.line(img, (x1, y1), (x1, y1 + line_length_y), color, thickness)  #-- top-left
    cv2.line(img, (x1, y1), (x1 + line_length_x, y1), color, thickness)
    
    cv2.line(img, (x1, y2), (x1, y2 - line_length_y), color, thickness)  #-- bottom-left
    cv2.line(img, (x1, y2), (x1 + line_length_x, y2), color, thickness)

    cv2.line(img, (x2, y1), (x2 - line_length_x, y1), color, thickness)  #-- top-right
    cv2.line(img, (x2, y1), (x2, y1 + line_length_y), color, thickness)

    cv2.line(img, (x2, y2), (x2, y2 - line_length_y), color, thickness)  #-- bottom-right
    cv2.line(img, (x2, y2), (x2 - line_length_x, y2), color, thickness)

    return img


def process_video(video_path):
    # Convert uploaded file to file path
    video_path = "uploaded_video.mp4"
    with open(video_path, "wb") as f:
        f.write(video_file.getbuffer())

    results = {}
    mot_tracker = Sort()

    # Load models
    coco_model = YOLO('yolov8n')
    license_plate_detector = YOLO("pages/yolov8n_license_plate.pt")


    cap = cv2.VideoCapture(video_path)
    vehicles = [2, 3, 5, 7]

    # Read frames
    frame_nmr = -1
    ret = True
    while ret:
        frame_nmr += 1
        ret, frame = cap.read()
        if ret:
            results[frame_nmr] = {}

            # Detect vehicles
            detections = coco_model(frame)[0]
            detections_ = []
            for detection in detections.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = detection
                if int(class_id) in vehicles:
                    detections_.append([x1, y1, x2, y2, score])

            # Track vehicles
            track_ids = mot_tracker.update(np.asarray(detections_))

            # Detect license plates
            license_plates = license_plate_detector(frame)[0]
            for license_plate in license_plates.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = license_plate

                # Assign license plate to car
                xcar1, ycar1, xcar2, ycar2, car_id = util.get_car(license_plate, track_ids)

                if car_id != -1:
                    # Crop license plate
                    license_plate_crop = frame[int(y1):int(y2), int(x1): int(x2), :]

                    # Process license plate
                    license_plate_crop_gray = cv2.cvtColor(license_plate_crop, cv2.COLOR_BGR2GRAY)
                    _, license_plate_crop_thresh = cv2.threshold(license_plate_crop_gray, 64, 255, cv2.THRESH_BINARY_INV)

                    # Read license plate number
                    license_plate_text, license_plate_text_score = util.read_license_plate(license_plate_crop_thresh)

                    if license_plate_text is not None:
                        results[frame_nmr][car_id] = {'car': {'bbox': [xcar1, ycar1, xcar2, ycar2]},
                                                      'license_plate': {'bbox': [x1, y1, x2, y2],
                                                                        'text': license_plate_text,
                                                                        'bbox_score': score,
                                                                        'text_score': license_plate_text_score}}

    # Write results
    output_csv_path = 'output.csv'
    util.write_csv(results, output_csv_path)

    # Interpolate missing data
    with open(output_csv_path, 'r') as file:
        reader = pd.read_csv(file)
        data = list(reader)

    interpolated_data = interpolate_bounding_boxes(data)

    # Write updated data to a new CSV file
    header = ['frame_nmr', 'car_id', 'car_bbox', 'license_plate_bbox', 'license_plate_bbox_score', 'license_number', 'license_number_score']
    with open('test_interpolated.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        writer.writerows(interpolated_data)

    # Load video again for visualization
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter('./output.mp4', fourcc, fps, (width, height))

    license_plate = {}
    for car_id in np.unique(results['car_id']):
        max_score_index = results[results['car_id'] == car_id]['license_plate_bbox_score'].idxmax()
        license_plate_number = results.loc[max_score_index, 'license_number']
        license_plate_bbox = ast.literal_eval(results.loc[max_score_index, 'license_plate_bbox'])
        x1, y1, x2, y2 = license_plate_bbox

        cap.set(cv2.CAP_PROP_POS_FRAMES, int(results.loc[max_score_index, 'frame_nmr']))
        ret, frame = cap.read()

        license_crop = frame[int(y1):int(y2), int(x1):int(x2), :]
        license_crop = cv2.resize(license_crop, (int((x2 - x1) * 400 / (y2 - y1)), 400))

        license_plate[car_id] = {'license_crop': license_crop, 'license_plate_number': license_plate_number}

    frame_nmr = -1
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Read frames again for visualization
    ret = True
    while ret:
        ret, frame = cap.read()
        frame_nmr += 1
        if ret:
            df1 = results[results['frame_nmr'] == frame_nmr]
            for row_indx in range(len(df1)):
                # Draw car
                car_x1, car_y1, car_x2, car_y2 = ast.literal_eval(df1.iloc[row_indx]['car_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                draw_border(frame, (int(car_x1), int(car_y1)), (int(car_x2), int(car_y2)), (0, 255, 0), 25,
                            line_length_x=200, line_length_y=200)

                # Draw license plate
                x1, y1, x2, y2 = ast.literal_eval(df1.iloc[row_indx]['license_plate_bbox'].replace('[ ', '[').replace('   ', ' ').replace('  ', ' ').replace(' ', ','))
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 12)

                # Crop license plate
                license_crop = license_plate[df1.iloc[row_indx]['car_id']]['license_crop']

                H, W, _ = license_crop.shape

                try:
                    frame[int(car_y1) - H - 100:int(car_y1) - 100,
                          int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = license_crop

                    frame[int(car_y1) - H - 400:int(car_y1) - H - 100,
                          int((car_x2 + car_x1 - W) / 2):int((car_x2 + car_x1 + W) / 2), :] = (255, 255, 255)

                    (text_width, text_height), _ = cv2.getTextSize(
                        license_plate[df1.iloc[row_indx]['car_id']]['license_plate_number'],
                        cv2.FONT_HERSHEY_SIMPLEX,
                        4.3,
                        17)

                    cv2.putText(frame,
                                license_plate[df1.iloc[row_indx]['car_id']]['license_plate_number'],
                                (int((car_x2 + car_x1 - text_width) / 2), int(car_y1 - H - 250 + (text_height / 2))),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                4.3,
                                (0, 0, 0),
                                17)

                except:
                    pass

            out.write(frame)
            frame = cv2.resize(frame, (1280, 720))

            # Display frame in Streamlit
            st.image(frame, channels="BGR", use_column_width=True)

    out.release()
    cap.release()

# Streamlit app
def main():
    st.title("Video Processor")

    # File uploader
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4"])

    if uploaded_file is not None:
        # Process the video
        process_video(uploaded_file)

        # Provide download links for the processed video and CSV
        st.markdown("[Download processed video](./output.mp4)")
        st.markdown("[Download processed CSV](./test_interpolated.csv)")

if __name__ == "__main__":
    main()

