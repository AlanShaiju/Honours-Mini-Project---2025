import csv
import random
from datetime import datetime, timedelta
import os

# Directory setup
data_dir = "iot_security_dataset/data"
os.makedirs(data_dir, exist_ok=True)

# Parameters
num_records = 100
start_time = datetime(2025, 3, 10, 10, 0, 0)
filename = f"{data_dir}/medical_data.csv"

# Generate data
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["PatientID", "Timestamp", "HeartRate", "BloodPressure", "Temperature"])
    for i in range(num_records):
        patient_id = f"{i+1:03d}"
        timestamp = start_time + timedelta(seconds=i*60)  # Increment by 1 minute
        hr = random.randint(60, 100)
        bp_sys = random.randint(100, 140)
        bp_dia = random.randint(60, 90)
        temp = round(random.uniform(36.0, 37.5), 1)
        writer.writerow([patient_id, timestamp, hr, f"{bp_sys}/{bp_dia}", temp])

print(f"Generated {num_records} records in {filename}")