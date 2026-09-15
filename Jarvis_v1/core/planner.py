
import json
import re
import inspect
import time


class Planner:

    def __init__(self, brain=None):
        self.brain = brain
        self.last_plan = []
        self.chat = None

        if self.brain:
            self.chat = self.brain.client.chats.create(
                model=self.brain.model,
                config={
                    "system_instruction": (
                        "You are the JARVIS task planner. "
                        "Return valid JSON only. "
                        "Never execute tools yourself."
                    ),
                },
            )

    # ---------------------------------------------------------
    # AVAILABLE TOOLS
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # TOOL CONTEXT
    # ---------------------------------------------------------

    def build_tool_context(self):

        tools = self.get_available_tools()

        if not tools:
            return (
                "No tools are currently available."
            )

        lines = []

        for tool in tools:

            lines.append(
                f"- {tool['name']}"
            )

            lines.append(
                f"  Signature: "
                f"{tool['signature']}"
            )

            lines.append(
                f"  Description: "
                f"{tool['description']}"
            )

        return "\n".join(lines)

    # ---------------------------------------------------------
    # CREATE PLAN
    # ---------------------------------------------------------

    def create_plan(self, user_input, context=None):

        if not user_input:
            return []

        user_input = str(
            user_input
        ).strip()

        if not user_input:
            return []

        if not self.chat:
            return self._conversation_fallback(
                user_input
            )

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

7. If one step depends on the result of a previous
   step, mark the dependency.

8. Use:
   "depends_on": []

   when the step has no dependency.

9. If step 2 depends on step 1, use:

   "depends_on": [1]

10. If step 3 depends on step 1 and step 2, use:

    "depends_on": [1, 2]

11. Avoid duplicate tool calls.

12. Do NOT call the same tool multiple times unless
    the user explicitly asks for repeated or fresh data.

13. Avoid collecting the same information with multiple
    tools.

14. IMPORTANT:

    "get_system_info" already provides:

    - CPU
    - RAM
    - Disk
    - Machine
    - Operating system

15. Therefore, when "get_system_info" is used,
    DO NOT separately call:

    - get_ram_info
    - get_cpu_info
    - get_disk_info

16. For a request such as:

    "give me a full system report"

    Prefer:

    Step 1:
    get_system_info

    Step 2:
    get_battery

    Do NOT create separate RAM, CPU, or disk steps.

17. For a RAM-only request, prefer:

    get_ram_info

18. For a CPU-only request, prefer:

    get_cpu_info

19. For a disk-only request, prefer:

    get_disk_info

20. Use the smallest number of tools necessary
    to complete the user's request.

21. If an earlier tool already provides information
    needed by a later step, do not call another tool
    just to collect the same information.

22. If no tool is required, use:

    "conversation"

23. Do not execute tools.

24. Return JSON only.

25. When actions must happen in a specific order,
    use depends_on to represent that order.

26. Do not add unnecessary dependencies to independent
    actions.

27. When a step needs information produced by a previous
    step, reference that previous result using:

    "{{step_1.result}}"

28. When a specific field from a previous result is needed,
    use the exact field path supported by that tool's result.

29. Only reference a previous step when that step is listed
    in "depends_on".

30. Do NOT invent values that should come from a previous
    step.

31. IMPORTANT RESULT STRUCTURE RULE:

    Always inspect the AVAILABLE JARVIS TOOLS descriptions
    and understand the expected result structure before
    creating a dependency reference.

32. If a previous tool returns an object containing a nested
    list, reference the list using its actual field name.

33. For example, web_research returns this structure:

    {{
        "success": true,
        "query": "AI",
        "result_count": 5,
        "results": [
            {{
                "rank": 1,
                "title": "Example article",
                "url": "https://example.com/article",
                "content": "Article summary",
                "score": 0.95
            }},
            {{
                "rank": 2,
                "title": "Another article",
                "url": "https://example.com/article-2",
                "content": "Another summary",
                "score": 0.90
            }}
        ]
    }}

