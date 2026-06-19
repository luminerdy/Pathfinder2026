# A2 - Robot Pi OS Build Steps

**Purpose:** Create an SD card image for a Pathfinder2026 workshop robot.
**Platform:** Raspberry Pi 4 (4GB+)  
**OS:** Raspberry Pi OS (Debian 13 Trixie, 64-bit)  
**Raspberry Pi Imager:** 2.0.0
**Current Pi OS Released:** 2026-06-18
**Last tested:** 2026-06-18
**Time:** ~30 minutes

> **OS Note:** Use the Raspberry Pi OS 64-bit release dated **2026-06-18**. This guide was last tested on **2026-06-18**.

---

## Overview

After completing these steps you will have an SD card that can be cloned for all workshop robots. Each robot gets an identical image; WiFi credentials and assigned IP address are recorded per robot.

**Materials:** see [BILL_OF_MATERIALS.md](BILL_OF_MATERIALS.md) in this folder for the robot/setup BOM.

---

## Step 1: Flash Base OS

### Download
- Go to https://www.raspberrypi.com/software/
- Download **Raspberry Pi Imager 2.0.0**

### Flash Settings
- **OS:** Raspberry Pi OS (64-bit), released 2026-06-18
  - Lite (no desktop) is recommended for robot-only images
  - Desktop is fine if students will use VNC
- **Storage:** Select your SD card (16GB minimum, 32GB recommended)

### Pre-Configure in Imager (gear icon / Ctrl+Shift+X)
- **Device name / hostname:** any event label you prefer; use IP addresses for all event connections
- **Enable SSH:** Yes (password authentication)
- **Username:** `robot`
- **Password:** choose your own workshop password
- **WiFi:** Configure your workshop network SSID and password
- **Locale:** Set timezone and keyboard layout

> **Event account note:** Event notes may refer to the user name as "Robot"; keep the Linux account lowercase as `robot` so paths and commands match `/home/robot/pathfinder`.

### Flash
Click **Write** and wait for completion.

> **Locale tip:** If you set locale to `en_US` during imaging but see locale warnings over SSH, the locale may not be fully generated. Fix with:
> ```bash
> sudo locale-gen en_US.UTF-8
> sudo update-locale LANG=en_US.UTF-8
> ```

---

## Step 2: Boot and Connect

1. Insert SD card into Pi 4
2. Power on
3. Wait ~60 seconds for first boot (filesystem expands)
4. Find the Pi's IP address on your network:
   ```bash
   # On the robot, if you have a monitor attached
   hostname -I

   # Or check your router / DHCP client list
   ```
5. SSH in using the robot IP address:
   ```bash
   ssh robot@<ROBOT_IP>
   ```

> **Remote development:** With SSH enabled here, the Pi 500 can connect to this robot using VSCode Remote SSH. See [A1_PI500_OS_BUILD.md](A1_PI500_OS_BUILD.md) for Pi 500 configuration.

---

## Step 3: System Updates

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

---

## Step 4: Enable Interfaces

Enable SSH, VNC, I2C, and the UART configuration needed by the robot control board.

### Confirm SSH

SSH should already be enabled from Raspberry Pi Imager. If needed, enable it manually:

```bash
sudo raspi-config nonint do_ssh 0
```

### Enable VNC

```bash
sudo raspi-config nonint do_vnc 0
```

### Enable I2C (for motor board and sonar)
```bash
sudo raspi-config nonint do_i2c 0
```

### Enable UART and Disable Bluetooth
The motor board communicates via UART at 1,000,000 baud. On Pi 4, Bluetooth uses the good UART (ttyAMA0) by default. We need to swap it.

```bash
# Edit boot config
sudo nano /boot/firmware/config.txt
```

Find the `[all]` section and ensure these lines are present:
```
[all]
enable_uart=1

# Pathfinder2026: Free ttyAMA0 for motor board (1Mbaud)
dtoverlay=disable-bt
```

Disable Bluetooth services:
```bash
sudo systemctl disable hciuart bluetooth
sudo systemctl stop bluetooth
```

### Disable Serial Console on ttyAMA0

By default, the kernel and systemd both attach a serial console to `ttyAMA0`. This conflicts with the motor board â the port must be completely free for 1Mbaud communication.

```bash
# Remove the serial console from kernel boot parameters
sudo sed -i 's/console=serial0,[0-9]* //' /boot/firmware/cmdline.txt

# Disable the serial login prompt (getty)
sudo systemctl disable serial-getty@ttyAMA0.service
```

