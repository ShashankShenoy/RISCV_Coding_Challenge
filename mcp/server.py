from mcp.registry import CAPABILITIES

class MCPServer:
    def __init__(self):
        self.capabilities = CAPABILITIES
    
    def handle(self, request: dict) -> dict:
        capability = request["capability"]
        input_text = request["input"]

        if capability not in self.capabilities:
            raise ValueError("Unknown capability")

        return self.capabilities[capability].execute(input_text)