34. Therefore, when accessing the first web research
    result, the correct path is:

    "{{step_1.result.results[0]}}"

35. When accessing the URL of the first web research
    result, the correct path is:

    "{{step_1.result.results[0].url}}"

36. NEVER use:

    "{{step_1.result[0]}}"

    or:

    "{{step_1.result[0].url}}"

    for web_research.

37. When the user asks:

    "research something and open the best article"

    use this pattern:

    Step 1:
    web_research

    Step 2:
    open_url

    Step 2 must depend on Step 1.

38. Example:

    User request:

    "research AI and open the best article"

    Correct plan:

    {{
        "goal": "Research AI and open the best article",
        "steps": [
            {{
                "step": 1,
                "action": "web_research",
                "description": "Research current information about AI",
                "arguments": {{
                    "query": "AI"
                }},
                "depends_on": []
            }},
            {{
                "step": 2,
                "action": "open_url",
                "description": "Open the first relevant article from the research results",
                "arguments": {{
                    "url": "{{{{step_1.result.results[0].url}}}}"
                }},
                "depends_on": [1]
            }}
        ]
    }}

39. When opening a URL returned by a research/search
    tool, use "open_url".

40. Do NOT use "open_browser" to open a specific
    research result.

41. "open_browser" is only for launching/checking a
    specific browser.

42. "open_url" is for opening a specific URL.

43. If the user asks to research/search AND then open
    an article/result, the research result URL must
    come from the previous tool result.

44. If the user asks to SEARCH AND TELL/EXPLAIN/RESEARCH/FIND
    INFORMATION, use "web_research".

    Do NOT use "google_search" for these requests.

45. If a research result contains multiple results and
    the user asks for the "best" article, use the first
    result only when the research tool's ranking/order
    represents relevance.

46. Do not reference a list index unless the previous
    tool result clearly contains that list and the index
    is valid.

47. If the user only asks to open Google or perform a Google
    search in the browser, use "google_search".

48. "web_research" returns actual structured web search
    results that JARVIS can inspect and use in later
    dependent steps.

49. Never use "google_search" when the user expects JARVIS
    to inspect search results and provide information.

50. Preserve important names, topics, phrases, and entities
    from the user's request when constructing the research query.

51. Do not unnecessarily shorten or alter a proper name or topic.

52. When a "web_research" step is followed by an action that
    needs a result from the research, the later step MUST use
    a dependency reference to the actual research result.

53. For example:

    "{{step_1.result.results[0].url}}"

    is valid for opening the first web research result.

54. Do NOT assume that "result" itself is a list.
    The "results" field contains the list.

55. ONLINE PERSON / NAME SEARCH:

    If the user asks to find information about a person's name,
    username, profile, social media account, professional identity,
    online presence, or anything that may exist on the internet,
    use web_research.

56. GITHUB USERNAME / PROFILE SEARCH:

    If the user asks whether a GitHub username/account/profile exists,
    prefer a GitHub-specific tool or direct GitHub profile URL check.

    Examples:
    - "github a tarekhossen71 account ache kina"
    - "check this github username"
    - "does this github profile exist"
    - "find this github account"

    Do NOT rely only on generic web_research when the request
    specifically targets GitHub.

    If a GitHub-specific tool is unavailable, construct the direct
    GitHub profile URL:

    https://github.com/<username>

    and use open_url or an appropriate web tool to verify it.

57. Examples of ONLINE/WEB research:

    - "Tarek Hossen Naeem er kichu thakle ber kore dao"
    - "tarekhossen71 name er kicu khuje dao"
    - "find Tarek Hossen Naeem"
    - "search this username online"
    - "find this person"
    - "find profiles for this name"

    These requests mean ONLINE/WEB research.

    Do NOT use file-search tools for these requests.

58. Only use file/folder search tools when the user explicitly
    refers to their computer, PC, laptop, local files, folders,
    documents, drives, or files stored on the machine.

    Examples:
    - "amar PC te tarekhossen71 file ta khuje dao"
    - "find this file on my computer"
    - "search my Downloads folder"

