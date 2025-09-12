# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个为用户"秋芝"设计的多代理个人助理系统。系统由5个专业化AI代理组成，通过协调工作流程提供全面的日常生活协助。

## 常用命令

### 运行系统
```bash
# 运行多代理系统主程序
python main.py

# 使用UTF-8编码运行（推荐用于中文内容）
PYTHONIOENCODING=utf-8 python main.py
```

### 系统状态检查
```bash
# 检查所有组件是否正确初始化
python -c "from main import PersonalAssistant; assistant = PersonalAssistant()"
```

## 架构概览

### 核心组件
- **PersonalAssistant** (`main.py`): 管理所有代理的主控制器
- **BaseAgent** (`src/agents/base_agent.py`): 所有代理的抽象基类
- **WorkflowManager** (`src/utils/workflow_manager.py`): 管理代理执行序列
- **ConfigManager** (`src/utils/config_manager.py`): 集中配置管理
- **FileManager** (`src/utils/file_manager.py`): 文件和数据管理

### 五大代理系统
1. **NewsAgent** (`src/agents/news_agent.py`): 每日新闻收集和简报
2. **OutfitAgent** (`src/agents/outfit_agent.py`): 基于天气的时尚推荐
3. **DailyReportAgent** (`src/agents/daily_report_agent.py`): 工作报告生成
4. **CoachAgent** (`src/agents/coach_agent.py`): 健康管理和运动建议
5. **ReflectionAgent** (`src/agents/reflection_agent.py`): 深度反思和个人成长分析

### 关键设计模式
- **多代理模式**: 每个代理都有特定职责
- **工作流驱动执行**: 代理按定义序列执行并处理依赖关系
- **模板化内容生成**: 使用Markdown模板标准化输出
- **MCP工具集成**: 利用外部工具增强功能

## 配置系统

### 配置文件
- `config/agent_config.json`: 代理特定配置
- `config/workflow_config.json`: 工作流定义和触发器
- `config/user_preferences.json`: 用户偏好和设置

### 用户档案数据
- `aboutme/personal_info.json`: 基本用户信息和生活方式
- `aboutme/style_preferences.json`: 时尚和风格偏好
- `aboutme/health_goals.json`: 健康和健身目标
- `aboutme/personality_traits.json`: 性格和认知特征
- `aboutme/work_profile.json`: 职业和工作相关信息

## 模板系统

### 模板文件
- `templates/news_template.md`: 新闻简报格式
- `templates/outfit_template.md`: 时尚推荐格式
- `templates/report_template.md`: 日报格式
- `templates/reflection_template.md`: 反思报告格式

## 数据管理

### 目录结构
```
data/
├── daily_records/    # 每日执行记录
├── history/          # 用于分析的历史数据
└── analytics/        # 分析和洞察
```

## MCP工具集成

系统集成多个MCP（模型上下文协议）工具：
- **Firecrawl**: 网页抓取和内容提取
- **天气API**: 实时天气信息
- **图像生成**: Jimeng用于创建服装图像
- **Lark**: 企业通信和文档管理

## 开发说明

### 代理开发
- 所有代理都继承自`BaseAgent`类
- 实现具有特定代理逻辑的`execute()`方法
- 使用模板系统保持输出格式一致
- 通过工作流管理器处理依赖关系

### 配置管理
- 使用`ConfigManager`访问配置数据
- 用户偏好以JSON格式存储
- 代理配置支持动态更新

### 文件管理
- 使用`FileManager`进行文件操作和模板渲染
- 每次执行时自动创建每日文件夹
- 历史数据按日期组织用于分析

### 错误处理
- 系统包含全面的错误处理和日志记录
- 工作流管理器支持失败步骤的重试机制
- 代理执行失败会被记录，但不会停止整个工作流

## 系统初始化

系统需要正确初始化：
1. 配置管理器（加载用户偏好和代理配置）
2. 文件管理器（设置目录结构和模板）
3. 工作流管理器（需要配置和文件管理器作为依赖）
4. 单个代理（每个都需要配置和文件管理器）

创建`PersonalAssistant`新实例时，确保所有依赖都正确初始化以避免初始化错误。