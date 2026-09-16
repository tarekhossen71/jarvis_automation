import threading
import time
from datetime import datetime


class Scheduler:

    def __init__(self):
        self.jobs = []
        self.running = False
        self.thread = None

    # =========================================================
    # ADD JOB
    # =========================================================

    def every(self, seconds: int, callback, name: str = "job"):
        """
        Run a callback repeatedly after a fixed number
        of seconds.
        """

        job = {
            "name": name,
            "interval": seconds,
            "callback": callback,
            "last_run": 0,
        }

        self.jobs.append(job)

        print(
            f"⏰ Scheduled: {name} "
            f"(every {seconds} seconds)"
        )

        return job

    # =========================================================
    # REMOVE JOB
    # =========================================================

    def remove(self, name: str):

        self.jobs = [
            job
            for job in self.jobs
            if job["name"] != name
        ]

    # =========================================================
    # RUN LOOP
    # =========================================================

    def _run_loop(self):

        while self.running:

            now = time.time()

            for job in self.jobs:

                if now - job["last_run"] >= job["interval"]:

                    try:

                        print(
                            f"⏰ Running scheduled job: "
                            f"{job['name']}"
                        )

                        job["callback"]()

                    except Exception as e:

                        print(
                            f"❌ Scheduler error "
                            f"[{job['name']}]: {e}"
                        )

                    job["last_run"] = now

            time.sleep(1)

    # =========================================================
    # START
    # =========================================================

    def start(self):

        if self.running:
            return

        self.running = True

        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
        )

        self.thread.start()

        print("⏰ Scheduler started.")

    # =========================================================
    # STOP
    # =========================================================

    def stop(self):

        self.running = False

        print("⏰ Scheduler stopped.")

    # =========================================================
    # LIST JOBS
    # =========================================================

    def get_jobs(self):

        return [
            {
                "name": job["name"],
                "interval": job["interval"],
            }
            for job in self.jobs
        ]