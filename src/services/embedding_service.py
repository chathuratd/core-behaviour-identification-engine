from typing import List
import logging
import openai

from src.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using OpenAI"""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        if self.api_key:
            openai.api_key = self.api_key
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using OpenAI
        
        Args:
            text: Input text to embed
            
        Returns:
            List[float]: Embedding vector
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured")
            # Return a dummy embedding for testing
            return [0.0] * 1536
        
        try:
            response = openai.Embedding.create(
                input=text,
                model="text-embedding-ada-002"
            )
            embedding = response['data'][0]['embedding']
            logger.info(f"Generated embedding for text: {text[:50]}...")
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
