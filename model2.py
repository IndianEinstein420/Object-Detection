import torch
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision import transforms as T
from PIL import Image
import cv2
import matplotlib.pyplot as plt

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

# Helper function to get outputs and filter vehicle detections
def detect_vehicles(image, threshold=0.5):
    transform = T.Compose([T.ToTensor()])
    img_tensor = transform(image).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        predictions = model(img_tensor)[0]  # Get the predictions

    # Filter for vehicle classes and high confidence scores
    vehicle_indices = []
    
    for i, label in enumerate(predictions['labels']):
        # Check if the label is within bounds and then check the class
        if label < len(COCO_INSTANCE_CATEGORY_NAMES) and COCO_INSTANCE_CATEGORY_NAMES[label] in VEHICLE_CLASSES and predictions['scores'][i] > threshold:
            vehicle_indices.append(i)

    boxes = predictions['boxes'][vehicle_indices].cpu().numpy()
    labels = [COCO_INSTANCE_CATEGORY_NAMES[label] for label in predictions['labels'][vehicle_indices]]
    scores = predictions['scores'][vehicle_indices].cpu().numpy()

    return boxes, labels, scores

# Video processing to detect vehicles in real-time
def process_video(video_path, display_time=1, scan_interval=2):  # scan_interval is in seconds
    cap = cv2.VideoCapture(video_path)

    # Check if the video file is opened successfully
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)  # Get the frame rate of the video
    frame_skip = int(fps * scan_interval)  # Calculate the number of frames to skip

    total_cars_detected = 0  # Initialize a counter for total cars detected
    frame_count = 0  # Initialize frame count

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Reached end of the video or failed to grab frame.")
            break

        # Skip frames based on the frame_skip value
        if frame_count % frame_skip == 0:
            # Convert to PIL format
            pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Detect vehicles
            boxes, labels, scores = detect_vehicles(pil_img)

            # Count the number of cars detected in the current frame
            num_cars_in_frame = sum(1 for label in labels if label == 'car')
            total_cars_detected += num_cars_in_frame  # Increment total count

            # Draw boxes (optional, can be removed)
            for box, label, score in zip(boxes, labels, scores):
                x1, y1, x2, y2 = box.astype(int)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                text = f"{label}: {score:.2f}"
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Display the frame using Matplotlib (optional, can be removed)
            plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            plt.axis('off')  # Hide the axes
            plt.pause(display_time)  # Pause for the specified display time
            plt.clf()  # Clear the figure for the next frame

        frame_count += 1  # Increment frame count

    cap.release()
    plt.close()  # Close the Matplotlib window

    # Print the total number of cars detected in the entire video
    print(f"Total number of cars detected: {total_cars_detected}")

# Run the detection on a video file
process_video('22.mp4',scan_interval=1)  # Provide path to your video file
