from typing import Optional
from pydantic import BaseModel, Field

# TODO: Add field validator for each class


class LLMConfig(BaseModel):
    llm_name: str = Field(..., description="The name of the LLM model to use.")
    api_base: Optional[str] = Field(None, description="The base URL for the API endpoint.")
    api_key: str = Field(..., description="The environment variable name for the API key.")
    max_retries: Optional[int] = Field(3, ge=0, description="The maximum number of retries for API calls.")


class EmbedderConfig(BaseModel):
    embedding_name: str = Field(..., description="The name of the embedding model to use.")
    api_base: Optional[str] = Field(None, description="The base URL for the API endpoint.")
    max_retries: Optional[int] = Field(3, ge=0, description="The maximum number of retries for API calls.")
    dimension: int = Field(...,ge=0, description="The dimension of the embeddings.")

class ChunkerConfig(BaseModel):
    chunker_strategy: str = Field(..., description="The name of the chunker strategy to use.")
    embedding_model: str = Field(..., description="The name of the embedding model to use.")
    chunk_size: Optional[int] = Field(2048, ge=0, description="The size of each chunk.")
    threshold: Optional[float] = Field(0.8, ge=0, le=1, description="The threshold for similarity.")
    language: Optional[str] = Field("zh", description="The language of the text.")
    skip_window: Optional[int] = Field(0, ge=0, description="The window for skip-and-merge.")
    min_sentences: Optional[int] = Field(1, ge=0, description="The minimum number of sentences in each chunk.")
    min_characters_per_chunk: Optional[int] = Field(24, ge=0, description="The minimum number of characters in each chunk.")
