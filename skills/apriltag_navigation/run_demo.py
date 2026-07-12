#!/usr/bin/env python3
"""
AprilTag Navigation Demo (Level 1: Just Run It!)

This is the simplest way to use AprilTag navigation.
Just run this script and watch the robot find and approach one of the
Pathfinder2026 event AprilTags: 582, 583, 584, or 585.

No code changes needed - everything is pre-configured.

Usage:
    python3 run_demo.py

What it does:
    1. Opens camera
    2. Turns a little at a time until it finds event AprilTag IDs 582-585
    3. When found, approaches to ~20 inches
    4. Stops and beeps when complete

Press Ctrl+C to stop at any time.
"""

import sys
import os

# Add parent directory to path so we can import from skills
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from skills.strafe_nav import StrafeNavigator


EVENT_TAG_IDS = (582, 583, 584, 585)
TARGET_DISTANCE_METERS = 0.50
SEARCH_TIMEOUT_SECONDS = 20.0
NAVIGATION_TIMEOUT_SECONDS = 30.0


def main():
    print("=" * 60)
    print("APRILTAG NAVIGATION DEMO")
    print("=" * 60)
    print()
    print("Looking for event AprilTags: %s" % ", ".join(str(t) for t in EVENT_TAG_IDS))
    print("The robot will turn in small steps while searching.")
    print("Make sure:")
    print("  - Tag is printed and mounted on wall")
    print("  - Tag is at robot's camera height (~8-10 inches)")
    print("  - Good lighting, no glare on tag")
    print("  - Robot is 3-5 feet from tag")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 60)
    print()
    
    # Create navigator
    nav = StrafeNavigator()
    
    try:
        # Search for the closest visible event tag, then approach it.
        result = nav.search_and_navigate(
            target_ids=EVENT_TAG_IDS,
            target_distance=TARGET_DISTANCE_METERS,
            search_timeout=SEARCH_TIMEOUT_SECONDS,
            nav_timeout=NAVIGATION_TIMEOUT_SECONDS,
        )
        
        if result['success']:
            print()
            print("=" * 60)
            print(f"SUCCESS! Reached tag {result['tag_id']}")
            print(f"Final distance: {result['final_distance']:.2f}m")
            print("=" * 60)
            
            # Victory beep
            nav.board.set_buzzer(1000, 0.1, 0.1, 2)
            
        else:
            print()
            print("=" * 60)
            print("STOPPED: Could not reach an event AprilTag")
            print(f"Reason: {result['reason']}")
            print("=" * 60)
            print()
            print("Troubleshooting:")
            print("  - Is tag visible in camera view?")
            print("  - Try moving robot closer")
            print("  - Check lighting (no glare)")
            print("  - Verify the tag is one of: %s" % ", ".join(str(t) for t in EVENT_TAG_IDS))
    
    except KeyboardInterrupt:
        print()
        print("Stopped by user (Ctrl+C)")
    
    except Exception as e:
        print()
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Always stop motors and close camera
        nav.cleanup()
        print()
        print("Demo complete.")

if __name__ == "__main__":
    main()