IMPORTANT EXAMPLE 1:

User request:

"open chrome and search youtube"

Correct plan:

{{
    "goal": "Open Chrome and search YouTube",
    "steps": [
        {{
            "step": 1,
            "action": "open_application",
            "description": "Open Chrome",
            "arguments": {{
                "app_name": "chrome"
            }},
            "depends_on": []
        }},
        {{
            "step": 2,
            "action": "google_search",
            "description": "Search YouTube",
            "arguments": {{
                "query": "YouTube"
            }},
            "depends_on": [1]
        }}
    ]
}}

IMPORTANT EXAMPLE 2:

User request:

"give me a full system report"

Correct plan:

{{
    "goal": "Get a complete system report",
    "steps": [
        {{
            "step": 1,
            "action": "get_system_info",
            "description": "Get complete CPU, RAM, disk, OS, and machine information",
            "arguments": {{}},
            "depends_on": []
        }},
        {{
            "step": 2,
            "action": "get_battery",
            "description": "Get current battery information",
            "arguments": {{}},
            "depends_on": [1]
        }}
    ]
}}

Incorrect plan:

get_system_info
get_ram_info
get_cpu_info
get_disk_info
get_battery

Do NOT create the incorrect plan because
get_system_info already contains RAM, CPU, and disk data.

IMPORTANT EXAMPLE 3:

User request:

"open chrome, search youtube, then take a screenshot"

Correct plan:

{{
    "goal": "Open Chrome, search YouTube, and take a screenshot",
    "steps": [
        {{
            "step": 1,
            "action": "open_application",
            "description": "Open Chrome",
            "arguments": {{
                "app_name": "chrome"
            }},
            "depends_on": []
        }},
        {{
            "step": 2,
            "action": "google_search",
            "description": "Search YouTube",
            "arguments": {{
                "query": "YouTube"
            }},
            "depends_on": [1]
        }},
        {{
            "step": 3,
            "action": "take_screenshot",
            "description": "Capture the current screen",
            "arguments": {{}},
            "depends_on": [2]
        }}
    ]
}}

IMPORTANT EXAMPLE 4:

User request:

"check my battery and RAM"

These are independent actions.

Correct plan:

{{
    "goal": "Check battery and RAM",
    "steps": [
        {{
            "step": 1,
            "action": "get_battery",
            "description": "Check battery status",
            "arguments": {{}},
            "depends_on": []
        }},
        {{
            "step": 2,
            "action": "get_ram_info",
            "description": "Check RAM usage",
            "arguments": {{}},
            "depends_on": []
        }}
    ]
}}

Do NOT add a dependency between these steps.

Return exactly this JSON structure:

