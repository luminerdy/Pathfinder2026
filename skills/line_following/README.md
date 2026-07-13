# Line Following - Quick Reference

**Follow a lime green tape line using camera + mecanum drive**

## Quick Start

### Test detection only (no driving):
```bash
python3 test_line_detect.py
```

### Follow the line:
```bash
python3 run_demo.py
```

## API
```python
from skills.line_following.line_follower import LineFollower

follower = LineFollower()
result = follower.follow(timeout=30)
# result['success'], result['reason'], result['frames']
follower.cleanup()

# Detection only (no driving):
detection = follower.detect_line(frame)
# detection['found'], detection['cx'], detection['error'], detection['ratio']
```

## How It Works
1. Camera points down (arm repositioned)
2. Crop to the visible tape area (ROI)
3. HSV threshold for lime green (H=35-85)
4. Split the line into near, middle, and far bands
5. Strafe to stay centered over the near line
6. Add a small turn correction for curves
7. Stop when line ends (green ratio drops)

## Key Parameters
- HSV: [35,50,50] to [85,255,255] (lime green)
- Strafe gain: 0.14
- Turn gain: 0.08
- Forward speed: 38
- ROI: Top 65% of frame

## Why Lime Green?
- Far from red (H=0-10), blue (H=100-130), yellow (H=20-40)
- High contrast on gray floor
- No conflict with block detection

---
*Follow the line, stay on track!*
