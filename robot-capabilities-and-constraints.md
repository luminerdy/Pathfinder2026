# Robot Capabilities and Constraints

## Purpose

Pathfinder2026 depends on knowing what the robot can reliably do under real event conditions.

This document defines the core robot capability areas that need to be tested, measured, and documented before finalizing the competition field, autonomous behaviors, scoring model, and team guidance.

The goal is not to capture theoretical specifications. The goal is to define the robot’s practical operating envelope:

> What can the robot reliably sense, move, grab, carry, push, detect, and decide during the event?

This becomes the baseline for:
- Game design
- Field layout
- Scoring rules
- Autonomous behavior examples
- Team strategy
- LLM-assisted coding
- Troubleshooting
- Fair competition design

---

## Guiding Principle

The Pathfinder2026 game should challenge teams at the edge of the robot’s tested capabilities, not beyond them.

Teams should be able to succeed through:
- Good teamwork
- Good strategy
- Careful tuning
- Iterative testing
- Smart use of available robot capabilities
- Optional LLM-assisted improvements

The game should avoid failure modes caused by unknown robot limitations, inconsistent sensor behavior, or field elements that were not tested.

---

# 1. Drive System Limitations

## Why This Matters

The drive system defines how precisely the robot can move, turn, strafe, stop, and recover. Since the robot uses mecanum wheels, it has strong movement flexibility, but it may also experience drift, uneven movement, and inconsistent strafing.

## Questions to Answer

| Capability | Question |
|---|---|
| Minimum forward power | What is the lowest motor power where the robot consistently moves forward? |
| Minimum reverse power | What is the lowest motor power where the robot consistently moves backward? |
| Minimum turn power | What is the lowest motor power where the robot reliably rotates? |
| Minimum strafe power | What is the lowest motor power where sideways movement works reliably? |
| Straight-line drift | Does the robot pull left or right during forward movement? |
| Strafing drift | Does the robot drift forward/backward while strafing? |
| Turning repeatability | Does the robot rotate the same amount for the same command duration? |
| Stopping distance | How far does the robot continue moving after a stop command? |
| Battery impact | Does movement behavior change as the battery drains? |
| Surface impact | Does movement change on foam tiles, floor, tape, or seams? |
| Payload impact | Does carrying or pushing objects change movement reliability? |

## Test Results

| Test | Result | Notes |
|---|---|---|
| Minimum forward power | TBD |  |
| Minimum reverse power | TBD |  |
| Minimum turn power | TBD |  |
| Minimum strafe power | TBD |  |
| Forward drift over 4 ft | TBD |  |
| Strafe drift over 4 ft | TBD |  |
| 90-degree turn repeatability | TBD |  |
| Stop distance at low speed | TBD |  |
| Stop distance at medium speed | TBD |  |
| Battery impact observed | TBD |  |

## Event Impact

Documented drive limits should influence:
- Default motor power constants
- Autonomous movement examples
- Field path widths
- Obstacle spacing
- Scoring zone size
- Whether precision movement is realistic
- How much time teams need for tuning

---

# 2. Camera and Vision Limitations

## Why This Matters

The robot may use the camera for AprilTag detection, color detection, object location, and driver feedback. Camera-based features are affected by motion, lighting, angle, distance, and processing speed.

A key question is whether the robot must stop before using vision reliably.

## Questions to Answer

| Capability | Question |
|---|---|
| Detection while stopped | Can the robot reliably detect AprilTags or blocks while stationary? |
| Detection while moving | Can the robot detect targets while driving slowly? |
| Detection while turning | Can the robot detect targets while rotating? |
| Motion blur | Does movement cause missed or incorrect detections? |
| Lighting sensitivity | Does detection change under room lighting, shadows, or glare? |
| Distance sensitivity | What is the useful detection range? |
| Angle sensitivity | How far off-angle can the robot detect a target? |
| Field of view | How much of the field can the camera see? |
| Processing speed | How quickly can camera frames be processed? |
| Camera delay | Is there noticeable delay between what the camera sees and what the robot does? |

## Test Results

