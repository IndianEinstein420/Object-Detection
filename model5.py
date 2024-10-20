import cv2
import time
import serial
from PIL import Image
import torch
import torchvision.transforms as transforms
import matplotlib.pyplot as plt

# Setup Arduino serial communication
arduino = serial.Serial('COM3', 9600)  # Change 'COM3' to your Arduino's port

# Define COCO classes
COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat'
]

# Define vehicle classes
VEHICLE_CLASSES = ['car', 'motorcycle', 'bus', 'truck']

# Load the model
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

# Function to send vehicle data to Arduino
def send_to_arduino(vehicle_count):
    data = str(vehicle_count) + '\n'  # Prepare the data to be sent
    arduino.write(data.encode())  # Send the data

# Function to process video from the camera and send data every 30 seconds
def process_camera():
    cap = cv2.VideoCapture(1)  # Change '1' to your external camera index
    total_vehicles = 0
    scan_interval = 1  # seconds between each detection
    last_scan_time = time.time()
    last_send_time = time.time()  # Track the last time data was sent
    send_interval = 30  # seconds between each data transmission

    plt.ion()  # Interactive mode for matplotlib
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

            # Check if 30 seconds have passed to send data
            if time.time() - last_send_time >= send_interval:
                last_send_time = time.time()
                send_to_arduino(total_vehicles)  # Send the total vehicle count to Arduino
                print(f"Data sent to Arduino: {total_vehicles} vehicles")

            # (Optional) Update the Matplotlib display
            ax.clear()
            ax.imshow(frame_rgb)
            ax.set_title(f"Processing... Total vehicles: {total_vehicles}")
            plt.pause(0.001)

    except KeyboardInterrupt:
        print("Process interrupted by user.")

    finally:
        cap.release()
        plt.ioff()  # Turn off interactive mode
        plt.show()
        arduino.close()  # Close serial communication

    # Print the final total vehicle count
    print(f"Total vehicles detected: {total_vehicles}")

# Start the camera processing
process_camera()
