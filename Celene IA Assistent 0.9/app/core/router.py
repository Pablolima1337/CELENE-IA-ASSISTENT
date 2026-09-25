from app.commands.system import execute


class Router:
    def __init__(self, memory):
        self.memory = memory

    def route(self, message: str):
        command = execute(message)

        if command:
            return command

        msg = message.lower().strip()

        if msg.startswith("meu nome é"):
            name = message[len("meu nome é"):].strip()

            if not name:
                return "Você esqueceu de me dizer seu nome."

            self.memory["nome"] = name

            return f"Prazer em conhecer você, {name}!"

        if "qual meu nome" in msg:
            name = self.memory.get("nome")

            if name:
                return f"Seu nome é {name}."

            return "Você ainda não me contou seu nome."

        return None