| Test | Result | Notes |
|---|---|---|
| AprilTag detection while stopped | TBD |  |
| AprilTag detection while moving slowly | TBD |  |
| AprilTag detection while turning | TBD |  |
| Color detection while stopped | TBD |  |
| Color detection while moving | TBD |  |
| Reliable camera range | TBD |  |
| Reliable camera angle | TBD |  |
| Camera processing rate | TBD |  |

## Recommended Pattern

If testing confirms that vision is unreliable during motion, use this pattern for autonomous behaviors:

```text
Move → Stop → Look → Decide → Move
```

Or:

```text
1. Stop the robot
2. Capture several frames
3. Select the most reliable reading
4. Make a decision
5. Move again
```

## Event Impact

Vision limits should influence:
- Whether teams are expected to scan while moving or while stopped
- AprilTag placement
- Block placement
- Field lighting requirements
- Sample code design
- Autonomous mission difficulty
- LLM prompt guidance

---

# 3. Ultrasonic Sensor Limitations

## Why This Matters

The ultrasonic sensor can help with obstacle detection, wall distance, and simple navigation. However, ultrasonic readings can be noisy and may be affected by material, angle, object size, and motion.

## Questions to Answer

| Capability | Question |
|---|---|
| Minimum reliable range | How close is too close for useful readings? |
| Maximum reliable range | How far can the sensor detect field objects reliably? |
| Best operating range | What distance band produces stable readings? |
| Sampling frequency | How often can readings be taken reliably? |
| Moving readings | Are readings reliable while driving? |
| Turning readings | Are readings reliable while rotating? |
| Material impact | Do black edging, white boxes, cardboard, foam, or wood reflect differently? |
| Angle sensitivity | Do angled objects produce incorrect or missing readings? |
| Narrow object detection | Can the sensor detect small blocks, or only larger walls/boxes? |

## Test Results

| Test | Result | Notes |
|---|---|---|
| Minimum reliable range | TBD |  |
| Maximum reliable range | TBD |  |
| Best operating range | TBD |  |
| Recommended sample interval | TBD |  |
| Reliable while stopped | TBD |  |
| Reliable while moving slowly | TBD |  |
| Reliable while turning | TBD |  |
| Black boundary detection | TBD |  |
| White box detection | TBD |  |
| Foam block detection | TBD |  |
| Wood block detection | TBD |  |

## Recommended Pattern

Ultrasonic readings should not be trusted as a single measurement unless testing proves they are stable.

Recommended approach:

```text
1. Take multiple readings
2. Remove obvious outliers
3. Use median or average value
4. Make a movement decision
```

Example:

```text
Take 5 readings
Sort the readings
Use the median reading
Ignore sudden large jumps
```

## Event Impact

Ultrasonic limits should influence:
- Obstacle avoidance examples
- Wall-following behavior
- Field materials
- Maze spacing
- Stop distance
- Autonomous speed
- Whether sonar-based challenges are fair

---

# 4. AprilTag Detection Limits

## Why This Matters

AprilTags can provide known visual landmarks for navigation and decision-making. Their reliability depends on size, distance, angle, lighting, movement, and camera processing.

## Questions to Answer

| Capability | Question |
|---|---|
| Minimum detection distance | How close can the robot be before the tag is too large or partially out of view? |
| Maximum detection distance | How far away can the robot reliably detect the tag? |
| Best detection range | What distance gives the best balance of detection and accuracy? |
| Angle limit | How far off-angle can the robot detect the tag? |
| Motion impact | Does detection work while moving or turning? |
| Lighting impact | Do shadows, glare, or dim light affect detection? |
| Multiple tags | Can the robot choose the correct tag when several are visible? |
| Tag size | Is the selected tag size appropriate for the field? |
| Tag placement | Should tags be on walls, boxes, stands, or other markers? |

## Test Results

| Test | Result | Notes |
|---|---|---|
| Minimum reliable detection distance | TBD |  |
| Maximum reliable detection distance | TBD |  |
| Best detection range | TBD |  |
| Maximum reliable angle | TBD |  |
| Detection while stopped | TBD |  |
| Detection while moving | TBD |  |
| Detection while turning | TBD |  |
| Detection with multiple tags visible | TBD |  |
| Recommended tag height/location | TBD |  |

