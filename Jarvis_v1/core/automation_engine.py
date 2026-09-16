# automation_engine.py
from tools.notifications.notification_manager import show_notification
class AutomationEngine:

    def __init__(self, event_manager=None, brain=None,output_manager=None):

        self.event_manager = event_manager
        self.brain = brain
        self.output_manager = output_manager

        self.automations = []

        # Events already connected to this automation engine
        self.registered_events = set()

    # =========================================================
    # REGISTER AUTOMATION
    # =========================================================

    def register(
        self,
        name,
        event,
        action,
        condition=None,
        enabled=True,
    ):

        automation = {
            "name": name,
            "event": event,
            "action": action,
            "condition": condition,
            "enabled": enabled,
        }

        self.automations.append(automation)

        # Register this AutomationEngine as a listener
        # only once for each event.
        if (
            self.event_manager
            and event not in self.registered_events
        ):

            self.event_manager.on(
                event,
                self._handle_event,
            )

            self.registered_events.add(event)

        print(
            f"🤖 Automation registered: {name}"
        )

        return automation

    # =========================================================
    # HANDLE EVENT
    # =========================================================

    def _handle_event(self, event):

        event_name = event["name"]

        for automation in self.automations:

            if not automation["enabled"]:
                continue

            if automation["event"] != event_name:
                continue

            try:

                if not self._check_condition(
                    automation,
                    event,
                ):
                    continue

                self._execute(
                    automation,
                    event,
                )

            except Exception as e:

                print(
                    f"❌ Automation error "
                    f"[{automation['name']}]: {e}"
                )

    # =========================================================
    # CONDITION
    # =========================================================

    def _check_condition(
        self,
        automation,
        event,
    ):

        condition = automation.get("condition")

        # No condition = always trigger
        if condition is None:
            return True

        # Callable condition
        if callable(condition):
            return bool(
                condition(event)
            )

        # Dictionary condition
        if isinstance(condition, dict):
            return self._check_dict_condition(
                condition,
                event,
            )

        # Unknown condition type
        return False

    # =========================================================
    # DICTIONARY CONDITION
    # =========================================================

    def _check_dict_condition(
        self,
        condition,
        event,
    ):

        metric = condition.get("metric")
        operator = condition.get("operator")
        threshold = condition.get("value")

        if not metric or not operator:
            return False

        try:
            threshold = float(threshold)
        except (TypeError, ValueError):
            return False

        # -----------------------------------------------------
        # Get event data
        # -----------------------------------------------------

        data = event.get("data")

        if not isinstance(data, dict):
            return False

        value = data.get(metric)

        if value is None:
            return False

        try:
            value = float(value)
        except (TypeError, ValueError):
            return False

        # -----------------------------------------------------
        # Compare
        # -----------------------------------------------------

        if operator == ">":
            return value > threshold

        if operator == ">=":
            return value >= threshold

        if operator == "<":
            return value < threshold

        if operator == "<=":
            return value <= threshold

        if operator == "==":
            return value == threshold

        if operator == "!=":
            return value != threshold

        return False

    # =========================================================
    # EXECUTE
    # =========================================================

    def _execute(self, automation, event):

        action = automation["action"]

        print(
            f"🤖 Automation executing: "
            f"{automation['name']}"
        )

        # =========================================================
        # CALLABLE ACTION
        # =========================================================

        if callable(action):
            return action(event)

        # =========================================================
        # STRING ACTION
        # =========================================================

        if isinstance(action, str):

            # Event data
            data = event.get("data")

            if not isinstance(data, dict):
                data = {}

            # -----------------------------------------------------
            # Replace supported placeholders
            # -----------------------------------------------------

            message = action

            for key, value in data.items():

                placeholder = "{" + str(key) + "}"

                if placeholder in message:
                    message = message.replace(
                        placeholder,
                        str(value),
                    )

            # =====================================================
            # REAL ACTION HANDLERS
            # =====================================================

            if action == "show_notification":

                title = (
                    data.get(
                        "title",
                        "JARVIS Automation",
                    )
                )

                notification_message = (
                    data.get(
                        "message",
                        f"Automation triggered: "
                        f"{automation['name']}",
                    )
                )

                result = show_notification(
                    title,
                    notification_message,
                )

                print(
                    f"🔔 JARVIS Desktop Notification: "
                    f"{notification_message}"
                )

                return {
                    "success": True,
                    "action": action,
                    "automation": automation["name"],
                    "event": event["name"],
                    "result": result,
                    "data": data,
                }

            # =====================================================
            # UNKNOWN STRING ACTION
            # =====================================================

            print(
                f"⚠️ Unknown automation action: "
                f"{action}"
            )

            return {
                "success": False,
                "error": f"Unknown automation action: {action}",
                "automation": automation["name"],
            }

        # =========================================================
        # UNKNOWN ACTION
        # =========================================================

        print(
            f"⚠️ No execution handler "
            f"for action: {action}"
        )

    # =========================================================
    # ENABLE
    # =========================================================

    def enable(self, name):

        for automation in self.automations:

            if automation["name"] == name:

                automation["enabled"] = True

                return True

        return False

    # =========================================================
    # DISABLE
    # =========================================================

    def disable(self, name):

        for automation in self.automations:

            if automation["name"] == name:

                automation["enabled"] = False

                return True

        return False

    def delete(self, name):
        """
        Permanently delete an automation.
        """

        name = str(name).strip()

        for index, automation in enumerate(self.automations):

            if automation["name"].lower() == name.lower():

                deleted = self.automations.pop(index)

                return deleted

        return None
    # =========================================================
    # LIST AUTOMATIONS
    # =========================================================

    def get_automations(self):

        return self.automations