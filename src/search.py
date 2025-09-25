import argparse
import asyncio
import json
import os
from typing import List
from dotenv import load_dotenv
from datetime import datetime

from database.neo4j_connector import Neo4jConnector
from database.graph_search import search_graph_by_embedding, search_graph
from llm_tools.openai_embedder import OpenAIEmbedderClient
from models.config_models import EmbedderConfig
from utils.helpers import get_embedder_config

load_dotenv()


def log_search_query(query_text: str, search_type: str, group_id: str | None, limit: int, include: List[str], log_file: str = "search_log.txt"):
    """Log search query information to file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "query": query_text,
        "search_type": search_type,
        "group_id": group_id,
        "limit": limit,
        "include": include
    }
    
    # Append to log file
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    print(f"🔍 Search logged: {query_text} ({search_type})")


async def run_hybrid_search(
    query_text: str,
    search_type: str,
    embedding_name: str,
    group_id: str | None,
    limit: int,
    include: List[str],
    output_path: str | None,
):
    """
    
    Run search with specified type: 'keyword', 'embedding', or 'hybrid'
    """
    # Log the search query
    log_search_query(query_text, search_type, group_id, limit, include)
    
    connector = Neo4jConnector()
    results = {}
    
    try:
        if search_type in ["keyword", "hybrid"]:
            # Keyword-based search
            print("🔤 Running keyword search...")
            keyword_results = await search_graph(
                connector=connector,
                q=query_text,
                group_id=group_id,
                limit=limit
            )
            
            if search_type == "keyword":
                results = keyword_results
            else:
                results["keyword_search"] = keyword_results
        
        if search_type in ["embedding", "hybrid"]:
            # Embedding-based search
            print("🧠 Running embedding search...")
            
            # Ensure API key exists
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY environment variable is not set")

            # Load embedder config from config.json
            cfg_dict = get_embedder_config(embedding_name)
            embedder_config = EmbedderConfig.model_validate(cfg_dict)

            # Init embedder
            embedder = OpenAIEmbedderClient(model_config=embedder_config, api_key=api_key)
            
            embedding_results = await search_graph_by_embedding(
                connector=connector,
                embedder_client=embedder,
                query_text=query_text,
                group_id=group_id,
                limit=limit,
                include=include,
            )
            
            if search_type == "embedding":
                results = embedding_results
            else:
                results["embedding_search"] = embedding_results
        
        # For hybrid search, merge and rank results
        if search_type == "hybrid":
            results["combined_summary"] = {
                "total_keyword_results": sum(len(v) if isinstance(v, list) else 0 for v in keyword_results.values()),
                "total_embedding_results": sum(len(v) if isinstance(v, list) else 0 for v in embedding_results.values()),
                "search_query": query_text,
                "search_timestamp": datetime.now().isoformat()
            }
        
        print(json.dumps(results, ensure_ascii=False, indent=2, default=str))

        # Save to file
        output_path = output_path or "search_results.json"
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)
        print(f"Search results saved to: {output_path}")
        
        # Log search completion with result count
        if search_type == "hybrid":
            result_counts = {
                "keyword": {key: len(value) if isinstance(value, list) else 0 for key, value in keyword_results.items()},
                "embedding": {key: len(value) if isinstance(value, list) else 0 for key, value in embedding_results.items()}
            }
        else:
            result_counts = {key: len(value) if isinstance(value, list) else 0 for key, value in results.items()}
        
        completion_log = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query_text,
            "search_type": search_type,
            "status": "completed",
            "result_counts": result_counts,
            "output_file": output_path
        }
        
        with open("search_log.txt", "a", encoding="utf-8") as f:
            f.write(json.dumps(completion_log, ensure_ascii=False) + "\n")
            
    finally:
        await connector.close()


def main():
    """Main entry point for the hybrid graph search CLI.
    
    Parses command line arguments and executes search with specified parameters.
    Supports keyword, embedding, and hybrid search modes.
    """
    parser = argparse.ArgumentParser(description="Hybrid graph search with keyword and embedding options")
    parser.add_argument(
        "--query", "-q", required=True, help="Free-text query to search"
    )
    parser.add_argument(
        "--search-type",
        "-t",
        choices=["keyword", "embedding", "hybrid"],
        default="hybrid",
        help="Search type: keyword (text matching), embedding (semantic), or hybrid (both) (default: hybrid)"
    )
    parser.add_argument(
        "--embedding-name",
        "-m",
        default="openai/nomic-embed-text:v1.5",
        help="Embedding config name from config.json (default: openai/nomic-embed-text:v1.5)",
    )
    parser.add_argument(
        "--group-id",
        "-g",
        default=None,
        help="Optional group_id to filter results (default: None)",
    )
    parser.add_argument(
        "--limit",
        "-k",
        type=int,
        default=5,
        help="Max number of results per type (default: 5)",
    )
    parser.add_argument(
        "--include",
        "-i",
        nargs="+",
        default=["statements", "dialogues", "entities"],
        choices=["statements", "dialogues", "entities"],
        help="Which targets to search for embedding search (default: statements dialogues entities)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="search_results.json",
        help="Path to save the search results JSON (default: search_results.json)",
    )
    args = parser.parse_args()

    asyncio.run(
        run_hybrid_search(
            query_text=args.query,
            search_type=args.search_type,
            embedding_name=args.embedding_name,
            group_id=args.group_id,
            limit=args.limit,
            include=args.include,
            output_path=args.output,
        )
    )


if __name__ == "__main__":
    main()