## Event Impact

AprilTag testing should influence:
- Field marker placement
- Tag size
- Autonomous navigation rules
- Sample scanning behavior
- Whether robots need to stop before tag detection
- Competition mission design

---

# 5. Color Detection Limits

## Why This Matters

If game pieces use color, the robot needs to detect colors consistently. Color detection is sensitive to lighting, shadows, distance, camera angle, and background.

## Current Candidate Colors

- Red
- Yellow
- Blue

## Questions to Answer

| Capability | Question |
|---|---|
| Color separation | Which colors are easiest to distinguish? |
| Lighting sensitivity | Do colors change under event lighting? |
| Shadow sensitivity | Do shadows cause false readings? |
| Distance | How close does the robot need to be? |
| Angle | Does camera angle affect color recognition? |
| Background impact | Do black borders, white boxes, or foam tiles interfere? |
| Motion impact | Can colors be detected while moving? |
| False positives | Does the robot mistake field elements for blocks? |

## Test Results

| Test | Red | Yellow | Blue | Notes |
|---|---:|---:|---:|---|
| Detection while stopped | TBD | TBD | TBD |  |
| Detection while moving | TBD | TBD | TBD |  |
| Detection in shadow | TBD | TBD | TBD |  |
| Detection near white box | TBD | TBD | TBD |  |
| Detection near black boundary | TBD | TBD | TBD |  |
| Reliable detection distance | TBD | TBD | TBD |  |
| False positives observed | TBD | TBD | TBD |  |

## Event Impact

Color detection limits should influence:
- Block color selection
- Field lighting requirements
- Scoring rules
- Sample code
- Object placement
- Difficulty levels

---

# 6. Arm and Gripper Limitations

## Why This Matters

The arm and gripper define whether the robot can pick up, carry, lift, and place game pieces. This is likely one of the hardest physical tasks and should be tested carefully.

## Questions to Answer

| Capability | Question |
|---|---|
| Forward reach | How far in front of the robot can the arm reach? |
| Minimum reach | Can the arm pick up objects close to the chassis? |
| Side reach | Can the gripper pick up objects that are off-center? |
| Lift height | How high can the arm lift an object? |
| Drop height | Can the arm place objects into a box or container? |
| Gripper width | What object sizes fit in the gripper? |
| Grip strength | Can the robot hold the object while driving? |
| Alignment tolerance | How centered does the robot need to be? |
| Pickup repeatability | How many successful pickups out of 10 attempts? |
| Carry stability | Does the object fall during movement or turns? |

## Test Results

| Test | Result | Notes |
|---|---|---|
| Maximum forward reach | TBD |  |
| Minimum pickup distance | TBD |  |
| Left/right alignment tolerance | TBD |  |
| Maximum lift height | TBD |  |
| Reliable drop height | TBD |  |
| Gripper width range | TBD |  |
| Pickup success rate | TBD |  |
| Carry success rate | TBD |  |
| Drop-off success rate | TBD |  |

## Pickup Success Zone

Document the area where the robot can successfully pick up an object.

| Object Position | Success Rate | Notes |
|---|---:|---|
| Centered, close | TBD |  |
| Centered, medium distance | TBD |  |
| Centered, far reach | TBD |  |
| Slightly left | TBD |  |
| Slightly right | TBD |  |
| Near wall | TBD |  |
| Near another object | TBD |  |

## Event Impact

Arm and gripper limits should influence:
- Game piece size
- Pickup zone design
- Scoring value for pickup vs. pushing
- Box/container height
- Required precision
- Mission difficulty
- Whether pickup should be optional, bonus, or core scoring

---

# 7. Object Interaction Limits

## Why This Matters

Robots will interact with blocks, boxes, barriers, walls, and field objects. The game should reward creativity but avoid allowing one physical exploit to dominate the competition.

## Questions to Answer

