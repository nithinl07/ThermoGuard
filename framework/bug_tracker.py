import requests
import datetime
import os


class BugTracker:
    """Auto-create GitHub Issues for thermal defects — 100% free"""

    def __init__(self, repo=None, token=None):
        # Set these as environment variables — never hardcode!
        self.repo = repo or os.environ.get('GITHUB_REPO')
        self.token = token or os.environ.get('GITHUB_TOKEN')
        self.base = "https://api.github.com"

    def create_issue(self, title, body, labels=None):
        """Create GitHub Issue for a detected defect"""

        if not self.token or not self.repo:
            print("GITHUB_TOKEN or GITHUB_REPO not set. Skipping issue creation.")
            return None

        url = f"{self.base}/repos/{self.repo}/issues"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "title": title,
            "body": body,
            "labels": labels or ["bug", "thermal-defect"]
        }

        resp = requests.post(url, json=payload, headers=headers)

        if resp.status_code == 201:
            issue = resp.json()
            print(f"Issue created: #{issue['number']} → {issue['html_url']}")
            return issue
        else:
            print(f"Failed: {resp.status_code} — {resp.text}")
            return None

    def auto_report_defects(self, summary):
        """Auto-create issues from trend analysis summary"""

        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        if summary.get('product_defects', 0) > 0:
            body = f"""
## ✅ Thermal Defect Detected
**Timestamp:** {ts}  
**Peak Temp:** {summary['max_temp']}°C (threshold: 90°C)  
**Defect Count:** {summary['product_defects']}  
**Throttle Events:** {summary['throttle_events']}

## 🧪 Steps to Reproduce
1. Run ThermoGuard under high load  
2. Monitor CPU temperature log  

## 📌 Expected vs Actual
- **Expected:** CPU stays below 90°C  
- **Actual:** Peak recorded at {summary['max_temp']}°C  

## ⚠️ Impact
Product quality risk — cooling system may not be functioning correctly.
"""

            self.create_issue(
                title=f"[THERMAL DEFECT] Critical temp exceedance — {ts}",
                body=body,
                labels=["bug", "thermal-defect", "priority-high"]
            )