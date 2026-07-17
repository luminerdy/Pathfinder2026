#!/usr/bin/env python3
"""
Web Control Interface for Pathfinder2026

Provides:
- Live video stream
- Drive controls (WASD/arrows)
- Servo sliders (6 servos)
- Save/load arm positions
- Real-time battery monitoring

Usage:
    python3 web_control.py
    Then open: http://<ROBOT_IP>:8080
"""

from flask import Flask, render_template, Response, jsonify, request
import cv2
import time
import json
import sys, os
import threading
from types import SimpleNamespace
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from lib.board import get_board
from lib.battery import is_runtime_safe, read_voltage, status_for_voltage
from skills.block_detect import BlockDetector
from skills.strafe_nav import StrafeNavigator
from skills.line_following.line_follower import LineFollower
BoardController = None  # Use get_board() instead

app = Flask(__name__)
REPO_ROOT = Path(__file__).resolve().parents[1]
SAVED_POSITIONS_PATH = REPO_ROOT / 'saved_positions.json'

# Global state
board = get_board()
camera = None  # Opened lazily to avoid locking camera on import
sonar = None  # Opened lazily so non-robot syntax checks do not need I2C hardware
camera_lock = threading.Lock()
sonar_lock = threading.Lock()
state_lock = threading.Lock()
board_lock = threading.Lock()
automation_lock = threading.Lock()
battery_cache = {
    'voltage': None,
    'updated_at': 0,
}
automation_state = {
    'active': False,
    'mode': None,
    'status': 'Idle',
    'detail': '',
    'cancel_requested': False,
    'started_at': 0.0,
    'finished_at': 0.0,
}
tracking_state = {
    'mode': None,
    'tag_id': None,
    'distance': None,
    'angle': None,
    'action': '',
    'line_found': False,
    'line_cx': None,
    'line_error': 0,
    'line_heading': 0,
    'line_ratio': 0.0,
}
block_detection_state = {
    'enabled': False,
    'colors': [],
    'raw_count': 0,
    'merged_count': 0,
    'selected_target': None,
    'updated_at': 0.0,
}
sonar_overlay_state = {
    'enabled': False,
    'distance_mm': None,
    'distance_cm': None,
    'message': 'Off',
    'updated_at': 0.0,
}
drive_state_lock = threading.Lock()
drive_state = {
    'active': False,
    'last_command_at': 0.0,
}
DRIVE_COMMAND_TIMEOUT = 0.75
DRIVE_WATCHDOG_INTERVAL = 0.10

ALLOWED_DIRECTIONS = {
    'forward', 'backward', 'left', 'right',
    'strafe_left', 'strafe_right', 'stop',
}

SERVO_LIMITS = {
    1: (1550, 2500),  # Claw/gripper. 1550=closed, 2500=open.
    3: (500, 2500),   # Wrist
    4: (500, 2500),   # Elbow
    5: (500, 2500),   # Shoulder
    6: (500, 2500),   # Base
}


def clamp(value, low, high):
    return max(low, min(high, int(value)))


def get_battery_voltage(max_age=5.0, retries=1, delay=0.0):
    """Return a recent battery voltage without blocking drive controls."""
    now = time.time()
    if battery_cache['voltage'] is not None and now - battery_cache['updated_at'] <= max_age:
        return battery_cache['voltage']

    with board_lock:
        voltage = read_voltage(board, retries=retries, delay=delay)

    if voltage is not None:
        battery_cache['voltage'] = voltage
        battery_cache['updated_at'] = time.time()
    return voltage


def set_drive_motors(commands):
    """Send drive motor commands without sharing the board port with other requests."""
    with board_lock:
        board.set_motor_duty(commands)


def stop_drive():
    """Stop all drive motors and clear the active-drive state."""
    set_drive_motors([(1, 0), (2, 0), (3, 0), (4, 0)])
    with drive_state_lock:
        drive_state['active'] = False
        drive_state['last_command_at'] = 0.0


def mark_drive_command():
    """Record a movement heartbeat received from the browser."""
    with drive_state_lock:
        drive_state['active'] = True
        drive_state['last_command_at'] = time.monotonic()


