import re


class ToolDetector:

    # ==================================================
    # PALAVRAS-CHAVE
    # ==================================================

    WEATHER_KEYWORDS = [
        "clima",
        "tempo",
        "previsão",
        "previsao",
        "chuva",
        "chover",
        "temperatura",
        "vento",
        "meteorológico",
        "meteorologico",
    ]


    CODE_KEYWORDS = [
        # Código
        "crie um código",
        "crie um codigo",
        "cria um código",
        "cria um codigo",

        "faça um código",
        "faça um codigo",
        "faz um código",
        "faz um codigo",

        "gere um código",
        "gere um codigo",
        "gera um código",
        "gera um codigo",

        "escreva um código",
        "escreva um codigo",

        "desenvolva um código",
        "desenvolva um codigo",

        # Funções
        "crie uma função",
        "crie uma funcao",
        "cria uma função",
        "cria uma funcao",

        "faça uma função",
        "faça uma funcao",

        "gere uma função",
        "gere uma funcao",

        # Scripts
        "crie um script",
        "cria um script",

        "faça um script",
        "faz um script",

        "gere um script",
        "gera um script",

        "escreva um script",

        # Programas
        "crie um programa",
        "cria um programa",

        "faça um programa",
        "faz um programa",

        "desenvolva um programa",

        # Linguagens
        "código em python",
        "codigo em python",
        "programa em python",
        "script em python",

        "código javascript",
        "codigo javascript",
        "código em javascript",
        "codigo em javascript",

        "código typescript",
        "codigo typescript",

        "código html",
        "codigo html",

        "código css",
        "codigo css",

        "código php",
        "codigo php",

        "código java",
        "codigo java",

        "código c++",
        "codigo c++",

        "código c#",
        "codigo c#",

        "código sql",
        "codigo sql",
    ]


    # ==================================================
    # DETECTOR PRINCIPAL
    # ==================================================

    @staticmethod
    def detect(
        message: str
    ):
        if not message:
            return None

        text = (
            message
            .lower()
            .strip()
        )


        # ==============================================
        # WEATHER
        # ==============================================

        if any(
            keyword in text
            for keyword
            in ToolDetector.WEATHER_KEYWORDS
        ):
            return ToolDetector._detect_weather(
                message
            )


        # ==============================================
        # CALCULATOR
        # ==============================================

        calculator = (
            ToolDetector
            ._detect_calculator(
                message
            )
        )

        if calculator:
            return calculator


        # ==============================================
        # CODE
        # ==============================================

        if any(
            keyword in text
            for keyword
            in ToolDetector.CODE_KEYWORDS
        ):
            return {
                "tool": "code",
                "request": message
            }


        # ==============================================
        # NENHUMA TOOL
        # ==============================================

        return None


    # ==================================================
    # WEATHER
    # ==================================================

    @staticmethod
    def _detect_weather(
        message: str
    ):
        text = (
            message
            .lower()
        )


        # ==============================================
        # PERÍODO
        # ==============================================

        period = "today"


        if any(
            word in text
            for word in [
                "amanhã",
                "amanha"
            ]
        ):
            period = "tomorrow"


        elif any(
            word in text
            for word in [
                "semana",
                "próximos dias",
                "proximos dias",
                "7 dias",
                "sete dias"
            ]
        ):
            period = "week"


        # ==============================================
        # LOCALIZAÇÃO
        # ==============================================

        city = None
        state = None
        country_code = "BR"


        state_codes = {
            "AC",
            "AL",
            "AP",
            "AM",
            "BA",
            "CE",
            "DF",
            "ES",
            "GO",
            "MA",
            "MT",
            "MS",
            "MG",
            "PA",
            "PB",
            "PR",
            "PE",
            "PI",
            "RJ",
            "RN",
            "RS",
            "RO",
            "RR",
            "SC",
            "SP",
            "SE",
            "TO"
        }


        # ==============================================
        # PADRÃO:
        #
        # Horizonte CE
        # Fortaleza CE Brasil
        # Horizonte - CE
        # ==============================================

        cleaned = re.sub(
            r"[,\-]",
            " ",
            message
        )

        words = cleaned.split()


        state_index = None


        for index, word in enumerate(
            words
        ):
            if (
                word.upper()
                in state_codes
            ):
                state = (
                    word.upper()
                )

                state_index = index

                break


        if state_index is not None:

            ignored_words = {
                "qual",
                "é",
                "e",
                "a",
                "o",
                "previsão",
                "previsao",
                "do",
                "tempo",
                "clima",
                "para",
                "em",
                "de",
                "hoje",
                "amanhã",
                "amanha",
                "na",
                "no",
                "cidade",
            }


            possible_city = []


            for word in words[
                :state_index
            ]:
                if (
                    word.lower()
                    not in ignored_words
                ):
                    possible_city.append(
                        word
                    )


            if possible_city:
                city = (
                    possible_city[-1]
                )


        return {
            "tool": "weather",
            "city": city,
            "state": state,
            "country_code": country_code,
            "period": period
        }


    # ==================================================
    # CALCULATOR
    # ==================================================

    @staticmethod
    def _detect_calculator(
        message: str
    ):
        text = (
            message
            .lower()
            .strip()
        )


        # ==============================================
        # NORMALIZA SÍMBOLOS
        # ==============================================

        normalized = (
            text
            .replace("×", "*")
            .replace("÷", "/")
        )


        # ==============================================
        # EXPRESSÕES DIRETAS
        #
        # 10 + 20
        # 5 * 8
        # 100 / 4
        # ==============================================

        pattern = (
            r"(?<!\w)"
            r"(-?\d+(?:[.,]\d+)?)"
            r"\s*"
            r"([\+\-\*\/])"
            r"\s*"
            r"(-?\d+(?:[.,]\d+)?)"
        )


        match = re.search(
            pattern,
            normalized
        )


        if match:
            left = (
                match
                .group(1)
                .replace(
                    ",",
                    "."
                )
            )

            operator = (
                match.group(2)
            )

            right = (
                match
                .group(3)
                .replace(
                    ",",
                    "."
                )
            )


            expression = (
                f"{left} "
                f"{operator} "
                f"{right}"
            )


            return {
                "tool":
                    "calculator",

                "expression":
                    expression
            }


        # ==============================================
        # FRASES
        #
        # quanto é 20 mais 30
        # calcule 50 dividido por 2
        # ==============================================

        word_operations = [
            (
                r"(-?\d+(?:[.,]\d+)?)"
                r"\s+mais\s+"
                r"(-?\d+(?:[.,]\d+)?)",
                "+"
            ),

            (
                r"(-?\d+(?:[.,]\d+)?)"
                r"\s+menos\s+"
                r"(-?\d+(?:[.,]\d+)?)",
                "-"
            ),

            (
                r"(-?\d+(?:[.,]\d+)?)"
                r"\s+vezes\s+"
                r"(-?\d+(?:[.,]\d+)?)",
                "*"
            ),

            (
                r"(-?\d+(?:[.,]\d+)?)"
                r"\s+multiplicado por\s+"
                r"(-?\d+(?:[.,]\d+)?)",
                "*"
            ),

            (
                r"(-?\d+(?:[.,]\d+)?)"
                r"\s+dividido por\s+"
                r"(-?\d+(?:[.,]\d+)?)",
                "/"
            ),
        ]


        for pattern, operator in (
            word_operations
        ):
            match = re.search(
                pattern,
                normalized
            )


            if not match:
                continue


            left = (
                match
                .group(1)
                .replace(
                    ",",
                    "."
                )
            )

            right = (
                match
                .group(2)
                .replace(
                    ",",
                    "."
                )
            )


            return {
                "tool":
                    "calculator",

                "expression": (
                    f"{left} "
                    f"{operator} "
                    f"{right}"
                )
            }


        return None