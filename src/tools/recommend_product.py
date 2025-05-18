from typing import Any, Dict, List

from openai import OpenAI
from store.product_embedding_store import ProductEmbeddingStore
from store.product_store import ProductStore
from tools.function_tool import FunctionTool
from utils.logger import logger


class RecommendProduct(FunctionTool):

    def __init__(self, product_embedding_store: ProductEmbeddingStore, product_store: ProductStore):
        super().__init__()
        self.product_embedding_store = product_embedding_store
        self.product_store = product_store
        self.client = OpenAI()

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get product recommendations based on user preferences."""
        preferences = args.get("preferences", "")
        
        # Special case for 'general' preferences - return popular products
        if preferences.lower() == "general":
            popular_products = self.product_store.get_popular_products(limit=3)
            return {
                "recommendations": popular_products
            }
        
        recommendations = self.product_embedding_store.get_top_k_similar_products(preferences)
        
        # Post-process recommendations using LLM to evaluate relevance
        filtered_recommendations = self.filter_recommendations_with_llm(preferences, recommendations)
            
        return {
            "recommendations": filtered_recommendations
        }
    
    def get_definition(self) -> Dict[str, Any]:
        return {
            "name": "recommend_product",
            "description": "Get product recommendations based on user preferences",
            "parameters": {
                "type": "object",
                "properties": {
                    "preferences": {"type": "string", "description": "User's product preferences or requirements"}
                },
                "required": ["preferences"],
                "additionalProperties": False
            },
            "strict": True
        }
    
    def get_name(self) -> str:
        return "recommend_product"

    def filter_recommendations_with_llm(self, preferences: str, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not recommendations:
            return []
            
        filtered_recommendations = []
        
        # Create a prompt for the LLM to evaluate each product
        for product in recommendations:
            product_info = f"Product Name: {product.get('ProductName', '')}, " \
                          f"Description: {product.get('Description', '')}, " \
                          f"Tags: {', '.join(product.get('Tags', []))}"
                          
            prompt = f"""
            
            USER PREFERENCES: {preferences}
            
            PRODUCT DETAILS: {product_info}
            
            Is this product relevant to the user's preferences? Consider the product features, description, and intended use.
            Respond with only 'YES' if the product is relevant or 'NO' if it is not relevant.
            """
            
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that evaluates product relevance."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=10,
                    temperature=0.1
                )
                
                evaluation = response.choices[0].message.content.strip().upper()
                
                if evaluation == "YES":
                    filtered_recommendations.append(product)
                    
            except Exception as e:
                logger.error(f"Error in LLM evaluation: {e}")
                # If there's an error, include the product to be safe
                filtered_recommendations.append(product)
            
        return filtered_recommendations