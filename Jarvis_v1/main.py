from config import ASSISTANT_NAME, INPUT_MODE

from core.brain import Brain
from core.agent import Agent

from core.event_manager import EventManager
from core.scheduler import Scheduler
from core.automation_engine import AutomationEngine

from input.input_manager import InputManager
from output.output_manager import OutputManager

from core.watcher_manager import WatcherManager
from core.security_event_manager import SecurityEventManager

from tools.watchers.security_watcher import SecurityWatcher
from tools.watchers.network_watcher import NetworkWatcher
from tools.watchers.startup_watcher import StartupWatcher


from tools.monitoring.system_monitor import (
    set_event_manager,
    start_system_monitor,
    set_monitor_thresholds,
)
from tools.automation.automation_tools import (
    set_automation_engine,
)

from tools.security.security_history import (
    set_security_event_manager,
)

def main():

    print("=" * 50)
    print(f"        {ASSISTANT_NAME} v3")
    print("=" * 50)

    print(f"Input Mode : {INPUT_MODE}")
    print()

    # ======================================
    # INITIALIZE CORE
    # ======================================

    brain = Brain()

    agent = Agent(brain)

    # ======================================
    # INITIALIZE AUTONOMOUS SYSTEM
    # ======================================

    event_manager = EventManager()

    set_event_manager(event_manager)

    scheduler = Scheduler()


    automation_engine = AutomationEngine(
        event_manager=event_manager,
        brain=brain,
    )

    set_automation_engine(automation_engine)


    # ======================================
    # INPUT / OUTPUT
    # ======================================

    input_manager = InputManager(
        initial_mode=INPUT_MODE
    )

    output_manager = OutputManager()

    # =========================================================
    # SYSTEM MONITOR AUTOMATIONS
    # =========================================================

    # CPU HIGH
    automation_engine.register(
        name="CPU High Alert",
        event="CPU_HIGH",
        action=lambda event: output_manager.send(
            f"CPU usage is high: {event['data']['cpu_percent']}%.",
            input_manager.mode,
        ),
    )


    # RAM HIGH
    automation_engine.register(
        name="RAM High Alert",
        event="RAM_HIGH",
        action=lambda event: output_manager.send(
            f"RAM usage is high: {event['data']['ram_percent']}%.",
            input_manager.mode,
        ),
    )


    # DISK HIGH
    automation_engine.register(
        name="Disk High Alert",
        event="DISK_HIGH",
        action=lambda event: output_manager.send(
            f"Disk usage is high: {event['data']['disk_percent']}%.",
            input_manager.mode,
        ),
    )


    # BATTERY LOW
    automation_engine.register(
        name="Battery Low Alert",
        event="BATTERY_LOW",
        action=lambda event: output_manager.send(
            f"Battery is low: {event['data']['battery_percent']}%.",
            input_manager.mode,
        ),
    )


    # INTERNET DOWN
    automation_engine.register(
        name="Internet Down Alert",
        event="INTERNET_DOWN",
        action=lambda event: output_manager.send(
            "Internet connection appears to be unavailable.",
            input_manager.mode,
        ),
    )

    # ======================================
    # START SYSTEM MONITOR
    # ======================================
    
    set_monitor_thresholds(
        cpu_threshold=90,
        ram_threshold=90,
        disk_threshold=90,
        battery_threshold=20,
        interval=30,
    )
    start_system_monitor()

    # ======================================
    # START SCHEDULER
    # ======================================

    scheduler.start()

    print("⚡ Event Manager initialized.")
    print("🤖 Automation Engine initialized.")
    print("⏰ Scheduler initialized.")
    print("🖥️ System Monitor initialized.")

    # =========================================================
    # SECURITY WATCHER SYSTEM
    # =========================================================

    security_event_manager = SecurityEventManager(
        output_manager=output_manager,
    )

    set_security_event_manager(
        security_event_manager
    )

    def security_watcher_callback(watcher_name, data):

        security_event_manager.handle_event(
            watcher_name,
            data,
        )


    watcher_manager = WatcherManager()

    watcher_manager.register(
        SecurityWatcher(
            callback=security_watcher_callback
        )
    )

    watcher_manager.register(
        NetworkWatcher(
            callback=security_watcher_callback
        )
    )

    watcher_manager.register(
        StartupWatcher(
            callback=security_watcher_callback
        )
    )

    # ======================================
    # START SECURITY WATCHERS
    # ======================================

    watcher_manager.start(
        "security_watcher"
    )

    watcher_manager.start(
        "network_watcher"
    )

    watcher_manager.start(
        "startup_watcher"
    )

    print("🛡️ Security Watcher System initialized.")

    # ======================================
    # MAIN LOOP
    # ======================================

    try:

        while True:

            try:

                # ==================================
                # GET USER INPUT
                # ==================================

                user_input = input_manager.get_input()

                if not user_input:
                    continue

                # ==================================
                # EXIT
                # ==================================

                if user_input == "__EXIT__":

                    output_manager.send(
                        "Goodbye Tarek.",
                        input_manager.mode
                    )

                    break

                # ==================================
                # MODE SWITCH
                # ==================================

                if user_input == "__VOICE_MODE__":

                    output_manager.send(
                        "Voice mode activated.",
                        input_manager.mode
                    )

                    continue

                if user_input == "__TEXT_MODE__":

                    output_manager.send(
                        "Text mode activated.",
                        input_manager.mode
                    )

                    continue

                # ==================================
                # VOICE STANDBY
                # ==================================

                if user_input == "__STANDBY__":

                    output_manager.send(
                        "Okay. Going to standby.",
                        input_manager.mode
                    )

                    continue

                # ==================================
                # NORMAL EXIT COMMANDS
                # ==================================

                if user_input.lower() in [
                    "exit",
                    "quit",
                    "bye",
                    "goodbye",
                ]:

                    output_manager.send(
                        "Goodbye Tarek.",
                        input_manager.mode
                    )

                    break

                # ==================================
                # SEND TO AGENT
                # ==================================

                response = agent.run(user_input)

                # ==================================
                # SEND RESPONSE
                # ==================================

                if response:

                    output_manager.send(
                        response,
                        input_manager.mode
                    )

            # ======================================
            # CTRL + C
            # ======================================

            except KeyboardInterrupt:

                print()

                output_manager.send(
                    "JARVIS shutting down.",
                    input_manager.mode
                )

                break

            # ======================================
            # LOOP ERROR
            # ======================================

            except Exception as e:

                print(
                    f"❌ Error: {e}"
                )

    finally:

        # ======================================
        # STOP SCHEDULER
        # ======================================

        try:
            scheduler.stop()
        except Exception:
            pass

        # ======================================
        # STOP INPUT
        # ======================================

        try:
            input_manager.stop()
        except Exception:
            pass

        print("🤖 JARVIS automation system stopped.")


if __name__ == "__main__":
    main()