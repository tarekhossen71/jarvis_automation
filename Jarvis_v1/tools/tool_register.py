# tools/tool_register.py

from tools.system.battery import get_battery
from tools.system.screenshot import take_screenshot
from tools.system.system_info import (
    get_system_info,
    get_ram_info,
    get_cpu_info,
    get_disk_info,
)
from tools.system.volume import (
    get_volume,
    set_volume,
    increase_volume,
    decrease_volume,
    mute_volume,
    unmute_volume,
)
from tools.browser.browser import (
    open_browser,
    open_url,
    open_website,
    google_search,
    youtube_search,
)
from tools.browser.youtube_play import play_youtube

from tools.files.file_manager import (
    list_folder,
    search_files,
    get_file_info,
    create_file,
    create_folder,
    rename_file,
    copy_file,
    move_file,
    open_file,
    open_folder,
    get_recent_files,
    delete_file,
    confirm_delete,
    cancel_delete,
    empty_recycle_bin,
    confirm_empty_recycle_bin,
    cancel_recycle_bin,
)
from tools.apps.app_manager import (
    open_application,
    is_application_running,
    get_running_applications,
    # close_application,
    # force_close_application,
)

from tools.clipboard.clipboard_manager import (
    read_clipboard,
    copy_to_clipboard,
    clear_clipboard,
    get_clipboard_history,
    search_clipboard_history,
    delete_clipboard_history,
    start_clipboard_monitor,
    stop_clipboard_monitor,
    clipboard_monitor_status,
)

from tools.internet.speed_test import (
    check_internet_connection,
    get_internet_info,
    run_internet_speed_test,
    test_download_speed,
    test_upload_speed,
    test_ping,
)

from tools.reminders.reminder_manager import (
    create_reminder,
    create_relative_reminder,
    list_reminders,
    find_reminder,
    cancel_reminder,
    delete_reminder,
    complete_reminder,
    get_due_reminders,
    start_reminder_monitor,
    stop_reminder_monitor,
    reminder_monitor_status,
)

from tools.system.window_manager import (
    get_open_windows,
    minimize_window,
    maximize_window,
    restore_window,
    focus_window,
    show_desktop,
)

from tools.system.keyboard_manager import (
    type_text,
    press_key,
    hotkey,
)

from tools.system.power_manager import (
    lock_pc,
    sleep_pc,
    restart_pc,
    shutdown_pc,
)

from tools.notifications.notification_manager import (
    show_notification,
    set_timer,
    list_timers,
    cancel_timer,
)

from tools.monitoring.system_monitor import (
    start_system_monitor,
    stop_system_monitor,
    system_monitor_status,
    set_monitor_thresholds,
)
from tools.browser.youtube_research import youtube_research
from tools.browser.google_research import google_research
from tools.web.web_research import web_research

from tools.security.security_history import (
    get_recent_security_events,
    get_latest_security_event,
    get_security_events,
    get_security_summary,
)

from tools.applications.close_application import (
    close_application,
    force_close_application,
)

from tools.automation.automation_tools import (
    list_automations,
    enable_automation,
    disable_automation,
    automation_status,
    create_automation,
    stop_all_automations,
    delete_automation,
)




