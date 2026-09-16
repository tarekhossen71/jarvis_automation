from core.security_alert_policy import SecurityAlertPolicy


class SecurityEventManager:

    def __init__(
        self,
        callback=None,
        alert_callback=None,
        output_manager=None,
    ):
        self.callback = callback
        self.alert_callback = alert_callback
        self.output_manager = output_manager

        self.policy = SecurityAlertPolicy()

        self.event_count = 0
        self.events = []

    # =========================================================
    # RECEIVE EVENT
    # =========================================================

    def handle_event(self, watcher_name, data):

        if not data:
            return {
                "success": False,
                "error": "Empty security event data.",
            }

        normalized_events = self._normalize_events(
            watcher_name,
            data,
        )

        processed_events = []

        for event in normalized_events:

            policy_result = self.policy.evaluate(event)

            event["policy"] = policy_result

            self.events.append(event)
            self.event_count += 1

            processed_events.append(event)

            if self.callback:
                self.callback(event)

            if (
                policy_result.get("success")
                and policy_result.get("notify")
            ):
                self._send_security_alert(
                    event,
                    policy_result,
                )

        return {
            "success": True,
            "count": len(processed_events),
            "events": processed_events,
        }

    # =========================================================
    # SECURITY ALERT
    # =========================================================

    def _send_security_alert(self, event, policy):

        risk = policy.get("risk", "UNKNOWN")
        action = policy.get("action", "UNKNOWN")
        source = event.get("source", "unknown")
        event_type = event.get(
            "type",
            "SECURITY_EVENT",
        )
        reason = event.get("reason", "")

        message = (
            f"Security alert. "
            f"Risk level {risk}. "
            f"Source {source}. "
            f"Event {event_type}. "
            f"{reason}"
        )

        if self.output_manager:
            self.output_manager.send(message)

        if self.alert_callback:
            self.alert_callback(
                event,
                policy,
            )

    # =========================================================
    # NORMALIZE EVENTS
    # =========================================================

    def _normalize_events(self, watcher_name, data):

        events = data.get("events")

        if not events:
            events = [data]

        normalized = []

        for event in events:

            if not isinstance(event, dict):
                continue

            normalized_event = {
                "source": watcher_name,
                "type": event.get(
                    "type",
                    "SECURITY_EVENT",
                ),
                "risk": event.get(
                    "risk",
                    "UNKNOWN",
                ),
                "reason": event.get(
                    "reason",
                    "",
                ),
                "data": event,
            }

            normalized.append(normalized_event)

        return normalized

    # =========================================================
    # RECENT EVENTS
    # =========================================================

    def get_events(self, limit=20):
        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 20

        if limit <= 0:
            return []

        return self.events[-limit:]


    def get_recent_events(self, limit=10):
        events = self.get_events(limit)

        result = []

        for event in events:
            result.append({
                "source": event.get("source"),
                "type": event.get("type"),
                "risk": event.get("risk"),
                "reason": event.get("reason"),
                "policy": event.get("policy"),
                "data": event.get("data"),
            })

        return {
            "success": True,
            "count": len(result),
            "events": result,
        }

    # =========================================================
    # STATUS
    # =========================================================

    def status(self):

        return {
            "event_count": self.event_count,
            "stored_events": len(self.events),
        }

    # =========================================================
    # CLEAR
    # =========================================================

    def clear(self):

        self.events.clear()
        self.event_count = 0

        return {
            "success": True,
            "message": "Security events cleared.",
        }