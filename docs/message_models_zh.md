# 消息模型文档

本文档详细描述了`src/models/message_models.py`中使用的Pydantic模型。这些模型定义了对话、陈述及其相关元数据的数据结构。

## ConversationMessage

代表来自“用户”或“AI”的单条消息。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `role` | `str` | 发言者的角色（例如，“用户”、“AI”）。 |
| `msg` | `str` | 消息的文本内容。 |

---

## TemporalValidityRange

代表陈述的时间有效性范围。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `valid_at` | `Optional[str]` | 陈述有效期的开始日期，格式为“YYYY-MM-DD”或“None”。 |
| `invalid_at` | `Optional[str]` | 陈述有效期的结束日期，格式为“YYYY-MM-DD”或“None”。 |

---

## Statement

代表具有陈述类型和时间信息的陈述。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `statement` | `str` | 陈述的文本内容。 |
| `stmt_type` | `StatementType` | 陈述的类型。 |
| `temporal_info` | `TemporalInfo` | 陈述的时间信息。 |
| `relevence_info` | `RelevenceInfo` | 陈述的相关性信息。 |
| `temporal_validity` | `Optional[TemporalValidityRange]` | 陈述的时间有效性范围。 |

---

## ConversationContext

代表对话历史，解析为消息列表。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `msgs` | `List[ConversationMessage]` | 对话中的消息列表。 |

---

## Chunk

对话上下文中的文本块。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `id` | `str` | 块的唯一标识符。 |
| `text` | `List[ConversationMessage]` | 块中的消息列表。 |
| `content` | `str` | 块的内容（字符串形式）。 |
| `statements` | `List[Statement]` | 块中的陈述列表。 |
| `metadata` | `dict[str, Any]` | 块的附加元数据。 |

---

## DialogData

代表对话记录的整个数据结构。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `id` | `str` | 对话的唯一标识符。 |
| `context` | `ConversationContext` | 完整的对话上下文（单个字符串）。 |
| `ref_id` | `str` | 引用外部对话ID。用于链接到原始对话。 |
| `created_at` | `datetime` | 创建对话时的时间戳。 |
| `metadata` | `Dict[str, str]` | 对话的附加元数据。 |
| `chunks` | `List[Chunk]` | 来自对话上下文的块列表。 |