| Capability | Question |
|---|---|
| Push force | What can the robot push reliably? |
| Drag limit | Can the robot push a box without wheels/casters? |
| Block movement | Does the robot push blocks cleanly or scatter them? |
| Bulldozing | Can the robot score too easily by pushing everything? |
| Object snagging | Do field objects catch on the robot, wheels, wires, or arm? |
| Wall contact | Does the robot get stuck against field boundaries? |
| Obstacle contact | Does the robot climb, jam, or redirect when hitting objects? |
| Multi-object pushing | Can it push more than one object at a time? |

## Test Results

| Object | Pushable? | Pickable? | Carryable? | Notes |
|---|---|---|---|---|
| Colored wood block | TBD | TBD | TBD |  |
| Foam block | TBD | TBD | TBD |  |
| White box | TBD | TBD | TBD |  |
| Box with casters | TBD | TBD | TBD |  |
| Cardboard tag box | TBD | TBD | TBD |  |
| Field boundary | TBD | N/A | N/A |  |

## Event Impact

Object interaction limits should influence:
- Scoring model
- Anti-bulldozing rules
- Object placement
- Box weight and drag
- Whether casters are used
- Allowed attachments
- Strategy options

---

# 8. Field and Surface Constraints

## Why This Matters

The robot does not operate in isolation. The field surface, boundaries, tape, obstacles, lighting, and game pieces all affect robot behavior.

## Field Elements to Test

| Field Element | Constraint to Test |
|---|---|
| Foam tiles | Wheel grip, seams, drift, unevenness |
| Tile seams | Do wheels catch or drift? |
| Green tape | Does it create bumps or visual confusion? |
| Black boundary | Does it reflect or absorb ultrasonic readings? |
| White boxes | Are they reliable ultrasonic targets? |
| Foam blocks | Do they absorb sonar or cause pushing issues? |
| Wood blocks | Are they easy to push, pick up, or detect? |
| Cardboard boxes | Do they move too easily or collapse? |
| Lighting | Does it affect camera, color, or AprilTag detection? |

## Test Results

| Field Element | Result | Notes |
|---|---|---|
| Foam tile traction | TBD |  |
| Tile seam impact | TBD |  |
| Green tape impact | TBD |  |
| Black boundary detection | TBD |  |
| White box detection | TBD |  |
| Foam block interaction | TBD |  |
| Wood block interaction | TBD |  |
| Lighting impact | TBD |  |

## Event Impact

Field constraints should influence:
- Field layout
- Path widths
- Obstacle spacing
- Lighting setup
- Material selection
- Driver practice area
- Autonomous test expectations

---

# 9. Compute and Control Limits

## Why This Matters

Robot behavior depends on software responsiveness, sensor processing, camera frame rate, web UI latency, and CPU load. Adding more features does not always make the robot better if those features slow down control.

## Questions to Answer

| Capability | Question |
|---|---|
| Camera FPS | How many frames per second can the robot process? |
| AprilTag processing | How fast can AprilTag detection run? |
| Color detection processing | How fast can color detection run? |
| Web UI delay | Is there noticeable lag in browser-based driving? |
| Command delay | How quickly does the robot react to commands? |
| CPU load | Does vision processing slow motor control? |
| Multiple features | Can the robot stream video, detect tags, and drive at the same time? |
| Startup reliability | Do robot services start correctly after reboot? |
| Network reliability | Does Wi-Fi introduce delays or dropouts? |

## Test Results

| Test | Result | Notes |
|---|---|---|
| Camera FPS | TBD |  |
| AprilTag detection FPS | TBD |  |
| Color detection FPS | TBD |  |
| Web UI control delay | TBD |  |
| Command response delay | TBD |  |
| CPU load during driving | TBD |  |
| CPU load during vision | TBD |  |
| Service startup reliability | TBD |  |
| Network reliability | TBD |  |

## Recommended Pattern

Use operating modes instead of running every feature at full speed all the time.

Example modes:

```text
Drive Mode
Scan Mode
Pickup Mode
Delivery Mode
Debug Mode
```

## Event Impact

Compute and control limits should influence:
- Sample code structure
- LLM-generated feature guidance
- Dashboard expectations
- Logging settings
- Autonomous behavior design
- Troubleshooting documentation

---

# 10. Battery and Power Limits

## Why This Matters