### Reboot
```bash
sudo reboot
```

### Verify After Reboot
```bash
# UART available (should point to ttyAMA0, NOT ttyS0)
ls -la /dev/serial0
# Should show: /dev/serial0 -> ttyAMA0

# ttyAMA0 exists
ls /dev/ttyAMA0
# Should show: /dev/ttyAMA0

# I2C available
ls /dev/i2c-1
# Should show: /dev/i2c-1

# Bluetooth inactive
systemctl is-active bluetooth
# Should show: inactive

# Serial console removed from ttyAMA0
systemctl is-active serial-getty@ttyAMA0
# Should show: inactive

# ttyAMA0 not held by any process
fuser /dev/ttyAMA0
# Should return nothing (no output)
```

> **Note:** Before adding `dtoverlay=disable-bt`, `/dev/serial0` points to `ttyS0`. After adding it and rebooting, it correctly points to `ttyAMA0`. The motor board requires `ttyAMA0`.

---

## Step 5: Install Python Dependencies

### System Packages
```bash
sudo apt-get install -y python3-pip python3-dev i2c-tools git python3-opencv
```

> **Trixie note:** `python3-opencv` (4.10.0) is available via apt on Debian 13 Trixie and is the recommended install method â no pip needed for OpenCV.

### Python Packages
```bash
pip3 install --break-system-packages \
    pupil-apriltags \
    flask \
    pyserial \
    smbus2 \
    pyyaml \
    numpy
```

**Note:** `--break-system-packages` is required on Trixie/Bookworm (PEP 668). `numpy` and `flask` may already be present; pip will skip them if current.

### Verify Installation
```bash
python3 -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python3 -c "from pupil_apriltags import Detector; print('AprilTags: OK')"
python3 -c "import flask; print('Flask: OK')"
python3 -c "import serial; print('PySerial: OK')"
python3 -c "import smbus2; print('SMBus2: OK')"
python3 -c "import yaml; print('PyYAML: OK')"
python3 -c "import numpy; print(f'NumPy: OK')"
```

All should print without errors.

> **Flask version warning:** Flask 3.1+ shows a deprecation warning when accessing `flask.__version__`. This is harmless â Flask is working correctly.

---

## Step 6: Install Visual Studio Code

VS Code is installed directly on the robot so students can code on it locally or via Remote SSH from the Pi 500.

```bash
sudo apt-get install -y code
```

### Install the Python Extension

```bash
code --install-extension ms-python.python --user-data-dir /home/robot/.vscode
```

This also installs Pylance and the Python debugger automatically.

### Verify
```bash
code --version
# Should show VS Code version number
```

---

## Step 7: Install Pathfinder2026

### Clone Repository
```bash
mkdir -p /home/robot/pathfinder
cd /home/robot/pathfinder
git clone https://github.com/luminerdy/Pathfinder2026.git .
```

### Verify Clone
```bash
ls skills/
# Should show skill files including strafe_nav.py, block_detect.py, etc.
```

### Verify All Imports
```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board, PLATFORM
print(f'Platform: {PLATFORM}')
from skills.block_detect import BlockDetector
from skills.strafe_nav import StrafeNavigator
print('All imports OK!')
"
```

Should print:
```
Platform: pi4
All imports OK!
```

---

## Step 8: Verify User Permissions

The `robot` user should already have the correct groups from Raspberry Pi Imager. Verify:

```bash
groups robot
```

Must include: `dialout` `i2c` `gpio` `video`

If any are missing:
```bash
sudo usermod -a -G dialout,i2c,gpio,video robot
# Then logout and login again
```

**No sudo needed to run robot code** if groups are correct.

---

## Step 9: Test Hardware

**Important:** Robot must be assembled with batteries installed before this step.

### Battery
```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board
import time
board = get_board()
time.sleep(1)
for i in range(5):
    mv = board.get_battery()
    if mv and 5000 < mv < 20000:
        print(f'Battery: {mv/1000:.2f}V')
        break
    time.sleep(0.3)
else:
    print('No battery reading â check motor board power')
"
```

### Buzzer
```bash
python3 -c "
from lib.board import get_board
import time
board = get_board(); time.sleep(0.5)
board.set_buzzer(1000, 0.1, 0.1, 2)
print('You should hear 2 beeps')
"
```

### Servos
```bash
python3 -c "
from lib.board import get_board
import time
board = get_board(); time.sleep(0.5)
board.set_servo_position(1000, [(1,2500),(3,590),(4,2450),(5,700),(6,1500)])
print('Arm should move to camera-forward position')
"
```

