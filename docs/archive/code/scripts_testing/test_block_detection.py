#!/usr/bin/env python3
"""
Test Block Detection on Real Field
Shows what blocks the robot can see
"""

import cv2
import time
from skills.block_detect import BlockDetector  # was: capabilities.vision

def main():
    print("=" * 60)
    print("BLOCK DETECTION TEST")
    print("=" * 60)

    # Initialize camera
    camera = cv2.VideoCapture(0)
    time.sleep(0.5)

    # Initialize detector
    detector = BlockDetector()

    print("\nCapturing image...")
    ret, frame = camera.read()
    if not ret:
        print("ERROR: Could not capture frame")
        return

    print(f"Image size: {frame.shape[1]}x{frame.shape[0]}")

    # Detect blocks by color
    print("\nDetecting blocks...")

    blocks = detector.detect(frame)

    # Report findings
    print("\n" + "=" * 60)
    print("DETECTION RESULTS")
    print("=" * 60)

    total = len(blocks)
    for i, block in enumerate(blocks, 1):
        print(f"\n{block.color.upper()} BLOCK {i}:")
        print(f"  Center: ({block.center_x}, {block.center_y}) pixels")
        print(f"  Area: {block.area:.0f} pixels")
        print(f"  Width: {block.width} pixels")
        print(f"  Height: {block.height} pixels")
        print(f"  Distance: {block.estimated_distance_mm/10:.0f} cm")
        print(f"  Confidence: {block.confidence:.2f}")

    if total == 0:
        print("\nNO BLOCKS DETECTED")
        print("\nTroubleshooting:")
        print("  - Are blocks in camera view?")
        print("  - Is lighting sufficient?")
        print("  - Are colors distinct enough?")
    else:
        print(f"\n{total} total block(s) detected!")

    # Save annotated image
    print("\nSaving annotated image...")
    annotated = frame.copy()

    detector.annotate_frame(annotated, blocks)

    filename = f'blocks_detected_{int(time.time())}.jpg'
    cv2.imwrite(filename, annotated)
    print(f"Saved: {filename}")

    # Also save raw image for comparison
    raw_filename = f'blocks_raw_{int(time.time())}.jpg'
    cv2.imwrite(raw_filename, frame)
    print(f"Saved: {raw_filename}")

    camera.release()

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

    if total > 0:
        print("\nNext steps:")
        print("  1. Check annotated image to verify detections")
        print("  2. If blocks detected, try: python3 test_approach_smart.py")
        print("  3. For full pickup test: python3 test_pickup_ik.py")
    else:
        print("\nAdjust lighting or block positions and try again")


if __name__ == '__main__':
    main()
