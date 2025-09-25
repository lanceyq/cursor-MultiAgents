from typing import List, Optional

from database.cypher_queries import DIALOGUE_NODE_SAVE, STATEMENT_NODE_SAVE
from models.graph_models import DialogueNode, StatementNode  
from database.neo4j_connector import Neo4jConnector


async def delete_all_nodes(group_id: str, connector: Neo4jConnector):
    """Delete all nodes in the database."""
    result = await connector.execute_query(f"MATCH (n {{group_id: '{group_id}'}}) DETACH DELETE n")
    print(f"All group_id: {group_id} node and edge deleted successfully")
    return result

async def add_dialogue_nodes(dialogues: List[DialogueNode], connector: Neo4jConnector) -> Optional[List[str]]:
    """Add dialogue nodes to Neo4j database.
    
    Args:
        dialogues: List of DialogueNode objects to save
        connector: Neo4j connector instance
        
    Returns:
        List of created node UUIDs or None if failed
    """
    if not dialogues:
        print("No dialogues to save")
        return []
    
    try:
        result = await connector.execute_query(
            DIALOGUE_NODE_SAVE, 
            dialogues=[dialogue.model_dump() for dialogue in dialogues]
        )
        
        created_uuids = [record["uuid"] for record in result]
        print(f"Successfully created {len(created_uuids)} dialogue nodes: {created_uuids}")
        return created_uuids
        
    except Exception as e:
        print(f"Error creating dialogue nodes: {e}")
        return None


async def add_statement_nodes(statements: List[StatementNode], connector: Neo4jConnector) -> Optional[List[str]]:
    """Add statement nodes to Neo4j database.
    
    Args:
        statements: List of StatementNode objects to save
        connector: Neo4j connector instance
        
    Returns:
        List of created node UUIDs or None if failed
    """
    if not statements:
        print("No statements to save")
        return []
    
    try:
        # Flatten StatementNode objects to only include primitive types
        flattened_statements = []
        for statement in statements:
            flattened_statement = {
                "id": statement.id,
                "group_id": statement.group_id,
                "chunk_id": statement.chunk_id,
                "created_at": statement.t_created.isoformat(), 
                "stmt_type": statement.stmt_type,
                "temporal_info": statement.temporal_info.value,
                "relevence_info": statement.relevence_info.value,
                "statement": statement.statement,
                "temporal_validity_valid_at": statement.temporal_validity_valid_at.isoformat() if statement.temporal_validity_valid_at else None,
                "temporal_validity_invalid_at": statement.temporal_validity_invalid_at.isoformat() if statement.temporal_validity_invalid_at else None,
                # "triplet_extraction_info": json.dumps({
                #     "triplets": [triplet.model_dump() for triplet in statement.triplet_extraction_info.triplets] if statement.triplet_extraction_info else [],
                #     "entities": [entity.model_dump() for entity in statement.triplet_extraction_info.entities] if statement.triplet_extraction_info else []
                # }) if statement.triplet_extraction_info else json.dumps({"triplets": [], "entities": []}),
                "statement_embedding": statement.statement_embedding if statement.statement_embedding else None,
                "chunk_embedding": statement.chunk_embedding if statement.chunk_embedding else None
            }
            flattened_statements.append(flattened_statement)
        
        result = await connector.execute_query(
            STATEMENT_NODE_SAVE, 
            statements=flattened_statements
        )
        
        created_uuids = [record["uuid"] for record in result]
        print(f"Successfully created {len(created_uuids)} statement nodes")
        return created_uuids
        
    except Exception as e:
        print(f"Error creating statement nodes: {e}")
        return None


