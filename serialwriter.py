import serial
import time

# Import pySerial library and setup serial communication with Arduino
arduino = serial.Serial('COM3', 9600)  # Change 'COM3' to your Arduino's port

# Function to send data to Arduino
def send_to_arduino(vehicle_count):
    data = str(vehicle_count) + '\n'  # Prepare the data to be sent
    arduino.write(data.encode())  # Send the data

# Example of how you could integrate sending data
total_vehicles = 75 # This will hold the total vehicle count

# At the end of your loop or after processing:
send_to_arduino(total_vehicles)  # Send the total count to Arduino
print(f"Total vehicles detected: {total_vehicles}")

# Close the serial connection when done (important)
arduino.close()
