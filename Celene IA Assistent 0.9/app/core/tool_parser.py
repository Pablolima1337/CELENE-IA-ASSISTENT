import json


class ToolParser:
    @staticmethod
    def parse(text: str):
        try:
            start = text.find("{")
            end = text.rfind("}")

            if start == -1 or end == -1:
                return None

            json_text = text[start:end + 1]

            return json.loads(json_text)

        except json.JSONDecodeError:
            return None