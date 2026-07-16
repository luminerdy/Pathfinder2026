# Mecanum Drive Skill - Quick Reference

**Foundation skill - start here!**

---

## Quick Start

```bash
cd /home/robot/pathfinder/skills/mecanum_drive
python3 run_demo.py
```

**What you'll see:** three square patterns (standard square, mecanum square, diagonal wheel-pair square)

**Time:** 15-20 minutes

---

## Learning Outcomes

After this skill, you can:
- [OK] **Explain** why mecanum wheels have 45° rollers
- [OK] **Control** robot in all directions
- [OK] **Implement** movement patterns
- [OK] **Tune** speed limits for your floor
- [OK] **Debug** motor direction issues

**Assessment:** Drive square pattern successfully

---

## Files

| File | Level | Purpose |
|------|-------|---------|
| `SKILL.md` | All | Complete documentation (4 sections) |
| `run_demo.py` | 1 | One-click demo (no code changes) |
| `run_demo.py` `TEAM TUNING` section | 2 | Tune speeds and timing |
| `config.yaml` | Reference | Planned/reference values; not loaded by the demo |
| `README.md` | - | This file |

---

## Troubleshooting

**robot doesn't move:**
- Check battery: `python3 scripts/tools/check_battery.py`
- Test motors: `python3 scripts/tools/check_motors.py`

**Wrong direction:**
- Return to the Phase 1 individual-motor test.
- Re-check motor ports and wiring before changing code.

**Strafe is crooked:**
- Check wheel mounting (45° roller angle)
- Verify weight distribution (battery centered)

---

## Next Skills

After mastering mecanum drive, try:

- **Sonar Sensors** - Add obstacle detection
- **Robotic Arm** - Control servos and gripper
- **AprilTag Navigation** - Autonomous movement

---

*Master movement first - everything builds on this!*
