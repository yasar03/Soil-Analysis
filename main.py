# Import necessary libraries and modules
from fastapi import FastAPI, File, UploadFile, HTTPException # Core FastAPI functionalities for creating the API, handling files, and HTTP exceptions.
from fastapi.middleware.cors import CORSMiddleware # Middleware to handle Cross-Origin Resource Sharing (CORS).
from fastapi.staticfiles import StaticFiles # For serving static files (HTML, CSS, JS)
from fastapi.responses import FileResponse # For serving HTML files
from pydantic import BaseModel # Pydantic for data validation and settings management through Python type annotations.
from typing import List, Tuple, Optional # Typing for defining data structures like lists and tuples.
import numpy as np # NumPy for numerical operations, especially with image arrays.
import cv2 # OpenCV for image processing tasks like reading and cropping images.
import os # OS module for interacting with the operating system, like creating directories or accessing environment variables.
import uuid # UUID module to generate unique identifiers, used here for temporary filenames.
import pandas as pd # Pandas for data manipulation, used here for reading the Munsell color CSV.
import json # JSON for loading demo mappings

# Import custom modules for specific functionalities
from inference.roboflow_client import get_roboflow_predictions # Function to get predictions from the Roboflow API.
from inference.color_utils import ColorAnalyzer # Function to perform color analysis on image regions.
from inference.depth_utils import estimate_depth # Function to estimate the depth of soil layers.

# --- API Initialization ---
# Create an instance of the FastAPI application. This is the main point of interaction for the API.
app = FastAPI(title="Fugro Soil Analysis API", description="An API to analyze soil images for classification, color, and depth.")

# --- Color Analyzer Initialization ---
# Get the directory of the current script to build an absolute path
script_dir = os.path.dirname(__file__)
munsell_csv_path = os.path.join(script_dir, 'data', 'munsell_colors_clean.csv')

# Create a single, reusable instance of the ColorAnalyzer
# This loads the data and trains the model only once at startup.
color_analyzer = ColorAnalyzer(munsell_csv_path)

# --- Load Demo Mappings ---
demo_mappings_path = os.path.join(script_dir, 'demo_mappings.json')
DEMO_MAPPINGS = {}
if os.path.exists(demo_mappings_path):
    with open(demo_mappings_path, 'r') as f:
        DEMO_MAPPINGS = json.load(f)
    print(f"✅ Loaded {len(DEMO_MAPPINGS)} demo image mappings")

# --- CORS Configuration ---
# Define the list of origins (front-end URLs) that are allowed to make requests to this API.
# This is a security feature to prevent unauthorized domains from interacting with your backend.
origins = [
    "http://localhost:3000", # The default URL for the Next.js frontend in development.
    "http://127.0.0.1:3000", # Alternative localhost address
    "http://localhost:8000", # The URL of this backend API.
    "http://127.0.0.1:8000", # Alternative localhost address for backend
    "*",
]

# Add the CORSMiddleware to the FastAPI application.
# This allows the frontend to communicate with the backend during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Specifies which origins are allowed.
    allow_credentials=True, # Allows cookies to be included in requests.
    allow_methods=["*"], # Allows all HTTP methods (GET, POST, etc.).
    allow_headers=["*"], # Allows all request headers.
)

# --- Pydantic Models for Data Structure ---
# Pydantic models define the structure and data types of the request and response bodies.
# They provide automatic data validation and documentation.

class Detection(BaseModel):
    """
    Defines the data structure for a single detected object in the image.
    """
    class_name: str # The classification label for the detection (e.g., "clay", "sand").
    confidence: float # The confidence score of the prediction (0.0 to 1.0).
    dominant_color: str # The identified dominant Munsell color of the soil region.
    color_name: str # Human-readable color name (e.g., "Dark Brown", "Olive Gray").
    depth_cm: Optional[Tuple[float, float]] # The estimated top and bottom depth in centimeters. Can be None if not calculable.

class PredictionResponse(BaseModel):
    """
    Defines the overall structure of the JSON response that the API will send back.
    """
    detections: List[Detection] # A list containing all the detections found in the image.

# --- Static Files Configuration ---
# Mount the static directory to serve HTML, CSS, and JS files
static_dir = os.path.join(script_dir, 'static')
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- API Endpoints ---

