#!/usr/bin/env python3
"""
Camera-only block detection viewer.

This tool is for tuning block identification before any autonomous pickup work.
It does not import the motor board and it does not move the robot.

Usage:
    cd /home/robot/pathfinder
    python3 skills/block_detection/viewer.py

Then open:
    http://<ROBOT_IP>:8081
"""

import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

import cv2
from flask import Flask, Response, jsonify

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.block_detect import BlockDetector


REPO_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_DIR = REPO_ROOT / 'block_detection_captures'
FRAME_W = 640
FRAME_H = 480
PORT = 8081

app = Flask(__name__)

camera = None
camera_lock = threading.Lock()
state_lock = threading.Lock()
detector = BlockDetector()

latest_state = {
    'frame': None,
    'annotated': None,
    'detections': [],
    'updated_at': 0.0,
    'saved_count': 0,
}


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


def annotate(frame, detections):
    """Draw detection boxes plus extra tuning guides."""
    annotated = detector.annotate_frame(frame.copy(), detections)

    # Center line helps judge whether the chosen target is usable for pickup.
    cv2.line(annotated, (FRAME_W // 2, 0), (FRAME_W // 2, FRAME_H),
             (255, 255, 255), 1)

    # Lower-half guide: pickup automation should mostly trust blocks on floor.
    cv2.line(annotated, (0, FRAME_H // 2), (FRAME_W, FRAME_H // 2),
             (120, 120, 120), 1)

    cv2.putText(annotated, 'camera-only block viewer',
                (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 255), 2)
    cv2.putText(annotated, 'detections: %d' % len(detections),
                (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 255, 255), 2)

    return annotated


def process_frame():
    """Capture, detect blocks, annotate, and update shared state."""
    frame = read_frame()
    if frame is None:
        return None

    detections = detector.detect(frame)
    annotated = annotate(frame, detections)

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
        Camera-only viewer. No drive motors or servos are controlled by this page.
        Use it to see false positives, lighting problems, and candidate confidence before changing pickup code.
      </p>
      <button onclick="saveSnapshot()">Save Snapshot</button>
      <span id="status">Ready.</span>
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

    function refreshDetections() {
      fetch('/detections')
        .then(response => response.json())
        .then(data => {
          const summary = document.getElementById('summary');
          const body = document.getElementById('detections');
          const detections = data.detections || [];

          summary.textContent =
            detections.length + ' detection(s), ' +
            data.saved_count + ' saved snapshot(s)';

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

    with state_lock:
        raw = latest_state['frame'].copy() if latest_state['frame'] is not None else None

    if raw is not None:
        cv2.imwrite(str(raw_path), raw)
    cv2.imwrite(str(annotated_path), annotated)

    with state_lock:
        latest_state['saved_count'] += 1

    return jsonify({
        'status': 'ok',
        'message': 'Saved %s' % annotated_path.name,
        'raw': str(raw_path),
        'annotated': str(annotated_path),
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
        print("Camera-only. This does not move the robot.")
        print("Open in browser: http://<ROBOT_IP>:%d" % PORT)
        print("Snapshots save to: %s" % CAPTURE_DIR)
        print()
        app.run(host='0.0.0.0', port=PORT, threaded=True)
    finally:
        release_camera()
