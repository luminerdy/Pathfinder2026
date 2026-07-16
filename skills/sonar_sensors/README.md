# Sonar Sensors Skill - Quick Reference

**Learn distance sensing and obstacle detection**

---

## Quick Start

```bash
cd /home/robot/pathfinder/skills/sonar_sensors
python3 run_demo.py
```

**What you'll see:** 6 sonar demos (distance, filtering, detection, zones, safe movement, avoidance)

**Time:** 15-20 minutes

---

## Learning Outcomes

After this skill, you can:
- [OK] **Explain** how ultrasonic sensors work (sound echo timing)
- [OK] **Read** distance values in centimeters
- [OK] **Implement** threshold logic (stop/slow/go)
- [OK] **Use** RGB LEDs for visual feedback
- [OK] **Filter** noisy sensor data (median, average)

**Assessment:** robot stops before hitting obstacle, RGB shows correct colors

---

## Files

| File | Level | Purpose |
|------|-------|---------|
| `SKILL.md` | All | Complete documentation (4 sections) |
| `run_demo.py` | 1 | One-click 6-demo showcase |
| `run_demo.py` `TEAM TUNING` section | 2 | Tune thresholds, speed, and timing |
| `config.yaml` | Reference | Planned/reference values; not loaded by the demo |
| `README.md` | - | This file |

---

## Troubleshooting

**Readings always 400cm:**
- Normal if no object (sensor sees "infinity")
- Object too far away (>4 meters)

**Noisy readings:**
- Use the filtered-reading part of the demo instead of one sample.
- Re-check sensor mounting and nearby ultrasonic interference.

**RGB doesn't light:**
- Check the sonar cable connection.
- Return to the Phase 1 sonar test before changing code.

---

## Next Skills

- **Robotic Arm** - Add manipulation
- **AprilTag Navigation** + Sonar = Safe autonomous navigation
- **Visual Servoing** - Camera + Sonar for precise approach

---

*Safety first - let sensors guide the way!*
