import torch
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision import transforms as T
from PIL import Image
import matplotlib.pyplot as plt
import cv2
import numpy as np

# Load the pre-trained SSD model
model = ssdlite320_mobilenet_v3_large(pretrained=True)
model.eval()
# Define the COCO dataset classes for vehicles
COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
    'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
    'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
    'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table',
    'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
    'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

# Filtered classes for vehicles only
VEHICLE_CLASSES = ['car', 'bus', 'motorcycle', 'truck']

#Calculate Delay
def calc(value): 
    if value >= 100:
        return 1
    elif 90 <= value < 100:
        return 1.5
    elif 80 <= value < 90:
        return 2
    elif 70 <= value < 80:
        return 2.5
    elif 60 <= value < 70:
        return 3
    elif 50 <= value < 60:
        return 3.5
    elif 40 <= value < 50:
        return 4
    else:  # For values below 40
        return 5

# Helper function to get outputs and filter vehicle detections
def detect_vehicles(image, threshold=0.5):
    transform = T.Compose([T.ToTensor()])
    img_tensor = transform(image).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        predictions = model(img_tensor)[0]  # Get the predictions

    vehicle_indices = []

    for i, label in enumerate(predictions['labels']):
        if label < len(COCO_INSTANCE_CATEGORY_NAMES) and COCO_INSTANCE_CATEGORY_NAMES[label] in VEHICLE_CLASSES and predictions['scores'][i] > threshold:
            vehicle_indices.append(i)

    boxes = predictions['boxes'][vehicle_indices].cpu().numpy()
    labels = [COCO_INSTANCE_CATEGORY_NAMES[label] for label in predictions['labels'][vehicle_indices]]
    scores = predictions['scores'][vehicle_indices].cpu().numpy()

    return boxes, labels, scores

# Function to check if a new box is close to any previous boxes
def is_near_existing_box(new_box, existing_boxes, distance_threshold=50):
    for box in existing_boxes:
        if (abs(new_box[0] - box[0]) < distance_threshold and  # x1
            abs(new_box[1] - box[1]) < distance_threshold and  # y1
            abs(new_box[2] - box[2]) < distance_threshold and  # x2
            abs(new_box[3] - box[3]) < distance_threshold):    # y2
            return True
    return False

# Video processing to detect vehicles in real-time
def process_video(video_path, scan_interval=2):  # scan_interval is in seconds
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frame rate of the video
    frame_skip = int(fps * scan_interval)  # Calculate the number of frames to skip

    total_cars_detected = 0  # Initialize a counter for total cars detected
    previous_boxes = []  # List to store previous bounding boxes

    plt.ion()  # Turn on interactive mode for Matplotlib

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Reached end of the video or failed to grab frame.")
            break

        frame_count = int(cap.get(cv2.CAP_PROP_POS_FRAMES))  # Current frame count

        if frame_count % frame_skip == 0:
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Detect vehicles
            boxes, labels, scores = detect_vehicles(pil_img)

            # Count the number of unique cars detected
            unique_cars = 0
            for box in boxes:
                # Check if this box is not close to any previous box
                if not is_near_existing_box(box, previous_boxes):
                    unique_cars += 1
                    previous_boxes.append(box)  # Add to the list of tracked boxes

            total_cars_detected += unique_cars  # Increment total count

            # Visualize the detection
            plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            plt.title(f'Total Unique Cars: {total_cars_detected}')
            plt.axis('off')
            plt.pause(0.01)  # Pause to allow the plot to update
            plt.clf()  # Clear the current figure for the next frame

    plt.ioff()  # Turn off interactive mode for Matplotlib
    cap.release()

    # Print the total number of unique cars detected in the entire video
    print(f"Total number of unique cars detected: {total_cars_detected}")

avg_speed = int(input("Enter Average Speed:"))
delay_rate= calc(avg_speed)
# Run the detection on a video file
process_video('timelapse.mp4',scan_interval=delay_rate)  # Provide path to your video file
