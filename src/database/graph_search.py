from typing import Any, Dict, List, Optional

from database.neo4j_connector import Neo4jConnector
from database.cypher_queries import (
    SEARCH_STATEMENTS_BY_KEYWORD,
    SEARCH_ENTITIES_BY_NAME,
    SEARCH_DIALOGUES_BY_CONTENT,
    STATEMENT_EMBEDDING_SEARCH,
    DIALOGUE_EMBEDDING_SEARCH,
    SEARCH_ENTITIES_BY_NAME,
)

async def search_graph(
    connector: Neo4jConnector,
    q: str,
    group_id: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Search across Statements, Entities, and Dialogues using a free-text query.

    - Statements: matches s.statement CONTAINS q
    - Entities: matches e.name CONTAINS q
    - Dialogues: matches d.content CONTAINS q
    Optionally filters by group_id and limits results.
    """
    statements = await connector.execute_query(
        SEARCH_STATEMENTS_BY_KEYWORD, q=q, group_id=group_id, limit=limit
    )
    entities = await connector.execute_query(
        SEARCH_ENTITIES_BY_NAME, q=q, group_id=group_id, limit=limit
    )
    dialogues = await connector.execute_query(
        SEARCH_DIALOGUES_BY_CONTENT, q=q, group_id=group_id, limit=limit
    )
    return {
        "statements": statements,
        "entities": entities,
        "dialogues": dialogues,
    }

async def search_graph_by_embedding(
    connector: Neo4jConnector,
    embedder_client,  
    query_text: str,
    group_id: Optional[str] = None,
    limit: int = 50,
    include: List[str] = ["statements", "dialogues", "entities"],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Embedding-based semantic search across Statements and Dialogues.

    - Computes query embedding with the provided embedder_client
    - Ranks by cosine similarity in Cypher
    - Filters by group_id if provided
    - Returns up to 'limit' per included type
    """
    # Get embedding for the query
    embeddings = await embedder_client.response([query_text])
    if not embeddings or not embeddings[0]:
        return {"statements": [], "dialogues": []}
    embedding = embeddings[0]

    results: Dict[str, List[Dict[str, Any]]] = {"statements": [], "dialogues": [], "entities": []}

    # Statements (embedding)
    if "statements" in include:
        results["statements"] = await connector.execute_query(
            STATEMENT_EMBEDDING_SEARCH,
            embedding=embedding,
            group_id=group_id,
            limit=limit,
        )

    # Dialogues (embedding)
    if "dialogues" in include:
        results["dialogues"] = await connector.execute_query(
            DIALOGUE_EMBEDDING_SEARCH,
            embedding=embedding,
            group_id=group_id,
            limit=limit,
        )

    # Entities  
    if "entities" in include:
        results["entities"] = await connector.execute_query(
            SEARCH_ENTITIES_BY_NAME,
            q=query_text,
            group_id=group_id,
            limit=limit,
        )

    return results