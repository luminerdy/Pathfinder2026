#!/usr/bin/env python3
"""
Camera-only web viewer for Pathfinder2026.

This is for setup testing only. It opens the USB camera and serves a live
browser view without robot movement or servo controls.

Usage:
    python3 web/camera_view.py
    Then open: http://<ROBOT_IP>:8080
"""

import atexit
import time

import cv2
from flask import Flask, Response


app = Flask(__name__)
camera = None


def get_camera():
    """Open the first USB camera lazily."""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        time.sleep(0.5)
    return camera


def generate_frames():
    """Yield MJPEG frames for the browser."""
    while True:
        cam = get_camera()
        success, frame = cam.read()
        if not success:
            time.sleep(0.2)
            continue

        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


@app.route("/")
def index():
    """Serve a simple camera-only page."""
    return """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pathfinder2026 Camera Test</title>
  <style>
    body {
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #101418;
      color: #f4f7fb;
      font-family: Arial, sans-serif;
    }
    main {
      width: min(960px, calc(100vw - 32px));
    }
    h1 {
      margin: 0 0 12px;
      font-size: 28px;
      font-weight: 700;
    }
    p {
      margin: 0 0 16px;
      color: #c8d1dc;
      font-size: 16px;
    }
    img {
      display: block;
      width: 100%;
      aspect-ratio: 4 / 3;
      object-fit: contain;
      background: #000;
      border: 1px solid #303943;
    }
  </style>
</head>
<body>
  <main>
    <h1>Camera Test</h1>
    <p>Live view from the robot USB camera.</p>
    <img src="/video_feed" alt="Live camera feed">
  </main>
</body>
</html>
"""


@app.route("/video_feed")
@app.route("/stream")
def video_feed():
    """Video streaming route."""
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


def release_camera():
    if camera is not None and camera.isOpened():
        camera.release()


atexit.register(release_camera)


if __name__ == "__main__":
    print("=" * 70)
    print("Pathfinder2026 Camera Test")
    print("=" * 70)
    print()
    print("Starting camera-only web viewer...")
    print("Open in browser: http://<ROBOT_IP>:8080")
    print()
    print("Press Ctrl+C in this terminal to stop the camera viewer.")
    print()

    app.run(host="0.0.0.0", port=8080, threaded=True)