def register_all_tools(tools: object):
    """Register all system, browser, file, and application tools."""

    def get_available_features():
        """
        Return all currently registered JARVIS tools/features.
        """

        try:

            registered_tools = tools.all()

            feature_names = [
                tool["name"]
                for tool in registered_tools
            ]

            return {
                "success": True,
                "count": len(feature_names),
                "features": feature_names,
            }

        except Exception as e:

            return {
                "success": False,
                "error": str(e),
            }

    tools.register(
        name="get_available_features",
        description=(
            "Show all currently available JARVIS features and tools. "
            "Use this when the user asks what features JARVIS has, "
            "what JARVIS can do, show available features, "
            "or list all available capabilities."
        ),
        function=get_available_features,
    )

    tools.register(
        "get_system_info",
        "Get complete system information including CPU, RAM, disk, operating system, and machine information.",
        get_system_info,
    )

    tools.register(
        "get_ram_info",
        "Get current RAM usage, total RAM, used RAM, and available RAM.",
        get_ram_info,
    )

    tools.register(
        "get_cpu_info",
        "Get current CPU usage and processor information.",
        get_cpu_info,
    )

    tools.register(
        "get_disk_info",
        "Get disk usage information for a specific drive. "
        "The drive parameter can be C:\\, D:\\, E:\\ etc.",
        get_disk_info,
    )

    tools.register(
        name="get_battery",
        description=(
            "Get the current computer battery information. "
            "Use this tool when the user asks about battery "
            "percentage, charging status, or remaining battery."
        ),
        function=get_battery,
    )

    tools.register(
        name="take_screenshot",
        description=(
            "Take a screenshot of the user's current computer screen "
            "and save it as an image file. "
            "Use this tool when the user asks to take, capture, "
            "save, or make a screenshot."
        ),
        function=take_screenshot,
    )

    tools.register(
        name="get_volume",
        description=(
            "Get the current computer master volume percentage "
            "and mute status."
        ),
        function=get_volume,
    )

    tools.register(
        name="set_volume",
        description=(
            "Set the computer master volume to a specific "
            "percentage from 0 to 100."
        ),
        function=set_volume,
    )

    tools.register(
        name="increase_volume",
        description=(
            "Increase the computer master volume. "
            "Default increase is 10 percent."
        ),
        function=increase_volume,
    )

    tools.register(
        name="decrease_volume",
        description=(
            "Decrease the computer master volume. "
            "Default decrease is 10 percent."
        ),
        function=decrease_volume,
    )

    tools.register(
        name="mute_volume",
        description=(
            "Mute the computer master volume."
        ),
        function=mute_volume,
    )

    tools.register(
        name="unmute_volume",
        description=(
            "Unmute the computer master volume."
        ),
        function=unmute_volume,
    )

    
    # =====================================================
    # BROWSER TOOLS
    # =====================================================

    tools.register(
        name="open_browser",
        description=(
            "Open a specific web browser. "
            "Supported browsers are Chrome, Firefox, Edge, and Brave. "
            "If the requested browser is already running, do not launch "
            "another browser instance."
        ),
        function=open_browser,
    )

    tools.register(
        name="open_url",
        description=(
            "Open a specific URL in a web browser. "
            "Optional browser parameter can be used: "
            "chrome, firefox, edge, or brave. "
            "If the user explicitly names a browser, "
            "you MUST pass that browser. "
            "If no browser is specified, use the default browser."
        ),
        function=open_url,
    )

    tools.register(
        name="open_website",
        description=(
            "Open a known website such as Google, YouTube, Facebook, "
            "GitHub, Gmail, ChatGPT, or LinkedIn. "
            "Optional browser parameter: chrome, firefox, edge, or brave. "
            "If the user explicitly names a browser, "
            "you MUST use that browser. "
            "Do not use the system default browser when a specific "
            "browser was requested."
        ),
        function=open_website,
    )

    tools.register(
        name="google_search",
        description=(
            "Search Google for the requested query. "
            "Optional browser parameter: chrome, firefox, edge, or brave. "
            "If the user specifies a browser, pass that browser. "
            "Otherwise use the default browser."
        ),
        function=google_search,
    )

    tools.register(
        name="youtube_search",
        description=(
            "Search YouTube for the requested query. "
            "Optional browser parameter: chrome, firefox, edge, or brave. "
            "If the user specifies a browser, you MUST pass that browser. "
            "Otherwise use the default browser."
        ),
        function=youtube_search,
    )

    tools.register(
        name="play_youtube",
        description=(
            "Search YouTube for a requested topic and play the first "
            "relevant video. Optional browser parameter can be "
            "chrome, firefox, edge, or brave. If browser is not "
            "specified, use the default browser."
        ),
        function=play_youtube,
    )

    tools.register(
        "youtube_research",
        "Search YouTube and return actual video results including title, channel, publish time, views, duration, and URL. Use this when the user wants information about YouTube search results, latest videos, episodes, or research.",
        youtube_research,
    )

    # tools.register(
    #     "google_research",
    #     "Search Google and return actual search results including title, URL, domain, and snippet. Use this when the user wants information, research, latest information, news, facts, or wants JARVIS to inspect Google search results.",
    #     google_research,
    # )

    tools.register(
        name="list_folder",
        description=(
            "List files and folders inside a directory. "
            "Supports Desktop, Downloads, Documents, "
            "or an absolute Windows path."
        ),
        function=list_folder,
    )

    tools.register(
        name="search_files",
        description=(
            "Search for files or folders by name inside a directory."
        ),
        function=search_files,
    )

    tools.register(
        name="get_file_info",
        description=(
            "Get information about a file or folder including "
            "path, type, size and modified time."
        ),
        function=get_file_info,
    )

    tools.register(
        name="create_file",
        description=(
            "Create a new text file. "
            "Never overwrite an existing file."
        ),
        function=create_file,
    )

    tools.register(
        name="create_folder",
        description=(
            "Create a new folder."
        ),
        function=create_folder,
    )

    tools.register(
        name="rename_file",
        description=(
            "Rename an existing file or folder. "
            "Never overwrite an existing destination."
        ),
        function=rename_file,
    )

    tools.register(
        name="copy_file",
        description=(
            "Copy a file or folder into an existing destination folder. "
            "Never overwrite an existing destination."
        ),
        function=copy_file,
    )

    tools.register(
        name="move_file",
        description=(
            "Move a file or folder into an existing destination folder. "
            "Never overwrite an existing destination."
        ),
        function=move_file,
    )

    tools.register(
        name="open_file",
        description=(
            "Open a file using its Windows default application."
        ),
        function=open_file,
    )

    tools.register(
        name="open_folder",
        description=(
            "Open a folder in Windows File Explorer."
        ),
        function=open_folder,
    )

    tools.register(
        name="get_recent_files",
        description=(
            "Find recently modified files inside a folder. "
            "Useful when the user asks for recent files."
        ),
        function=get_recent_files,
    )

    tools.register(
        name="delete_file",
        description=(
            "Request deletion of a file or folder. "
            "IMPORTANT: This does NOT delete immediately. "
            "It creates a pending confirmation request. "
            "After asking the user for confirmation, "
            "use confirm_delete only when the user explicitly "
            "confirms with words such as yes, confirm, or do it."
        ),
        function=delete_file,
    )

    tools.register(
        name="confirm_delete",
        description=(
            "Execute the pending file deletion after the user "
            "has explicitly confirmed it. "
            "Never use this without explicit user confirmation."
        ),
        function=confirm_delete,
    )

    tools.register(
        name="cancel_delete",
        description=(
            "Cancel the pending file deletion when the user "
            "says no, cancel, don't, or otherwise refuses."
        ),
        function=cancel_delete,
    )

    tools.register(
        name="empty_recycle_bin",
        description=(
            "Request emptying the Windows Recycle Bin. "
            "This creates a confirmation request and does NOT "
            "permanently delete anything immediately."
        ),
        function=empty_recycle_bin,
    )

    tools.register(
        name="confirm_empty_recycle_bin",
        description=(
            "Permanently empty the Windows Recycle Bin only "
            "after the user explicitly confirms the request."
        ),
        function=confirm_empty_recycle_bin,
    )

    tools.register(
        name="cancel_recycle_bin",
        description=(
            "Cancel a pending Recycle Bin empty request "
            "when the user refuses."
        ),
        function=cancel_recycle_bin,
    )

    tools.register(
        name="open_application",
        description=(
            "Open a Windows application. "
            "Supports common apps such as Notepad, Calculator, "
            "Chrome, Edge, Firefox, VS Code, Paint, File Explorer, "
            "Command Prompt and PowerShell."
        ),
        function=open_application,
    )

    tools.register(
        name="is_application_running",
        description=(
            "Check whether a specific Windows application "
            "is currently running."
        ),
        function=is_application_running,
    )

    tools.register(
        name="get_running_applications",
        description=(
            "List currently running user applications "
            "on Windows."
        ),
        function=get_running_applications,
    )

    tools.register(
        name="close_application",
        description=(
            "Request closing a running Windows application. "
            "This does NOT close it immediately. "
            "It requires user confirmation first."
        ),
        function=close_application,
    )

    tools.register(
        name="force_close_application",
        description=(
            "Close a Windows application after explicit user "
            "confirmation. Unsaved work may be lost. "
            "NEVER call this without explicit confirmation."
        ),
        function=force_close_application,
    )

    tools.register(
        name="read_clipboard",
        description=(
            "Read the current text from the Windows clipboard."
        ),
        function=read_clipboard,
    )

    tools.register(
        name="copy_to_clipboard",
        description=(
            "Copy the requested text to the Windows clipboard."
        ),
        function=copy_to_clipboard,
    )

    tools.register(
        name="clear_clipboard",
        description=(
            "Clear the current Windows clipboard."
        ),
        function=clear_clipboard,
    )

    tools.register(
        name="get_clipboard_history",
        description=(
            "Show recent clipboard history items. "
            "The clipboard manager automatically records "
            "new text copied to the clipboard."
        ),
        function=get_clipboard_history,
    )

    tools.register(
        name="search_clipboard_history",
        description=(
            "Search saved clipboard history for matching text."
        ),
        function=search_clipboard_history,
    )

    tools.register(
        name="delete_clipboard_history",
        description=(
            "Delete all saved clipboard history."
        ),
        function=delete_clipboard_history,
    )

    tools.register(
        name="start_clipboard_monitor",
        description=(
            "Start the background clipboard monitor."
        ),
        function=start_clipboard_monitor,
    )

    tools.register(
        name="stop_clipboard_monitor",
        description=(
            "Stop the background clipboard monitor."
        ),
        function=stop_clipboard_monitor,
    )

    tools.register(
        name="clipboard_monitor_status",
        description=(
            "Check whether the clipboard history monitor "
            "is currently running."
        ),
        function=clipboard_monitor_status,
    )

    # =====================================================
    # INTERNET SPEED TOOLS
    # =====================================================

    tools.register(
        name="check_internet_connection",
        description=(
            "Check whether the computer currently has "
            "an active internet connection."
        ),
        function=check_internet_connection,
    )

    tools.register(
        name="get_internet_info",
        description=(
            "Get internet connection information including "
            "ISP, public IP, speed-test server, country, "
            "and latency."
        ),
        function=get_internet_info,
    )

    tools.register(
        name="run_internet_speed_test",
        description=(
            "Run a complete internet speed test. "
            "Measure download speed, upload speed, ping, "
            "ISP, public IP, and test server."
        ),
        function=run_internet_speed_test,
    )

    tools.register(
        name="test_download_speed",
        description=(
            "Test the current internet download speed "
            "in Mbps."
        ),
        function=test_download_speed,
    )

    tools.register(
        name="test_upload_speed",
        description=(
            "Test the current internet upload speed "
            "in Mbps."
        ),
        function=test_upload_speed,
    )

    tools.register(
        name="test_ping",
        description=(
            "Test the current internet latency/ping "
            "in milliseconds."
        ),
        function=test_ping,
    )

    # =====================================================
    # CALENDAR / REMINDER TOOLS
    # =====================================================

    tools.register(
        name="create_reminder",
        description=(
            "Create a persistent reminder with a title, "
            "future date/time, and optional description. "
            "Use YYYY-MM-DD HH:MM format for date_time."
        ),
        function=create_reminder,
    )
    tools.register(
        "create_relative_reminder",
        "Create a persistent reminder after a relative amount of time such as seconds, minutes, hours, or days.",
        create_relative_reminder,
    )

    tools.register(
        name="list_reminders",
        description=(
            "List the user's saved reminders."
        ),
        function=list_reminders,
    )

    tools.register(
        name="find_reminder",
        description=(
            "Search reminders by title, description, or reminder ID."
        ),
        function=find_reminder,
    )

    tools.register(
        name="cancel_reminder",
        description=(
            "Cancel a reminder using its reminder ID. "
            "The reminder remains in history but will no longer trigger."
        ),
        function=cancel_reminder,
    )

    tools.register(
        name="delete_reminder",
        description=(
            "Permanently delete a reminder using its reminder ID."
        ),
        function=delete_reminder,
    )

    tools.register(
        name="complete_reminder",
        description=(
            "Mark a reminder as completed using its reminder ID."
        ),
        function=complete_reminder,
    )

    tools.register(
        name="get_due_reminders",
        description=(
            "Get reminders that are currently due and "
            "have not yet triggered a notification."
        ),
        function=get_due_reminders,
    )

    tools.register(
        name="start_reminder_monitor",
        description=(
            "Start the background reminder monitor."
        ),
        function=start_reminder_monitor,
    )

    tools.register(
        name="stop_reminder_monitor",
        description=(
            "Stop the background reminder monitor."
        ),
        function=stop_reminder_monitor,
    )

    tools.register(
        name="reminder_monitor_status",
        description=(
            "Check whether the background reminder monitor "
            "is currently running."
        ),
        function=reminder_monitor_status,
    )

    # =====================================================
    # WINDOW MANAGEMENT TOOLS
    # =====================================================

    tools.register(
        name="get_open_windows",
        description="List open Windows application windows.",
        function=get_open_windows,
    )

    tools.register(
        name="minimize_window",
        description="Minimize an open window. Only use for explicit minimize requests.",
        function=minimize_window,
    )

    tools.register(
        name="maximize_window",
        description="Maximize an open window. Only use for explicit maximize requests.",
        function=maximize_window,
    )

    tools.register(
        name="restore_window",
        description="Restore an open window. Only use for explicit restore requests.",
        function=restore_window,
    )

    tools.register(
        name="focus_window",
        description="Focus or switch to an open window. Only use for explicit switch or focus requests.",
        function=focus_window,
    )

    tools.register(
        name="show_desktop",
        description="Show the Windows desktop. Only use for explicit show desktop requests.",
        function=show_desktop,
    )

    # =====================================================
    # KEYBOARD CONTROL TOOLS
    # =====================================================

    tools.register(
        name="type_text",
        description=(
            "Type text into the currently focused application. "
            "ONLY use when the user explicitly asks JARVIS to type text."
        ),
        function=type_text,
    )

    tools.register(
        name="press_key",
        description=(
            "Press a single keyboard key such as Enter, Tab, Escape, "
            "Backspace, Space, or a function key. "
            "ONLY use when the user explicitly asks to press a key."
        ),
        function=press_key,
    )

    tools.register(
        name="hotkey",
        description=(
            "Press a keyboard shortcut such as Ctrl+C, Ctrl+V, Ctrl+S, "
            "Alt+Tab, or Ctrl+A. "
            "ONLY use when the user explicitly asks for a keyboard shortcut."
        ),
        function=hotkey,
    )

    # =====================================================
    # SYSTEM POWER TOOLS
    # =====================================================

    tools.register(
        name="lock_pc",
        description=(
            "Lock the Windows PC immediately. "
            "ONLY use when the user explicitly asks to lock the PC."
        ),
        function=lock_pc,
    )

    tools.register(
        name="sleep_pc",
        description=(
            "Put the Windows PC into sleep mode. "
            "ONLY use when the user explicitly asks to sleep the PC."
        ),
        function=sleep_pc,
    )

    tools.register(
        name="restart_pc",
        description=(
            "Restart the Windows PC. "
            "ONLY use when the user explicitly asks to restart the PC. "
            "This action requires confirmed=true."
        ),
        function=restart_pc,
    )

    tools.register(
        name="shutdown_pc",
        description=(
            "Shut down the Windows PC. "
            "ONLY use when the user explicitly asks to shut down the PC. "
            "This action requires confirmed=true."
        ),
        function=shutdown_pc,
    )

    tools.register(
        name="show_notification",
        description=(
            "Show a Windows desktop notification to the user. "
            "Use only when the user explicitly asks JARVIS "
            "to show or send a desktop notification."
        ),
        function=show_notification,
    )

    tools.register(
        name="set_timer",
        description=(
            "Set a background timer. "
            "Use when the user asks JARVIS to set a timer "
            "for a future duration such as minutes or hours."
        ),
        function=set_timer,
    )

    tools.register(
        name="list_timers",
        description=(
            "List currently active JARVIS timers. "
            "Use only when the user asks to see active timers."
        ),
        function=list_timers,
    )

    tools.register(
        name="cancel_timer",
        description=(
            "Cancel an active JARVIS timer. "
            "Use only when the user explicitly asks to cancel a timer."
        ),
        function=cancel_timer,
    )

    tools.register(
        name="start_system_monitor",
        description=(
            "Start background monitoring of CPU, RAM, disk, "
            "battery, and internet connection. "
            "Only use when the user explicitly asks JARVIS "
            "to monitor or watch system health."
        ),
        function=start_system_monitor,
    )

    tools.register(
        name="stop_system_monitor",
        description=(
            "Stop background system monitoring. "
            "Only use when the user explicitly asks to stop "
            "system monitoring."
        ),
        function=stop_system_monitor,
    )

    tools.register(
        name="system_monitor_status",
        description=(
            "Show whether background system monitoring is running "
            "and return its current settings. "
            "Use when the user asks about monitoring status."
        ),
        function=system_monitor_status,
    )

    tools.register(
        name="set_monitor_thresholds",
        description=(
            "Change system monitoring alert thresholds. "
            "Use only when the user explicitly asks to change "
            "CPU, RAM, disk, battery, or monitoring interval thresholds."
        ),
        function=set_monitor_thresholds,
    )

    tools.register(
        name="web_research",
        description=(
            "Search the live web for current information, news, research, facts, comparisons, and other real-time topics."
        ),
        function=web_research,
    )

    tools.register(
        name="get_recent_security_events",
        description=(
            "Get recent security events detected by JARVIS security "
            "watchers, including process, network, and startup events. "
            "Use this LOCAL tool when the user asks to see, show, "
            "check, review, or list recent security events or security "
            "history. Do NOT use web research for these requests."
        ),
        function=get_recent_security_events,
    )
    tools.register(
        name="get_latest_security_event",
        description=(
            "Get the latest security event detected by JARVIS. "
            "Use this LOCAL tool when the user asks for the latest, "
            "last, newest, or most recent security event."
        ),
        function=get_latest_security_event,
    )
    tools.register(
        name="get_security_events",
        description=(
            "Filter and retrieve security events from the local JARVIS "
            "security history. Use this tool when the user asks for "
            "security events filtered by risk level, source, or event type. "
            "Supported risk levels: LOW, MEDIUM, HIGH, CRITICAL. "
            "Supported sources include security_watcher, network_watcher, "
            "and startup_watcher."
        ),
        function=get_security_events,
    )
    tools.register(
        name="get_security_summary",
        description=(
            "Get a summary of local JARVIS security events, including "
            "total events, counts by risk level, and counts by watcher source. "
            "Use this LOCAL tool when the user asks for a security summary, "
            "security overview, security statistics, or security status."
        ),
        function=get_security_summary,
    )
    tools.register(
        name="list_automations",
        description=(
            "List all JARVIS automations and show "
            "whether each is enabled or disabled."
        ),
        function=list_automations,
    )

    tools.register(
        name="enable_automation",
        description=(
            "Enable a JARVIS automation by its exact name."
        ),
        function=enable_automation,
    )

    tools.register(
        name="disable_automation",
        description=(
            "Disable a JARVIS automation by its exact name."
        ),
        function=disable_automation,
    )

    tools.register(
        name="automation_status",
        description=(
            "Check the status of a specific "
            "JARVIS automation."
        ),
        function=automation_status,
    )

    tools.register(
        name="create_automation",
        description=(
            "Create a new JARVIS automation. "
            "Requires a name, event, and action. "
            "An optional condition can be supplied as a structured object "
            "with metric, operator, and numeric value. "
            "Supported metrics are cpu, ram, disk, and battery. "
            "Supported operators are >, >=, <, <=, ==, !=. "
            "Example condition: "
            "{'metric': 'cpu', 'operator': '>', 'value': 80}."
        ),
        function=create_automation,
    )
    tools.register(
        name="stop_all_automations",
        description=(
            "Disable ALL currently configured JARVIS automations. "
            "Use this LOCAL tool when the user says stop all "
            "automations, disable all automations, or turn off "
            "all automations."
        ),
        function=stop_all_automations,
    )
    tools.register(
        name="delete_automation",
        description=(
            "Permanently delete an existing JARVIS automation "
            "from the automation list. "
            "Use this when the user says delete, remove, "
            "or permanently remove an automation. "
            "Requires the exact automation name."
        ),
        function=delete_automation,
    )