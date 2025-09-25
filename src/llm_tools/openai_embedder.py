from typing import List
from llm_tools.embedder_client import EmbedderClient
from models.config_models import EmbedderConfig

from litellm import embedding

class OpenAIEmbedderClient(EmbedderClient):
    def __init__(self, model_config: EmbedderConfig,api_key:str):
        super().__init__(model_config, api_key)


    async def response(
        self, 
        messages: List[str],
        ) -> List[List[float]]:
        """
        Get the response from the OpenAI API.

        Args:
            messages (List[str]): The list of messages to send to the API.

        Returns:
            List[List[float]]: The list of embeddings for each message.
        """
        # Filter out invalid inputs (empty strings, None values, or very short texts)
        valid_messages = []
        valid_indices = []
        
        for i, msg in enumerate(messages):
            if msg and isinstance(msg, str) and len(msg.strip()) > 0:
                valid_messages.append(msg.strip())
                valid_indices.append(i)
        
        if not valid_messages:
            # Return empty embeddings if no valid messages
            return [[0.0] * 1536 for _ in messages]  # Default embedding dimension for text-embedding-ada-002
        
        response = embedding(
            model = self.model,
            api_base=self.api_base, 
            api_key=self.api_key,  
            input=valid_messages
            )
        
        # Create result list with proper indexing
        embeddings = [item['embedding'] for item in response.data]
        result = []
        embedding_idx = 0
        
        for i in range(len(messages)):
            if i in valid_indices:
                result.append(embeddings[embedding_idx])
                embedding_idx += 1
            else:
                # Use zero vector for invalid messages
                result.append([0.0] * len(embeddings[0]) if embeddings else [0.0] * 1536)
        
        return result

