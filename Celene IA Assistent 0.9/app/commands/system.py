import os


def execute(message: str):
    command = message.lower().strip()

    if command == "limpar":
        os.system("cls")
        return "Terminal limpo."

    return None