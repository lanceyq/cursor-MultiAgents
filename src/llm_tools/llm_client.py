from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pydantic import BaseModel
from models.config_models import LLMConfig

class LLMClient(ABC):
    def __init__(self, model_config: LLMConfig, api_key: str):
        self.config = model_config

        self.model = self.config.llm_name
        self.api_base = self.config.api_base
        self.max_retries = self.config.max_retries
        self.api_key = api_key

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> Any:
        pass

    @abstractmethod
    async def response_structured(
        self,
        messages: List[Dict[str, str]],
        response_model: type[BaseModel],
    ) -> type[BaseModel]:
        pass

