# TheGAVL API Deployment Guide

**Copyright (c) 2025 Joshua Hendricks Cole (DBA: Corporation of Light). All Rights Reserved. PATENT PENDING.**

This guide explains how to run the TheGAVL API server so users can submit cases and get predictions.

---

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
cd /Users/noone/repos/TheGAVLSuite

# Install required packages
pip install fastapi uvicorn pydantic python-multipart
```

### 2. Start the API Server

```bash
# Run the enhanced production API
python gavl_production_api_enhanced.py
```

The API will start on **http://localhost:8000**

### 3. Test the API

Open your browser to:
- **http://localhost:8000** - API info
- **http://localhost:8000/docs** - Interactive API documentation (Swagger)
- **http://localhost:8000/api/v1/health** - Health check

### 4. Test from Website

Now visit **http://thegavl.com/onboarding.html** and submit a case. It will call the local API and display results.

---

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Submit Case for Prediction
```bash
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "case_id": "TEST-001",
    "case_name": "Test Case",
    "issue_area": "constitutional",
    "opinion_text": "This is a test case about constitutional rights...",
    "petitioner": "John Doe",
    "respondent": "State of California"
  }'
```

### Get Metrics
```bash
curl http://localhost:8000/api/v1/metrics
```

---

## Production Deployment Options

### Option 1: Run on Your Mac (Simple)

**Pros:** Free, immediate, full control
**Cons:** API only available when your Mac is on and connected

```bash
# Keep API running in background
nohup python gavl_production_api_enhanced.py > gavl_api.log 2>&1 &

# Check if running
ps aux | grep gavl_production_api_enhanced

# View logs
tail -f gavl_api.log

# Stop
pkill -f gavl_production_api_enhanced
```

### Option 2: Deploy to Cloud (Recommended for Production)

#### Heroku (Easiest)

1. Create `Procfile`:
```
web: uvicorn gavl_production_api_enhanced:app --host 0.0.0.0 --port $PORT
```

2. Create `requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
```

3. Deploy:
```bash
heroku create thegavl-api
git push heroku main
```

4. Update website to use Heroku URL:
```javascript
// In onboarding.html
const API_URL = 'https://thegavl-api.herokuapp.com/api/v1/predict';
```

#### Railway.app (Modern, Simple)

1. Connect GitHub repo
2. Railway auto-detects FastAPI
3. Deploy with one click
4. Get URL like: `https://thegavl-api.up.railway.app`

#### AWS EC2 / DigitalOcean (Full Control)

```bash
# SSH into server
ssh user@your-server.com

# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Clone repo
git clone https://github.com/Workofarttattoo/TheGAVLSuite.git
cd TheGAVLSuite

# Install Python packages
pip3 install -r requirements.txt

# Run with systemd
sudo nano /etc/systemd/system/gavl-api.service
```

**Service file:**
```ini
[Unit]
Description=TheGAVL API Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/TheGAVLSuite
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/usr/bin/python3 gavl_production_api_enhanced.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start gavl-api
sudo systemctl enable gavl-api

# Check status
sudo systemctl status gavl-api
```

---

## CORS Configuration

The API already has CORS enabled for all origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify: ["https://thegavl.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, update to:
```python
allow_origins=["https://thegavl.com", "https://www.thegavl.com"]
```

---

## Monitoring & Logs

### View API Metrics

```bash
# Get prediction count, average confidence, etc.
curl http://localhost:8000/api/v1/metrics
```

### View Prediction Logs

```bash
# All predictions are logged to:
tail -f /tmp/gavl_predictions.jsonl

# Each line is JSON:
{
  "timestamp": "2025-10-29T...",
  "case_id": "CASE-123",
  "outcome": "petitioner_total_win",
  "probability": 0.68,
  "confidence": 0.75,
  "model_agreement": 0.8
}
```

### Monitor with Health Checks

Set up a cron job to ping the health endpoint:

```bash
# Add to crontab (crontab -e)
*/5 * * * * curl -s http://localhost:8000/api/v1/health > /dev/null || echo "GAVL API DOWN!" | mail -s "Alert" your@email.com
```

---

## Troubleshooting

### API Won't Start

**Error: "Address already in use"**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 [PID]

# Or use a different port
python gavl_production_api_enhanced.py --port 8001
```

**Error: "Module not found: fastapi"**
```bash
pip install fastapi uvicorn pydantic
```

### Website Can't Connect to API

**Error in browser console: "CORS error" or "Failed to fetch"**

1. Check API is running: `curl http://localhost:8000/api/v1/health`
2. Check CORS settings in API code
3. If testing locally, access website via `http://` not `file://`

**Error: "ERR_CONNECTION_REFUSED"**

1. API isn't running - start it
2. Firewall blocking port 8000 - allow it
3. Wrong URL in onboarding.html - update it

### Predictions Look Wrong

The current API uses `_mock_predict()` which generates simulated predictions. To use real trained models:

1. Check model files exist: `ls -lh /Users/noone/repos/TheGAVLSuite/trained_models/`
2. Models should be > 1KB (currently they're stub files ~100 bytes)
3. If models are stubs, you need to retrain with actual data
4. Update `_mock_predict()` method to use real model inference

---

## Updating the Website

After deploying API to production, update the URL:

```javascript
// In /Users/noone/thegavl-website/onboarding.html line 1154:

// BEFORE (local testing):
const API_URL = 'http://localhost:8000/api/v1/predict';

// AFTER (production):
const API_URL = 'https://api.thegavl.com/api/v1/predict';
// Or: 'https://thegavl-api.herokuapp.com/api/v1/predict'
// Or: 'https://thegavl-api.up.railway.app/api/v1/predict'
```

Then commit and push:
```bash
git add onboarding.html
git commit -m "Update API URL to production"
git push
```

---

## Security Notes

1. **Rate Limiting**: Add rate limiting to prevent abuse:
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/predict")
@limiter.limit("10/minute")
async def predict(case_input: CaseInput):
    ...
```

2. **API Keys**: For production, require API keys:
```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "your-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
```

3. **HTTPS**: Always use HTTPS in production (Heroku/Railway handle this automatically)

---

## Performance Optimization

### For High Traffic

1. **Use Gunicorn with multiple workers:**
```bash
pip install gunicorn
gunicorn gavl_production_api_enhanced:app -w 4 -k uvicorn.workers.UvicornWorker
```

2. **Add Redis caching** for repeated cases:
```python
import redis
cache = redis.Redis(host='localhost', port=6379)

# Cache predictions for 1 hour
cache.setex(f"pred:{case_id}", 3600, json.dumps(prediction))
```

3. **Load models once at startup** (already done in current code)

---

## Next Steps

1. ✅ API is running locally
2. ⬜ Test end-to-end: Submit case on website → Get verdict
3. ⬜ Deploy to cloud (Heroku/Railway/AWS)
4. ⬜ Update website with production URL
5. ⬜ Set up monitoring and logging
6. ⬜ Add rate limiting and API keys
7. ⬜ Train real models (if needed)

---

**Questions? Contact:** inventor@aios.is

**Last Updated:** October 29, 2025
