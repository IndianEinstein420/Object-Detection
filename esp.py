import network
import socket
import time

# WiFi credentials
SSID = 'YourSSID'
PASSWORD = 'YourPassword'

# Initialize vehicle count variables
vehicle_counts = [0, 0, 0, 0]  # For four roads

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    while not wlan.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
    print("Connected:", wlan.ifconfig())

# Start server to receive vehicle counts
def start_server():
    addr = socket.getaddrinfo('0.0.0.0', 12345)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Server listening on', addr)

    while True:
        cl, addr = s.accept()
        print('Connection from', addr)
        data = cl.recv(1024).decode('utf-8')
        
        # Process data in the format "R1:count1,R2:count2,R3:count3,R4:count4"
        if data:
            try:
                parts = data.strip().split(',')
                for i in range(4):
                    road, count = parts[i].split(':')
                    vehicle_counts[i] = int(count)
                print("Updated vehicle counts:", vehicle_counts)
                cl.send("Counts updated\n")
            except Exception as e:
                print("Failed to process data:", e)
                cl.send("Error\n")
        cl.close()

# Main execution
connect_wifi()
start_server()