Battery level affects motor power, servo strength, camera stability, and robot reliability. A robot may work well at the beginning of testing but behave differently later.

## Questions to Answer

| Capability | Question |
|---|---|
| Runtime | How long does the robot run before behavior changes? |
| Motor power | Does minimum drive power increase as battery drains? |
| Servo strength | Does the arm weaken or jitter? |
| Camera stability | Does the camera disconnect or lag? |
| Brownouts | Does the robot reboot or lose control under load? |
| Charging time | How long does it take to prepare batteries? |
| Event readiness | How many batteries and chargers are needed? |

## Test Results

| Test | Result | Notes |
|---|---|---|
| Runtime under light use | TBD |  |
| Runtime under competition use | TBD |  |
| Drive behavior after 30 minutes | TBD |  |
| Arm behavior after 30 minutes | TBD |  |
| Camera stability over time | TBD |  |
| Battery recharge time | TBD |  |
| Batteries needed per team | TBD |  |
| Chargers needed per event | TBD |  |

## Event Impact

Battery and power limits should influence:
- Practice schedule
- Competition schedule
- Charging plan
- Spare battery plan
- Robot readiness checklist
- Troubleshooting guide

---

# 11. Human and Team Constraints

## Why This Matters

Pathfinder2026 is not only a robotics competition. It is a leadership, teamwork, and problem-solving experience. The robot capability baseline needs to account for the fact that teams have limited time and mixed experience levels.

## Known Constraints

| Area | Constraint |
|---|---|
| Time | Teams have limited time to build, test, tune, and compete |
| Skill level | Some participants may have little or no coding experience |
| Assembly variation | Robot build quality may vary between teams |
| Debugging experience | Teams may not know whether failure is mechanical, electrical, software, or sensor-related |
| LLM usage | LLM-generated code may require testing, tuning, and correction |
| Strategy | Teams may overbuild instead of focusing on scoring |
| Team dynamics | Communication and role clarity will affect performance |

## Event Impact

Human constraints should influence:
- Baseline code quality
- Step-by-step setup guides
- Simple test scripts
- Troubleshooting checklists
- Role guidance
- LLM prompt examples
- Time-boxed challenge design
- Clear scoring strategy

---

# 12. Capability Test Matrix

This table summarizes the major capability areas that need to be tested and documented.

| Capability Area | What We Need to Know | Test Method | Result | Event Impact |
|---|---|---|---|---|
| Drive minimum power | Lowest reliable power for forward, reverse, turn, and strafe | Run repeated movement trials at different power levels | TBD | Defines movement constants |
| Drive repeatability | How consistent movement is over distance and time | Run repeated forward, turn, and strafe commands | TBD | Defines autonomous movement expectations |
| Ultrasonic range | Reliable minimum and maximum range | Test against field materials at known distances | TBD | Defines obstacle avoidance rules |
| Ultrasonic sampling | Stable sample rate and filtering approach | Compare raw readings vs. filtered readings | TBD | Defines sensor polling pattern |
| Camera while moving | Whether vision works during movement | Detect tags/colors while stopped, moving, and turning | TBD | Defines scan behavior |
| AprilTag range | Reliable detection range and angle | Test distance and angle grid | TBD | Defines field tag placement |
| Color detection | Reliable color identification conditions | Test colors under event lighting | TBD | Defines block scoring and sample code |
| Arm reach | Pickup and drop-off envelope | Measure block positions and success rate | TBD | Defines object placement rules |
| Gripper reliability | Pickup, carry, and drop success rate | Run repeated trials per object | TBD | Defines scoring difficulty |
| Object pushing | What robot can push reliably | Test blocks, boxes, and barriers | TBD | Prevents unfair exploits |
| Battery life | Runtime before performance degradation | Run practice and competition simulations | TBD | Defines charging plan |
| Compute load | Impact of vision, UI, and control features | Monitor performance during robot operation | TBD | Defines safe software patterns |

---

# 13. Recommended Test Process

## Step 1: Establish Baseline Robot

Use one known-good robot as the baseline test unit.

Record:
- Robot model
- Raspberry Pi version
- Battery type
- Camera used
- Software version
- Field surface
- Lighting condition
- Test date

