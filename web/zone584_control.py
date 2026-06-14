"""
Zone 584 Field Controller

Drive the robot into position via browser, then launch Zone584Navigator.

Usage (on robot):
    cd ~/pathfinder
    PYTHONPATH=/home/robot/pathfinder python3 web/zone584_control.py

Open in browser: http://10.10.10.142:5000
"""

import sys
import os
import time
import threading
import collections
import subprocess
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, Response, jsonify, request, render_template
from robot import Robot
from skills.zone584_nav import Zone584Navigator

# ── App + shared state ──────────────────────────────────────────────────────

app = Flask(__name__)

robot = None    # initialized in main block so we don't init hardware on import
nav_running   = False
nav_log       = collections.deque(maxlen=200)
nav_log_lock  = threading.Lock()
_log_seq      = 0   # monotonic counter so client can detect new lines cheaply

DRIVE_POWER = 40


# ── Nav thread ──────────────────────────────────────────────────────────────

def _log(tag_id, dist, angle, msg):
    global _log_seq
    dist_s  = ('%.2fm'  % dist)  if dist  is not None else '---'
    angle_s = ('%+.1fd' % angle) if angle is not None else '---'
    line = '[%s] %s %s  %s' % (tag_id or '---', dist_s, angle_s, msg)
    with nav_log_lock:
        _log_seq += 1
        nav_log.append(line)


def _run_nav():
    global nav_running
    nav_running = True
    _log(None, None, None, '--- Zone584Navigator started ---')
    try:
        nav    = Zone584Navigator(robot)
        result = nav.navigate(timeout=90, callback=_log)
        status = 'SUCCESS' if result['success'] else 'FAILED'
        _log(584, result.get('final_distance'), result.get('final_angle'),
             'DONE: %s / %s' % (status, result['reason']))
    except Exception as e:
        _log(None, None, None, 'ERROR: %s' % str(e))
    finally:
        nav_running = False
        robot.stop()


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('zone584.html')


# Live MJPEG stream
def _gen_frames():
    while True:
        frame = robot.camera.get_raw_frame()
        if frame is None:
            time.sleep(0.04)
            continue

        # Overlay: nav status
        if nav_running:
            cv2.putText(frame, 'NAV ACTIVE', (10, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        # Overlay: battery
        v = robot.battery
        if v:
            color = (0, 200, 0) if v > 7.8 else (0, 140, 255) if v > 7.4 else (0, 0, 255)
            cv2.putText(frame, '%.2fV' % v, (540, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        _, buf = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
               + buf.tobytes() + b'\r\n')


@app.route('/stream')
def stream():
    return Response(_gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/drive', methods=['POST'])
def drive():
    if nav_running:
        return jsonify(ok=False, msg='Nav is running - stop it first')

    d = request.json.get('direction', 'stop')
    p = DRIVE_POWER

    if   d == 'forward':      robot.board.set_motor_duty([(1, p),(2, p),(3, p),(4, p)])
    elif d == 'backward':     robot.board.set_motor_duty([(1,-p),(2,-p),(3,-p),(4,-p)])
    elif d == 'left':         robot.board.set_motor_duty([(1,-p),(2, p),(3,-p),(4, p)])
    elif d == 'right':        robot.board.set_motor_duty([(1, p),(2,-p),(3, p),(4,-p)])
    elif d == 'strafe_left':  robot.board.set_motor_duty([(1,-p),(2, p),(3, p),(4,-p)])
    elif d == 'strafe_right': robot.board.set_motor_duty([(1, p),(2,-p),(3,-p),(4, p)])
    else:                     robot.stop()

    return jsonify(ok=True)


@app.route('/arm/camera_forward', methods=['POST'])
def arm_camera_forward():
    robot.arm.camera_forward()
    return jsonify(ok=True)


@app.route('/nav/start', methods=['POST'])
def nav_start():
    if nav_running:
        return jsonify(ok=False, msg='Already running')
    with nav_log_lock:
        nav_log.clear()
    t = threading.Thread(target=_run_nav, daemon=True)
    t.start()
    return jsonify(ok=True)


@app.route('/nav/stop', methods=['POST'])
def nav_stop():
    robot.stop()
    return jsonify(ok=True)


@app.route('/nav/log')
def nav_log_route():
    with nav_log_lock:
        lines = list(nav_log)
        seq   = _log_seq
    return jsonify(lines=lines, seq=seq, running=nav_running)


@app.route('/battery')
def battery():
    v = robot.battery
    return jsonify(voltage=v, ok=robot.battery_ok)


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('=' * 55)
    print('Zone 584 Field Controller')
    print('=' * 55)

    robot = Robot(enable_camera=True)

    # Set manual exposure=5 — empirically tested for outdoor field lighting.
    # Auto-exposure (value=3) settles at ~60 which is still too bright.
    # exp=5 -> brightness ~144, exp=10 -> ~186. 5 is the sweet spot.
    subprocess.run(
        ['v4l2-ctl', '-d', '/dev/video0',
         '--set-ctrl=auto_exposure=1',
         '--set-ctrl=exposure_time_absolute=5'],
        capture_output=True
    )
    time.sleep(1.0)
    print('Camera: manual exposure=5 (outdoor field setting)')

    print('Arm -> camera_forward...')
    robot.arm.camera_forward()
    time.sleep(1.0)

    v = robot.battery
    print('Battery: %.2fV' % v if v else 'Battery: unknown')
    print()
    print('Open in browser: http://10.10.10.142:5000')
    print('Controls: WASD / arrow keys, Q/E to strafe')
    print('Ctrl-C to quit')
    print()

    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        robot.stop()
        robot.shutdown()
