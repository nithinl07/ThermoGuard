import pandas as pd
import numpy as np
from enum import Enum
import os


class FailureType(Enum):
    TEST_ISSUE = "Test Issue"
    PRODUCT_DEFECT = "Product Defect"
    WARNING = "Warning"
    NORMAL = "Normal"


class LogAnalyzer:
    """Analyzes thermal CSV logs for anomalies and failure trends"""

    TEMP_CRITICAL = 90   # °C — product defect threshold
    TEMP_WARNING = 80    # °C — warning threshold
    TEMP_NORMAL_MAX = 70 # °C — normal operating max

    def load_log(self, log_path):
        """Load thermal CSV log into DataFrame"""
        if not os.path.exists(log_path):
            raise FileNotFoundError(f"Log not found: {log_path}")

        df = pd.read_csv(log_path, parse_dates=['timestamp'])
        df = df.dropna()
        df['cpu_temp'] = pd.to_numeric(df['cpu_temp'], errors='coerce')

        print(f"Loaded {len(df)} log entries")
        return df

    def classify_entry(self, temp, event=""):
        """Classify a single log entry"""

        if temp > self.TEMP_CRITICAL:
            return FailureType.PRODUCT_DEFECT

        elif "sensor_timeout" in str(event).lower():
            return FailureType.TEST_ISSUE

        elif temp > self.TEMP_WARNING:
            return FailureType.WARNING

        return FailureType.NORMAL

    def classify_all(self, df):
        """Add failure_type column to DataFrame"""

        df['failure_type'] = df.apply(
            lambda row: self.classify_entry(
                row['cpu_temp'],
                row.get('event', '')
            ),
            axis=1
        )

        return df

    def identify_trends(self, df):
        """Find failure patterns and statistics"""
        classified = self.classify_all(df.copy())
        total = len(classified)

        summary = {
            'total_entries': total,
            'avg_temp': round(classified['cpu_temp'].mean(), 2),
            'max_temp': round(classified['cpu_temp'].max(), 2),
            'min_temp': round(classified['cpu_temp'].min(), 2),
            'product_defects': len(classified[classified['failure_type'] == FailureType.PRODUCT_DEFECT]),
            'test_issues': len(classified[classified['failure_type'] == FailureType.TEST_ISSUE]),
            'warnings': len(classified[classified['failure_type'] == FailureType.WARNING]),
            'normal': len(classified[classified['failure_type'] == FailureType.NORMAL]),
            'throttle_events': len(classified[classified['event'] == 'THROTTLE']),
        }

        print("\n===== TREND ANALYSIS =====")
        for k, v in summary.items():
            print(f"{k:25} {v}")

        return summary, classified

    def detect_anomalies(self, df, window=5, threshold=10):
        """Detect sudden temperature spikes using rolling mean"""
        df = df.copy()
        df['rolling_mean'] = df['cpu_temp'].rolling(window=window).mean()
        df['deviation'] = abs(df['cpu_temp'] - df['rolling_mean'])

        anomalies = df[df['deviation'] > threshold]

        print(f"\nAnomalies detected: {len(anomalies)}")
        return anomalies