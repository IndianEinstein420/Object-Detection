import cv2
import time
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from PIL import Image
import torch
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

# Define COCO classes
COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat'
    # Continue with other categories if needed
]

# Define vehicle classes
VEHICLE_CLASSES = ['car', 'motorcycle', 'bus', 'truck']

# Load your model (make sure to load the appropriate model as per your setup)
model = ssdlite320_mobilenet_v3_large(pretrained=True)
model.eval()

# Function to convert camera frames and run detection
def detect_vehicles(pil_img):
    transform = transforms.Compose([transforms.Resize((300, 300)),
                                    transforms.ToTensor()])
    img_tensor = transform(pil_img).unsqueeze(0)  # Add batch dimension
    with torch.no_grad():
        predictions = model(img_tensor)
    
    boxes = predictions[0]['boxes']
    labels = predictions[0]['labels']
    scores = predictions[0]['scores']

    return boxes, labels, scores

# Function to process video from the external camera
def process_camera():
    # Use the external camera, set index accordingly (1, 2, etc.)
    cap = cv2.VideoCapture(1)  # Change '1' to your external camera index
    total_vehicles = 0
    scan_interval = 1  # seconds
    last_scan_time = time.time()

    plt.ion()  # Interactive mode on (optional for matplotlib)
    fig, ax = plt.subplots()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame. Exiting...")
                break

            # Convert frame to RGB for processing
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)

            # Process frames every scan_interval seconds
            if time.time() - last_scan_time >= scan_interval:
                last_scan_time = time.time()
                boxes, labels, scores = detect_vehicles(pil_img)

                # Count vehicles and filter based on class and score
                for label, score in zip(labels, scores):
                    if label < len(COCO_INSTANCE_CATEGORY_NAMES):  # Check label range
                        if COCO_INSTANCE_CATEGORY_NAMES[label] in VEHICLE_CLASSES and score > 0.5:
                            total_vehicles += 1

            # (Optional) Update the Matplotlib display, or comment out if no display is needed
            ax.clear()
            ax.imshow(frame_rgb)
            ax.set_title(f"Processing... Total vehicles: {total_vehicles}")
            plt.pause(0.001)

    except KeyboardInterrupt:
        # Gracefully handle exit with Ctrl+C
        print("Process interrupted by user.")

    finally:
        cap.release()
        plt.ioff()  # Turn off interactive mode
        plt.show()

    # Print the total vehicles detected after exiting
    print(f"Total vehicles detected: {total_vehicles}")

# Start the camera processing
process_camera()
