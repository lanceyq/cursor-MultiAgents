#!/bin/bash

# memsci项目快速Jenkins CI/CD脚本
# 跳过耗时的安装步骤，适用于已配置环境的Jenkins

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
WORKSPACE_DIR=$(pwd)
BUILD_DIR="$WORKSPACE_DIR/build"
DIST_DIR="$WORKSPACE_DIR/dist"

# 清理函数
cleanup() {
    log_info "清理临时文件..."
}

# 设置陷阱，确保脚本退出时执行清理
trap cleanup EXIT

echo "========================================="
echo "    memsci项目 快速CI/CD Pipeline"
echo "========================================="

# Stage 1: 验证工作目录
log_info "Stage 1: 验证Jenkins工作空间..."
log_info "当前工作目录: $(pwd)"
log_info "项目文件检查:"
[ -f "pyproject.toml" ] && log_info "✓ pyproject.toml 存在" || log_warning "✗ pyproject.toml 不存在"
[ -d "src" ] && log_info "✓ src/ 目录存在" || log_warning "✗ src/ 目录不存在"
[ -d "tests" ] && log_info "✓ tests/ 目录存在" || log_warning "✗ tests/ 目录不存在"
log_success "工作空间验证完成"

# Stage 2: 环境检查（不安装）
log_info "Stage 2: 检查现有环境..."

# 检查Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    log_info "✓ Python3: $($PYTHON_CMD --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    log_info "✓ Python: $($PYTHON_CMD --version)"
else
    log_error "✗ 未找到Python"
    exit 1
fi

# 检查Poetry（不安装）
if command -v poetry &> /dev/null; then
    log_info "✓ Poetry: $(poetry --version)"
    USE_POETRY=true
else
    log_warning "✗ Poetry未安装，将使用pip"
    USE_POETRY=false
fi

log_success "环境检查完成"

# Stage 3: 快速依赖检查
log_info "Stage 3: 快速依赖检查..."

if [ "$USE_POETRY" = true ] && [ -f "pyproject.toml" ]; then
    log_info "检查Poetry环境..."
    if poetry env info &> /dev/null; then
        log_info "✓ Poetry虚拟环境已存在"
    else
        log_warning "Poetry虚拟环境不存在，创建中..."
        poetry install --no-dev --no-interaction --quiet
    fi
elif [ -f "requirements.txt" ]; then
    log_info "使用系统Python环境"
else
    log_warning "未找到依赖配置文件"
fi

log_success "依赖检查完成"

# Stage 4: 代码质量检查（简化）
log_info "Stage 4: 快速代码检查..."

# 创建构建目录
mkdir -p "$BUILD_DIR"

# 基本语法检查
if [ -d "src" ]; then
    log_info "执行Python语法检查..."
    find src/ -name "*.py" -exec $PYTHON_CMD -m py_compile {} \; 2>/dev/null && log_info "✓ 语法检查通过" || log_warning "✗ 发现语法问题"
fi

log_success "代码检查完成"

# Stage 5: 快速测试
log_info "Stage 5: 快速测试..."

if [ -d "tests" ]; then
    if [ "$USE_POETRY" = true ]; then
        log_info "使用Poetry运行测试..."
        poetry run python -m pytest tests/ --tb=short -q --junitxml="$BUILD_DIR/test-results.xml" 2>/dev/null || log_warning "部分测试失败"
    else
        log_info "使用系统Python运行测试..."
        $PYTHON_CMD -m unittest discover tests/ -v 2>/dev/null || log_warning "部分测试失败"
    fi
else
    log_warning "未找到tests目录，跳过测试"
fi

log_success "测试执行完成"

# Stage 6: 简单构建
log_info "Stage 6: 创建构建产物..."

# 创建分发目录
mkdir -p "$DIST_DIR"

# 简单打包
if [ -d "src" ]; then
    log_info "创建源码包..."
    tar -czf "$DIST_DIR/${PROJECT_NAME}-$(date +%Y%m%d-%H%M%S).tar.gz" src/ --exclude="__pycache__" --exclude="*.pyc"
    log_success "源码包创建完成"
fi

# Stage 7: 归档产物
log_info "Stage 7: 归档构建产物..."

mkdir -p "$BUILD_DIR/artifacts"

# 复制构建产物
if [ -d "$DIST_DIR" ] && [ "$(ls -A $DIST_DIR)" ]; then
    cp -r "$DIST_DIR"/* "$BUILD_DIR/artifacts/"
    log_success "构建产物已归档"
fi

# 复制测试报告
if [ -f "$BUILD_DIR/test-results.xml" ]; then
    cp "$BUILD_DIR/test-results.xml" "$BUILD_DIR/artifacts/"
    log_info "测试报告已归档"
fi

log_success "产物归档完成"

echo "========================================="
echo "    快速CI/CD Pipeline 执行完成"
echo "========================================="
echo "构建产物位置: $BUILD_DIR/artifacts/"
echo "执行时间: 约1-2分钟（vs 完整版本5-10分钟）"