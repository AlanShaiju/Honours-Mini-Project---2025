from tinyec import registry
import secrets
import csv
import os

# Directory setup
data_dir = "iot_security_dataset/data"
os.makedirs(data_dir, exist_ok=True)

# Load curve
curve = registry.get_curve('secp256r1')

# Generate key pair
private_key = secrets.randbelow(curve.field.n)
public_key = private_key * curve.g

# Encryption function (simplified, not full EGC)
def encrypt_message(message, public_key):
    k = secrets.randbelow(curve.field.n)
    C1 = k * curve.g  # Point on curve
    C2 = (k * public_key).x ^ int.from_bytes(message.encode(), 'big')  # XOR with x-coordinate
    return C1, C2

# Read and encrypt medical data
encrypted_data = []
input_file = f"{data_dir}/medical_data.csv"
output_file = f"{data_dir}/encrypted_medical_data.csv"

with open(input_file, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        message = ','.join(row)
        C1, C2 = encrypt_message(message, public_key)
        encrypted_data.append((C1.x, C1.y, C2))

# Save encrypted data
with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["C1_x", "C1_y", "C2"])
    for data in encrypted_data:
        writer.writerow(data)

print(f"Encrypted data saved to {output_file}")