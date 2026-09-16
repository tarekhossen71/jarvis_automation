from core.security_alert_policy import SecurityAlertPolicy


policy = SecurityAlertPolicy()


test_events = [

    {
        "source": "security_watcher",
        "type": "SECURITY_PROCESS_STARTED",
        "risk": "LOW",
        "reason": "Known Windows system executable.",
    },

    {
        "source": "startup_watcher",
        "type": "SECURITY_STARTUP_ITEM_ADDED",
        "risk": "MEDIUM",
        "reason": "Startup item type is not recognized.",
    },

    {
        "source": "security_watcher",
        "type": "SECURITY_PROCESS_STARTED",
        "risk": "HIGH",
        "reason": "Suspicious executable location.",
    },

    {
        "source": "network_watcher",
        "type": "SECURITY_NETWORK_CONNECTION",
        "risk": "CRITICAL",
        "reason": "Critical security event.",
    },

]


for event in test_events:

    result = policy.evaluate(event)

    print("\nSecurity Event:")
    print(event)

    print("Policy Result:")
    print(result)