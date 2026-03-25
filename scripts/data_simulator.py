import numpy as np
import pandas as pd
import os


def generate_thermal_data(hours=8, output_path="logs/thermal_log.csv"):
    """Generate realistic simulated thermal log data"""

    os.makedirs("logs", exist_ok=True)

    n = hours * 60  # one row per minute
    timestamps = pd.date_range("2024-01-01", periods=n, freq="1min")

    # Realistic temp pattern: idle → load → recovery cycles
    base = 45
    spikes = np.random.choice([0, 12, 28, 47], n, p=[0.65, 0.2, 0.1, 0.05])
    noise = np.random.normal(0, 2, n)

    temps = np.clip(base + spikes + noise, 35, 98)
    cpu_pct = np.clip(spikes * 2 + np.random.normal(10, 5, n), 0, 100)

    events = ["THROTTLE" if t > 85 else "NORMAL" for t in temps]

    df = pd.DataFrame({
        'timestamp': timestamps,
        'cpu_temp': np.round(temps, 2),
        'cpu_percent': np.round(cpu_pct, 1),
        'event': events
    })

    df.to_csv(output_path, index=False)
    print(f"Generated {n} rows → {output_path}")

    return df


if __name__ == "__main__":
    generate_thermal_data(hours=24)