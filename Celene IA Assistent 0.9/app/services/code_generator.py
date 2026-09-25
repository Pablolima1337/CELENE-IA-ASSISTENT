import json


class CodeGenerator:
    def __init__(self, ai_model):
        self.ai = ai_model

    # ==================================================
    # GERAÇÃO
    # ==================================================

    def generate(
        self,
        request: str,
        history=None
    ):
        print(
            "[CODE] Preparando geração..."
        )

        messages = []

        # ==============================================
        # CONTEXTO DO SISTEMA
        # ==============================================

        if hasattr(
            self.ai,
            "_get_system_context"
        ):
            messages.append({
                "role": "system",
                "content":
                    self.ai._get_system_context()
            })

        # ==============================================
        # INSTRUÇÕES DO CODE MODE
        # ==============================================

        messages.append({
            "role": "system",
            "content": """
Você é o módulo de geração de código da Celene.

Sua tarefa é gerar código solicitado pelo usuário.

Responda obrigatoriamente usando um objeto JSON.

Campos obrigatórios:

title
language
filename
description
code

Exemplo da estrutura:

{
    "title": "Calculadora de média",
    "language": "python",
    "filename": "media.py",
    "description": "Calcula a média de uma lista de números.",
    "code": "def calcular_media(valores):\\n    return sum(valores) / len(valores)"
}

Regras:

- Gere código funcional.
- Não use blocos Markdown.
- Não coloque ``` no código.
- language deve estar em letras minúsculas.
- filename deve possuir uma extensão adequada.
- description deve ser curta.
- code deve conter apenas o código.
- Não explique nada fora do JSON.
"""
        })

        # ==============================================
        # HISTÓRICO CURTO
        # ==============================================

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

        # ==============================================
        # PEDIDO ATUAL
        # ==============================================

        messages.append({
            "role": "user",
            "content": request
        })

        # ==============================================
        # OLLAMA
        # ==============================================

        try:
            print(
                "[CODE] Enviando para o Ollama..."
            )

            response = (
                self.ai.client.chat(
                    model=self.ai.model_name,
                    messages=messages,

                    # Força saída JSON
                    format="json",

                    options={
                        "temperature": 0.2
                    }
                )
            )

            content = (
                response[
                    "message"
                ][
                    "content"
                ]
            )

            print(
                "[CODE] Resposta recebida."
            )

            print(
                "[CODE] RAW:"
            )

            print(content)

            return self._parse_response(
                content
            )

        except Exception as error:
            print(
                "[CODE] Erro durante geração:"
            )

            print(error)

            return None

    # ==================================================
    # PARSER
    # ==================================================

    def _parse_response(
        self,
        content: str
    ):
        if not content:
            print(
                "[CODE] Resposta vazia."
            )

            return None

        try:
            data = json.loads(
                content
            )

        except json.JSONDecodeError as error:
            print(
                "[CODE] JSON inválido:"
            )

            print(error)

            print(
                "[CODE] Conteúdo recebido:"
            )

            print(content)

            return None

        # ==============================================
        # VALIDA CODE
        # ==============================================

        code = data.get(
            "code"
        )

        if not code:
            print(
                "[CODE] Campo 'code' ausente."
            )

            return None

        # ==============================================
        # LANGUAGE
        # ==============================================

        language = str(
            data.get(
                "language",
                "text"
            )
        ).lower().strip()

        # ==============================================
        # FILENAME
        # ==============================================

        filename = data.get(
            "filename"
        )

        if not filename:
            filename = (
                self._default_filename(
                    language
                )
            )

        # ==============================================
        # RESULTADO
        # ==============================================

        result = {
            "title": str(
                data.get(
                    "title",
                    "Código gerado"
                )
            ),

            "language":
                language,

            "filename":
                str(filename),

            "description":
                str(
                    data.get(
                        "description",
                        "Código gerado pela Celene."
                    )
                ),

            "code":
                str(code)
        }

        print(
            "[CODE] Código interpretado "
            "com sucesso."
        )

        return result

    # ==================================================
    # EXTENSÕES
    # ==================================================

    def _default_filename(
        self,
        language: str
    ):
        filenames = {
            "python":
                "codigo.py",

            "javascript":
                "codigo.js",

            "typescript":
                "codigo.ts",

            "html":
                "index.html",

            "css":
                "style.css",

            "php":
                "codigo.php",

            "java":
                "Main.java",

            "c":
                "main.c",

            "c++":
                "main.cpp",

            "cpp":
                "main.cpp",

            "c#":
                "Program.cs",

            "csharp":
                "Program.cs",

            "go":
                "main.go",

            "rust":
                "main.rs",

            "sql":
                "query.sql",

            "json":
                "data.json",

            "bash":
                "script.sh",

            "powershell":
                "script.ps1",
        }

        return filenames.get(
            language,
            "codigo.txt"
        )