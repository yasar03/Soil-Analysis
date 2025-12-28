# Soil Color Analysis API

A FastAPI-based soil color analysis tool using OpenCV and the Munsell Color System.

## Features

- 🎨 **Soil Color Analysis**: Extract dominant colors using K-means clustering
- 🏷️ **Munsell Matching**: Match colors to standard Munsell Soil Color Chart
- 📏 **Depth Estimation**: Calculate soil layer depths
- 🔍 **Smart Filtering**: Automatically excludes white pipe casings and artifacts
- ⚡ **Fast API**: RESTful API with automatic documentation

## Project Structure

```
soil-color-analysis/
├── main.py                 # FastAPI application
├── inference/
│   ├── __init__.py
│   ├── color_utils.py      # Soil color analysis (OpenCV)
│   ├── roboflow_client.py  # Object detection integration
│   └── depth_utils.py      # Depth estimation
├── data/
│   └── munsell_colors_clean.csv  # 171 Munsell colors
├── samples/                # Sample soil images
│   ├── Sample 1.jpg
│   └── Sample 24.jpg
├── demo_mappings.json      # Demo image mappings
├── requirements.txt
└── README.md
```

## Quick Start

```bash
# 1. Navigate to project
cd Soil-Analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python3 main.py or python main.py

# 4. Open browser
# API Docs: http://localhost:8000/docs
```

## API Usage

### Upload Image for Analysis

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@samples/Sample 1.jpg"
```

### Response Example

```json
{
  "detections": [
    {
      "class_name": "clay",
      "confidence": 0.88,
      "dominant_color": "10YR 2/2",
      "color_name": "Very dark brown",
      "depth_cm": [82.3, 163.1]
    }
  ]
}
```

## Munsell Color System

| Code | Meaning |
|------|---------|
| 10YR 2/2 | Hue=10YR, Value=2 (dark), Chroma=2 |
| 5YR 3/1 | Hue=5YR, Value=3, Chroma=1 |
| GLEY1 6/N | Gray (neutral) |

## Standalone Color Analysis

```python
from inference.color_utils import ColorAnalyzer
import cv2

analyzer = ColorAnalyzer('data/munsell_colors_clean.csv')
image = cv2.imread('samples/Sample 1.jpg')
color, name = analyzer.analyze_color_with_name(image)
print(f"{color} - {name}")  # e.g., "10YR 3/2 - Very dark brown"
```

## 🚀 Free Deployment

Deploy this API for free on various platforms! See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed step-by-step guides.

### Quick Deploy Options:

| Platform | Setup Time | Features | Deploy Link |
|----------|-----------|----------|-------------|
| **Render** ⭐ | 5 min | Auto HTTPS, GitHub sync | [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com) |
| **Railway** | 3 min | $5/month free credit | [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app) |
| **Fly.io** | 5 min | Global edge deployment | [Deploy Guide](DEPLOYMENT.md#3-flyio) |

**Recommended:** Start with **Render** for the easiest deployment experience.

### One-Click Deploy to Render:

1. Fork this repository
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Render will auto-detect settings from `render.yaml`
6. Click "Create Web Service"

Your API will be live in ~3 minutes at `https://your-app.onrender.com` 🎉

### Environment Variables (Optional):

```bash
ROBOFLOW_API_KEY=your_api_key_here  # Optional - app works without it
ROBOFLOW_MODEL_ID=soil-classification
ROBOFLOW_VERSION=1
```

The app works perfectly without API keys using built-in demo predictions!

---

## 📋 Configuration Files

This repository includes ready-to-use deployment configurations:

- **render.yaml** - Render platform configuration
- **railway.json** - Railway platform configuration  
- **fly.toml** - Fly.io platform configuration
- **Dockerfile** - Docker container configuration
- **.env.example** - Environment variables template

---