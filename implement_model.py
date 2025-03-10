import cv2
import numpy as np
import csv
import os
from tinyec import registry
import secrets
import math

# Directory setup with Windows-compatible paths
base_dir = "iot_security_dataset"
video_dir = os.path.join(base_dir, "videos")
data_dir = os.path.join(base_dir, "data")
output_dir = os.path.join(base_dir, "stego_videos")
os.makedirs(output_dir, exist_ok=True)

# Step 1: Load and Encrypt Data
curve = registry.get_curve('secp256r1')
private_key = secrets.randbelow(curve.field.n)
public_key = private_key * curve.g

def encrypt_message(message, public_key):
    k = secrets.randbelow(curve.field.n)
    C1 = k * curve.g
    C2 = (k * public_key).x ^ int.from_bytes(message.encode(), 'big')
    return C1.x, C1.y, C2

encrypted_data = []
with open(os.path.join(data_dir, "medical_data.csv"), 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header
    for row in reader:
        message = ','.join(row)
        C1_x, C1_y, C2 = encrypt_message(message, public_key)
        encrypted_data.append((C1_x, C1_y, C2))

print(f"Loaded and encrypted {len(encrypted_data)} records.")

# Step 2: Matrix XOR Steganography
def matrix_xor_embed(cover_block, secret_bit):
    secret_binary = bin(secret_bit)[2:].zfill(8)[:1]
    cover_binary = bin(cover_block[0, 0])[2:].zfill(8)
    result = int(secret_binary, 2) ^ int(cover_binary[-1], 2)
    if result == 0:
        return cover_block
    cover_block[0, 0] = cover_block[0, 0] ^ 1
    return cover_block

# Step 3: Adaptive Firefly Optimization
def firefly_optimize(frame, num_blocks=10):
    height, width = frame.shape[:2]
    block_size = 8
    blocks = []
    brightness = lambda block: np.mean(block)
    for y in range(0, height - block_size + 1, block_size):
        for x in range(0, width - block_size + 1, block_size):
            block = frame[y:y+block_size, x:x+block_size]
            blocks.append((block, (x, y), brightness(block)))
    blocks.sort(key=lambda x: x[2])
    return blocks[:num_blocks]

# Step 4: Embed Data into Videos
video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4')]  # Changed to .mp4
bits_per_frame = 10
total_bits = len(encrypted_data) * 3 * 64

for video_file in video_files:
    input_path = os.path.join(video_dir, video_file)
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"Error: Could not open {input_path}")
        continue

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Use MP4 with mp4v codec
    output_file = os.path.join(output_dir, f"stego_{video_file}")  # Keeps .mp4 extension
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Reliable codec for MP4
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

    if not out.isOpened():
        print(f"Error: Could not open VideoWriter for {output_file}")
        cap.release()
        continue

    bit_index = 0
    frames_written = 0
    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            print(f"Warning: Failed to read frame {i} from {video_file}")
            break

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        selected_blocks = firefly_optimize(frame_gray, bits_per_frame)

        for block, (x, y), _ in selected_blocks:
            if bit_index < total_bits:
                record_idx = bit_index // (3 * 64)
                field_idx = (bit_index % (3 * 64)) // 64
                bit_pos = bit_index % 64
                if record_idx < len(encrypted_data):
                    secret_bit = (encrypted_data[record_idx][field_idx] >> (63 - bit_pos)) & 1
                    block = matrix_xor_embed(block, secret_bit)
                    frame_gray[y:y+8, x:x+8] = block
                bit_index += 1

        frame_stego = cv2.cvtColor(frame_gray, cv2.COLOR_GRAY2BGR)
        out.write(frame_stego)
        frames_written += 1

    print(f"Wrote {frames_written} frames to {output_file}")
    cap.release()
    out.release()

    # Optional: Convert to H.264 with FFmpeg for consistency (uncomment if needed)
    # temp_file = output_file
    # output_file_h264 = output_file.replace('.mp4', '_h264.mp4')
    # os.system(f"ffmpeg -i \"{temp_file}\" -c:v libx264 -y \"{output_file_h264}\"")
    # os.remove(temp_file)
    # print(f"Processed {video_file} -> {output_file_h264}")

    print(f"Processed {video_file} -> {output_file}")

# Step 5: Evaluate PSNR
def calculate_psnr(original, stego):
    mse = np.mean((original - stego) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * math.log10(255**2 / mse)

cap_orig = cv2.VideoCapture(os.path.join(video_dir, "video1.mp4"))  # Changed to .mp4
cap_stego = cv2.VideoCapture(os.path.join(output_dir, "stego_video1.mp4"))  # Changed to .mp4
ret_orig, frame_orig = cap_orig.read()
ret_stego, frame_stego = cap_stego.read()
if ret_orig and ret_stego:
    psnr = calculate_psnr(cv2.cvtColor(frame_orig, cv2.COLOR_BGR2GRAY),
                          cv2.cvtColor(frame_stego, cv2.COLOR_BGR2GRAY))
    print(f"PSNR for video1: {psnr:.2f} dB")
else:
    print("Error: Could not read frames for PSNR calculation.")
cap_orig.release()
cap_stego.release()

print("Model implementation complete.")