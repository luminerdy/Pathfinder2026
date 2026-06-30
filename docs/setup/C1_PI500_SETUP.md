# C1: Pi 500 Setup

**Purpose:** Connect your Pi 500 to a monitor and prepare it as your team's control hub

The Pi 500 is a keyboard computer — the keyboard IS the computer. You just need a monitor and mouse.

For a short team-facing checklist, use [Team Start Handout](../handouts/TEAM_START_HANDOUT.md).

---

## Materials Needed

- Full setup BOM: [BILL_OF_MATERIALS.md](BILL_OF_MATERIALS.md)
- Raspberry Pi 500 (with SD card already imaged — see [A1](A1_PI500_OS_BUILD.md))
- Portable monitor
- Micro HDMI to HDMI adapter
- USB mouse
- Power supply (USB-C)

## Photos In This Guide

These images are stored in this repo under `docs/images/pi500/`.

| Photo file | Show |
|------------|------|
| `docs/images/pi500/01_pi500_connection.jpg` | Pi 500 connected to monitor, mouse, and power |
| `docs/images/pi500/02_pi500_connection_closeup.jpg` | Pi 500 connection closeup |
| `docs/images/pi500/03_pi500_boot_desktop.jpg` | Pi 500 after boot |
| `docs/images/pi500/04_pi_config_password.jpg` | Raspberry Pi configuration/password screen |
| `docs/images/pi500/05_wifi_setup.jpg` | WiFi network menu |
| `docs/images/pi500/06_open_terminal.jpg` | Terminal menu location |

## Step 1: Connect Hardware

<img src="../images/pi500/01_pi500_connection.jpg" width="400" alt="Pi 500 connected to monitor and mouse">

<img src="../images/pi500/02_pi500_connection_closeup.jpg" width="400" alt="Closeup of Pi 500 monitor and mouse connections">

```
[Monitor] ←HDMI→ [Micro HDMI Adapter] ←→ [Pi 500 HDMI port]
[Mouse] ←USB→ [Pi 500 USB port]
[Power] ←USB-C→ [Pi 500 power port]
```

The Pi 500's keyboard is built-in — no separate keyboard needed.

## Step 2: Power On

<img src="../images/pi500/03_pi500_boot_desktop.jpg" width="500" alt="Pi 500 booted to desktop">

1. Plug in power
2. Wait for desktop to appear (~30 seconds)
3. If prompted for password, enter the one set during imaging

If the Raspberry Pi configuration or password screen appears, keep the event hostname as `pihub` and use the password provided for the event.

<img src="../images/pi500/04_pi_config_password.jpg" width="500" alt="Raspberry Pi configuration password screen">

## Step 3: Connect to WiFi

<img src="../images/pi500/05_wifi_setup.jpg" width="250" alt="WiFi setup menu">

1. Click the network icon in the top-right taskbar
2. Select your workshop WiFi network
3. Enter password if required
4. Verify: open terminal (Ctrl+Alt+T) and run:
   ```bash
   ping -c 3 google.com
   ```

## Step 4: Open Terminal

<img src="../images/pi500/06_open_terminal.jpg" width="500" alt="Open terminal from Raspberry Pi menu">

You'll use the terminal for everything in this workshop:

- **Menu bar:** Click the terminal icon in the top taskbar
- **Keyboard shortcut:** Ctrl+Alt+T

Practice opening a terminal now. You'll be using it constantly.

## Step 5: Install VS Code (Recommended)

VS Code gives you a real code editor with syntax highlighting, file browser, and built-in terminal — much better than editing in nano.

1. **Install from terminal:**
   ```bash
   sudo apt-get install -y code
   ```
2. **Fallback if apt cannot find `code`:** Pi Menu -> **Preferences** -> **Recommended Software** -> check **Visual Studio Code** -> Apply
3. **Add required extensions from terminal:**
   ```bash
   code --install-extension ms-python.python
   code --install-extension ms-vscode-remote.remote-ssh
   ```
4. **Or add extensions in VS Code** (open VS Code, click Extensions icon on left):
   - **Python** (Microsoft) — syntax highlighting, linting
   - **Remote - SSH** (Microsoft) — edit files directly on the robot!

The Pi 500 is now ready for event-time robot connection. When the robot is assembled, use [C2: robot Pi WiFi Setup](C2_ROBOT_PI_WIFI_SETUP.md), then [C3: Connect and Test](C3_CONNECT_AND_TEST.md).

---

## Step 6: Open Workshop Repo

Use the GitHub repo as the main source:

```text
https://github.com/luminerdy/Pathfinder2026
```

Open `START_HERE.md` from the repo page.

Optional: if you cloned the repo locally during image setup, verify it:

```bash
cd ~/Pathfinder2026
ls
```

You should see files like `START_HERE.md`, `README.md`, and the `docs/` folder.

---

## Pi 500 Quick Reference

| Action | How |
|--------|-----|
| Open terminal | Ctrl+Alt+T |
| SSH to robot | `ssh robot@<ROBOT_IP>` |
| Copy file to robot | `scp file.py robot@<ROBOT_IP>:/home/robot/team_code/` |
| View robot camera | After web control is running on the robot, open browser: `http://<ROBOT_IP>:8080` |
| Edit code | `nano filename.py` or use Thonny (GUI editor) |
| Run Python | `python3 script.py` |
| Stop a running script | Ctrl+C |

---

**Next:** [C2: robot Pi WiFi Setup](C2_ROBOT_PI_WIFI_SETUP.md)