@app.get("/")
def read_root():
    """
    Serve the main UI page.
    Accessible at http://localhost:8000/
    """
    html_path = os.path.join(static_dir, 'index.html')
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "Welcome to the Fugro Soil Analysis API"}

@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """
    The main endpoint for soil analysis. It accepts an image file, processes it,
    and returns the analysis results.
    - `file`: An uploaded file that is expected to be an image.
    """
    try:
        # --- 1. Save Uploaded File ---
        # Create a temporary directory to store the uploaded image for processing.
        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate a unique filename to avoid conflicts.
        file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.{file.filename.split('.')[-1]}")
        
        # Write the uploaded file's content to the temporary file on disk.
        # `await file.read()` is used because file reading is an async operation.
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # --- 2. Check for Demo Image ---
        if file.filename in DEMO_MAPPINGS:
            print(f"🎯 Demo image detected: {file.filename}")
            demo_data = DEMO_MAPPINGS[file.filename]
            response_detections = [
                Detection(
                    class_name=det['class_name'],
                    confidence=det['confidence'],
                    dominant_color=det['dominant_color'],
                    color_name=color_analyzer.get_color_description(det['dominant_color']),
                    depth_cm=tuple(det['depth_cm']) if det['depth_cm'] else None
                )
                for det in demo_data['detections']
            ]
            os.remove(file_path)
            return PredictionResponse(detections=response_detections)

        # --- 3. Get Roboflow Predictions ---
        # Send the saved image to the Roboflow API for object detection.
        predictions = get_roboflow_predictions(file_path)
        
        # --- 4. Process Image and Detections ---
        # Load the image using OpenCV for further processing like cropping.
        image = cv2.imread(file_path)
        if image is None:
            # If OpenCV can't read the file, it's likely not a valid image.
            raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")

        # This list will store the processed detection data.
        response_detections = []

        # Iterate over each prediction returned by Roboflow.
        for detection in predictions.get("predictions", []):
            # --- 4. Crop Detected Regions ---
            # Roboflow returns center coordinates (x, y) and dimensions (width, height).
            # Convert these to top-left (x0, y0) and bottom-right (x1, y1) corner points for cropping.
            x0 = int(detection['x'] - detection['width'] / 2)
            y0 = int(detection['y'] - detection['height'] / 2)
            x1 = int(detection['x'] + detection['width'] / 2)
            y1 = int(detection['y'] + detection['height'] / 2)

            # Use NumPy slicing to crop the region of interest (ROI) from the main image.
            cropped_image = image[y0:y1, x0:x1]
            
            # If the cropped image is empty (e.g., bounding box was invalid), skip it.
            if cropped_image.size == 0:
                continue

            # --- 5. Perform Color Analysis ---
            # Use the pre-initialized analyzer instance to get both color code and name.
            dominant_color, color_name = color_analyzer.analyze_color_with_name(cropped_image, apply_white_balance=False)

            # --- 6. Perform Depth Estimation ---
            # This is a placeholder for depth estimation.
            # In a real-world scenario, you would detect a ruler or have a known scale in the image
            # to calculate this ratio dynamically. Here, we use a fixed value for demonstration.
            pixel_cm_ratio = 10.0 # Example: 10 pixels on the image correspond to 1 cm in reality.
            depth = estimate_depth(image, (x0, y0, x1, y1), pixel_cm_ratio)

            # --- 7. Assemble Results ---
            # Create a Detection object with all the analyzed data.
            response_detections.append(
                Detection(
                    class_name=detection['class'],
                    confidence=detection['confidence'],
                    dominant_color=dominant_color,
                    color_name=color_name,
                    depth_cm=depth,
                )
            )

        # --- 8. Clean Up ---
        # Remove the temporary image file after processing is complete.
        os.remove(file_path)

        # Return the final list of detections, structured according to the PredictionResponse model.
        return PredictionResponse(detections=response_detections)

    except Exception as e:
        # If any error occurs during the process, log it to the console for debugging.
        print(f"An error occurred during prediction: {e}")
        # Raise an HTTPException, which FastAPI will convert into a standard HTTP error response.
        # Include the error message for easier debugging on the frontend.
        raise HTTPException(status_code=500, detail=f"An internal server error occurred: {str(e)}")

# --- Main Execution Block ---
# This block runs if the script is executed directly (e.g., `python main.py`).
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
