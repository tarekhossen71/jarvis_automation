import requests


class OfflineBrain:

    def __init__(
        self,
        model="llama3.2:3b",
        base_url="http://127.0.0.1:11434",
        system_prompt=None,
    ):

        self.model = model
        self.base_url = base_url.rstrip("/")

        self.system_prompt = (
            system_prompt
            or
            """
You are JARVIS, a local offline AI assistant.

User name: Tarek.

Rules:
1. Reply in English or Banglish only.
2. Never use Bangla script.
3. Be concise and natural.
4. Do not invent information.
5. If you do not know something, say so clearly.
"""
        )

    # ==================================================
    # CHECK OLLAMA
    # ==================================================

    def is_available(self):

        try:

            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=3,
            )

            return response.status_code == 200

        except Exception:

            return False

    # ==================================================
    # ASK OLLAMA
    # ==================================================

    def ask(
        self,
        user_input,
        context="",
    ):

        if not user_input:
            return None

        prompt = ""

        if context:
            prompt += (
                "CONVERSATION CONTEXT:\n"
                f"{context}\n\n"
            )

        prompt += (
            "CURRENT USER MESSAGE:\n"
            f"{user_input}"
        )

        payload = {
            "model": self.model,
            "system": self.system_prompt,
            "prompt": prompt,
            "stream": False,
        }

        try:

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120,
            )

            response.raise_for_status()

            data = response.json()

            answer = data.get(
                "response",
                "",
            )

            if not answer:

                return (
                    "Offline brain returned an empty response."
                )

            return answer.strip()

        except requests.exceptions.ConnectionError:

            return (
                "Offline brain is unavailable. "
                "Please make sure Ollama is running."
            )

        except requests.exceptions.Timeout:

            return (
                "Offline brain took too long to respond."
            )

        except Exception as e:

            return (
                "Offline brain error: "
                f"{e}"
            )

    # ==================================================
    # PROCESS
    # ==================================================

    def process(
        self,
        user_input,
        context="",
    ):

        return self.ask(
            user_input=user_input,
            context=context,
        )

    # ==================================================
    # PROCESS TOOL RESULTS
    # ==================================================

    def process_tool_results(
        self,
        user_input,
        tool_results,
    ):

        if not tool_results:

            return (
                "I could not get any tool results."
            )

        prompt = f"""
            The user asked:

            {user_input}

            JARVIS executed the required actions.

            REAL TOOL RESULTS:

            {tool_results}

            Now answer the user's original question.

            Rules:

            1. Use ONLY the information in the tool results.
            2. Never invent values.
            3. Clearly provide the actual result.
            4. If the result contains news or research results, summarize
            the useful information naturally.
            5. If the result contains RAM information, mention RAM usage.
            6. If the result contains CPU information, mention CPU usage.
            7. If the result contains disk information, mention disk usage.
            8. If the result contains battery information, mention battery status.
            9. For browser/application/file actions, clearly tell the user
            what was completed.
            10. Keep the answer concise and natural.
            11. Reply in English or Banglish only.
            12. Never use Bangla script.
            13. Do not mention internal tool names unless necessary.
            14. Do not say "I executed a tool".
            """

        return self.ask(
            user_input=prompt,
        )