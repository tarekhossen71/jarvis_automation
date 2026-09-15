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
    # DIRECT TOOLS
    # =========================================================

    # =========================================================
    # DIRECT / LOCAL TOOLS
    # =========================================================

    def try_direct_tool(self, user_input):

        import re

        text = user_input.lower().strip()

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

        disk_keywords = (
            "disk usage",
            "disk status",
            "disk space",
            "free disk space",
            "hard disk usage",
            "storage usage",
            "storage status",
        )

        if any(
            keyword in text
            for keyword in disk_keywords
        ):
            return (
                "get_disk_info",
                {},
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
        #
        # Examples:
        #
        # open chrome
        # open whatsapp
        # open notepad
        # open calculator
        #
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
        #
        # Examples:
        #
        # close chrome
        # close whatsapp
        # close explorer
        #
        # Confirmation will still be handled by
        # the existing confirmation system.
        #
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

            free = data.get(
                "free_gb"
            )

            total = data.get(
                "total_gb"
            )

            used = data.get(
                "used_gb"
            )

            percent = data.get(
                "usage_percent"
            )

            if free is not None:

                return (
                    f"You have {free} GB of free "
                    f"space on the {drive} drive. "
                    f"It is using {used} GB out of "
                    f"{total} GB ({percent}% used)."
                )

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