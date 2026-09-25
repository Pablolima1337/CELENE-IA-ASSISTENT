import json
from pathlib import Path

MEMORY_PATH = Path(__file__).parent.parent / "data" / "memory.json"


def load_memory():
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    except:
        return {}


def save_memory(memory):
    with open(MEMORY_PATH, "w", encoding="utf-8") as file:
        json.dump(memory, file, indent=4, ensure_ascii=False)