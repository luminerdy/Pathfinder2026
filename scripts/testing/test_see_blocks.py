#!/usr/bin/env python3
"""
Simple Block Detection Test
Shows what blocks robot can see
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
        camera.release()
        return

    print(f"Image size: {frame.shape[1]}x{frame.shape[0]}")

    # Detect each color
    print("\n" + "=" * 60)
    print("DETECTION RESULTS")
    print("=" * 60)

    detections = detector.detect(frame)
    total = len(detections)

    for block in detections:
        print(f"\n{block.color.upper()} BLOCK DETECTED:")
        print(f"  Position: ({block.center_x}, {block.center_y}) pixels")
        print(f"  Size: {block.width}x{block.height} pixels")
        print(f"  Distance: {block.estimated_distance_mm/10:.0f} cm")
        print(f"  Area: {block.area:.0f} pixels")
        print(f"  Confidence: {block.confidence:.2f}")

    if total == 0:
        print("\nNO BLOCKS DETECTED")
        print("\nTroubleshooting:")
        print("  - Are blocks in camera view?")
        print("  - Is lighting sufficient?")
        print("  - Try adjusting HSV ranges in config.yaml")
    else:
        print(f"\n{total} block(s) detected!")

    # Save annotated image
    print("\nSaving images...")
    annotated = frame.copy()

    detector.annotate_frame(annotated, detections)

    # Save files
    timestamp = int(time.time())
    annotated_file = f'blocks_detected_{timestamp}.jpg'
    raw_file = f'blocks_raw_{timestamp}.jpg'

    cv2.imwrite(annotated_file, annotated)
    cv2.imwrite(raw_file, frame)

    print(f"  Annotated: {annotated_file}")
    print(f"  Raw: {raw_file}")

    camera.release()

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

    if total > 0:
        print("\nNext steps:")
        print("  1. Check annotated image to verify detections")
        print("  2. Try approaching a block: python3 test_approach_smart.py")
        print("  3. Test IK pickup: python3 test_pickup_ik.py")


if __name__ == '__main__':
    main()
