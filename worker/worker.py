import redis
import time
import os
import signal
import sys

# Fix #4: Redis config from environment
redis_host = os.getenv("REDIS_HOST", "redis")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

# Fix #5: Graceful shutdown
running = True
health_file = Path("/tmp/worker_health")

def signal_handler(sig, frame):
    global running
    print("Received shutdown signal. Finishing current job...")
    running = False
    health_file.unlink(missing_ok=True)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def process_job(job_id):
    try:
        print(f"Processing job {job_id}")
	health_file.write_text(f"processing:{job_id}")
        time.sleep(2)  # simulate work
        r.hset(f"job:{job_id}", "status", "completed")
        print(f"Done: {job_id}")
        health_file.write_text("idle")
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")
        r.hset(f"job:{job_id}", "status", "failed")

print("Worker started")
health_file.write_text("started")

# Fix #6: Error handling in main loop
while running:
    try:
        job = r.brpop("job", timeout=5)
        if job and running:
            _, job_id = job
            process_job(job_id)
    except redis.ConnectionError as e:
        print(f"Redis connection lost: {e}. Retrying in 5s...")
        time.sleep(5)
    except Exception as e:
        print(f"Worker error: {e}")
        time.sleep(1)

print("Worker shut down gracefully.")
