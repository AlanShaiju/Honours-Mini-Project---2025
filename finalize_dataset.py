import os
import cv2

# Directory setup with Windows-compatible paths
base_dir = "iot_security_dataset"
video_dir = os.path.join(base_dir, "videos")
data_dir = os.path.join(base_dir, "data")

# Expected files
expected_videos = [f"video{i}.mp4" for i in range(1, 6)]  # Changed to .mp4
expected_data = ["medical_data.csv", "encrypted_medical_data.csv"]

# Verify videos
print("Checking videos...")
for video in expected_videos:
    video_path = os.path.join(video_dir, video)
    if not os.path.exists(video_path):
        print(f"Error: {video} is missing.")
        continue
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open {video}.")
    else:
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"{video}: {frame_count} frames, {fps} fps, {width}x{height}")
    cap.release()

# Verify data files
print("\nChecking data files...")
for data_file in expected_data:
    data_path = os.path.join(data_dir, data_file)
    if not os.path.exists(data_path):
        print(f"Error: {data_file} is missing.")
    else:
        with open(data_path, 'r') as f:
            lines = len(f.readlines()) - 1  # Subtract header
        print(f"{data_file}: {lines} records")

print("\nDataset verification complete.")