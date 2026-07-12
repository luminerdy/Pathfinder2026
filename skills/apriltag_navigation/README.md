# AprilTag Navigation (E3) - Quick Reference

**Quick Reference Card**

---

## Choose Your Level

###  Level 1: Just Run It (Beginners)
**File:** `run_demo.py`
**What:** Pre-built demo, no code changes needed
**Time:** 5 minutes

```bash
python3 run_demo.py
```

### Level 2: Template Configuration Reference
**File:** `config.yaml`
**What:** Values used by the learning template, not by `run_demo.py`
**Time:** 15 minutes

Use this file only while completing `apriltag_nav_template.py`. To change the one-click demo, edit the target and movement values in `run_demo.py`.

###  Level 3: Fill in the Blanks (Learning to Code)
**File:** `apriltag_nav_template.py`
**What:** Complete the TODO sections
**Time:** 30-45 minutes

1. Read `SKILL.md` Implementation Guide
2. Open `apriltag_nav_template.py`
3. Search for `???` and fill in your code
4. Run and test

## Quick Troubleshooting

**Problem:** "No module named 'pupil_apriltags'"
**Solution:** `pip3 install pupil-apriltags`

**Problem:** "No tag detected"
**Solution:**
- Use the print-ready tags in [../../apriltags/README.md](../../apriltags/README.md)
- Ensure tag is flat, well-lit, in camera view
- Start 3-5 feet away

**Problem:** "robot doesn't move"
**Solution:**
- Check battery: `python3 scripts/tools/check_battery.py`
- Test motors: `python3 scripts/tools/check_motors.py`

**Problem:** "ImportError: cannot import name 'get_board'"
**Solution:** Run from correct directory or fix Python path

---

## Files

| File | Level | Purpose |
|------|-------|---------|
| `SKILL.md` | All | Complete documentation (4 sections) |
| `run_demo.py` | 1 | One-click demo |
| `config.yaml` | 2 | Learning-template configuration; not loaded by `run_demo.py` |
| `apriltag_nav_template.py` | 3 | Learning template |
| `README.md` | - | This file |

---

## Next Skills

After mastering AprilTag Navigation, try:

- **Block Detection** - Find colored blocks using computer vision
- **Visual Servoing** - Approach objects using camera feedback
- **Multi-Tag Tour** - Visit multiple tags in sequence
- **Autonomous Pickup** - Navigate + detect + grab blocks

---

*Questions? Read SKILL.md or ask a mentor!*
