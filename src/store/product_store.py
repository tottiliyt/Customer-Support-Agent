import json
from pathlib import Path
from typing import Any, Dict, List
from utils.logger import logger

class ProductStore:
    def __init__(self, products_file: Path):
        self._products = self._load_products(products_file)

    def _load_products(self, products_file: Path) -> Dict[str, Dict[str, Any]]:
        try:
            with open(products_file, 'r') as f:
                product_list = json.load(f)
            return {product['SKU']: {
                'ProductName': product['ProductName'],
                'Description': product['Description'],
                'Tags': product['Tags'],
            } for product in product_list}
        except Exception as e:
            logger.error(f"Error loading product data from {products_file}: {e}")
            return {}

    def get_product(self, sku: str) -> Dict[str, Any]:
        return self._products.get(sku)
    
    def get_all_products(self) -> Dict[str, Dict[str, Any]]:
        return self._products
        
    def get_popular_products(self, limit: int = 3) -> List[Dict[str, Any]]:
        
        # In a real implementation, this would use actual popularity metrics
        # For now, we'll just return the first few products as a mock
        products = list(self._products.values())
        return products[:limit]
