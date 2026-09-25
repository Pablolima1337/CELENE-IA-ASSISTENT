from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent

PROMPT_PATH = ROOT / "prompts" / "system_prompt.txt"


def load_personality():
    with open(PROMPT_PATH, "r", encoding="utf-8") as file:
        return file.read()