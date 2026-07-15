#!/usr/bin/env python3
"""
Block Detection Skill

Detects colored blocks on the floor using HSV color filtering.
Returns block position, estimated distance, and tracking info.

Design:
- Color is primary detection (works at distance)
- Shape validation when close (filter noise)
- Known block size (30mm) enables distance estimation
- Optimized for low-saturation floor (blocks = high saturation)

Block size: 1.2 inches = 30mm
Camera: 640x480, fx~500

Distance estimation:
  pixel_width = (focal_length * real_width) / distance
  distance_mm = (500 * 30) / pixel_width
"""

import cv2
import numpy as np
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class BlockDetection:
    """Single detected block"""
    color: str              # 'red', 'green', 'blue'
    center_x: int           # pixel X (0-640)
    center_y: int           # pixel Y (0-480)
    width: int              # bounding box width (pixels)
    height: int             # bounding box height (pixels)
    area: int               # contour area (pixels)
    aspect_ratio: float     # min/max of width/height (1.0 = square)
    offset_from_center: int # pixels from frame center (positive = right)
    estimated_distance_mm: float  # estimated distance in mm
    confidence: float       # 0.0 - 1.0


# HSV color ranges tuned for indoor lighting on neutral floor
# These work best with saturated colored blocks on a gray/neutral surface
# Workshop challenge colors: Red, Blue, Yellow
# Chosen for maximum HSV separation and reliable detection
# Red is intentionally tighter than blue/yellow because workshop lighting and
# shadows can create small reddish false positives on the foam floor.
# Red: H=0-8 + 172-180 with S>=110/V>=80
# Blue: H=100-130 with S>=85/V>=60
# Yellow: H=20-40
COLOR_RANGES = {
    'red': [
        {'lower': (0, 110, 80), 'upper': (8, 255, 255)},       # Low red
        {'lower': (172, 110, 80), 'upper': (180, 255, 255)},   # High red (wraps)
    ],
    'blue': [
        # Blue needs a higher saturation/value floor to avoid shadow ghosts on
        # the dark foam tiles.
        {'lower': (100, 85, 60), 'upper': (130, 255, 255)},
    ],
    'yellow': [
        {'lower': (20, 80, 50), 'upper': (40, 255, 255)},
    ],
}

# Detection parameters
FOCAL_LENGTH = 500          # Estimated camera focal length (pixels)
BLOCK_SIZE_MM = 30          # Real block size (1.2 inches)
FRAME_CENTER_X = 320        # 640 / 2
MIN_AREA = 30               # Minimum contour area
MIN_ASPECT = 0.4            # Minimum aspect ratio
MAX_AREA = 5000             # Maximum area (1.2" block can't be huge)
MIN_CONFIDENCE = 0.3        # Lowered — was missing real blocks at 0.5


