class SecurityAlertPolicy:

    LEVELS = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }

    ACTIONS = {
        "LOW": "LOG_ONLY",
        "MEDIUM": "NOTIFY",
        "HIGH": "ALERT",
        "CRITICAL": "IMMEDIATE_ALERT",
    }

    def evaluate(self, event):

        if not isinstance(event, dict):
            return {
                "success": False,
                "error": "Invalid security event.",
            }

        risk = str(
            event.get(
                "risk",
                "UNKNOWN",
            )
        ).upper()

        if risk not in self.LEVELS:

            return {
                "success": False,
                "error": f"Unknown risk level: {risk}",
            }

        action = self.ACTIONS[risk]

        return {
            "success": True,
            "risk": risk,
            "level": self.LEVELS[risk],
            "action": action,
            "notify": risk != "LOW",
        }