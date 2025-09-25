# 配置文档

本文档介绍了MemSci项目中用于管理各种服务终端和模型配置的`config.json`配置文件。

## 概述

`config.json`文件包含以下配置设置：
- 大型语言模型（LLM）
- 嵌入模型
- Neo4j数据库连接
- 文本分块策略

## 配置结构

### LLM配置（`llm_list`）

定义可用的大型语言模型及其API终端。

```json
"llm_list": [
  {
    "llm_name": "openai/qwen2.5-14b",
    "api_base": "http://43.137.4.24:9090/v1"
  }
]
```

**字段：**
- `llm_name` (string): LLM模型的标识符
- `api_base` (string): API终端的基本URL

**可用模型：**
- `openai/qwen2.5-14b`
- `openai/qwen3-14b`
- `openai/deepseek-r1-0528-qwen3-8b`

### 嵌入配置（`embeddding_list`）

定义用于文本向量化的嵌入模型。

```json
"embeddding_list": [
  {
    "embedding_name": "openai/nomic-embed-text:v1.5",
    "api_base": "http://119.45.239.97:11434/v1",
    "dimension": 768
  }
]
```

**字段：**
- `embedding_name` (string): 嵌入模型的标识符
- `api_base` (string): 嵌入API的基本URL
- `dimension` (integer): 嵌入的向量维度

### Neo4j数据库配置（`neo4j`）

Neo4j图形数据库的数据库连接设置。

```json
"neo4j": {
  "uri": "bolt://1.94.111.67:7687",
  "username": "neo4j"
}
```

**字段：**
- `uri` (string): 使用Bolt协议的Neo4j数据库连接URI
- `username` (string): 数据库用户名（密码应通过环境变量设置）

### 分块配置（`chunker_list`）

定义不同的文本分块策略及其参数。

#### SemanticChunker

基于语义相似性对文本进行分块。

```json
{
  "chunker_strategy": "SemanticChunker",
  "embedding_model": "BAAI/bge-m3",
  "chunk_size": 2048,
  "threshold": 0.8,
  "min_sentences": 10,
  "language": "zh",
  "skip_window": 1
}
```

**参数：**
- `chunker_strategy`: "SemanticChunker"
- `embedding_model`: 用于语义相似性计算的模型
- `chunk_size`: 每个分块的最大令牌数
- `threshold`: 分块边界的相似性阈值（0-1）
- `min_sentences`: 每个分块所需的最少句子数
- `language`: 目标语言（"zh"表示中文）
- `skip_window`: 跳跃和合并窗口大小

#### RecursiveChunker

使用递归拆分规则对文本进行分块。

```json
{
  "chunker_strategy": "RecursiveChunker",
  "embedding_model": "BAAI/bge-m3",
  "chunk_size": 2048,
  "threshold": 0.8,
  "min_sentences": 2,
  "language": "zh",
  "skip_window": 0
}
```

**参数：**
- 与SemanticChunker类似，但具有不同的默认值
- `min_sentences`: 2 (低于SemanticChunker)
- `skip_window`: 0 (禁用)

#### LateChunker

在初始处理后执行分块。

```json
{
  "chunker_strategy": "LateChunker",
  "embedding_model": "all-MiniLM-L6-v2",
  "chunk_size": 2048,
  "min_characters_per_chunk": 24
}
```

**参数：**
- `chunker_strategy`: "LateChunker"
- `embedding_model`: 针对后期分块优化的不同模型
- `chunk_size`: 最大分块大小
- `min_characters_per_chunk`: 每个分块所需的最少字符数

#### NeuralChunker

使用神经网络进行智能分块。

```json
{
  "chunker_strategy": "NeuralChunker",
  "embedding_model": "mirth/chonky_modernbert_base_1",
  "min_characters_per_chunk": 24
}
```

**参数：**
- `chunker_strategy`: "NeuralChunker"
- `embedding_model`: 用于分块的专用神经模型
- `min_characters_per_chunk`: 每个分块的最少字符数

## 用法

配置由`src/utils/helpers.py`中的辅助函数加载：

- `get_model_config(llm_name)`: 检索LLM配置
- `get_embedder_config(embedding_name)`: 检索嵌入配置
- `get_chunker_config(chunker_strategy)`: 检索分块器配置

## 环境变量

一些敏感信息应存储在环境变量中：
- `NEO4J_PASSWORD`: Neo4j数据库密码
- `OPENAI_API_KEY`: OpenAI兼容服务的API密钥

## 注意

- 所有API终端目前都指向内部/开发服务器
- 嵌入列表有一个拼写错误："embeddding_list"应为"embedding_list"
- 分块器配置支持各种用例的不同策略
- 中文（"zh"）是文本处理的主要目标语言