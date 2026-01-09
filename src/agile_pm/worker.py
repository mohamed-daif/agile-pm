"""Celery worker entry point."""
import signal
import sys
from agile_pm.queue.celery_app import celery_app

def signal_handler(signum, frame):
    print("Shutting down worker gracefully...")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    celery_app.worker_main(["worker", "-l", "INFO"])

if __name__ == "__main__":
    main()
