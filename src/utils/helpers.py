import os
import json
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from pydantic import BaseModel

from utils.definitions import PROJECT_ROOT
from llm_tools.openai_client import OpenAIClient
from models.config_models import LLMConfig

# Setup logging for prompt rendering
prompt_logger = logging.getLogger('prompt_renderer')
prompt_logger.setLevel(logging.INFO)

# Create file handler only (no console output)
file_handler = logging.FileHandler('prompt_logs.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add only file handler to logger
prompt_logger.addHandler(file_handler)
prompt_logger.propagate = False  

# Setup Jinja2 environment
prompt_dir = os.path.join(PROJECT_ROOT, "src", "utils", "prompts")
prompt_env = Environment(loader=FileSystemLoader(prompt_dir))

def get_neo4j_config() ->dict:
    config_path = os.path.join(PROJECT_ROOT, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    return config["neo4j"]

def get_model_config(llm_name: str) -> dict:
    # Load configuration from JSON file
    config_path = os.path.join(PROJECT_ROOT, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    """Retrieves the configuration for a specific model from the config file."""
    for model_config in config["llm_list"]:
        if model_config["llm_name"] == llm_name:
            return model_config
    raise ValueError(f"Model '{llm_name}' not found in config.json")

def get_embedder_config(embedding_name: str) -> dict:
    # Load configuration from JSON file
    config_path = os.path.join(PROJECT_ROOT, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)

    """Retrieves the configuration for a specific model from the config file."""
    for embedder_config in config["embeddding_list"]:
        if embedder_config["embedding_name"] == embedding_name:
            return embedder_config
    raise ValueError(f"Embedder '{embedding_name}' not found in config.json")

def get_chunker_config(chunker_strategy: str) -> dict:
    # Load configuration from JSON file
    config_path = os.path.join(PROJECT_ROOT, "config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    for chunker_config in config["chunker_list"]:
        if chunker_config["chunker_strategy"] == chunker_strategy:
            return chunker_config
    raise ValueError(f"Chunker '{chunker_strategy}' not found in config.json")

def get_llm_client(llm_name: str = "openai/qwen2.5-14b"):
    """Create and return an LLM client based on the specified type.
    
    Args:
        llm_type: Either 'openai' for OpenAI models or 'qwen' for Qwen models
        
    Returns:
        Configured OpenAIClient instance
    """

    if not llm_name.startswith("openai"):
        raise ValueError(f"LLM name {llm_name} not supported")
    model_config = get_model_config(llm_name)
    api_key = os.getenv(model_config["api_key"])
    if not api_key:
        raise ValueError(f"API key for {llm_name} not found in environment variables")

    return OpenAIClient(
        model_config=LLMConfig.model_validate(model_config),
        api_key=api_key
    )

async def handle_response(response: type[BaseModel]) -> dict:
    return response.model_dump()

def log_time(step_name: str, duration: float, log_file: str = "time.log"):
    """Log timing information to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {step_name}: {duration:.2f} seconds\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)
    
    print(f"✓ {step_name}: {duration:.2f}s")


def get_prompts(message: str) -> list[dict]:
    """
    Renders system and user prompts using Jinja2 templates.
    """
    system_template = prompt_env.get_template("system.jinja2")
    user_template = prompt_env.get_template("user.jinja2")

    system_prompt = system_template.render()
    user_prompt = user_template.render(message=message)
    
    prompt_logger.info("\n=== RENDERED SYSTEM PROMPT ===")
    prompt_logger.info(system_prompt)
    prompt_logger.info("\n=== RENDERED USER PROMPT ===")
    prompt_logger.info(user_prompt)
    prompt_logger.info("\n" + "="*50 + "\n")

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

def render_statement_extraction_prompt(chunk_content: str, definitions: dict, json_schema: dict) -> str:
    """
    Renders the statement extraction prompt using the extract_statement.jinja2 template.
    
    Args:
        chunk_content: The content of the chunk to process
        definitions: Label definitions for statement classification
        json_schema: JSON schema for the expected output format
        
    Returns:
        Rendered prompt content as string
    """
    template = prompt_env.get_template("extract_statement.jinja2")
    rendered_prompt = template.render(
        inputs={"chunk": chunk_content},
        definitions=definitions,
        json_schema=json_schema
    )
    
    prompt_logger.info("\n=== RENDERED STATEMENT EXTRACTION PROMPT ===")
    prompt_logger.info(rendered_prompt)
    prompt_logger.info("\n" + "="*50 + "\n")
    
    return rendered_prompt

def render_temporal_extraction_prompt(
    ref_dates: dict,
    statement: dict,
    temporal_guide: dict,
    statement_guide: dict,
    json_schema: dict,
) -> str:
    """
    Renders the temporal extraction prompt using the extract_temporal.jinja2 template.

    Args:
        ref_dates: Reference dates for context.
        statement: The statement to process.
        temporal_guide: Guidance on temporal types.
        statement_guide: Guidance on statement types.
        json_schema: JSON schema for the expected output format.

    Returns:
        Rendered prompt content as a string.
    """
    template = prompt_env.get_template("extract_temporal.jinja2")
    inputs = ref_dates | statement
    rendered_prompt = template.render(
        inputs=inputs,
        temporal_guide=temporal_guide,
        statement_guide=statement_guide,
        json_schema=json_schema,
    )

    prompt_logger.info("\n=== RENDERED TEMPORAL EXTRACTION PROMPT ===")
    prompt_logger.info(rendered_prompt)
    prompt_logger.info("\n" + "=" * 50 + "\n")

    return rendered_prompt

def render_triplet_extraction_prompt(statement: str,chunk_content: str, json_schema: dict, predicate_instructions: dict = None) -> str:
    """
    Renders the triplet extraction prompt using the extract_triplet.jinja2 template.
    
    Args:
        statement: Statement text to process
        chunk_content: The content of the chunk to process
        json_schema: JSON schema for the expected output format
        predicate_instructions: Optional predicate instructions
        
    Returns:
        Rendered prompt content as string
    """
    template = prompt_env.get_template("extract_triplet.jinja2")
    rendered_prompt = template.render(
        statement=statement,
        chunk_content=chunk_content,
        json_schema=json_schema,
        predicate_instructions=predicate_instructions
    )
    
    prompt_logger.info("\n=== RENDERED TRIPLET EXTRACTION PROMPT ===")
    prompt_logger.info(rendered_prompt)
    prompt_logger.info("\n" + "="*50 + "\n")
    
    return rendered_prompt