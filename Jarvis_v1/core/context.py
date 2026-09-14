
class ContextManager:
    def __init__(self, memory_manager, max_messages=10):
        self.memory = memory_manager
        self.max_messages = max_messages

    def get_context(self):
        return self.memory.build_context(
            conversation_limit=self.max_messages
        )

    def save_user_message(self, message):
        self.memory.add_conversation(
            role="user",
            content=message,
        )

    def save_assistant_message(self, message):
        self.memory.add_conversation(
            role="assistant",
            content=message,
        )

    def remember(self, key, value):
        return self.memory.remember(key, value)

    def recall(self, key):
        return self.memory.recall(key)

    def forget(self, key):
        return self.memory.forget(key)

    def get_all_memory(self):
        return self.memory.get_all_memory()

    def clear_memory(self):
        return self.memory.clear_memory()

    def clear_conversation(self):
        return self.memory.clear_conversation_history()
