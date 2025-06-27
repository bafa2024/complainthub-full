from typing import Dict

class ConversationManager:
    def __init__(self):
        self.sessions: Dict[str, list] = {}

    def add_message(self, user_id: str, message: str):
        self.sessions.setdefault(user_id, []).append(message)

    def get_history(self, user_id: str):
        return self.sessions.get(user_id, [])