{{
    "goal": "short description",
    "steps": [
        {{
            "step": 1,
            "action": "tool_name",
            "description": "what this step does",
            "arguments": {{}},
            "depends_on": []
        }}
    ]
}}
"""

        try:

            # -------------------------------------------------
            # GEMINI PLANNER RETRY
            # -------------------------------------------------

            max_attempts = 2
            response = None

            for attempt in range(max_attempts):

                try:

                    if self.brain:
                        self.brain.wait_for_rate_limit()

                    response = self.chat.send_message(
                        prompt
                    )

                    if response is None:
                        raise RuntimeError(
                            "Planner received no response."
                        )

                    break

                except Exception as e:

                    error_text = str(
                        e
                    ).lower()

                    is_temporary_error = (
                        "503" in error_text
                        or "unavailable" in error_text
                        or "high demand" in error_text
                        or "resource_exhausted" in error_text
                        or "429" in error_text
                    )

                    if (
                        is_temporary_error
                        and attempt < max_attempts - 1
                    ):

                        print(
                            "⚠️ Gemini planner temporarily "
                            "unavailable. Retrying..."
                        )

                        time.sleep(3)

                        continue

                    raise

            if response is None:
                raise RuntimeError(
                    "Planner did not receive a response."
                )

            text = (
                response.text.strip()
                if response.text
                else ""
            )

            # -------------------------------------------------
            # EMPTY RESPONSE
            # -------------------------------------------------

            if not text:
                raise ValueError(
                    "Planner returned an empty response."
                )

            # -------------------------------------------------
            # REMOVE MARKDOWN JSON WRAPPER
            # -------------------------------------------------

            if text.startswith("```"):

                text = re.sub(
                    r"^```(?:json)?\s*",
                    "",
                    text,
                    flags=re.IGNORECASE,
                )

                text = re.sub(
                    r"\s*```$",
                    "",
                    text,
                ).strip()

            # -------------------------------------------------
            # PARSE JSON
            # -------------------------------------------------

            plan_data = json.loads(
                text
            )

            if not isinstance(
                plan_data,
                dict,
            ):
                raise ValueError(
                    "Planner response must be a JSON object."
                )

            steps = plan_data.get(
                "steps",
                [],
            )

            if not isinstance(
                steps,
                list,
            ):
                raise ValueError(
                    "Planner 'steps' must be a list."
                )

            # -------------------------------------------------
            # AVAILABLE TOOL NAMES
            # -------------------------------------------------

            available_tools = {
                tool["name"]
                for tool in self.get_available_tools()
            }

            validated_steps = []

            # -------------------------------------------------
            # VALIDATE EACH STEP
            # -------------------------------------------------

            for index, step in enumerate(
                steps,
                start=1,
            ):

                if not isinstance(
                    step,
                    dict,
                ):
                    raise ValueError(
                        f"Planner step {index} "
                        "must be an object."
                    )

                action = step.get(
                    "action"
                )

                description = step.get(
                    "description",
                    "",
                )

                arguments = step.get(
                    "arguments",
                    {},
                )

                depends_on = step.get(
                    "depends_on",
                    [],
                )

                if not action:
                    raise ValueError(
                        f"Planner step {index} "
                        "has no action."
                    )

                # conversation is the only special
                # non-tool action.
                if (
                    action != "conversation"
                    and action not in available_tools
                ):
                    raise ValueError(
                        "Planner selected unavailable "
                        f"tool: {action}"
                    )

                if not isinstance(
                    arguments,
                    dict,
                ):
                    raise ValueError(
                        f"Planner step {index} "
                        "arguments must be an object."
                    )

                if not isinstance(
                    depends_on,
                    list,
                ):
                    raise ValueError(
                        f"Planner step {index} "
                        "depends_on must be a list."
                    )

                validated_steps.append(
                    {
                        "step": step.get(
                            "step",
                            index,
                        ),
                        "action": action,
                        "description": description,
                        "arguments": arguments,
                        "depends_on": depends_on,
                    }
                )

            # -------------------------------------------------
            # EMPTY PLAN
            # -------------------------------------------------

            if not validated_steps:

                validated_steps = [
                    {
                        "step": 1,
                        "action": "conversation",
                        "description": user_input,
                        "arguments": {},
                        "depends_on": [],
                    }
                ]

            self.last_plan = validated_steps

            return validated_steps

        except Exception as e:

            print(
                f"⚠️ Planner error: {e}"
            )

            return self._conversation_fallback(
                user_input
            )

    # ---------------------------------------------------------
    # CONVERSATION FALLBACK
    # ---------------------------------------------------------

    def _conversation_fallback(
        self,
        user_input,
    ):

        fallback = [
            {
                "step": 1,
                "action": "conversation",
                "description": user_input,
                "arguments": {},
                "depends_on": [],
            }
        ]

        self.last_plan = fallback

        return fallback

    # ---------------------------------------------------------
    # LAST PLAN
    # ---------------------------------------------------------

    def get_last_plan(self):

        return list(
            self.last_plan
        )

    # ---------------------------------------------------------
    # CLEAR PLAN
    # ---------------------------------------------------------

    def clear_plan(self):

        self.last_plan = []
