# Pre-Deployment Checklist

Before deploying your Soil Analysis API, review this checklist to ensure a smooth deployment.

## ✅ Pre-Deployment Steps

### 1. Code Preparation
- [ ] All code changes committed to Git
- [ ] No sensitive data (API keys, passwords) in code
- [ ] `.gitignore` configured to exclude secrets
- [ ] Dependencies listed in `requirements.txt`

### 2. Configuration Files
- [ ] Choose deployment platform (Render/Railway/Fly.io)
- [ ] Review platform configuration file:
  - [ ] `render.yaml` for Render
  - [ ] `railway.json` for Railway
  - [ ] `fly.toml` for Fly.io
  - [ ] `Dockerfile` for Docker

### 3. Environment Variables
- [ ] Created `.env` file locally (from `.env.example`)
- [ ] Know which environment variables to set on platform:
  - `ROBOFLOW_API_KEY` (optional - app works without it)
  - `ROBOFLOW_MODEL_ID` (if using Roboflow)
  - `ROBOFLOW_VERSION` (if using Roboflow)

### 4. CORS Configuration
- [ ] If using a frontend, update `origins` list in `main.py`:
  ```python
  origins = [
      "http://localhost:3000",
      "https://your-frontend.com",  # Add your frontend URL
      "https://your-backend.onrender.com",  # Add your backend URL
  ]
  ```
- [ ] If API-only (no frontend), CORS is already configured

### 5. Testing Locally
- [ ] Tested locally with: `python main.py` or `./start.sh`
- [ ] API accessible at http://localhost:8000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Successfully uploaded and analyzed a test image
- [ ] (Optional) Tested with Docker: `docker build -t soil-api . && docker run -p 8000:8000 soil-api`

## 📋 Platform-Specific Checklists

### Render Deployment
- [ ] GitHub repository is public or Render has access
- [ ] Signed up at https://render.com
- [ ] Created new Web Service in dashboard
- [ ] Connected GitHub repository
- [ ] Selected correct branch (usually `main`)
- [ ] Verified `render.yaml` is detected
- [ ] Set environment variables (if needed)
- [ ] Deployment started successfully

### Railway Deployment
- [ ] Signed up at https://railway.app
- [ ] (Optional) Added credit card for extended free tier
- [ ] Created new project
- [ ] Connected GitHub repository
- [ ] Verified `railway.json` is detected
- [ ] Set environment variables (if needed)
- [ ] Generated public domain

### Fly.io Deployment
- [ ] Signed up at https://fly.io
- [ ] Installed Fly CLI
- [ ] Logged in via CLI: `flyctl auth login`
- [ ] Reviewed `fly.toml` configuration
- [ ] Ran `flyctl launch` successfully
- [ ] Set secrets via CLI: `flyctl secrets set KEY=value`
- [ ] Deployed with `flyctl deploy`

### Docker Deployment
- [ ] Docker installed locally
- [ ] Built image successfully: `docker build -t soil-api .`
- [ ] Ran container: `docker run -d -p 8000:8000 soil-api`
- [ ] Verified container is running: `docker ps`
- [ ] Accessed API at http://localhost:8000

## ✅ Post-Deployment Verification

### 1. Health Check
```bash
# Replace with your deployed URL
curl https://your-app.onrender.com/
```
**Expected:** `{"message":"Welcome to the Fugro Soil Analysis API"}`

### 2. API Documentation
- [ ] Open in browser: `https://your-app-url.com/docs`
- [ ] Swagger UI loads correctly
- [ ] All endpoints visible
- [ ] Can expand and view endpoint details

### 3. Test Image Upload
```bash
curl -X POST "https://your-app-url.com/predict" \
  -F "file=@path/to/test-image.jpg"
```
**Expected:** JSON response with soil analysis results

### 4. Monitor Logs
- [ ] Check deployment platform logs
- [ ] No error messages
- [ ] Application started successfully
- [ ] Health checks passing

### 5. Performance Check
- [ ] First request (cold start) completes
- [ ] Subsequent requests are faster
- [ ] Image processing completes successfully
- [ ] Response times acceptable (<30s for free tier)

## 🔧 Common Issues to Check

### If Deployment Fails
1. [ ] Check build logs in platform dashboard
2. [ ] Verify Python version (should be 3.10 or 3.11)
3. [ ] Check all dependencies install successfully
4. [ ] Ensure start command is correct: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. [ ] Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### If API Doesn't Respond
1. [ ] Check app is running in platform dashboard
2. [ ] Verify health endpoint: `/`
3. [ ] Check logs for errors
4. [ ] Ensure port binding uses `$PORT` variable
5. [ ] Wait for cold start (can take 30-60s on free tier)

### If Image Upload Fails
1. [ ] Check CORS configuration
2. [ ] Verify image format is supported (JPG, PNG, BMP)
3. [ ] Check file size (should be < 10MB)
4. [ ] Review error message in API response
5. [ ] Check platform logs for details

## 📊 Success Criteria

Your deployment is successful when:

✅ API endpoint is accessible  
✅ Health check returns success  
✅ API documentation loads  
✅ Image upload and analysis works  
✅ No errors in platform logs  
✅ Cold start completes within timeout  
✅ CORS allows your frontend (if applicable)  

## 🎉 Ready to Deploy!

If all checklist items are complete, you're ready to deploy!

**Quick Deploy Links:**
- **Render:** https://dashboard.render.com
- **Railway:** https://railway.app
- **Fly.io:** Run `flyctl launch`
- **Docker:** Run `docker build -t soil-api .`

**Need Help?**
- [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed guides
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common fixes
- [QUICKSTART.md](QUICKSTART.md) - Quick reference

---

**Pro Tip:** Deploy to Render first - it's the easiest and most reliable free option! 🚀
