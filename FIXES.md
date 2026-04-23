## Bug Fixes Documentation

# Overview
This document lists all bugs found and fixed in the Stage 2 microservices application.

---

## Fixes Found

## Fix #1: API Redis Connection Hardcoded to Localhost

**File:** `api/main.py`  
**Line:** 8
**Problem:** Redis client connects to `localhost:6379` which won't work in Docker containers where Redis runs in a separate container named `redis`  
**Impact:** API cannot connect to Redis when containerized  
**Solution:** Use environment variable `REDIS_HOST` with default value `redis`  
**Before:**
```python
r = redis.Redis(host="localhost", port=6379)```
**After:**
```python
1 redis_host = os.getenv("REDIS_HOST","redis")
2 r = redis.Redis(host=redis_host, port=6379)```

## Fix #2: Frontend API URL Hardcoded to Localhost

**File:** `frontend/app.js`
**Line:** 5
**Problem:** Frontend makes requests to http://localhost:8000 which won't work in Docker network
**Impact:** Frontend cannot communicate with API service in containerized environment
**Solution:** Use environment variable API_URL with default http://api:8000
**Before:**
```javascript
1 const API_URL = "http://localhost:8000";```
**After:**
```javascript
1 const API_URL = process.env.API_URL || "http://api:8000";```


##Fix #3: Missing Health Check Endpoints

**File:** api/main.py
**Line:** Add after line 11
**Problem:** No /health endpoint for Docker HEALTHCHECK and load balancer health verification
**Impact:** Cannot verify service health, Docker HEALTHCHECK will fail
**Solution:** Add health check route
**After:**

```python
1 @app.get("/health")
2 def health ():
	return {"status": "healthy"}```


**File:** frontend/app.js
**Line:** Add after line 11
**Problem:** No /health endpoint
**Impact:** Cannot verify frontend service health
**Solution:** Add health check route
**After:**

```javascript
1 app.get('/health', (req,res) => {
    res.json({ status: 'healthy' });
  });```



---

## Fix #4: Worker Redis Connection Hardcoded to Localhost

**File:** `worker/worker.py`  
**Line:** 7  
**Problem:** Redis client connects to `localhost:6379` which won't work in Docker containers  
**Impact:** Worker cannot connect to Redis when containerized  
**Solution:** Use environment variable `REDIS_HOST` with default value `redis`  
**Before:**

```python
r = redis.Redis(host="localhost", port=6379)```

**After:**
```python
redis_host = os.getenv("REDIS_HOST", "redis")
r = redis.Redis(host=redis_host, port=6379, decode_responses=True)```


## Fix #5: Worker Missing Graceful Shutdown

**File:** worker/worker.py
**Line:** Missing
**Problem:** No signal handling for SIGTERM/SIGINT, worker cannot shut down gracefully
**Impact:** Docker containers cannot stop worker cleanly, jobs may be interrupted
**Solution:** Add signal handlers to set shutdown flag and finish current job
**After:**
```python
import signal

running = True

def signal_handler(sig, frame):
    global running
    print("Received shutdown signal")
    running = False

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)```


## Fix #6: Worker Missing Error Handling

**File:** worker/worker.py
**Line:** 24-26 (while loop)
**Problem:** No try/except around job processing, worker crashes on errors
**Impact:** Single job failure crashes entire worker
**Solution:** Wrap job processing in try/except block
**After:**
```python
while running:
    try:
        job = r.brpop("job", timeout=5)
        if job and running:
            _, job_id = job
            process_job(job_id)
    except Exception as e:
        print(f"Worker error: {e}")
        time.sleep(1)```


## Fix #7: API Missing CORS Configuration

**File:** api/main.py
**Line:** Missing
**Problem:** No CORS headers, browser blocks frontend→API requests
**Impact:** Frontend cannot make cross-origin requests to API
**Solution:** Add CORS middleware
**After:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)```

## Fix #8: API Missing Error Status Codes

**File:** api/main.py
**Line:** 14-22
**Problem:** Error responses return HTTP 200 instead of 404/500
**Impact:** Clients cannot detect errors from status code
**Solution:** Return proper HTTP status codes
**After:**
```python
from fastapi import HTTPException

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": status.decode()}```


## Fix #9: Missing /views Directory

**File:** frontend/app.js
**Line:** 9
**Problem:** Express serves static files from views/ directory that doesn't exist
**Impact:** Frontend crashes on startup with directory not found error
**Solution:** Create views directory with index.html
**After:**
```bash
mkdir -p views
echo "<h1>Job Submission System</h1>" > views/index.html```

**TOTAL BUGS FOUND: 9**

