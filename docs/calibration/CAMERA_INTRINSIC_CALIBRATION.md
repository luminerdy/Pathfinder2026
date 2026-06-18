# Camera Intrinsic Calibration

## Why This Matters

The robot uses `fx=500` as an estimated focal length. The real value is likely 600–900 depending on the lens.
This estimate causes ~50% error in AprilTag distance calculations — the robot thinks a tag is 40cm away
when it's actually 20cm, or vice versa. Real calibration eliminates this.

## What You Need

- A printed 8x6 square checkerboard (7x5 inner corners)
- The robot with camera mounted in its normal position
- ~5 minutes

Tip: Mount the checkerboard flat on a clipboard or book so it stays rigid.

## Running the Calibration

Run on the robot (SSH or VSCode Remote):

```bash
cd Pathfinder2026
python3 scripts/calibration/calibrate_camera_intrinsics.py
```

The script runs headless — no display or screen needed.

### What to Do During Capture

The script auto-captures every 2 seconds when it detects the board. After each capture, move the board
to a new position. Aim for variety:

| Position Type | Why |
|--------------|-----|
| Center, straight-on | Baseline |
| Tilted left/right ~30° | Constrains fx |
| Tilted up/down ~30° | Constrains fy |
| Close (~20cm) | High pixel density |
| Far (~60cm) | Low pixel density |
| Board in frame corners | Captures lens edge distortion |

20 captures total. The script stops and calibrates automatically.

## Output

`lib/camera_calibration.npz` — contains `mtx_array` (camera matrix) and `dist_array` (distortion coefficients).

**This file is gitignored** (`.npz` files are excluded). Copy it to any robot that uses the same camera.

## Using the Calibration

```python
with Robot(calibration_path='lib/camera_calibration.npz') as robot:
    ...

# Verify it loaded:
robot.status()  # prints: Camera cal: fx=XXX fy=XXX
```

## Interpreting Results

| Reprojection Error | Quality |
|-------------------|---------|
| < 0.5 px | Excellent |
| 0.5 – 1.0 px | Acceptable |
| > 1.0 px | Re-run with more varied angles |

## Notes

- The Pi 4 camera has noticeable fisheye/barrel distortion — calibration also corrects this
- Calibration is per-camera-lens. If you swap the camera module, recalibrate
- Both buddy1 and buddy2 should be calibrated separately if their camera modules differ
- The checkerboard on the competition field (8x6 squares, 7x5 inner corners) works as the calibration target
