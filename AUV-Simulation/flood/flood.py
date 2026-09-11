import random
import joblib
import os
import pandas as pd
from datetime import datetime, timedelta


# ============================================================
# FLOOD ML MODULE
# ============================================================

class Flood:

    def __init__(self):

        # ----------------------------------------------------
        # Load trained ML model
        # ----------------------------------------------------

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        self.model = joblib.load(
            os.path.join(BASE_DIR, "flood_model.pkl")
        )

        self.features = joblib.load(
            os.path.join(BASE_DIR, "flood_features.pkl")
        )

        self.labels = joblib.load(
            os.path.join(BASE_DIR, "flood_labels.pkl")
        )

        # ----------------------------------------------------
        # Initial simulated values
        # ----------------------------------------------------

        self.water_level = 2.5

        self.simulated_time = datetime.now()

        self.previous_level = self.water_level

        self.previous_time = self.simulated_time

        # ----------------------------------------------------
        # Location
        # ----------------------------------------------------

        self.latitude = 12.90
        self.longitude = 74.80

        # ----------------------------------------------------
        # Environmental values
        # ----------------------------------------------------

        self.rainfall = 60.0
        self.temperature = 30.0
        self.humidity = 50.0

        self.river_discharge = 1000.0

        self.elevation = 500.0

        self.population_density = 5000.0

        self.historical_floods = 0

        self.reading_number = 0


    # ========================================================
    # GENERATE FLUCTUATING ENVIRONMENTAL CONDITIONS
    # ========================================================

    def generate_environmental_data(self):

        self.reading_number += 1

        # ----------------------------------------------------
        # Create repeating risk cycle
        #
        # 1-5   : LOW
        # 6-10  : MEDIUM
        # 11-15 : HIGH
        # 16-20 : MEDIUM
        # Then repeat
        # ----------------------------------------------------

        cycle_position = (
            (self.reading_number - 1) % 20
        ) + 1


        # ====================================================
        # LOW RISK
        # ====================================================

        if cycle_position <= 5:

            self.rainfall = random.uniform(
                40,
                90
            )

            self.humidity = random.uniform(
                40,
                60
            )

            self.river_discharge = random.uniform(
                500,
                1500
            )

            self.water_level = random.uniform(
                2.0,
                3.5
            )

            self.historical_floods = 0


        # ====================================================
        # MEDIUM RISK
        # ====================================================

        elif cycle_position <= 10:

            self.rainfall = random.uniform(
                120,
                190
            )

            self.humidity = random.uniform(
                60,
                74
            )

            self.river_discharge = random.uniform(
                2000,
                3200
            )

            self.water_level = random.uniform(
                4.2,
                6.2
            )

            self.historical_floods = random.choice(
                [0, 1]
            )


        # ====================================================
        # HIGH RISK
        # ====================================================

        elif cycle_position <= 15:

            self.rainfall = random.uniform(
                220,
                350
            )

            self.humidity = random.uniform(
                75,
                95
            )

            self.river_discharge = random.uniform(
                3500,
                5000
            )

            self.water_level = random.uniform(
                7.2,
                9.5
            )

            self.historical_floods = 1


        # ====================================================
        # MEDIUM RISK - RETURNING TO NORMAL
        # ====================================================

        else:

            self.rainfall = random.uniform(
                120,
                190
            )

            self.humidity = random.uniform(
                60,
                74
            )

            self.river_discharge = random.uniform(
                2000,
                3200
            )

            self.water_level = random.uniform(
                4.2,
                6.2
            )

            self.historical_floods = random.choice(
                [0, 1]
            )


        # ----------------------------------------------------
        # Small temperature variation
        # ----------------------------------------------------

        self.temperature += random.uniform(
            -0.3,
            0.3
        )

        self.temperature = max(
            20,
            min(
                self.temperature,
                40
            )
        )


    # ========================================================
    # ML FLOOD-RISK PREDICTION
    # ========================================================

    def predict_risk(self):

        # ----------------------------------------------------
        # Create DataFrame using the exact trained features
        # This also removes the sklearn feature-name warning.
        # ----------------------------------------------------

        input_data = pd.DataFrame(
            [[
                self.latitude,
                self.longitude,
                self.rainfall,
                self.temperature,
                self.humidity,
                self.river_discharge,
                self.water_level,
                self.elevation,
                self.population_density,
                self.historical_floods
            ]],
            columns=self.features
        )

        # ----------------------------------------------------
        # Random Forest prediction
        # ----------------------------------------------------

        prediction = self.model.predict(
            input_data
        )[0]

        prediction = int(prediction)

        # ----------------------------------------------------
        # Convert numerical class to risk label
        # ----------------------------------------------------

        risk = self.labels.get(
            prediction,
            "MEDIUM"
        )

        return risk


    # ========================================================
    # GENERATE FLOOD READING
    # ========================================================

    def generate_reading(self):

        # ----------------------------------------------------
        # Generate changing environmental conditions
        # ----------------------------------------------------

        self.generate_environmental_data()


        # ----------------------------------------------------
        # Move simulated time forward
        # ----------------------------------------------------

        current_time = (
            self.simulated_time
            + timedelta(minutes=1)
        )


        # ----------------------------------------------------
        # Calculate water-level change
        # ----------------------------------------------------

        level_difference = (
            self.water_level
            - self.previous_level
        )

        rate = level_difference / 1.0


        # ----------------------------------------------------
        # Negative change means water level is falling.
        # For flood monitoring, report falling/stable as 0.
        # ----------------------------------------------------

        if rate < 0:

            rate = 0


        # ====================================================
        # ML PREDICTION
        # ====================================================

        risk = self.predict_risk()


        # ====================================================
        # CONVERT ML RISK TO DASHBOARD STATUS
        # ====================================================

        if risk == "LOW":

            status = "normal"

            alert = False

            alert_type = None

            action = (
                "Log readings quietly"
            )


        elif risk == "MEDIUM":

            status = "warning"

            alert = False

            alert_type = "FLOOD_RISK"

            action = (
                "Flag potential risk to dashboard"
            )


        else:

            status = "high"

            alert = True

            alert_type = "FLOOD_RISK"

            action = (
                "Raise immediate flood warning"
            )


        # ====================================================
        # UPDATE PREVIOUS VALUES
        # ====================================================

        self.previous_level = (
            self.water_level
        )

        self.previous_time = (
            current_time
        )

        self.simulated_time = (
            current_time
        )


        # ====================================================
        # RETURN DASHBOARD DATA
        # ====================================================

        return {

            "module": "flood",

            "timestamp":
                current_time.strftime(
                    "%Y-%m-%dT%H:%M:%S"
                ),

            "status":
                status,

            "risk":
                risk,

            "value":
                round(
                    rate,
                    3
                ),

            "water_level":
                round(
                    self.water_level,
                    3
                ),

            "rate_m_per_min":
                round(
                    rate,
                    3
                ),

            "rainfall_mm":
                round(
                    self.rainfall,
                    2
                ),

            "humidity_percent":
                round(
                    self.humidity,
                    2
                ),

            "river_discharge":
                round(
                    self.river_discharge,
                    2
                ),

            "alert":
                alert,

            "alert_type":
                alert_type,

            "action":
                action,

            "ml_model":
                "Random Forest",

            "prediction_source":
                "environmental_data"
        }