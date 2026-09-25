class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name: str, handler):
        self.tools[name] = handler

    def exists(self, name: str) -> bool:
        return name in self.tools

    def execute(self, name: str, **kwargs):
        handler = self.tools.get(name)

        if handler is None:
            return None

        return handler(**kwargs)