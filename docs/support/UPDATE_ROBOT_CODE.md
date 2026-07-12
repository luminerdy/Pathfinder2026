# Update robot code

**Purpose:** Pull the latest Pathfinder2026 code onto the robot when workshop fixes or updates are published.

Use this only when a facilitator tells the team to update, or when a GitHub change needs to reach the robot.

Student edits should be saved outside the official repo before updating. Use [Team code workflow](TEAM_CODE_WORKFLOW.md) for the copy-first editing pattern.

## Where To Run These Commands

Run these commands while logged into the robot.

Your prompt should look like:

```text
robot@pathfinder:~ $
```

or similar, such as:

```text
robot@pathfinder-2:~ $
```

Do not run these commands from the Pi 500 prompt unless you have already connected to the robot with SSH.

## Step 1: Connect To The robot

From the Pi 500:

```bash
ssh robot@<ROBOT_IP>
```

## Step 2: Go To The robot Code Folder

```bash
cd /home/robot/pathfinder
```

## Step 3: Check For Local Changes

```bash
git status
```

If the output says `working tree clean`, continue.

If files are modified, stop and ask a facilitator before pulling. Those changes may be team work or local testing changes.

If the team needs to keep those changes, copy them to `/home/robot/team_code` before updating.

## Step 4: Pull The Latest Code

```bash
git pull --ff-only
```

This updates the robot code only if Git can do it cleanly.

## Step 5: Confirm The Update

```bash
git log -1 --oneline
```

The first line should show the latest commit from GitHub.

## Step 6: Run The Test Again

For example, after updating motor-demo changes:

```bash
python3 skills/mecanum_drive/run_demo.py
```

## If `git pull` Does Not Work

**Local changes error:**

```text
error: Your local changes to the following files would be overwritten by merge
```

Stop and ask a facilitator. Do not delete files or reset the repo unless a facilitator tells you to.

**Network error:**

- Confirm the robot is on WiFi.
- Confirm the Pi 500 and robot are on the workshop network.
- Try:

```bash
ping -c 3 github.com
```

**Authentication error:**

The public Pathfinder2026 repo should not require GitHub login for a normal pull. Ask a facilitator to check the robot's Git remote:

```bash
git remote -v
```

## Quick Version

```bash
ssh robot@<ROBOT_IP>
cd /home/robot/pathfinder
git status
git pull --ff-only
git log -1 --oneline
```
