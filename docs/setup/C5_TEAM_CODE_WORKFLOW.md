# C5: Team code workflow

**Purpose:** Give teams a safe place to edit code without blocking future updates to the official Pathfinder2026 repo.

## The Rule

Treat this folder as the official workshop code:

```bash
/home/robot/pathfinder
```

Use this folder for team experiments:

```bash
/home/robot/team_code
```

Facilitators may update `/home/robot/pathfinder` during the event with `git pull`. Student changes should live in `/home/robot/team_code` so they are not overwritten or mixed with official updates.

## Create The Team Folder

Run this while logged into the robot:

```bash
mkdir -p /home/robot/team_code
```

## Copy Before Editing

Example: copy the mecanum drive demo before changing it.

```bash
cp /home/robot/pathfinder/skills/mecanum_drive/run_demo.py /home/robot/team_code/mecanum_experiment.py
```

Edit the copy:

```bash
nano /home/robot/team_code/mecanum_experiment.py
```

Run the copy with the official Pathfinder libraries available:

```bash
PYTHONPATH=/home/robot/pathfinder python3 /home/robot/team_code/mecanum_experiment.py
```

## Copy A Whole Skill Folder

If a demo uses nearby config files, copy the whole skill folder:

```bash
cp -a /home/robot/pathfinder/skills/mecanum_drive /home/robot/team_code/mecanum_drive
cd /home/robot/team_code/mecanum_drive
PYTHONPATH=/home/robot/pathfinder python3 run_demo.py
```

Now the team can edit files in `/home/robot/team_code/mecanum_drive` without changing the official repo.

## VS Code Remote SSH

When using VS Code Remote SSH, open this folder for student edits:

```bash
/home/robot/team_code
```

Use `/home/robot/pathfinder` as the source for examples and official code, but do not edit official files unless a facilitator tells you to.

## Before Updating The robot

Before running [C4: Update robot code](C4_UPDATE_ROBOT_CODE.md), check the official repo:

```bash
cd /home/robot/pathfinder
git status
```

If `git status` shows modified files, stop and ask a facilitator. Those changes may need to be copied into `/home/robot/team_code` before updating.

## If Files Become Read-Only

Do not use `sudo git pull` in `/home/robot/pathfinder`. It can make files owned by `root`, which may prevent students from editing them.

Check ownership:

```bash
ls -ld /home/robot/pathfinder
ls -l /home/robot/pathfinder | head
```

If files are owned by `root`, ask a facilitator to fix ownership:

```bash
sudo chown -R robot:robot /home/robot/pathfinder
```

Then check again:

```bash
git status
```

## Quick Version

```bash
mkdir -p /home/robot/team_code
cp -a /home/robot/pathfinder/skills/mecanum_drive /home/robot/team_code/mecanum_drive
cd /home/robot/team_code/mecanum_drive
PYTHONPATH=/home/robot/pathfinder python3 run_demo.py
```
