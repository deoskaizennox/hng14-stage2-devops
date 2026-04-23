from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import uuid
import os

app = FastAPI()

# Fix #8: CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fix #1: Redis host from env, decode_responses for string handling
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


@app.get("/health")
def health():
    try:
        r.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unreachable: {e}")


@app.post("/jobs")
def create_job():
    try:
        job_id = str(uuid.uuid4())
        r.lpush("job", job_id)
        r.hset(f"job:{job_id}", "status", "queued")
        return {"job_id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": status}
