import random
from datetime import datetime, timedelta


# ============================================================
# FLOOD DETECTION THRESHOLDS
# ============================================================

NORMAL_THRESHOLD = 0.05    # m/min
ALERT_THRESHOLD = 0.15     # m/min


# ============================================================
# FLOOD MODULE
# ============================================================

class Flood:

    def __init__(self):
        # Initial simulated water level
        self.water_level = 2.000

        # Simulated time
        self.simulated_time = datetime.now()

        # Previous reading
        self.previous_level = self.water_level
        self.previous_time = self.simulated_time

        # Simulation stage
        self.reading_number = 0

    # --------------------------------------------------------
    # Simulated water sensor
    # --------------------------------------------------------

    def generate_water_level(self, condition):

        if condition == "normal":
            change = random.uniform(0.01, 0.04)

        elif condition == "warning":
            change = random.uniform(0.06, 0.14)

        elif condition == "alert":
            change = random.uniform(0.16, 0.25)

        else:
            change = 0

        return self.water_level + change

    # --------------------------------------------------------
    # Calculate rate of water-level rise
    # --------------------------------------------------------

    def calculate_rate_of_change(
        self,
        previous_level,
        current_level,
        previous_time,
        current_time
    ):

        level_difference = current_level - previous_level

        time_difference = (
            current_time - previous_time
        ).total_seconds() / 60

        if time_difference <= 0:
            return 0

        rate = level_difference / time_difference

        # Water falling is not considered a flood rise
        if rate < 0:
            rate = 0

        return rate

    # --------------------------------------------------------
    # Determine flood status
    # --------------------------------------------------------

    def determine_status(self, rate):

        if rate < NORMAL_THRESHOLD:
            return "normal"

        elif rate < ALERT_THRESHOLD:
            return "warning"

        else:
            return "high"

    # --------------------------------------------------------
    # Generate reading for AUV simulator
    # --------------------------------------------------------

    def generate_reading(self):

        self.reading_number += 1

        # 5 normal → 5 warning → 5 alert
        stage = (self.reading_number - 1) // 5

        if stage == 0:
            condition = "normal"

        elif stage == 1:
            condition = "warning"

        else:
            condition = "alert"

        # Generate new water level
        current_level = self.generate_water_level(condition)

        # Move simulated time by 1 minute
        current_time = self.simulated_time + timedelta(minutes=1)

        # Calculate rate
        rate = self.calculate_rate_of_change(
            self.previous_level,
            current_level,
            self.previous_time,
            current_time
        )

        # Determine status
        status = self.determine_status(rate)

        # Update previous values
        self.water_level = current_level
        self.previous_level = current_level
        self.previous_time = current_time
        self.simulated_time = current_time

        # Return module JSON
        return {
            "module": "flood",
            "timestamp": current_time.strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),
            "status": status,
            "value": round(rate, 3),
            "water_level": round(current_level, 3),
            "rate_m_per_min": round(rate, 3),
            "alert": status == "high",
            "alert_type": "FLOOD_RISK" if status == "high" else None,
            "action": (
                "Log readings quietly"
                if status == "normal"
                else
                "Flag potential risk to dashboard"
                if status == "warning"
                else
                "Raise immediate flood warning"
            )
        }