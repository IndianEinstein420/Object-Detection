import cv2
import time
import torch
import matplotlib.pyplot as plt
from ultralytics import YOLO  # Import YOLO from ultralytics package

# Load the YOLOv5 model (replace with path if you have a specific model file)
model = YOLO('yolov5s.pt')  # or another YOLO model file, e.g., 'best.pt' from your training

# Initialize webcam
cap = cv2.VideoCapture(0)  # 0 is usually the default webcam

# Timer settings
start_time = time.time()
vehicle_count = 0
frame_resize = (640, 480)  # Resize frame for faster processing

plt.ion()  # Enable interactive mode for Matplotlib
last_inference_time = time.time()  # Track the last time inference was run

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from camera.")
            break

        # Resize frame for faster processing
        frame_resized = cv2.resize(frame, frame_resize)
        
        # Run YOLOv5 inference every 1 second
        if time.time() - last_inference_time >= 1:
            last_inference_time = time.time()

            # Perform inference
            results = model(frame_resized)

            # Count vehicles in results
            current_vehicle_count = 0
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])  # Get class id
                    if model.names[cls] in ["car", "motorcycle", "bus", "truck"]:
                        current_vehicle_count += 1

            vehicle_count += current_vehicle_count

            # Check if 20 seconds have passed
            if time.time() - start_time >= 20:
                print(f"Vehicle count in the last 20 seconds: {vehicle_count}")
                vehicle_count = 0  # Reset counter for the next interval
                start_time = time.time()  # Reset timer

        # Display the frame using Matplotlib (refresh every 5 seconds)
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        plt.imshow(frame_rgb)
        plt.title(f"Vehicle count: {current_vehicle_count}")
        plt.axis('off')
        plt.draw()
        plt.pause(0.001)  # Short pause to allow the image to update

finally:
    # Release resources
    cap.release()
    plt.close()  # Close the Matplotlib window
