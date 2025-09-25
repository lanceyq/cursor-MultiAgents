from typing import List

from database.neo4j_connector import Neo4jConnector   
from database.add_nodes import add_dialogue_nodes, add_statement_nodes
from database.cypher_queries import (
    DIALOGUE_STATEMENT_EDGE_SAVE, 
    STATEMENT_ENTITY_EDGE_SAVE, 
    ENTITY_RELATIONSHIP_SAVE, 
    EXTRACTED_ENTITY_NODE_SAVE  
)
from models.graph_models import (
    DialogueNode,
    StatementDialogEdge,
    StatementEntityEdge,
    StatementNode,
    ExtractedEntityNode,
    EntityEntityEdge,
)

async def save_entities_and_relationships(
    entity_nodes: List[ExtractedEntityNode], 
    entity_entity_edges: List[EntityEntityEdge], 
    connector: Neo4jConnector
):
    """Save entities and their relationships using graph models"""
    all_entities = [entity.model_dump() for entity in entity_nodes]
    all_relationships = []
    
    for edge in entity_entity_edges:
        relationship = {
            'source_id': edge.source,
            'target_id': edge.target,
            'predicate': edge.relation_type,
            'statement_id': edge.source_statement_id,
            'value': edge.relation_value,
            'created_at': edge.t_created.isoformat(),
            'statement_id': edge.source_statement_id,
            'statement': edge.statement,
            'temporal_validity_valid_at': edge.temporal_validity_valid_at.isoformat() if edge.temporal_validity_valid_at else None,
            'temporal_validity_invalid_at': edge.temporal_validity_invalid_at.isoformat() if edge.temporal_validity_invalid_at else None,
        }
        all_relationships.append(relationship)
    
    # Save entities
    if all_entities:
        entity_uuids = await connector.execute_query(EXTRACTED_ENTITY_NODE_SAVE, entities=all_entities, return_created_ids=True)
        if entity_uuids:
            print(f"Successfully saved {len(entity_uuids)} entity nodes to Neo4j")
        else:
            print("Failed to save entity nodes to Neo4j")
    else:
        print("No entity nodes to save")
    
    # Create relationships
    if all_relationships:
        relationship_uuids = await connector.execute_query(ENTITY_RELATIONSHIP_SAVE, relationships=all_relationships, return_created_ids=True)
        if relationship_uuids:
            print(f"Successfully saved {len(relationship_uuids)} entity relationships (edges) to Neo4j")
        else:
            print("Failed to save entity relationships to Neo4j")
    else:
        print("No entity relationships to save")


async def save_statement_dialog_edges(
    statement_dialog_edges: List[StatementDialogEdge], 
    connector: Neo4jConnector
):
    """Save statement-dialog edges using graph models"""
    if not statement_dialog_edges:
        print("No statement-dialog edges to save")
        return

    all_sd_edges = []
    for edge in statement_dialog_edges:
        all_sd_edges.append({
            "id": edge.id,
            "source": edge.source,
            "target": edge.target,
            "group_id": edge.group_id,
            "t_created": edge.t_created,
            "t_expired": edge.t_expired
        })
    
    sd_uuids = await connector.execute_query(
        DIALOGUE_STATEMENT_EDGE_SAVE,
        dialogue_statement_edges=all_sd_edges,
        return_created_ids=True
    )
    if sd_uuids:
        print(f"Successfully saved {len(sd_uuids)} statement-dialog edges to Neo4j")
    else:
        print("Failed to save statement-dialog edges to Neo4j")

async def save_statement_entity_edges(
    statement_entity_edges: List[StatementEntityEdge], 
    connector: Neo4jConnector
):
    """Save statement-entity edges using graph models"""
    if not statement_entity_edges:
        print("No statement-entity edges to save")
        return

    all_se_edges = []
    for edge in statement_entity_edges:
        edge_data = {
            "source": edge.source,
            "target": edge.target,
            "group_id": edge.group_id,
            "t_created": edge.t_created.isoformat(),
            "t_expired": edge.t_expired.isoformat()
        }
        all_se_edges.append(edge_data)
    
    if all_se_edges:
        se_uuids = await connector.execute_query(STATEMENT_ENTITY_EDGE_SAVE, relationships=all_se_edges, return_created_ids=True)
        if se_uuids:
            print(f"Successfully saved {len(se_uuids)} statement-entity edges to Neo4j")
        else:
            print("Failed to save statement-entity edges to Neo4j")

async def save_dialog_and_statements_to_neo4j(
    dialogue_nodes: List[DialogueNode],
    statement_nodes: List[StatementNode],
    entity_nodes: List[ExtractedEntityNode],
    entity_edges: List[EntityEntityEdge],
    statement_dialog_edges: List[StatementDialogEdge],  
    statement_entity_edges: List[StatementEntityEdge],   
    connector: Neo4jConnector
) -> bool:
    """Save dialogue nodes, statement nodes, entities, and all relationships to Neo4j using graph models.
    
    Args:
        dialogue_nodes: List of DialogueNode objects to save
        statement_nodes: List of StatementNode objects to save
        entity_nodes: List of ExtractedEntityNode objects to save
        entity_edges: List of EntityEntityEdge objects to save
        statement_dialog_edges: List of StatementDialogEdge objects to save  # New
        statement_entity_edges: List of StatementEntityEdge objects to save  # New
        connector: Neo4j connector instance
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Save all dialogue nodes in batch
        dialogue_uuids = await add_dialogue_nodes(dialogue_nodes, connector)
        if dialogue_uuids:
            print(f"Dialogues saved to Neo4j with UUIDs: {dialogue_uuids}")
        else:
            print("Failed to save dialogues to Neo4j")
            return False
        
        # Save all statement nodes in batch
        if statement_nodes:
            statement_uuids = await add_statement_nodes(statement_nodes, connector)
            if statement_uuids:
                print(f"Successfully saved {len(statement_uuids)} statement nodes to Neo4j")
            else:
                print("Failed to save statement nodes to Neo4j")
                return False
        else:
            print("No statement nodes to save")
        
        # Save entities and relationships
        await save_entities_and_relationships(entity_nodes, entity_edges, connector)
        print("Successfully saved entities and relationships to Neo4j")
        
        # Save new edges
        await save_statement_dialog_edges(statement_dialog_edges, connector)
        await save_statement_entity_edges(statement_entity_edges, connector)
        
        return True
        
    except Exception as e:
        print(f"Neo4j integration error: {e}")
        print("Continuing without database storage...")
        return False