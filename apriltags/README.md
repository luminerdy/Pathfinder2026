# Pathfinder2026 AprilTags

Use tag36h11 IDs 582-585 for the four field areas.

| Area | Tag | Field Location |
|------|-----|----------------|
| 1 | 582 | Bottom right - start and blue blocks |
| 2 | 583 | Top right - red blocks |
| 3 | 584 | Top left - yellow blocks |
| 4 | 585 | Bottom left - delivery zone |

## Print Files

Use the [combined four-page PDF](../output/pdf/Pathfinder2026_AprilTags_582-585_10in.pdf), or choose an individual tag PDF from the same folder.

High-resolution PNGs are under `apriltags/print/`.

## Required Print Settings

- Paper: 13 x 19 inches or larger
- Scale: Actual Size or 100%
- Do not select Fit, Shrink, or Scale to Page
- Black and white printing is correct
- Keep the complete white border around the tag

The AprilTag measurement used by the robot is the outside edge of the black square. That black square must measure exactly 10 inches after printing. The complete image is 12.5 inches because it includes the required white quiet zone.

Measure the 10-inch verification line and the outside black square before printing the remaining copies.

## Mounting And Testing

- Mount each tag flat on rigid material.
- Keep the white quiet zone visible and unobstructed.
- Avoid glossy lamination that creates glare.
- Keep all tags upright and at a consistent height.
- Test each printed tag with the event robot under event lighting.

Run the camera test first, then the optional AprilTag demo:

```bash
cd /home/robot/pathfinder
python3 skills/camera_vision/test_camera.py
python3 skills/apriltag_navigation/run_demo.py
```

The one-click navigation demo targets tag 582.

## Source And Regeneration

The 10 x 10 source bitmaps under `apriltags/source/` come from the [AprilRobotics apriltag-imgs repository](https://github.com/AprilRobotics/apriltag-imgs/tree/master/tag36h11).

Regenerate the print files with a Python environment containing Pillow and ReportLab:

```bash
python3 scripts/setup/generate_apriltags.py
```
