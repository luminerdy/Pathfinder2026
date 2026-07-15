# Block Approach Development Notes

**Last updated:** July 15, 2026

These notes track active block detection and approach testing. This work is not ready for the participant event flow yet and should not be added to the workshop phase list until the approach and pickup behavior is reliable.

## Today's Progress

- Added a block detection viewer workflow that saves raw images, annotated images, and metadata.
- Added arm/camera controls to the block detection viewer.
- Added Red, Blue, and Yellow color checkboxes so one color or two colors can be isolated during tuning.
- Tuned red detection to reduce false positives on the foam floor.
- Tuned blue detection to reduce shadow ghosts.
- Added selected target logic:
  - filters weak detections,
  - ignores edge-touching detections,
  - merges nearby same-color detections,
  - scores candidates by confidence, center position, image position, size, and distance.
- Added a green selected-target overlay to the viewer.
- Throttled the viewer to reduce robot CPU load:
  - shared JPEG cache,
  - 5 FPS processing cap,
  - lower JPEG quality,
  - one processing lock for snapshots and live stream.
- Added `skills/block_approach/run_demo.py` as an approach-only test.
- Updated the approach demo so it moves the shoulder/camera angle during approach instead of treating `S5=1214` as a final stop.

## Current Calibration Notes

- `S5=995`: block at about 7 inches is visible low in the frame.
- `S5=1214`: block at about 12 inches is visible near the top of the frame.
- `S5=1214` should be treated as a close tracking or handoff view, not the final pickup-ready pose.
- If blocks are very close together, too much merge padding can combine separate blocks. Current merge padding is `8px`.
- The viewer looked stable with Blue-only selection and three close blue blocks.

## Current Test Commands

Viewer:

```bash
cd /home/robot/pathfinder
python3 skills/block_detection/viewer.py
```

Approach-only test:

```bash
cd /home/robot/pathfinder
python3 skills/block_approach/run_demo.py --color blue
```

## Tomorrow To-Dos

1. Test the current approach demo with a single blue block at several distances:
   - about 24 inches,
   - about 18 inches,
   - about 12 inches,
   - about 7 inches.
2. Confirm that the robot drives while moving the shoulder/camera angle, instead of stopping just to adjust the camera.
3. Tune the shoulder/camera tracking values:
   - `APPROACH_START_S5`,
   - `APPROACH_TOUCH_S5`,
   - `APPROACH_MAX_S5`,
   - `TARGET_VIEW_Y`,
   - `TOUCH_VIEW_Y_MIN`.
4. Determine the final pickup-ready camera/arm pose when the block is touching the front of the robot.
5. Decide whether the approach should:
   - keep pulsed stop-look-drive motion, or
   - move toward a slow continuous drive while camera angle changes.
6. Do not add this to the event participant flow yet.

## Known Risks

- The block viewer can still stress the robot if multiple browser tabs are open. Use one viewer tab and stop the program with `Ctrl+C` when finished.
- Low battery may make motors hum without moving. Use a fresh battery before judging approach tuning.
- The approach code currently does not close the claw. Pickup should stay separate until approach is reliable.
