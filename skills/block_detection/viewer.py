#!/usr/bin/env python3
"""
Servo-only block detection viewer.

This tool is for tuning block identification before any autonomous pickup work.
It can move the arm servos to adjust the camera angle, but it does not drive
the robot base.

Usage:
    cd /home/robot/pathfinder
    python3 skills/block_detection/viewer.py

Then open:
    http://<ROBOT_IP>:8081
"""

import os
import sys
import time
import json
import threading
from datetime import datetime
from pathlib import Path

import cv2
from flask import Flask, Response, jsonify, request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.arm_positions import POS_CAMERA_DOWN, POS_CAMERA_FORWARD
from lib.board import get_board
from skills.block_detect import BlockDetector


REPO_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_DIR = REPO_ROOT / 'block_detection_captures'
FRAME_W = 640
FRAME_H = 480
PORT = 8081

app = Flask(__name__)

camera = None
board = None
camera_lock = threading.Lock()
board_lock = threading.Lock()
state_lock = threading.Lock()
detector = BlockDetector()
SELECTABLE_COLORS = ('red', 'blue', 'yellow')
enabled_colors = list(SELECTABLE_COLORS)

SERVO_LIMITS = {
    1: (1550, 2500),  # Claw/gripper. 1550=closed, 2500=open.
    3: (500, 2500),   # Wrist
    4: (500, 2500),   # Elbow
    5: (500, 2500),   # Shoulder
    6: (500, 2500),   # Base rotation
}

ARM_PRESETS = {
    'camera_forward': {
        'label': 'Camera Forward',
        'duration_ms': 1000,
        'positions': POS_CAMERA_FORWARD,
    },
    'camera_down': {
        'label': 'Camera Down',
        'duration_ms': 800,
        'positions': POS_CAMERA_DOWN,
    },
}

servo_positions = dict(POS_CAMERA_FORWARD)

latest_state = {
    'frame': None,
    'annotated': None,
    'detections': [],
    'updated_at': 0.0,
    'saved_count': 0,
}


def clamp(value, low, high):
    """Keep a servo pulse inside its safe range."""
    return max(low, min(high, int(value)))


def get_enabled_colors():
    """Return the currently selected block colors."""
    with state_lock:
        return enabled_colors.copy()


def set_enabled_colors(colors):
    """Update color filters, preserving the event color order."""
    selected = [color for color in SELECTABLE_COLORS if color in colors]
    if not selected:
        raise ValueError('Select at least one color')

    with state_lock:
        enabled_colors[:] = selected
    return selected


def get_arm_board():
    """Open the robot board lazily so the viewer still imports cleanly."""
    global board
    if board is None:
        board = get_board()
    return board


def apply_servo_positions(positions, duration_ms=500):
    """Move one or more arm servos, then update the displayed state."""
    clamped_positions = []
    for servo_id, pulse in positions:
        if servo_id not in SERVO_LIMITS:
            raise ValueError('Invalid servo id: %s' % servo_id)
        low, high = SERVO_LIMITS[servo_id]
        clamped_positions.append((servo_id, clamp(pulse, low, high)))

    with board_lock:
        get_arm_board().set_servo_position(duration_ms, clamped_positions)

    with state_lock:
        for servo_id, pulse in clamped_positions:
            servo_positions[servo_id] = pulse

    return dict(clamped_positions)


def get_camera():
    """Open the USB camera lazily."""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
        # Let exposure and white balance settle before trusting detections.
        time.sleep(1.0)
    return camera


def read_frame():
    """Read one camera frame safely."""
    with camera_lock:
        cam = get_camera()
        ok, frame = cam.read()
    return frame if ok else None


def detection_to_dict(block):
    """Convert a BlockDetection object to JSON-safe data."""
    return {
        'color': block.color,
        'center_x': block.center_x,
        'center_y': block.center_y,
        'width': block.width,
        'height': block.height,
        'area': block.area,
        'aspect_ratio': round(block.aspect_ratio, 3),
        'offset_from_center': block.offset_from_center,
        'estimated_distance_cm': round(block.estimated_distance_mm / 10.0, 1),
        'confidence': round(block.confidence, 3),
    }


