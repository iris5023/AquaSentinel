import math
import os

from ultralytics import YOLO


class SAR:

    def __init__(self, detection_radius_m, target):

        self.detection_radius_m = detection_radius_m

        self.target_latitude = target["latitude"]
        self.target_longitude = target["longitude"]

        # Remember if target has ever been detected
        self.target_detected = False
        self.detection_distance = None

        # =========================
        # YOLO MODEL
        # =========================

        model_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "models",
            "best.pt"
        )

        self.model = YOLO(model_path)

        # Classes from our trained model
        self.class_names = self.model.names

        print("SAR YOLO model loaded")
        print("Classes:", self.class_names)

    # =========================
    # CALCULATE DISTANCE
    # =========================

    def calculate_distance(self, auv_lat, auv_lon):

        R = 6371000

        lat1 = math.radians(auv_lat)
        lat2 = math.radians(self.target_latitude)

        delta_lat = math.radians(
            self.target_latitude - auv_lat
        )

        delta_lon = math.radians(
            self.target_longitude - auv_lon
        )

        a = (
            math.sin(delta_lat / 2) ** 2
            +
            math.cos(lat1)
            * math.cos(lat2)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )

        return R * c

    # =========================
    # YOLO DETECTION
    # =========================

    def detect_frame(self, frame):

        results = self.model.predict(
            source=frame,
            conf=0.35,
            verbose=False
        )

        detections = []

        for result in results:

            for box in result.boxes:

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                # YOLO bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()

                class_name = self.class_names[class_id]

                detections.append({
                    "class": class_name,

                    "confidence": round(
                        confidence,
                        2
                    ),

                    "bbox": {
                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2)
                    }
                })

        # Check for swimmer
        swimmer_detected = any(
            d["class"] == "swimmer"
            for d in detections
        )

        # Check for boat
        boat_detected = any(
            d["class"] == "boat"
            for d in detections
        )

        return {
            "detections": detections,
            "swimmer_detected": swimmer_detected,
            "boat_detected": boat_detected
        }

    # =========================
    # DISTANCE TARGET DETECTION
    # =========================

    def detect_target(self, auv_lat, auv_lon):

        distance = self.calculate_distance(
            auv_lat,
            auv_lon
        )

        if distance <= self.detection_radius_m:

            self.target_detected = True
            self.detection_distance = round(
                distance,
                2
            )

        if self.target_detected:

            return True, self.detection_distance

        return False, round(distance, 2)

    # =========================
    # SAR DATA
    # =========================

    def get_data(
        self,
        auv_lat,
        auv_lon,
        frame=None
    ):

        detected, distance = self.detect_target(
            auv_lat,
            auv_lon
        )

        # Default YOLO results
        yolo_data = {
            "detections": [],
            "swimmer_detected": False,
            "boat_detected": False
        }

        # Run YOLO only when a camera frame
        # is available
        if frame is not None:

            yolo_data = self.detect_frame(
                frame
            )

        # Swimmer = SAR survivor
        if yolo_data["swimmer_detected"]:

            detected = True
            self.target_detected = True

        # =========================
        # FINAL SAR OUTPUT
        # =========================

        if yolo_data["swimmer_detected"]:

            status = "survivor_detected"
            alert = True
            alert_type = "SURVIVOR_DETECTED"

        elif yolo_data["boat_detected"]:

            status = "boat_detected"
            alert = True
            alert_type = "BOAT_DETECTED"

        elif detected:

            status = "target_detected"
            alert = True
            alert_type = "SAR_TARGET"

        else:

            status = "searching"
            alert = False
            alert_type = None

        return {

            "module": "sar",

            "status": status,

            "target": {
                "latitude":
                    self.target_latitude,

                "longitude":
                    self.target_longitude
            },

            "distance_to_target_m":
                distance,

            "detection_radius_m":
                self.detection_radius_m,

            "detected":
                detected,

            "alert":
                alert,

            "alert_type":
                alert_type,

            "yolo": yolo_data
        }

    # =========================
    # SAR SEARCH PATTERN
    # =========================

    def generate_search_pattern(
        self,
        center_lat,
        center_lon
    ):

        offset = 0.001

        pattern = [

            {
                "id": "SAR1",
                "latitude":
                    center_lat - offset,
                "longitude":
                    center_lon - offset
            },

            {
                "id": "SAR2",
                "latitude":
                    center_lat - offset,
                "longitude":
                    center_lon + offset
            },

            {
                "id": "SAR3",
                "latitude":
                    center_lat,
                "longitude":
                    center_lon
            },

            {
                "id": "SAR4",
                "latitude":
                    center_lat + offset,
                "longitude":
                    center_lon
            },

            {
                "id": "SAR5",
                "latitude":
                    center_lat + offset,
                "longitude":
                    center_lon - offset
            }
        ]

        return pattern