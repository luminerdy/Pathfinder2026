#!/usr/bin/env python3
"""
Camera calibration webapp — live feed + manual capture.

Run on the robot:
    python3 scripts/calibration/calibration_webapp.py

Then open in any browser:
    http://<ROBOT_IP>:5000

Captured images → calibration_captures/
Calibration output → lib/camera_calibration.npz
"""

import threading
import time
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, Response

# ── Board config ──────────────────────────────────────────────────────────────
BOARD_W, BOARD_H = 7, 5          # inner corners (8x6 square board)
BOARD_SIZE       = (BOARD_W, BOARD_H)
IMG_W, IMG_H     = 640, 480
MIN_FOR_CAL      = 15

REPO_ROOT    = Path(__file__).resolve().parent.parent.parent
CAPTURES_DIR = REPO_ROOT / "calibration_captures"
OUTPUT_PATH  = REPO_ROOT / "lib" / "camera_calibration.npz"

# ── Shared camera state ───────────────────────────────────────────────────────
_lock         = threading.Lock()
_latest_frame = None   # annotated — for stream
_latest_raw   = None   # clean — for saving
_board_found  = False


def _camera_worker():
    global _latest_frame, _latest_raw, _board_found
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_H)
    time.sleep(1.0)

    subpix = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        gray   = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(
            gray, BOARD_SIZE,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
        )

        display = frame.copy()
        if found:
            c2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), subpix)
            cv2.drawChessboardCorners(display, BOARD_SIZE, c2, True)

        with _lock:
            _latest_frame = display
            _latest_raw   = frame.copy()
            _board_found  = bool(found)


def _gen_stream():
    while True:
        with _lock:
            f = _latest_frame
        if f is None:
            time.sleep(0.05)
            continue
        _, jpg = cv2.imencode('.jpg', f, [cv2.IMWRITE_JPEG_QUALITY, 72])
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n'
        time.sleep(0.04)   # ~25 fps


# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Camera Calibration</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #1a1a2e; color: #eee;
    font-family: system-ui, sans-serif;
    display: flex; flex-direction: column; align-items: center;
    min-height: 100vh; padding: 20px; gap: 16px;
  }
  h1 { font-size: 1.3rem; color: #a8d8ea; letter-spacing: 1px; }

  #stream-wrap { position: relative; border: 2px solid #444; border-radius: 8px; overflow: hidden; }
  #stream { display: block; max-width: 100%; }
  #badge {
    position: absolute; top: 8px; right: 8px;
    padding: 4px 12px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 600;
    background: #555; transition: background 0.2s;
  }
  #badge.found { background: #27ae60; }

  #counter { font-size: 1.1rem; color: #a8d8ea; }
  #progress-bar-wrap { width: 640px; max-width: 100%; height: 8px; background: #333; border-radius: 4px; overflow: hidden; }
  #progress-bar { height: 100%; width: 0%; background: #27ae60; transition: width 0.3s; }

  .controls { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
  button {
    padding: 12px 28px; border: none; border-radius: 8px;
    font-size: 1rem; font-weight: 600; cursor: pointer;
    transition: opacity 0.15s, transform 0.1s;
  }
  button:active { transform: scale(0.96); }
  button:disabled { opacity: 0.35; cursor: default; transform: none; }
  #btn-capture   { background: #27ae60; color: #fff; min-width: 140px; }
  #btn-calibrate { background: #2980b9; color: #fff; }
  #btn-clear     { background: #7f8c8d; color: #fff; }

  #log {
    width: 640px; max-width: 100%;
    background: #16213e; border-radius: 8px;
    padding: 12px; font-size: 0.82rem; font-family: monospace;
    max-height: 180px; overflow-y: auto;
    white-space: pre-wrap; color: #ccc;
  }
</style>
</head>
<body>

<h1>Camera Calibration</h1>

<div id="stream-wrap">
  <img id="stream" src="/stream" alt="camera" width="640" height="480">
  <span id="badge">Searching...</span>
</div>

<div id="counter">Captures: <b id="count">0</b> / 20</div>
<div id="progress-bar-wrap"><div id="progress-bar"></div></div>

<div class="controls">
  <button id="btn-capture" onclick="capture()">&#128247; Capture</button>
  <button id="btn-calibrate" onclick="runCalibration()" disabled>&#9881; Run Calibration</button>
  <button id="btn-clear" onclick="clearAll()">&#128465; Clear</button>
</div>

<div id="log">Ready. Hold the 8x6 checkerboard in view and press Capture.
</div>

<script>
const MIN = 15;
let count = 0;

function log(msg) {
  const el = document.getElementById('log');
  el.textContent += msg + '\n';
  el.scrollTop = el.scrollHeight;
}

function setCount(n) {
  count = n;
  document.getElementById('count').textContent = n;
  document.getElementById('progress-bar').style.width = Math.min(n / 20 * 100, 100) + '%';
  document.getElementById('btn-calibrate').disabled = n < MIN;
}

async function capture() {
  document.getElementById('btn-capture').disabled = true;
  try {
    const r = await fetch('/capture', { method: 'POST' });
    const d = await r.json();
    if (d.ok) {
      setCount(d.count);
      const boardMsg = d.board_found ? '[OK] board detected' : '[WARN] board NOT detected in this frame';
      log(`[${String(d.count).padStart(2,'0')}/20] Captured  ${boardMsg}`);
    } else {
      log('Capture failed: ' + d.error);
    }
  } finally {
    document.getElementById('btn-capture').disabled = false;
  }
}

