# Competition Ideas

**Last Updated:** July 17, 2026
**Status:** Planning notes for field testing, not final event rules

Use this document to develop the competition layout before moving final decisions into [Field Layout](FIELD_LAYOUT.md) and [Scoring](SCORING.md).

## Design Goal

The field should encourage teams to combine capabilities instead of relying only on manual driving.

The proposed counter-clockwise progression is:

1. Area 1: start, open driving, and blue blocks.
2. Area 2: AprilTag 583 navigation and sonar-assisted barriers.
3. Area 3: AprilTag 584 navigation and line following.
4. Area 4: AprilTag 585 navigation and block delivery.

```text
                         Top side
          +-----------------------------------+
          | Area 3                 Area 2     |
          | tag 584                tag 583    |
          | line following         sonar      |
          | yellow blocks          red blocks |
          |                                   |
Left side |                                   | Right side
          |                                   |
          |                                   |
          | Area 4                 Area 1     |
          | tag 585                tag 582    |
          | delivery zone          start      |
          |                         blue blocks|
          +-----------------------------------+
                        Bottom side
```

## AprilTag Placement

- Use 10-inch `tag36h11` tags 582-585.
- Mount every tag flat and at a consistent camera height.
- Angle each corner tag approximately 45 degrees toward the field center.
- Keep a clear camera sightline to each tag from its expected approach route.
- Do not place tall obstacles directly between the robot and a navigation tag.
- Challenge programs should request a specific tag ID rather than navigating to whichever event tag is closest.

## Area 2: AprilTag And Sonar

### Purpose

Area 2 should let teams use tag 583 as a visual heading reference while using the forward sonar to detect and pass fixed barriers.

### Proposed Layout

- Mount tag 583 in the top-right corner, angled toward the field center.
- Create a 36-inch-wide approach lane from Area 1.
- Build three low cardboard barrier levels with openings on alternating sides.
- Make each fixed barrier from two 12-inch boxes placed together, creating a 24-inch barrier.
- Make each clear opening at least 30 inches wide.
- Separate the barrier levels by 30 to 36 inches.
- Place the red block pickup area beyond the final barrier level.
- Keep red blocks 12 to 18 inches apart and away from the perimeter.
- Use only sonar-visible cardboard barriers in this route.
- Do not place sonar-invisible foam cubes in the required travel path.

The barrier levels create a simple S-shaped sonar course. The robot detects a barrier, finds the opening by moving sideways, moves forward before turning, then continues toward tag 583.

Keep the layout simple enough that the published `skills/sonar_apriltag_navigation/run_demo.py` route can clear it consistently. If the baseline robot cannot complete three barrier levels reliably, remove the farthest level before the event.

### Published Starting Tool

Use:

```bash
python3 skills/sonar_apriltag_navigation/run_demo.py
```

Current known-good defaults from field testing:

| Setting | Value |
|---------|-------|
| Target tag | `583` |
| Fast forward | `50%` |
| Slow zone | `20 cm` |
| Slow forward | `30%` |
| Barrier stop | `12 cm` |
| Clear edge | `40 cm` |
| Strafe mode | `alternate` |
| Extra wheel clearance | `0.45 s` |
| Edge search timeout | `12 s` |
| Forward after clearing | `0.45 s` |
| No-pivot window after clearing | `1.0 s` |

### Area 2 Test Questions

- Can the robot keep tag 583 visible while moving through the openings?
- Does sonar consistently detect every cardboard barrier?
- Is a 30-inch opening wide enough for different robot builds and storage additions?
- Can the robot complete the route at lower battery voltage?
- Can the robot stop without touching the fixed barriers?
- Can it reach the red block area with enough room to position the arm?

## Area 3: AprilTag And Line Following

### Purpose

Area 3 should use tag 584 to reach a predictable staging point. The robot then points its camera down and follows a lime-green line to the yellow block area.

### Proposed Layout

- Mount tag 584 in the top-left corner, angled toward the field center.
- Place the beginning of the green line near the robot's expected 0.50-meter AprilTag stopping position.
- Begin with a 24-inch straight section so the robot can acquire the line.
- Add one gentle S-curve with a minimum curve radius of approximately 24 inches.
- Finish with another 24-inch straight section.
- End the line 12 to 18 inches before the yellow block pickup area.
- Keep barriers and foam cubes at least 18 inches from the line center.
- Provide a clear area after the end of the line so the robot can stop safely.

Use one continuous line. Avoid intersections, forks, loops, 90-degree turns, and sudden direction changes.

