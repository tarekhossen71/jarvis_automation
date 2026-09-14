import json
import re
import inspect


class Planner:

    def __init__(self, brain=None):
        self.brain = brain
        self.last_plan = []

    # =========================================================
    # GET AVAILABLE TOOLS
    # =========================================================

    def get_available_tools(self):

        if not self.brain:
            return []

        tools = self.brain.tools.all()

        available = []

        for tool in tools:

            function = tool.get("function")

            try:
                signature = str(
                    inspect.signature(function)
                )
            except Exception:
                signature = "(...)"

            available.append(
                {
                    "name": tool.get("name"),
                    "description": tool.get(
                        "description",
                        "",
                    ),
                    "signature": signature,
                }
            )

        return available

    # =========================================================
    # BUILD TOOL CONTEXT
    # =========================================================

    def build_tool_context(self):

        tools = self.get_available_tools()

        if not tools:
            return "No tools are currently available."

        lines = []

        for tool in tools:

            lines.append(
                f"- {tool['name']}"
            )

            lines.append(
                f"  Signature: {tool['signature']}"
            )

            lines.append(
                f"  Description: {tool['description']}"
            )

        return "\n".join(lines)

    # =========================================================
    # CREATE PLAN
    # =========================================================

    def create_plan(self, user_input):

        if not user_input:
            return []

        user_input = str(
            user_input
        ).strip()

        if not user_input:
            return []

        tool_context = (
            self.build_tool_context()
        )

        prompt = f"""
You are the task planner for JARVIS.

Convert the user's request into small,
executable steps.

AVAILABLE JARVIS TOOLS:

{tool_context}

USER REQUEST:

{user_input}

PLANNING RULES:

1. Break multi-action requests into separate steps.

2. Each step must perform ONE clear action.

3. Use ONLY tools from the AVAILABLE JARVIS TOOLS list.

4. NEVER invent a tool name.

5. NEVER invent argument names.

6. The "arguments" object MUST use the EXACT
   parameter names shown in the tool Signature.

7. Example:

If the tool signature is:

open_application(app_name: str, arguments: str = "")

then the correct arguments are:

{{
    "app_name": "chrome"
}}

NOT:

{{
    "application_name": "chrome"
}}

8. If no tool is required, use:
"conversation"

9. Do not execute tools.

10. Return JSON only.

Return exactly:

{{
    "goal": "short description",
    "steps": [
        {{
            "step": 1,
            "action": "tool_name",
            "description": "what this step does",
            "arguments": {{}}
        }}
    ]
}}
"""

        try:

            response = (
                self.brain.client.models.generate_content(
                    model=self.brain.model,
                    contents=prompt,
                )
            )

            text = response.text.strip()

            # -------------------------------------------------
            # Remove markdown code fences
            # -------------------------------------------------

            text = re.sub(
                r"^```json\s*",
                "",
                text,
                flags=re.IGNORECASE,
            )

            text = re.sub(
                r"^```\s*",
                "",
                text,
            )

            text = re.sub(
                r"\s*```$",
                "",
                text,
            )

            plan_data = json.loads(text)

            steps = plan_data.get(
                "steps",
                [],
            )

            if not isinstance(
                steps,
                list,
            ):
                raise ValueError(
                    "Planner returned invalid steps."
                )

            # -------------------------------------------------
            # VALID TOOL NAMES
            # -------------------------------------------------

            valid_tools = {
                tool["name"]
                for tool in self.get_available_tools()
            }

            validated_steps = []

            # -------------------------------------------------
            # VALIDATE STEPS
            # -------------------------------------------------

            for step in steps:

                action = step.get(
                    "action"
                )

                if not action:
                    continue

                if (
                    action != "conversation"
                    and action not in valid_tools
                ):

                    print(
                        f"⚠️ Planner generated "
                        f"unknown tool: {action}"
                    )

                    continue

                arguments = step.get(
                    "arguments",
                    {},
                )

                if not isinstance(
                    arguments,
                    dict,
                ):
                    arguments = {}

                validated_steps.append(
                    {
                        "step": step.get(
                            "step",
                            len(
                                validated_steps
                            ) + 1,
                        ),
                        "action": action,
                        "description": step.get(
                            "description",
                            "",
                        ),
                        "arguments": arguments,
                    }
                )

            # -------------------------------------------------
            # SAVE PLAN
            # -------------------------------------------------

            if validated_steps:

                self.last_plan = (
                    validated_steps
                )

                return validated_steps

        except Exception as e:

            print(
                f"⚠️ Planner error: {e}"
            )

        # =====================================================
        # FALLBACK
        # =====================================================

        fallback = [
            {
                "step": 1,
                "action": "conversation",
                "description": user_input,
                "arguments": {},
            }
        ]

        self.last_plan = fallback

        return fallback

    # =========================================================
    # PLAN HELPERS
    # =========================================================

    def get_last_plan(self):
        return list(
            self.last_plan
        )

    def clear_plan(self):
        self.last_plan = []