def drive_watchdog():
    """Stop motion when movement heartbeats stop arriving."""
    while True:
        time.sleep(DRIVE_WATCHDOG_INTERVAL)
        with drive_state_lock:
            expired = (
                drive_state['active']
                and time.monotonic() - drive_state['last_command_at']
                > DRIVE_COMMAND_TIMEOUT
            )
        if expired:
            try:
                stop_drive()
                print("Drive watchdog stopped the robot after command timeout.")
            except Exception as error:
                print(f"Drive watchdog stop failed: {error}")


def battery_display(voltage):
    """Return CSS status and participant-facing battery details."""
    status, message, safe = status_for_voltage(voltage)
    css_status = 'good' if status in ('OK', 'EXCELLENT') else 'low' if status == 'CAUTION' else 'critical'
    return status, message, safe, css_status


def get_camera():
    """Get or open camera (lazy initialization)"""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(0.5)
    return camera

# Servo positions (match startup script camera-forward position)
servo_positions = {
    1: 2500,  # Claw (Gripper open)
    3: 590,   # Wrist
    4: 2450,  # Elbow
    5: 700,   # Shoulder
    6: 1500   # Base (center/forward)
}

# Saved positions
saved_positions = {}

# Motor power (global, can be adjusted via web interface)
motor_power = {
    'drive': 30,
    'turn': 30
}

EVENT_TAG_IDS = (582, 583, 584, 585)
APRILTAG_TARGET_DISTANCE = 0.50
APRILTAG_SEARCH_TIMEOUT = 40.0
APRILTAG_NAV_TIMEOUT = 30.0
LINE_FOLLOW_TIMEOUT = 30.0
CAMERA_FORWARD_POSITION = [(1, 2500), (3, 590), (4, 2450), (5, 700), (6, 1500)]
APRILTAG_OVERLAY_DETECTOR = None
BLOCK_DETECTOR = BlockDetector()
BLOCK_DETECTION_COLORS = ('red', 'blue', 'yellow')


class LockedBoard:
    """Board wrapper used by background automations.

    Flask routes and automation threads can run at the same time. The wrapper
    keeps motor, servo, buzzer, RGB, and battery reads serialized on the shared
    serial connection.
    """

    def __init__(self, raw_board):
        self._raw_board = raw_board

    def set_motor_duty(self, commands):
        with board_lock:
            self._raw_board.set_motor_duty(commands)

    def set_servo_position(self, duration_ms, positions):
        with board_lock:
            self._raw_board.set_servo_position(duration_ms, positions)

    def set_buzzer(self, *args, **kwargs):
        with board_lock:
            return self._raw_board.set_buzzer(*args, **kwargs)

    def set_rgb(self, values):
        with board_lock:
            self._raw_board.set_rgb(values)

    def get_battery(self):
        with board_lock:
            return self._raw_board.get_battery()

    def __getattr__(self, name):
        return getattr(self._raw_board, name)


class WebCameraSource:
    """Camera adapter shared by MJPEG streaming and automation code."""

    camera_params = [525, 533, 325, 116]

    def is_open(self):
        with camera_lock:
            cam = get_camera()
            return cam is not None and cam.isOpened()

    def get_raw_frame(self):
        frame = read_camera_frame()
        return frame


def read_camera_frame():
    """Read one frame from the shared camera safely."""
    with camera_lock:
        cam = get_camera()
        success, frame = cam.read()
        return frame if success else None


def set_automation_state(**updates):
    """Update automation state shown by the browser and video overlay."""
    with automation_lock:
        automation_state.update(updates)


def get_automation_snapshot():
    """Return a copy of automation and tracking state for routes/overlays."""
    with automation_lock:
        auto = automation_state.copy()
        track = tracking_state.copy()
    return auto, track


def set_tracking_state(**updates):
    """Update tracking details shown on the video stream."""
    with automation_lock:
        tracking_state.update(updates)


def clear_tracking_state(mode=None):
    """Clear tracking overlay values."""
    with automation_lock:
        tracking_state.update({
            'mode': mode,
            'tag_id': None,
            'distance': None,
            'angle': None,
            'action': '',
            'line_found': False,
            'line_cx': None,
            'line_error': 0,
            'line_heading': 0,
            'line_ratio': 0.0,
        })


