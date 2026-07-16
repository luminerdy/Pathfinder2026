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
- Raised block detector `MAX_AREA` from `5000` to `12000` because a real close blue cube was being rejected at about `7109px` contour area.
- Updated the approach demo to stop at a camera handoff point before the block drops out of view.
- Added target locking so the approach demo does not jump to a different same-color block after movement starts.
- Added approach-only candidate limits:
  - ignore targets close to the camera edge,
  - ignore targets farther than about `45cm`.
- Tuned the approach strafe:
  - `STRAFE_POWER = 42`,
  - `STRAFE_PULSE_SECONDS = 0.35`,
  - `X_TOLERANCE_PX = 60`.
- Added a centering-stall stop so the robot does not keep pulsing if the target offset is not improving.
- Added `skills/block_pickup/run_demo.py` as a pickup-only test that uses the tested `Arm.pickup_front()` sequence.
- Ran `skills/block_approach_pickup/run_demo.py --color blue --yes` on the robot. Approach reached handoff and pickup completed.

## Current Calibration Notes

- `S5=995`: block at about 7 inches is visible low in the frame.
- `S5=1214`: block at about 12 inches is visible near the top of the frame.
- `S5=1214` should be treated as a close tracking or handoff view, not the final pickup-ready pose.
- July 15 test: the robot tracked a blue block down to about `12cm`, `S5=1230`, then one more forward pulse pushed the block out of view. The current handoff stop is designed to prevent that last bad pulse.
- July 15 test: after the robot had moved, the selected blue block was near the left image edge. The approach demo now refuses to drive from that unsafe view instead of chasing a different far blue block.
- July 15 retest: a manual strafe-left correction moved a left-edge blue block toward center. The approach demo's original `STRAFE_POWER = 32` was too weak at about `7.7V`; `42` worked better.
- July 15 successful run: the robot locked a blue block, centered it, drove forward, adjusted camera angle, and stopped with `Result: SUCCESS`, `Reason: reached`.
- Successful final camera view after the run showed the selected blue block still visible at about `17cm`, `offset=+43`.
- July 15 pickup-only test: ran `Arm.pickup_front()` from the approach handoff position. The post-pickup camera snapshot showed no blue block selected on the floor in front of the robot. This is a positive sign, but a human visual check is still needed to confirm the block is held in the claw.
- July 15 combined test at about `7.62V`: approach locked a blue target, drove to handoff, reported `Approach result: SUCCESS`, then ran pickup and reported `Pickup result: SUCCESS`.
- The post-combined-test camera snapshot still saw other blue blocks in the field, so it cannot prove the target block was held in the claw. Human visual confirmation is still required.
- Later July 15 run at `7.43V` showed the tracker switching from the near blue block to a farther blue block: distance jumped from about `17cm` to about `39cm` while the target moved higher in the image.
- Updated target lock behavior to follow the last accepted target, reject sudden farther/higher same-color detections, and use a stricter final pickup handoff tolerance of `25px`.
- Added a fine-strafe correction near handoff so pickup alignment can be tighter than general approach alignment.
- July 15 run at `8.15V` drove well and fine-strafed correctly, but missed the handoff. The log showed a good pickup stop candidate at about `14cm`, `offset=+3`, `y=302`; the robot then drove one more forward pulse, reached `12cm`, and lost the target.
- Updated handoff to stop when centered within `25px`, at about `17cm` or closer, and `y >= 300`.
- July 15 settle test showed approach still drove one pulse too far. The missed stop frame was about `17cm`, `offset=+19`, `y=345`, so the distance handoff was moved back to `170mm` while keeping `y >= 300`.
- Photos after the run showed the block centered well, about 5 inches from the robot, but still forward of the claw pickup geometry.
- Added a tiny forward settle in the combined approach-and-pickup script before pickup: `24%` power for `0.12s`, with motors stopped before pickup begins.
- July 15 settle retest at about `7.97V`: approach stopped at about `14cm`, `offset=+18`, `y=345`, ran the forward settle, then pickup reported `SUCCESS`.
- Current handoff values are `HANDOFF_DISTANCE_MM = 170` and `HANDOFF_VIEW_Y_MIN = 300`.
- Current pickup alignment tolerance is `PICKUP_X_TOLERANCE_PX = 25`.
- If blocks are very close together, too much merge padding can combine separate blocks. Current merge padding is `8px`.
- The viewer looked stable with Blue-only selection and three close blue blocks.
- Added a combined approach-and-pickup script. It only runs pickup if approach reports success.

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

Pickup-only test:

```bash
cd /home/robot/pathfinder
python3 skills/block_pickup/run_demo.py
```

Approach-and-pickup test:

```bash
cd /home/robot/pathfinder
python3 skills/block_approach_pickup/run_demo.py --color blue
```

Skip final settle if needed:

```bash
python3 skills/block_approach_pickup/run_demo.py --color blue --no-settle
```

## Next To-Dos

1. Retest the current approach demo with a single blue block at several starting distances:
   - about 24 inches,
   - about 18 inches,
   - about 12 inches,
   - about 7 inches.
2. Repeat the successful run with red and yellow blocks to confirm color-specific behavior.
3. Have a human confirm whether the block is held in the claw after `skills/block_approach_pickup/run_demo.py --color blue`.
4. If blue pickup is confirmed, repeat the combined test with red and yellow blocks.
5. Decide whether the approach should:
   - keep pulsed stop-look-drive motion, or
   - move toward a slow continuous drive while camera angle changes.
6. Do not add this to the event participant flow yet.

## Known Risks

- The block viewer can still stress the robot if multiple browser tabs are open. Use one viewer tab and stop the program with `Ctrl+C` when finished.
- Low battery may make motors hum without moving. Use a fresh battery before judging approach tuning.
- The approach code currently does not close the claw. Pickup should stay separate until approach is reliable.
