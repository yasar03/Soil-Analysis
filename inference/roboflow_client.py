"""
Roboflow API Client for Soil Classification

This module handles communication with the Roboflow API for object detection
and soil classification from images.
"""

import os
import requests
from typing import Optional
import base64


# Roboflow API configuration
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "your_api_key_here")
ROBOFLOW_MODEL_ID = os.getenv("ROBOFLOW_MODEL_ID", "soil-classification")
ROBOFLOW_VERSION = os.getenv("ROBOFLOW_VERSION", "1")
ROBOFLOW_API_URL = f"https://detect.roboflow.com/{ROBOFLOW_MODEL_ID}/{ROBOFLOW_VERSION}"


def get_roboflow_predictions(image_path: str, confidence_threshold: float = 0.4) -> dict:
    """
    Send an image to Roboflow for soil classification predictions.
    
    Args:
        image_path: Path to the image file
        confidence_threshold: Minimum confidence score for predictions (0.0-1.0)
        
    Returns:
        Dictionary containing predictions with bounding boxes and classifications
        
    Example response:
        {
            "predictions": [
                {
                    "x": 150,        # Center x coordinate
                    "y": 200,        # Center y coordinate
                    "width": 100,    # Bounding box width
                    "height": 80,    # Bounding box height
                    "class": "clay", # Soil classification
                    "confidence": 0.92
                }
            ],
            "image": {
                "width": 640,
                "height": 480
            }
        }
    """
    # Check if using demo mode (no API key)
    if ROBOFLOW_API_KEY == "your_api_key_here":
        print("⚠️ Roboflow API key not set. Using demo predictions.")
        return _get_demo_predictions(image_path)
    
    try:
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Prepare the request
        params = {
            "api_key": ROBOFLOW_API_KEY,
            "confidence": confidence_threshold
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # Make the API request
        response = requests.post(
            ROBOFLOW_API_URL,
            params=params,
            data=image_data,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Roboflow API error: {e}")
        return _get_demo_predictions(image_path)


def _get_demo_predictions(image_path: str) -> dict:
    """
    Generate demo predictions when Roboflow API is not available.
    
    This creates sample soil layer predictions for testing purposes.
    """
    import cv2
    
    # Try to read the image to get dimensions
    image = cv2.imread(image_path)
    if image is None:
        # Default dimensions if image can't be read
        width, height = 640, 480
    else:
        height, width = image.shape[:2]
    
    # Generate demo soil layer predictions
    # Divides the image into horizontal layers (typical for soil profiles)
    layer_height = height // 4
    
    demo_predictions = {
        "predictions": [
            {
                "x": width // 2,
                "y": layer_height // 2,
                "width": width - 40,
                "height": layer_height - 10,
                "class": "topsoil",
                "confidence": 0.95
            },
            {
                "x": width // 2,
                "y": layer_height + layer_height // 2,
                "width": width - 40,
                "height": layer_height - 10,
                "class": "clay",
                "confidence": 0.88
            },
            {
                "x": width // 2,
                "y": 2 * layer_height + layer_height // 2,
                "width": width - 40,
                "height": layer_height - 10,
                "class": "sandy_clay",
                "confidence": 0.82
            },
            {
                "x": width // 2,
                "y": 3 * layer_height + layer_height // 2,
                "width": width - 40,
                "height": layer_height - 10,
                "class": "sand",
                "confidence": 0.91
            }
        ],
        "image": {
            "width": width,
            "height": height
        }
    }
    
    return demo_predictions


def validate_api_connection() -> bool:
    """
    Test the connection to the Roboflow API.
    
    Returns:
        True if connection is successful, False otherwise
    """
    if ROBOFLOW_API_KEY == "your_api_key_here":
        return False
    
    try:
        # Make a simple test request
        response = requests.get(
            f"https://api.roboflow.com/{ROBOFLOW_MODEL_ID}",
            params={"api_key": ROBOFLOW_API_KEY},
            timeout=10
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


# Soil classification labels commonly used in geotechnical analysis
SOIL_CLASSES = {
    "topsoil": "Organic-rich surface soil, typically dark colored",
    "clay": "Fine-grained soil with high plasticity",
    "sandy_clay": "Clay with significant sand content",
    "silty_clay": "Clay with significant silt content",
    "sand": "Coarse-grained soil with low cohesion",
    "silty_sand": "Sand with significant silt content",
    "gravel": "Coarse particles larger than 2mm",
    "organic": "Soil with high organic matter content",
    "peat": "Highly organic soil from decomposed vegetation",
    "fill": "Man-made soil fill material"
}


def get_soil_description(soil_class: str) -> str:
    """
    Get a description for a soil classification.
    
    Args:
        soil_class: The classification label from predictions
        
    Returns:
        Human-readable description of the soil type
    """
    return SOIL_CLASSES.get(soil_class.lower(), f"Soil type: {soil_class}")
