from pathlib import Path


ROOT = Path(__file__).parent.parent.parent

DATA = ROOT / "data"

PROMPTS = ROOT / "prompts"

MEMORY = DATA / "memory.json"

CONVERSATIONS = DATA / "conversations.json"

SYSTEM_PROMPT = PROMPTS / "system_prompt.txt"