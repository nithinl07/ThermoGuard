import threading
import time
import multiprocessing


class StressEngine:
    """Pure Python CPU stress — no external tools needed"""

    def __init__(self):
        self._threads = []
        self._running = False

    def _cpu_burn(self):
        """Burn CPU cycles to generate heat"""
        while self._running:
            _ = [x**2 for x in range(10000)]

    def start(self, duration=30, intensity="medium"):
        """Start CPU stress. intensity: low / medium / high"""

        core_map = {
            "low": 1,
            "medium": 2,
            "high": multiprocessing.cpu_count()
        }

        num_cores = core_map.get(intensity, 2)
        self._running = True
        self._threads = []

        for _ in range(num_cores):
            t = threading.Thread(target=self._cpu_burn, daemon=True)
            t.start()
            self._threads.append(t)

        if duration:
            print(f"Stress started: {num_cores} cores for {duration}s")
            threading.Timer(duration, self.stop).start()
        else:
            print(f"Stress started: {num_cores} cores (no time limit)")

    def stop(self):
        self._running = False
        print("Stress stopped")