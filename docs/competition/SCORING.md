# Scoring

**Last Updated:** July 13, 2026
**Status:** Draft scoring model
**Companion doc:** [Field Layout](FIELD_LAYOUT.md)

All block scoring happens at the end of the run. Bonuses and penalties are tallied by the field judge during the run.

The scoring goal is to reward teams for collecting all three block colors. Each block has the same base value. The color-set bonus is what encourages teams to divide work across blue, red, and yellow tasks.

---

## Block Delivery

| Block | Area | In delivery zone |
|-------|------|------------------|
| Blue | Area 1 | 10 pts |
| Red | Area 2 | 10 pts |
| Yellow | Area 3 | 10 pts |

Blocks outside the delivery zone score 0 points unless a later rule adds partial credit.

A block scores only if it is fully inside the taped delivery zone at the end of the run. Blocks carried on the robot at the buzzer score 0 points.

## Bonuses

| Action | Points |
|--------|--------|
| Robot starts fully inside the Area 1 start square | +5 |
| Robot returns fully to the start square at the end | +5 |
| Complete color set delivered: one blue, one red, one yellow | +25 per set |
| Autonomous delivery declared before the run and completed without human driving | +10 per block |

### Complete Color Set

A complete color set is one blue block, one red block, and one yellow block fully inside the delivery zone at the end of the run.

Examples:

| Blocks In Delivery Zone | Set Bonuses |
|-------------------------|-------------|
| 1 blue, 1 red, 1 yellow | 1 |
| 2 blue, 2 red, 1 yellow | 1 |
| 3 blue, 3 red, 3 yellow | 3 |

### Autonomous Delivery

A delivery earns the autonomous bonus if the robot picks up, carries, and delivers the block using only code after the autonomous program is started.

Before activation, the team may:

- Choose and start the autonomous program.
- Select a target color, route, or mode.
- Position the robot only as allowed by the run rules.

After activation, the team may not:

- Drive with keyboard, gamepad, web buttons, joystick, or manual controls.
- Give movement guidance or task guidance.
- Aim, reposition, or touch the robot except for an allowed safety stop.
- Pause and resume the robot to correct the route.

Human input after activation ends the autonomous bonus for that block. A safety stop is always allowed, but the stopped delivery does not receive the autonomous bonus unless a later rule allows a restart.

## Penalties

| Violation | Points |
|-----------|--------|
| Robot leaves the field | -5 per occurrence |
| Human touches robot outside the allowed start area | -3 per touch |
| Fixed field element or AprilTag is moved by the robot | -5 per occurrence |
| Block is thrown or launched into the delivery zone | That block scores 0 |

## Score Sheet

**Team: ____________  Run #: ___  Judge: ____________**

### At The End Of The Run

| Count | x Pts | Total |
|-------|-------|-------|
| Blue blocks in delivery zone: ____ | x 10 | ____ |
| Red blocks in delivery zone: ____ | x 10 | ____ |
| Yellow blocks in delivery zone: ____ | x 10 | ____ |
| Complete color sets: ____ | x 25 | ____ |

### During The Run

| Item | Tally | Total |
|------|-------|-------|
| Start square bonus | | ____ |
| Return-to-start bonus | | ____ |
| Autonomous deliveries | | ____ |
| Penalties | | -____ |

**RUN TOTAL: ________**

## Open Questions

- Confirm final run time after the physical field is tested.
- Confirm whether autonomous restarts are allowed after a safety stop.
