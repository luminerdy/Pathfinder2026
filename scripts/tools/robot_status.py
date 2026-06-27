#!/usr/bin/env python3
"""
Quick robot status check
Shows: battery, camera, system info
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_BATTERY = REPO_ROOT / 'scripts' / 'tools' / 'check_battery.py'

print("=" * 60)
print("PATHFINDER ROBOT STATUS")
print("=" * 60)

# System info
print("\n=== SYSTEM ===")
print(f"Hostname: {subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip()}")
print(f"User: robot")

# Battery
print("\n=== BATTERY ===")
try:
    result = subprocess.run(['python3', str(CHECK_BATTERY)],
                            capture_output=True, text=True, cwd=str(REPO_ROOT))
    print(result.stdout)
except:
    print("Could not check battery")

# Camera
print("\n=== CAMERA ===")
import cv2
camera_found = False
for device in [0, 1, 2]:
    try:
        cap = cv2.VideoCapture(device)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"Camera: Found on /dev/video{device}")
                print(f"Resolution: {frame.shape[1]}x{frame.shape[0]}")
                camera_found = True
                cap.release()
                break
            cap.release()
    except:
        pass

if not camera_found:
    print("Camera: NOT DETECTED")
    print("  - Check USB connection")
    print("  - Try: lsusb | grep -i camera")

# USB devices
print("\n=== USB DEVICES ===")
try:
    result = subprocess.run(['lsusb'], capture_output=True, text=True)
    for line in result.stdout.strip().split('\n'):
        if 'camera' in line.lower() or 'video' in line.lower() or 'webcam' in line.lower():
            print(f"  {line}")
except:
    pass

# Serial devices
print("\n=== SERIAL DEVICES ===")
try:
    result = subprocess.run(['ls', '-la', '/dev/ttyAMA*'], capture_output=True, text=True)
    for line in result.stdout.strip().split('\n'):
        if 'ttyAMA' in line:
            print(f"  {line}")
except:
    print("  Could not list serial devices")

print("\n" + "=" * 60)