## Step 2: Test One Capability at a Time

Avoid testing too many variables at once.

Example:

```text
First test drive power on a clean field.
Then test drive power while carrying a block.
Then test drive power as the battery drains.
```

## Step 3: Use Repeated Trials

A single successful test is not enough.

Recommended minimum:

```text
10 trials per test condition
```

Track:
- Success count
- Failure count
- Average behavior
- Unusual behavior
- Notes

## Step 4: Convert Results Into Rules

The final result should not just be raw test data. Convert findings into practical rules.

Example:

```text
Finding:
The robot detects AprilTags most reliably when stopped.

Rule:
Autonomous tag scanning should stop the robot before processing frames.
```

## Step 5: Update Code and Game Design

Use findings to update:
- Constants
- Sample code
- Field layout
- Scoring
- Team instructions
- Troubleshooting guide

---

# 14. Pathfinder2026 Robot Operating Envelope

Use this section to summarize the final tested limits.

## Drive

| Item | Value |
|---|---|
| Minimum forward power | TBD |
| Minimum reverse power | TBD |
| Minimum turn power | TBD |
| Minimum strafe power | TBD |
| Recommended autonomous drive power | TBD |
| Recommended autonomous turn power | TBD |
| Reliable straight-line distance | TBD |
| Reliable turn accuracy | TBD |

## Ultrasonic

| Item | Value |
|---|---|
| Minimum reliable range | TBD |
| Maximum reliable range | TBD |
| Best operating range | TBD |
| Recommended sample interval | TBD |
| Recommended filter | TBD |
| Reliable while moving? | TBD |
| Reliable while turning? | TBD |

## Camera and Vision

| Item | Value |
|---|---|
| Reliable AprilTag range | TBD |
| Reliable AprilTag angle | TBD |
| Reliable color detection range | TBD |
| Detection while moving? | TBD |
| Detection while turning? | TBD |
| Recommended scan behavior | TBD |

## Arm and Gripper

| Item | Value |
|---|---|
| Maximum forward reach | TBD |
| Pickup alignment tolerance | TBD |
| Maximum lift height | TBD |
| Reliable drop height | TBD |
| Pickup success rate | TBD |
| Carry success rate | TBD |
| Drop-off success rate | TBD |

## Field Interaction

| Item | Value |
|---|---|
| Minimum recommended path width | TBD |
| Best object spacing | TBD |
| Pushable objects | TBD |
| Objects requiring pickup | TBD |
| Problem materials | TBD |
| Recommended boundary material | TBD |

## Battery and Power

| Item | Value |
|---|---|
| Expected runtime | TBD |
| Recommended battery swap interval | TBD |
| Batteries needed per team | TBD |
| Chargers needed | TBD |
| Power-related failure signs | TBD |

---

# 15. Open Items

Use this section to track unresolved questions.

| Open Question | Owner | Status | Notes |
|---|---|---|---|
| Does camera detection require the robot to stop? | TBD | Open |  |
| What is the reliable ultrasonic range on the actual field? | TBD | Open |  |
| Can the arm reliably place blocks into boxes? | TBD | Open |  |
| How much does battery drain affect motor power? | TBD | Open |  |
| What field materials interfere with sensors? | TBD | Open |  |
| What scoring rules discourage pure bulldozing without removing creativity? | TBD | Open |  |

---

# 16. Recommended Related Documents

This document should connect to other Pathfinder2026 documentation:

```text
docs/field-layout.md
docs/game-rules.md
docs/scoring-model.md
docs/team-strategy-guide.md
docs/robot-test-checklist.md
docs/llm-assisted-development-guide.md
docs/troubleshooting.md
```

---

# Summary

This document defines the robot capability areas that must be tested before finalizing Pathfinder2026.

The most important areas are:

1. Movement limits
2. Sensor limits
3. Vision limits
4. Arm and gripper limits
5. Object interaction limits
6. Field material limits
7. Compute and control limits
8. Battery and power limits
9. Human/team constraints

The final output should be a tested robot operating envelope that helps teams compete fairly, helps mentors troubleshoot quickly, and helps the event team design challenges that are difficult but achievable.
