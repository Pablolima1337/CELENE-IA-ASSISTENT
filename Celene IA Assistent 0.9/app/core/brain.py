from time import perf_counter

from app.ai.model import AIModel
from app.commands.calculator import Calculator
from app.commands.weather import Weather
from app.core.router import Router
from app.core.tool_detector import ToolDetector
from app.core.tool_registry import ToolRegistry
from app.services.code_generator import CodeGenerator
from app.services.conversation import Conversation


class Brain:
    def __init__(self, memory):
        self.memory = memory

        self.router = Router(memory)
        self.conversation = Conversation()
        self.ai = AIModel()

        # ==========================================
        # TOOL REGISTRY
        # ==========================================

        self.tools = ToolRegistry()

        # ==========================================
        # FERRAMENTAS
        # ==========================================

        self.weather = Weather()
        self.calculator = Calculator()
        self.code_generator = CodeGenerator(
            self.ai
        )

        # ==========================================
        # CONTEXTO DAS FERRAMENTAS
        # ==========================================

        self.pending_tool = None
        self.last_tool = None

        # ==========================================
        # REGISTRO DAS FERRAMENTAS
        # ==========================================

        self.tools.register(
            "weather",
            self.weather.get_forecast
        )

        self.tools.register(
            "calculator",
            self.calculator.calculate
        )

    # ==================================================
    # THINK
    # ==================================================

    def think(self, message: str):
        history = self.conversation.get_recent(
            limit=6
        )

        start = perf_counter()

        response = None

        # ==============================================
        # FERRAMENTA PENDENTE
        # ==============================================

        if self.pending_tool == "weather":
            response = self.handle_pending_weather(
                message
            )

        # ==============================================
        # CONTINUAÇÃO DE CLIMA
        # ==============================================

        if (
            response is None
            and self.last_tool == "weather"
            and self.looks_like_location(message)
        ):
            city, state, country_code = (
                self.parse_location(message)
            )

            if city:
                print(
                    "[WEATHER] Continuação detectada: "
                    f"{city}, {state}"
                )

                response = self.handle_weather(
                    message=message,
                    tool={
                        "tool": "weather",
                        "city": city,
                        "state": state,
                        "country_code": country_code,
                        "period": "today"
                    }
                )

        # ==============================================
        # ROUTER
        # ==============================================

        if response is None:
            response = self.router.route(
                message
            )

        # ==============================================
        # TOOL DETECTOR
        # ==============================================

        if response is None:
            tool = ToolDetector.detect(
                message
            )

            if tool:
                response = self.handle_tool(
                    message=message,
                    tool=tool
                )

            else:
                response = self.ai.generate(
                    message=message,
                    history=history
                )

        # ==============================================
        # TEMPO
        # ==============================================

        response_time = (
            perf_counter()
            - start
        )

        # ==============================================
        # GARANTIA
        # ==============================================

        if response is None:
            response = (
                "Não consegui processar "
                "sua solicitação."
            )

        # ==============================================
        # RESPOSTA ESTRUTURADA
        # ==============================================

        if isinstance(response, dict):
            result = response

            result["response_time"] = round(
                response_time,
                2
            )

        else:
            result = {
                "type": "text",
                "response": response,
                "data": None,
                "response_time": round(
                    response_time,
                    2
                )
            }

        # ==============================================
        # HISTÓRICO
        # ==============================================

        self.conversation.add(
            author="user",
            content=message
        )

        self.conversation.add(
            author="celene",
            content=result["response"],
            response_time=response_time
        )

        return result

    # ==================================================
    # TOOL HANDLER
    # ==================================================

    def handle_tool(
        self,
        message: str,
        tool: dict
    ):
        tool_name = tool.get(
            "tool"
        )

        if not tool_name:
            return None

        if (
                tool_name != "code"
                and not self.tools.exists(
                tool_name
                )
            ):
            return {
                "type": "text",
                "response": (
                    f"A ferramenta "
                    f"'{tool_name}' "
                    "ainda não está disponível."
                ),
                "data": None
            }

        # ==============================================
        # CALCULATOR
        # ==============================================

        if tool_name == "calculator":
            expression = tool.get(
                "expression"
            )

            if not expression:
                return {
                    "type": "text",
                    "response": (
                        "Não consegui identificar "
                        "o cálculo."
                    ),
                    "data": None
                }

            print(
                "[CALCULATOR] Calculando: "
                f"{expression}"
            )

            calc_result = (
                self.tools.execute(
                    "calculator",
                    expression=expression
                )
            )

            if calc_result is None:
                return {
                    "type": "text",
                    "response": (
                        "Não consegui realizar "
                        "esse cálculo."
                    ),
                    "data": None
                }

            self.last_tool = (
                "calculator"
            )

            return {
                "type": "calculator",

                "response": str(
                    calc_result
                ),

                "data": {
                    "expression":
                        expression,

                    "result":
                        calc_result
                }
            }

        # ==============================================
        # WEATHER
        # ==============================================

        if tool_name == "weather":
            return self.handle_weather(
                message=message,
                tool=tool
            )

        # ==============================================
        # CODE
        # ==============================================

        if tool_name == "code":
            request = tool.get(
                "request",
                message
            )

            print(
                "[CODE] Gerando código..."
            )

            history = (
                self.conversation
                .get_recent(
                    limit=4
                )
            )

            code_result = (
                self.code_generator
                .generate(
                    request=request,
                    history=history
                )
            )

            if not code_result:
                return {
                    "type": "text",

                    "response": (
                        "Não consegui gerar "
                        "esse código."
                    ),

                    "data": None
                }

            self.last_tool = "code"

            description = (
                code_result.get(
                    "description"
                )
                or
                "Código gerado com sucesso."
            )

            return {
                "type": "code",

                "response": description,

                "data": {
                    "title":
                        code_result.get(
                            "title",
                            "Código gerado"
                        ),

                    "language":
                        code_result.get(
                            "language",
                            "text"
                        ),

                    "filename":
                        code_result.get(
                            "filename",
                            "codigo.txt"
                        ),

                    "description":
                        description,

                    "code":
                        code_result[
                            "code"
                        ]
                }
            }

        return {
            "type": "text",

            "response": (
                "Não consegui executar "
                "essa ferramenta."
            ),

            "data": None
        }

    # ==================================================
    # WEATHER
    # ==================================================

    def handle_weather(
        self,
        message: str,
        tool: dict
    ):
        city = tool.get(
            "city"
        )

        state = tool.get(
            "state"
        )

        country_code = tool.get(
            "country_code",
            "BR"
        )

        period = tool.get(
            "period",
            "today"
        )

        # ==============================================
        # SEM CIDADE
        # ==============================================

        if not city:
            self.pending_tool = (
                "weather"
            )

            self.last_tool = (
                "weather"
            )

            return {
                "type": "text",

                "response": (
                    "Qual cidade você "
                    "quer consultar?"
                ),

                "data": None
            }

        print(
            "[WEATHER] Consultando "
            f"{city}..."
        )

        # ==============================================
        # EXECUTA TOOL
        # ==============================================

        result = self.tools.execute(
            "weather",
            city=city,
            state=state,
            country_code=country_code
        )

        if not result:
            return {
                "type": "text",

                "response": (
                    "Não consegui encontrar "
                    f"a previsão para {city}."
                ),

                "data": None
            }

        # ==============================================
        # CONTEXTO
        # ==============================================

        self.pending_tool = None
        self.last_tool = "weather"

        location = result[
            "location"
        ]

        daily = result[
            "daily"
        ]

        # ==============================================
        # PERÍODO
        # ==============================================

        index = 0

        if period == "tomorrow":
            index = 1

        if period == "week":
            return (
                self.handle_weather_week(
                    message=message,
                    result=result
                )
            )

        if index >= len(
            daily.get(
                "time",
                []
            )
        ):
            return {
                "type": "text",

                "response": (
                    "Não tenho dados disponíveis "
                    "para esse período."
                ),

                "data": None
            }

        # ==============================================
        # PROMPT
        # ==============================================

        prompt = f"""
Responda à pergunta do usuário usando somente
os dados meteorológicos abaixo.

Local:
{location["name"]},
{location["state"]},
{location["country"]}

Data:
{daily["time"][index]}

Temperatura máxima:
{daily["temperature_2m_max"][index]} °C

Temperatura mínima:
{daily["temperature_2m_min"][index]} °C

Sensação térmica máxima:
{daily["apparent_temperature_max"][index]} °C

Sensação térmica mínima:
{daily["apparent_temperature_min"][index]} °C

Probabilidade máxima de chuva:
{daily["precipitation_probability_max"][index]} %

Volume de precipitação:
{daily["precipitation_sum"][index]} mm

Velocidade máxima do vento:
{daily["wind_speed_10m_max"][index]} km/h

Nascer do sol:
{daily["sunrise"][index]}

Pôr do sol:
{daily["sunset"][index]}

Pergunta original:
{message}

Instruções:

- Responda em português do Brasil.
- Seja clara e objetiva.
- Use somente os dados fornecidos.
- Não invente dados.
- Não mencione ferramentas internas.
- Não mencione JSON.
- Não mencione prompts.
"""

        natural_response = (
            self.ai.generate(
                message=prompt
            )
        )

        # ==============================================
        # RETORNO
        # ==============================================

        return {
            "type": "weather",

            "response":
                natural_response,

            "data": {
                "location": (
                    f"{location['name']}, "
                    f"{location['state']}"
                ),

                "country":
                    location[
                        "country"
                    ],

                "date":
                    daily[
                        "time"
                    ][index],

                "max":
                    daily[
                        "temperature_2m_max"
                    ][index],

                "min":
                    daily[
                        "temperature_2m_min"
                    ][index],

                "apparent_max":
                    daily[
                        "apparent_temperature_max"
                    ][index],

                "apparent_min":
                    daily[
                        "apparent_temperature_min"
                    ][index],

                "rain":
                    daily[
                        "precipitation_probability_max"
                    ][index],

                "precipitation":
                    daily[
                        "precipitation_sum"
                    ][index],

                "wind":
                    daily[
                        "wind_speed_10m_max"
                    ][index],

                "sunrise":
                    daily[
                        "sunrise"
                    ][index],

                "sunset":
                    daily[
                        "sunset"
                    ][index]
            }
        }

    # ==================================================
    # WEATHER PENDENTE
    # ==================================================

    def handle_pending_weather(
        self,
        message: str
    ):
        city, state, country_code = (
            self.parse_location(
                message
            )
        )

        if not city:
            return {
                "type": "text",

                "response": (
                    "Não consegui identificar "
                    "a cidade. Tente algo como "
                    "'Horizonte - CE - Brasil'."
                ),

                "data": None
            }

        self.pending_tool = None

        tool = {
            "tool": "weather",
            "city": city,
            "state": state,
            "country_code": country_code,
            "period": "today"
        }

        return self.handle_weather(
            message=message,
            tool=tool
        )

    # ==================================================
    # WEATHER WEEK
    # ==================================================

    def handle_weather_week(
        self,
        message: str,
        result: dict
    ):
        location = result[
            "location"
        ]

        daily = result[
            "daily"
        ]

        days = []

        total_days = min(
            7,
            len(
                daily.get(
                    "time",
                    []
                )
            )
        )

        for index in range(
            total_days
        ):
            days.append({
                "date":
                    daily[
                        "time"
                    ][index],

                "max":
                    daily[
                        "temperature_2m_max"
                    ][index],

                "min":
                    daily[
                        "temperature_2m_min"
                    ][index],

                "rain":
                    daily[
                        "precipitation_probability_max"
                    ][index]
            })

        prompt = f"""
O usuário pediu uma previsão meteorológica
para vários dias.

Local:
{location["name"]},
{location["state"]},
{location["country"]}

Dados dos próximos dias:
{days}

Pergunta original:
{message}

Responda em português do Brasil.

Faça um resumo simples dos próximos dias,
informando temperaturas e chance de chuva.

Use somente os dados fornecidos.
Não invente informações.
"""

        natural_response = (
            self.ai.generate(
                message=prompt
            )
        )

        self.last_tool = "weather"

        return {
            "type": "weather_week",

            "response":
                natural_response,

            "data": {
                "location": (
                    f"{location['name']}, "
                    f"{location['state']}"
                ),

                "country":
                    location[
                        "country"
                    ],

                "days":
                    days
            }
        }

    # ==================================================
    # DETECTA LOCALIZAÇÃO
    # ==================================================

    def looks_like_location(
        self,
        message: str
    ) -> bool:
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

        text = (
            message
            .replace(
                "-",
                " "
            )
            .replace(
                ",",
                " "
            )
        )

        parts = text.split()

        for part in parts:
            if (
                part.upper()
                in state_codes
            ):
                return True

        return False

    # ==================================================
    # PARSER DE LOCALIZAÇÃO
    # ==================================================

    def parse_location(
        self,
        message: str
    ):
        text = (
            message
            .replace(
                ",",
                " "
            )
            .replace(
                "-",
                " "
            )
            .strip()
        )

        parts = [
            part.strip()
            for part
            in text.split()
            if part.strip()
        ]

        if not parts:
            return (
                None,
                None,
                "BR"
            )

        state_map = {
            "AC": "Acre",
            "AL": "Alagoas",
            "AP": "Amapá",
            "AM": "Amazonas",
            "BA": "Bahia",
            "CE": "Ceará",
            "DF": "Distrito Federal",
            "ES": "Espírito Santo",
            "GO": "Goiás",
            "MA": "Maranhão",
            "MT": "Mato Grosso",
            "MS": "Mato Grosso do Sul",
            "MG": "Minas Gerais",
            "PA": "Pará",
            "PB": "Paraíba",
            "PR": "Paraná",
            "PE": "Pernambuco",
            "PI": "Piauí",
            "RJ": "Rio de Janeiro",
            "RN": "Rio Grande do Norte",
            "RS": "Rio Grande do Sul",
            "RO": "Rondônia",
            "RR": "Roraima",
            "SC": "Santa Catarina",
            "SP": "São Paulo",
            "SE": "Sergipe",
            "TO": "Tocantins"
        }

        state = None
        country_code = "BR"

        city_parts = []

        for part in parts:
            upper = (
                part.upper()
            )

            if upper in state_map:
                state = (
                    state_map[
                        upper
                    ]
                )

                continue

            if upper in {
                "BR",
                "BRASIL",
                "BRAZIL"
            }:
                country_code = "BR"

                continue

            city_parts.append(
                part
            )

        city = " ".join(
            city_parts
        ).strip()

        if not city:
            return (
                None,
                state,
                country_code
            )

        return (
            city,
            state,
            country_code
        )