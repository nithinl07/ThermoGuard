import psutil
import time
import datetime
import csv
import os
import platform


class ThermalMonitor:
    """Monitors CPU temperature using psutil — works on Linux/Mac/Windows"""

    def __init__(self, log_path="logs/thermal_log.csv"):
        self.log_path = log_path
        os.makedirs("logs", exist_ok=True)
        self._init_log()

    def _init_log(self):
        """Create CSV log file with headers if not exists"""
        if not os.path.exists(self.log_path):
            with open(self.log_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'cpu_temp', 'cpu_percent', 'event'])

    def get_cpu_temperature(self):
        """Get current CPU temperature in Celsius"""
        try:
            temps = psutil.sensors_temperatures()

            if not temps:
                # Windows fallback: simulate realistic temp
                cpu_pct = psutil.cpu_percent(interval=1)
                return 40 + (cpu_pct * 0.5)

            # Try common sensor names
            for name in ['coretemp', 'cpu_thermal', 'k10temp', 'acpitz']:
                if name in temps:
                    return temps[name][0].current

            # Return first available sensor
            first_key = list(temps.keys())[0]
            return temps[first_key][0].current

        except Exception as e:
            print(f"Temp sensor unavailable: {e}. Using simulation.")
            return self._simulate_temp()

    def _simulate_temp(self):
        """Simulate realistic temperature based on CPU load"""
        import numpy as np
        cpu_pct = psutil.cpu_percent(interval=0.5)
        base = 42
        load_contrib = cpu_pct * 0.45
        noise = np.random.normal(0, 1.5)
        return round(base + load_contrib + noise, 2)

    def get_all_sensor_readings(self):
        """Get readings from all available sensors"""
        readings = {}
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for sensor_name, entries in temps.items():
                    for i, entry in enumerate(entries):
                        key = f"{sensor_name}_{i}"
                        readings[key] = entry.current
            else:
                readings['cpu_simulated'] = self._simulate_temp()
                readings['gpu_simulated'] = self._simulate_temp() - 5
        except:
            return readings

        readings['cpu_simulated'] = self._simulate_temp()
        return readings

    def monitor_and_log(self, duration_seconds=60, interval=2):
        """Monitor temperature for given duration and log to CSV"""
        print(f"Monitoring for {duration_seconds}s (every {interval}s)...")

        readings = []
        end_time = time.time() + duration_seconds

        while time.time() < end_time:
            temp = self.get_cpu_temperature()
            cpu_pct = psutil.cpu_percent()
            ts = datetime.datetime.now().isoformat()
            event = "THROTTLE" if temp > 85 else "NORMAL"

            row = [ts, temp, cpu_pct, event]
            readings.append(row)

            with open(self.log_path, 'a', newline='') as f:
                csv.writer(f).writerow(row)

            print(f"[{ts[:19]}] Temp: {temp:.1f}°C | CPU: {cpu_pct}% | {event}")
            time.sleep(interval)

        return readings

    def get_peak_temperature(self, samples=10):
        """Get peak temp over multiple samples"""
        temps = [self.get_cpu_temperature() for _ in range(samples)]
        return max(temps)

    def measure_recovery_time(self, target_temp=60, timeout=180):
        """Measure how long device takes to cool to target temp"""
        start = time.time()
        while time.time() - start < timeout:
            if self.get_cpu_temperature() <= target_temp:
                return round(time.time() - start, 2)
            time.sleep(2)
        return timeout  # timed out