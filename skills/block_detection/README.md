# Block Detection - Quick Reference

**Detect colored blocks using HSV color filtering**

## Quick Start

### Block detection viewer

Use this first when tuning block identification. It shows live annotated camera output, lets you move the arm/camera servos, and saves raw/annotated snapshots with arm-position metadata.

This viewer does not drive the robot base. Keep hands clear before moving the arm.

```bash
cd /home/robot/pathfinder
python3 skills/block_detection/viewer.py
```

Open from the Pi 500 browser:

```text
http://<ROBOT_IP>:8081
```

Snapshots are saved in:

```text
/home/robot/pathfinder/block_detection_captures
```

Each saved snapshot includes:

- `block_raw_*.jpg`: original camera frame
- `block_annotated_*.jpg`: frame with detection boxes and tuning guides
- `block_metadata_*.json`: detections and current servo positions

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
nearest = detector.find_nearest(frame, 'red') # Nearest red

# Each block has:
# .color, .center_x, .center_y, .width, .height
# .offset_from_center, .estimated_distance_mm, .confidence
```

## Color Ranges (HSV)
- Red: H=0-8 + H=172-180, with higher saturation/value filtering to reduce false positives
- Blue: H=100-130
- Yellow: H=20-40

## Pipeline
Camera -> HSV -> Threshold -> Morphology -> Contours -> Filter -> Detect

## Next Skills
- Visual servoing: drive toward detected blocks
- Autonomous pickup: detect, drive, and grab

---
*Find the blocks!*
