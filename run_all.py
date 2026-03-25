"""
ThermoGuard — Full Pipeline Runner
Run this to execute the entire project end-to-end.
"""

import subprocess
import sys
from scripts.data_simulator import generate_thermal_data
from framework.log_analyzer import LogAnalyzer
from dashboard.thermal_dashboard import ThermalDashboard
from scripts.report_generator import generate_report
from framework.bug_tracker import BugTracker


def run_pipeline():
    print("\n" + "=" * 50)
    print(" THERMOGUARD PIPELINE STARTING")
    print("=" * 50 + "\n")

    # Step 1: Generate simulated thermal data
    print("[1/5] Generating thermal data...\n")
    generate_thermal_data(hours=24)

    # Step 2: Run test suite
    print("\n[2/5] Running test suite...\n")
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/test_log_analyzer.py", "-v",
        "--html=reports/test_report.html",
        "--self-contained-html"
    ])

    # Step 3: Analyze logs
    print("\n[3/5] Analyzing thermal logs...\n")
    analyzer = LogAnalyzer()
    df = analyzer.load_log("logs/thermal_log.csv")
    summary, _ = analyzer.identify_trends(df)
    analyzer.detect_anomalies(df)

    # Step 4: Generate dashboard
    print("\n[4/5] Generating dashboard...\n")
    ThermalDashboard().generate()

    # Step 5: Generate report
    print("\n[5/5] Generating test report...\n")
    generate_report()

    # Optional: Auto-create GitHub issues for defects
    tracker = BugTracker()
    tracker.auto_report_defects(summary)

    print("\n" + "=" * 50)
    print(" PIPELINE COMPLETE")
    print(" Dashboard → docs/index.html")
    print(" Test Report → reports/test_report.html")
    print(" Thermal Rpt → reports/thermal_report.html")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_pipeline()
