import pytest
from datetime import datetime
from pydantic import ValidationError

from models.graph_models import (
    Edge,
    EntityEntityEdge,
    ChunkEdge,
    ChunkEntityEdge,
    Node,
    DialogueNode,
    StatementNode,
    ExtractedEntityNode,
)
from models.message_models import Statement

# Fixtures for common data
@pytest.fixture
def basic_edge_data():
    return {
        "id": "edge1",
        "source": "node1",
        "target": "node2",
        "group_id": "group1",
        "t_created": datetime.now(),
        "t_expired": datetime.now(),
    }

@pytest.fixture
def basic_node_data():
    return {
        "id": "node1",
        "name": "Test Node",
        "group_id": "group1",
        "t_created": datetime.now(),
        "t_expired": datetime.now(),
    }

@pytest.fixture
def statement_data():
    return {
        "chunk_id": "chunk_1",
        "statement": "This is a test statement.",
        "stmt_type": "FACT",
        "temporal_info": "STATIC",
        "relevence_info": "RELEVANT",
    }

# Tests for Edge
def test_edge_creation(basic_edge_data):
    edge = Edge(**basic_edge_data)
    assert edge.id == "edge1"
    assert edge.source == "node1"
    assert edge.target == "node2"

def test_edge_missing_field(basic_edge_data):
    del basic_edge_data["source"]  # Delete a required field without default
    with pytest.raises(ValidationError):
        Edge(**basic_edge_data)

# Tests for EntityEntityEdge
def test_entity_entity_edge_creation(basic_edge_data, statement_data):
    statement = Statement(**statement_data)
    entity_edge_data = {
        **basic_edge_data,
        "relation_type": "COLLABORATES_WITH",
        "statement": statement.statement,  # Use statement text
        "source_statement_id": "stmt_1",
        "temporal_validity_valid_at": datetime.now(),
        "temporal_validity_invalid_at": datetime.now(),
    }
    entity_edge = EntityEntityEdge(**entity_edge_data)
    assert entity_edge.relation_type == "COLLABORATES_WITH"
    assert entity_edge.statement == "This is a test statement."

# Tests for ChunkEdge
def test_chunk_edge_creation(basic_edge_data):
    chunk_edge = ChunkEdge(**basic_edge_data)
    assert chunk_edge.id == "edge1"

# Tests for ChunkEntityEdge
def test_chunk_entity_edge_creation(basic_edge_data):
    chunk_entity_edge = ChunkEntityEdge(**basic_edge_data)
    assert chunk_entity_edge.id == "edge1"

# Tests for Node
def test_node_creation(basic_node_data):
    node = Node(**basic_node_data)
    assert node.id == "node1"
    assert node.name == "Test Node"

def test_node_missing_field(basic_node_data):
    del basic_node_data["name"]
    with pytest.raises(ValidationError):
        Node(**basic_node_data)

# Tests for DialogueNode
def test_dialogue_node_creation(basic_node_data):
    dialogue_node_data = {
        **basic_node_data,
        "ref_id": "dialog_1",
        "content": "This is a test dialogue.",
        "temporal_validity_valid_at": datetime.now(),
        "temporal_validity_invalid_at": datetime.now(),
        "dialog_embedding": [0.1, 0.2, 0.3],
    }
    dialogue_node = DialogueNode(**dialogue_node_data)
    assert dialogue_node.content == "This is a test dialogue."
    assert dialogue_node.ref_id == "dialog_1"

# Tests for ExtractedEntityNode
def test_extracted_entity_node_creation(basic_node_data):
    entity_node_data = {
        **basic_node_data,
        "entity_idx": 1,
        "statement_id": "stmt_1",
        "entity_type": "PERSON",
        "description": "A test entity.",
        "aliases": ["Testy", "McTestFace"],
        "name_embedding": [0.1, 0.2, 0.3],
        "fact_summary": "This is a fact summary about the entity.",
    }
    entity_node = ExtractedEntityNode(**entity_node_data)
    assert entity_node.entity_type == "PERSON"
    assert entity_node.aliases[0] == "Testy"
    assert entity_node.entity_idx == 1