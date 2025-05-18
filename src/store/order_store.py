import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from utils.logger import logger


class OrderStore:
    
    def __init__(self, orders_file: Path):
        
        self._orders_file = orders_file
        
        # Load data into cache
        self._orders = self._load_data(self._orders_file, "orders")
    
    def _load_data(self, file_path: Path, data_type: str) -> List[Dict[str, Any]]:
        """Load data from JSON file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # If the file is a direct array, return it directly
                if isinstance(data, list):
                    return data
                # If it's an object with a key matching data_type, return that
                return data.get(data_type, [])
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {e}")
            return []
    
    def get_order_by_email_and_number(self, email: str, order_number: str) -> Optional[Dict[str, Any]]:
        """Find an order by customer email and order number."""
        try:
            # Normalize order number format (add # if not present)
            if order_number and not order_number.startswith('#'):
                order_number = f"#{order_number}"
            
            for order in self._orders:
                if (order.get('Email', '').lower() == email.lower() and 
                    order.get('OrderNumber', '').upper() == order_number.upper()):
                    # Create a response with tracking link if available
                    tracking_number = order.get('TrackingNumber')
                    tracking_link = None
                    if tracking_number:
                        tracking_link = f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}"
                    
                    return {
                        'OrderNumber': order.get('OrderNumber'),
                        'Status': order.get('Status'),
                        'TrackingNumber': tracking_number,
                        'TrackingLink': tracking_link
                    }
            return None
        except Exception as e:
            logger.error(f"Error looking up order for email {email} and order number {order_number}: {e}")
            raise
