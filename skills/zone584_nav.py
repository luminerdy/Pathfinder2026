"""
Zone 584 Navigator — Barrier Slalom to AT584

Robot behavior:
  1. Lock heading to AT584 (top-right corner) via AprilTag angle correction
  2. Drive forward
  3. When sonar < BARRIER_STOP_CM (~3 inches): stop, probe left/right for gap
  4. Strafe through gap, applying heading correction every N ticks
  5. If AT584 lost during strafe: recover via micro-rotate sweep
  6. Repeat until AT584 reached at TARGET_DIST_M

Field notes:
  - Barriers: Hoikwo 12x4x3 cardboard boxes — sonar-VISIBLE
  - Gap between barriers: ~12 inches (~30 cm)
  - Stop threshold: 3 inches = 7.6 cm -> BARRIER_STOP_CM = 8
  - Robot uses mecanum wheels: strafe does NOT cause yaw

Usage:
    from robot import Robot
    from skills.zone584_nav import Zone584Navigator

    with Robot(enable_camera=True) as robot:
        nav = Zone584Navigator(robot)
        result = nav.navigate(callback=print)
        print(result)
"""

import time
import math
import cv2
from pupil_apriltags import Detector

# ── TUNING CONSTANTS ────────────────────────────────────────────────────────
TAG_ID           = 584
BARRIER_STOP_CM  = 8      # ~3 inches — stop forward when sonar reads this
GAP_CLEAR_CM     = 25     # sonar must exceed this to confirm gap is open
TARGET_DIST_M    = 0.90   # arrive at AT584 at this distance (matches StrafeNavigator)

HEADING_TOL_DEG  = 8      # don't rotate if angle within this many degrees
MAX_STRAFE_TICKS = 60     # abort strafe if gap not found after this many pulses (~6s)
STRAFE_PULSE_S   = 0.10   # seconds per strafe tick
HEADING_CHECK_N  = 3      # apply heading correction every N strafe ticks
TAG_ACQUIRE_S    = 1.0    # seconds to try acquiring AT584 on entry

FORWARD_POWER    = 40     # matches StrafeNavigator tuned value
STRAFE_POWER     = 38
ROTATE_POWER     = 35


