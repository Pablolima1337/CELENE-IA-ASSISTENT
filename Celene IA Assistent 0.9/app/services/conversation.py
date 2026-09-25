import json
from datetime import datetime
from pathlib import Path

from app.core.message import Message


CONVERSATION_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "conversations.json"
)


class Conversation:
    def __init__(self):
        self.history = []

        self.load()

    def add(
        self,
        author: str,
        content: str,
        response_time: float | None = None
    ):
        message = Message(
            author=author,
            content=content,
            timestamp=datetime.now(),
            response_time=response_time
        )

        self.history.append(message)

        self.save()

    def get_history(self):
        return self.history

    def get_recent(self, limit: int = 10):
        return self.history[-limit:]

    def clear(self):
        self.history.clear()

        self.save()

    def save(self):
        data = []

        for message in self.history:
            data.append({
                "author": message.author,
                "content": message.content,
                "timestamp": message.timestamp.isoformat(),
                "response_time": message.response_time
            })

        with open(
            CONVERSATION_PATH,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

    def load(self):
        if not CONVERSATION_PATH.exists():
            return

        try:
            with open(
                CONVERSATION_PATH,
                "r",
                encoding="utf-8"
            ) as file:
                data = json.load(file)

            for item in data:
                message = Message(
                    author=item["author"],
                    content=item["content"],
                    timestamp=datetime.fromisoformat(
                        item["timestamp"]
                    ),
                    response_time=item.get(
                        "response_time"
                    )
                )

                self.history.append(message)

        except (
            json.JSONDecodeError,
            KeyError,
            ValueError
        ):
            self.history = []