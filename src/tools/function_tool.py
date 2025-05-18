from typing import Any, Dict


class FunctionTool:

    def __init__(self):
        pass

    def execute(self, _args: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method")

    def get_definition(self) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_name(self) -> str:
        raise NotImplementedError("Subclasses must implement this method")
