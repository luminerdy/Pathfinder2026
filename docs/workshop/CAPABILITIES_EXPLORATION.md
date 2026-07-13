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

Before changing a demo, read the [Demo Tuning Guide](CONFIG_GUIDE.md).

If something fails, use [Student troubleshooting](../support/TROUBLESHOOTING.md). Compare with another team first. Get help right away if the issue involves wiring, batteries, heat, smoke, broken parts, or `sudo` commands.

## Where To Run Commands

Run these commands while connected to the robot:

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
```

## Before Editing Or Updating Code

During this phase, teams should read code and may make small experiments. Keep the official `/home/robot/pathfinder` repo updateable, and do team edits in `/home/robot/team_code`.

- To edit safely, use [Team code workflow](../support/TEAM_CODE_WORKFLOW.md).
- If a facilitator says new GitHub code is available, use [Update robot code](../support/UPDATE_ROBOT_CODE.md).
- For SSH, copying files, terminals, and connection troubleshooting, use [robot connection reference](../support/ROBOT_CONNECTION_REFERENCE.md).

## Recommended Before Phase 3

Run these demos first. They cover the robot behaviors most teams need before attempting the course.

| Capability | Demo |
|------------|------|
| Mecanum drive | `python3 skills/mecanum_drive/run_demo.py` |
| Sonar sensors | `python3 skills/sonar_sensors/run_demo.py` |
| robotic arm | `python3 skills/robotic_arm/run_demo.py` |

## Recommended Demo Notes

### Mecanum Drive

This demo starts with a standard square pattern, then shows a mecanum square using sideways movement, then shows a diagonal square using diagonal wheel pairs.

**Caution:** The robot will move as soon as the demo starts. Put it on the floor, not on a table. Clear at least a 4-foot by 4-foot area so it can move about 2 feet in any direction.

```bash
python3 skills/mecanum_drive/run_demo.py
```

Watch which functions match each side of each square. If the movement is wrong, go back to Phase 1 motor wiring checks before changing code.

### Sonar Sensors

This demo shows the code that reads distance from the ultrasonic sensor and uses that distance to make simple decisions.

```bash
python3 skills/sonar_sensors/run_demo.py
```

Put your hand or a block in front of the robot and watch the distance readings change. Move the object closer and farther away so the team can see how sensor input becomes numbers in the code.

If the readings do not change, go back to Phase 1 sonar wiring checks before changing code.

### robotic arm pickup

This demo shows the code that moves the arm through a pickup-and-load sequence.

Only run this after Phase 1 servo checks passed. Place the robot on the floor and put one block directly in front of the gripper.

<img src="../images/robot/17_pickup_1.jpg" width="120" alt="block placed in front of robot gripper"> <img src="../images/robot/18_pickup_2.jpg" width="120" alt="arm lowering toward block"> <img src="../images/robot/19_pickup_3.jpg" width="120" alt="gripper approaching block"> <img src="../images/robot/20_pickup_4.jpg" width="120" alt="gripper holding block"> <img src="../images/robot/21_pickup_5.jpg" width="120" alt="arm lifting block"> <img src="../images/robot/22_pickup_6.jpg" width="120" alt="block loaded onto robot back">

```bash
python3 skills/robotic_arm/run_demo.py
```

If any movement is not correct, stop and re-check the arm assembly, block placement, and servo wiring before changing code.

## Manual Control Tools

Use these after the team has explored the individual capability scripts. Manual control is useful for practice, field scouting, and testing strategy, but it should not replace understanding the code that makes each capability work.

| Tool | Guide |
|------|-------|
| Web manual control | [Web Manual Control](WEB_MANUAL_CONTROL.md) |
| Gamepad remote control | [Gamepad Remote Control](GAMEPAD_REMOTE_CONTROL.md) |

## Optional If Time Allows

Use these after the recommended demos are working. These are useful for stronger autonomous runs, but teams should not get stuck here before they have a simple course strategy.

| Capability | Demo |
|------------|------|
| AprilTag navigation | `python3 skills/apriltag_navigation/run_demo.py` |
| Line following | `python3 skills/line_following/run_demo.py` |

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
- Camera hardware has been tested.
- Optional vision tools have been tested in event lighting if the team plans to use them.
- The team has a basic pickup or storage strategy.
- The team has selected a navigation strategy.

## Next Phase

Continue to [Phase 3: Course Challenge](COURSE_CHALLENGE.md).
