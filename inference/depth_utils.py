"""
Depth Estimation Module for Soil Profile Analysis

This module provides functionality to estimate the depth of soil layers
based on their position in the image and a known pixel-to-centimeter ratio.
"""

import cv2
import numpy as np
from typing import Tuple, Optional


def estimate_depth(
    image: np.ndarray,
    bounding_box: Tuple[int, int, int, int],
    pixel_cm_ratio: float = 10.0,
    reference_top_cm: float = 0.0
) -> Tuple[float, float]:
    """
    Estimate the depth range of a detected soil layer in centimeters.
    """
    x0, y0, x1, y1 = bounding_box

    # Validate pixel_cm_ratio
    if pixel_cm_ratio <= 0:
        pixel_cm_ratio = 10.0

    # Convert pixel positions to depth (y-axis represents depth)
    top_depth_cm = reference_top_cm + (y0 / pixel_cm_ratio)
    bottom_depth_cm = reference_top_cm + (y1 / pixel_cm_ratio)

    # Round to 1 decimal place
    top_depth_cm = round(top_depth_cm, 1)
    bottom_depth_cm = round(bottom_depth_cm, 1)

    return (top_depth_cm, bottom_depth_cm)


def detect_ruler_and_calibrate(image: np.ndarray) -> Optional[float]:
    """
    Attempt to automatically detect a ruler in the image and calculate
    the pixel-to-centimeter ratio.
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150)

    # Detect lines
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180, threshold=50,
        minLineLength=20, maxLineGap=5
    )

    if lines is None:
        return None

    # Filter vertical lines
    vertical_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 - x1 != 0:
            angle = abs(np.degrees(np.arctan((y2 - y1) / (x2 - x1))))
            if angle > 70:  # within 20 degrees of vertical
                vertical_lines.append(line[0])

    if len(vertical_lines) < 2:
        return None

    # Sort by x position
    x_positions = sorted([line[0] for line in vertical_lines])

    if len(x_positions) < 3:
        return None

    # Spacing between lines
    spacings = [
        x_positions[i + 1] - x_positions[i]
        for i in range(len(x_positions) - 1)
    ]

    avg_spacing = np.mean(spacings)
    std_spacing = np.std(spacings)

    # If spacing is consistent → possible ruler
    if std_spacing < avg_spacing * 0.2:
        return avg_spacing  # assume 1cm marks

    return None


def calculate_layer_thickness(
    top_depth_cm: float,
    bottom_depth_cm: float
) -> float:
    """Calculate thickness of a layer."""
    return round(abs(bottom_depth_cm - top_depth_cm), 1)


def format_depth_range(depth_tuple: Tuple[float, float]) -> str:
    """Format depth range as string."""
    top, bottom = depth_tuple
    return f"{top} - {bottom} cm"


def estimate_total_profile_depth(image: np.ndarray, pixel_cm_ratio: float = 10.0) -> float:
    """Estimate overall profile depth."""
    height = image.shape[0]
    return round(height / pixel_cm_ratio, 1)


def get_depth_zones(total_depth_cm: float, n_zones: int = 4) -> list:
    """
    Divide the soil profile into depth zones.
    """
    zone_height = total_depth_cm / n_zones

    zone_names = ["Surface", "Shallow", "Medium", "Deep"]
    if n_zones > 4:
        zone_names = [f"Zone {i+1}" for i in range(n_zones)]

    zones = []
    for i in range(n_zones):
        name = zone_names[i] if i < len(zone_names) else f"Zone {i+1}"
        top = round(i * zone_height, 1)
        bottom = round((i + 1) * zone_height, 1)
        zones.append((name, top, bottom))

    return zones


class DepthCalibrator:
    """
    Manage depth calibration for profile images.
    """

    def __init__(self, pixel_cm_ratio: float = 10.0):
        self.pixel_cm_ratio = pixel_cm_ratio
        self.reference_points = []

    def add_reference_point(self, pixel_y: int, depth_cm: float) -> None:
        """Add calibration reference."""
        self.reference_points.append((pixel_y, depth_cm))

        # Recalculate ratio if 2+ points exist
        if len(self.reference_points) >= 2:
            self._recalculate_ratio()

    def _recalculate_ratio(self) -> None:
        """Recompute pixel/cm ratio from reference points."""
        if len(self.reference_points) < 2:
            return

        sorted_points = sorted(self.reference_points, key=lambda x: x[0])

        ratios = []
        for i in range(len(sorted_points) - 1):
            p1, d1 = sorted_points[i]
            p2, d2 = sorted_points[i + 1]

            pixel_diff = p2 - p1
            depth_diff = d2 - d1

            if depth_diff != 0:
                ratios.append(pixel_diff / depth_diff)

        if ratios:
            self.pixel_cm_ratio = np.mean(ratios)

    def get_depth_at_pixel(self, pixel_y: int) -> float:
        """Convert pixel y-position to depth."""
        if self.reference_points:
            ref_pixel, ref_depth = self.reference_points[0]
            return ref_depth + ((pixel_y - ref_pixel) / self.pixel_cm_ratio)
        else:
            return pixel_y / self.pixel_cm_ratio

    def get_calibration_info(self) -> dict:
        """Return calibration info."""
        return {
            "pixel_cm_ratio": self.pixel_cm_ratio,
            "reference_points": self.reference_points,
            "cm_per_pixel": 1 / self.pixel_cm_ratio if self.pixel_cm_ratio > 0 else 0
        }