def block_target_to_dict(block):
    """Return browser-friendly details for the selected block target."""
    if block is None:
        return None

    return {
        'color': block.color,
        'center_x': block.center_x,
        'center_y': block.center_y,
        'width': block.width,
        'height': block.height,
        'offset': block.offset_from_center,
        'distance_cm': round(block.estimated_distance_mm / 10.0, 1),
        'confidence': round(block.confidence, 2),
        'score': BLOCK_DETECTOR.pickup_target_score(block),
    }


def set_block_detection_colors(colors):
    """Select which block colors should be shown in the overlay."""
    selected = [color for color in BLOCK_DETECTION_COLORS if color in colors]
    with automation_lock:
        block_detection_state.update({
            'enabled': bool(selected),
            'colors': selected,
            'raw_count': 0,
            'merged_count': 0,
            'selected_target': None,
            'updated_at': time.time(),
        })


def get_block_detection_snapshot():
    """Return the current block detection overlay status."""
    with automation_lock:
        return block_detection_state.copy()


def get_sonar():
    """Create the sonar object only when the overlay is used."""
    global sonar
    if sonar is None:
        from lib.sonar import Sonar
        sonar = Sonar()
    return sonar


def set_sonar_overlay_enabled(enabled):
    """Turn the sonar distance overlay on or off."""
    with state_lock:
        sonar_overlay_state.update({
            'enabled': bool(enabled),
            'distance_mm': None,
            'distance_cm': None,
            'message': 'On' if enabled else 'Off',
            'updated_at': 0.0,
        })


def get_sonar_overlay_snapshot():
    """Return the current sonar overlay status."""
    with state_lock:
        return sonar_overlay_state.copy()


def read_sonar_for_overlay(max_age=0.25):
    """Read sonar distance for the camera overlay without over-polling I2C."""
    now = time.time()
    snapshot = get_sonar_overlay_snapshot()
    if not snapshot['enabled']:
        return snapshot
    if snapshot['updated_at'] and now - snapshot['updated_at'] <= max_age:
        return snapshot

    try:
        with sonar_lock:
            distance_mm = get_sonar().get_distance()
    except Exception as error:
        with state_lock:
            sonar_overlay_state.update({
                'distance_mm': None,
                'distance_cm': None,
                'message': 'Error: %s' % error,
                'updated_at': time.time(),
            })
            return sonar_overlay_state.copy()

    distance_cm = distance_mm / 10.0 if distance_mm is not None else None
    message = 'No reading' if distance_cm is None else '%.0f cm' % distance_cm
    with state_lock:
        sonar_overlay_state.update({
            'distance_mm': distance_mm,
            'distance_cm': distance_cm,
            'message': message,
            'updated_at': time.time(),
        })
        return sonar_overlay_state.copy()


def automation_cancel_requested():
    """Return True when the browser has requested automation cancellation."""
    with automation_lock:
        return automation_state['cancel_requested']


def request_automation_cancel():
    """Ask a running automation to stop at its next cancel check."""
    with automation_lock:
        if automation_state['active']:
            automation_state['cancel_requested'] = True
            automation_state['status'] = 'Cancelling'
            automation_state['detail'] = 'Stop requested from web control'
            return True
    return False


def start_automation(mode):
    """Start a background automation if one is not already running."""
    with automation_lock:
        if automation_state['active']:
            return False, 'Automation already running'
        automation_state.update({
            'active': True,
            'mode': mode,
            'status': 'Starting',
            'detail': '',
            'cancel_requested': False,
            'started_at': time.time(),
            'finished_at': 0.0,
        })

    clear_tracking_state(mode)

    target = run_apriltag_automation if mode == 'apriltag' else run_line_automation
    threading.Thread(target=target, daemon=True).start()
    return True, 'Started %s automation' % mode


def finish_automation(mode, status, detail=''):
    """Mark an automation complete and stop the drive motors."""
    try:
        stop_drive()
    finally:
        set_automation_state(
            active=False,
            mode=mode,
            status=status,
            detail=detail,
            cancel_requested=False,
            finished_at=time.time(),
        )


def move_camera_forward():
    """Move arm/camera to the AprilTag navigation pose."""
    with board_lock:
        board.set_servo_position(1000, CAMERA_FORWARD_POSITION)
    with state_lock:
        for servo_id, pulse in CAMERA_FORWARD_POSITION:
            servo_positions[servo_id] = pulse
    time.sleep(1.1)


