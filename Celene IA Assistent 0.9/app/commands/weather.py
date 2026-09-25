import requests


class Weather:
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        self.timeout = 10

    def get_coordinates(
        self,
        city: str,
        state: str | None = None,
        country_code: str = "BR"
    ):
        """
        Procura uma cidade e retorna suas coordenadas.
        """

        params = {
            "name": city,
            "count": 10,
            "language": "pt",
            "format": "json",
            "countryCode": country_code,
        }

        try:
            response = requests.get(
                self.GEOCODING_URL,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:
            print(
                f"[WEATHER] Erro ao localizar cidade: {error}"
            )
            return None

        results = data.get("results", [])

        if not results:
            print(
                f"[WEATHER] Cidade não encontrada: {city}"
            )
            return None

        # Se um estado foi informado,
        # tenta encontrar a cidade naquele estado.
        if state:
            state_normalized = state.lower().strip()

            for location in results:
                admin1 = (
                    location
                    .get("admin1", "")
                    .lower()
                    .strip()
                )

                admin1_code = (
                    location
                    .get("admin1_code", "")
                    .lower()
                    .strip()
                )

                if (
                    state_normalized == admin1
                    or state_normalized == admin1_code
                    or state_normalized in admin1
                ):
                    return self._format_location(
                        location
                    )

        # Se nenhum estado foi informado,
        # usa o primeiro resultado encontrado.
        return self._format_location(results[0])

    def _format_location(self, location):
        """
        Padroniza os dados retornados pela
        API de geocodificação.
        """

        return {
            "name": location.get(
                "name",
                ""
            ),
            "state": location.get(
                "admin1",
                ""
            ),
            "country": location.get(
                "country",
                ""
            ),
            "country_code": location.get(
                "country_code",
                ""
            ),
            "latitude": location.get(
                "latitude"
            ),
            "longitude": location.get(
                "longitude"
            ),
            "timezone": location.get(
                "timezone",
                ""
            ),
        }

    def get_forecast(
        self,
        city: str,
        state: str | None = None,
        country_code: str = "BR",
        forecast_days: int = 7
    ):
        """
        Busca a previsão meteorológica
        para uma determinada cidade.
        """

        print(
            f"[WEATHER] Procurando: "
            f"{city}"
        )

        location = self.get_coordinates(
            city=city,
            state=state,
            country_code=country_code,
        )

        if not location:
            return None

        print(
            "[WEATHER] Local encontrado: "
            f"{location['name']}, "
            f"{location['state']}, "
            f"{location['country']}"
        )

        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],

            "current": [
                "temperature_2m",
                "apparent_temperature",
                "relative_humidity_2m",
                "weather_code",
                "wind_speed_10m",
            ],

            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "precipitation_probability_max",
                "precipitation_sum",
                "wind_speed_10m_max",
                "sunrise",
                "sunset",
            ],

            "timezone": "auto",

            "forecast_days": forecast_days,
        }

        try:
            response = requests.get(
                self.FORECAST_URL,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:
            print(
                "[WEATHER] Erro ao buscar "
                f"previsão: {error}"
            )
            return None

        return {
            "location": location,

            "current": data.get(
                "current",
                {}
            ),

            "current_units": data.get(
                "current_units",
                {}
            ),

            "daily": data.get(
                "daily",
                {}
            ),

            "daily_units": data.get(
                "daily_units",
                {}
            ),
        }