import math


class Navigation:
    def __init__(self, start_position, speed_knots, waypoints):
        self.latitude = start_position["latitude"]
        self.longitude = start_position["longitude"]
        self.depth_m = start_position["depth_m"]

        self.speed_knots = speed_knots
        self.waypoints = waypoints
        self.current_waypoint = 0

        # Store the current AUV heading
        self.heading_deg = start_position.get("heading_deg", 0)

    def calculate_distance(self, target_lat, target_lon):
        R = 6371000

        lat1 = math.radians(self.latitude)
        lat2 = math.radians(target_lat)

        delta_lat = math.radians(target_lat - self.latitude)
        delta_lon = math.radians(target_lon - self.longitude)

        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1)
            * math.cos(lat2)
            * math.sin(delta_lon / 2) ** 2
        )

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def calculate_bearing(self, target_lat, target_lon):
        lat1 = math.radians(self.latitude)
        lat2 = math.radians(target_lat)

        delta_lon = math.radians(
            target_lon - self.longitude
        )

        x = (
            math.sin(delta_lon)
            * math.cos(lat2)
        )

        y = (
            math.cos(lat1)
            * math.sin(lat2)
            - math.sin(lat1)
            * math.cos(lat2)
            * math.cos(delta_lon)
        )

        bearing = math.degrees(
            math.atan2(x, y)
        )

        return (bearing + 360) % 360

    def get_current_waypoint(self):
        if self.current_waypoint >= len(self.waypoints):
            return None

        return self.waypoints[
            self.current_waypoint
        ]

    def move(self, dt_seconds):

        waypoint = self.get_current_waypoint()

        if waypoint is None:
            return

        distance = self.calculate_distance(
            waypoint["latitude"],
            waypoint["longitude"]
        )

        # Calculate direction to waypoint
        bearing = self.calculate_bearing(
            waypoint["latitude"],
            waypoint["longitude"]
        )

        # Store heading
        self.heading_deg = bearing

        speed_mps = (
            self.speed_knots *
            0.514444
        )

        travel_distance = (
            speed_mps *
            dt_seconds
        )

        if travel_distance >= distance:

            self.latitude = waypoint["latitude"]

            self.longitude = waypoint["longitude"]

            self.current_waypoint += 1

            return

        R = 6371000

        bearing_rad = math.radians(
            bearing
        )

        lat1 = math.radians(
            self.latitude
        )

        lon1 = math.radians(
            self.longitude
        )

        angular_distance = (
            travel_distance / R
        )

        lat2 = math.asin(

            math.sin(lat1)
            * math.cos(angular_distance)

            +

            math.cos(lat1)
            * math.sin(angular_distance)
            * math.cos(bearing_rad)

        )

        lon2 = lon1 + math.atan2(

            math.sin(bearing_rad)
            * math.sin(angular_distance)
            * math.cos(lat1),

            math.cos(angular_distance)
            - math.sin(lat1)
            * math.sin(lat2)

        )

        self.latitude = math.degrees(
            lat2
        )

        self.longitude = math.degrees(
            lon2
        )

    def get_status(self):

        waypoint = self.get_current_waypoint()

        if waypoint is None:
            return "mission_complete"

        distance = self.calculate_distance(
            waypoint["latitude"],
            waypoint["longitude"]
        )

        if distance <= 5:
            return "waypoint_reached"

        return "moving"

    def get_data(self):

        waypoint = self.get_current_waypoint()

        return {
            "module": "navigation",

            "status": self.get_status(),

            "position": {
                "latitude": round(
                    self.latitude,
                    6
                ),

                "longitude": round(
                    self.longitude,
                    6
                ),

                "depth_m": self.depth_m
            },

            "speed_knots": self.speed_knots,

            "heading_deg": round(
                self.heading_deg,
                2
            ),

            "current_waypoint":
                waypoint["id"]
                if waypoint
                else None
        }

    def set_waypoints(self, waypoints):

        self.waypoints = waypoints

        self.current_waypoint = 0