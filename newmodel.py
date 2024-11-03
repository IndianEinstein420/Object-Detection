import cv2
import time
import threading
import sqlite3
import socket
import torch
from PIL import Image
import torchvision.transforms as transforms
from torchvision.models.detection import ssdlite320_mobilenet_v3_large

# ESP32 Camera stream URLs
camera_stream_urls = [
    "http://192.168.1.100:8081/stream",  # Camera 1
    "http://192.168.1.100:8082/stream",  # Camera 2
    "http://192.168.1.100:8083/stream",  # Camera 3
    "http://192.168.1.100:8084/stream"   # Camera 4
]

# Vehicle counts for each road
vehicle_counts = [0, 0, 0, 0]

# Load the pretrained model
model = ssdlite320_mobilenet_v3_large(pretrained=True)
model.eval()

# Define COCO classes
COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat'
]
VEHICLE_CLASSES = ['car', 'motorcycle', 'bus', 'truck']

# Database setup
db_conn = sqlite3.connect('vehicle_data.db')
db_cursor = db_conn.cursor()
db_cursor.execute('''CREATE TABLE IF NOT EXISTS vehicle_counts (timestamp TEXT, road_id INTEGER, count INTEGER)''')
db_conn.commit()

# Function to process each camera stream
def process_camera(url, road_id):
    cap = cv2.VideoCapture(url)
    global vehicle_counts

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to RGB for detection
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(frame_rgb)

        # Transform and detect vehicles
        transform = transforms.Compose([transforms.Resize((300, 300)), transforms.ToTensor()])
        img_tensor = transform(pil_img).unsqueeze(0)

        with torch.no_grad():
            predictions = model(img_tensor)

        # Filter results and count vehicles
        boxes, labels, scores = predictions[0]['boxes'], predictions[0]['labels'], predictions[0]['scores']
        vehicle_count = sum(1 for label, score in zip(labels, scores)
                            if label < len(COCO_INSTANCE_CATEGORY_NAMES) and 
                            COCO_INSTANCE_CATEGORY_NAMES[label] in VEHICLE_CLASSES and score > 0.5)
        
        # Update vehicle count for this road
        vehicle_counts[road_id] = vehicle_count
        print(f"Road {road_id + 1}: {vehicle_count} vehicles")

        # Optional delay for reduced processing rate (e.g., process every 2 seconds)
        time.sleep(2)

# Start threads for each camera stream
threads = []
for i, url in enumerate(camera_stream_urls):
    thread = threading.Thread(target=process_camera, args=(url, i))
    threads.append(thread)
    thread.start()

# Function to log vehicle counts to the database
def log_to_database():
    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        for road_id, count in enumerate(vehicle_counts):
            db_cursor.execute("INSERT INTO vehicle_counts (timestamp, road_id, count) VALUES (?, ?, ?)",
                              (timestamp, road_id, count))
        db_conn.commit()
        print("Data saved to database")
        time.sleep(30)  # Log data every 30 seconds

# Start logging thread
logging_thread = threading.Thread(target=log_to_database)
logging_thread.start()

# Function to send data to ESP32
def send_data_to_esp32():
    esp32_ip = '192.168.1.100'  # Replace with the ESP32's IP address
    esp32_port = 12345          # Replace with the ESP32's port

    while True:
        # Create message for ESP32 with vehicle counts for each road
        message = f"R1:{vehicle_counts[0]},R2:{vehicle_counts[1]},R3:{vehicle_counts[2]},R4:{vehicle_counts[3]}\n"
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((esp32_ip, esp32_port))
                s.sendall(message.encode())
                print(f"Data sent to ESP32: {message}")
        except (socket.error, Exception) as e:
            print("Failed to send data:", e)
        
        time.sleep(30)  # Send data every 30 seconds

# Start ESP32 data transmission thread
esp32_thread = threading.Thread(target=send_data_to_esp32)
esp32_thread.start()
