from typing import Dict, Any

from tools.function_tool import FunctionTool
from store.order_store import OrderStore
from utils.logger import logger


class LookUpOrder(FunctionTool):
    """Tool to look up order status using email and order number."""

    def __init__(self, order_store: OrderStore):
        """Initialize the LookUpOrder tool with an order store.
        
        Args:
            order_store: The OrderStore instance to use for order lookups
        """
        super().__init__()
        self.order_store = order_store

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Look up order status using email and order number.
        
        Args:
            args: Dictionary containing:
                - email (str): Customer's email address
                - order_number (str): Order number or ID
        
        Returns:
            Dict containing:
                - found (bool): Whether the order was found
                - order (dict): Order details if found
                - message (str): Error message if not found
        """
        email = args.get("email", "")
        order_number = args.get("order_number", "")
        
        try:
            order = self.order_store.get_order_by_email_and_number(email, order_number)
        except Exception as e:
            logger.error(f"Error looking up order: {e}")
            raise
        
        if order:
            return {
                "found": True,
                "order": order
            }
        else:
            return {
                "found": False,
                "message": "Order not found."
            }

    def get_definition(self) -> Dict[str, Any]:
        """Get the function definition for the AI.
        
        Returns:
            Dict containing the function definition for the AI to use.
        """
        return {
                    "name": "lookup_order",
                    "description": "Look up order status using email and order number",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "description": "Customer's email address"},
                            "order_number": {"type": "string", "description": "Order number or ID"}
                        },
                        "required": ["email", "order_number"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
    
    def get_name(self) -> str:
        return "lookup_order"