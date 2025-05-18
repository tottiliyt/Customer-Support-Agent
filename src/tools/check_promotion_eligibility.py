from datetime import datetime, time
import pytz
from typing import Dict, Any
import random
import string

from tools.function_tool import FunctionTool
from utils.logger import logger


class CheckPromotionEligibility(FunctionTool):
    """Tool to check if the Early Risers Promotion is currently active."""
    
    def __init__(self):
        super().__init__()

    def execute(self, _args: Dict[str, Any]) -> Dict[str, Any]:
        """Check if the Early Risers Promotion is currently active."""
        try:
            # Get current time in Pacific Time
            pacific_tz = pytz.timezone('US/Pacific')
            now = datetime.now(pacific_tz)
            current_time = now.time()
            # current_time = time(8, 30)  # uncomment this line to test the code with a fixed time
            
            # Early Risers Promotion is active between 8:00 AM and 10:00 AM Pacific Time
            promotion_start = time(8, 0)  # 8:00 AM
            promotion_end = time(10, 0)   # 10:00 AM
            
            is_valid_time = (current_time >= promotion_start and current_time <= promotion_end)
            
            # Generate a unique code with format EARLY-XXXX where X is alphanumeric
            discount_code = None
            if is_valid_time:
                chars = string.ascii_uppercase + string.digits
                unique_part1 = ''.join(random.choice(chars) for _ in range(4))
                discount_code = f"EARLY-{unique_part1}"
        except Exception as e:
            logger.error(f"Error checking promotion eligibility: {e}")
            raise
    
        return {
            "is_valid_time": is_valid_time,
            "current_time": now.strftime("%I:%M %p %Z"),
            "promotion_hours": "8:00 AM - 10:00 AM Pacific Time",
            "discount_code": discount_code
        }

    def get_definition(self) -> Dict[str, Any]:
        """Get the function definition for the AI.
        
        Returns:
            Dict containing the function definition for the AI to use.
        """
        return {
                    "name": "check_promotion_eligibility",
                    "description": "Check if the Early Risers Promotion is currently active",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                        "additionalProperties": False
                    },
                    "strict": True
                }
    
    def get_name(self) -> str:
        return "check_promotion_eligibility"