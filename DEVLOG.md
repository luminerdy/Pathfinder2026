# PathfinderV2 — Dev Log

Ongoing record of daily work, discussions, and accomplishments. Newest entries at top.

---

## 2026-05-15

### Agent Doc
- Reviewed README.md; identified gaps in AGENT_CODING_REFERENCE.md
- Added to camera specs: `fps: 30`, `apriltag_family: "tag36h11"`
- Added `runtime_competition_min: "30-45"` to battery section (distinct from light-load 80 min)
- Added **Section 0: Capabilities at a Glance** — new top-level JSON block covering locomotion, manipulation, sensing, navigation, autonomy, and competition context; gives agents orientation before the detailed API
- Pushed all updates to GitHub

### Project Management
- Created full project backlog (11 tasks) covering agent doc work and codebase cleanup
- Saved backlog to persistent memory so it survives across sessions

---

## 2026-05-14

### Agent Doc (v1 — initial build)
- Designed format: hybrid Markdown/JSON — section headers in MD, all API/data in compact JSON blocks, patterns as Python examples
- Decision: single flat file in repo root (`AGENT_CODING_REFERENCE.md`) — humans browse GitHub, agents fetch raw URL
- Built all 12 sections from scratch:
  - Fleet, Entry Point, Drive, Arm, Camera, Sonar, Battery
  - 4 skills: bump_grab, StrafeNavigator, color_delivery, bin_collect
  - 6 canonical code patterns (minimal robot, stop-scan-decide, sonar filtering, bump-grab+deliver, multi-block, battery check)
  - Operating Envelope, Do-Not table, Imports, Open Issues
- Pushed v1 to GitHub

---

## 2026-04-25 (approximate — Day 22 area)

### buddy2 Setup
- buddy2 confirmed running Debian 13.4 Trixie (not Bookworm), Python 3.13.5
- Discovered: `i2cdetect` does not show motor board at 0x7A on buddy2 — confirmed normal; use Python battery read test instead
- Updated `A1_ROBOT_PI_OS_BUILD.md` for Trixie and pushed to GitHub

### Open Priorities Identified
- Camera calibration: `fx=500` is hardcoded estimate across 9 files; real `.npz` from V1 needed (top priority)
- `competition.py` refactor needed (553 lines, still on old `auto_pickup` pattern)
- 44 files have `sys.path.insert()` hacks; need `setup.py`
- Dead skills to remove: `auto_pickup`, `block_approach`, `block_pursue` (~1,400 lines)
- Workshop starter templates need updating to Robot pattern

---

## Earlier Work (Days 1–22, through ~April 24, 2026)

See git log for detailed history. Key milestones:

- **Day 2** — Fixed motor silence bug: missing `dtparam=uart0=on` in `/boot/firmware/config.txt`
- **Day 9** — Board auto-detect fix: "must be ALL or NOTHING" — 37-file change
- **Day 16** — Major architecture refactor: single `Robot` class owns all hardware; all skills accept Robot instance
- **Proven** — 8/8 AprilTag tour at 7.86V; bump-and-grab insight: camera on arm, block vanishing = contact signal
- **Decommissioned PathfinderV2 Pi 5** — 25W draw too high for batteries; switched to Pi 4 (15W)
- **Workshop docs complete** — competition rules, facilitator guide, BOM, field layout, scoring, SD card guide, Pi 500 setup, OpenClaw setup, VSCode Remote SSH setup