class BlockDetector:
    """
    Detects colored blocks in camera frames.

    Usage:
        detector = BlockDetector()
        blocks = detector.detect(frame)
        blocks = detector.detect(frame, colors=['red'])
        nearest = detector.find_nearest(frame, color='red')
        merged = detector.merge_close_detections(blocks)
        target = detector.select_pickup_target(merged)
    """

    def __init__(self, colors=None):
        """
        Args:
            colors: List of colors to detect. Default: all defined colors.
        """
        self.colors = colors or list(COLOR_RANGES.keys())
        self.kernel = np.ones((3, 3), np.uint8)

    def _create_mask(self, hsv, color):
        """Create combined mask for a color (handles red wrapping)"""
        ranges = COLOR_RANGES.get(color, [])
        if not ranges:
            return np.zeros(hsv.shape[:2], dtype=np.uint8)

        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for r in ranges:
            lower = np.array(r['lower'])
            upper = np.array(r['upper'])
            mask |= cv2.inRange(hsv, lower, upper)

        # Clean up: remove noise, fill gaps
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)

        return mask

    def _estimate_distance(self, pixel_width):
        """Estimate distance from known block size and apparent pixel size"""
        if pixel_width <= 0:
            return float('inf')
        return (FOCAL_LENGTH * BLOCK_SIZE_MM) / pixel_width

    def _compute_confidence(self, area, aspect_ratio, pixel_width):
        """
        Compute detection confidence (0-1).
        Higher when: larger area, squarer shape, reasonable size.
        """
        conf = 1.0

        # Aspect ratio: 1.0 is perfect square, penalize elongated
        if aspect_ratio < 0.6:
            conf *= 0.5
        elif aspect_ratio < 0.8:
            conf *= 0.8

        # Area: very small = low confidence
        if area < 50:
            conf *= 0.3
        elif area < 100:
            conf *= 0.6
        elif area < 200:
            conf *= 0.8

        # Size reasonableness: a 30mm block should be 5-200 pixels wide
        if pixel_width < 5:
            conf *= 0.3  # Too small to be reliable
        elif pixel_width > 200:
            conf *= 0.5  # Probably not a single block

        return min(conf, 1.0)

    def detect(self, frame, colors=None):
        """
        Detect all visible blocks in frame.

        Args:
            frame: BGR image (640x480)
            colors: Override which colors to detect

        Returns:
            List of BlockDetection, sorted by distance (nearest first)
        """
        if colors is None:
            colors = self.colors

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        detections = []

        for color in colors:
            mask = self._create_mask(hsv, color)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                           cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < MIN_AREA or area > MAX_AREA:
                    continue

                x, y, w, h = cv2.boundingRect(contour)
                aspect = min(w, h) / max(w, h) if max(w, h) > 0 else 0

                if aspect < MIN_ASPECT:
                    continue

                cx = x + w // 2
                cy = y + h // 2
                pixel_width = max(w, h)

                dist_mm = self._estimate_distance(pixel_width)
                confidence = self._compute_confidence(area, aspect, pixel_width)
                offset = cx - FRAME_CENTER_X

                if confidence < MIN_CONFIDENCE:
                    continue

                detections.append(BlockDetection(
                    color=color,
                    center_x=cx,
                    center_y=cy,
                    width=w,
                    height=h,
                    area=area,
                    aspect_ratio=aspect,
                    offset_from_center=offset,
                    estimated_distance_mm=dist_mm,
                    confidence=confidence
                ))

        # Sort by distance (nearest first)
        detections.sort(key=lambda d: d.estimated_distance_mm)

        return detections

    def find_nearest(self, frame, color=None):
        """
        Find the nearest block, optionally of a specific color.

        Args:
            frame: BGR image
            color: Specific color to find, or None for any

        Returns:
            BlockDetection or None
        """
        colors = [color] if color else None
        blocks = self.detect(frame, colors=colors)

        # Return highest confidence block among the nearest
        if not blocks:
            return None

        # Among blocks within 20% of nearest distance, pick highest confidence
        nearest_dist = blocks[0].estimated_distance_mm
        candidates = [b for b in blocks
                      if b.estimated_distance_mm < nearest_dist * 1.2]

        return max(candidates, key=lambda b: b.confidence)

    def _block_bounds(self, block):
        """Return bounding-box edges for a detection."""
        x1 = block.center_x - block.width // 2
        y1 = block.center_y - block.height // 2
        x2 = x1 + block.width
        y2 = y1 + block.height
        return x1, y1, x2, y2

    def _boxes_close(self, first, second, padding_px=18):
        """Return True when two same-color boxes likely belong together."""
        ax1, ay1, ax2, ay2 = self._block_bounds(first)
        bx1, by1, bx2, by2 = self._block_bounds(second)

        return not (
            ax2 + padding_px < bx1 or
            bx2 + padding_px < ax1 or
            ay2 + padding_px < by1 or
            by2 + padding_px < ay1
        )

    def merge_close_detections(self, detections, padding_px=18):
        """
        Merge nearby same-color detections into one block candidate.

        Real cubes sometimes split into two contours because of highlights or
        shadows. Merging nearby boxes keeps target selection from flickering.
        """
        remaining = list(detections)
        merged = []

        while remaining:
            group = [remaining.pop(0)]
            changed = True
            while changed:
                changed = False
                for candidate in remaining[:]:
                    if candidate.color != group[0].color:
                        continue
                    if any(self._boxes_close(candidate, item, padding_px) for item in group):
                        group.append(candidate)
                        remaining.remove(candidate)
                        changed = True

            if len(group) == 1:
                merged.append(group[0])
                continue

            x1 = min(self._block_bounds(block)[0] for block in group)
            y1 = min(self._block_bounds(block)[1] for block in group)
            x2 = max(self._block_bounds(block)[2] for block in group)
            y2 = max(self._block_bounds(block)[3] for block in group)

            width = max(1, int(x2 - x1))
            height = max(1, int(y2 - y1))
            center_x = int(x1 + width / 2)
            center_y = int(y1 + height / 2)
            pixel_width = max(width, height)
            aspect = min(width, height) / max(width, height)

            merged.append(BlockDetection(
                color=group[0].color,
                center_x=center_x,
                center_y=center_y,
                width=width,
                height=height,
                area=sum(block.area for block in group),
                aspect_ratio=aspect,
                offset_from_center=center_x - FRAME_CENTER_X,
                estimated_distance_mm=self._estimate_distance(pixel_width),
                confidence=max(block.confidence for block in group),
            ))

        merged.sort(key=lambda d: d.estimated_distance_mm)
        return merged

    def _is_edge_touching(self, block, frame_width=640, frame_height=480,
                          margin_px=8):
        """Return True when a block box touches the unreliable image edge."""
        x1, y1, x2, y2 = self._block_bounds(block)
        return (
            x1 <= margin_px or
            y1 <= margin_px or
            x2 >= frame_width - margin_px or
            y2 >= frame_height - margin_px
        )

    def pickup_target_score(self, block, frame_width=640, frame_height=480):
        """
        Score a detected block for pickup approach.

        Higher score means the block is more useful as a target:
        confident, near center, lower in the image, and reasonably large.
        """
        center_score = 1.0 - min(abs(block.offset_from_center) / (frame_width / 2), 1.0)
        lower_score = min(max(block.center_y / frame_height, 0.0), 1.0)
        size_score = min(max(max(block.width, block.height) / 80.0, 0.0), 1.0)
        distance_score = 1.0 - min(block.estimated_distance_mm / 1500.0, 1.0)

        return round(
            block.confidence * 4.0 +
            center_score * 3.0 +
            lower_score * 2.0 +
            size_score * 2.0 +
            distance_score,
            3
        )

    def select_pickup_target(self, detections, frame_width=640, frame_height=480,
                             min_confidence=0.6, min_area=80,
                             edge_margin_px=8):
        """
        Pick the best block for a future pickup approach.

        This does not move the robot. It filters out weak/edge detections and
        chooses the candidate with the best pickup target score.
        """
        candidates = []
        for block in detections:
            if block.confidence < min_confidence:
                continue
            if block.area < min_area:
                continue
            if self._is_edge_touching(
                block,
                frame_width=frame_width,
                frame_height=frame_height,
                margin_px=edge_margin_px,
            ):
                continue
            candidates.append(block)

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda block: self.pickup_target_score(
                block,
                frame_width=frame_width,
                frame_height=frame_height,
            )
        )

    def annotate_frame(self, frame, detections):
        """
        Draw detection boxes and labels on frame.

        Args:
            frame: BGR image (modified in place)
            detections: List of BlockDetection

        Returns:
            Annotated frame
        """
        color_bgr = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'yellow': (0, 255, 255),
            'green': (0, 255, 0),
        }

        for det in detections:
            bgr = color_bgr.get(det.color, (255, 255, 255))

            # Bounding box
            x1 = det.center_x - det.width // 2
            y1 = det.center_y - det.height // 2
            cv2.rectangle(frame, (x1, y1), (x1 + det.width, y1 + det.height), bgr, 2)

            # Label
            dist_cm = det.estimated_distance_mm / 10
            label = f"{det.color} {dist_cm:.0f}cm c={det.confidence:.1f}"
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, bgr, 1)

            # Center dot
            cv2.circle(frame, (det.center_x, det.center_y), 3, bgr, -1)

        return frame


