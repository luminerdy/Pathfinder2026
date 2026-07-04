# Capabilities Exploration

**Phase 2 of 3**

Capabilities Exploration is where teams learn how the robot works before they attempt the course.

## Why This Phase Matters

The goal is to understand the code that makes the robot move, sense, see, and use its arm.

Do not treat the demos as magic commands. Run them, observe what the robot does, then open the code and connect the behavior to the file that caused it. That understanding is what lets the team choose a simple strategy for Phase 3.

By the end of this phase, the team should know:

- Which scripts make the robot drive.
- Which scripts read sensors.
- Which scripts use the camera.
- Which scripts move the arm.
- Which settings might need small tuning.

Before editing tuning files, read [Configuration Guide](CONFIG_GUIDE.md).

If something fails, use [Student Troubleshooting](TROUBLESHOOTING.md). Compare with another team first. Get help right away if the issue involves wiring, batteries, heat, smoke, broken parts, or `sudo` commands.

## Where To Run Commands

Run these commands while connected to the robot:

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
```

## Step 0: Manual Control

The web control interface is useful for driving, viewing camera output, checking battery, and moving the arm.

Start here before running the capability demos. Manual control gives the team a quick way to confirm that the robot is awake, connected, and responding.

```bash
python3 web/web_control.py
```

Open `http://<ROBOT_IP>:8080` from the Pi 500.

If a movement button does not respond, check the drive status message under the buttons and confirm the robot battery is not low.

## Recommended Before Phase 3

Run these demos first. They cover the robot behaviors most teams need before attempting the course.

| Step | Capability | Demo |
|------|------------|------|
| D1 | Mecanum drive | `python3 skills/mecanum_drive/run_demo.py` |
| D2 | Sonar sensors | `python3 skills/sonar_sensors/run_demo.py` |
| D3 | robotic arm | `python3 skills/robotic_arm/run_demo.py` |
| D4 | Camera vision | `python3 skills/camera_vision/test_camera.py` |
| E3 | Block detection | `python3 skills/block_detection/run_demo.py` |

## Recommended Demo Notes

### D1: Mecanum Drive

This demo shows the code that drives forward, backward, strafes, rotates, moves diagonally, and combines moves into a square pattern.

**Caution:** The robot will move as soon as the demo starts. Put it on the floor, not on a table. Clear at least a 4-foot by 4-foot area so it can move about 2 feet in any direction.

```bash
python3 skills/mecanum_drive/run_demo.py
```

Watch which functions match each movement. If the movement is wrong, go back to Phase 1 motor wiring checks before changing code.

### D3: robotic arm pickup

This demo shows the code that moves the arm through a pickup-and-load sequence.

Only run this after Phase 1 servo checks passed. Place the robot on the floor and put one block directly in front of the gripper.

<img src="../images/robot/17_pickup_1.jpg" width="120" alt="block placed in front of robot gripper"> <img src="../images/robot/18_pickup_2.jpg" width="120" alt="arm lowering toward block"> <img src="../images/robot/19_pickup_3.jpg" width="120" alt="gripper approaching block"> <img src="../images/robot/20_pickup_4.jpg" width="120" alt="gripper holding block"> <img src="../images/robot/21_pickup_5.jpg" width="120" alt="arm lifting block"> <img src="../images/robot/22_pickup_6.jpg" width="120" alt="block loaded onto robot back">

```bash
python3 skills/robotic_arm/run_demo.py
```

If any movement is not correct, stop and re-check the arm assembly, block placement, and servo wiring before changing code.

## Optional If Time Allows

Use these after the recommended demos are working. These are useful for stronger autonomous runs, but teams should not get stuck here before they have a simple course strategy.

| Step | Capability | Demo |
|------|------------|------|
| E2 | AprilTag navigation | `python3 skills/apriltag_navigation/run_demo.py` |
| E4 | Visual servoing | `python3 skills/visual_servoing/run_demo.py` |
| E5 | Autonomous pickup | `python3 skills/autonomous_pickup/run_demo.py` |
| E6 | Line following | `python3 skills/line_following/run_demo.py` |

## Team Notes

For each capability, teams should record:

- What worked immediately
- What needed tuning
- What failed
- Which settings changed
- Whether the capability is reliable enough for the course
- Which capability the team will actually use in the course

## Phase 2 Complete

The team is ready for Phase 3: Course Challenge when:

- The robot can drive forward, strafe, and turn.
- The team can stop the robot quickly.
- Battery checks are routine.
- Camera and block detection have been tested in event lighting.
- The team has a basic pickup or storage strategy.
- The team has selected a navigation strategy.
