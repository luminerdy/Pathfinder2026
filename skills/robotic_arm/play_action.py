#!/usr/bin/env python3
"""
Action Group Playback (Level 1.5)

Play pre-recorded arm movement sequences.

Usage:
    python3 play_action.py stand
    python3 play_action.py shake_head
    python3 play_action.py wave

Action groups are like "macros" - pre-recorded servo movements
that play back exactly as recorded. Great for gestures, demos,
and complex sequences that are hard to program.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from lib.board import get_board
from skills.arm_control import ArmController

# Available action groups
AVAILABLE_ACTIONS = {
    'stand': 'Neutral standing position',
    'shake_head': 'Head shake gesture',
    'wave': 'Wave gesture',
    'camera_forward': 'Camera-forward position',
    'rest': 'Rest position',
}

ACTION_MAP = {
    'stand': ('position', 'rest'),
    'shake_head': ('sequence', 'shake_no'),
    'wave': ('sequence', 'wave'),
    'camera_forward': ('position', 'camera_forward'),
    'rest': ('position', 'rest'),
}

def play_action(action_name):
    """
    Play an action group.

    Args:
        action_name: Name of action (without .d6a extension)
    """
    print(f"Playing action group: {action_name}")

    board = get_board()
    controller = ArmController(board)

    action_type, mapped_name = ACTION_MAP[action_name]
    if action_type == 'sequence':
        controller.run_sequence(mapped_name)
    else:
        controller.move_to_named(mapped_name, duration_ms=800)
        time.sleep(1.0)

    print(f"Action '{action_name}' complete!")

def main():
    if len(sys.argv) < 2:
        print("=" * 60)
        print("ACTION GROUP PLAYBACK")
        print("=" * 60)
        print()
        print("Usage: python3 play_action.py <action_name>")
        print()
        print("Available actions:")
        for name, description in AVAILABLE_ACTIONS.items():
            print(f"  {name:30s} - {description}")
        print()
        print("Example:")
        print("  python3 play_action.py stand")
        print("  python3 play_action.py shake_head")
        print()
        return

    action_name = sys.argv[1]

    # Remove .d6a extension if provided
    if action_name.endswith('.d6a'):
        action_name = action_name[:-4]

    print("=" * 60)
    print(f"ACTION: {action_name}")
    print("=" * 60)
    print()

    if action_name in AVAILABLE_ACTIONS:
        print(f"Description: {AVAILABLE_ACTIONS[action_name]}")

    print()

    try:
        play_action(action_name)
        print()
        print("[OK] Success!")

    except FileNotFoundError:
        print(f"[!!] Error: Action group '{action_name}' not found")
        print()
        print("Available actions:")
        for name in AVAILABLE_ACTIONS.keys():
            print(f"  - {name}")

    except Exception as e:
        print(f"[!!] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
