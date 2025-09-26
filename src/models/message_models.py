from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime

from ontology.ontology import StatementType, TemporalInfo, RelevenceInfo
from models.triplet_models import TripletExtractionResponse, Triplet

# TODO: Add field validator for each class

# Define the structure for a single chat message within the conversation.
class ConversationMessage(BaseModel):
    """Represents a single message from the '用户' or 'AI'."""
    role: str = Field(..., description="The role of the speaker (e.g., '用户', 'AI').")
    msg: str = Field(..., description="The text content of the message.")
class TemporalValidityRange(BaseModel):
    """Represents the temporal validity range of a statement."""
    valid_at: Optional[str] = Field(
        None,
        description="The start date of the statement's validity, in 'YYYY-MM-DD' format or 'None'.",
    )
    invalid_at: Optional[str] = Field(
        None,
        description="The end date of the statement's validity, in 'YYYY-MM-DD' format or 'None'.",
    )
class Statement(BaseModel):
    """Represents a statement with statement type and temporal information"""
    id: str = Field(default_factory=lambda: uuid4().hex, description="A unique identifier for the statement.")
    chunk_id: str = Field(..., description="ID of the parent chunk this statement belongs to.")
    group_id: Optional[str] = Field(None, description="ID of the group this statement belongs to.")
    statement: str = Field(..., description="The text content of the statement.")
    statement_embedding: Optional[List[float]] = Field(None, description="The embedding vector of the statement.")
    stmt_type: StatementType = Field(..., description="The type of the statement.")
    temporal_info: TemporalInfo = Field(..., description="The temporal information of the statement.")
    relevence_info: RelevenceInfo = Field(..., description="The relevence information of the statement.")   
    temporal_validity: Optional[TemporalValidityRange] = Field(
        None, description="The temporal validity range of the statement."
    )
    triplet_extraction_info: Optional[TripletExtractionResponse] = Field(
        None, description="The triplet extraction information of the statement."
    )
# Define the full conversation history. This is the 'context' field.
class ConversationContext(BaseModel):
    """Represents the conversation history, parsed into a list of messages."""
    msgs: List[ConversationMessage] = Field(..., description="A list of messages in the conversation.")

    @property
    def content(self) -> str:
        """Get the content of the conversation as a string."""
        return "\n".join([f"{msg.role}: {msg.msg}" for msg in self.msgs])

# Define the structure for a single chunk of text from the conversation
class Chunk(BaseModel):
    """A chunk of text from the conversation context"""
    id: str = Field(default_factory=lambda: uuid4().hex, description="A unique identifier for the chunk.")
    text: List[ConversationMessage] = Field(default_factory=list, description="A list of messages in the chunk.")
    content: str = Field(..., description="The content of the chunk as a string.")
    statements: List[Statement] = Field(default_factory=list, description="A list of statements in the chunk.")
    chunk_embedding: Optional[List[float]] = Field(None, description="The embedding vector of the chunk.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the chunk.")

    @classmethod
    def from_messages(cls, messages: List[ConversationMessage], metadata: Optional[dict[str, Any]] = None):
        """Create a chunk from a list of messages."""
        if metadata is None:
            metadata = {}
        # Generate content from messages
        content = "\n".join([f"{msg.role}: {msg.msg}" for msg in messages])
        return cls(text=messages, content=content, metadata=metadata)


# Define the main data model for the entire input JSON object.
class DialogData(BaseModel):
    """Represents the entire data structure for the dialog record."""
    id: str = Field(default_factory=lambda: uuid4().hex, description="A unique identifier for the dialog.")
    context: ConversationContext = Field(..., description="The full conversation context as a single string.")
    dialog_embedding: Optional[List[float]] = Field(None, description="The embedding vector of the dialog.")
    ref_id: str = Field(..., description="Refer to external dialog id. This is used to link to the original dialog.")
    group_id: str = Field(..., description="Group ID of dialogue data")
    created_at: datetime = Field(default_factory=datetime.now, description="The timestamp when the dialog was created.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata for the dialog.")
    chunks: List[Chunk] = Field(default_factory=list, description="A list of chunks from the conversation context.")

    @property
    def content(self) -> str:
        """Get the content of the dialog as a string."""
        return self.context.content
    
    def get_statement_chunk(self, statement_id: str) -> Optional[Chunk]:
        """Find the chunk containing a specific statement"""
        for chunk in self.chunks:
            for statement in chunk.statements:
                if statement.id == statement_id:
                    return chunk
        return None
    
    def get_all_statements(self) -> List[Statement]:
        """Get all statements from all chunks"""
        all_statements = []
        for chunk in self.chunks:
            all_statements.extend(chunk.statements)
        return all_statements
    
    def get_statement_by_id(self, statement_id: str) -> Optional[Statement]:
        """Find a specific statement by its ID"""
        for chunk in self.chunks:
            for statement in chunk.statements:
                if statement.id == statement_id:
                    return statement
        return None
    
    def get_triplets_for_statement(self, statement_id: str) -> List[Triplet]:
        """Get all triplets extracted from a specific statement"""
        statement = self.get_statement_by_id(statement_id)
        if statement and statement.triplet_extraction_info:
            return statement.triplet_extraction_info.triplets
        return []
    
    def assign_group_id_to_statements(self):
        """Assign this dialog's group_id to all statements in all chunks"""
        for chunk in self.chunks:
            for statement in chunk.statements:
                if statement.group_id is None:
                    statement.group_id = self.group_id