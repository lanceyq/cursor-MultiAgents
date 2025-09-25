# Message Models Documentation

This document provides a detailed description of the Pydantic models used in `src/models/message_models.py`. These models define the data structures for conversations, statements, and their associated metadata.

## ConversationMessage

Represents a single message from the '用户' or 'AI'.

| Field | Type | Description |
| --- | --- | --- |
| `role` | `str` | The role of the speaker (e.g., '用户', 'AI'). |
| `msg` | `str` | The text content of the message. |

---

## TemporalValidityRange

Represents the temporal validity range of a statement.

| Field | Type | Description |
| --- | --- | --- |
| `valid_at` | `Optional[str]` | The start date of the statement's validity, in 'YYYY-MM-DD' format or 'None'. |
| `invalid_at` | `Optional[str]` | The end date of the statement's validity, in 'YYYY-MM-DD' format or 'None'. |

---

## Statement

Represents a statement with statement type and temporal information

| Field | Type | Description |
| --- | --- | --- |
| `statement` | `str` | The text content of the statement. |
| `stmt_type` | `StatementType` | The type of the statement. |
| `temporal_info` | `TemporalInfo` | The temporal information of the statement. |
| `relevence_info` | `RelevenceInfo` | The relevence information of the statement. |
| `temporal_validity` | `Optional[TemporalValidityRange]` | The temporal validity range of the statement. |

---

## ConversationContext

Represents the conversation history, parsed into a list of messages.

| Field | Type | Description |
| --- | --- | --- |
| `msgs` | `List[ConversationMessage]` | A list of messages in the conversation. |

---

## Chunk

A chunk of text from the conversation context

| Field | Type | Description |
| --- | --- | --- |
| `id` | `str` | A unique identifier for the chunk. |
| `text` | `List[ConversationMessage]` | A list of messages in the chunk. |
| `content` | `str` | The content of the chunk as a string. |
| `statements` | `List[Statement]` | A list of statements in the chunk. |
| `metadata` | `dict[str, Any]` | Additional metadata for the chunk. |

---

## DialogData

Represents the entire data structure for the dialog record.

| Field | Type | Description |
| --- | --- | --- |
| `id` | `str` | A unique identifier for the dialog. |
| `context` | `ConversationContext` | The full conversation context as a single string. |
| `ref_id` | `str` | Refer to external dialog id. This is used to link to the original dialog. |
| `created_at` | `datetime` | The timestamp when the dialog was created. |
| `metadata` | `Dict[str, str]` | Additional metadata for the dialog. |
| `chunks` | `List[Chunk]` | A list of chunks from the conversation context. |