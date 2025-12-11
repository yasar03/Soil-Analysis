"""
Soil Color Analysis Module using OpenCV

This module provides functionality to analyze soil colors from images
and match them to the Munsell Soil Color Chart, which is the standard
for soil color classification in geotechnical and agricultural sciences.
"""

import cv2
import numpy as np
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from typing import Tuple, Optional
import os


class ColorAnalyzer:
    """
    A class to analyze soil colors from images and match them to Munsell colors.

    The Munsell color system describes colors based on three properties:
    - Hue: The color type (e.g., 10YR, 7.5YR)
    - Value: Lightness (0 = black, 10 = white)
    - Chroma: Color saturation/intensity

    Example Munsell notation: "10YR 4/3" means Hue=10YR, Value=4, Chroma=3
    """

    def __init__(self, munsell_csv_path: str):
        """
        Initialize the ColorAnalyzer with a Munsell color reference CSV.

        Args:
            munsell_csv_path: Path to CSV file containing Munsell colors with RGB values
        """
        self.munsell_df = None
        self.knn_model = None
        self.munsell_labels = None

        if os.path.exists(munsell_csv_path):
            self._load_munsell_data(munsell_csv_path)
            self._train_classifier()
            print(f"✅ ColorAnalyzer initialized with {len(self.munsell_df)} Munsell colors")
        else:
            print(f"⚠️ Munsell CSV not found at {munsell_csv_path}. Using fallback color analysis.")

    def _load_munsell_data(self, csv_path: str) -> None:
        """Load the Munsell color reference data from CSV."""
        self.munsell_df = pd.read_csv(csv_path)

        required_cols = ['munsell_name', 'R', 'G', 'B']
        for col in required_cols:
            if col not in self.munsell_df.columns:
                raise ValueError(f"Missing required column: {col}")

    def _train_classifier(self) -> None:
        """Train a KNN classifier on the Munsell color data."""
        if self.munsell_df is None:
            return

        X = self.munsell_df[['R', 'G', 'B']].values
        self.munsell_labels = self.munsell_df['munsell_name'].values

        self.knn_model = KNeighborsClassifier(n_neighbors=1, metric='euclidean')
        self.knn_model.fit(X, self.munsell_labels)

    def analyze_color(self, image: np.ndarray, apply_white_balance: bool = True) -> str:
        """
        Analyze the dominant color of a soil image region.
        """
        if image is None or image.size == 0:
            return "Unknown"

        filtered_image = self._filter_soil_pixels(image)

        if apply_white_balance and filtered_image is not None and filtered_image.size > 0:
            filtered_image = self._apply_white_balance(filtered_image)

        if filtered_image is not None and filtered_image.size > 0:
            dominant_rgb = self._get_dominant_color_kmeans(filtered_image)
        else:
            dominant_rgb = self._get_dominant_color_kmeans(image)

        if self.knn_model is not None:
            return self._match_to_munsell(dominant_rgb)
        else:
            return self._fallback_color_description(dominant_rgb)

    def _filter_soil_pixels(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Filter out non-soil pixels from the image.
        """
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

            brightness_mask = (hsv[:, :, 2] > 25) & (hsv[:, :, 2] < 200)
            saturation_mask = hsv[:, :, 1] < 150

            hue = hsv[:, :, 0]
            hue_mask = (hue < 50) | (hue > 160) | (hsv[:, :, 1] < 30)

            combined_mask = brightness_mask & saturation_mask & hue_mask

            filtered = cv2.bitwise_and(image, image, mask=combined_mask.astype(np.uint8) * 255)

            valid_pixels = np.sum(combined_mask)
            total_pixels = image.shape[0] * image.shape[1]

            if valid_pixels < total_pixels * 0.1:  # Less than 10%
                simple_mask = (hsv[:, :, 2] > 30) & (hsv[:, :, 2] < 220)
                filtered = cv2.bitwise_and(image, image, mask=simple_mask.astype(np.uint8) * 255)

            return filtered

        except Exception as e:
            print(f"Warning: Soil filtering failed: {e}")
            return image

    def _apply_white_balance(self, image: np.ndarray) -> np.ndarray:
        """Apply white balance using Gray World algorithm."""
        img_float = image.astype(np.float32)

        avg_b = np.mean(img_float[:, :, 0])
        avg_g = np.mean(img_float[:, :, 1])
        avg_r = np.mean(img_float[:, :, 2])

        avg_gray = (avg_b + avg_g + avg_r) / 3

        avg_b = avg_b or 1
        avg_g = avg_g or 1
        avg_r = avg_r or 1

        img_float[:, :, 0] *= avg_gray / avg_b
        img_float[:, :, 1] *= avg_gray / avg_g
        img_float[:, :, 2] *= avg_gray / avg_r

        return np.clip(img_float, 0, 255).astype(np.uint8)

    def _get_dominant_color_kmeans(self, image: np.ndarray, k: int = 3) -> Tuple[int, int, int]:
        """Extract dominant soil color with K-means."""
        pixels = image.reshape(-1, 3).astype(np.float32)

        not_black = np.all(pixels > 15, axis=1)
        not_white = np.all(pixels < 240, axis=1)
        not_too_bright = np.mean(pixels, axis=1) < 220

        mask = not_black & not_white & not_too_bright
        pixels = pixels[mask]

        if len(pixels) == 0:
            return (128, 128, 128)

        avg_brightness = np.mean(pixels)
        if avg_brightness > 180:
            darker_mask = np.mean(pixels, axis=1) < 180
            if np.sum(darker_mask) > 100:
                pixels = pixels[darker_mask]

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)

        _, labels, centers = cv2.kmeans(
            pixels,
            min(k, len(pixels)),
            None,
            criteria,
            10,
            cv2.KMEANS_RANDOM_CENTERS
        )

        unique, counts = np.unique(labels, return_counts=True)
        dominant_idx = unique[np.argmax(counts)]
        dominant_bgr = centers[dominant_idx]

        return (int(dominant_bgr[2]), int(dominant_bgr[1]), int(dominant_bgr[0]))

    def _match_to_munsell(self, rgb: Tuple[int, int, int]) -> str:
        """Match RGB to nearest Munsell color."""
        rgb_array = np.array([[rgb[0], rgb[1], rgb[2]]])
        prediction = self.knn_model.predict(rgb_array)
        return prediction[0]

    def get_color_description(self, munsell_code: str) -> str:
        """Get human-readable name of Munsell color."""
        if self.munsell_df is None:
            return "Unknown"

        match = self.munsell_df[self.munsell_df['munsell_name'] == munsell_code]

        if not match.empty and 'description' in match.columns:
            return match['description'].iloc[0]

        return self._generate_description_from_code(munsell_code)

    def _generate_description_from_code(self, munsell_code: str) -> str:
        """Generate description from Munsell code."""
        code = munsell_code.upper()

        try:
            parts = code.split()
            value_chroma = parts[1].split('/')
            value = int(value_chroma[0])

            if value <= 2:
                lightness = "Black"
            elif value <= 3:
                lightness = "Very Dark"
            elif value <= 4:
                lightness = "Dark"
            elif value <= 5:
                lightness = "Medium"
            elif value <= 6:
                lightness = "Light"
            elif value <= 7:
                lightness = "Pale"
            else:
                lightness = "Very Pale"
        except:
            lightness = ""

        if 'YR' in code:
            if '10YR' in code or '7.5YR' in code:
                base = "Brown"
            elif '5YR' in code or '2.5YR' in code:
                base = "Reddish Brown"
            else:
                base = "Brown"
        elif 'Y' in code:
            if '5Y' in code:
                base = "Olive"
            else:
                base = "Yellowish Brown"
        elif 'GLEY' in code:
            base = "Gray"
        elif 'R' in code:
            base = "Red"
        else:
            base = "Gray"

        if lightness:
            return f"{lightness} {base}"
        return base

    def analyze_color_with_name(self, image: np.ndarray, apply_white_balance: bool = True) -> Tuple[str, str]:
        """Return both Munsell code and readable color name."""
        munsell_code = self.analyze_color(image, apply_white_balance)
        color_name = self.get_color_description(munsell_code)
        return (munsell_code, color_name)

    def _fallback_color_description(self, rgb: Tuple[int, int, int]) -> str:
        """Fallback when no Munsell data available."""
        r, g, b = rgb

        bgr = np.uint8([[[b, g, r]]])
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        h, s, v = hsv[0][0]

        if v < 50:
            brightness = "Dark"
        elif v < 150:
            brightness = "Medium"
        else:
            brightness = "Light"

        if s < 30:
            saturation = "Grayish"
        elif s < 100:
            saturation = ""
        else:
            saturation = "Vivid"

        if s < 30:
            hue_name = "Gray"
        elif h < 15 or h > 165:
            hue_name = "Reddish"
        elif h < 25:
            hue_name = "Orange"
        elif h < 35:
            hue_name = "Yellowish Brown"
        elif h < 85:
            hue_name = "Brown"
        else:
            hue_name = "Grayish Brown"

        return " ".join([p for p in [brightness, saturation, hue_name] if p])

    def get_color_histogram(self, image: np.ndarray) -> dict:
        """Return color histogram data."""
        histograms = {}
        colors = ['Blue', 'Green', 'Red']

        for i, color in enumerate(colors):
            hist = cv2.calcHist([image], [i], None, [256], [0, 256])
            histograms[color] = hist.flatten().tolist()

        return histograms

    def analyze_color_distribution(self, image: np.ndarray, n_colors: int = 5) -> list:
        """Analyze dominant color groups in an image."""
        pixels = image.reshape(-1, 3).astype(np.float32)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(
            pixels,
            n_colors,
            None,
            criteria,
            10,
            cv2.KMEANS_RANDOM_CENTERS
        )

        unique, counts = np.unique(labels, return_counts=True)
        total_pixels = len(labels)

        color_distribution = []

        for cluster_id, count in zip(unique, counts):
            bgr = centers[cluster_id]
            rgb = (int(bgr[2]), int(bgr[1]), int(bgr[0]))
            percentage = (count / total_pixels) * 100

            info = {
                'rgb': rgb,
                'hex': '#{:02x}{:02x}{:02x}'.format(*rgb),
                'percentage': round(percentage, 2)
            }

            if self.knn_model is not None:
                info['munsell'] = self._match_to_munsell(rgb)

            color_distribution.append(info)

        return sorted(color_distribution, key=lambda x: x['percentage'], reverse=True)


def analyze_soil_color_simple(image_path: str) -> dict:
    """
    Simple standalone soil color analysis.
    """
    image = cv2.imread(image_path)
    if image is None:
        return {'error': 'Could not read image'}

    pixels = image.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)

    _, labels, centers = cv2.kmeans(
        pixels,
        3,
        None,
        criteria,
        10,
        cv2.KMEANS_RANDOM_CENTERS
    )

    unique, counts = np.unique(labels, return_counts=True)
    dominant_idx = unique[np.argmax(counts)]
    dominant_bgr = centers[dominant_idx]

    dominant_rgb = (int(dominant_bgr[2]), int(dominant_bgr[1]), int(dominant_bgr[0]))

    return {
        'dominant_color_rgb': dominant_rgb,
        'dominant_color_hex': '#{:02x}{:02x}{:02x}'.format(*dominant_rgb),
        'image_dimensions': (image.shape[1], image.shape[0]),
        'total_pixels_analyzed': len(pixels)
    }