def move_camera_down():
    """Move arm/camera to the line-following pose and update web state."""
    with board_lock:
        board.set_servo_position(800, LineFollower.ARM_CAMERA_DOWN)
    with state_lock:
        for servo_id, pulse in LineFollower.ARM_CAMERA_DOWN:
            servo_positions[servo_id] = pulse
    time.sleep(1.0)


def run_apriltag_automation():
    """Run AprilTag navigation in the background for the web button."""
    mode = 'apriltag'
    locked_board = LockedBoard(board)
    web_camera = WebCameraSource()
    robot = SimpleNamespace(board=locked_board, camera=web_camera)
    nav = StrafeNavigator(robot)

    try:
        set_automation_state(status='Moving camera forward', detail='Preparing AprilTag view')
        stop_drive()
        move_camera_forward()

        set_automation_state(status='Searching', detail='Looking for AprilTags 582-585')

        def callback(tag_id, dist, angle, action):
            set_tracking_state(
                mode=mode,
                tag_id=tag_id,
                distance=dist,
                angle=angle,
                action=action,
            )
            set_automation_state(
                status='Running',
                detail='Tag %s: %.2fm, %+.1fdeg - %s' % (tag_id, dist, angle, action),
            )

        result = nav.search_and_navigate(
            target_ids=EVENT_TAG_IDS,
            target_distance=APRILTAG_TARGET_DISTANCE,
            search_timeout=APRILTAG_SEARCH_TIMEOUT,
            nav_timeout=APRILTAG_NAV_TIMEOUT,
            callback=callback,
            cancel_callback=automation_cancel_requested,
        )

        status = 'Cancelled' if result['reason'] == 'cancelled' else 'Done'
        detail = 'AprilTag navigation: %s' % result['reason']
        if result.get('tag_id') is not None:
            detail += ' (tag %s)' % result['tag_id']
        finish_automation(mode, status, detail)
    except Exception as error:
        print(f"AprilTag automation error: {error}")
        finish_automation(mode, 'Error', str(error))
    finally:
        nav.cleanup()


def run_line_automation():
    """Run line following in the background for the web button."""
    mode = 'line'
    locked_board = LockedBoard(board)
    web_camera = WebCameraSource()
    robot = SimpleNamespace(board=locked_board, camera=web_camera)
    follower = LineFollower(robot=robot)

    try:
        set_automation_state(status='Moving camera down', detail='Preparing line following')
        stop_drive()
        move_camera_down()

        def callback(detection, strafe, turn):
            set_tracking_state(
                mode=mode,
                line_found=detection['found'],
                line_cx=detection['cx'],
                line_error=detection['error'],
                line_heading=detection['heading_error'],
                line_ratio=detection['ratio'],
                action='strafe=%+.1f turn=%+.1f' % (strafe, turn),
            )
            set_automation_state(
                status='Running',
                detail='line err=%+d heading=%+d' % (
                    detection['error'], detection['heading_error']
                ),
            )

        result = follower.follow(
            timeout=LINE_FOLLOW_TIMEOUT,
            position_camera=False,
            callback=callback,
            cancel_callback=automation_cancel_requested,
        )

        status = 'Cancelled' if result['reason'] == 'cancelled' else 'Done'
        detail = 'Line following: %s' % result['reason']
        finish_automation(mode, status, detail)
    except Exception as error:
        print(f"Line following automation error: {error}")
        finish_automation(mode, 'Error', str(error))
    finally:
        follower.cleanup()


