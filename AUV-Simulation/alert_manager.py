from alerts.sms_notifier import SMSNotifier


class AlertManager:

    def __init__(self):

        self.sms_notifier = SMSNotifier()

        self.previous_states = {
            "SAR": False,
            "FLOOD": False,
            "POLLUTION": False
        }

        self.latest_alert = {
            "status": "NO ACTIVE ALERT",
            "type": None,
            "risk": None,
            "location": None,
            "action": None,
            "sms_status": "NOT_SENT",
            "timestamp": None
        }

    def process(
        self,
        sar_data,
        pollution_data,
        flood_data,
        latitude,
        longitude
    ):

        # -------------------------
        # SAR
        # -------------------------

        sar_alert = (
            sar_data.get("detected", False)
            or sar_data.get("survivor_detected", False)
        )

        if sar_alert:

            alert = {
                "status": "ALERT SENT",
                "type": "SAR",
                "risk": "EMERGENCY",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "action": "Initiate rescue response"
            }

            if not self.previous_states["SAR"]:

                sms_result = self.sms_notifier.send_alert(
                    alert
                )

                alert.update(sms_result)

            else:

                alert["sms_status"] = "ALREADY_SENT"
                alert["message_sid"] = None

            self.previous_states["SAR"] = True
            self.latest_alert = alert

            return alert

        self.previous_states["SAR"] = False

        # -------------------------
        # FLOOD
        # -------------------------

        flood_risk = flood_data.get(
            "risk",
            "LOW"
        )

        flood_alert = (
            flood_risk == "HIGH"
        )

        if flood_alert:

            alert = {
                "status": "ALERT SENT",
                "type": "FLOOD_RISK",
                "risk": "HIGH",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "action": flood_data.get(
                    "action",
                    "Raise immediate flood warning"
                )
            }

            if not self.previous_states["FLOOD"]:

                sms_result = self.sms_notifier.send_alert(
                    alert
                )

                alert.update(sms_result)

            else:

                alert["sms_status"] = "ALREADY_SENT"
                alert["message_sid"] = None

            self.previous_states["FLOOD"] = True
            self.latest_alert = alert

            return alert

        self.previous_states["FLOOD"] = False

        # -------------------------
        # POLLUTION
        # -------------------------

        pollution_alert = pollution_data.get(
            "alert",
            False
        )

        if pollution_alert:

            alert = {
                "status": "ALERT SENT",
                "type": "POLLUTION",
                "risk": pollution_data.get(
                    "status",
                    "CRITICAL"
                ),
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "action": "Initiate water-quality response"
            }

            if not self.previous_states["POLLUTION"]:

                sms_result = self.sms_notifier.send_alert(
                    alert
                )

                alert.update(sms_result)

            else:

                alert["sms_status"] = "ALREADY_SENT"
                alert["message_sid"] = None

            self.previous_states["POLLUTION"] = True
            self.latest_alert = alert

            return alert

        self.previous_states["POLLUTION"] = False

        # -------------------------
        # NO ACTIVE ALERT
        # -------------------------

        self.latest_alert = {
            "status": "NO ACTIVE ALERT",
            "type": None,
            "risk": None,
            "location": None,
            "action": None,
            "sms_status": "NOT_SENT",
            "message_sid": None
        }

        return self.latest_alert