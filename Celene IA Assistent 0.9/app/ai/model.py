from datetime import datetime

from ollama import Client

from app.core.tool_parser import ToolParser


class AIModel:
    def __init__(self, model_name: str = "celene"):
        self.model_name = model_name

        self.client = Client(
            host="http://127.0.0.1:11434",
            timeout=120.0
        )

    # ==================================================
    # CONTEXTO ATUAL DO SISTEMA
    # ==================================================

    def _get_system_context(self) -> str:
        now = datetime.now()

        return (
            "Contexto atual do sistema:\n"
            f"- Data atual: {now.strftime('%d/%m/%Y')}\n"
            f"- Hora atual: {now.strftime('%H:%M:%S')}\n"
            f"- Ano atual: {now.year}\n\n"
            "Use essas informações quando a pergunta "
            "depender da data ou hora atual."
        )

    # ==================================================
    # MONTA AS MENSAGENS
    # ==================================================

    def _build_messages(
        self,
        message: str,
        history=None
    ):
        messages = [
            {
                "role": "system",
                "content": self._get_system_context()
            }
        ]

        if history:
            for item in history:
                role = (
                    "assistant"
                    if item.author == "celene"
                    else "user"
                )

                messages.append({
                    "role": role,
                    "content": item.content
                })

        messages.append({
            "role": "user",
            "content": message
        })

        return messages

    # ==================================================
    # GERAÇÃO NORMAL
    # ==================================================

    def generate(
        self,
        message: str,
        history=None
    ) -> str:
        print(
            "[AI] Enviando mensagem "
            "para o Ollama..."
        )

        messages = self._build_messages(
            message=message,
            history=history
        )

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=messages
            )

            print(
                "[AI] Resposta recebida."
            )

            content = response[
                "message"
            ][
                "content"
            ]

            if not content:
                return (
                    "Não consegui gerar uma "
                    "resposta para isso."
                )

            return content

        except Exception as error:
            print(
                f"[AI] ERRO: {error}"
            )

            return (
                "Ocorreu um erro ao acessar "
                f"o modelo: {error}"
            )

    # ==================================================
    # STREAMING
    # ==================================================

    def stream_generate(
        self,
        message: str,
        history=None
    ):
        print(
            "[AI STREAM] Iniciando "
            "streaming..."
        )

        messages = self._build_messages(
            message=message,
            history=history
        )

        try:
            stream = self.client.chat(
                model=self.model_name,
                messages=messages,
                stream=True
            )

            for chunk in stream:
                content = chunk[
                    "message"
                ][
                    "content"
                ]

                if content:
                    yield content

            print(
                "[AI STREAM] Streaming "
                "finalizado."
            )

        except Exception as error:
            print(
                f"[AI STREAM] ERRO: {error}"
            )

            yield (
                "Ocorreu um erro durante "
                "a geração da resposta."
            )

    # ==================================================
    # DETECTOR INTELIGENTE DE FERRAMENTAS
    # ==================================================

    def detect_tool(
        self,
        message: str
    ) -> dict | None:
        print(
            "[AI] Analisando intenção..."
        )

        prompt = f"""
Analise a mensagem do usuário e determine
se é necessário usar uma ferramenta.

Ferramentas disponíveis:

WEATHER

Use "weather" para:
- clima
- previsão do tempo
- temperatura
- chuva
- vento
- condições meteorológicas

Formato:

{{
    "tool": "weather",
    "city": "Fortaleza",
    "state": "Ceará",
    "country_code": "BR",
    "period": "today"
}}

O campo "period" pode ser:

- "today"
- "tomorrow"
- "week"


CALCULATOR

Use "calculator" para cálculos matemáticos.

Formato:

{{
    "tool": "calculator",
    "expression": "928 * 74"
}}


SEM FERRAMENTA

Se nenhuma ferramenta for necessária:

{{
    "tool": null
}}


REGRAS:

- Retorne SOMENTE JSON válido.
- Não use markdown.
- Não explique sua decisão.
- Não escreva texto antes do JSON.
- Não escreva texto depois do JSON.
- Não invente ferramentas.

Mensagem:

{message}
"""

        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response[
                "message"
            ][
                "content"
            ]

            if not content:
                return None

            tool = ToolParser.parse(
                content
            )

            if tool is None:
                print(
                    "[AI] Não foi possível "
                    "interpretar a intenção."
                )

                return None

            tool_name = tool.get(
                "tool"
            )

            if tool_name:
                print(
                    "[AI] Ferramenta detectada: "
                    f"{tool_name}"
                )

                print(
                    f"[AI] Parâmetros: {tool}"
                )

            return tool

        except Exception as error:
            print(
                "[AI] Erro ao detectar "
                f"ferramenta: {error}"
            )

            return None