def draw_text_box(frame, lines, origin=(10, 30), color=(255, 255, 255)):
    """Draw readable status text on the camera frame."""
    x, y = origin
    for line in lines:
        cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 4)
        cv2.putText(frame, line, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
        y += 28
    return y


def draw_apriltag_overlay(frame):
    """Draw visible event AprilTags on the live stream while navigation runs."""
    global APRILTAG_OVERLAY_DETECTOR
    try:
        if APRILTAG_OVERLAY_DETECTOR is None:
            from pupil_apriltags import Detector
            APRILTAG_OVERLAY_DETECTOR = Detector(families='tag36h11')

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = APRILTAG_OVERLAY_DETECTOR.detect(gray, estimate_tag_pose=False)
    except Exception:
        return

    for tag in tags:
        if tag.tag_id not in EVENT_TAG_IDS:
            continue
        corners = tag.corners.astype(int)
        for i in range(4):
            p1 = tuple(corners[i])
            p2 = tuple(corners[(i + 1) % 4])
            cv2.line(frame, p1, p2, (0, 255, 255), 3)
        center = tuple(tag.center.astype(int))
        cv2.circle(frame, center, 5, (0, 255, 255), -1)
        cv2.putText(frame, f"tag {tag.tag_id}", (center[0] + 8, center[1] - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)


def draw_line_overlay(frame, track):
    """Draw line-following tracking values on the live stream."""
    cv2.line(frame, (320, 0), (320, frame.shape[0]), (255, 255, 255), 1)
    if track.get('line_found') and track.get('line_cx') is not None:
        roi_y = int(LineFollower.FRAME_H * LineFollower.ROI_BOTTOM_RATIO / 2)
        cx = int(track['line_cx'])
        cv2.circle(frame, (cx, roi_y), 10, (0, 255, 0), -1)
        cv2.line(frame, (cx, roi_y), (320, roi_y), (0, 255, 0), 2)
        label = 'line err=%+d heading=%+d' % (
            track.get('line_error', 0),
            track.get('line_heading', 0),
        )
        cv2.putText(frame, label, (10, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
    else:
        cv2.putText(frame, 'line not found', (10, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)


def draw_selected_block_overlay(frame, target):
    """Draw the selected block target with a green box."""
    frame_h, frame_w = frame.shape[:2]
    if target is None:
        cv2.putText(frame, 'selected block: none', (10, frame_h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 165, 255), 2)
        return

    x1 = target.center_x - target.width // 2
    y1 = target.center_y - target.height // 2
    x2 = x1 + target.width
    y2 = y1 + target.height

    cv2.rectangle(frame, (x1 - 4, y1 - 4), (x2 + 4, y2 + 4),
                  (0, 255, 0), 4)
    cv2.drawMarker(frame, (target.center_x, target.center_y),
                   (0, 255, 0), markerType=cv2.MARKER_CROSS,
                   markerSize=24, thickness=2)
    label = 'selected: %s %.0fcm offset=%+d' % (
        target.color,
        target.estimated_distance_mm / 10.0,
        target.offset_from_center,
    )
    cv2.putText(frame, label, (10, frame_h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)


def draw_block_detection_overlay(frame):
    """Draw block detections on the live camera feed when enabled."""
    state = get_block_detection_snapshot()
    colors = state.get('colors', [])
    if not colors:
        return

    raw_blocks = BLOCK_DETECTOR.detect(frame, colors=colors)
    blocks = BLOCK_DETECTOR.merge_close_detections(raw_blocks)
    target = BLOCK_DETECTOR.select_pickup_target(
        blocks,
        frame_width=frame.shape[1],
        frame_height=frame.shape[0],
    )

    BLOCK_DETECTOR.annotate_frame(frame, blocks)

    cv2.line(frame, (frame.shape[1] // 2, 0),
             (frame.shape[1] // 2, frame.shape[0]), (255, 255, 255), 1)
    cv2.line(frame, (0, frame.shape[0] // 2),
             (frame.shape[1], frame.shape[0] // 2), (120, 120, 120), 1)
    cv2.putText(frame, 'blocks: %s' % ', '.join(colors), (10, 105),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
    detection_label = 'blocks: %d' % len(blocks)
    if len(raw_blocks) != len(blocks):
        detection_label += ' (merged from %d)' % len(raw_blocks)
    cv2.putText(frame, detection_label, (10, 132),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
    draw_selected_block_overlay(frame, target)

    with automation_lock:
        block_detection_state.update({
            'raw_count': len(raw_blocks),
            'merged_count': len(blocks),
            'selected_target': block_target_to_dict(target),
            'updated_at': time.time(),
        })


def draw_sonar_overlay(frame):
    """Draw the current sonar distance on the live camera feed when enabled."""
    state = read_sonar_for_overlay()
    if not state['enabled']:
        return

    distance_cm = state.get('distance_cm')
    if distance_cm is None:
        label = 'Sonar: %s' % state.get('message', 'No reading')
        color = (0, 165, 255)
    else:
        label = 'Sonar: %.0f cm' % distance_cm
        if distance_cm < 15:
            color = (0, 0, 255)
        elif distance_cm < 31:
            color = (0, 255, 255)
        else:
            color = (0, 255, 0)

    x = max(10, frame.shape[1] - 230)
    cv2.putText(frame, label, (x, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 0), 4)
    cv2.putText(frame, label, (x, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)


def draw_automation_overlay(frame):
    """Add active automation status/tracking overlays to the video stream."""
    auto, track = get_automation_snapshot()
    if not auto['active'] and auto['status'] == 'Idle':
        return

    mode = auto['mode'] or 'automation'
    lines = ['%s: %s' % (mode.upper(), auto['status'])]
    if auto.get('detail'):
        lines.append(auto['detail'][:60])
    if track.get('action'):
        lines.append(track['action'][:60])
    draw_text_box(frame, lines, origin=(10, 120), color=(0, 255, 255))

    if auto['active'] and mode == 'apriltag':
        draw_apriltag_overlay(frame)
    elif auto['active'] and mode == 'line':
        draw_line_overlay(frame, track)

def generate_frames():
    """Generate video frames for streaming"""
    while True:
        frame = read_camera_frame()
        if frame is None:
            time.sleep(0.05)
            continue

        # Add battery voltage overlay
        voltage = get_battery_voltage(max_age=5.0, retries=1, delay=0.0)
        if voltage:
            _, _, _, css_status = battery_display(voltage)
            color = (0, 255, 0) if css_status == 'good' else (0, 165, 255) if css_status == 'low' else (0, 0, 255)
            cv2.putText(frame, f"Battery: {voltage:.2f}V", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        # Add servo positions overlay
        y_pos = 70
        for servo_id in sorted(servo_positions.keys()):
            pos = servo_positions[servo_id]
            cv2.putText(frame, f"S{servo_id}: {pos}", (10, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            y_pos += 30

        draw_block_detection_overlay(frame)
        draw_sonar_overlay(frame)
        draw_automation_overlay(frame)

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    """Serve main control page"""
    return render_template('control.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/drive', methods=['POST'])
def drive():
    """Drive motor control"""
    try:
        data = request.json
        direction = data.get('direction')
        if direction not in ALLOWED_DIRECTIONS:
            return jsonify({'status': 'error', 'message': 'Invalid direction'}), 400

        if direction == 'stop':
            request_automation_cancel()
            stop_drive()
            return jsonify({'status': 'ok'})

        with automation_lock:
            automation_active = automation_state['active']
        if automation_active:
            return jsonify({
                'status': 'error',
                'message': 'Automation is running. Stop automation before manual driving.',
            }), 409

        # Safety check: prevent motor commands at low battery
        voltage = get_battery_voltage(max_age=10.0, retries=3, delay=0.2)
        if not is_runtime_safe(voltage):
            _, message, _, _ = battery_display(voltage)
            voltage_text = f'{voltage:.2f}V' if voltage is not None else 'unavailable'
            stop_drive()
            return jsonify({
                'status': 'error',
                'message': f'Battery {voltage_text}: {message}',
            })

        drive_pwr = motor_power['drive']
        turn_pwr = motor_power['turn']

        # Limit max power to prevent crashes
        drive_pwr = min(drive_pwr, 40)
        turn_pwr = min(turn_pwr, 40)

        if direction == 'forward':
            set_drive_motors([(1, drive_pwr), (2, drive_pwr),
                                  (3, drive_pwr), (4, drive_pwr)])
        elif direction == 'backward':
            set_drive_motors([(1, -drive_pwr), (2, -drive_pwr),
                                  (3, -drive_pwr), (4, -drive_pwr)])
        elif direction == 'left':
            set_drive_motors([(1, -turn_pwr), (2, turn_pwr),
                                  (3, -turn_pwr), (4, turn_pwr)])
        elif direction == 'right':
            set_drive_motors([(1, turn_pwr), (2, -turn_pwr),
                                  (3, turn_pwr), (4, -turn_pwr)])
        elif direction == 'strafe_left':
            set_drive_motors([(1, -drive_pwr), (2, drive_pwr),
                                  (3, drive_pwr), (4, -drive_pwr)])
        elif direction == 'strafe_right':
            set_drive_motors([(1, drive_pwr), (2, -drive_pwr),
                                  (3, -drive_pwr), (4, drive_pwr)])

        mark_drive_command()
        return jsonify({'status': 'ok'})

    except Exception as e:
        # Emergency stop on any error
        print(f"Error in drive(): {e}")
        try:
            stop_drive()
        except:
            pass
        return jsonify({'status': 'error', 'message': 'Drive command failed'}), 500

@app.route('/servo', methods=['POST'])
def servo():
    """Servo control"""
    try:
        data = request.json or {}
        servo_id = int(data.get('servo'))
        position = int(data.get('position'))
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'Invalid servo request'}), 400

    if servo_id not in SERVO_LIMITS:
        return jsonify({'status': 'error', 'message': 'Invalid servo id'}), 400

    low, high = SERVO_LIMITS[servo_id]
    position = clamp(position, low, high)

    # Update position
    with state_lock:
        servo_positions[servo_id] = position

    # Send to board
    with board_lock:
        board.set_servo_position(500, [(servo_id, position)])

    return jsonify({'status': 'ok', 'servo': servo_id, 'position': position})

@app.route('/save_position', methods=['POST'])
def save_position():
    """Save current arm position"""
    data = request.json
    name = str(data.get('name', '')).strip()[:40]
    if not name:
        return jsonify({'status': 'error', 'message': 'Position name required'}), 400

    with state_lock:
        saved_positions[name] = servo_positions.copy()

        # Save to file
        with open(SAVED_POSITIONS_PATH, 'w') as f:
            json.dump(saved_positions, f, indent=2)

    return jsonify({'status': 'ok', 'name': name, 'positions': servo_positions})

@app.route('/load_position', methods=['POST'])
def load_position():
    """Load saved arm position"""
    data = request.json
    name = data.get('name')
    if not isinstance(name, str):
        return jsonify({'status': 'error', 'message': 'Position name required'}), 400

    with state_lock:
        position_found = name in saved_positions
        positions = saved_positions[name].copy() if position_found else None

    if position_found:
        clamped_positions = {}
        for sid, pos in positions.items():
            sid = int(sid)
            if sid in SERVO_LIMITS:
                low, high = SERVO_LIMITS[sid]
                clamped_positions[sid] = clamp(pos, low, high)

        # Apply all servos
        servo_list = [(sid, pos) for sid, pos in clamped_positions.items()]
        with board_lock:
            board.set_servo_position(500, servo_list)

        # Update state
        with state_lock:
            servo_positions.update(clamped_positions)

        return jsonify({'status': 'ok', 'name': name, 'positions': clamped_positions})
    else:
        return jsonify({'status': 'error', 'message': 'Position not found'}), 404

@app.route('/get_positions', methods=['GET'])
def get_positions():
    """Get all saved positions"""
    with state_lock:
        return jsonify({'positions': list(saved_positions.keys()),
                       'current': servo_positions})

@app.route('/battery', methods=['GET'])
def battery():
    """Get battery voltage"""
    voltage = get_battery_voltage(max_age=2.0, retries=2, delay=0.2)
    status, message, safe, css_status = battery_display(voltage)
    return jsonify({
        'voltage': voltage,
        'status': css_status,
        'battery_status': status,
        'message': message,
        'safe_to_drive': safe,
    })

@app.route('/motor_power', methods=['GET'])
def get_motor_power():
    """Get current motor power settings"""
    return jsonify(motor_power)

@app.route('/motor_power', methods=['POST'])
def set_motor_power():
    """Set motor power"""
    data = request.json
    try:
        with state_lock:
            if 'drive' in data:
                motor_power['drive'] = clamp(data['drive'], 0, 50)
            if 'turn' in data:
                motor_power['turn'] = clamp(data['turn'], 0, 50)
            return jsonify({'status': 'ok', 'motor_power': motor_power})
    except (TypeError, ValueError):
        return jsonify({'status': 'error', 'message': 'Invalid motor power'}), 400

@app.route('/automation/status', methods=['GET'])
def automation_status():
    """Return current automation status for the browser."""
    auto, track = get_automation_snapshot()
    return jsonify({'automation': auto, 'tracking': track})

@app.route('/automation/start', methods=['POST'])
def automation_start():
    """Start an automation from the web interface."""
    data = request.json or {}
    mode = data.get('mode')
    if mode not in ('apriltag', 'line'):
        return jsonify({'status': 'error', 'message': 'Invalid automation mode'}), 400

    voltage = get_battery_voltage(max_age=10.0, retries=3, delay=0.2)
    if not is_runtime_safe(voltage):
        _, message, _, _ = battery_display(voltage)
        voltage_text = f'{voltage:.2f}V' if voltage is not None else 'unavailable'
        stop_drive()
        return jsonify({
            'status': 'error',
            'message': f'Battery {voltage_text}: {message}',
        }), 400

    ok, message = start_automation(mode)
    status_code = 200 if ok else 409
    return jsonify({'status': 'ok' if ok else 'error', 'message': message}), status_code

@app.route('/automation/stop', methods=['POST'])
def automation_stop():
    """Request cancellation of the active automation."""
    if request_automation_cancel():
        stop_drive()
        return jsonify({'status': 'ok', 'message': 'Automation stop requested'})
    stop_drive()
    return jsonify({'status': 'ok', 'message': 'No automation running'})

@app.route('/block_detection/status', methods=['GET'])
def block_detection_status():
    """Return current block detection overlay status."""
    return jsonify(get_block_detection_snapshot())

@app.route('/block_detection/toggle', methods=['POST'])
def block_detection_toggle():
    """Select which block colors the overlay should show."""
    data = request.json or {}
    colors = data.get('colors', [])
    if not isinstance(colors, list):
        return jsonify({
            'status': 'error',
            'message': 'colors must be a list',
        }), 400

    invalid = [color for color in colors if color not in BLOCK_DETECTION_COLORS]
    if invalid:
        return jsonify({
            'status': 'error',
            'message': 'Invalid color: %s' % invalid[0],
        }), 400

    set_block_detection_colors(colors)
    return jsonify({
        'status': 'ok',
        'block_detection': get_block_detection_snapshot(),
    })

@app.route('/sonar/status', methods=['GET'])
def sonar_status():
    """Return current sonar overlay status."""
    return jsonify(get_sonar_overlay_snapshot())

@app.route('/sonar/toggle', methods=['POST'])
def sonar_toggle():
    """Turn the sonar distance overlay on or off."""
    data = request.json or {}
    enabled = bool(data.get('enabled', False))
    set_sonar_overlay_enabled(enabled)
    return jsonify({
        'status': 'ok',
        'sonar': get_sonar_overlay_snapshot(),
    })

# Load saved positions on startup
try:
    with open(SAVED_POSITIONS_PATH, 'r') as f:
        saved_positions = json.load(f)
        # Convert string keys to ints for servo_positions dict
        for name, positions in saved_positions.items():
            saved_positions[name] = {int(k): v for k, v in positions.items()}
except FileNotFoundError:
    pass

if __name__ == '__main__':
    print("="*70)
    print("Pathfinder2026 Web Control")
    print("="*70)
    print()

    # Position robot to startup/camera-forward position
    print("Positioning robot to startup position...")
    try:
        # Turn off sonar LEDs (both LEDs on the sonar)
        with board_lock:
            board.set_rgb([(0, 0, 0, 0), (1, 0, 0, 0)])

        # Stop motors
        stop_drive()

        # Move to camera-forward position (ONE SERVO AT A TIME to avoid power spike)
        camera_forward = [
            (1, 2500),  # Claw open
            (6, 1500),  # Base center
            (5, 700),   # Shoulder
            (4, 2450),  # Elbow
            (3, 590),   # Wrist
        ]

        print("  Moving servos sequentially...")
        for servo_id, pwm in camera_forward:
            with board_lock:
                board.set_servo_position(800, [(servo_id, pwm)])  # Slower speed (800ms)
            time.sleep(0.5)  # Longer delay between servos

        print("  Robot positioned to camera-forward")
    except Exception as e:
        print(f"  Warning: Could not position robot: {e}")

    print()
    print("Starting web server...")
    print("Open in browser: http://<ROBOT_IP>:8080")
    print()
    print("Controls:")
    print("  WASD or Arrow keys - Drive")
    print("  Q/E - Strafe left/right")
    print("  Space - Stop")
    print("  Sliders - Servo control")
    print("  Save/Load - Store arm positions")
    print()

    threading.Thread(target=drive_watchdog, daemon=True).start()
    try:
        app.run(host='0.0.0.0', port=8080, threaded=True)
    finally:
        stop_drive()
        print("Web control stopped. Drive motors are off.")
