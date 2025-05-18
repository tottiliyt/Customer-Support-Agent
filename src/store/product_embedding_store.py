import json
from openai import OpenAI
import numpy as np
from pathlib import Path
from typing import List, Dict, Any

from store.product_store import ProductStore
from utils.logger import logger


class ProductEmbeddingStore:
    def __init__(self, product_store: ProductStore, embeddings_file: Path,
                 model: str = "text-embedding-3-small"):

        self.product_store = product_store
        self.model = model
        self.client = OpenAI()
        self.embeddings_file = embeddings_file
        self.product_embeddings = self._generate_embeddings()

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding vector from OpenAI text-embedding-3-small model."""
        try:
            response = self.client.embeddings.create(input=[text], model=self.model)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            raise

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def _generate_embeddings(self) -> Dict[str, List[float]]:

        try:
            with open(self.embeddings_file, 'r') as f:
                embeddings = json.load(f)
        except Exception as e:
            logger.error(f"Error loading embeddings file: {e}")
            self.embeddings_file.parent.mkdir(parents=True, exist_ok=True)
            embeddings = {}

        try:
            updated = False
            for sku, product in self.product_store.get_all_products().items():
                if sku not in embeddings:
                    text = f"{product['ProductName']} {product['Description']} {' '.join(product['Tags'])}"
                    embedding = self._get_embedding(text)
                    embeddings[sku] = embedding
                    updated = True

            if updated:
                self.embeddings_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.embeddings_file, 'w') as f:
                    json.dump(embeddings, f)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")

        return embeddings

    def get_top_k_similar_products(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        try:
            query_embedding = self._get_embedding(query)
            scored = []

            for sku, embedding in self.product_embeddings.items():
                score = self._cosine_similarity(query_embedding, embedding)
                scored.append((score, sku))

            top_products = sorted(scored, key=lambda x: x[0], reverse=True)[:top_k]
            
            return[self.product_store.get_product(sku) for _, sku in top_products]
        except Exception as e:
            logger.error(f"Error finding similar products: {e}")
            raise