### Motors
```bash
python3 -c "
from lib.board import get_board
import time
board = get_board(); time.sleep(0.5)
board.set_motor_duty([(1,30),(2,30),(3,30),(4,30)])
time.sleep(0.5)
board.set_motor_duty([(1,0),(2,0),(3,0),(4,0)])
print('Robot should have moved forward briefly')
"
```

### Camera
```bash
python3 -c "
import cv2
cam = cv2.VideoCapture(0)
import time; time.sleep(1)
ret, frame = cam.read()
if ret: print(f'Camera: {frame.shape[1]}x{frame.shape[0]} OK')
else: print('Camera: FAILED â check USB connection')
cam.release()
"
```

> **GStreamer warning:** On Trixie you may see `GStreamer warning: Cannot query video position` â this is harmless, the camera works fine.

### Sonar
```bash
python3 -c "
from hardware.sonar import Sonar
import time
sonar = Sonar()
for i in range(3):
    d = sonar.get_distance()
    if d: print(f'Sonar: {d:.1f} cm')
    else: print('Sonar: No reading')
    time.sleep(0.3)
"
```

### Full Test (All at Once)
```bash
cd /home/robot/pathfinder
python3 -c "
from lib.board import get_board, PLATFORM
from hardware.sonar import Sonar
import cv2, time

print('Pathfinder2026 Hardware Test')
print('Platform:', PLATFORM)
print()

board = get_board()
time.sleep(1)

# Battery
for i in range(5):
    mv = board.get_battery()
    if mv and 5000 < mv < 20000:
        print(f'Battery: {mv/1000:.2f}V')
        break
    time.sleep(0.3)
else:
    print('Battery: FAILED')

# Buzzer
board.set_buzzer(1000, 0.1, 0.1, 2)
print('Buzzer: Sent 2 beeps')

# Servos
board.set_servo_position(1000, [(1,2500),(3,590),(4,2450),(5,700),(6,1500)])
time.sleep(1.5)
print('Servos: Camera forward position set')

# Motors
board.set_motor_duty([(1,30),(2,30),(3,30),(4,30)])
time.sleep(0.3)
board.set_motor_duty([(1,0),(2,0),(3,0),(4,0)])
print('Motors: Brief forward sent')

# Sonar
sonar = Sonar()
d = sonar.get_distance()
if d: print(f'Sonar: {d:.1f} cm')
else: print('Sonar: No reading')

# Camera
cam = cv2.VideoCapture(0)
time.sleep(1)
ret, frame = cam.read()
if ret:
    print(f'Camera: {frame.shape[1]}x{frame.shape[0]} OK')
    from pupil_apriltags import Detector
    det = Detector(families='tag36h11')
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = det.detect(gray)
    print(f'AprilTags: {len(tags)} detected')
cam.release()

print()
print('Hardware test complete!')
"
```

---

## Step 10: Enable Startup Service

`start_robot.py` runs automatically at boot and verifies all hardware is ready.

**Checks performed:**
- **Board** -- motor controller connected
- **Battery** -- voltage with good / caution / LOW status
- **Arm** -- moves to camera-forward position, gripper open
- **Sonar** -- reads distance, LEDs show distance-zone color
- **Camera** -- opens and captures a test frame

**Feedback (no screen needed):**
- **All clear:** 2 quick beeps + green LEDs for 5 seconds then off
- **Needs attention:** 5 slow beeps + red LEDs stay on until next boot

### Run Manually to Verify

```bash
cd /home/robot/pathfinder
python3 start_robot.py
```

### Install the Service

The service file is included in the repo at `systemd/pathfinder-startup.service`.

```bash
sudo cp /home/robot/pathfinder/systemd/pathfinder-startup.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pathfinder-startup.service
sudo systemctl start pathfinder-startup.service
```

### Check Last Run

```bash
journalctl -u pathfinder-startup.service
```

---

## Step 11: Clone the Image

Once one SD card is fully set up and tested, clone it for all robots:

### On Linux/Mac
```bash
# Read from SD card
sudo dd if=/dev/sdX of=Pathfinder2026.img bs=4M status=progress

# Write to new SD card
sudo dd if=Pathfinder2026.img of=/dev/sdY bs=4M status=progress
```

### On Windows
Use **Win32 Disk Imager** or **balenaEtcher** to read/write the image.

### Per-Robot Changes After Cloning
Each robot needs an assigned IP address recorded on the event IP sheet. If static IPs are used, configure the assigned IP before the event.

