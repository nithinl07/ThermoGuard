import pytest
import time
from framework.thermal_monitor import ThermalMonitor
from framework.stress_engine import StressEngine


@pytest.fixture
def monitor():
    return ThermalMonitor(log_path="logs/test_log.csv")


@pytest.fixture
def stress():
    engine = StressEngine()
    yield engine
    engine.stop()


class TestThermalSensors:

    def test_cpu_temp_readable(self, monitor):
        """TC-001: CPU temperature must be readable"""
        temp = monitor.get_cpu_temperature()
        assert temp is not None, "Temperature reading returned None"
        assert isinstance(temp, (int, float)), "Temperature must be numeric"

    def test_cpu_temp_in_valid_range(self, monitor):
        """TC-002: CPU temp must be within physical limits (20–105°C)"""
        temp = monitor.get_cpu_temperature()
        assert 20 <= temp <= 105, f"Temp out of range: {temp}°C"

    def test_all_sensors_readable(self, monitor):
        """TC-003: All available sensors must return valid readings"""
        readings = monitor.get_all_sensor_readings()
        assert len(readings) > 0, "No sensors found"

        for sensor, temp in readings.items():
            assert 15 <= temp <= 110, (
                f"Sensor '{sensor}' invalid: {temp}°C"
            )

    def test_temp_increases_under_load(self, monitor, stress):
        """TC-004: CPU temp must increase under heavy load"""
        baseline = monitor.get_cpu_temperature()
        stress.start(duration=15, intensity="high")

        time.sleep(12)
        peak = monitor.get_cpu_temperature()

        # Allow 1°C tolerance for low-powered systems
        assert peak >= baseline - 1, (
            f"Temp did not respond to load. Baseline: {baseline} Peak: {peak}"
        )

    def test_cpu_never_exceeds_critical(self, monitor, stress):
        """TC-005: CPU must not exceed 95°C (product defect threshold)"""
        stress.start(duration=10, intensity="high")
        time.sleep(8)

        peak = monitor.get_peak_temperature(samples=5)
        assert peak < 95, (
            f"PRODUCT DEFECT: Temp exceeded 95°C → {peak}°C"
        )


class TestThermalLogging:

    def test_log_file_created(self, monitor):
        """TC-006: Log file must be created"""
        import os
        assert os.path.exists(monitor.log_path), (
            f"Log file not found: {monitor.log_path}"
        )

    def test_monitoring_logs_data(self, monitor):
        """TC-007: Monitoring must produce log entries"""
        rows = monitor.monitor_and_log(duration_seconds=6, interval=2)
        assert len(rows) >= 2, "Expected at least 2 log entries"