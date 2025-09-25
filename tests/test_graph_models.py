import pytest
from datetime import datetime
from pydantic import ValidationError

from models.graph_models import (
    Edge,
    EntityEdge,
    ChunkEdge,
    ChunkEntityEdge,
    Node,
    ChunkNode,
    EntityNode,
)
from models.message_models import Statement

# Fixtures for common data
@pytest.fixture
def basic_edge_data():
    return {
        "id": "edge1",
        "source": "node1",
        "target": "node2",
        "groupid": "group1",
        "t_created": datetime.now(),
        "t_expired": datetime.now(),
    }

@pytest.fixture
def basic_node_data():
    return {
        "id": "node1",
        "name": "Test Node",
        "groupid": "group1",
        "t_created": datetime.now(),
        "t_expired": datetime.now(),
    }

@pytest.fixture
def statement_data():
    return {
        "role": "test_speaker",
        "msg": "This is a test statement.",
        "stmt_type": "FACT",
        "temporal_info": "STATIC",
    }

# Tests for Edge
def test_edge_creation(basic_edge_data):
    edge = Edge(**basic_edge_data)
    assert edge.id == "edge1"
    assert edge.source == "node1"
    assert edge.target == "node2"

def test_edge_missing_field(basic_edge_data):
    del basic_edge_data["id"]
    with pytest.raises(ValidationError):
        Edge(**basic_edge_data)

# Tests for EntityEdge
def test_entity_edge_creation(basic_edge_data, statement_data):
    statement = Statement(**statement_data)
    entity_edge_data = {
        **basic_edge_data,
        "relation_type": "COLLABORATES_WITH",
        "statement": statement,
        "fact": "Test fact",
        "t_valid": datetime.now(),
        "t_invalid": datetime.now(),
    }
    entity_edge = EntityEdge(**entity_edge_data)
    assert entity_edge.relation_type == "COLLABORATES_WITH"
    assert entity_edge.statement.role == "test_speaker"

# Tests for ChunkEdge
def test_chunk_edge_creation(basic_edge_data):
    chunk_edge_data = {
        **basic_edge_data,
        "changed_topic": True,
    }
    chunk_edge = ChunkEdge(**chunk_edge_data)
    assert chunk_edge.changed_topic is True

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

# Tests for ChunkNode
def test_chunk_node_creation(basic_node_data):
    chunk_node_data = {
        **basic_node_data,
        "content": "This is a test chunk.",
        "list_of_entities": ["entity1", "entity2"],
        "list_of_edges": ["edge1"],
    }
    chunk_node = ChunkNode(**chunk_node_data)
    assert chunk_node.content == "This is a test chunk."
    assert "entity1" in chunk_node.list_of_entities

# Tests for EntityNode
def test_entity_node_creation(basic_node_data):
    entity_node_data = {
        **basic_node_data,
        "entity_type": "PERSON",
        "entity_embedding": [0.1, 0.2, 0.3],
        "description": "A test entity.",
        "aliases": ["Testy", "McTestFace"],
    }
    entity_node = EntityNode(**entity_node_data)
    assert entity_node.entity_type == "PERSON"
    assert entity_node.aliases[0] == "Testy"