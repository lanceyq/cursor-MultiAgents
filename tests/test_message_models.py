import pytest
from pydantic import ValidationError
from datetime import datetime
from uuid import UUID

from models.message_models import (
    ConversationMessage,
    ConversationContext,
    Chunk,
    DialogData,
)

# Test data for ConversationMessage
MSG_USER = {"role": "用户", "msg": "Hello, AI!"}
MSG_AI = {"role": "AI", "msg": "Hello, user!"}

# Test for ConversationMessage

def test_conversation_message_creation():
    """Test successful creation of a ConversationMessage."""
    msg = ConversationMessage(**MSG_USER)
    assert msg.role == MSG_USER["role"]
    assert msg.msg == MSG_USER["msg"]

def test_conversation_message_missing_fields():
    """Test that ConversationMessage raises an error if fields are missing."""
    with pytest.raises(ValidationError):
        ConversationMessage(role="用户")  # Missing msg
    with pytest.raises(ValidationError):
        ConversationMessage(msg="Hello")  # Missing role

# Test for ConversationContext

def test_conversation_context_creation():
    """Test successful creation of a ConversationContext."""
    messages = [ConversationMessage(**MSG_USER), ConversationMessage(**MSG_AI)]
    context = ConversationContext(msgs=messages)
    assert len(context.msgs) == 2
    assert context.msgs[0].msg == MSG_USER["msg"]

def test_conversation_context_with_invalid_message_type():
    """Test that ConversationContext validates the type of messages."""
    with pytest.raises(ValidationError):
        ConversationContext(msgs=[{"msg": "Missing role"}])

# Test for Chunk

def test_chunk_creation_and_content():
    """Test successful creation of a Chunk and its content property."""
    messages = [ConversationMessage(**MSG_USER), ConversationMessage(**MSG_AI)]
    chunk = Chunk.from_messages(messages)
    assert len(chunk.text) == 2
    assert isinstance(UUID(chunk.id, version=4), UUID)
    expected_content = "用户: Hello, AI!\nAI: Hello, user!"
    assert chunk.content == expected_content

def test_chunk_from_messages_with_metadata():
    """Test creating a Chunk with metadata."""
    messages = [ConversationMessage(**MSG_USER)]
    metadata = {"source": "test"}
    chunk = Chunk.from_messages(messages, metadata=metadata)
    assert chunk.metadata["source"] == "test"

# Test for DialogData

def test_dialog_data_creation():
    """Test successful creation of DialogData with default values."""
    context = ConversationContext(msgs=[ConversationMessage(**MSG_USER)])
    dialog = DialogData(context=context, ref_id="test_ref_123", group_id="test_group_1")
    assert isinstance(UUID(dialog.id, version=4), UUID)
    assert isinstance(dialog.created_at, datetime)
    assert dialog.ref_id == "test_ref_123"
    assert dialog.group_id == "test_group_1"
    assert dialog.context.msgs[0].role == "用户"

def test_dialog_data_content_property():
    """Test the content property of DialogData."""
    context = ConversationContext(msgs=[ConversationMessage(**MSG_USER), ConversationMessage(**MSG_AI)])
    dialog = DialogData(context=context, ref_id="test_ref_456", group_id="test_group_2")
    content = dialog.content
    assert "用户: Hello, AI!" in content
    assert "AI: Hello, user!" in content

def test_dialog_data_missing_required_fields():
    """Test that DialogData raises an error if required fields are missing."""
    with pytest.raises(ValidationError):
        DialogData(ref_id="123")  # Missing context
    with pytest.raises(ValidationError):
        context = ConversationContext(msgs=[])
        DialogData(context=context)  # Missing ref_id