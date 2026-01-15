class Capability:
    name = None

    def execute(self, input_text: str) -> dict:
        raise NotImplementedError
