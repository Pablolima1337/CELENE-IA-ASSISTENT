from datetime import datetime

from app.core.brain import Brain
from app.services.memory import load_memory, save_memory


def current_time():
    return datetime.now().strftime("%H:%M:%S")


def main():
    memory = load_memory()

    brain = Brain(memory)

    print("=" * 50)
    print("                 Celene v0.3")
    print("=" * 50)

    while True:
        user = input(f"\n[{current_time()}] Você: ")

        if user.lower() == "sair":
            save_memory(memory)

            print(
                f"\n[{current_time()}] "
                "Celene: Até logo!"
            )

            break

        response, response_time = brain.think(user)

        print(
            f"\n[{current_time()}] Celene "
            f"({response_time:.2f}s): {response}"
        )


if __name__ == "__main__":
    main()