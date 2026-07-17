# Line Following - Quick Reference

**Follow a lime green tape line using camera + mecanum drive**

## Quick Start

### Test detection only (drive motors do not move):
```bash
cd /home/robot/pathfinder
python3 skills/line_following/test_line_detect.py
```

### Follow the line:
```bash
cd /home/robot/pathfinder
python3 skills/line_following/run_demo.py
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
2. Measure three thin horizontal scan strips in the camera image
3. HSV threshold for lime green (H=35-85)
4. Use the largest connected green region in each strip
5. Search until the far strip confirms that the line is ahead
6. Strafe to stay centered over the nearest visible line
7. Add a small turn correction from the near-to-far line angle
8. Stop after three frames without a line

## Key Parameters
- HSV: [35,50,50] to [85,255,255] (lime green)
- Strafe gain: 0.22
- Turn gain: 0.08
- Forward speed: 38
- Minimum strafe: 18
- Maximum strafe: 28
- Scan strips: rows 240-280, 340-380, and 420-465
- Search turn power: 40
- Lost-line confirmation: 3 frames

## Why Lime Green?
- Far from red (H=0-10), blue (H=100-130), yellow (H=20-40)
- High contrast on gray floor
- No conflict with block detection

---
*Follow the line, stay on track!*
