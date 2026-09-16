# tools/automation/automation_tools.py

_automation_engine = None


def set_automation_engine(automation_engine):
    global _automation_engine
    _automation_engine = automation_engine

    return {
        "success": True,
        "message": "Automation tools connected.",
    }


def list_automations():
    if _automation_engine is None:
        return {
            "success": False,
            "error": "Automation Engine is not connected.",
        }

    automations = _automation_engine.get_automations()

    result = []

    for automation in automations:

        condition = automation.get("condition")

        result.append({
            "name": automation["name"],
            "event": automation["event"],
            "enabled": automation["enabled"],
            "condition": condition,
        })

    return {
        "success": True,
        "automations": result,
        "count": len(result),
    }


def enable_automation(name: str):
    if _automation_engine is None:
        return {
            "success": False,
            "error": "Automation Engine is not connected.",
        }

    name = name.strip()

    for automation in _automation_engine.get_automations():
        if automation["name"].lower() == name.lower():
            _automation_engine.enable(name)

            return {
                "success": True,
                "message": f"Automation '{automation['name']}' enabled.",
                "name": automation["name"],
                "enabled": True,
            }

    return {
        "success": False,
        "error": f"Automation '{name}' was not found.",
    }


def disable_automation(name: str):

    if _automation_engine is None:
        return {
            "success": False,
            "error": "Automation Engine is not connected.",
        }

    name = str(name).strip()

    for automation in _automation_engine.get_automations():

        if automation["name"].lower() == name.lower():

            actual_name = automation["name"]

            disabled = _automation_engine.disable(
                actual_name
            )

            if not disabled:
                return {
                    "success": False,
                    "error": (
                        f"Failed to disable "
                        f"automation '{actual_name}'."
                    ),
                }

            # Read the actual state from the engine
            current_enabled = automation.get(
                "enabled",
                False,
            )

            return {
                "success": True,
                "message": (
                    f"Automation '{actual_name}' "
                    f"disabled."
                ),
                "name": actual_name,
                "enabled": current_enabled,
                "event": automation.get(
                    "event"
                ),
            }

    return {
        "success": False,
        "error": (
            f"Automation '{name}' "
            f"was not found."
        ),
    }


def automation_status(name: str):
    if _automation_engine is None:
        return {
            "success": False,
            "error": "Automation Engine is not connected.",
        }

    name = name.strip()

    for automation in _automation_engine.get_automations():
        if automation["name"].lower() == name.lower():
            return {
                "success": True,
                "name": automation["name"],
                "event": automation["event"],
                "enabled": automation["enabled"],
            }

    return {
        "success": False,
        "error": f"Automation '{name}' was not found.",
    }

def create_automation(
    name: str,
    event: str,
    action: str,
    condition=None,
):
    if _automation_engine is None:
        return {
            "success": False,
            "error": "Automation Engine is not connected.",
        }

    name = name.strip()
    event = event.strip().upper()
    action = action.strip()

    if not name:
        return {
            "success": False,
            "error": "Automation name is required.",
        }

    if not event:
        return {
            "success": False,
            "error": "Automation event is required.",
        }

    if not action:
        return {
            "success": False,
            "error": "Automation action is required.",
        }

    # =========================================================
    # NORMALIZE CONDITION
    # =========================================================

    if isinstance(condition, dict):

        metric = condition.get("metric")
        operator = condition.get("operator")
        value = condition.get("value")

        if metric:
            metric = str(metric).strip().lower()

        if operator:
            operator = str(operator).strip()

        try:
            value = float(value)
        except (TypeError, ValueError):
            return {
                "success": False,
                "error": "Automation condition value must be numeric.",
            }

        allowed_metrics = {
            "cpu",
            "ram",
            "disk",
            "battery",
        }

        allowed_operators = {
            ">",
            ">=",
            "<",
            "<=",
            "==",
            "!=",
        }

        if metric not in allowed_metrics:
            return {
                "success": False,
                "error": (
                    "Invalid condition metric. "
                    "Supported metrics: cpu, ram, disk, battery."
                ),
            }

        if operator not in allowed_operators:
            return {
                "success": False,
                "error": (
                    "Invalid condition operator. "
                    "Supported operators: >, >=, <, <=, ==, !=."
                ),
            }

        condition = {
            "metric": metric,
            "operator": operator,
            "value": value,
        }

    # =========================================================
    # CHECK DUPLICATE
    # =========================================================

    for automation in _automation_engine.get_automations():

        if automation["name"].lower() == name.lower():

            return {
                "success": False,
                "error": (
                    f"Automation '{name}' already exists."
                ),
            }

    # =========================================================
    # REGISTER
    # =========================================================

    automation = _automation_engine.register(
        name=name,
        event=event,
        action=action,
        condition=condition,
        enabled=True,
    )

    return {
        "success": True,
        "message": (
            f"Automation '{name}' created successfully."
        ),
        "name": automation["name"],
        "event": automation["event"],
        "action": automation["action"],
        "condition": automation["condition"],
        "enabled": automation["enabled"],
    }

def stop_all_automations():

    if _automation_engine is None:
        return {
            "success": False,
            "error": "Automation Engine is not connected.",
        }

    automations = _automation_engine.get_automations()

    if not automations:
        return {
            "success": True,
            "message": "There are no automations configured.",
            "count": 0,
            "disabled": [],
        }

    disabled = []

    for automation in automations:

        name = automation.get("name")

        if not name:
            continue

        if automation.get("enabled"):

            result = _automation_engine.disable(
                name
            )

            if result:
                disabled.append(name)

    return {
        "success": True,
        "message": (
            f"{len(disabled)} automation"
            f"{'s' if len(disabled) != 1 else ''} "
            "disabled."
        ),
        "count": len(disabled),
        "disabled": disabled,
    }

def delete_automation(name: str):
    if _automation_engine is None:
        return {
            "success": False,
            "error": "Automation Engine is not connected.",
        }

    name = str(name).strip()

    if not name:
        return {
            "success": False,
            "error": "Automation name is required.",
        }

    for automation in _automation_engine.get_automations():

        if automation["name"].lower() == name.lower():

            actual_name = automation["name"]

            deleted = _automation_engine.delete(
                actual_name
            )

            if deleted is None:
                return {
                    "success": False,
                    "error": (
                        f"Failed to delete "
                        f"automation '{actual_name}'."
                    ),
                }

            return {
                "success": True,
                "message": (
                    f"Automation '{actual_name}' "
                    f"deleted successfully."
                ),
                "name": actual_name,
                "event": deleted.get("event"),
                "enabled": deleted.get("enabled"),
            }

    return {
        "success": False,
        "error": (
            f"Automation '{name}' "
            f"was not found."
        ),
    }