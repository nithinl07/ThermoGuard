import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os


class ThermalDashboard:
    """Generate interactive HTML dashboard from thermal log data"""

    def load_data(self, log_path="logs/thermal_log.csv"):
        df = pd.read_csv(log_path, parse_dates=['timestamp'])
        df['cpu_temp'] = pd.to_numeric(df['cpu_temp'], errors='coerce')
        return df.dropna()

    def generate(self, log_path="logs/thermal_log.csv", output="docs/index.html"):
        """Build and save the full dashboard as HTML"""
        os.makedirs("docs", exist_ok=True)

        df = self.load_data(log_path)

        # Classify events for coloring
        def color_event(evt):
            return '#ff4444' if evt == 'THROTTLE' else '#00d4ff'

        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                'CPU Temperature Timeline',
                'Event Distribution',
                'CPU Load vs Temperature',
                'Temperature Histogram'
            ),
            specs=[[{}, {}], [{}, {}]]
        )

        # 1. Temperature timeline
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['cpu_temp'],
                mode='lines',
                name='CPU Temp (°C)',
                line=dict(color='#ff6b35', width=1.5),
                fill='tozeroy',
                fillcolor='rgba(255,107,53,0.1)'
            ),
            row=1,
            col=1
        )

        # Critical threshold line
        fig.add_hline(
            y=85,
            line_dash='dash',
            line_color='red',
            row=1,
            col=1,
            annotation_text="Critical (85°C)"
        )

        # 2. Event distribution pie
        event_counts = df['event'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=event_counts.index,
                values=event_counts.values,
                name='Events',
                marker_colors=['#ff4444', '#00d4ff']
            ),
            row=1,
            col=2
        )

        # 3. Scatter: CPU% vs Temp
        fig.add_trace(
            go.Scatter(
                x=df['cpu_percent'],
                y=df['cpu_temp'],
                mode='markers',
                name='Load vs Temp',
                marker=dict(
                    color=df['cpu_temp'],
                    colorscale='RdYlBu_r',
                    size=4,
                    showscale=True
                )
            ),
            row=2,
            col=1
        )

        # 4. Temperature histogram
        fig.add_trace(
            go.Histogram(
                x=df['cpu_temp'],
                nbinsx=30,
                name='Temp Distribution',
                marker_color='#7fff6b',
                opacity=0.8
            ),
            row=2,
            col=2
        )

        # Dashboard layout & theme
        fig.update_layout(
            title=dict(
                text='ThermoGuard — Thermal SQA Dashboard',
                font=dict(size=22)
            ),
            paper_bgcolor='#0a0a0f',
            plot_bgcolor='#111118',
            font=dict(color='#e8e8f0'),
            height=700,
            showlegend=False
        )

        fig.write_html(output, include_plotlyjs='cdn')
        print(f"Dashboard saved → {output}")

        return output


if __name__ == "__main__":
    from scripts.data_simulator import generate_thermal_data

    generate_thermal_data(hours=24)
    ThermalDashboard().generate()