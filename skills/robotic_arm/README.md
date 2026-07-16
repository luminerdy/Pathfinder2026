# Robotic Arm Skill - Quick Reference

**Control a 5-servo robotic arm for manipulation tasks**

---

## Quick Start Levels

### Level 1A: Web UI (Visual, No Code)
```bash
cd /home/robot/pathfinder
python3 web/web_control.py
# Open browser: http://<ROBOT_IP>:8080
```
Move sliders, see arm respond!

### Level 1.5: Action Groups (Pre-Recorded)
```bash
python3 play_action.py shake_head
python3 play_action.py stand
```
Play back pre-recorded sequences.

### Level 2: Block Pickup Demo (Python)
```bash
python3 run_demo.py
```
Pick up a block and load it onto the robot's back.

---

## Learning Outcomes

After this skill, you can:
- Explain what each servo does (base, shoulder, elbow, wrist, gripper)
- Control servos via web UI or Python
- Run the block pickup demo
- Play action groups (pre-recorded sequences)
- Program pick-and-place sequences after positions are verified

---

## Hardware Reference

**5 Servos:**
1. Gripper (1550=closed, 2500=open)
3. Wrist (500-2500)
4. Elbow (500-2500)
5. Shoulder (500-2500)
6. Base (500-2500)

*Note: Servo 2 doesn't exist*

---

## Troubleshooting

**Servo doesn't move:**
- Check PWM range (500-2500)
- Verify servo ID (no servo 2!)

**Arm hits itself:**
- Stop with `Ctrl+C`
- Re-check servo wiring before running the pickup demo again
- Move through waypoints

**Gripper won't close:**
- Object too large?
- Try max force: `arm.grip(force=1.0)`

---

## Next Skills

- **Block Detection** - Find objects to grab
- **Autonomous Pickup** - Vision and arm integration

---

*Position, grab, manipulate.*
