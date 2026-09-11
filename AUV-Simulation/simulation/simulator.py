import json
import urllib.request
import urllib.error
import os
import cv2

from navigation.navigation import Navigation
from sar.sar import SAR
from flood.flood import Flood


class Simulator:

    def __init__(self, config):

        self.navigation = Navigation(
            config["auv"]["start_position"],
            config["auv"]["speed_knots"],
            config["waypoints"]
        )

        self.sar = SAR(
            config["sar"]["detection_radius_m"],
            config["sar"]["target"]
        )

        self.flood = Flood()

        self.pollution_api_url = (
            "http://127.0.0.1:5001/api/pollution"
        )

        # Simulated camera frames
        self.camera_folder = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "camera_frames"
        )

        self.camera_frames = []

        if os.path.exists(self.camera_folder):

            for filename in sorted(
                os.listdir(self.camera_folder)
            ):

                if filename.lower().endswith(
                    (".jpg", ".jpeg", ".png")
                ):

                    self.camera_frames.append(
                        os.path.join(
                            self.camera_folder,
                            filename
                        )
                    )

        self.camera_index = 0

        print(
            "Simulated camera frames:",
            len(self.camera_frames)
        )

    def get_camera_frame(self):

        if not self.camera_frames:
            return None

        frame_path = self.camera_frames[
            self.camera_index
        ]

        frame = cv2.imread(frame_path)

        self.camera_index += 1

        if self.camera_index >= len(
            self.camera_frames
        ):
            self.camera_index = 0

        return frame

    def setup_sar_search(self):

        search_pattern = self.sar.generate_search_pattern(
            self.sar.target_latitude,
            self.sar.target_longitude
        )

        self.navigation.set_waypoints(
            search_pattern
        )

    def get_pollution_data(self):

        depth = self.navigation.depth_m

        url = (
            self.pollution_api_url
            + "?depth="
            + str(depth)
        )

        try:

            with urllib.request.urlopen(
                url,
                timeout=2
            ) as response:

                pollution_data = json.loads(
                    response.read().decode("utf-8")
                )

                return pollution_data

        except (
            urllib.error.URLError,
            TimeoutError
        ):

            return {
                "module": "pollution",
                "status": "unavailable",
                "alert": False,
                "value": None,
                "metrics": {},
                "metric_statuses": {},
                "error": "Pollution API is not running"
            }

    def step(self, dt_seconds):

        self.navigation.move(dt_seconds)

        auv_lat = self.navigation.latitude
        auv_lon = self.navigation.longitude

        # Get simulated camera frame
        camera_frame = self.get_camera_frame()

        # Run SAR + YOLO
        sar_data = self.sar.get_data(
            auv_lat,
            auv_lon,
            camera_frame
        )

        # Pollution
        pollution_data = self.get_pollution_data()

        # Flood
        flood_data = self.flood.generate_reading()

        return {
            "navigation": self.navigation.get_data(),
            "sar": sar_data,
            "pollution": pollution_data,
            "flood": flood_data
        }

    def run(self, steps=100, dt_seconds=10):

        self.setup_sar_search()

        for _ in range(steps):

            data = self.step(dt_seconds)

            print(
                json.dumps(
                    data,
                    indent=2
                )
            )

            if data["sar"]["detected"]:

                print("🚨 TARGET DETECTED!")