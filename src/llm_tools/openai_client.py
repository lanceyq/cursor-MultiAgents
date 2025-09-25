from pydantic import BaseModel
import instructor
from litellm import completion, acompletion
from typing import List, Dict, Any

from llm_tools.llm_client import LLMClient
from models.config_models import LLMConfig

class OpenAIClient(LLMClient):
    def __init__(self, model_config: LLMConfig, api_key: str):
        super().__init__(model_config, api_key)
        # Initialize instructor client with litellm async completion
        self.client = instructor.from_litellm(acompletion)

    def chat(self, messages: List[Dict[str, str]]) -> Any:
        """
        Generate a response using the OpenAI API.

        Args:
            messages (List[Dict[str, str]]): The list of messages in the conversation.

        Returns:
            The response from the OpenAI API.
        """
        response = completion(
            model=self.model,
            api_key=self.api_key,
            api_base=self.api_base,
            messages=messages,
            max_retries=self.max_retries,
        )
        return response
    
    async def response_structured(
            self, 
            messages: List[Dict[str, str]],
            response_model: type[BaseModel],
            ) -> type[BaseModel]:
        """
        Generate a structured response using the OpenAI API.

        Args:
            messages (List[Dict[str, str]]): The list of messages in the conversation.
            response_model (type[BaseModel]): The Pydantic model to use for structuring the response.

        Returns:
            The structured response as an instance of the specified Pydantic model.
        """
        response =  await self.client.chat.completions.create(
            model=self.model,
            response_model=response_model,
            messages=messages,
            max_retries=self.max_retries,
            # LiteLLM specific parameters
            api_key=self.api_key,
            api_base=self.api_base,
        )

        return response

