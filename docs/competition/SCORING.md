# Scoring

**Last Updated:** July 11, 2026
**Status:** Draft scoring model
**Companion doc:** [Field Layout](FIELD_LAYOUT.md)

All block scoring happens at the end of the run. Bonuses and penalties are tallied by the field judge during the run.

---

## Block Delivery

| Block | Area | In delivery zone |
|-------|------|------------------|
| Blue | Area 1 | 5 pts |
| Red | Area 2 | 10 pts |
| Yellow | Area 3 | 15 pts |

Blocks outside the delivery zone score 0 points unless a later rule adds partial credit.

## Bonuses

| Action | Points |
|--------|--------|
| Robot starts fully inside the Area 1 start square | +5 |
| Robot returns fully to the start square at the end | +5 |
| Complete color set delivered: one blue, one red, one yellow | +25 per set |
| Autonomous delivery declared before the run and completed without human driving | +10 per block |

## Penalties

| Violation | Points |
|-----------|--------|
| Robot leaves the field | -5 per occurrence |
| Human touches robot outside the allowed start area | -3 per touch |
| Field element or AprilTag is moved by the robot | -5 per occurrence |
| Block is thrown or launched into the delivery zone | That block scores 0 |

## Score Sheet

**Team: ____________  Run #: ___  Judge: ____________**

### At The End Of The Run

| Count | x Pts | Total |
|-------|-------|-------|
| Blue blocks in delivery zone: ____ | x 5 | ____ |
| Red blocks in delivery zone: ____ | x 10 | ____ |
| Yellow blocks in delivery zone: ____ | x 15 | ____ |
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

- Confirm whether delivery means fully inside the taped zone or touching the zone.
- Confirm whether blocks carried on the robot at the buzzer score anything.
- Confirm final run time after the physical field is tested.
