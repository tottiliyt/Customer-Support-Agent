import json
from datetime import datetime, time
import pytz
from pathlib import Path
from typing import Dict, List, Any

from store.order_store import OrderStore
from store.product_embedding_store import ProductEmbeddingStore
from tools.function_tool import FunctionTool
from tools.recommend_product import RecommendProduct
from utils.logger import logger


class FunctionTools:
    """Handles execution of AI function calls."""
    
    def __init__(self, tools: List[FunctionTool]):
        # Initialize services
        self.tools = {tool.get_name(): tool for tool in tools}
    
    def execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a function by name with the provided arguments."""
        if function_name in self.tools:
            try:
                return self.tools[function_name].execute(arguments)
            except Exception as e:
                logger.error(f"Error executing function {function_name}: {e}")
                raise
        else:
            logger.error(f"Unknown function: {function_name}")
            return {"error": f"Unknown function: {function_name}"}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get the list of tools available to the AI."""
        return [{
                "type": "function",
                "function": tool.get_definition()
            } for tool in self.tools.values()]