class Zone584Navigator:
    """
    Navigate through Zone 584 barrier slalom to AT584.

    Key difference from StrafeNavigator: robot always FACES AT584
    via rotation correction. Mecanum strafe is used ONLY when a
    barrier blocks the forward path.
    """

    # Empirically calibrated camera params (fx, fy, cx, cy) at 640x480
    CAMERA_PARAMS = [525, 533, 325, 116]
    TAG_SIZE      = 0.165  # meters (16.5 cm tags)

    def __init__(self, robot):
        self._robot  = robot
        self.board   = robot.board
        self.sonar   = robot.sonar if hasattr(robot, 'sonar') else None
        self._camera = robot.camera if hasattr(robot, 'camera') else None

        if self._camera and hasattr(self._camera, 'camera_params'):
            self.CAMERA_PARAMS = list(self._camera.camera_params)

        self.detector = Detector(families='tag36h11')

    # ── HARDWARE HELPERS ────────────────────────────────────────────────────

    def _frame(self):
        if self._camera and hasattr(self._camera, 'get_raw_frame'):
            return self._camera.get_raw_frame()
        return None

    def _sonar_cm(self):
        if self.sonar is None:
            return None
        d = self.sonar.get_distance()
        if d is None:
            return None
        return d / 10.0 if d > 100 else d  # handle mm vs cm

    def _stop(self):
        self._robot.stop()

    def _forward(self):
        p = FORWARD_POWER
        self.board.set_motor_duty([(1, p), (2, p), (3, p), (4, p)])

    def _strafe(self, direction):
        """direction: +1 = right, -1 = left (mecanum lateral move, no yaw)"""
        p = int(STRAFE_POWER * direction)
        self.board.set_motor_duty([
            (1,  p), (2, -p),
            (3, -p), (4,  p)
        ])

    def _rotate(self, direction):
        """direction: +1 = clockwise, -1 = counter-clockwise"""
        p = int(ROTATE_POWER * direction)
        self.board.set_motor_duty([
            (1,  p), (2, -p),
            (3,  p), (4, -p)
        ])

    # ── APRILTAG DETECTION ──────────────────────────────────────────────────

    def _detect(self):
        """
        Detect AT584 and return (angle_deg, dist_m).
        angle > 0 means tag is to robot's RIGHT -> rotate clockwise to re-center.
        Returns (None, None) if tag not visible.
        """
        frame = self._frame()
        if frame is None:
            return None, None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = self.detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=self.CAMERA_PARAMS,
            tag_size=self.TAG_SIZE
        )

        for tag in tags:
            if tag.tag_id == TAG_ID and tag.pose_t is not None:
                x     = float(tag.pose_t[0][0])
                z     = float(tag.pose_t[2][0])
                dist  = math.sqrt(x * x + z * z)
                angle = math.degrees(math.atan2(x, z))
                return angle, dist

        return None, None

    # ── HEADING CORRECTION ──────────────────────────────────────────────────

    def _apply_heading_correction(self, angle):
        """
        Rotate to re-center AT584 if heading has drifted past HEADING_TOL_DEG.
        Called before each forward drive pulse and during gap strafe.

        Mecanum strafe doesn't cause yaw — but strafing far enough laterally
        shifts the geometric angle to the corner tag. This corrects that drift.

        Returns updated angle, or last_angle if tag not re-detected after rotation.
        """
        if angle is None or abs(angle) <= HEADING_TOL_DEG:
            return angle

        direction = 1 if angle > 0 else -1  # positive angle -> tag is right -> CW
        self._rotate(direction)
        time.sleep(0.06)
        self._stop()
        time.sleep(0.03)

        new_angle, _ = self._detect()
        return new_angle if new_angle is not None else angle

    # ── TAG RECOVERY ────────────────────────────────────────────────────────

    def _recover_tag(self, last_angle):
        """
        AT584 lost during strafe. Attempt re-acquisition in three stages:

          Stage 1 (fast): Micro-rotate toward last known direction.
                          Mecanum strafe doesn't rotate, so tag is likely
                          just past the camera FOV edge — a small nudge
                          brings it back. Covers 90% of loss events.

          Stage 2 (wider): Sweep opposite direction in case we overshot.
                           AT584 is fixed in top-right corner — it won't
                           move, so a ±25deg sweep always finds it if in range.

          Stage 3 (fallback): Hold last_angle. Robot continues strafing on
                              last known heading. Tag re-enters frame once
                              gap is found and forward motion resumes.

        Returns recovered angle, or last_angle as best effort.
        """
        direction = 1 if (last_angle or 0) >= 0 else -1

        # Stage 1: micro-rotate toward last known position (3 pulses)
        for _ in range(3):
            self._rotate(direction)
            time.sleep(0.06)
            self._stop()
            time.sleep(0.03)
            angle, _ = self._detect()
            if angle is not None:
                return angle

        # Stage 2: wider sweep in opposite direction (6 pulses ~ 25 deg)
        for _ in range(6):
            self._rotate(-direction)
            time.sleep(0.06)
            self._stop()
            time.sleep(0.03)
            angle, _ = self._detect()
            if angle is not None:
                return angle

        # Stage 3: hold last known heading — trust that strafe didn't cause yaw
        return last_angle

    # ── GAP DETECTION ───────────────────────────────────────────────────────

    def _probe_gap(self):
        """
        Probe left and right with short strafe pulses to find which side
        has more open space in front. Robot returns to original position
        after each probe.

        Returns 'left', 'right', or None if readings are equal.
        """
        def probe(direction):
            self._strafe(direction)
            time.sleep(0.12)
            self._stop()
            time.sleep(0.05)
            dist = self._sonar_cm()
            # Return to original position
            self._strafe(-direction)
            time.sleep(0.12)
            self._stop()
            time.sleep(0.05)
            return dist or 0

        left_dist  = probe(-1)
        right_dist = probe(+1)

        if left_dist > right_dist:
            return 'left'
        if right_dist > left_dist:
            return 'right'
        return None  # equal — caller falls back to 'left'

    # ── STRAFE TO GAP ───────────────────────────────────────────────────────

    def _strafe_to_gap(self, direction, last_angle, callback=None):
        """
        Strafe in direction until front sonar clears GAP_CLEAR_CM.
        Applies heading correction every HEADING_CHECK_N ticks so the
        robot stays pointed at AT584 while moving sideways.

        Returns last known angle when gap is found (or MAX_STRAFE_TICKS hit).
        """
        dir_val    = -1 if direction == 'left' else +1
        curr_angle = last_angle
        tick       = 0

        while tick < MAX_STRAFE_TICKS:
            sonar = self._sonar_cm()
            if sonar and sonar > GAP_CLEAR_CM:
                self._stop()
                return curr_angle  # gap aligned — resume forward

            self._strafe(dir_val)
            time.sleep(STRAFE_PULSE_S)
            self._stop()
            time.sleep(0.03)
            tick += 1

            # Periodic heading correction while strafing
            if tick % HEADING_CHECK_N == 0:
                angle, _ = self._detect()
                if angle is not None:
                    curr_angle = angle
                    curr_angle = self._apply_heading_correction(curr_angle)
                else:
                    curr_angle = self._recover_tag(curr_angle)
                    if callback:
                        callback(TAG_ID, None, curr_angle,
                                 'AT584 lost at tick %d - recovering' % tick)

        self._stop()
        return curr_angle  # timed out — return best known angle

    # ── TAG SEARCH ──────────────────────────────────────────────────────────

    def _search_for_tag(self, search_timeout=10, callback=None):
        """
        Rotate to find AT584. Tries CW for first half, CCW for second half
        so the tag isn't skipped if it starts just behind the camera.

        Returns (angle, dist) if found, or (None, None) on timeout.
        """
        start     = time.time()
        clockwise = True
        half      = search_timeout / 2.0

        while time.time() - start < search_timeout:
            angle, dist = self._detect()
            if angle is not None:
                self._stop()
                return angle, dist

            if time.time() - start > half and clockwise:
                clockwise = False

            p = ROTATE_POWER if clockwise else -ROTATE_POWER
            self.board.set_motor_duty([(1, p), (2, -p), (3, p), (4, -p)])
            time.sleep(0.08)
            self._stop()
            time.sleep(0.05)

        self._stop()
        return None, None

    # ── MAIN NAVIGATE ───────────────────────────────────────────────────────

    def navigate(self, timeout=60, callback=None):
        """
        Drive through Zone 584 barrier slalom and arrive at AT584.

        Args:
            timeout:  Max seconds before giving up
            callback: Optional function(tag_id, dist, angle, message)

        Returns:
            dict: success, final_distance, final_angle, reason
        """
        start      = time.time()
        last_angle = None
        last_dist  = None

        # ── Phase 1: Acquire AT584 — quick look, then rotation search ────
        deadline = time.time() + TAG_ACQUIRE_S
        while time.time() < deadline:
            angle, dist = self._detect()
            if angle is not None:
                last_angle = angle
                last_dist  = dist
                break
            time.sleep(0.03)

        if last_angle is None:
            # Rotate to search — AT584 is top-right corner, try CW first
            if callback:
                callback(TAG_ID, None, None, 'AT584 not visible - rotating to search')
            last_angle, last_dist = self._search_for_tag(search_timeout=10, callback=callback)

        if last_angle is None:
            return {'success': False, 'reason': 'at584_not_visible_on_entry',
                    'final_distance': 0, 'final_angle': 0}

        if callback:
            callback(TAG_ID, last_dist, last_angle,
                     'ENTRY: AT584 acquired at %.2fm, %+.1fdeg' % (last_dist, last_angle))

        # ── Phase 2: Barrier slalom loop ─────────────────────────────────
        while time.time() - start < timeout:

            # Check arrival
            if last_dist and last_dist <= TARGET_DIST_M:
                self._stop()
                if callback:
                    callback(TAG_ID, last_dist, last_angle,
                             'REACHED AT584 at %.2fm' % last_dist)
                return {'success': True, 'reason': 'reached',
                        'final_distance': last_dist, 'final_angle': last_angle}

            # Correct heading before each forward pulse
            last_angle = self._apply_heading_correction(last_angle)

            sonar = self._sonar_cm()

            if sonar and sonar < BARRIER_STOP_CM:
                # ── Barrier detected: find and strafe through gap ────────
                self._stop()
                if callback:
                    callback(TAG_ID, last_dist, last_angle,
                             'BARRIER %.1fcm - probing for gap' % sonar)

                direction  = self._probe_gap() or 'left'
                if callback:
                    callback(TAG_ID, last_dist, last_angle,
                             'PROBED: gap is %s' % direction)

                last_angle = self._strafe_to_gap(direction, last_angle, callback)

                if callback:
                    callback(TAG_ID, last_dist, last_angle, 'GAP cleared - resuming forward')

            else:
                # ── Path clear: drive forward one pulse ──────────────────
                self._forward()
                time.sleep(0.05)
                self._stop()

            # Update tag reading after each action
            angle, dist = self._detect()
            if angle is not None:
                last_angle = angle
                last_dist  = dist
            else:
                last_angle = self._recover_tag(last_angle)

            time.sleep(0.02)

        self._stop()
        return {'success': False, 'reason': 'timeout',
                'final_distance': last_dist, 'final_angle': last_angle}


# ── STANDALONE TEST ──────────────────────────────────────────────────────────

def _cb(tag_id, dist, angle, msg):
    dist_str  = ('%.2fm' % dist)  if dist  is not None else '---'
    angle_str = ('%+.1fd' % angle) if angle is not None else '---'
    print('  [%s] %s %s  %s' % (tag_id or '---', dist_str, angle_str, msg))


if __name__ == '__main__':
    from robot import Robot

    print('Zone 584 Navigator')
    print('=' * 50)

    with Robot(enable_camera=True) as robot:
        nav    = Zone584Navigator(robot)
        result = nav.navigate(timeout=60, callback=_cb)

    print()
    print('=' * 50)
    print('Result : %s' % ('SUCCESS' if result['success'] else 'FAILED'))
    print('Reason : %s' % result['reason'])
    if result['final_distance']:
        print('Dist   : %.2fm' % result['final_distance'])
    if result['final_angle']:
        print('Angle  : %+.1fdeg' % result['final_angle'])
