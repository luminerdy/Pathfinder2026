# Battery Safety

The robot uses two rechargeable 18650 lithium-ion cells. Handle them carefully and ask a facilitator for help with any damaged, hot, swollen, or leaking cell.

## Before Driving

Run the battery check while connected to the robot:

```bash
cd /home/robot/pathfinder
python3 scripts/tools/check_battery.py
```

| Voltage | Status | Action |
|---------|--------|--------|
| 8.2V or higher | Excellent | Ready for movement tests |
| 7.5V to 8.2V | OK | Normal testing; turns may vary as voltage drops |
| 7.0V to 7.5V | Caution | Light testing only; replace soon |
| Below 7.0V | Low | Replace or charge before moving the robot |

Check the battery before motor demos and again if movement becomes slow or inconsistent.

## Safe Battery Changes

1. Stop all robot programs.
2. Turn off the robot.
3. Remove the battery holder.
4. Ask a facilitator for a charged pair.
5. Check the polarity markings before inserting both cells.
6. Reinstall the holder and power on the robot with hands clear of the arm and wheels.
7. Run the battery check again.

Always use the two cells as a matched pair. Do not mix charged and discharged cells.

## Charging And Storage

- Charge cells only in the approved 18650 charger.
- Check polarity before placing cells in the charger.
- Keep charging batteries where event staff can monitor them.
- Do not leave charging batteries unattended overnight.
- Keep loose cells in a battery case so metal objects cannot short the terminals.
- Do not use a cell with a torn wrapper, dent, swelling, leak, unusual heat, or odor.

## Stop Immediately

Turn off the robot and get a facilitator if:

- A battery or holder becomes hot.
- A cell is swollen, leaking, dented, or has a damaged wrapper.
- You see smoke or smell a sharp chemical odor.
- The robot repeatedly reboots when motors start.
- Battery voltage cannot be read.