async function runCalibration() {
  log('\nRunning calibration on ' + count + ' images...');
  document.getElementById('btn-calibrate').disabled = true;
  try {
    const r = await fetch('/calibrate', { method: 'POST' });
    const d = await r.json();
    if (d.ok) {
      log(
        `\nCalibration complete (${d.used} images used)\n` +
        `  fx = ${d.fx.toFixed(2)}   fy = ${d.fy.toFixed(2)}\n` +
        `  cx = ${d.cx.toFixed(2)}   cy = ${d.cy.toFixed(2)}\n` +
        `  reprojection error: ${d.error.toFixed(4)} px` +
        (d.error < 0.5 ? '  [OK] excellent' : d.error < 1.0 ? '  [OK] acceptable' : '  [WARN] re-run with more varied angles') +
        `\n\nSaved → lib/camera_calibration.npz`
      );
    } else {
      log('Calibration failed: ' + d.error);
    }
  } finally {
    document.getElementById('btn-calibrate').disabled = count < MIN;
  }
}

async function clearAll() {
  await fetch('/clear', { method: 'POST' });
  setCount(0);
  log('\nCaptures cleared.');
}

// Poll board detection + capture count every 500ms
setInterval(async () => {
  try {
    const d = await (await fetch('/status')).json();
    const badge = document.getElementById('badge');
    if (d.board_found) {
      badge.textContent = 'Board detected [OK]';
      badge.classList.add('found');
    } else {
      badge.textContent = 'No board';
      badge.classList.remove('found');
    }
    if (d.count !== count) setCount(d.count);
  } catch {}
}, 500);

// Keyboard shortcut: Space = capture
document.addEventListener('keydown', e => {
  if (e.code === 'Space' && !document.getElementById('btn-capture').disabled) {
    e.preventDefault();
    capture();
  }
});
</script>
</body>
</html>"""


@app.route('/')
def index():
    return HTML


@app.route('/stream')
def stream():
    return Response(_gen_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/status')
def status():
    with _lock:
        found = _board_found
    count = len(list(CAPTURES_DIR.glob('*.jpg'))) if CAPTURES_DIR.exists() else 0
    return {'board_found': found, 'count': count}


@app.route('/capture', methods=['POST'])
def capture():
    with _lock:
        raw   = _latest_raw
        found = _board_found
    if raw is None:
        return {'ok': False, 'error': 'No frame available'}
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    count = len(list(CAPTURES_DIR.glob('*.jpg')))
    cv2.imwrite(str(CAPTURES_DIR / f'capture_{count:03d}.jpg'), raw)
    return {'ok': True, 'count': count + 1, 'board_found': found}


@app.route('/clear', methods=['POST'])
def clear():
    if CAPTURES_DIR.exists():
        for f in CAPTURES_DIR.glob('*.jpg'):
            f.unlink()
    return {'ok': True}


@app.route('/calibrate', methods=['POST'])
def calibrate():
    if not CAPTURES_DIR.exists():
        return {'ok': False, 'error': 'No captures directory'}

    images = sorted(CAPTURES_DIR.glob('*.jpg'))
    if len(images) < 10:
        return {'ok': False, 'error': f'Need at least 10 images, have {len(images)}'}

    objp = np.zeros((BOARD_H * BOARD_W, 3), np.float32)
    objp[:, :2] = np.mgrid[0:BOARD_W, 0:BOARD_H].T.reshape(-1, 2)
    subpix = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    obj_pts, img_pts = [], []
    for path in images:
        img  = cv2.imread(str(path))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        found, corners = cv2.findChessboardCorners(
            gray, BOARD_SIZE,
            cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE,
        )
        if found:
            obj_pts.append(objp)
            img_pts.append(cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), subpix))

    if len(obj_pts) < 10:
        return {'ok': False, 'error': f'Board found in only {len(obj_pts)}/{len(images)} images — try recapturing with the full board clearly in frame'}

    h, w = cv2.imread(str(images[0])).shape[:2]
    _, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(obj_pts, img_pts, (w, h), None, None)

    total_err = sum(
        cv2.norm(img_pts[i], cv2.projectPoints(obj_pts[i], rvecs[i], tvecs[i], mtx, dist)[0], cv2.NORM_L2)
        / len(img_pts[i])
        for i in range(len(obj_pts))
    )
    mean_err = total_err / len(obj_pts)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez(str(OUTPUT_PATH), mtx_array=mtx, dist_array=dist)

    return {
        'ok':    True,
        'fx':    float(mtx[0, 0]),
        'fy':    float(mtx[1, 1]),
        'cx':    float(mtx[0, 2]),
        'cy':    float(mtx[1, 2]),
        'error': float(mean_err),
        'used':  len(obj_pts),
    }


if __name__ == '__main__':
    CAPTURES_DIR.mkdir(parents=True, exist_ok=True)
    threading.Thread(target=_camera_worker, daemon=True).start()
    print('\n  Open in browser -> http://<ROBOT_IP>:5000\n')
    app.run(host='0.0.0.0', port=5000, threaded=True)
