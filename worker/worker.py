import redis
import time
import os
import signal
from pathlib import Path

redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

running = True
health_file = Path("/tmp/worker_health")


def signal_handler(sig, frame):
    global running
    print("Received shutdown signal")
    running = False
    health_file.unlink(missing_ok=True)


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


def process_job(job_id):
    try:
        print(f"Processing job {job_id}")
        health_file.write_text(f"processing:{job_id}")
        time.sleep(2)
        r.hset(f"job:{job_id}", "status", "completed")
        print(f"Done: {job_id}")
        health_file.write_text("idle")
    except Exception as e:
        print(f"Error: {e}")
        r.hset(f"job:{job_id}", "status", "failed")


print("Worker started")
health_file.write_text("started")

while running:
    try:
        job = r.brpop("job", timeout=5)
        if job and running:
            _, job_id = job
            process_job(job_id)
        health_file.write_text("waiting")
    except Exception as e:
        print(f"Worker error: {e}")
        time.sleep(1)

health_file.unlink(missing_ok=True)
print("Worker shutdown")