def annotate(frame, detections, colors):
    """Draw detection boxes plus extra tuning guides."""
    annotated = detector.annotate_frame(frame.copy(), detections)

    # Center line helps judge whether the chosen target is usable for pickup.
    cv2.line(annotated, (FRAME_W // 2, 0), (FRAME_W // 2, FRAME_H),
             (255, 255, 255), 1)

    # Lower-half guide: pickup automation should mostly trust blocks on floor.
    cv2.line(annotated, (0, FRAME_H // 2), (FRAME_W, FRAME_H // 2),
             (120, 120, 120), 1)

    cv2.putText(annotated, 'block viewer - arm controls enabled',
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 255), 2)
    cv2.putText(annotated, 'detections: %d' % len(detections),
                (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 255), 2)
    cv2.putText(annotated, 'colors: %s' % ', '.join(colors),
                (10, 82), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                (0, 255, 255), 1)

    y_pos = 110
    with state_lock:
        positions = servo_positions.copy()
    for servo_id in sorted(positions.keys()):
        cv2.putText(annotated, 'S%d: %d' % (servo_id, positions[servo_id]),
                    (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (255, 255, 255), 1)
        y_pos += 24

    return annotated


def process_frame():
    """Capture, detect blocks, annotate, and update shared state."""
    frame = read_frame()
    if frame is None:
        return None

    colors = get_enabled_colors()
    detections = detector.detect(frame, colors=colors)
    annotated = annotate(frame, detections, colors)

    with state_lock:
        latest_state['frame'] = frame
        latest_state['annotated'] = annotated
        latest_state['detections'] = [detection_to_dict(d) for d in detections]
        latest_state['updated_at'] = time.time()

    return annotated


def generate_frames():
    """Yield MJPEG frames for the browser."""
    while True:
        annotated = process_frame()
        if annotated is None:
            time.sleep(0.05)
            continue

        ok, buffer = cv2.imencode('.jpg', annotated)
        if not ok:
            continue

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            buffer.tobytes() +
            b'\r\n'
        )


@app.route('/')
def index():
    """Serve the block detection viewer page."""
    return """
<!doctype html>
<html>
<head>
  <title>Pathfinder2026 Block Detection Viewer</title>
  <style>
    body {
      margin: 0;
      padding: 20px;
      font-family: Arial, sans-serif;
      background: #1a1a1a;
      color: #f5f5f5;
    }
    .wrap {
      max-width: 1100px;
      margin: 0 auto;
    }
    h1 {
      color: #4CAF50;
      text-align: center;
    }
    .panel {
      background: #2a2a2a;
      border: 1px solid #444;
      border-radius: 6px;
      padding: 16px;
      margin-top: 16px;
    }
    img {
      width: 100%;
      max-width: 800px;
      display: block;
      margin: 0 auto;
      border: 2px solid #4CAF50;
      border-radius: 5px;
    }
    button {
      padding: 12px 18px;
      font-size: 16px;
      font-weight: bold;
      background: #2196F3;
      border: 0;
      border-radius: 5px;
      color: white;
      cursor: pointer;
    }
    button:active {
      background: #0b7dda;
    }
    button.secondary {
      background: #607D8B;
    }
    button.warning {
      background: #8a5b17;
    }
    .button-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      margin-bottom: 12px;
    }
    .filter-row {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 12px 0;
    }
    .color-filter {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: #222;
      border: 1px solid #555;
      border-radius: 5px;
      font-weight: bold;
      cursor: pointer;
    }
    .color-filter input {
      width: 18px;
      height: 18px;
    }
    .color-filter.red {
      color: #ff6b6b;
    }
    .color-filter.blue {
      color: #6ca8ff;
    }
    .color-filter.yellow {
      color: #fff36b;
    }
    .servo-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
    }
    .servo-control {
      background: #222;
      border: 1px solid #3a3a3a;
      border-radius: 5px;
      padding: 12px;
    }
    .servo-label {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 8px;
      font-size: 14px;
      color: #ddd;
    }
    .servo-slider {
      width: 100%;
    }
    .range-labels {
      display: flex;
      justify-content: space-between;
      color: #aaa;
      font-size: 12px;
      margin-top: 4px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
    }
    th, td {
      border-bottom: 1px solid #444;
      padding: 8px;
      text-align: left;
      font-size: 14px;
    }
    th {
      color: #ddd;
    }
    .muted {
      color: #aaa;
      font-size: 14px;
      line-height: 1.4;
    }
    .caution {
      color: #ffd166;
      font-weight: bold;
    }
    #status {
      margin-left: 12px;
      color: #ddd;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Pathfinder2026 Block Detection Viewer</h1>

    <div class="panel">
      <img src="/video_feed" alt="Annotated block detection feed">
      <p class="muted">
        Servo-only viewer. This page can move the arm for camera tuning, but it does not drive the robot base.
        Use it to see false positives, lighting problems, and candidate confidence before changing pickup code.
      </p>
      <p class="caution">
        Keep hands clear of the arm before pressing pose buttons or moving sliders.
      </p>
      <div class="filter-row">
        <label class="color-filter red">
          <input type="checkbox" id="color-red" value="red" checked>
          Red
        </label>
        <label class="color-filter blue">
          <input type="checkbox" id="color-blue" value="blue" checked>
          Blue
        </label>
        <label class="color-filter yellow">
          <input type="checkbox" id="color-yellow" value="yellow" checked>
          Yellow
        </label>
      </div>
      <p class="muted">
        Select one or more colors to isolate detections while tuning.
      </p>
      <button onclick="saveSnapshot()">Save Snapshot</button>
      <span id="status">Ready.</span>
    </div>

    <div class="panel">
      <h2>Arm Camera Position</h2>
      <p class="muted">
        Use these controls to compare block detection with the camera forward or tilted down.
        Servo 1 is the claw. Servos 3-6 move the arm and camera.
      </p>
      <div class="button-row">
        <button class="secondary" onclick="applyPreset('camera_forward')">Camera Forward</button>
        <button class="secondary" onclick="applyPreset('camera_down')">Camera Down</button>
        <button class="warning" onclick="setServo(1, 2500)">Open Claw</button>
        <button class="warning" onclick="setServo(1, 1550)">Close Claw</button>
      </div>
      <div class="servo-grid">
        <div class="servo-control">
          <div class="servo-label"><span>Servo 1 - Claw</span><span id="servo1-value">2500</span></div>
          <input type="range" class="servo-slider" id="servo1" min="1550" max="2500" value="2500" step="1">
          <div class="range-labels"><span>Closed 1550</span><span>Open 2500</span></div>
        </div>
        <div class="servo-control">
          <div class="servo-label"><span>Servo 3 - Wrist</span><span id="servo3-value">590</span></div>
          <input type="range" class="servo-slider" id="servo3" min="500" max="2500" value="590" step="1">
        </div>
        <div class="servo-control">
          <div class="servo-label"><span>Servo 4 - Elbow</span><span id="servo4-value">2450</span></div>
          <input type="range" class="servo-slider" id="servo4" min="500" max="2500" value="2450" step="1">
        </div>
        <div class="servo-control">
          <div class="servo-label"><span>Servo 5 - Shoulder</span><span id="servo5-value">700</span></div>
          <input type="range" class="servo-slider" id="servo5" min="500" max="2500" value="700" step="1">
        </div>
        <div class="servo-control">
          <div class="servo-label"><span>Servo 6 - Base</span><span id="servo6-value">1500</span></div>
          <input type="range" class="servo-slider" id="servo6" min="500" max="2500" value="1500" step="1">
        </div>
      </div>
    </div>

    <div class="panel">
      <h2>Current Detections</h2>
      <div id="summary" class="muted">Waiting for camera...</div>
      <table>
        <thead>
          <tr>
            <th>Color</th>
            <th>Center</th>
            <th>Size</th>
            <th>Area</th>
            <th>Aspect</th>
            <th>Offset</th>
            <th>Distance</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody id="detections"></tbody>
      </table>
    </div>
  </div>

  <script>
    function updateStatus(text) {
      document.getElementById('status').textContent = text;
    }

    function saveSnapshot() {
      updateStatus('Saving snapshot...');
      fetch('/snapshot', {method: 'POST'})
        .then(response => response.json())
        .then(data => {
          updateStatus(data.message || 'Snapshot saved.');
          refreshDetections();
        })
        .catch(error => {
          updateStatus('Snapshot failed.');
          console.log(error);
        });
    }

    function updateServoControls(positions) {
      Object.keys(positions || {}).forEach(servo => {
        const slider = document.getElementById(`servo${servo}`);
        const value = document.getElementById(`servo${servo}-value`);
        if (slider && value) {
          slider.value = positions[servo];
          value.textContent = positions[servo];
        }
      });
    }

    function postJson(path, data) {
      return fetch(path, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
      });
    }

    const colorIds = ['red', 'blue', 'yellow'];

    function getSelectedColors() {
      return colorIds.filter(color => {
        return document.getElementById(`color-${color}`).checked;
      });
    }

    function updateColorControls(colors) {
      const selected = new Set(colors || colorIds);
      colorIds.forEach(color => {
        const checkbox = document.getElementById(`color-${color}`);
        if (checkbox) {
          checkbox.checked = selected.has(color);
        }
      });
    }

    function setColorFilters() {
      const colors = getSelectedColors();
      if (colors.length === 0) {
        updateStatus('Select at least one color.');
        refreshDetections();
        return;
      }

      updateStatus('Updating color filter...');
      postJson('/color_filters', {colors: colors})
        .then(response => response.json())
        .then(data => {
          if (data.status !== 'ok') {
            updateStatus(data.message || 'Color filter update failed.');
            refreshDetections();
            return;
          }
          updateColorControls(data.enabled_colors);
          updateStatus(`Detecting: ${data.enabled_colors.join(', ')}.`);
          refreshDetections();
        })
        .catch(error => {
          updateStatus('Color filter update failed.');
          console.log(error);
          refreshDetections();
        });
    }

    colorIds.forEach(color => {
      document.getElementById(`color-${color}`).addEventListener('change', setColorFilters);
    });

    function setServo(servo, position) {
      updateStatus(`Moving servo ${servo}...`);
      postJson('/servo', {servo: servo, position: position})
        .then(response => response.json())
        .then(data => {
          if (data.status !== 'ok') {
            updateStatus(data.message || 'Servo move failed.');
            return;
          }
          updateServoControls(data.positions);
          updateStatus(`Servo ${data.servo} set to ${data.position}.`);
        })
        .catch(error => {
          updateStatus('Servo command failed.');
          console.log(error);
        });
    }

    function applyPreset(preset) {
      updateStatus('Moving arm...');
      postJson('/arm_preset', {preset: preset})
        .then(response => response.json())
        .then(data => {
          if (data.status !== 'ok') {
            updateStatus(data.message || 'Arm preset failed.');
            return;
          }
          updateServoControls(data.positions);
          updateStatus(data.message || 'Arm moved.');
        })
        .catch(error => {
          updateStatus('Arm preset command failed.');
          console.log(error);
        });
    }

    [1, 3, 4, 5, 6].forEach(servo => {
      const slider = document.getElementById(`servo${servo}`);
      const value = document.getElementById(`servo${servo}-value`);
      slider.addEventListener('input', function() {
        value.textContent = this.value;
      });
      slider.addEventListener('change', function() {
        setServo(servo, parseInt(this.value));
      });
    });

    function refreshDetections() {
      fetch('/detections')
        .then(response => response.json())
        .then(data => {
          const summary = document.getElementById('summary');
          const body = document.getElementById('detections');
          const detections = data.detections || [];

          summary.textContent =
            detections.length + ' detection(s), ' +
            data.saved_count + ' saved snapshot(s), colors: ' +
            (data.enabled_colors || []).join(', ');
          updateServoControls(data.servo_positions);
          updateColorControls(data.enabled_colors);

          body.innerHTML = '';
          detections.forEach(det => {
            const row = document.createElement('tr');
            row.innerHTML = `
              <td>${det.color}</td>
              <td>(${det.center_x}, ${det.center_y})</td>
              <td>${det.width} x ${det.height}</td>
              <td>${det.area}</td>
              <td>${det.aspect_ratio}</td>
              <td>${det.offset_from_center}</td>
              <td>${det.estimated_distance_cm} cm</td>
              <td>${det.confidence}</td>
            `;
            body.appendChild(row);
          });
        })
        .catch(error => console.log(error));
    }

    refreshDetections();
    window.setInterval(refreshDetections, 1000);
  </script>
</body>
</html>
"""


@app.route('/video_feed')
def video_feed():
    """Serve annotated MJPEG camera stream."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/detections')
def detections():
    """Return latest detection list."""
    with state_lock:
        return jsonify({
            'detections': latest_state['detections'],
            'updated_at': latest_state['updated_at'],
            'saved_count': latest_state['saved_count'],
            'servo_positions': servo_positions.copy(),
            'enabled_colors': enabled_colors.copy(),
        })


@app.route('/color_filters', methods=['POST'])
def color_filters():
    """Select which block colors the viewer should detect."""
    data = request.json or {}
    colors = data.get('colors', [])
    if not isinstance(colors, list):
        return jsonify({
            'status': 'error',
            'message': 'colors must be a list',
        }), 400

    try:
        selected = set_enabled_colors(colors)
    except ValueError as error:
        return jsonify({
            'status': 'error',
            'message': str(error),
        }), 400

    return jsonify({
        'status': 'ok',
        'enabled_colors': selected,
    })


@app.route('/servo', methods=['POST'])
def servo():
    """Move one arm servo from the viewer controls."""
    try:
        data = request.json or {}
        servo_id = int(data.get('servo'))
        position = int(data.get('position'))
    except (TypeError, ValueError):
        return jsonify({
            'status': 'error',
            'message': 'Invalid servo request',
        }), 400

    try:
        positions = apply_servo_positions([(servo_id, position)], duration_ms=500)
    except Exception as error:
        return jsonify({
            'status': 'error',
            'message': 'Servo move failed: %s' % error,
        }), 500

    return jsonify({
        'status': 'ok',
        'servo': servo_id,
        'position': positions[servo_id],
        'positions': servo_positions.copy(),
    })


@app.route('/arm_preset', methods=['POST'])
def arm_preset():
    """Move the arm to a named camera pose."""
    data = request.json or {}
    preset_name = data.get('preset')
    preset = ARM_PRESETS.get(preset_name)
    if preset is None:
        return jsonify({
            'status': 'error',
            'message': 'Unknown arm preset',
        }), 400

    try:
        apply_servo_positions(preset['positions'], duration_ms=preset['duration_ms'])
    except Exception as error:
        return jsonify({
            'status': 'error',
            'message': 'Arm preset failed: %s' % error,
        }), 500

    return jsonify({
        'status': 'ok',
        'message': '%s selected.' % preset['label'],
        'positions': servo_positions.copy(),
    })


@app.route('/snapshot', methods=['POST'])
def snapshot():
    """Save the latest raw and annotated frames for tuning."""
    annotated = process_frame()
    if annotated is None:
        return jsonify({
            'status': 'error',
            'message': 'No camera frame available',
        }), 500

    CAPTURE_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_path = CAPTURE_DIR / ('block_raw_%s.jpg' % timestamp)
    annotated_path = CAPTURE_DIR / ('block_annotated_%s.jpg' % timestamp)
    metadata_path = CAPTURE_DIR / ('block_metadata_%s.json' % timestamp)

    with state_lock:
        raw = latest_state['frame'].copy() if latest_state['frame'] is not None else None
        metadata = {
            'timestamp': timestamp,
            'detections': latest_state['detections'],
            'enabled_colors': enabled_colors.copy(),
            'servo_positions': servo_positions.copy(),
        }

    if raw is not None:
        cv2.imwrite(str(raw_path), raw)
    cv2.imwrite(str(annotated_path), annotated)
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    with state_lock:
        latest_state['saved_count'] += 1

    return jsonify({
        'status': 'ok',
        'message': 'Saved %s' % annotated_path.name,
        'raw': str(raw_path),
        'annotated': str(annotated_path),
        'metadata': str(metadata_path),
    })


def release_camera():
    """Release the camera when the process exits."""
    global camera
    with camera_lock:
        if camera is not None and camera.isOpened():
            camera.release()
            camera = None


if __name__ == '__main__':
    try:
        print("=" * 70)
        print("Pathfinder2026 Block Detection Viewer")
        print("=" * 70)
        print()
        print("Servo-only arm controls. This does not drive the robot base.")
        print("Open in browser: http://<ROBOT_IP>:%d" % PORT)
        print("Snapshots save to: %s" % CAPTURE_DIR)
        print()
        app.run(host='0.0.0.0', port=PORT, threaded=True)
    finally:
        release_camera()