The line follower does not currently use sonar obstacle avoidance. Objects may make the surrounding area visually interesting, but nothing should enter the required line-following corridor.

### Area 3 Test Questions

- Can the robot find the line after stopping near tag 584?
- Is the first straight section long enough for reliable acquisition?
- Can the robot follow the curve while staying centered over the tape?
- Does the line remain visible across foam-tile seams?
- Does event lighting change the appearance of the fluorescent tape?
- Does the robot stop with enough space to begin yellow block detection or pickup?

## Area 4: AprilTag And Delivery

### Purpose

Area 4 should provide a reliable autonomous destination. Tag 585 guides the robot to the delivery zone after it collects a block.

### Proposed Layout

- Mount tag 585 in the bottom-left corner, angled toward the field center.
- Provide a clear approach lane at least 36 inches wide.
- Keep barriers and foam cubes out of the final approach.
- Center the taped delivery zone on the robot's tested stopping position when navigating to 0.50 meters from tag 585.
- Test the current 24-inch zone before deciding whether to enlarge it to 30 inches.
- Confirm that the robot can release a block fully inside the zone without the robot blocking the camera's view of tag 585.

Place the delivery-zone tape after testing the actual robot stop position. The tested stop location is more useful than an unverified measurement from the corner.

## Autonomous Scoring Ideas

The current scoring gives a bonus only when the robot picks up, carries, and delivers a block autonomously. That complete sequence is difficult, and it does not reward teams that successfully demonstrate autonomous navigation.

One possible scoring model is:

| Autonomous Achievement | Proposed Points | Limit |
|------------------------|-----------------|-------|
| Complete the Area 2 sonar route without human control | +10 | Once per run |
| Complete the Area 3 line route without human control | +10 | Once per run |
| Navigate to tag 585 and enter the delivery zone | +10 | Once per run |
| Pick up, carry, and deliver one block autonomously | +20 | Per block |

Keep the normal 10-point block value and 25-point complete-color-set bonus. A team can then earn meaningful points for working automation even if it does not complete an entire block mission.

Do not add a separate autonomous color-set bonus initially. The existing color-set bonus already rewards completing all three block areas.

## Autonomous Attempt Ideas

A clearly defined autonomous attempt makes judging easier and prevents a team from manually positioning the robot inches from a target before claiming an autonomous result.

- Mark an autonomous activation line or box at the entrance to each area.
- Begin with the robot stationary and fully behind the marked line.
- Allow the team to select a target color, route, or mode before activation.
- Allow one action to start the autonomous program.
- After activation, do not allow manual driving, repositioning, or task guidance.
- Always allow a safety stop.
- Human intervention ends the current autonomous attempt but does not remove ordinary block points.
- Allow another autonomous attempt only after the robot returns to a marked activation location.
- Award each area route bonus only once per run.
- Require judges to observe behavior, not inspect or interpret team code during the run.

## Run-Time Idea

Use six minutes as a provisional run time during testing. AprilTag searches, line following, block positioning, and arm movement are slower than manual driving.

Time a complete baseline route before finalizing the limit. If a reliable autonomous route uses most of the six minutes, either simplify the field or increase the time rather than making autonomy impractical.

## Software Work Suggested By The Layout

- Use explicit target IDs 583, 584, and 585 during the challenge.
- Keep the published Area 2 sonar navigator tuned against the final barrier layout.
- Verify sonar barrier thresholds against the actual cardboard boxes.
- Verify the software's expected opening width against the physical Area 2 gaps.
- Test the Area 3 line follower using the final tape, lighting, curves, and foam floor.
- Keep autonomous pickup presented as a starting tool rather than a guaranteed complete solution.

## Field Test Targets

Before freezing the layout, run at least ten trials of each required autonomous section with a known-good robot.

Suggested success targets:

| Section | Target Success Rate |
|---------|---------------------|
| Navigate to the correct AprilTag | At least 8 of 10 |
| Complete one Area 2 sonar barrier level | At least 8 of 10 |
| Complete the full Area 2 sonar route | At least 7 of 10 |
| Complete the Area 3 line | At least 8 of 10 |
| Enter the Area 4 delivery zone | At least 8 of 10 |

If a required section misses its target, first widen the route or simplify one field element. The competition should test team decisions and integration, not depend on one unusually precise robot movement.

## Decisions Still Needed

- Final Area 2 opening width.
- Final Area 3 line length and curve shape.
- Final delivery-zone size.
- Final autonomous point values.
- Final autonomous restart rule.
- Final run time.
- Whether autonomous activation locations need visible taped boxes or only entry lines.
