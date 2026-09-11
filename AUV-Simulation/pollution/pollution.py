import random
import time
import json
from datetime import datetime, timezone

# ---- Thresholds (tune these based on real-world reference values) ----
THRESHOLDS = {
    "ph": {"normal": (6.5, 8.5), "warning": (6.0, 9.0)},
    "turbidity_ntu": {"normal": (0, 5), "warning": (5, 15)},
    "dissolved_oxygen_mgL": {"normal": (6.5, 14), "warning": (4, 6.5)},
    "heavy_metals_ppm": {"normal": (0, 0.01), "warning": (0.01, 0.05)},
}


class PollutionSensor:
    """Stateful simulator so readings drift smoothly instead of jumping randomly."""

    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

        # start at healthy baseline values
        self.state = {
            "ph": 7.2,
            "turbidity_ntu": 2.0,
            "dissolved_oxygen_mgL": 9.0,
            "heavy_metals_ppm": 0.002,
        }

    def _drift(self, key, step, min_val, max_val):
        """Random walk with soft bounds."""
        change = random.uniform(-step, step)
        self.state[key] = max(
            min_val,
            min(max_val, self.state[key] + change)
        )

    def _inject_event(self):
        """Occasionally simulate a pollution spike (e.g. runoff, dumping)."""
        if random.random() < 0.05:
            spike_target = random.choice(list(self.state.keys()))

            if spike_target == "dissolved_oxygen_mgL":
                self.state[spike_target] *= 0.5
            else:
                self.state[spike_target] *= random.uniform(2, 4)

    def _classify(self, key, value):
        norm_lo, norm_hi = THRESHOLDS[key]["normal"]
        warn_lo, warn_hi = THRESHOLDS[key]["warning"]

        if norm_lo <= value <= norm_hi:
            return "normal"

        elif warn_lo <= value <= warn_hi:
            return "warning"

        else:
            return "critical"

    def read(self) -> dict:

        # update each metric
        self._drift("ph", 0.05, 4, 10)
        self._drift("turbidity_ntu", 0.3, 0, 50)
        self._drift("dissolved_oxygen_mgL", 0.2, 0, 14)
        self._drift("heavy_metals_ppm", 0.001, 0, 0.2)

        self._inject_event()

        metrics = {
            k: round(v, 4)
            for k, v in self.state.items()
        }

        statuses = {
            k: self._classify(k, v)
            for k, v in metrics.items()
        }

        # overall status = worst individual status
        severity_rank = {
            "normal": 0,
            "warning": 1,
            "critical": 2
        }

        overall_status = max(
            statuses.values(),
            key=lambda s: severity_rank[s]
        )

        reading = {
            "timestamp":
                datetime.now(timezone.utc).isoformat(),

            "module":
                "pollution",

            "value":
                metrics["turbidity_ntu"],

            "status":
                overall_status,

            "alert":
                overall_status != "normal",

            "metrics":
                metrics,

            "metric_statuses":
                statuses,
        }

        return reading


def generate_reading(
    sensor: PollutionSensor = None
) -> dict:

    """Convenience function for one-off use
    (e.g. from a Flask/FastAPI endpoint)."""

    sensor = sensor or PollutionSensor()

    return sensor.read()


if __name__ == "__main__":

    sensor = PollutionSensor(seed=42)

    print(
        "AquaSentinel Pollution Module — "
        "live simulated stream (Ctrl+C to stop)\n"
    )

    try:

        while True:

            reading = sensor.read()

            print(
                json.dumps(
                    reading,
                    indent=2
                )
            )

            print("-" * 50)

            time.sleep(2)

    except KeyboardInterrupt:

        print("\nStopped.")