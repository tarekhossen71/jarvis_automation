class ToolRegistry:
    """
    Central registry for JARVIS tools.
    """

    def __init__(self):
        self.tools = {}

    def register(self, name, description, function):
        self.tools[name] = {
            "name": name,
            "description": description,
            "function": function,
        }

    def get(self, name):
        return self.tools.get(name)

    def all(self):
        return list(self.tools.values())

    def get_functions(self):
        """
        Return all registered Python functions
        for Gemini automatic function calling.
        """

        return [
            tool["function"]
            for tool in self.tools.values()
        ]

    def execute(self, tool_name, **kwargs):

        tool = self.get(tool_name)

        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' does not exist.",
            }

        try:
            result = tool["function"](**kwargs)

            return {
                "success": True,
                "result": result,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }