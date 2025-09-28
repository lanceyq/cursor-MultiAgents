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

## 依赖安装加速与缓存复用

为支持“每次都新建并删除虚拟环境”的自动化测试场景，脚本已集成镜像源、持久缓存以及本地 wheel 仓库，显著缩短每次安装时间。

- 镜像源配置（已内置，亦可覆盖）：
  - `PIP_INDEX_URL`（默认 `https://pypi.tuna.tsinghua.edu.cn/simple`）
  - `PIP_EXTRA_INDEX_URL`（默认 `https://pypi.org/simple`）

- 持久缓存目录（推荐设置为 Jenkins 不会清理的路径）：
  - `CACHE_DIR`：默认 `~/.cache/memsci`，脚本会自动将 `PIP_CACHE_DIR` 设置为 `CACHE_DIR/pip`、`POETRY_CACHE_DIR` 设置为 `CACHE_DIR/poetry`
  - 示例：
    - Windows Agent：`set CACHE_DIR=D:\jenkins-cache\memsci`
    - Linux Agent：`export CACHE_DIR=/var/cache/jenkins/memsci`

- 本地 wheel 仓库：
  - 脚本会使用 `poetry export -f requirements.txt` 生成依赖清单，并在 `CACHE_DIR/wheels` 预编译 wheels（`pip wheel --prefer-binary`）
  - 安装阶段优先使用本地 wheel 仓库（`pip install --no-index --find-links=CACHE_DIR/wheels -r requirements.txt`），避免重复下载与编译

- 流程效果：
  - 即使每次构建都新建/删除 venv，依赖安装将主要命中持久缓存与本地 wheels，实现快速安装
  - 若依赖版本更新，仅编译/下载变化部分，其余依赖走缓存

- Jenkins 注意事项：
  - 若使用 `cleanWs()`，务必确保 `CACHE_DIR` 指向工作空间之外的持久目录，以免缓存被清理
  - 可以在 Pipeline 的环境变量中统一配置上述变量，确保不同 Stage 下生效

示例（Windows Pipeline 执行批处理）：

```bat
set CACHE_DIR=D:\jenkins-cache\memsci
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
set PIP_EXTRA_INDEX_URL=https://pypi.org/simple
bash ci-cd-jenkins.sh
```

示例（Linux Agent）：

```bash
export CACHE_DIR=/var/cache/jenkins/memsci
export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
export PIP_EXTRA_INDEX_URL=https://pypi.org/simple
bash ci-cd-jenkins.sh
```

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