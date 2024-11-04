from flask import Flask, request
import numpy as np
import cv2
import torch
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision import transforms
import sqlite3
import time

app = Flask(__name__)

# Load the pretrained model
model = ssdlite320_mobilenet_v3_large(pretrained=True)
model.eval()

# Define COCO classes
COCO_INSTANCE_CATEGORY_NAMES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat'
]
VEHICLE_CLASSES = ['car', 'motorcycle', 'bus', 'truck']

# Database setup
db_conn = sqlite3.connect('vehicle_data.db', check_same_thread=False)
db_cursor = db_conn.cursor()
db_cursor.execute('''CREATE TABLE IF NOT EXISTS vehicle_counts (
                      timestamp TEXT,
                      road_id INTEGER,
                      count INTEGER)''')
db_conn.commit()

# Function to detect vehicles in the image
def detect_vehicles(image):
    transform = transforms.Compose([transforms.ToTensor()])
    img_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        predictions = model(img_tensor)

    boxes, labels, scores = predictions[0]['boxes'], predictions[0]['labels'], predictions[0]['scores']
    vehicle_count = sum(1 for label, score in zip(labels, scores)
                        if label < len(COCO_INSTANCE_CATEGORY_NAMES) and 
                        COCO_INSTANCE_CATEGORY_NAMES[label] in VEHICLE_CLASSES and score > 0.5)

    return vehicle_count

@app.route('/process_image', methods=['POST'])
def process_image():
    image_data = request.data
    # Convert byte data to a numpy array
    np_arr = np.frombuffer(image_data, np.uint8)
    # Decode the image
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Detect vehicles
    vehicle_count = detect_vehicles(image)

    # Print vehicle count
    print(f"Detected vehicles: {vehicle_count}")

    # Log to database
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    road_id = 1  # Set this based on the camera/road id being processed
    db_cursor.execute("INSERT INTO vehicle_counts (timestamp, road_id, count) VALUES (?, ?, ?)",
                      (timestamp, road_id, vehicle_count))
    db_conn.commit()
    
    return str(vehicle_count)  # Return the vehicle count as a string

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