if __name__ == '__main__':
    """Demo: Detect blocks in current camera view"""
    import time

    print("BLOCK DETECTION DEMO")
    print("="*70)
    print()
    print("Colors: " + ", ".join(COLOR_RANGES.keys()))
    print(f"Block size: {BLOCK_SIZE_MM}mm (1.2 inches)")
    print()

    camera = cv2.VideoCapture(0)
    time.sleep(1.5)

    detector = BlockDetector()

    # Take 5 frames and show results
    for i in range(5):
        ret, frame = camera.read()
        if not ret:
            continue

        raw_blocks = detector.detect(frame)
        blocks = detector.merge_close_detections(raw_blocks)

        if i == 0:  # First frame detailed output
            if blocks:
                print(f"Detected {len(blocks)} block(s) "
                      f"(merged from {len(raw_blocks)} raw detection(s)):")
                for b in blocks:
                    print(f"  {b.color}: {b.estimated_distance_mm/10:.0f}cm away, "
                          f"{b.width}x{b.height}px, "
                          f"offset={b.offset_from_center:+d}px, "
                          f"conf={b.confidence:.2f}")
                target = detector.select_pickup_target(blocks)
                if target:
                    score = detector.pickup_target_score(target)
                    print()
                    print("Selected pickup target:")
                    print(f"  {target.color}: score={score:.1f}, "
                          f"{target.estimated_distance_mm/10:.0f}cm away, "
                          f"offset={target.offset_from_center:+d}px")
            else:
                print("No blocks detected")
                print("  (Place colored blocks in view and try again)")
            print()

        time.sleep(0.2)

    # Save annotated frame
    if blocks:
        frame = detector.annotate_frame(frame, blocks)

    output_path = Path(__file__).resolve().parents[1] / 'block_detect_result.jpg'
    cv2.imwrite(str(output_path), frame)
    print(f"Saved annotated frame: {output_path}")

    camera.release()
    print("Done")
