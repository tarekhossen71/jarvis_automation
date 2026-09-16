import re
from core.planner import Planner
from core.confirmation_manager import ConfirmationManager


class Agent:

    def __init__(self, brain):
        self.brain = brain
        self.planner = Planner(brain=brain)

        # Previous conversation/tool context
        self.conversation_context = []

        # Central confirmation manager
        self.confirmation_manager = ConfirmationManager()

    # =========================================================
    # OBVIOUS CONVERSATION
    # =========================================================

    def is_obvious_conversation(self, user_input):

        text = user_input.lower().strip()

        if not text:
            return False

        conversation_phrases = (
            "hello",
            "hi",
            "hey",
            "hello jarvis",
            "hey jarvis",
            "how are you",
            "how are you doing",
            "what are you doing",
            "what are you up to",
            "who are you",
            "what can you do",
            "tell me about yourself",
            "good morning",
            "good afternoon",
            "good evening",
            "good night",
            "thank you",
            "thanks",
            "okay",
            "ok",
            "nice",
            "great",
        )

        return text in conversation_phrases

 
    # =========================================================
    # DIRECT / LOCAL TOOLS
    # =========================================================

    def try_direct_tool(self, user_input):

        import re

        text = user_input.lower().strip()

        # -----------------------------------------------------
        # AUTOMATION COMMANDS
        #
        # Automation requests must go through the Planner.
        # Otherwise words like "CPU usage" inside an
        # automation request can trigger get_cpu_info.
        # -----------------------------------------------------

        automation_keywords = (
            "create an automation",
            "create automation",
            "make an automation",
            "make automation",
            "add an automation",
            "add automation",
            "new automation",
        )

        if any(
            keyword in text
            for keyword in automation_keywords
        ):
            return None

        # -----------------------------------------------------
        # RAM
        # -----------------------------------------------------

        ram_keywords = (
            "ram usage",
            "ram use",
            "memory usage",
            "memory use",
            "how much ram",
            "how much memory",
            "ram status",
            "memory status",
        )

        if any(
            keyword in text
            for keyword in ram_keywords
        ):
            return (
                "get_ram_info",
                {},
            )

        # -----------------------------------------------------
        # CPU
        # -----------------------------------------------------

        cpu_keywords = (
            "cpu usage",
            "processor usage",
            "cpu use",
            "processor use",
            "cpu status",
            "processor status",
        )

        if any(
            keyword in text
            for keyword in cpu_keywords
        ):
            return (
                "get_cpu_info",
                {},
            )

        # -----------------------------------------------------
        # BATTERY
        # -----------------------------------------------------

        battery_keywords = (
            "battery",
            "battery percentage",
            "battery level",
            "battery status",
        )

        if any(
            keyword in text
            for keyword in battery_keywords
        ):
            return (
                "get_battery",
                {},
            )

        # -----------------------------------------------------
        # DISK
        # -----------------------------------------------------
        #
        # Supports:
        #
        # disk status
        # disk usage
        # disk space
        # my disk status
        #
        # Specific drives:
        #
        # check C drive
        # check D drive
        # check E drive
        # check F drive
        #
        # Also:
        #
        # check E
        # check E disk
        # my disk status D:
        # my disk status D
        # free space in E drive
        # free space on F drive
        #
        # -----------------------------------------------------

        disk_keywords = (
            "disk usage",
            "disk status",
            "disk space",
            "free disk space",
            "hard disk usage",
            "storage usage",
            "storage status",
            "my disk status",
            "check drive",
            "check disk",
            "free space in",
            "free space on",
            "how much free space in",
            "how much free space on",
        )

        # -----------------------------------------------------
        # Detect explicit drive command
        #
        # Examples:
        #
        # check E drive
        # check E:
        # check E
        # check E disk
        # disk status E
        # disk status E:
        # my disk status D:
        #
        # -----------------------------------------------------

        drive_match = re.search(
            r"\b([a-z])\s*:?\s*(?:drive|disk)?\b",
            text,
        )

        # -----------------------------------------------------
        # Explicit "check X drive/disk" pattern
        #
        # This specifically handles:
        #
        # check E drive
        # check F drive
        #
        # -----------------------------------------------------

        explicit_check_drive = re.search(
            r"\bcheck\s+([a-z])\s*:?\s*(?:drive|disk)?\b",
            text,
        )

        if explicit_check_drive:

            drive_letter = (
                explicit_check_drive.group(1)
                .upper()
            )

            drive = f"{drive_letter}:\\"

            return (
                "get_disk_info",
                {
                    "drive": drive,
                },
            )

        # -----------------------------------------------------
        # General disk commands
        # -----------------------------------------------------

        if any(
            keyword in text
            for keyword in disk_keywords
        ):

            if drive_match:

                drive_letter = (
                    drive_match.group(1)
                    .upper()
                )

                drive = f"{drive_letter}:\\"

            else:

                # Default drive
                drive = "C:\\"

            return (
                "get_disk_info",
                {
                    "drive": drive,
                },
            )

        # -----------------------------------------------------
        # VOLUME - GET
        # -----------------------------------------------------

        if text in (
            "what is my volume",
            "check volume",
            "volume level",
            "what is the volume",
            "volume status",
        ):
            return (
                "get_volume",
                {},
            )

        # -----------------------------------------------------
        # VOLUME - UP
        # -----------------------------------------------------

        if text in (
            "volume up",
            "increase volume",
            "increase the volume",
            "turn volume up",
            "make volume louder",
            "louder",
        ):
            return (
                "increase_volume",
                {},
            )

        # -----------------------------------------------------
        # VOLUME - DOWN
        # -----------------------------------------------------

        if text in (
            "volume down",
            "decrease volume",
            "decrease the volume",
            "turn volume down",
            "make volume lower",
            "quieter",
        ):
            return (
                "decrease_volume",
                {},
            )

        # -----------------------------------------------------
        # MUTE
        # -----------------------------------------------------

        if text in (
            "mute",
            "mute volume",
            "mute the volume",
        ):
            return (
                "mute_volume",
                {},
            )

        # -----------------------------------------------------
        # UNMUTE
        # -----------------------------------------------------

        if text in (
            "unmute",
            "unmute volume",
            "unmute the volume",
        ):
            return (
                "unmute_volume",
                {},
            )

        # -----------------------------------------------------
        # SCREENSHOT
        # -----------------------------------------------------

        if text in (
            "take screenshot",
            "take a screenshot",
            "screenshot",
            "capture screenshot",
            "capture a screenshot",
        ):
            return (
                "take_screenshot",
                {},
            )

        # -----------------------------------------------------
        # INTERNET
        # -----------------------------------------------------

        if text in (
            "check internet",
            "check internet connection",
            "is internet working",
            "internet status",
            "check my internet",
        ):
            return (
                "check_internet_connection",
                {},
            )

        # -----------------------------------------------------
        # CLIPBOARD
        # -----------------------------------------------------

        if text in (
            "read clipboard",
            "check clipboard",
            "what is in my clipboard",
            "show clipboard",
        ):
            return (
                "read_clipboard",
                {},
            )

        # -----------------------------------------------------
        # OPEN APPLICATION
        # -----------------------------------------------------

        open_match = re.match(
            r"^(?:open|launch|start)\s+(.+?)\s*$",
            text,
        )

        if open_match:

            app_name = (
                open_match.group(1)
                .strip()
            )

            # Do not treat browser search requests
            # as application opening.
            if app_name not in (
                "browser",
                "website",
            ):

                return (
                    "open_application",
                    {
                        "app_name": app_name,
                    },
                )

        # -----------------------------------------------------
        # CLOSE APPLICATION
        # -----------------------------------------------------

        close_match = re.match(
            r"^(?:close|exit|quit)\s+(.+?)\s*$",
            text,
        )

        if close_match:

            app_name = (
                close_match.group(1)
                .strip()
            )

            return (
                "close_application",
                {
                    "app_name": app_name,
                },
            )

        return None

    # =========================================================
    # EXECUTE DIRECT TOOL
    # =========================================================

    def execute_direct_tool(
        self,
        tool_name,
        arguments=None,
    ):

        if arguments is None:
            arguments = {}

        tool = self.brain.tools.get(tool_name)

        if not tool:
            return {
                "success": False,
                "error": (
                    f"Tool '{tool_name}' does not exist."
                ),
            }

        try:

            return self.brain.tools.execute(
                tool_name,
                **arguments,
            )

        except Exception as e:

            return {
                "success": False,
                "error": str(e),
            }

    # =========================================================
    # DEPENDENCY CHECK
    # =========================================================

    def dependencies_completed(
        self,
        step,
        completed_steps,
    ):

        dependencies = step.get(
            "depends_on",
            [],
        )

        if not dependencies:
            return True

        for dependency in dependencies:

            dependency_result = (
                completed_steps.get(
                    dependency
                )
            )

            if not dependency_result:
                return False

            if not dependency_result.get(
                "success",
                False,
            ):
                return False

        return True

    # =========================================================
    # DEPENDENCY CONTEXT
    # =========================================================

    def build_dependency_context(
        self,
        step,
        completed_steps,
    ):

        dependencies = step.get(
            "depends_on",
            [],
        )

        if not dependencies:
            return ""

        context_lines = []

        for dependency in dependencies:

            result = completed_steps.get(
                dependency
            )

            if not result:
                continue

            context_lines.append(
                f"Previous Step {dependency} Result:"
            )

            context_lines.append(
                str(
                    result.get(
                        "result",
                        result.get(
                            "error",
                            "",
                        ),
                    )
                )
            )

        if not context_lines:
            return ""

        return "\n".join(
            context_lines
        )

    # =========================================================
    # DEPENDENCY VALUE RESOLVER
    # =========================================================

       # =========================================================
    # DEPENDENCY VALUE RESOLVER
    # =========================================================

    def resolve_dependency_value(
        self,
        value,
        completed_steps,
    ):

        if not isinstance(
            value,
            str,
        ):
            return value

        value = value.strip()

        if not (
            value.startswith("{{")
            and value.endswith("}}")
        ):
            return value

        reference = value[
            2:-2
        ].strip()

        if not reference:
            return value

        # -----------------------------------------------------
        # Convert:
        #
        # step_1.result.results[0].url
        #
        # into:
        #
        # step_1
        # result
        # results
        # 0
        # url
        # -----------------------------------------------------

        import re

        tokens = re.findall(
            r'([^[.\]]+)|\[(\d+)\]',
            reference,
        )

        parts = []

        for name, index in tokens:

            if name:
                parts.append(name)

            elif index:
                parts.append(
                    int(index)
                )

        if len(parts) < 2:

            return value

        # -----------------------------------------------------
        # STEP NUMBER
        # -----------------------------------------------------

        step_part = parts[0]

        if not isinstance(
            step_part,
            str,
        ):
            return value

        if not step_part.startswith(
            "step_"
        ):
            return value

        try:

            step_number = int(
                step_part.replace(
                    "step_",
                    "",
                    1,
                )
            )

        except ValueError:

            return value

        # -----------------------------------------------------
        # GET STEP RESULT
        # -----------------------------------------------------

        step_result = completed_steps.get(
            step_number
        )

        if not step_result:

            raise ValueError(
                f"Step {step_number} result "
                "is not available."
            )

        current_value = step_result

        # -----------------------------------------------------
        # RESOLVE PATH
        # -----------------------------------------------------

        for part in parts[1:]:

            # -----------------------------------------------
            # DICTIONARY FIELD
            # -----------------------------------------------

            if isinstance(
                current_value,
                dict,
            ):

                if part not in current_value:

                    raise ValueError(
                        f"Field '{part}' was not "
                        f"found in step "
                        f"{step_number} result."
                    )

                current_value = (
                    current_value[part]
                )

            # -----------------------------------------------
            # LIST INDEX
            # -----------------------------------------------

            elif isinstance(
                current_value,
                list,
            ):

                if not isinstance(
                    part,
                    int,
                ):

                    raise ValueError(
                        f"Expected a list index "
                        f"but received '{part}' "
                        f"in step "
                        f"{step_number} result."
                    )

                if part < 0 or part >= len(
                    current_value
                ):

                    raise ValueError(
                        f"Index [{part}] is out of "
                        f"range in step "
                        f"{step_number} result."
                    )

                current_value = (
                    current_value[part]
                )

            # -----------------------------------------------
            # INVALID PATH
            # -----------------------------------------------

            else:

                raise ValueError(
                    f"Cannot access '{part}' "
                    f"from step {step_number} "
                    "result."
                )

        return current_value

    # =========================================================
    # RESOLVE ARGUMENTS
    # =========================================================

    def resolve_arguments(
        self,
        arguments,
        completed_steps,
    ):

        if not isinstance(
            arguments,
            dict,
        ):
            return {}

        resolved = {}

        for key, value in arguments.items():

            if isinstance(
                value,
                dict,
            ):

                resolved[key] = (
                    self.resolve_arguments(
                        value,
                        completed_steps,
                    )
                )

            elif isinstance(
                value,
                list,
            ):

                resolved[key] = [
                    self.resolve_dependency_value(
                        item,
                        completed_steps,
                    )
                    if isinstance(
                        item,
                        str,
                    )
                    else item
                    for item in value
                ]

            else:

                resolved[key] = (
                    self.resolve_dependency_value(
                        value,
                        completed_steps,
                    )
                )

        return resolved

    # =========================================================
    # HANDLE CONFIRMATION RESPONSE
    # =========================================================

    def handle_confirmation(
        self,
        user_input,
    ):

        manager = self.confirmation_manager
        

        # =====================================================
        # NO PENDING CONFIRMATION
        # =====================================================

        if not manager.has_pending():
            return None

        # =====================================================
        # YES
        # =====================================================

        if manager.is_confirmation(user_input):

            pending = manager.confirm()

            if not pending:
                return None

            action = pending.get("action")
            arguments = pending.get(
                "arguments",
                {},
            )

            original_request = pending.get(
                "original_request",
                user_input,
            )

            print(
                f"🔐 Confirmation accepted: {action}"
            )

            # -------------------------------------------------
            # EXECUTE CONFIRMED ACTION
            # -------------------------------------------------

            result = self.execute_direct_tool(
                action,
                arguments,
            )

            if not result.get(
                "success",
                False,
            ):

                return (
                    "I could not complete "
                    "the confirmed action: "
                    f"{result.get('error', 'Unknown error.')}"
                )

            # -------------------------------------------------
            # FINAL RESPONSE
            # -------------------------------------------------

            return self.brain.process_tool_results(
                user_input=original_request,
                tool_results=[
                    {
                        "step": 1,
                        "action": action,
                        **result,
                    }
                ],
            )

        # =====================================================
        # NO
        # =====================================================

        if manager.is_cancellation(user_input):

            pending = manager.get_pending()

            manager.cancel()

            return (
                "Okay. I cancelled the pending "
                f"action: {pending.get('action')}."
            )

        # =====================================================
        # SOMETHING ELSE WHILE WAITING
        # =====================================================

        return (
            "I am waiting for your confirmation. "
            "Please say yes to proceed or no to cancel."
        )


    # =========================================================
    # BUILD LOCAL DIRECT RESPONSE
    # =========================================================

    def build_local_direct_response(
        self,
        user_input,
        action,
        result,
    ):

        data = result.get(
            "result",
            {},
        )

        if not isinstance(
            data,
            dict,
        ):
            data = {}

        # -----------------------------------------------------
        # RAM
        # -----------------------------------------------------

        if action == "get_ram_info":

            total = data.get(
                "total_gb"
            )

            available = data.get(
                "available_gb"
            )

            used = data.get(
                "used_gb"
            )

            percent = data.get(
                "usage_percent"
            )

            if percent is not None:

                return (
                    f"RAM usage is {percent}%. "
                    f"Used: {used} GB, "
                    f"Available: {available} GB, "
                    f"Total: {total} GB."
                )

        # -----------------------------------------------------
        # CPU
        # -----------------------------------------------------

        if action == "get_cpu_info":

            percent = data.get(
                "usage_percent"
            )

            processor = data.get(
                "processor"
            )

            if percent is not None:

                if processor:

                    return (
                        f"CPU usage is {percent}%. "
                        f"Processor: {processor}."
                    )

                return (
                    f"CPU usage is {percent}%."
                )

        # -----------------------------------------------------
        # BATTERY
        # -----------------------------------------------------

        if action == "get_battery":

            percent = data.get(
                "percentage"
            )

            charging = data.get(
                "charging"
            )

            if percent is not None:

                charging_text = (
                    "and it is charging"
                    if charging
                    else "and it is not charging"
                )

                return (
                    f"Battery is at {percent}% "
                    f"{charging_text}."
                )

        # -----------------------------------------------------
        # DISK
        # -----------------------------------------------------

        if action == "get_disk_info":

            drive = data.get(
                "drive",
                "",
            )

            usage = data.get(
                "usage_percent"
            )

            total = data.get(
                "total_gb"
            )

            used = data.get(
                "used_gb"
            )

            free = data.get(
                "free_gb"
            )

            error = data.get(
                "error"
            )

            if error:
                return str(error)

            lines = []

            if drive:
                lines.append(
                    f"Drive: {drive}"
                )

            if usage is not None:
                lines.append(
                    f"Disk Usage: {usage}%"
                )

            if total is not None:
                lines.append(
                    f"Total: {total} GB"
                )

            if used is not None:
                lines.append(
                    f"Used: {used} GB"
                )

            if free is not None:
                lines.append(
                    f"Free: {free} GB"
                )

            if lines:
                return "\n".join(lines)

            return "No disk information was available."
        # -----------------------------------------------------
        # VOLUME
        # -----------------------------------------------------

        if action == "get_volume":

            volume = data.get(
                "volume",
                data.get(
                    "level"
                ),
            )

            if volume is not None:

                return (
                    f"Current volume is {volume}%."
                )

        if action == "increase_volume":

            return "Volume increased."

        if action == "decrease_volume":

            return "Volume decreased."

        if action == "mute_volume":

            return "Volume muted."

        if action == "unmute_volume":

            return "Volume unmuted."

        # -----------------------------------------------------
        # SCREENSHOT
        # -----------------------------------------------------

        if action == "take_screenshot":

            return (
                "Screenshot captured successfully."
            )

        # -----------------------------------------------------
        # INTERNET
        # -----------------------------------------------------

        if action == "check_internet_connection":

            connected = data.get(
                "connected"
            )

            if connected is True:

                return "Internet connection is working."

            if connected is False:

                return "Internet connection is not available."

        # -----------------------------------------------------
        # CLIPBOARD
        # -----------------------------------------------------

        if action == "read_clipboard":

            content = data.get(
                "content",
                data.get(
                    "text",
                    "",
                ),
            )

            if content:

                return (
                    f"Your clipboard contains: {content}"
                )

            return "Your clipboard is empty."

        # -----------------------------------------------------
        # OPEN APPLICATION
        # -----------------------------------------------------

        if action == "open_application":

            app_name = data.get(
                "application",
                "application",
            )

            return (
                f"{app_name} has been opened."
            )

        # -----------------------------------------------------
        # FALLBACK
        # -----------------------------------------------------

        message = (
            data.get(
                "message"
            )
            or
            result.get(
                "message"
            )
        )

        if message:

            return str(message)

        return (
            f"{action} completed successfully."
        )

    # =========================================================
    # MAIN AGENT
    # =========================================================

    def run(self, user_input):

        if not user_input:
            return None

        user_input = str(
            user_input
        ).strip()

        if not user_input:
            return None

        # =====================================================
        # IMPORTANT:
        # HANDLE PENDING CONFIRMATION FIRST
        # =====================================================

        confirmation_response = (
            self.handle_confirmation(
                user_input
            )
        )

        if confirmation_response is not None:

            return confirmation_response

        # =====================================================
        # DIRECT / LOCAL TOOL
        # =====================================================

        direct_request = (
            self.try_direct_tool(
                user_input
            )
        )

        if direct_request is not None:

            direct_action, direct_arguments = (
                direct_request
            )

            print(
                f"⚡ Local tool: {direct_action}"
            )

            # -------------------------------------------------
            # CLOSE APPLICATION
            #
            # This goes through the normal confirmation
            # system without using Gemini.
            # -------------------------------------------------

            if direct_action == "close_application":

                result = self.execute_direct_tool(
                    direct_action,
                    direct_arguments,
                )

                if not result.get(
                    "success",
                    False,
                ):

                    return (
                        "I could not complete "
                        "the request: "
                        f"{result.get('error', 'Unknown error.')}"
                    )

                # ---------------------------------------------
                # CHECK CONFIRMATION
                # ---------------------------------------------

                tool_result_data = result.get(
                    "result",
                    {},
                )

                if not isinstance(
                    tool_result_data,
                    dict,
                ):
                    tool_result_data = {}

                confirmation_required = (
                    result.get(
                        "requires_confirmation",
                        False,
                    )
                    or
                    result.get(
                        "confirmation_required",
                        False,
                    )
                    or
                    tool_result_data.get(
                        "requires_confirmation",
                        False,
                    )
                    or
                    tool_result_data.get(
                        "confirmation_required",
                        False,
                    )
                )

                if confirmation_required:

                    confirmation_message = (
                        result.get(
                            "message",
                            tool_result_data.get(
                                "message",
                                "This action requires confirmation.",
                            ),
                        )
                    )

                    pending_action = (
                        "force_close_application"
                    )

                    pending_arguments = {
                        "app_name":
                            direct_arguments.get(
                                "app_name",
                                "",
                            )
                    }

                    self.confirmation_manager.set_pending(
                        action=pending_action,
                        arguments=pending_arguments,
                        message=confirmation_message,
                        original_request=user_input,
                    )

                    print(
                        "🔐 Confirmation required."
                    )

                    return (
                        "This action requires confirmation."
                    )

                return self.build_local_direct_response(
                    user_input,
                    direct_action,
                    result,
                )

            # -------------------------------------------------
            # NORMAL LOCAL TOOL
            # -------------------------------------------------

            result = self.execute_direct_tool(
                direct_action,
                direct_arguments,
            )

            if not result.get(
                "success",
                False,
            ):

                return (
                    "I could not complete "
                    "the request: "
                    f"{result.get('error', 'Unknown error.')}"
                )

            return self.build_local_direct_response(
                user_input,
                direct_action,
                result,
            )
        # =====================================================
        # OBVIOUS CONVERSATION
        # =====================================================

        if self.is_obvious_conversation(
            user_input
        ):

            return self.brain.process(
                user_input
            )

        # =====================================================
        # CREATE PLAN
        # =====================================================

        planner_context = (
            self.build_planner_context()
        )

        plan = self.planner.create_plan(
            user_input,
            context=planner_context,
        )

        if not plan:

            return (
                "I could not create a "
                "plan for that request."
            )

        # =====================================================
        # CONVERSATION ONLY
        # =====================================================

        if (
            len(plan) == 1
            and plan[0].get(
                "action"
            ) == "conversation"
        ):

            response = self.brain.process(
                user_input
            )

            self.conversation_context.append(
                {
                    "user": user_input,
                    "tool_results": [],
                    "assistant": response,
                }
            )

            self.conversation_context = (
                self.conversation_context[-5:]
            )

            return response

        # =====================================================
        # EXECUTE PLAN
        # =====================================================

        results = []

        completed_steps = {}

        for step in plan:

            step_number = step.get(
                "step",
                len(results) + 1,
            )

            action = step.get(
                "action"
            )

            arguments = step.get(
                "arguments",
                {},
            )

            description = step.get(
                "description",
                action,
            )

            depends_on = step.get(
                "depends_on",
                [],
            )

            # -------------------------------------------------
            # DEPENDENCY CHECK
            # -------------------------------------------------

            if not self.dependencies_completed(
                step,
                completed_steps,
            ):

                print(
                    f"⛔ Agent step "
                    f"{step_number} skipped."
                )

                print(
                    f"   Depends on: "
                    f"{depends_on}"
                )

                dependency_result = {
                    "step": step_number,
                    "action": action,
                    "success": False,
                    "skipped": True,
                    "error": (
                        "Required previous "
                        "step failed or was "
                        "not completed."
                    ),
                    "depends_on": depends_on,
                }

                results.append(
                    dependency_result
                )

                completed_steps[
                    step_number
                ] = dependency_result

                break

            print(
                f"🧩 Agent step "
                f"{step_number}: "
                f"{description}"
            )

            if depends_on:

                print(
                    f"   ↳ Depends on: "
                    f"{depends_on}"
                )

            # -------------------------------------------------
            # CONVERSATION
            # -------------------------------------------------

            if action == "conversation":

                result = self.brain.process(
                    description
                )

                step_result = {
                    "step": step_number,
                    "action": action,
                    "success": True,
                    "result": result,
                    "depends_on": depends_on,
                }

                results.append(
                    step_result
                )

                completed_steps[
                    step_number
                ] = step_result

                print(
                    f"✅ Agent step "
                    f"{step_number} completed."
                )

                continue

            # -------------------------------------------------
            # GET TOOL
            # -------------------------------------------------

            tool = self.brain.tools.get(
                action
            )

            if not tool:

                error = (
                    f"Tool '{action}' "
                    "does not exist."
                )

                print(
                    f"❌ {error}"
                )

                step_result = {
                    "step": step_number,
                    "action": action,
                    "success": False,
                    "error": error,
                    "depends_on": depends_on,
                }

                results.append(
                    step_result
                )

                completed_steps[
                    step_number
                ] = step_result

                break

            # -------------------------------------------------
            # DEPENDENCY CONTEXT
            # -------------------------------------------------

            dependency_context = (
                self.build_dependency_context(
                    step,
                    completed_steps,
                )
            )

            if dependency_context:

                print(
                    "   ↳ Previous results "
                    "available."
                )

            # -------------------------------------------------
            # RESOLVE ARGUMENTS
            # -------------------------------------------------

            try:

                resolved_arguments = (
                    self.resolve_arguments(
                        arguments,
                        completed_steps,
                    )
                )

                if (
                    resolved_arguments
                    != arguments
                ):

                    print(
                        "   ↳ Dependency "
                        "values resolved."
                    )

            except Exception as e:

                result = {
                    "success": False,
                    "error": str(e),
                }

                step_result = {
                    "step": step_number,
                    "action": action,
                    **result,
                    "depends_on": depends_on,
                }

                results.append(
                    step_result
                )

                completed_steps[
                    step_number
                ] = step_result

                break

            # -------------------------------------------------
            # EXECUTE TOOL
            # -------------------------------------------------
            # -------------------------------------------------
            # DANGEROUS POWER ACTIONS
            # -------------------------------------------------
            #
            # These actions MUST NEVER execute directly.
            # Confirmation must happen before the real tool call.
            #
            # -------------------------------------------------

            if action in (
                "shutdown_pc",
                "restart_pc",
            ):

                confirmation_message = (
                    "Are you sure you want to "
                    f"{'shut down' if action == 'shutdown_pc' else 'restart'} "
                    "the PC? Please confirm with yes or no."
                )

                # IMPORTANT:
                # Never trust Gemini/planner's "confirmed" value.
                # First execution is ALWAYS unconfirmed.
                pending_arguments = (
                    resolved_arguments.copy()
                )

                pending_arguments["confirmed"] = True

                self.confirmation_manager.set_pending(
                    action=action,
                    arguments=pending_arguments,
                    message=confirmation_message,
                    original_request=user_input,
                )

                print(
                    "🔐 Confirmation required."
                )

                return confirmation_message
            try:

                result = (
                    self.brain.tools.execute(
                        action,
                        **resolved_arguments,
                    )
                )

            except Exception as e:

                result = {
                    "success": False,
                    "error": str(e),
                }

            # -------------------------------------------------
            # OBSERVE RESULT
            # -------------------------------------------------

            observation = self.observe_result(
                step,
                result,
            )

            if observation.get("success"):
                print(
                    f"👀 Agent observed: "
                    f"step {step_number} succeeded."
                )
            else:
                print(
                    f"👀 Agent observed: "
                    f"step {step_number} failed."
                )

                print(
                    f"   Reason: "
                    f"{observation.get('message')}"
                )

            # -------------------------------------------------
            # CHECK CONFIRMATION
            # -------------------------------------------------

            tool_result_data = result.get(
                "result",
                {}
            )

            if not isinstance(
                tool_result_data,
                dict,
            ):
                tool_result_data = {}

            confirmation_required = (
                result.get(
                    "requires_confirmation",
                    False,
                )
                or
                result.get(
                    "confirmation_required",
                    False,
                )
                or
                tool_result_data.get(
                    "requires_confirmation",
                    False,
                )
                or
                tool_result_data.get(
                    "confirmation_required",
                    False,
                )
            )

            if confirmation_required:

                confirmation_message = (
                    result.get(
                        "message",
                        "This action requires confirmation.",
                    )
                )

                pending_arguments = (
                    resolved_arguments.copy()
                )

                # -------------------------------------------------
                # POWER ACTIONS
                # -------------------------------------------------

                if action in (
                    "shutdown_pc",
                    "restart_pc",
                ):

                    # IMPORTANT:
                    # First execution only checks confirmation.
                    # Actual execution will happen with
                    # confirmed=True after user says YES.

                    pending_arguments["confirmed"] = True

                # -------------------------------------------------
                # CLOSE APPLICATION
                # -------------------------------------------------

                if action == "close_application":

                    pending_action = (
                        "force_close_application"
                    )

                    pending_arguments = {
                        "app_name":
                            pending_arguments.get(
                                "app_name",
                                pending_arguments.get(
                                    "application",
                                    "",
                                ),
                            )
                    }

                else:

                    pending_action = action

                self.confirmation_manager.set_pending(
                    action=pending_action,
                    arguments=pending_arguments,
                    message=confirmation_message,
                    original_request=user_input,
                )

                pending = (
                    self.confirmation_manager
                    .get_pending()
                )

                pending[
                    "original_request"
                ] = user_input

                print(
                    "🔐 Confirmation required."
                )

                step_result = {
                    "step": step_number,
                    "action": action,
                    "success": True,
                    "requires_confirmation": True,
                    "result": result,
                    "depends_on": depends_on,
                }

                results.append(
                    step_result
                )

                completed_steps[
                    step_number
                ] = step_result

                return confirmation_message
            
         
            # -------------------------------------------------
            # VERIFY RESULT
            # -------------------------------------------------

            verified = self.verify_result(
                step,
                result,
            )

            if verified:

                print(
                    f"🔎 Agent verified: "
                    f"step {step_number} completed successfully."
                )

            else:

                print(
                    f"🔎 Agent verification failed "
                    f"for step {step_number}."
                )

                failure = self.analyze_failure(
                    step,
                    result,
                )

                print(
                    f"   Failure analysis: "
                    f"{failure}"
                )

                # -------------------------------------------------
                # EXECUTE RECOVERY PLAN
                # -------------------------------------------------

                recovery = self.run_recovery(
                    user_input=user_input,
                    failed_step=failure,
                    completed_steps=completed_steps,
                    attempt=1,
                    max_attempts=2,
                )

                if recovery.get("success"):

                    print(
                        "🧠 Agent recovery plan is ready."
                    )

                    recovery_plan = recovery.get(
                        "plan"
                    )

                    print(
                        "🧩 Executing recovery plan..."
                    )

                    recovery_result = (
                        self.execute_recovery_plan_steps(
                            recovery_plan
                        )
                    )

                    if recovery_result.get(
                        "success"
                    ):

                        print(
                            "✅ Recovery plan "
                            "completed successfully."
                        )

                    else:

                        print(
                            "❌ Recovery plan "
                            "execution failed."
                        )

                        print(
                            f"   Reason: "
                            f"{recovery_result.get('error')}"
                        )
                else:

                    print(
                        "❌ Agent recovery failed."
                    )

                    print(
                        f"   Reason: "
                        f"{recovery.get('error')}"
                    )

            # -------------------------------------------------
            # NORMAL RESULT
            # -------------------------------------------------

            step_result = {
                "step": step_number,
                "action": action,
                **result,
                "depends_on": depends_on,
            }

            results.append(
                step_result
            )

            completed_steps[
                step_number
            ] = step_result

            if result.get(
                "success",
                False,
            ):

                print(
                    f"✅ Agent step "
                    f"{step_number} completed."
                )

            else:

                print(
                    f"❌ Agent step "
                    f"{step_number} failed:"
                )

                print(
                    result.get(
                        "error",
                        "Unknown error.",
                    )
                )

                break

        # =====================================================
        # NO RESULTS
        # =====================================================

        if not results:

            return (
                "I could not complete "
                "the requested task."
            )

        # =====================================================
        # FAILED STEPS
        # =====================================================

        failed_steps = [
            item
            for item in results
            if not item.get(
                "success",
                False,
            )
        ]

        if failed_steps:

            failed = failed_steps[-1]

            completed = len([
                item
                for item in results
                if item.get(
                    "success",
                    False,
                )
            ])

            if failed.get(
                "skipped",
                False,
            ):

                return (
                    f"I completed "
                    f"{completed} step(s), "
                    f"but step "
                    f"{failed.get('step')} "
                    "was skipped because "
                    "a required previous "
                    "step was not completed."
                )

            return (
                f"I completed "
                f"{completed} step(s), "
                f"but step "
                f"{failed.get('step')} "
                "failed: "
                f"{failed.get('error', 'Unknown error.')}"
            )

        # =====================================================
        # LOCAL RESPONSE
        # =====================================================

        local_response = (
            self.build_local_tool_response(
                user_input=user_input,
                results=results,
            )
        )

        if local_response:

            self.conversation_context.append(
                {
                    "user": user_input,
                    "tool_results": results,
                    "assistant": local_response,
                }
            )

            self.conversation_context = (
                self.conversation_context[-5:]
            )

            return local_response

        # =====================================================
        # GEMINI FINAL RESPONSE
        # =====================================================

        final_response = (
            self.brain.process_tool_results(
                user_input=user_input,
                tool_results=results,
            )
        )

        self.conversation_context.append(
            {
                "user": user_input,
                "tool_results": results,
                "assistant": final_response,
            }
        )

        self.conversation_context = (
            self.conversation_context[-5:]
        )

        return final_response

    
    # =========================================================
    # PLAN HELPERS
    # =========================================================

    def get_plan(self, user_input):

        planner_context = (
            self.build_planner_context()
        )

        return self.planner.create_plan(
            user_input,
            context=planner_context,
        )

    def get_last_plan(self):
        return self.planner.get_last_plan()

    def clear_plan(self):
        self.planner.clear_plan()


    # =========================================================
    # AGENT OBSERVATION
    # =========================================================

    def observe_result(self, step, result):
        """
        Analyze the result of an executed step.

        Returns a normalized observation that the agent
        can use for verification and re-planning.
        """

        if not isinstance(result, dict):
            return {
                "success": False,
                "status": "invalid_result",
                "message": "Tool returned an invalid result.",
                "step": step.get("step"),
                "action": step.get("action"),
            }

        success = result.get(
            "success",
            False,
        )

        if success:
            return {
                "success": True,
                "status": "success",
                "message": "Step executed successfully.",
                "step": step.get("step"),
                "action": step.get("action"),
                "result": result.get(
                    "result",
                    result,
                ),
            }

        return {
            "success": False,
            "status": "failed",
            "message": result.get(
                "error",
                "Step execution failed.",
            ),
            "step": step.get("step"),
            "action": step.get("action"),
            "result": result.get(
                "result",
                {},
            ),
        }

    # =========================================================
    # AGENT VERIFICATION
    # =========================================================

    def verify_result(self, step, result):
        """
        Verify whether a tool execution produced a valid
        successful result.

        This is intentionally conservative:
        a tool must explicitly report success=True.
        """

        if not isinstance(result, dict):
            return False

        if not result.get(
            "success",
            False,
        ):
            return False

        return True

    # =========================================================
    # AGENT FAILURE ANALYSIS
    # =========================================================

    def analyze_failure(
        self,
        step,
        result,
    ):
        """
        Build structured information about a failed step.
        This information will later be supplied to the
        Planner for re-planning.
        """

        if not isinstance(result, dict):
            return {
                "step": step.get("step"),
                "action": step.get("action"),
                "error": "Invalid tool result.",
            }

        return {
            "step": step.get("step"),
            "action": step.get("action"),
            "description": step.get(
                "description",
                "",
            ),
            "arguments": step.get(
                "arguments",
                {},
            ),
            "error": result.get(
                "error",
                "Unknown error.",
            ),
            "result": result.get(
                "result",
                {},
            ),
        }

    # =========================================================
    # AGENT RE-PLAN
    # =========================================================

    def create_recovery_plan(
        self,
        user_input,
        failed_step,
        completed_steps,
    ):
        """
        Create a new plan after an execution failure.

        The planner receives:
        - Original user request
        - Failed step
        - Error information
        - Previously completed steps
        """

        recovery_context = (
            self.build_planner_context()
        )

        recovery_context += "\n\n"
        recovery_context += (
            "IMPORTANT: The previous execution "
            "attempt failed."
        )

        recovery_context += "\n"
        recovery_context += (
            f"Failed step: "
            f"{failed_step.get('step')}"
        )

        recovery_context += "\n"
        recovery_context += (
            f"Failed action: "
            f"{failed_step.get('action')}"
        )

        recovery_context += "\n"
        recovery_context += (
            f"Failure: "
            f"{failed_step.get('error', 'Unknown error.')}"
        )

        recovery_context += "\n"
        recovery_context += (
            "Create an alternative recovery plan. "
            "Do not blindly repeat the exact failed action."
        )

        if completed_steps:

            recovery_context += "\n\n"
            recovery_context += (
                "Previously completed steps:"
            )

            for step_number, result in (
                completed_steps.items()
            ):

                recovery_context += "\n"
                recovery_context += (
                    f"Step {step_number}: "
                    f"{result.get('action')} "
                    f"→ "
                    f"{'success' if result.get('success') else 'failed'}"
                )

        try:

            new_plan = self.planner.create_plan(
                user_input,
                context=recovery_context,
            )

            return new_plan

        except Exception as e:

            print(
                f"❌ Recovery planning failed: {e}"
            )

            return None


    # =========================================================
    # AGENT RECOVERY EXECUTION
    # =========================================================

    def execute_recovery_plan(
        self,
        user_input,
        failed_step,
        completed_steps,
        max_attempts=2,
    ):
        """
        Create and execute an alternative recovery plan
        after a step failure.
        """

        print(
            "🧠 Agent: creating recovery plan..."
        )

        recovery_plan = self.create_recovery_plan(
            user_input=user_input,
            failed_step=failed_step,
            completed_steps=completed_steps,
        )

        if not recovery_plan:
            print(
                "❌ Agent: recovery plan could not be created."
            )
            return {
                "success": False,
                "error": "Recovery plan could not be created.",
            }

        print(
            "🧩 Agent: recovery plan created."
        )

        return {
            "success": True,
            "plan": recovery_plan,
        }

    
    # =========================================================
    # AGENT RECOVERY LOOP
    # =========================================================
    def run_recovery(
        self,
        user_input,
        failed_step,
        completed_steps,
        attempt=1,
        max_attempts=2,
    ):
        """
        Create and execute recovery plans.

        If a recovery plan fails, another recovery plan
        may be created until max_attempts is reached.
        """

        if attempt > max_attempts:

            print(
                "🛑 Agent recovery limit reached."
            )

            return {
                "success": False,
                "error": (
                    "Maximum recovery attempts reached."
                ),
            }

        print(
            f"🔄 Agent recovery attempt "
            f"{attempt}/{max_attempts}"
        )

        recovery = self.execute_recovery_plan(
            user_input=user_input,
            failed_step=failed_step,
            completed_steps=completed_steps,
        )

        if not recovery.get("success"):

            return {
                "success": False,
                "error": (
                    recovery.get(
                        "error",
                        "Recovery planning failed.",
                    )
                ),
            }

        recovery_plan = recovery.get(
            "plan"
        )

        if not recovery_plan:

            return {
                "success": False,
                "error": "Recovery plan is empty.",
            }

        print(
            "🧩 Agent: recovery plan received."
        )

        execution = (
            self.execute_recovery_plan_steps(
                recovery_plan
            )
        )

        if execution.get("success"):

            print(
                "✅ Recovery completed successfully."
            )

            return {
                "success": True,
                "plan": recovery_plan,
                "attempt": attempt,
            }

        # -----------------------------------------------------
        # RECOVERY FAILED
        # -----------------------------------------------------

        print(
            "❌ Recovery plan failed."
        )

        failed_recovery_step = execution.get(
            "failed_step"
        )

        recovery_result = execution.get(
            "result",
            {},
        )

        if not failed_recovery_step:

            return {
                "success": False,
                "error": execution.get(
                    "error",
                    "Recovery execution failed.",
                ),
            }

        failed_execution = (
            self.analyze_failure(
                failed_recovery_step,
                recovery_result,
            )
        )

        print(
            "🧠 Agent: analyzing recovery failure..."
        )

        return self.run_recovery(
            user_input=user_input,
            failed_step=failed_execution,
            completed_steps=completed_steps,
            attempt=attempt + 1,
            max_attempts=max_attempts,
        )
    

    # =========================================================
    # EXECUTE RECOVERY PLAN
    # =========================================================

    def execute_recovery_plan_steps(
        self,
        recovery_plan,
    ):
        """
        Execute the steps generated by the recovery planner.

        This method intentionally handles only the basic
        recovery execution flow. Confirmation, dependencies,
        and advanced recovery will be added separately.
        """

        if not isinstance(recovery_plan, list):
            return {
                "success": False,
                "error": "Invalid recovery plan.",
            }

        for recovery_step in recovery_plan:

            action = recovery_step.get(
                "action"
            )

            arguments = recovery_step.get(
                "arguments",
                {},
            )

            if not action:
                print(
                    "⚠️ Recovery step has no action."
                )
                continue

            print(
                f"🔄 Recovery executing: "
                f"{action}"
            )

            try:

                result = (
                    self.brain.tools.execute(
                        action,
                        **arguments,
                    )
                )

            except Exception as e:

                result = {
                    "success": False,
                    "error": str(e),
                }

            observation = self.observe_result(
                recovery_step,
                result,
            )

            if observation.get("success"):

                print(
                    "👀 Recovery step observed "
                    "successfully."
                )

                verified = self.verify_result(
                    recovery_step,
                    result,
                )

                if verified:

                    print(
                        "🔎 Recovery step verified "
                        "successfully."
                    )

                    continue

            print(
                "❌ Recovery step failed."
            )

            return {
                "success": False,
                "error": result.get(
                    "error",
                    "Recovery step failed.",
                ),
                "failed_step": recovery_step,
                "result": result,
            }

        return {
            "success": True,
            "message": (
                "Recovery plan executed successfully."
            ),
        }
    
    # =========================================================
    # BUILD PLANNER CONTEXT
    # =========================================================

    def build_planner_context(self):

        if not self.conversation_context:
            return ""

        context_lines = []

        for item in self.conversation_context:

            context_lines.append(
                f"User: {item.get('user', '')}"
            )

            tool_results = item.get(
                "tool_results"
            )

            if tool_results:

                context_lines.append(
                    "Tool Results:"
                )

                context_lines.append(
                    str(tool_results)
                )

            assistant_response = item.get(
                "assistant"
            )

            if assistant_response:

                context_lines.append(
                    f"JARVIS: {assistant_response}"
                )

        return "\n".join(
            context_lines
        )

    # =========================================================
    # LOCAL TOOL RESPONSE
    # =========================================================

    def build_local_tool_response(self,user_input,results):
        """
        Build a simple natural-language response for
        successfully executed local tools.
        """

        if not results:
            return None

        system_result = None
        battery_result = None
        lines = []
        # -----------------------------------------------------
        # COMPLETE PC INFORMATION
        # -----------------------------------------------------

        actions = [
            item.get("action")
            for item in results
            if isinstance(item, dict)
        ]

        if (
            "get_system_info" in actions
            and "get_battery" in actions
        ):

            

            for item in results:

                if item.get("action") == "get_system_info":
                    system_result = item.get(
                        "result",
                        {},
                    )

                elif item.get("action") == "get_battery":
                    battery_result = item.get(
                        "result",
                        {},
                    )

            # ---------------------------------------------
            # SYSTEM INFORMATION
            # ---------------------------------------------

            if isinstance(system_result, dict):

                machine = system_result.get("machine")
                operating_system = system_result.get(
                    "operating_system"
                )
                os_version = system_result.get(
                    "os_version"
                )

                cpu = system_result.get(
                    "cpu",
                    {},
                )

                ram = system_result.get(
                    "ram",
                    {},
                )

                disk = system_result.get(
                    "disk",
                    {},
                )

                if machine:
                    lines.append(
                        f"Machine: {machine}"
                    )

                if operating_system:
                    lines.append(
                        f"OS: {operating_system}"
                    )

                if os_version:
                    lines.append(
                        f"OS Version: {os_version}"
                    )

                # CPU
                if isinstance(cpu, dict):

                    cpu_usage = cpu.get(
                        "usage_percent"
                    )

                    processor = cpu.get(
                        "processor"
                    )

                    logical_cpus = cpu.get(
                        "logical_cpus"
                    )

                    physical_cpus = cpu.get(
                        "physical_cpus"
                    )

                    if processor:
                        lines.append(
                            f"Processor: {processor}"
                        )

                    if cpu_usage is not None:
                        lines.append(
                            f"CPU Usage: {cpu_usage}%"
                        )

                    if physical_cpus is not None:
                        lines.append(
                            f"Physical CPU Cores: {physical_cpus}"
                        )

                    if logical_cpus is not None:
                        lines.append(
                            f"Logical CPU Cores: {logical_cpus}"
                        )

                # RAM
                if isinstance(ram, dict):

                    ram_usage = ram.get(
                        "usage_percent"
                    )

                    total_ram = ram.get(
                        "total_gb"
                    )

                    used_ram = ram.get(
                        "used_gb"
                    )

                    available_ram = ram.get(
                        "available_gb"
                    )

                    if ram_usage is not None:
                        lines.append(
                            f"RAM Usage: {ram_usage}%"
                        )

                    if total_ram is not None:
                        lines.append(
                            f"RAM Total: {total_ram} GB"
                        )

                    if used_ram is not None:
                        lines.append(
                            f"RAM Used: {used_ram} GB"
                        )

                    if available_ram is not None:
                        lines.append(
                            f"RAM Available: {available_ram} GB"
                        )

                # Disk
                if isinstance(disk, dict):

                    drive = disk.get(
                        "drive"
                    )

                    disk_usage = disk.get(
                        "usage_percent"
                    )

                    total_disk = disk.get(
                        "total_gb"
                    )

                    used_disk = disk.get(
                        "used_gb"
                    )

                    free_disk = disk.get(
                        "free_gb"
                    )

                    if drive:
                        lines.append(
                            f"Disk ({drive}):"
                        )

                    if disk_usage is not None:
                        lines.append(
                            f"Disk Usage: {disk_usage}%"
                        )

                    if total_disk is not None:
                        lines.append(
                            f"Disk Total: {total_disk} GB"
                        )

                    if used_disk is not None:
                        lines.append(
                            f"Disk Used: {used_disk} GB"
                        )

                    if free_disk is not None:
                        lines.append(
                            f"Disk Free: {free_disk} GB"
                        )

            # ---------------------------------------------
            # BATTERY INFORMATION
            # ---------------------------------------------

            if isinstance(battery_result, dict):

                battery_message = battery_result.get(
                    "message"
                )

                if battery_message:

                    lines.append(
                        str(battery_message)
                    )

                else:

                    percentage = battery_result.get(
                        "percentage"
                    )

                    charging = battery_result.get(
                        "charging"
                    )

                    if percentage is not None:

                        if charging:
                            lines.append(
                                f"Battery: {percentage}% "
                                "and charging."
                            )
                        else:
                            lines.append(
                                f"Battery: {percentage}% "
                                "and not charging."
                            )

                    else:

                        lines.append(
                            "Battery: No battery detected. "
                            "The computer appears to be a desktop PC."
                        )

            if lines:
                return "\n".join(lines)

        last_result = results[-1]

        action = last_result.get(
            "action",
            "",
        )

        if not last_result.get(
            "success",
            False,
        ):

            error = last_result.get(
                "error"
            )

            if action == "delete_automation" and error:

                return str(error)

            return None

        result = last_result.get(
            "result",
            {},
        )

        if not isinstance(
            result,
            dict,
        ):
            result = {}



        # -----------------------------------------------------
        # FEATURES
        # -----------------------------------------------------
        if action == "get_available_features":

            features = result.get(
                "features",
                []
            )

            count = result.get(
                "count",
                len(features)
            )

            if not features:

                return (
                    "No JARVIS features are currently registered."
                )

            lines = [
                f"JARVIS currently has {count} available features:"
            ]

            for index, feature in enumerate(
                features,
                start=1
            ):
                lines.append(
                    f"{index}. {feature}"
                )

            return "\n".join(lines)
        # -----------------------------------------------------
        # SYSTEM
        # -----------------------------------------------------

        if action == "get_system_info":

            return (
                result.get("message")
                or "System information retrieved successfully."
            )

        if action == "get_battery":

            return (
                result.get("message")
                or "Battery information retrieved successfully."
            )

        # -----------------------------------------------------
        # VOLUME
        # -----------------------------------------------------

        if action == "get_volume":

            volume = result.get(
                "volume",
                result.get("level"),
            )

            if volume is not None:
                return (
                    f"Current volume is {volume}%."
                )

            return "Current volume retrieved successfully."

        if action == "increase_volume":
            return "Volume increased."

        if action == "decrease_volume":
            return "Volume decreased."

        if action == "mute_volume":
            return "Volume muted."

        if action == "unmute_volume":
            return "Volume unmuted."

        # -----------------------------------------------------
        # SCREENSHOT
        # -----------------------------------------------------

        if action == "take_screenshot":
            return (
                result.get("message")
                or "Screenshot captured successfully."
            )

        # -----------------------------------------------------
        # WINDOW MANAGEMENT
        # -----------------------------------------------------

        if action == "get_open_windows":

            count = result.get(
                "count"
            )

            if count is not None:
                return (
                    f"There are {count} visible windows open."
                )

            return "Open windows retrieved successfully."

        if action == "minimize_window":

            return (
                result.get("message")
                or "Window minimized successfully."
            )

        if action == "maximize_window":

            return (
                result.get("message")
                or "Window maximized successfully."
            )

        if action == "restore_window":

            return (
                result.get("message")
                or "Window restored successfully."
            )

        if action == "focus_window":

            return (
                result.get("message")
                or "Window focused successfully."
            )

        if action == "show_desktop":

            return (
                result.get("message")
                or "Desktop is now visible."
            )

        # -----------------------------------------------------
        # KEYBOARD
        # -----------------------------------------------------

        if action == "type_text":

            return (
                result.get("message")
                or "Text typed successfully."
            )

        if action == "press_key":

            key = result.get(
                "key"
            )

            if key:
                return f"Pressed {key}."

            return (
                result.get("message")
                or "Key pressed successfully."
            )

        if action == "hotkey":

            keys = result.get(
                "keys"
            )

            if isinstance(
                keys,
                list,
            ):
                return (
                    f"Pressed {'+'.join(keys)}."
                )

            return (
                result.get("message")
                or "Keyboard shortcut executed."
            )

        # -----------------------------------------------------
        # INTERNET
        # -----------------------------------------------------

        if action == "check_internet_connection":

            connected = result.get(
                "connected"
            )

            if connected is True:
                return "Internet connection is working."

            if connected is False:
                return "Internet connection is not available."

        if action == "get_internet_info":

            return (
                result.get("message")
                or "Internet information retrieved successfully."
            )

        if action == "run_internet_speed_test":

            download = result.get(
                "download_mbps",
                0
            )

            upload = result.get(
                "upload_mbps",
                0
            )

            ping = result.get(
                "ping_ms",
                0
            )

            isp = result.get(
                "isp",
                "Unknown"
            )

            server = result.get(
                "server",
                "Unknown"
            )

            country = result.get(
                "server_country",
                "Unknown"
            )

            return (
                "Internet speed test completed.\n"
                f"Download: {download} Mbps\n"
                f"Upload: {upload} Mbps\n"
                f"Ping: {ping} ms\n"
                f"ISP: {isp}\n"
                f"Server: {server}, {country}"
            )

        if action == "test_download_speed":

            speed = result.get(
                "download_mbps"
            )

            if speed is not None:
                return (
                    f"Download speed is {speed} Mbps."
                )

        if action == "test_upload_speed":

            speed = result.get(
                "upload_mbps"
            )

            if speed is not None:
                return (
                    f"Upload speed is {speed} Mbps."
                )

        if action == "test_ping":

            ping = result.get(
                "ping_ms"
            )

            if ping is not None:
                return (
                    f"Ping is {ping} milliseconds."
                )

        # -----------------------------------------------------
        # CLIPBOARD
        # -----------------------------------------------------

        if action == "read_clipboard":

            content = result.get(
                "content",
                result.get(
                    "text",
                    "",
                ),
            )

            if content:
                return (
                    f"Your clipboard contains: {content}"
                )

            return "Your clipboard is empty."

        if action == "copy_to_clipboard":

            return (
                result.get("message")
                or "Text copied to the clipboard."
            )

        if action == "clear_clipboard":

            return (
                result.get("message")
                or "Clipboard cleared."
            )

        if action == "get_clipboard_history":

            return (
                result.get("message")
                or "Clipboard history retrieved."
            )

        if action == "search_clipboard_history":

            return (
                result.get("message")
                or "Clipboard history search completed."
            )

        if action == "delete_clipboard_history":

            return (
                result.get("message")
                or "Clipboard history deleted."
            )

        # -----------------------------------------------------
        # APPLICATION
        # -----------------------------------------------------

        if action == "open_application":

            app_name = result.get(
                "application",
                result.get(
                    "app_name",
                    "Application",
                ),
            )

            return (
                f"{app_name} has been opened."
            )

        # -----------------------------------------------------
        # FILES / FOLDERS
        # -----------------------------------------------------

        if action == "open_file":
            return (
                result.get("message")
                or "File opened successfully."
            )

        if action == "open_folder":
            return (
                result.get("message")
                or "Folder opened successfully."
            )

        if action == "create_file":
            return (
                result.get("message")
                or "File created successfully."
            )

        if action == "create_folder":
            return (
                result.get("message")
                or "Folder created successfully."
            )

        if action == "rename_file":
            return (
                result.get("message")
                or "File or folder renamed successfully."
            )

        if action == "copy_file":
            return (
                result.get("message")
                or "File or folder copied successfully."
            )

        if action == "move_file":
            return (
                result.get("message")
                or "File or folder moved successfully."
            )

        # -----------------------------------------------------
        # REMINDERS
        # -----------------------------------------------------

        if action == "create_reminder":
            return (
                result.get("message")
                or "Reminder created successfully."
            )

        if action == "cancel_reminder":
            return (
                result.get("message")
                or "Reminder cancelled."
            )

        if action == "complete_reminder":
            return (
                result.get("message")
                or "Reminder completed."
            )

        if action == "delete_reminder":
            return (
                result.get("message")
                or "Reminder deleted."
            )

        # -----------------------------------------------------
        # AUTOMATIONS
        # -----------------------------------------------------

        if action == "create_automation":

            name = result.get(
                "name",
                "Automation",
            )

            event = result.get(
                "event",
                "Unknown",
            )

            enabled = result.get(
                "enabled",
                True,
            )

            status = (
                "enabled"
                if enabled
                else "disabled"
            )

            return (
                f"Automation '{name}' created successfully. "
                f"Event: {event}. "
                f"Status: {status}."
            )
        
        if action == "list_automations":
            automations = result.get("automations", [])

            if not automations:
                return "There are no configured automations."

            lines = ["Here are your current automations:"]

            for automation in automations:

                name = automation.get(
                    "name",
                    "Unknown",
                )

                event = automation.get(
                    "event",
                    "Unknown",
                )

                enabled = automation.get(
                    "enabled",
                    False,
                )

                status = (
                    "enabled"
                    if enabled
                    else "disabled"
                )

                condition = automation.get(
                    "condition"
                )

                condition_text = ""

                if isinstance(condition, dict):

                    metric = condition.get(
                        "metric"
                    )

                    operator = condition.get(
                        "operator"
                    )

                    value = condition.get(
                        "value"
                    )

                    if (
                        metric
                        and operator
                        and value is not None
                    ):
                        condition_text = (
                            f", {metric.upper()} "
                            f"{operator} {value:g}"
                        )

                lines.append(
                    f"- {name}: "
                    f"{status} "
                    f"({event}{condition_text})"
                )

            return "\n".join(lines)

        if action == "enable_automation":

            name = result.get(
                "name",
                "Automation",
            )

            return (
                f"{name} has been enabled."
            )

        if action == "disable_automation":

            name = result.get(
                "name",
                "Automation",
            )

            return (
                f"{name} has been disabled."
            )

        if action == "automation_status":

            name = result.get(
                "name",
                "Automation",
            )

            event = result.get(
                "event",
                "Unknown",
            )

            enabled = result.get(
                "enabled",
                False,
            )

            status = (
                "enabled"
                if enabled
                else "disabled"
            )

            return (
                f"{name} is currently {status}. "
                f"Event: {event}."
            )


        if action == "delete_automation":

            name = result.get(
                "name",
                "Automation",
            )

            if not name:
                name = "Automation"

            return (
                f"Automation '{name}' "
                "deleted successfully."
            )
        # -----------------------------------------------------
        # SECURITY EVENT HISTORY
        # -----------------------------------------------------

        if action == "get_recent_security_events":

            events = result.get(
                "events",
                [],
            )

            count = result.get(
                "count",
                len(events),
            )

            if not events:

                return (
                    "There are no recent security events."
                )

            lines = [
                f"I found {count} recent security event"
                f"{'s' if count != 1 else ''}:"
            ]

            for index, event in enumerate(
                events,
                start=1,
            ):

                source = event.get(
                    "source",
                    "unknown",
                )

                event_type = event.get(
                    "type",
                    "SECURITY_EVENT",
                )

                risk = event.get(
                    "risk",
                    "UNKNOWN",
                )

                reason = event.get(
                    "reason",
                    "",
                )

                lines.append(
                    f"{index}. "
                    f"Risk: {risk} | "
                    f"Source: {source} | "
                    f"Event: {event_type}"
                )

                if reason:
                    lines.append(
                        f"   Reason: {reason}"
                    )

            return "\n".join(lines)

        # -----------------------------------------------------
        # LATEST SECURITY EVENT
        # -----------------------------------------------------

        if action == "get_latest_security_event":

            event = result.get(
                "event"
            )

            if not event:

                return (
                    "There are no security events yet."
                )

            source = event.get(
                "source",
                "unknown",
            )

            event_type = event.get(
                "type",
                "SECURITY_EVENT",
            )

            risk = event.get(
                "risk",
                "UNKNOWN",
            )

            reason = event.get(
                "reason",
                "",
            )

            data = event.get(
                "data",
                {},
            )

            lines = [
                "Latest security event:",
                f"Risk: {risk}",
                f"Source: {source}",
                f"Event: {event_type}",
            ]

            if reason:
                lines.append(
                    f"Reason: {reason}"
                )

            if isinstance(data, dict):

                if data.get("process"):
                    lines.append(
                        f"Process: {data.get('process')}"
                    )

                if data.get("pid"):
                    lines.append(
                        f"PID: {data.get('pid')}"
                    )

                if data.get("remote_ip"):
                    lines.append(
                        f"Remote IP: {data.get('remote_ip')}"
                    )

                if data.get("remote_port"):
                    lines.append(
                        f"Remote Port: {data.get('remote_port')}"
                    )

                if data.get("name"):
                    lines.append(
                        f"Name: {data.get('name')}"
                    )

                if data.get("path"):
                    lines.append(
                        f"Path: {data.get('path')}"
                    )

            return "\n".join(lines)

        # -----------------------------------------------------
        # FILTERED SECURITY EVENTS
        # -----------------------------------------------------

        if action == "get_security_events":

            events = result.get(
                "events",
                [],
            )

            count = result.get(
                "count",
                len(events),
            )

            filters = result.get(
                "filters",
                {},
            )

            if not events:
                return "No security events matched the requested filter."

            filter_parts = []

            if filters.get("risk"):
                filter_parts.append(
                    f"risk {filters['risk']}"
                )

            if filters.get("source"):
                filter_parts.append(
                    f"source {filters['source']}"
                )

            if filters.get("event_type"):
                filter_parts.append(
                    f"type {filters['event_type']}"
                )

            if filter_parts:
                heading = (
                    "I found "
                    f"{count} security event"
                    f"{'s' if count != 1 else ''} "
                    "matching "
                    + ", ".join(filter_parts)
                    + ":"
                )
            else:
                heading = (
                    f"I found {count} security event"
                    f"{'s' if count != 1 else ''}:"
                )

            lines = [heading]

            for index, event in enumerate(
                events,
                start=1,
            ):

                lines.append(
                    f"{index}. "
                    f"Risk: {event.get('risk', 'UNKNOWN')} | "
                    f"Source: {event.get('source', 'unknown')} | "
                    f"Event: {event.get('type', 'SECURITY_EVENT')}"
                )

                reason = event.get(
                    "reason",
                    "",
                )

                if reason:
                    lines.append(
                        f"   Reason: {reason}"
                    )

            return "\n".join(lines)

        # -----------------------------------------------------
        # SECURITY SUMMARY
        # -----------------------------------------------------

        if action == "get_security_summary":

            total_events = result.get(
                "total_events",
                0,
            )

            risk_counts = result.get(
                "risk_counts",
                {},
            )

            source_counts = result.get(
                "source_counts",
                {},
            )

            lines = [
                "Security Summary:",
                f"Total events: {total_events}",
                f"LOW: {risk_counts.get('LOW', 0)}",
                f"MEDIUM: {risk_counts.get('MEDIUM', 0)}",
                f"HIGH: {risk_counts.get('HIGH', 0)}",
                f"CRITICAL: {risk_counts.get('CRITICAL', 0)}",
                "",
                "Sources:",
            ]

            if source_counts:

                for source, count in source_counts.items():

                    lines.append(
                        f"{source}: {count}"
                    )

            else:

                lines.append(
                    "No security events recorded."
                )

            return "\n".join(lines)

        # -----------------------------------------------------
        # WEB RESEARCH
        # -----------------------------------------------------

        if action == "web_research":

            # Web research contains useful information
            # that should be passed to Gemini for the
            # final natural-language response.
            return None
        # -----------------------------------------------------
        # GENERIC TOOL MESSAGE
        # -----------------------------------------------------

        message = result.get(
            "message"
        )

        if message:
            return str(message)

        return (
            f"{action} completed successfully."
            if action
            else "Task completed successfully."
        )

