from typing import List, Optional
from uuid import uuid4

from database.cypher_queries import DIALOGUE_STATEMENT_EDGE_SAVE
from models.message_models import DialogData
from database.neo4j_connector import Neo4jConnector

async def add_dialogue_statement_edges(dialog: DialogData, connector: Neo4jConnector) -> Optional[List[str]]:
    """Add edges between a dialogue node and its statement nodes in Neo4j.
    
    Args:
        dialog: DialogData object containing the statements
        connector: Neo4j connector instance
        
    Returns:
        List of created edge UUIDs or None if failed
    """
    statements = dialog.get_all_statements()
    if not statements:
        print("No statements found in dialog to create edges")
        return []
    
    try:
        # Prepare edge data for each statement
        edges = []
        for statement in statements:
            edge = {
                "uuid": uuid4().hex,
                "source_node_uuid": dialog.id,
                "target_node_uuid": statement.id,
                "group_id": dialog.group_id,
                "created_at": dialog.created_at.isoformat()
            }
            edges.append(edge)
        
        # Execute the query to create edges
        result = await connector.execute_query(
            DIALOGUE_STATEMENT_EDGE_SAVE,
            dialogue_statement_edges=edges
        )
        
        created_uuids = [record["uuid"] for record in result]
        print(f"Successfully created {len(created_uuids)} edges for dialog {dialog.id}")
        return created_uuids
        
    except Exception as e:
        print(f"Error creating dialogue-statement edges: {e}")
        return None

