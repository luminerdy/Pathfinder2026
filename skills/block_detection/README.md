# Block Detection - Quick Reference

**Detect colored blocks using HSV color filtering**

## Quick Start

### Block detection viewer

Use this first when tuning block identification. It shows live annotated camera output, lets you move the arm/camera servos, and saves raw/annotated snapshots with arm-position metadata.

This viewer does not drive the robot base. Keep hands clear before moving the arm.

Use the Red, Blue, and Yellow checkboxes to isolate one color or any two-color combination while tuning.

The viewer also highlights one selected pickup target in green. This is the block the robot would choose first based on confidence, distance, image position, and whether the box is safely away from the image edge.

Nearby same-color boxes are merged before target selection using a small padding. This reduces flicker when one cube is briefly split into multiple contours by glare or shadows, while avoiding merging separate blocks that are close together.

The viewer ignores detections above the visible field floor. This keeps bright objects outside the field perimeter from being labeled as blocks.

```bash
cd /home/robot/pathfinder
python3 skills/block_detection/viewer.py
```

Open from the Pi 500 browser:

```text
http://<ROBOT_IP>:8081
```

Keep one viewer tab open while tuning, then stop the program with `Ctrl+C` when finished. The viewer throttles camera processing to reduce robot CPU load.

Snapshots are saved in:

```text
/home/robot/pathfinder/block_detection_captures
```

Each saved snapshot includes:

- `block_raw_*.jpg`: original camera frame
- `block_annotated_*.jpg`: frame with detection boxes and tuning guides
- `block_metadata_*.json`: detections, raw detection count, selected target, selected color filters, and current servo positions

### Single-frame demo

```bash
cd /home/robot/pathfinder
python3 skills/block_detect.py
```
Place colored block in view, see detection output.

## API
```python
from skills.block_detect import BlockDetector

detector = BlockDetector()
blocks = detector.detect(frame)              # All colors
blocks = detector.detect(frame, ['red'])     # Red only
blocks = detector.detect(frame, field_min_y_ratio=0.45) # Ignore above-field objects
nearest = detector.find_nearest(frame, 'red') # Nearest red
merged = detector.merge_close_detections(blocks) # Reduce split boxes
target = detector.select_pickup_target(merged)   # Best pickup target

# Each block has:
# .color, .center_x, .center_y, .width, .height
# .offset_from_center, .estimated_distance_mm, .confidence
```

## Target Selection

`merge_close_detections()` combines nearby same-color boxes before target selection. `select_pickup_target()` then ignores weak and edge-touching detections, then scores the remaining blocks. A good target is confident, reasonably large, lower in the camera view, and closer to the center line.

## Color Ranges (HSV)
- Red: H=0-8 + H=172-180, with higher saturation/value filtering to reduce false positives
- Blue: H=100-130, with moderate saturation/value filtering to reduce shadow ghosts
- Yellow: H=20-40

## Pipeline
Camera -> HSV -> Threshold -> Morphology -> Contours -> Filter -> Detect

## Next Skills
- Block approach: approach the selected target without pickup
- Visual servoing: drive toward detected blocks
- Autonomous pickup: detect, drive, and grab

---
*Find the blocks!*
