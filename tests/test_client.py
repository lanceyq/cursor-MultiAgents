import sys
import os

import pytest
import asyncio
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from llm_tools.openai_client import OpenAIClient
from utils.helpers import get_model_config, get_prompts
from models.config_models import LLMConfig
load_dotenv()
@pytest.fixture(scope="module", params=[ "openai/qwen2.5-14b"])
def client(request):
    llm_name = request.param
    model_config = LLMConfig.model_validate(get_model_config(llm_name))
    return OpenAIClient(model_config=model_config, api_key=os.getenv("OPENAI_API_KEY"))

@pytest.fixture(scope="module", params=["openai/qwen-plus"])
def dashscope_client(request):
    llm_name = request.param
    model_config = LLMConfig.model_validate(get_model_config(llm_name))
    return OpenAIClient(model_config=model_config, api_key=os.getenv("DASHSCOPE_API_KEY"))

class User(BaseModel):
    name: str = Field(description="The name of the talker who is in the conversation")
    age: int = Field(description="The age of the talker who is in the conversation")

@pytest.mark.asyncio
async def test_openai_structured_response(client):

    test_cases = [
        {
            "role": "user",
            "content": "My name is Alice, I am 30 years old. How old am I?",
        }
    ]
    expected_results = {
        "name": "Alice",
        "age": 30,
    }

    for test_case in test_cases:
        response = await client.response_structured(get_prompts(test_case["content"]), User)
        assert response.name == expected_results["name"]
        assert response.age == expected_results["age"]

@pytest.mark.asyncio
async def test_dashscope_structured_response(dashscope_client):

    test_cases = [
        {
            "role": "user",
            "content": "My name is Bob, I am 25 years old. How old am I?",
        }
    ]
    expected_results = {
        "name": "Bob",
        "age": 25,
    }

    for test_case in test_cases:
        response = await dashscope_client.response_structured(get_prompts(test_case["content"]), User)
        assert response.name == expected_results["name"]
        assert response.age == expected_results["age"]