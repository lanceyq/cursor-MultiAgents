from uuid import uuid4

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from ontology.ontology import TemporalInfo, RelevenceInfo

class Edge(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex, description="A unique identifier for the edge.")
    source: str = Field(..., description="The ID of the source node.")
    target: str = Field(..., description="The ID of the target node.")
    group_id: str = Field(..., description="The group ID of the edge.")
    t_created: datetime = Field(..., description="The valid time of the edge from system perspective.")
    t_expired: datetime = Field(..., description="The expired time of the edge from system perspective.")

class ChunkEdge(Edge):
    pass 

class ChunkEntityEdge(Edge):
    pass

class StatementDialogEdge(Edge):
    """Edge connecting a statement to its parent dialog"""
    chunk_id: str = Field(..., description="ID of the chunk containing the statement")


class StatementEntityEdge(Edge):
    """Edge connecting a statement to entities extracted from it"""
    pass 

class EntityEntityEdge(Edge):
    """Edge connecting related entities (from triplet relationships)"""
    relation_type: str = Field(..., description="Relation type as defined in ontology")
    relation_value: Optional[str] = Field(None, description="Value of the relation")
    statement: str = Field(..., description='The statement of the edge.')
    source_statement_id: str = Field(..., description="Statement where this relationship was extracted")
    temporal_validity_valid_at: Optional[datetime] = Field(None, description="Temporal validity start")
    temporal_validity_invalid_at: Optional[datetime] = Field(None, description="Temporal validity end")
    
class Node(BaseModel):
    id: str = Field(..., description="The unique identifier for the node.")
    name: str = Field(..., description="The name of the node.")   
    group_id: str = Field(..., description="The group ID of the node.")
    t_created: datetime = Field(..., description="The valid time of the node from system perspective.")
    t_expired: datetime = Field(..., description="The expired time of the node from system perspective.")

class DialogueNode(Node):
    """Node representing a dialogue in the graph"""
    ref_id: str = Field(..., description="Reference identifier of the dialog")
    content: str = Field(..., description="Dialogue content")
    temporal_validity_valid_at: Optional[datetime] = Field(None, description="Temporal validity start")
    temporal_validity_invalid_at: Optional[datetime] = Field(None, description="Temporal validity end")
    dialog_embedding: Optional[List[float]] = Field(None, description="Dialog embedding vector")

class StatementNode(Node):
    """Node representing a statement in the graph"""
    chunk_id: str = Field(..., description="ID of the parent chunk")
    stmt_type: str = Field(..., description="Type of the statement")
    temporal_info: TemporalInfo = Field(..., description="Temporal information")
    relevence_info: RelevenceInfo = Field(..., description="Relevance information")
    statement: str = Field(..., description="The statement text content")
    temporal_validity_valid_at: Optional[datetime] = Field(None, description="Temporal validity start")
    temporal_validity_invalid_at: Optional[datetime] = Field(None, description="Temporal validity end")
    statement_embedding: Optional[List[float]] = Field(None, description="Statement embedding vector")
    chunk_embedding: Optional[List[float]] = Field(None, description="Chunk embedding vector")

class ExtractedEntityNode(Node):
    """Node representing an extracted entity in the graph"""
    entity_idx: int = Field(..., description="Unique identifier for the entity")
    statement_id: str = Field(..., description="Statement this entity was extracted from")
    entity_type: str = Field(..., description="Type of the entity")
    description: str = Field(..., description="Entity description")
    aliases: Optional[List[str]] = Field(default_factory=list, description="Entity aliases")
    name_embedding: Optional[List[float]] = Field(default_factory=list, description="Name embedding vector")
    fact_summary: str = Field(..., description="Summary of the fact about this entity")
    # attributes: dict[str, Any] = Field(default={}, description='Additional attributes.')
