# Troubleshooting Guide

Common issues and solutions for deploying the Soil Analysis API.

## Table of Contents
1. [Installation Issues](#installation-issues)
2. [Deployment Issues](#deployment-issues)
3. [Runtime Errors](#runtime-errors)
4. [Performance Issues](#performance-issues)

---

## Installation Issues

### Issue: `pip install` fails for opencv-python

**Symptoms:**
```
ERROR: Failed building wheel for opencv-python
```

**Solutions:**

**Option 1 - Install system dependencies (Linux/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install -y python3-opencv
# or
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
pip install opencv-python
```

**Option 2 - Use headless version:**
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

**Option 3 - Use pre-built wheels:**
```bash
pip install --upgrade pip
pip install opencv-python --no-cache-dir
```

---

### Issue: `ModuleNotFoundError: No module named 'cv2'`

**Solution:**
```bash
pip install opencv-python
# or for servers without display
pip install opencv-python-headless
```

---

### Issue: Virtual environment activation fails

**Windows:**
```bash
# If execution policy error
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
# or
. venv/bin/activate
```

---

## Deployment Issues

### Issue: Port already in use

**Symptoms:**
```
Error: Address already in use
```

**Solution:**
```bash
# Find process using port 8000
# Linux/Mac:
lsof -i :8000
# Windows:
netstat -ano | findstr :8000

# Kill the process
# Linux/Mac:
kill -9 <PID>
# Windows:
taskkill /PID <PID> /F

# Or use a different port
uvicorn main:app --port 8001
```

---

### Issue: Render deployment fails

**Symptoms:**
```
Build failed
```

**Common Causes & Solutions:**

1. **Wrong Python version:**
   - Add to `render.yaml`:
     ```yaml
     envVars:
       - key: PYTHON_VERSION
         value: 3.11.0
     ```

2. **Missing system dependencies:**
   - Create `packages.txt` in project root:
     ```
     libgl1-mesa-glx
     libglib2.0-0
     ```

3. **Build timeout:**
   - Optimize requirements.txt (remove unused packages)
   - Use `--no-cache-dir` in build command

---

### Issue: Railway out of memory

**Symptoms:**
```
Killed
137 exit code
```

**Solutions:**

1. **Optimize image processing:**
   ```python
   # In color_utils.py, resize large images
   max_dimension = 1024
   if max(image.shape[:2]) > max_dimension:
       scale = max_dimension / max(image.shape[:2])
       image = cv2.resize(image, None, fx=scale, fy=scale)
   ```

2. **Use opencv-python-headless:**
   - Smaller memory footprint
   - Update requirements.txt

3. **Upgrade to paid tier** (if needed)

---

### Issue: Fly.io deployment timeout

**Symptoms:**
```
Health check failed
```

**Solutions:**

1. **Increase timeout in fly.toml:**
   ```toml
   [http_service]
     grace_period = "10s"
     timeout = "30s"
   ```

2. **Check health endpoint:**
   ```bash
   flyctl logs
   # Ensure / route responds quickly
   ```

---

## Runtime Errors

### Issue: `CORS policy: No 'Access-Control-Allow-Origin' header`

**Solution:**

Update `main.py` with your frontend URL:
```python
origins = [
    "http://localhost:3000",
    "https://your-frontend.com",  # Add your frontend URL
    "https://your-backend.onrender.com",  # Add your backend URL
]
```

---

### Issue: `HTTPException: Invalid or corrupted image file`

**Causes:**
- Unsupported image format
- Corrupted upload
- File size too large

**Solutions:**

1. **Check supported formats:**
   - JPG/JPEG ✅
   - PNG ✅
   - BMP ✅
   - TIFF ❌ (needs additional codecs)

2. **Add file size limit:**
   ```python
   @app.post("/predict")
   async def predict(file: UploadFile = File(...)):
       # Add size check
       contents = await file.read()
       if len(contents) > 10 * 1024 * 1024:  # 10MB limit
           raise HTTPException(400, "File too large")
       # ... rest of code
   ```

---

### Issue: `FileNotFoundError: munsell_colors_clean.csv`

**Solution:**

Ensure `data/munsell_colors_clean.csv` exists:
```bash
# Check if file exists
ls -la data/

# If missing, the file should be in the repository
# Make sure it's committed to git
git status
git add data/munsell_colors_clean.csv
git commit -m "Add Munsell colors data"
```

---

### Issue: Roboflow API errors

**Symptoms:**
```
❌ Roboflow API error: 401 Unauthorized
```

**Solutions:**

1. **API key not set:**
   ```bash
   # On Render/Railway/Fly.io, set environment variable:
   ROBOFLOW_API_KEY=your_actual_key
   ```

2. **Use demo mode (no API needed):**
   - The app automatically falls back to demo predictions
   - No configuration needed

3. **Check API key validity:**
   - Log in to [roboflow.com](https://roboflow.com)
   - Go to Settings → API Keys
   - Generate new key if needed

---

## Performance Issues

### Issue: Slow cold starts

**Symptoms:**
- First request takes 30-60 seconds
- Subsequent requests are fast

**Explanation:**
- Free tier platforms spin down apps after inactivity
- First request "wakes up" the app

**Solutions:**

1. **Render:** 
   - Upgrade to paid tier ($7/month) for always-on

2. **Railway:**
   - No native solution on free tier

3. **Fly.io:**
   - Already better than others (~15s cold start)

4. **Use uptime monitoring:**
   - [UptimeRobot](https://uptimerobot.com) (free)
   - Ping your app every 5 minutes to keep it warm
   - Limited effectiveness on free tiers

---

### Issue: Image processing is slow

**Solutions:**

1. **Resize images before processing:**
   ```python
   def resize_if_large(image, max_size=1024):
       h, w = image.shape[:2]
       if max(h, w) > max_size:
           scale = max_size / max(h, w)
           new_h, new_w = int(h * scale), int(w * scale)
           return cv2.resize(image, (new_w, new_h))
       return image
   ```

2. **Optimize K-means clustering:**
   ```python
   # In color_utils.py
   # Reduce number of clusters or iterations if too slow
   kmeans = KMeans(n_clusters=3, n_init=5, max_iter=100)
   ```

3. **Add caching** (for repeated requests):
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def analyze_cached(image_hash):
       # ... analysis code
   ```

---

### Issue: High memory usage

**Solutions:**

1. **Use opencv-python-headless:**
   ```bash
   pip uninstall opencv-python
   pip install opencv-python-headless
   ```

2. **Delete temp files immediately:**
   ```python
   # In main.py, ensure cleanup
   try:
       # ... processing
   finally:
       if os.path.exists(file_path):
           os.remove(file_path)
   ```

3. **Limit concurrent requests:**
   ```python
   # Add rate limiting
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   
   @app.post("/predict")
   @limiter.limit("10/minute")
   async def predict(request: Request, file: UploadFile):
       # ... code
   ```

---

## Platform-Specific Issues

### Render

**Issue: App keeps restarting**
- Check logs: `Render Dashboard → Logs`
- Common cause: Port binding (use `$PORT`)
- Ensure: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Issue: Build takes too long**
- Add `packages.txt` instead of apt-get in code
- Remove unused dependencies
- Use build cache

---

### Railway

**Issue: Deployment not starting**
- Check: `Settings → Deploy` logs
- Ensure: Start command is set correctly
- Verify: `railway.json` is valid

**Issue: Exceeded free credit**
- Monitor usage: Dashboard → Usage
- Optimize: Remove unnecessary endpoints
- Alternative: Switch to Render

---

### Fly.io

**Issue: Image too large**
```bash
# Optimize Dockerfile
FROM python:3.11-slim  # Use slim, not full
RUN rm -rf /var/lib/apt/lists/*  # Clean up
```

**Issue: Region connectivity**
```bash
# List regions
flyctl platform regions

# Change region
flyctl regions set iad ord  # US East, US Central
```

---

## Getting Help

### Check Logs

**Render:**
```
Dashboard → Your Service → Logs
```

**Railway:**
```
Project → Service → Deployments → View Logs
```

**Fly.io:**
```bash
flyctl logs
flyctl logs --app your-app-name
```

**Local:**
```bash
# Run with debug mode
uvicorn main:app --reload --log-level debug
```

---

### Enable Debug Mode

Add to `main.py`:
```python
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/predict")
async def predict(file: UploadFile):
    logger.debug(f"Received file: {file.filename}")
    # ... rest of code
```

---

### Test Locally First

Before deploying:
```bash
# 1. Test locally
python main.py

# 2. Test with Docker
docker build -t soil-api .
docker run -p 8000:8000 soil-api

# 3. Test API endpoint
curl http://localhost:8000/
curl -X POST http://localhost:8000/predict -F "file=@test.jpg"
```

---

## Still Having Issues?

1. **Check platform status pages:**
   - Render: https://status.render.com
   - Railway: https://status.railway.app
   - Fly.io: https://status.flyio.net

2. **Search existing issues:**
   - GitHub Issues
   - Platform community forums

3. **Create an issue:**
   - Provide error logs
   - Include platform and Python version
   - Describe steps to reproduce

---

## Useful Commands

### Render
```bash
# View logs (if using Render CLI)
render logs --tail
```

### Railway
```bash
# View logs
railway logs

# Open dashboard
railway open
```

### Fly.io
```bash
# View logs
flyctl logs

# SSH into container
flyctl ssh console

# Check status
flyctl status

# Scale app
flyctl scale count 1
```

### Docker
```bash
# View container logs
docker logs soil-api

# Execute command in container
docker exec -it soil-api bash

# Remove and rebuild
docker rm -f soil-api
docker rmi soil-analysis-api
docker build -t soil-analysis-api .
```

---

## Prevention Tips

1. ✅ Always test locally before deploying
2. ✅ Use environment variables for configuration
3. ✅ Keep dependencies minimal
4. ✅ Monitor application logs
5. ✅ Set up health checks
6. ✅ Use version control (Git)
7. ✅ Document any custom setup steps
8. ✅ Keep Python and dependencies updated

---

**Last Updated:** December 2024
