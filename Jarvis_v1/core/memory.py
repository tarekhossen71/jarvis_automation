
import json
import os
import threading
from datetime import datetime


class MemoryManager:
    def __init__(self, memory_file="data/memory.json"):
        self.memory_file = memory_file
        self.lock = threading.Lock()
        self.data = {
            "user_memory": {},
            "conversation_history": [],
        }
        self._load()

    def _load(self):
        if not os.path.exists(self.memory_file):
            self._save()
            return

        try:
            with open(self.memory_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                self.data.update(data)

        except Exception:
            self.data = {
                "user_memory": {},
                "conversation_history": [],
            }
            self._save()

    def _save(self):
        temp_file = self.memory_file + ".tmp"

        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(
                self.data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        os.replace(temp_file, self.memory_file)

    # -----------------------------
    # User Memory
    # -----------------------------

    def remember(self, key, value):
        key = str(key).strip().lower()
        value = str(value).strip()

        if not key or not value:
            return False

        with self.lock:
            self.data["user_memory"][key] = {
                "value": value,
                "updated_at": datetime.now().isoformat(),
            }
            self._save()

        return True

    def recall(self, key):
        key = str(key).strip().lower()

        with self.lock:
            item = self.data["user_memory"].get(key)

        if not item:
            return None

        return item.get("value")

    def forget(self, key):
        key = str(key).strip().lower()

        with self.lock:
            if key not in self.data["user_memory"]:
                return False

            del self.data["user_memory"][key]
            self._save()

        return True

    def get_all_memory(self):
        with self.lock:
            return dict(self.data["user_memory"])

    def clear_memory(self):
        with self.lock:
            self.data["user_memory"] = {}
            self._save()

        return True

    # -----------------------------
    # Conversation History
    # -----------------------------

    def add_conversation(self, role, content):
        role = str(role).strip()
        content = str(content).strip()

        if not role or not content:
            return

        item = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        with self.lock:
            self.data["conversation_history"].append(item)

            # Keep only the latest 30 messages.
            self.data["conversation_history"] = (
                self.data["conversation_history"][-30:]
            )

            self._save()

    def get_conversation_history(self, limit=10):
        with self.lock:
            history = self.data["conversation_history"][-limit:]

        return list(history)

    def clear_conversation_history(self):
        with self.lock:
            self.data["conversation_history"] = []
            self._save()

        return True

    # -----------------------------
    # Context for Gemini
    # -----------------------------

    def build_memory_context(self):
        memory = self.get_all_memory()

        if not memory:
            return "No saved user memory."

        lines = []

        for key, item in memory.items():
            value = item.get("value", "")
            lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    def build_conversation_context(self, limit=10):
        history = self.get_conversation_history(limit)

        if not history:
            return "No previous conversation."

        lines = []

        for item in history:
            role = item.get("role", "unknown")
            content = item.get("content", "")

            if role == "user":
                label = "User"
            elif role == "assistant":
                label = "JARVIS"
            else:
                label = role.capitalize()

            lines.append(f"{label}: {content}")

        return "\n".join(lines)

    def build_context(self, conversation_limit=10):
        return (
            "SAVED USER MEMORY:\n"
            f"{self.build_memory_context()}\n\n"
            "RECENT CONVERSATION:\n"
            f"{self.build_conversation_context(conversation_limit)}"
        )
