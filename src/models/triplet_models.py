from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4


class Entity(BaseModel):
    """Represents an extracted entity"""
    id: str = Field(default_factory=lambda: uuid4().hex, description="Unique identifier for the entity.")
    entity_idx: int = Field(..., description="Unique identifier for the entity")
    name: str = Field(..., description="Name of the entity")
    name_embedding: Optional[List[float]] = Field(None, description="Embedding vector for the entity name")
    type: str = Field(..., description="Type/category of the entity")
    description: str = Field(..., description="Description of the entity")


class Triplet(BaseModel):
    """Represents an extracted knowledge triplet"""
    id: str = Field(default_factory=lambda: uuid4().hex, description="Unique identifier for the triplet.")
    statement_id: str = Field(..., description="ID of the parent statement this triplet was extracted from.")
    subject_name: str = Field(..., description="Name of the subject entity")
    subject_id: int = Field(..., description="ID of the subject entity")
    predicate: str = Field(..., description="Relationship/predicate between subject and object")
    object_name: str = Field(..., description="Name of the object entity")
    object_id: int = Field(..., description="ID of the object entity")
    value: Optional[str] = Field(None, description="Additional value or context")


class TripletExtractionResponse(BaseModel):
    """Response model for triplet extraction"""
    triplets: List[Triplet] = Field(default_factory=list, description="List of extracted triplets")
    entities: List[Entity] = Field(default_factory=list, description="List of extracted entities")
