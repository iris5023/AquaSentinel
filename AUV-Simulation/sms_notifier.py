import os
from twilio.rest import Client


class SMSNotifier:

    def __init__(self):

        self.account_sid = os.getenv(
            "TWILIO_ACCOUNT_SID"
        )

        self.auth_token = os.getenv(
            "TWILIO_AUTH_TOKEN"
        )

        self.from_number = os.getenv(
            "TWILIO_FROM_NUMBER"
        )

        self.to_number = os.getenv(
            "AUTHORITY_PHONE_NUMBER"
        )

        self.enabled = all([
            self.account_sid,
            self.auth_token,
            self.from_number,
            self.to_number
        ])

        if self.enabled:
            self.client = Client(
                self.account_sid,
                self.auth_token
            )
            print("SMS service enabled")
        else:
            self.client = None
            print("SMS service disabled - credentials not configured")

    def send_alert(self, alert):

        if not self.enabled:
            return {
                "sms_status": "NOT_CONFIGURED",
                "message_sid": None
            }

        location = alert.get("location", {})

        latitude = location.get(
            "latitude",
            "--"
        )

        longitude = location.get(
            "longitude",
            "--"
        )

        message_body = (
            "AquaSentinel ALERT\n\n"
            f"Alert Type: {alert.get('type', '--')}\n"
            f"Risk: {alert.get('risk', '--')}\n"
            f"Location: {latitude}, {longitude}\n\n"
            f"Action: {alert.get('action', '--')}"
        )

        try:

            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=self.to_number
            )

            print(
                "SMS sent:",
                message.sid
            )

            return {
                "sms_status": "SENT",
                "message_sid": message.sid
            }

        except Exception as error:

            print(
                "SMS failed:",
                error
            )

            return {
                "sms_status": "FAILED",
                "message_sid": None
            }