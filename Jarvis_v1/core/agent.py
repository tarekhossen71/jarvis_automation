from core.planner import Planner


class Agent:

    def __init__(self, brain):
        self.brain = brain
        self.planner = Planner(brain=brain)

    def run(self, user_input):

        if not user_input:
            return None

        # =====================================================
        # CREATE PLAN
        # =====================================================

        plan = self.planner.create_plan(user_input)

        if not plan:
            return "I could not create a plan for that request."

        # =====================================================
        # NORMAL CONVERSATION
        # =====================================================

        if (
            len(plan) == 1
            and plan[0].get("action") == "conversation"
        ):
            return self.brain.process(user_input)

        results = []

        # =====================================================
        # EXECUTE PLAN SEQUENTIALLY
        # =====================================================

        for step in plan:

            step_number = step.get(
                "step",
                len(results) + 1,
            )

            action = step.get("action")
            arguments = step.get(
                "arguments",
                {},
            )

            description = step.get(
                "description",
                action,
            )

            print(
                f"🧩 Agent step {step_number}: "
                f"{description}"
            )

            # -------------------------------------------------
            # CONVERSATION STEP
            # -------------------------------------------------

            if action == "conversation":

                result = self.brain.process(
                    description
                )

                results.append(
                    {
                        "step": step_number,
                        "action": action,
                        "success": True,
                        "result": result,
                    }
                )

                continue

            # -------------------------------------------------
            # CHECK TOOL
            # -------------------------------------------------

            tool = self.brain.tools.get(action)

            if not tool:

                error = (
                    f"Tool '{action}' does not exist."
                )

                print(f"❌ {error}")

                results.append(
                    {
                        "step": step_number,
                        "action": action,
                        "success": False,
                        "error": error,
                    }
                )

                break

            # -------------------------------------------------
            # EXECUTE TOOL
            # -------------------------------------------------

            try:

                result = self.brain.tools.execute(
                    action,
                    **arguments,
                )

            except Exception as e:

                result = {
                    "success": False,
                    "error": str(e),
                }

            # -------------------------------------------------
            # SAVE RESULT
            # -------------------------------------------------

            results.append(
                {
                    "step": step_number,
                    "action": action,
                    **result,
                }
            )

            # -------------------------------------------------
            # VERIFY RESULT
            # -------------------------------------------------

            if not result.get("success", False):

                print(
                    f"❌ Agent step {step_number} failed:"
                )

                print(
                    result.get(
                        "error",
                        result,
                    )
                )

                # IMPORTANT:
                # Stop immediately.
                # Do NOT execute next step.

                break

            print(
                f"✅ Agent step {step_number} completed."
            )

        # =====================================================
        # BUILD FINAL RESPONSE WITHOUT ANOTHER GEMINI CALL
        # =====================================================

        successful_steps = [
            item
            for item in results
            if item.get("success")
        ]

        failed_steps = [
            item
            for item in results
            if not item.get("success")
        ]

        # -----------------------------------------------------
        # ALL SUCCESSFUL
        # -----------------------------------------------------

        if (
            results
            and len(successful_steps) == len(results)
            and not failed_steps
        ):

            if len(results) == 1:

                result = results[0].get(
                    "result",
                    {},
                )

                if isinstance(result, dict):

                    message = result.get(
                        "message"
                    )

                    if message:
                        return message

                return (
                    f"Done. {description}"
                )

            return (
                f"Done. I completed all "
                f"{len(results)} steps successfully."
            )

        # -----------------------------------------------------
        # PARTIAL / FAILED
        # -----------------------------------------------------

        if failed_steps:

            failed = failed_steps[-1]

            error = failed.get(
                "error",
                "Unknown error.",
            )

            completed_count = len(
                successful_steps
            )

            return (
                f"I completed {completed_count} "
                f"step(s), but step "
                f"{failed.get('step')} failed: "
                f"{error}"
            )

        return (
            "I could not complete the requested task."
        )

    # =========================================================
    # PLAN HELPERS
    # =========================================================

    def get_plan(self, user_input):
        return self.planner.create_plan(
            user_input
        )

    def get_last_plan(self):
        return self.planner.get_last_plan()

    def clear_plan(self):
        self.planner.clear_plan()