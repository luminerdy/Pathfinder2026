# SD Card Images — Pre-Built for Workshop

**Purpose:** Pre-image all SD cards before workshop day so teams start in minutes, not hours.

Two images needed per team: one for the Pi 500 (control hub), one for the robot (Pi 4).

**Scale:** 49 teams = 49 robot SD cards + 49 Pi 500 SD cards = **98 cards total.**

---

## Why Pre-Build?

| Without pre-built | With pre-built |
|-------------------|----------------|
| 30 min OS install per device | Insert card, boot, done |
| WiFi config during workshop | WiFi already configured |
| Dependency installs fail on slow WiFi | Everything pre-installed |
| 1+ hour before teams can start | 5 minutes to first SSH |

**Pre-building saves 1-2 hours per team on workshop day.**

---

## Image 1: Pi 500 (Control Hub)

### Build Steps

1. **Image base OS:**
   - Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
   - Choose OS: **Raspberry Pi OS (64-bit) Desktop**
   - Advanced settings (gear icon):
     - Device name / hostname: `hub`
     - Enable SSH (password auth)
     - Username: `pi500`
     - Password: choose your own workshop password
     - WiFi: Your workshop network SSID + password
     - Timezone: Your timezone
   - Write to SD card

2. **Boot and install dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-opencv python3-pip python3-pygame sshpass joystick code
   pip3 install pupil-apriltags numpy --break-system-packages
   ```

3. **Install VS Code extensions:**
   ```bash
   code --install-extension ms-python.python
   code --install-extension ms-vscode-remote.remote-ssh
   ```

3. **Clone workshop repo:**
   ```bash
   cd ~
   git clone https://github.com/luminerdy/Pathfinder2026.git
   ```

4. **Add workshop files to desktop:**
   ```bash
   # Quick-access links on desktop
   ln -s ~/Pathfinder2026/START_HERE.md ~/Desktop/START_HERE.md
   ```

5. **Test:**
   ```bash
   cd ~/Pathfinder2026
   python3 -c "import cv2; import pupil_apriltags; import pygame; print('All dependencies OK')"
   ```

6. **Clone for each team:**
   - Shut down Pi 500
   - Remove SD card
   - Use Raspberry Pi Imager or `dd` to clone the card
   - For each clone, boot and record its assigned IP address:
     ```bash
     hostname -I
     ```
   - Optionally update the device label if needed.

### What's on the Pi 500 Image

| Item | Purpose |
|------|---------|
| Raspberry Pi OS Desktop | Visual interface |
| Python 3 + OpenCV + pygame | Run scripts + gamepad |
| VS Code + Remote SSH | Edit robot code with full IDE |
| SSH + sshpass | Connect to robot |
| pupil-apriltags | AprilTag detection (for testing) |
| Pathfinder2026 repo | All workshop skills and docs |
| Desktop shortcuts | START_HERE |

---

## Image 2: robot Pi (Pi 4)

Detailed build guide: [A2_ROBOT_PI_OS_BUILD.md](A2_ROBOT_PI_OS_BUILD.md)

### Build Steps

1. **Image base OS:**
   - Raspberry Pi Imager
   - Choose OS: **Raspberry Pi OS (64-bit) Desktop**
   - Advanced settings:
     - Device name / hostname: any event label you prefer; event connections use IP addresses
     - Enable SSH
     - Username: `robot`
     - Password: choose your own workshop password
     - WiFi: Workshop network
     - Timezone: Your timezone
   - Write to SD card

2. **Boot and install robot dependencies:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3-opencv python3-pip python3-smbus i2c-tools code
   pip3 install pupil-apriltags numpy smbus2 flask --break-system-packages
   ```

3. **Install VS Code Python extension:**
   ```bash
   code --install-extension ms-python.python
   ```

3. **Enable I2C:**
   ```bash
   sudo raspi-config nonint do_i2c 0
   ```

4. **Clone and setup robot code:**
   ```bash
   cd ~
   git clone https://github.com/luminerdy/Pathfinder2026.git pathfinder
   ```

5. **Install startup service:**
   ```bash
   sudo cp ~/pathfinder/systemd/pathfinder-startup.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable pathfinder-startup.service
   ```

6. **Test (with robot hardware connected):**
   ```bash
   cd ~/pathfinder
   python3 -c "from lib.board import get_board; print('Board OK')"
   python3 scripts/tools/check_battery.py
   ```

7. **Clone for each team:**
   - Same process as Pi 500
   - Record the assigned robot IP address:
     ```bash
     hostname -I
     ```
   - Optionally update the device label if needed.

### What's on the robot Image

| Item | Purpose |
|------|---------|
| Raspberry Pi OS | robot OS |
| Python 3 + OpenCV + Flask | Vision + web control |
| VS Code + Python extension | Local editing (via VNC) |
| I2C + smbus2 | Motor/servo communication |
| pupil-apriltags | Navigation |
| Pathfinder2026 code | All skills + scripts |
| Startup service | Auto-init on boot (beep when ready) |

---

## IP Assignment Convention

Use IP addresses for event connections. Keep an assignment sheet like this:

| House | Team | Pi 500 IP | robot IP |
|-------|------|-----------|----------|
| 1 | 1 | 10.1.1.11 | 10.1.1.101 |
| 1 | 2 | 10.1.1.12 | 10.1.1.102 |
| ... | ... | ... | ... |
| 7 | 49 | 10.7.1.17 | 10.7.1.107 |

**Static IPs recommended** - each house gets its own subnet (for example, House 1 = 10.1.x.x, House 2 = 10.2.x.x). Participants should connect with `ssh robot@<ROBOT_IP>`.

---

## Workshop Day Checklist

Before teams arrive:
- [ ] All Pi 500 SD cards imaged and tested
- [ ] All robot SD cards imaged and tested
- [ ] WiFi network up and tested
- [ ] All devices can ping each other
- [ ] SSH from each Pi 500 to its paired robot verified
- [ ] Batteries charged (2 sets per robot minimum)
- [ ] Spare SD cards available (things happen)
- [ ] Workshop practice field set up (tags, blocks, line tape, barriers as needed)

---

## Troubleshooting

**Card won't boot:**
- Re-image with Raspberry Pi Imager
- Try different SD card (bad cards are common)

**WiFi won't connect:**
- Check SSID/password in `/etc/wpa_supplicant/wpa_supplicant.conf`
- 5GHz vs 2.4GHz? Pi 500 supports both, Pi 4 supports both

**SSH refused:**
- `sudo systemctl enable ssh && sudo systemctl start ssh`

**robot code missing:**
- `cd ~ && git clone https://github.com/luminerdy/Pathfinder2026.git pathfinder`
