_security_event_manager = None


def set_security_event_manager(manager):
    global _security_event_manager
    _security_event_manager = manager


def get_recent_security_events(limit=10):

    if _security_event_manager is None:
        return {
            "success": False,
            "error": "Security event manager is not initialized.",
        }

    return _security_event_manager.get_recent_events(limit)

def get_latest_security_event():

    if _security_event_manager is None:
        return {
            "success": False,
            "error": "Security event manager is not initialized.",
        }

    events = _security_event_manager.get_events(limit=1)

    if not events:
        return {
            "success": True,
            "event": None,
        }

    return {
        "success": True,
        "event": events[0],
    }

def get_security_events(
    risk=None,
    source=None,
    event_type=None,
    limit=20,
):

    if _security_event_manager is None:
        return {
            "success": False,
            "error": "Security event manager is not initialized.",
        }

    events = _security_event_manager.get_events(
        limit=1000
    )

    filtered_events = []

    risk = (
        str(risk).strip().upper()
        if risk
        else None
    )

    source = (
        str(source).strip().lower()
        if source
        else None
    )

    event_type = (
        str(event_type).strip().lower()
        if event_type
        else None
    )

    for event in events:

        event_risk = str(
            event.get("risk", "")
        ).upper()

        event_source = str(
            event.get("source", "")
        ).lower()

        event_name = str(
            event.get("type", "")
        ).lower()

        if risk and event_risk != risk:
            continue

        if source and source not in event_source:
            continue

        if event_type and event_type not in event_name:
            continue

        filtered_events.append(event)

    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 20

    if limit <= 0:
        limit = 20

    filtered_events = filtered_events[-limit:]

    return {
        "success": True,
        "count": len(filtered_events),
        "events": filtered_events,
        "filters": {
            "risk": risk,
            "source": source,
            "event_type": event_type,
        },
    }

def get_security_summary():

    if _security_event_manager is None:
        return {
            "success": False,
            "error": "Security event manager is not initialized.",
        }

    events = _security_event_manager.get_events(
        limit=1000
    )

    risk_counts = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "CRITICAL": 0,
    }

    source_counts = {}

    for event in events:

        risk = str(
            event.get("risk", "UNKNOWN")
        ).upper()

        if risk in risk_counts:
            risk_counts[risk] += 1

        source = event.get(
            "source",
            "unknown",
        )

        source_counts[source] = (
            source_counts.get(source, 0) + 1
        )

    return {
        "success": True,
        "total_events": len(events),
        "risk_counts": risk_counts,
        "source_counts": source_counts,
    }