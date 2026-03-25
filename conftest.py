import pytest
import os


def pytest_configure(config):
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)


def pytest_html_report_title(report):
    report.title = "ThermoGuard — Thermal SQA Test Report"