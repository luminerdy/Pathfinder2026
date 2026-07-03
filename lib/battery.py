"""
Shared battery voltage helpers for Pathfinder2026.

Keep battery thresholds here so startup checks, demos, and robot skills agree.
"""

from lib.board import PLATFORM


MIN_RUNTIME_PI4 = 7.0
MIN_RUNTIME_PI5 = 8.1
GOOD_RUNTIME_VOLTAGE = 7.5
CALIBRATED_MOVEMENT_VOLTAGE = 8.2
# Ignore readings outside this range because they usually mean communication failed.
VALID_MIN_MV = 5000
VALID_MAX_MV = 20000


def runtime_minimum(platform=None):
    """Minimum voltage allowed before robot code should refuse motor-heavy work."""
    platform = platform or PLATFORM
    return MIN_RUNTIME_PI4 if platform == 'pi4' else MIN_RUNTIME_PI5


def voltage_from_mv(mv):
    """Convert a board millivolt reading to volts, or None if invalid."""
    # The board reports millivolts, so 8000 means 8.0 volts.
    if mv and VALID_MIN_MV < mv < VALID_MAX_MV:
        return mv / 1000.0
    return None


def read_voltage(board, retries=1, delay=0.0):
    """Read battery voltage from a board, retrying short invalid readings."""
    if delay:
        import time

    for attempt in range(retries):
        voltage = voltage_from_mv(board.get_battery())
        if voltage is not None:
            return voltage
        if delay and attempt < retries - 1:
            # A short retry helps when the board has not sent a fresh value yet.
            time.sleep(delay)
    return None


def is_runtime_safe(voltage, platform=None):
    """True when voltage is high enough for runtime use."""
    return voltage is not None and voltage >= runtime_minimum(platform)


def is_calibrated_movement_ready(voltage):
    """True when voltage is high enough for legacy calibrated movement values."""
    return voltage is not None and voltage >= CALIBRATED_MOVEMENT_VOLTAGE


def status_for_voltage(voltage, platform=None):
    """Return (status, message, runtime_safe) for participant-facing output."""
    minimum = runtime_minimum(platform)
    # Return both a short status and a sentence the scripts can print directly.
    if voltage is None:
        return 'UNKNOWN', 'Cannot read battery voltage.', False
    if voltage < minimum:
        return 'LOW', 'Replace or charge batteries before motor operation.', False
    if voltage < GOOD_RUNTIME_VOLTAGE:
        return 'CAUTION', 'Light testing only; replace soon.', True
    if voltage < CALIBRATED_MOVEMENT_VOLTAGE:
        return 'OK', 'Normal testing permitted; calibrated turns may vary.', True
    return 'EXCELLENT', 'Ready for calibrated movement tests.', True
