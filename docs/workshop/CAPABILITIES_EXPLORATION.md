# Capabilities Exploration

Capabilities Exploration is where teams learn what the robot can do before they attempt the course.

## Goal

Run short demos, observe behavior, and tune only what is needed. Each capability should be understood well enough that the team can reuse it during the Course Challenge.

## Recommended Order

| Step | Capability | Demo |
|------|------------|------|
| D1 | Mecanum drive | `python3 skills/mecanum_drive/run_demo.py` |
| D2 | Sonar sensors | `python3 skills/sonar_sensors/run_demo.py` |
| D3 | robotic arm | `python3 skills/robotic_arm/run_demo.py` |
| D4 | Camera vision | `python3 skills/camera_vision/test_camera.py` |
| E2 | AprilTag navigation | `python3 skills/apriltag_navigation/run_demo.py` |
| E3 | Block detection | `python3 skills/block_detection/run_demo.py` |
| E4 | Visual servoing | `python3 skills/visual_servoing/run_demo.py` |
| E5 | Autonomous pickup | `python3 skills/autonomous_pickup/run_demo.py` |
| E6 | Line following | `python3 skills/line_following/run_demo.py` |

## Manual Control

The web control interface is useful for driving, viewing camera output, checking battery, and moving the arm.

```bash
python3 web/web_control.py
```

Open `http://<ROBOT_IP>:8080` from the Pi 500.

## Team Notes

For each capability, teams should record:

- What worked immediately
- What needed tuning
- What failed
- Which settings changed
- Whether the capability is reliable enough for the course

## Ready To Move On

The team is ready for the Course Challenge when:

- The robot can drive forward, strafe, and turn.
- The team can stop the robot quickly.
- Battery checks are routine.
- Camera and block detection have been tested in event lighting.
- The team has a basic pickup or storage strategy.
- The team has selected a navigation strategy.
