# memsci项目 CI/CD 脚本使用指南

本文档介绍如何使用shell脚本替代Jenkinsfile来执行CI/CD流程。

## 文件说明

### 1. `ci-cd.sh` (Linux/Unix版本)
- 适用于Linux、macOS等Unix系统
- 包含完整的CI/CD流程
- 支持彩色输出和错误处理

### 2. `ci-cd.bat` (Windows版本)
- 适用于Windows系统
- 功能与Linux版本相同
- 使用Windows批处理语法

### 3. `jenkins-shell-pipeline.groovy` (简化Jenkins Pipeline)
- 简化的Jenkins Pipeline文件
- 直接调用shell脚本执行CI/CD
- 自动检测操作系统并选择合适的脚本

## 使用方法

### 方法一：直接执行脚本

#### Linux/Unix系统：
```bash
# 给脚本执行权限
chmod +x ci-cd.sh

# 执行脚本
./ci-cd.sh
```

#### Windows系统：
```cmd
# 直接执行批处理文件
ci-cd.bat
```

### 方法二：在Jenkins中使用

#### 选项1：使用简化的Pipeline
1. 在Jenkins中创建新的Pipeline项目
2. 在Pipeline配置中选择"Pipeline script from SCM"
3. 设置Git仓库URL和凭据
4. 将Script Path设置为：`jenkins-shell-pipeline.groovy`

#### 选项2：直接在Jenkins中执行脚本
1. 创建Freestyle项目
2. 在"Build Steps"中添加"Execute shell"（Linux）或"Execute Windows batch command"（Windows）
3. 输入以下命令：

**Linux/Unix:**
```bash
chmod +x ci-cd.sh
./ci-cd.sh
```

**Windows:**
```cmd
ci-cd.bat
```

## 脚本功能

### CI/CD流程包括：

1. **源代码检出**
   - 克隆或更新Git仓库
   - 切换到指定分支

2. **环境设置**
   - 检查Python版本
   - 安装Poetry（如果未安装）

3. **依赖安装**
   - 使用Poetry安装项目依赖

4. **代码质量检查**
   - 预留linting工具接口
   - 可扩展添加flake8、black等工具

5. **自动化测试**
   - 运行pytest测试
   - 生成JUnit格式的测试报告

6. **软件包构建**
   - 使用Poetry构建Python包

7. **构建产物归档**
   - 保存构建产物到指定目录
   - 生成构建摘要

### 输出文件

- `build/test-results.xml`: JUnit格式的测试结果
- `build/artifacts/`: 构建产物目录
- `dist/`: Poetry构建的Python包

## 环境要求

### 必需软件：
- Python 3.12+
- Git
- curl（用于安装Poetry）

### 可选软件：
- Poetry（脚本会自动安装）
- 代码质量检查工具（flake8、black等）

## 配置选项

### 环境变量
可以通过修改脚本开头的环境变量来自定义配置：

```bash
PROJECT_NAME="memsci"
PYTHON_VERSION="3.12"
WORKSPACE_DIR=$(pwd)
BUILD_DIR="$WORKSPACE_DIR/build"
DIST_DIR="$WORKSPACE_DIR/dist"
```

### Git仓库配置
如果需要修改Git仓库地址，请编辑脚本中的以下行：
```bash
git clone https://gitclone.com/github.com/lanceyq/cursor-MultiAgents.git temp_repo
```

## 故障排除

### 常见问题：

1. **Python未找到**
   - 确保Python已安装并在PATH中
   - 检查Python版本是否符合要求

2. **Poetry安装失败**
   - 检查网络连接
   - 确保curl可用
   - 手动安装Poetry

3. **测试失败**
   - 检查测试依赖是否正确安装
   - 查看详细的测试输出
   - 确保环境变量正确设置

4. **Git操作失败**
   - 检查网络连接
   - 验证Git凭据
   - 尝试使用SSH而非HTTPS

### 调试模式
在脚本开头添加以下行来启用调试模式：
```bash
set -x  # 显示执行的每个命令
```

## 与Jenkinsfile的对比

| 特性 | Jenkinsfile | Shell脚本 |
|------|-------------|-----------|
| 可移植性 | Jenkins专用 | 通用，可在任何环境运行 |
| 调试难度 | 较难 | 容易 |
| 执行速度 | 较慢（Jenkins开销） | 快速 |
| 功能丰富度 | 丰富（插件支持） | 基础但足够 |
| 维护复杂度 | 较高 | 较低 |

## 扩展建议

1. **添加代码质量检查**：
   ```bash
   poetry run flake8 src/ tests/
   poetry run black --check src/ tests/
   ```

2. **添加安全扫描**：
   ```bash
   poetry run safety check
   poetry run bandit -r src/
   ```

3. **添加覆盖率报告**：
   ```bash
   poetry run pytest --cov=src tests/
   ```

4. **添加通知功能**：
   - 邮件通知
   - Slack通知
   - 企业微信通知

这种方式提供了更大的灵活性和可控性，同时保持了CI/CD流程的完整性。