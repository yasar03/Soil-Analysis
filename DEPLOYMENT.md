# Free Deployment Guide for Soil Analysis API

This guide provides step-by-step instructions for deploying the Soil Analysis API on various free hosting platforms.

## Table of Contents
1. [Render (Recommended)](#1-render-recommended)
2. [Railway](#2-railway)
3. [Fly.io](#3-flyio)
4. [Hugging Face Spaces](#4-hugging-face-spaces)
5. [Local Docker Deployment](#5-local-docker-deployment)

---

## 1. Render (Recommended)

**Best for:** FastAPI applications, easy setup, generous free tier

### Free Tier Features:
- ✅ 750 hours/month (enough for continuous running)
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ✅ Environment variables support
- ⚠️ Spins down after 15 minutes of inactivity (cold starts ~1 minute)

### Deployment Steps:

1. **Create a Render Account**
   - Go to [https://render.com](https://render.com)
   - Sign up with your GitHub account

2. **Deploy from GitHub**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `Soil-Analysis` repository

3. **Configure the Service**
   - **Name:** `soil-analysis-api` (or any name you prefer)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables** (Optional)
   - Go to "Environment" tab
   - Add variables:
     ```
     ROBOFLOW_API_KEY=your_api_key_here (optional)
     ROBOFLOW_MODEL_ID=soil-classification
     ROBOFLOW_VERSION=1
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment
   - Your API will be available at: `https://your-service-name.onrender.com`

6. **Test Your Deployment**
   ```bash
   # Open API documentation
   https://your-service-name.onrender.com/docs
   
   # Test the API
   curl https://your-service-name.onrender.com/
   ```

### Using render.yaml (Alternative Method)

1. Push this repository to GitHub
2. In Render dashboard, click "New +" → "Blueprint"
3. Connect your repository
4. Render will automatically detect `render.yaml` and configure everything
5. Click "Apply" to deploy

---

## 2. Railway

**Best for:** Quick deployments, simple configuration

### Free Tier Features:
- ✅ $5 free credit per month (~500 hours)
- ✅ Automatic HTTPS
- ✅ Auto-deploy from GitHub
- ⚠️ Requires credit card after trial
- ⚠️ Limited to $5/month free credit

### Deployment Steps:

1. **Create a Railway Account**
   - Go to [https://railway.app](https://railway.app)
   - Sign up with GitHub

2. **Deploy from GitHub**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `Soil-Analysis` repository

3. **Railway Auto-Configuration**
   - Railway will automatically detect Python and install dependencies
   - The `railway.json` file configures the start command

4. **Set Environment Variables** (Optional)
   - Click on your service → "Variables" tab
   - Add:
     ```
     ROBOFLOW_API_KEY=your_api_key_here (optional)
     ROBOFLOW_MODEL_ID=soil-classification
     ROBOFLOW_VERSION=1
     ```

5. **Generate Domain**
   - Go to "Settings" → "Networking"
   - Click "Generate Domain"
   - Your API will be available at: `https://your-app.up.railway.app`

6. **Test Your Deployment**
   ```bash
   curl https://your-app.up.railway.app/
   ```

---

## 3. Fly.io

**Best for:** Global edge deployment, containerized apps

### Free Tier Features:
- ✅ 3 shared-cpu-1x VMs (256MB RAM each)
- ✅ 160GB outbound data transfer
- ✅ Global deployment
- ⚠️ Requires credit card for verification
- ⚠️ Auto-suspend after inactivity

### Deployment Steps:

1. **Install Fly CLI**
   ```bash
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Sign Up / Login**
   ```bash
   flyctl auth signup
   # or
   flyctl auth login
   ```

3. **Deploy the Application**
   ```bash
   # Navigate to your project directory
   cd Soil-Analysis
   
   # Launch (fly.toml is already configured)
   flyctl launch
   
   # Follow prompts:
   # - Choose app name (or use suggested)
   # - Select region
   # - Don't create a database
   # - Deploy now: Yes
   ```

4. **Set Environment Variables** (Optional)
   ```bash
   flyctl secrets set ROBOFLOW_API_KEY=your_api_key_here
   flyctl secrets set ROBOFLOW_MODEL_ID=soil-classification
   flyctl secrets set ROBOFLOW_VERSION=1
   ```

5. **Deploy/Update**
   ```bash
   flyctl deploy
   ```

6. **Open Your App**
   ```bash
   flyctl open
   # Your API will be at: https://your-app-name.fly.dev
   ```

---

## 4. Hugging Face Spaces

**Best for:** ML/AI applications, showcasing projects

### Free Tier Features:
- ✅ Completely free
- ✅ GPU access (limited)
- ✅ Public by default (great for demos)
- ⚠️ Slower than dedicated hosting
- ⚠️ Limited customization

### Deployment Steps:

1. **Create Hugging Face Account**
   - Go to [https://huggingface.co](https://huggingface.co)
   - Sign up for free

2. **Create a New Space**
   - Click "New" → "Space"
   - Choose:
     - **Space name:** `soil-analysis-api`
     - **License:** MIT
     - **Space SDK:** Docker
     - **Visibility:** Public

3. **Prepare Files**
   Create a file named `Dockerfile` in your Space:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   RUN apt-get update && apt-get install -y \
       libgl1-mesa-glx \
       libglib2.0-0 \
       && rm -rf /var/lib/apt/lists/*
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 7860
   
   ENV PORT=7860
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
   ```

4. **Push Your Code**
   ```bash
   # Clone your Space
   git clone https://huggingface.co/spaces/YOUR_USERNAME/soil-analysis-api
   cd soil-analysis-api
   
   # Copy your project files
   cp -r /path/to/Soil-Analysis/* .
   
   # Commit and push
   git add .
   git commit -m "Initial deployment"
   git push
   ```

5. **Your App Will Be Live At:**
   `https://huggingface.co/spaces/YOUR_USERNAME/soil-analysis-api`

---

## 5. Local Docker Deployment

**Best for:** Testing, development, self-hosting

### Steps:

1. **Install Docker**
   - Download from [https://docker.com](https://docker.com)

2. **Build the Image**
   ```bash
   cd Soil-Analysis
   docker build -t soil-analysis-api .
   ```

3. **Run the Container**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e ROBOFLOW_API_KEY=your_key_here \
     --name soil-api \
     soil-analysis-api
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs

5. **Stop/Remove Container**
   ```bash
   docker stop soil-api
   docker rm soil-api
   ```

---

## Platform Comparison

| Platform | Setup Time | Cold Starts | Custom Domain | Best For |
|----------|-----------|-------------|---------------|----------|
| **Render** | 5 min | ~60s | ✅ Free | Production-ready apps |
| **Railway** | 3 min | ~30s | ✅ Free | Quick prototypes |
| **Fly.io** | 5 min | ~15s | ✅ Free | Global deployment |
| **HF Spaces** | 10 min | ~90s | ❌ | ML demos |
| **Docker** | 2 min | None | N/A | Local/self-hosted |

---

## Environment Variables

All platforms support these optional environment variables:

```bash
# Optional: Roboflow API integration
ROBOFLOW_API_KEY=your_api_key_here
ROBOFLOW_MODEL_ID=soil-classification
ROBOFLOW_VERSION=1

# The app works without these - it will use demo predictions
```

---

## Testing Your Deployment

After deployment, test your API:

1. **Check Health**
   ```bash
   curl https://your-app-url.com/
   ```

2. **View API Documentation**
   ```
   https://your-app-url.com/docs
   ```

3. **Test Image Upload**
   ```bash
   curl -X POST "https://your-app-url.com/predict" \
     -F "file=@path/to/soil-image.jpg"
   ```

---

## Troubleshooting

### Common Issues:

1. **Port Binding Errors**
   - Ensure start command uses `--port $PORT` to bind to the platform's assigned port

2. **OpenCV Installation Fails**
   - Add system dependencies in Dockerfile (libgl1-mesa-glx, libglib2.0-0)

3. **Cold Start Timeouts**
   - Normal on free tiers, first request may take 30-60 seconds

4. **Out of Memory**
   - Reduce image processing size or upgrade to paid tier

5. **CORS Errors**
   - Update allowed origins in `main.py` to include your frontend URL

---

## Recommendations

**For Beginners:** Start with **Render** (easiest, most reliable free tier)

**For Developers:** Use **Railway** or **Fly.io** (better performance, more control)

**For ML Demos:** Use **Hugging Face Spaces** (great for showcasing)

**For Production:** Consider upgrading to paid tiers for better performance and uptime

---

## Need Help?

- **Render Docs:** https://render.com/docs
- **Railway Docs:** https://docs.railway.app
- **Fly.io Docs:** https://fly.io/docs
- **Hugging Face Docs:** https://huggingface.co/docs/hub/spaces

---

## Next Steps

After deployment:
1. ✅ Update CORS origins in `main.py` with your frontend URL
2. ✅ Set up custom domain (if supported by platform)
3. ✅ Configure monitoring and logging
4. ✅ Set up CI/CD for automatic deployments
5. ✅ Consider upgrading to paid tier for production use
