# A1: Pi 500 OS Build

**Purpose:** Create the SD card image for the Raspberry Pi 500 (team control hub)

**OS:** Raspberry Pi OS (Debian 13.5 Trixie, 64-bit) — tested on Pi 500, June 2026

The Pi 500 is your **command center** — you'll use it to write code, SSH into the robot, monitor camera feeds, and run all workshop scripts. The robot runs headless; you control everything from here.

---

## Materials Needed

- Full setup BOM: [BILL_OF_MATERIALS.md](BILL_OF_MATERIALS.md)
- Raspberry Pi 500 kit (keyboard computer)
- microSD card (32GB+ recommended)
- USB mouse
- Portable monitor + Micro HDMI to HDMI adapter
- Power supply (USB-C, included with Pi 500 kit)
- Another computer with internet (for imaging the SD card)

## Step 1: Download Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your computer
2. Insert microSD card into your computer
3. Open Raspberry Pi Imager
4. Choose OS: **Raspberry Pi OS (64-bit)** — Desktop version
5. Choose Storage: Select your microSD card
6. Click the **gear icon** (⚙️) for advanced settings:
   - Set device name / hostname: `pihub`
   - Enable SSH (password authentication)
   - Set username: `pi500`
   - Set password: (your choice, document it!)
   - Configure WiFi: Enter your workshop network SSID and password
   - Set locale: Your timezone
7. Click **Write** and wait for completion

Use `pihub` and `pi500` consistently for the Pi 500. The robot uses the `robot` account separately.

## Step 2: First Boot

1. Insert SD card into Pi 500
2. Connect monitor via Micro HDMI adapter
3. Connect USB mouse
4. Plug in power — Pi 500 will boot to desktop

## Step 3: Verify Setup

Open a terminal (Ctrl+Alt+T) and verify:

```bash
# Check WiFi
ping -c 3 google.com
# Should succeed

# Check Python
python3 --version
# Should show Python 3.11+

# Check SSH is running
sudo systemctl status ssh
# Should show: active (running)
```

## Step 4: Install Local Workshop Docs

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Recommended: install git so the Pi 500 can keep a local copy of the workshop docs
sudo apt install -y git

# Recommended: clone the workshop repository for local docs, checklists, and examples
cd ~
git clone https://github.com/luminerdy/Pathfinder2026.git
cd Pathfinder2026
```

The local clone is useful for reading docs without switching back to GitHub. It is not required to run robot code. Robot code runs on the robot through VS Code Remote SSH.

The Pi 500 does not need OpenCV, AprilTag, or NumPy for the normal event workflow. Install vision packages on the Pi 500 only if you plan to run separate Pi 500-side camera or AprilTag experiments.

## Step 5: Note Your IP Address

```bash
hostname -I
# Example: 10.10.10.141
```

Write this down for troubleshooting. The robot IP address is the important address for event connections.

## Step 6: Install Visual Studio Code

Use the terminal install for the event build. It is repeatable and easy to verify:

```bash
sudo apt-get install -y code
```

If that command cannot find `code`, use **Raspberry Pi menu -> Preferences -> Recommended Software**, check **Visual Studio Code**, then click **Apply**.

## Step 7: Configure VSCode Remote SSH to robot

VSCode Remote SSH lets you write and run robot code directly on the robot from the Pi 500 — no need to install a code editor on the robot.

**Install extensions:**
1. Open Visual Studio Code
2. Press `Ctrl+Shift+X` to open Extensions
3. Search for and install:
   - **Remote - SSH** (Microsoft)
   - **Python** (Microsoft)

**Connect to your robot:**
1. Press `F1` → type `Remote-SSH: Connect to Host` → select it
2. Enter: `robot@<ROBOT_IP>` using the IP address assigned to your team's robot
3. Enter the robot password when prompted
4. VSCode installs its server component on the robot automatically (first time only, ~1 minute)
5. Select **Open Folder** → navigate to `/home/robot/pathfinder`

You can now edit, run, and debug robot code directly from the Pi 500.

> **robot IP:** The event will use IP addresses for robot connections. Get your team's robot IP address from the facilitator or the event IP assignment sheet.

---

## What's on the Pi 500

After setup, your Pi 500 has:

| Item | Purpose |
|------|---------|
| Raspberry Pi OS Desktop | Visual interface for coding and monitoring |
| Python 3 | Basic scripting and tools |
| SSH client | Connect to robot remotely |
| Visual Studio Code + Remote SSH | Write and run robot code directly on the robot |
| Pathfinder2026 repo | Local copy of workshop docs, checklists, and examples |
| Terminal | Command line for SSH, git, python |

## What's NOT on the Pi 500

- No motor/servo drivers (those are on the robot)
- No hardware SDK (robot only)
- No camera access to robot camera (use SSH + web interface)
- No OpenCV, AprilTag, or NumPy required unless doing optional Pi 500-side vision testing

The Pi 500 is the **brain**. The robot is the **body**. They talk over WiFi.

---

## Pre-Built Option

For workshops, the facilitator can pre-image all SD cards to save time:

1. Build one Pi 500 image following steps above
2. Use Raspberry Pi Imager to clone the SD card
3. Update each clone's device label if needed and record the assigned IP address
4. Pre-connect to workshop WiFi

This skips 15-20 minutes of setup per team.

---

**Next:** [C1: Pi 500 Setup](C1_PI500_SETUP.md) (connect to monitor and configure)
