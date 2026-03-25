import pytest
import pandas as pd
from framework.log_analyzer import LogAnalyzer, FailureType
from scripts.data_simulator import generate_thermal_data


@pytest.fixture
def analyzer():
    return LogAnalyzer()


@pytest.fixture
def sample_df():
    return generate_thermal_data(hours=2, output_path="logs/test_sim.csv")


class TestLogAnalyzer:

    def test_classify_critical_temp(self, analyzer):
        """LA-001: Temp > 90°C must classify as Product Defect"""
        result = analyzer.classify_entry(92)
        assert result == FailureType.PRODUCT_DEFECT

    def test_classify_sensor_timeout(self, analyzer):
        """LA-002: Sensor timeout must classify as Test Issue"""
        result = analyzer.classify_entry(55, "sensor_timeout_error")
        assert result == FailureType.TEST_ISSUE

    def test_classify_normal_temp(self, analyzer):
        """LA-003: Normal temp must classify correctly"""
        result = analyzer.classify_entry(55)
        assert result == FailureType.NORMAL

    def test_trend_analysis_runs(self, analyzer, sample_df):
        """LA-004: Trend analysis must return complete summary"""
        summary, classified = analyzer.identify_trends(sample_df)

        required_keys = [
            'total_entries',
            'avg_temp',
            'max_temp',
            'product_defects'
        ]

        for key in required_keys:
            assert key in summary, f"Missing key: {key}"

    def test_anomaly_detection(self, analyzer, sample_df):
        """LA-005: Anomaly detection must return DataFrame"""
        anomalies = analyzer.detect_anomalies(sample_df)
        assert isinstance(anomalies, pd.DataFrame)