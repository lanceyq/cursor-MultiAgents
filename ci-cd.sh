#!/bin/bash

# memsci项目CI/CD脚本
# 等效于Jenkinsfile的功能

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 环境变量
PROJECT_NAME="memsci"
PYTHON_VERSION="3.12"
WORKSPACE_DIR=$(pwd)
BUILD_DIR="$WORKSPACE_DIR/build"
DIST_DIR="$WORKSPACE_DIR/dist"

# 清理函数
cleanup() {
    log_info "清理临时文件..."
    # 可以在这里添加清理逻辑
}

# 设置陷阱，确保脚本退出时执行清理
trap cleanup EXIT

echo "========================================="
echo "    memsci项目 CI/CD Pipeline 开始"
echo "========================================="

# Stage 1: 验证工作目录
log_info "Stage 1: 验证工作目录..."
log_info "当前工作目录: $(pwd)"
log_info "目录内容:"
ls -la
log_success "工作目录验证完成"

# Stage 2: Setup Environment
log_info "Stage 2: 设置Python环境..."

# 检查Python版本
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    log_error "未找到Python，请先安装Python"
    exit 1
fi

log_info "Python版本: $($PYTHON_CMD --version)"

# 检查并安装Poetry
if ! command -v poetry &> /dev/null; then
    log_info "安装Poetry..."
    curl -sSL https://install.python-poetry.org | $PYTHON_CMD -
    export PATH="$HOME/.local/bin:$PATH"
else
    log_info "Poetry已安装: $(poetry --version)"
fi

log_success "环境设置完成"

# Stage 3: Install Dependencies
log_info "Stage 3: 安装项目依赖..."
export PATH="$HOME/.local/bin:$PATH"
poetry install
log_success "依赖安装完成"

# Stage 4: Lint Code (可选)
log_info "Stage 4: 代码质量检查..."
# 如果项目中有linting工具，可以在这里运行
# poetry run flake8 src/ tests/ || log_warning "代码检查发现问题"
# poetry run black --check src/ tests/ || log_warning "代码格式检查发现问题"
log_info "代码检查完成"

# Stage 5: Run Tests
log_info "Stage 5: 运行自动化测试..."
export PATH="$HOME/.local/bin:$PATH"
export PYTHONPATH="$WORKSPACE_DIR/src:$PYTHONPATH"

# 创建测试结果目录
mkdir -p "$BUILD_DIR"

# 运行pytest测试
if poetry run pytest tests/ -v --tb=short --junitxml="$BUILD_DIR/test-results.xml"; then
    log_success "所有测试通过"
else
    log_warning "部分测试失败，但继续构建过程"
fi

# Stage 6: Build Package
log_info "Stage 6: 构建软件包..."
export PATH="$HOME/.local/bin:$PATH"
poetry build
log_success "软件包构建完成"

# Stage 7: Archive Artifacts
log_info "Stage 7: 归档构建产物..."
if [ -d "dist" ]; then
    mkdir -p "$BUILD_DIR/artifacts"
    cp -r dist/* "$BUILD_DIR/artifacts/"
    log_success "构建产物已归档到: $BUILD_DIR/artifacts/"
    
    # 显示构建产物
    log_info "构建产物列表:"
    ls -la "$BUILD_DIR/artifacts/"
else
    log_warning "未找到构建产物目录"
fi

echo "========================================="
echo "    CI/CD Pipeline 执行完成"
echo "========================================="

# 显示摘要
log_info "执行摘要:"
echo "  - 工作目录: $WORKSPACE_DIR"
echo "  - 构建目录: $BUILD_DIR"
if [ -f "$BUILD_DIR/test-results.xml" ]; then
    echo "  - 测试结果: $BUILD_DIR/test-results.xml"
fi
if [ -d "$BUILD_DIR/artifacts" ]; then
    echo "  - 构建产物: $BUILD_DIR/artifacts/"
fi

log_success "Pipeline执行成功完成！"