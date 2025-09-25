from abc import ABC, abstractmethod
from typing import List

from models.config_models import EmbedderConfig

class EmbedderClient(ABC):
    def __init__(self, model_config: EmbedderConfig,api_key:str):
        self.model = model_config.embedding_name
        self.api_base = model_config.api_base
        self.max_retries = model_config.max_retries
        self.dimension = model_config.dimension
        self.api_key = api_key


    @abstractmethod
    async def response(
        self, 
        messages: List[str],
        ) -> List[str]:
        pass


