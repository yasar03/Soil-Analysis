# Quick Reference - Free Deployment

One-page cheat sheet for deploying Soil Analysis API.

## 🚀 Fastest Deploy (Recommended)

### Render - 5 Minutes
```bash
1. Fork this repo on GitHub
2. Visit: https://dashboard.render.com
3. Click: "New +" → "Web Service"
4. Select: Your forked repository
5. Click: "Create Web Service" (auto-configured via render.yaml)
6. Done! 🎉
```

Your API: `https://your-app.onrender.com`  
API Docs: `https://your-app.onrender.com/docs`

---

## 📦 All Platform Commands

### Render
```bash
# Already configured! Just connect your GitHub repo
# Settings are in: render.yaml
```

### Railway
```bash
# Via CLI
npm i -g @railway/cli
railway login
railway init
railway up

# Via Dashboard
1. Visit: https://railway.app
2. New Project → Deploy from GitHub
3. Select repo → Deploy
```

### Fly.io
```bash
# Install CLI
curl -L https://fly.io/install.sh | sh

# Deploy
flyctl launch     # First time (uses fly.toml)
flyctl deploy     # Updates

# Set secrets
flyctl secrets set ROBOFLOW_API_KEY=your_key
```

### Docker (Local)
```bash
# Build
docker build -t soil-api .

# Run
docker run -d -p 8000:8000 --name soil-api soil-api

# View logs
docker logs soil-api

# Stop
docker stop soil-api && docker rm soil-api
```

---

## 🔧 Environment Variables

**Optional** - App works without them!

```bash
ROBOFLOW_API_KEY=your_key_here       # Optional: Roboflow API
ROBOFLOW_MODEL_ID=soil-classification
ROBOFLOW_VERSION=1
```

**How to set:**

- **Render:** Dashboard → Environment → Add Variable
- **Railway:** Dashboard → Variables → Add Variable  
- **Fly.io:** `flyctl secrets set KEY=value`
- **Docker:** `-e ROBOFLOW_API_KEY=key` in run command

---

## 📊 Platform Comparison

| Feature | Render | Railway | Fly.io |
|---------|--------|---------|--------|
| Free Tier | 750hrs/mo | $5 credit | 3 VMs free |
| Cold Start | ~60s | ~30s | ~15s |
| Setup Time | 5 min | 3 min | 5 min |
| Best For | Production | Quick tests | Global apps |

---

## 🧪 Testing Your Deploy

```bash
# 1. Health check
curl https://your-app-url.com/

# 2. View docs
open https://your-app-url.com/docs

# 3. Test upload
curl -X POST "https://your-app-url.com/predict" \
  -F "file=@test-image.jpg"
```

---

## 🐛 Quick Fixes

### Issue: Build fails
```bash
# Check Python version in platform settings
# Should be: 3.11 or 3.10
```

### Issue: App won't start
```bash
# Verify start command:
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Issue: CORS error
```python
# Add your frontend URL to origins in main.py
origins = [
    "http://localhost:3000",
    "https://your-frontend.com",  # Add this
]
```

### Issue: Port not binding
```bash
# Ensure using $PORT variable
--port $PORT  # Good ✅
--port 8000   # Bad on cloud platforms ❌
```

---

## 📁 Important Files

```
render.yaml       → Render configuration
railway.json      → Railway configuration
fly.toml          → Fly.io configuration
Dockerfile        → Docker build instructions
Procfile          → Heroku-style process file
.env.example      → Environment variable template
```

---

## 🔗 Helpful Links

- **Render:** https://render.com/docs
- **Railway:** https://docs.railway.app  
- **Fly.io:** https://fly.io/docs
- **Docker:** https://docs.docker.com

---

## 💡 Pro Tips

1. ✅ **Test locally first**: `./start.sh` or `python main.py`
2. ✅ **Use .env for secrets**: Never commit API keys
3. ✅ **Monitor logs**: Check for errors after deploy
4. ✅ **Start with Render**: Easiest for beginners
5. ✅ **No API key needed**: App has demo mode built-in

---

## 📞 Need Help?

1. Check **TROUBLESHOOTING.md** for common issues
2. Read **DEPLOYMENT.md** for detailed guides
3. View platform logs for error messages
4. Open a GitHub issue with logs

---

**Quick Start:** `./start.sh` (Linux/Mac) or `start.bat` (Windows)

**Deploy:** Push to GitHub → Connect to Render → Done! 🚀
