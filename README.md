# MemSci：从对话中提取知识


## 项目介绍

MemSci是一个基于对话数据的知识提取系统。它能够从对话中提取陈述、三元组和时间信息，构建一个知识图谱。

## 入门指南

### 先决条件

- Python 3.12或更高版本
- [Poetry](https://python-poetry.org/)用于依赖管理
- 一个OpenAI API密钥
- Neo4j数据库（用于知识图谱存储）

### 安装

1.  **克隆存储库：**
    ```bash
    git clone <your-repo-url>
    cd memsci
    ```

2.  **使用Poetry安装依赖项：**
    ```bash
    poetry install
    ```

3.  **激活虚拟环境：**
    ```bash
    poetry shell
    ```

4.  **设置环境变量：**

    在项目根目录中创建一个`.env`文件，并添加您的OpenAI API密钥：
    ```
    OPENAI_API_KEY="your-openai-api-key"
    ```

### 使用Conda和Poetry的替代设置

如果您更喜欢使用Conda进行环境管理，可以按照以下步骤操作：

1. **创建并激活新的Conda环境：**
   ```bash
   conda create --name memsci python=3.12
   conda activate memsci
   ```

2. **在Conda环境中安装Poetry：**
   ```bash
   pip install poetry
   ```

3. **配置Poetry以使用Conda环境的site-packages：**
   ```bash
   poetry config virtualenvs.in-project false
   poetry config virtualenvs.path $CONDA_PREFIX/envs
   ```

4. **使用Poetry安装项目依赖项：**
   ```bash
   poetry install
   ```

## 使用方法

### 知识提取和保存（使用 main.py）

要运行完整的知识提取流水线并将结果保存到Neo4j数据库，请执行`main.py`脚本：

```bash
python src/main.py
```

这将执行以下步骤：

1. 从`data/testdata.json`加载示例对话数据
2. 对对话进行分块处理
3. 从分块中提取陈述
4. 生成嵌入向量
5. 提取三元组关系
6. 提取时间信息
7. 创建图节点和边
8. **将所有数据保存到Neo4j数据库**

### 知识搜索（使用 search.py）

要搜索已保存的知识图谱，请使用`search.py`脚本：

```bash
# 混合搜索（关键词 + 语义搜索）
python src/search.py --query "你的搜索查询" --search-type hybrid

# 仅关键词搜索
python src/search.py --query "你的搜索查询" --search-type keyword

# 仅语义搜索
python src/search.py --query "你的搜索查询" --search-type embedding

# 指定搜索结果数量和输出文件
python src/search.py --query "你的搜索查询" --limit 10 --output results.json

# 按组ID过滤搜索结果
python src/search.py --query "你的搜索查询" --group-id "group_123"
```

#### 搜索参数说明：

- `--query, -q`: 搜索查询文本（必需）
- `--search-type, -t`: 搜索类型 (`keyword`, `embedding`, `hybrid`，默认：`hybrid`)
- `--embedding-name, -m`: 嵌入模型配置名称（默认：`openai/nomic-embed-text:v1.5`）
- `--group-id, -g`: 可选的组ID过滤器
- `--limit, -k`: 每种类型的最大结果数（默认：5）
- `--include, -i`: 要搜索的目标类型（`statements`, `dialogues`, `entities`）
- `--output, -o`: 保存搜索结果的JSON文件路径（默认：`search_results.json`）

## 项目结构

```
memsci/
├── .env                # 环境变量（例如，API密钥）
├── README.md           # 本文件
├── config.json         # LLM和嵌入模型的配置
├── data/
│   └── testdata.json   # 示例对话数据
├── docs/               # 项目文档
├── pyproject.toml      # Poetry的项目依赖项
└── src/
    ├── main.py         # 运行流水线的主脚本
    ├── data_preprocessing/ # 用于数据分块和预处理的脚本
    ├── database/       # Neo4j连接器
    ├── knowledge_extraction/ # 陈述和三元组提取的核心逻辑
    ├── llm_tools/      # 与LLM和嵌入模型交互的客户端
    ├── models/         # 用于数据结构的Pydantic模型
    ├── ontology/       # 定义知识图谱的本体
    └── utils/          # 辅助函数和提示
```

## 配置

可以在`config.json`文件中配置LLM和嵌入模型。您可以指定来自OpenAI等提供商的的不同模型。

## 文档

有关更详细的信息，请参阅`docs/`目录中的文档：

- `ontology.md`: 描述用于知识表示的本体。
- `configuration.md`: 提供有关配置应用程序的详细信息。
- `benchmark.md`: 包含基准测试结果。
- `quickstart.md`: 快速入门指南。