# Configuration Documentation

This document describes the configuration file `config.json` used in the MemSci project for managing various service endpoints and model configurations.

## Overview

The `config.json` file contains configuration settings for:
- Large Language Models (LLMs)
- Embedding models
- Neo4j database connection
- Text chunking strategies

## Configuration Structure

### LLM Configuration (`llm_list`)

Defines available Large Language Models and their API endpoints.

```json
"llm_list": [
  {
    "llm_name": "openai/qwen2.5-14b",
    "api_base": "http://43.137.4.24:9090/v1"
  }
]
```

**Fields:**
- `llm_name` (string): Identifier for the LLM model
- `api_base` (string): Base URL for the API endpoint

**Available Models:**
- `openai/qwen2.5-14b`
- `openai/qwen3-14b` 
- `openai/deepseek-r1-0528-qwen3-8b`

### Embedding Configuration (`embeddding_list`)

Defines embedding models for text vectorization.

```json
"embeddding_list": [
  {
    "embedding_name": "openai/nomic-embed-text:v1.5",
    "api_base": "http://119.45.239.97:11434/v1",
    "dimension": 768
  }
]
```

**Fields:**
- `embedding_name` (string): Identifier for the embedding model
- `api_base` (string): Base URL for the embedding API
- `dimension` (integer): Vector dimension of the embeddings

### Neo4j Database Configuration (`neo4j`)

Database connection settings for the Neo4j graph database.

```json
"neo4j": {
  "uri": "bolt://1.94.111.67:7687",
  "username": "neo4j"
}
```

**Fields:**
- `uri` (string): Neo4j database connection URI using Bolt protocol
- `username` (string): Database username (password should be set via environment variables)

### Chunking Configuration (`chunker_list`)

Defines different text chunking strategies and their parameters.

#### SemanticChunker

Chunks text based on semantic similarity.

```json
{
  "chunker_strategy": "SemanticChunker",
  "embedding_model": "BAAI/bge-m3",
  "chunk_size": 2048,
  "threshold": 0.8,
  "min_sentences": 10,
  "language": "zh",
  "skip_window": 1
}
```

**Parameters:**
- `chunker_strategy`: "SemanticChunker"
- `embedding_model`: Model used for semantic similarity calculation
- `chunk_size`: Maximum tokens per chunk
- `threshold`: Similarity threshold (0-1) for chunk boundaries
- `min_sentences`: Minimum sentences required per chunk
- `language`: Target language ("zh" for Chinese)
- `skip_window`: Skip-and-merge window size

#### RecursiveChunker

Chunks text using recursive splitting rules.

```json
{
  "chunker_strategy": "RecursiveChunker",
  "embedding_model": "BAAI/bge-m3",
  "chunk_size": 2048,
  "threshold": 0.8,
  "min_sentences": 2,
  "language": "zh",
  "skip_window": 0
}
```

**Parameters:**
- Similar to SemanticChunker but with different defaults
- `min_sentences`: 2 (lower than SemanticChunker)
- `skip_window`: 0 (disabled)

#### LateChunker

Performs chunking after initial processing.

```json
{
  "chunker_strategy": "LateChunker",
  "embedding_model": "all-MiniLM-L6-v2",
  "chunk_size": 2048,
  "min_characters_per_chunk": 24
}
```

**Parameters:**
- `chunker_strategy`: "LateChunker"
- `embedding_model`: Different model optimized for late chunking
- `chunk_size`: Maximum chunk size
- `min_characters_per_chunk`: Minimum characters required per chunk

#### NeuralChunker

Uses neural networks for intelligent chunking.

```json
{
  "chunker_strategy": "NeuralChunker",
  "embedding_model": "mirth/chonky_modernbert_base_1",
  "min_characters_per_chunk": 24
}
```

**Parameters:**
- `chunker_strategy`: "NeuralChunker"
- `embedding_model`: Specialized neural model for chunking
- `min_characters_per_chunk`: Minimum characters per chunk

## Usage

The configuration is loaded by helper functions in `src/utils/helpers.py`:

- `get_model_config(llm_name)`: Retrieves LLM configuration
- `get_embedder_config(embedding_name)`: Retrieves embedding configuration
- `get_chunker_config(chunker_strategy)`: Retrieves chunker configuration

## Environment Variables

Some sensitive information should be stored in environment variables:
- `NEO4J_PASSWORD`: Neo4j database password
- `OPENAI_API_KEY`: API key for OpenAI-compatible services

## Notes

- All API endpoints are currently pointing to internal/development servers
- The embedding list has a typo: "embeddding_list" should be "embedding_list"
- Chunker configurations support different strategies for various use cases
- Chinese language ("zh") is the primary target for text processing