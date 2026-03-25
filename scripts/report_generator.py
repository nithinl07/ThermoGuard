from jinja2 import Template
import datetime
import os
from framework.log_analyzer import LogAnalyzer
from scripts.data_simulator import generate_thermal_data


TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ThermoGuard Test Report</title>
<style>
body { font-family: monospace; background: #0a0a0f; color: #e8e8f0; padding: 40px; }
h1 { color: #ff6b35; border-bottom: 2px solid #ff6b35; padding-bottom: 10px; }
h2 { color: #00d4ff; margin-top: 32px; }

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin: 24px 0; }
.stat { background: #1a1a24; border: 1px solid #2a2a3a; padding: 16px; text-align: center; }
.stat .val { font-size: 32px; font-weight: bold; color: #ff6b35; }
.stat .lbl { font-size: 11px; color: #6b6b80; text-transform: uppercase; letter-spacing: 1px; }

.pass { color: #7fff6b; }
.fail { color: #ff4444; }
.warn { color: #ffd700; }

table { width: 100%; border-collapse: collapse; margin-top: 16px; }
th { background: #1a1a24; padding: 10px; text-align: left; font-size: 11px; letter-spacing: 1px; color: #6b6b80; }
td { padding: 10px; border-bottom: 1px solid #2a2a3a; }

.badge { display: inline-block; padding: 2px 10px; font-size: 11px; font-weight: bold; }
.badge.defect { background: rgba(255,68,68,0.2); color: #ff4444; }
.badge.warn { background: rgba(255,215,0,0.2); color: #ffd700; }
.badge.ok   { background: rgba(127,255,107,0.2); color: #7fff6b; }
</style>
</head>

<body>
<h1>ThermoGuard — Thermal SQA Test Report</h1>
<p>Generated: {{ date }} | Product: MacBook Simulation</p>

<h2>Summary</h2>
<div class="stat-grid">

<div class="stat">
  <div class="val">{{ summary.total_entries }}</div>
  <div class="lbl">Log Entries</div>
</div>

<div class="stat">
  <div class="val" style="color:#ff4444">{{ summary.product_defects }}</div>
  <div class="lbl">Product Defects</div>
</div>

<div class="stat">
  <div class="val" style="color:#ffd700">{{ summary.warnings }}</div>
  <div class="lbl">Warnings</div>
</div>

<div class="stat">
  <div class="val">{{ summary.avg_temp }}°C</div>
  <div class="lbl">Avg Temp</div>
</div>

</div>

<h2>Thermal Statistics</h2>
<table>
<tr>
  <th>Metric</th>
  <th>Value</th>
  <th>Status</th>
</tr>

<tr>
  <td>Average Temperature</td>
  <td>{{ summary.avg_temp }}°C</td>
  <td><span class="badge ok">PASS</span></td>
</tr>

<tr>
  <td>Peak Temperature</td>
  <td>{{ summary.max_temp }}°C</td>
  <td>
    {% if summary.max_temp > 90 %}
      <span class="badge defect">DEFECT</span>
    {% elif summary.max_temp > 80 %}
      <span class="badge warn">WARN</span>
    {% else %}
      <span class="badge ok">PASS</span>
    {% endif %}
  </td>
</tr>

<tr>
  <td>Throttle Events</td>
  <td>{{ summary.throttle_events }}</td>
  <td>
    {% if summary.throttle_events > 10 %}
      <span class="badge warn">WARN</span>
    {% else %}
      <span class="badge ok">PASS</span>
    {% endif %}
  </td>
</tr>

<tr>
  <td>Product Defects</td>
  <td>{{ summary.product_defects }}</td>
  <td>
    {% if summary.product_defects > 0 %}
      <span class="badge defect">FAIL</span>
    {% else %}
      <span class="badge ok">PASS</span>
    {% endif %}
  </td>
</tr>

</table>

<h2>Recommendations</h2>
<ul>
{% if summary.product_defects > 0 %}
  <li class="fail">CRITICAL: {{ summary.product_defects }} temperature exceedances detected.</li>
{% endif %}

{% if summary.throttle_events > 5 %}
  <li class="warn">Frequent throttling detected — review sustained load conditions.</li>
{% endif %}

{% if summary.product_defects == 0 and summary.throttle_events <= 5 %}
  <li class="pass">All thermal parameters within acceptable limits.</li>
{% endif %}
</ul>

</body>
</html>
"""


def generate_report(log_path="logs/thermal_log.csv"):
    os.makedirs("reports", exist_ok=True)

    # Ensure log exists
    if not os.path.exists(log_path):
        print("No log found, generating simulated data...")
        generate_thermal_data(hours=8, output_path=log_path)

    analyzer = LogAnalyzer()
    df = analyzer.load_log(log_path)
    summary, _ = analyzer.identify_trends(df)

    html = Template(TEMPLATE).render(
        date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        summary=summary
    )

    out = "reports/thermal_report.html"
    with open(out, "w") as f:
        f.write(html)

    print(f"Report saved → {out}")
    return out


if __name__ == "__main__":
    generate_report()