Optional: set a unique device label for local identification, but do not use it for event connections.

WiFi credentials should already be set from Step 1. If different networks are needed:
```bash
sudo nmcli dev wifi connect "SSID" password "PASSWORD"
```

> **Trixie note:** Debian 13 Trixie uses NetworkManager by default. `wpa_supplicant.conf` may not be the right place to set WiFi â use `nmcli` or the desktop network manager instead.

---

## Quick Reference: What's Installed

| Component | Version | Purpose |
|-----------|---------|---------|
| Raspberry Pi OS | Debian 13 Trixie 64-bit | Base operating system |
| Kernel | 6.12.75 | Linux kernel |
| Python | 3.13.5 | Programming language |
| OpenCV | 4.10.0 | Computer vision (via apt) |
| pupil-apriltags | 1.0.4 | AprilTag detection |
| Flask | 3.1.1 | Web control interface |
| PySerial | 3.5 | Serial communication (Pi 5) |
| SMBus2 | 0.4.3 | I2C communication (Pi 4) |
| PyYAML | 6.0.2 | Configuration files |
| NumPy | 2.2.4 | Math operations |
| Visual Studio Code | 1.119+ | Code editor |
| Python extension (ms-python) | 2026.4+ | Python language support in VS Code |
| Pathfinder2026 | Latest | Robot framework |

## Quick Reference: Hardware Interfaces

| Interface | Device | Config |
|-----------|--------|--------|
| UART (motor board) | `/dev/ttyAMA0` | `dtoverlay=disable-bt` |
| I2C (motor board) | `/dev/i2c-1` addr `0x7A` | `dtparam=i2c_arm=on` |
| I2C (sonar) | `/dev/i2c-1` addr `0x77` | Same bus |
| Camera | `/dev/video0` | USB camera |
| GPIO (buzzer) | Pin 31 | BOARD numbering |

---

## Troubleshooting

### No battery reading
- Check motor board power switch (must be ON)
- Check battery voltage (needs >7.0V)
- Try: `sudo i2cdetect -y 1` â should show `77` (sonar). **Note:** The motor board (`0x7A`) does NOT appear in `i2cdetect` output â it uses a non-standard probe response. Presence of `77` confirms I2C wiring is good; use the Python battery test to confirm the motor board is responding.

### Motors don't move
- Battery must be >7.0V
- Motor power minimum: 28-30 to overcome friction
- Check motor cables connected to board

### Camera not found
- Check USB cable
- Try: `ls /dev/video0`
- If locked: `lsof /dev/video0` â another process using it?
- GStreamer warning is harmless on Trixie

### UART not available / serial0 â ttyS0
- Bluetooth is still active â verify `dtoverlay=disable-bt` is in `/boot/firmware/config.txt` under `[all]`
- Verify `systemctl is-active bluetooth` returns `inactive`
- Must reboot after config change
- After fix: `ls -la /dev/serial0` should show `-> ttyAMA0`

### Motor board not responding / ttyAMA0 held at boot
Even after disabling Bluetooth, the serial console may still hold `ttyAMA0`. This is a separate issue â the kernel attaches a console to the port and systemd starts a login prompt on it.

Check:
```bash
fuser /dev/ttyAMA0                          # shows PID if port is held
systemctl is-active serial-getty@ttyAMA0   # should be inactive
grep 'serial0' /boot/firmware/cmdline.txt  # should return nothing
```

Fix:
```bash
sudo sed -i 's/console=serial0,[0-9]* //' /boot/firmware/cmdline.txt
sudo systemctl disable --now serial-getty@ttyAMA0.service
sudo reboot
```

### Permission denied on I2C
- User must be in `i2c` group: `groups robot`
- Fix: `sudo usermod -a -G i2c robot` then logout/login

### Locale warnings over SSH
- Harmless but can cause `perl` warnings in apt output
- Fix: `sudo locale-gen en_US.UTF-8 && sudo update-locale LANG=en_US.UTF-8`
- Then re-login

### WiFi config on Trixie
- Debian 13 uses NetworkManager, not wpa_supplicant
- Use `nmcli dev wifi connect "SSID" password "PASSWORD"` or the desktop GUI

---

*Created: March 26, 2026*  
*Updated: June 18, 2026 - aligned to Raspberry Pi OS release 2026-06-18 and Raspberry Pi Imager 2.0.0*
*Last tested: June 18, 2026*
*Tested on: Raspberry Pi 4 Model B, Debian 13 Trixie 64-bit, Python 3.13.x*
