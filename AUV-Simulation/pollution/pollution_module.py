import random
from datetime import datetime, timezone


THRESHOLD_PROFILES = {
    "freshwater": {
        "ph": {
            "normal": (6.5, 8.5),
            "warning": (6.0, 9.0)
        },
        "turbidity_ntu": {
            "normal": (0, 5),
            "warning": (5, 15)
        },
        "dissolved_oxygen_mgL": {
            "normal": (6.5, 14),
            "warning": (4, 6.5)
        },
        "heavy_metals_ppm": {
            "normal": (0, 0.01),
            "warning": (0.01, 0.05)
        }
    },

    "seawater": {
        "ph": {
            "normal": (7.5, 8.5),
            "warning": (7.0, 9.0)
        },
        "turbidity_ntu": {
            "normal": (0, 5),
            "warning": (5, 15)
        },
        "dissolved_oxygen_mgL": {
            "normal": (6.0, 14),
            "warning": (4, 6.0)
        },
        "heavy_metals_ppm": {
            "normal": (0, 0.01),
            "warning": (0.01, 0.05)
        }
    }
}


SALINITY_FRESHWATER_MAX = 0.5
SALINITY_SEAWATER_MIN = 30.0


class PollutionSensor:

    def __init__(
        self,
        seed=None,
        water_type="auto",
        depth_m=0,
        surface_salinity=0.2,
        bottom_salinity=35.0,
        halocline_depth=10.0,
        auto_dive=True
    ):

        if seed is not None:
            random.seed(seed)

        self.water_type = water_type

        self.depth_m = depth_m

        self.surface_salinity = surface_salinity
        self.bottom_salinity = bottom_salinity

        self.halocline_depth = halocline_depth

        self.auto_dive = auto_dive

        self.state = {
            "ph": 7.8,
            "turbidity_ntu": 2.0,
            "dissolved_oxygen_mgL": 9.0,
            "heavy_metals_ppm": 0.002
        }

    # =========================
    # SET DEPTH
    # =========================

    def set_depth(self, depth_m):

        self.depth_m = max(
            0,
            float(depth_m)
        )

        # External navigation controls depth
        self.auto_dive = False

    # =========================
    # SALINITY
    # =========================

    def _salinity_at_current_depth(self):

        if self.depth_m <= 0:
            return self.surface_salinity

        if self.depth_m >= self.halocline_depth:
            return self.bottom_salinity

        ratio = (
            self.depth_m /
            self.halocline_depth
        )

        return (
            self.surface_salinity
            +
            (
                self.bottom_salinity
                - self.surface_salinity
            )
            * ratio
        )

    # =========================
    # WATER TYPE
    # =========================

    def _current_water_type(self):

        if self.water_type != "auto":
            return self.water_type

        salinity = self._salinity_at_current_depth()

        if salinity <= SALINITY_FRESHWATER_MAX:
            return "freshwater"

        if salinity >= SALINITY_SEAWATER_MIN:
            return "seawater"

        return "brackish"

    # =========================
    # DRIFT
    # =========================

    def _drift(
        self,
        key,
        step,
        min_val,
        max_val
    ):

        change = random.uniform(
            -step,
            step
        )

        self.state[key] = max(
            min_val,
            min(
                max_val,
                self.state[key] + change
            )
        )

    # =========================
    # RANDOM POLLUTION EVENT
    # =========================

    def _inject_event(self):

        if random.random() < 0.05:

            target = random.choice(
                list(self.state.keys())
            )

            if target == "dissolved_oxygen_mgL":

                self.state[target] *= 0.5

            else:

                self.state[target] *= random.uniform(
                    2,
                    4
                )

    # =========================
    # CLASSIFICATION
    # =========================

    def _classify(
        self,
        key,
        value,
        water_type
    ):

        if water_type == "brackish":
            water_type = "seawater"

        thresholds = THRESHOLD_PROFILES[
            water_type
        ]

        normal_low, normal_high = (
            thresholds[key]["normal"]
        )

        warning_low, warning_high = (
            thresholds[key]["warning"]
        )

        if normal_low <= value <= normal_high:

            return "normal"

        elif warning_low <= value <= warning_high:

            return "warning"

        else:

            return "critical"

    # =========================
    # READ SENSOR
    # =========================

    def read(self):

        # Optional automatic diving
        if self.auto_dive:

            self.depth_m += 1

            if self.depth_m > 30:
                self.depth_m = 0

        self._drift(
            "ph",
            0.05,
            4,
            10
        )

        self._drift(
            "turbidity_ntu",
            0.3,
            0,
            50
        )

        self._drift(
            "dissolved_oxygen_mgL",
            0.2,
            0,
            14
        )

        self._drift(
            "heavy_metals_ppm",
            0.001,
            0,
            0.2
        )

        self._inject_event()

        water_type = self._current_water_type()

        salinity = (
            self._salinity_at_current_depth()
        )

        metrics = {
            "ph": round(
                self.state["ph"],
                4
            ),

            "turbidity_ntu": round(
                self.state["turbidity_ntu"],
                4
            ),

            "dissolved_oxygen_mgL": round(
                self.state["dissolved_oxygen_mgL"],
                4
            ),

            "heavy_metals_ppm": round(
                self.state["heavy_metals_ppm"],
                4
            ),

            "depth_m": round(
                self.depth_m,
                2
            ),

            "salinity_ppt": round(
                salinity,
                2
            )
        }

        metric_statuses = {
            key: self._classify(
                key,
                metrics[key],
                water_type
            )

            for key in self.state.keys()
        }

        severity_rank = {
            "normal": 0,
            "warning": 1,
            "critical": 2
        }

        overall_status = max(
            metric_statuses.values(),
            key=lambda status:
                severity_rank[status]
        )

        return {
            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "module":
                "pollution",

            "water_type":
                water_type,

            "value":
                metrics["turbidity_ntu"],

            "status":
                overall_status,

            "alert":
                overall_status != "normal",

            "metrics":
                metrics,

            "metric_statuses":
                metric_statuses
        }