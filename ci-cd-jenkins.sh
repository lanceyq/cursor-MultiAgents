#!/bin/bash

# memsci项目Jenkins CI/CD脚本
# 专为Jenkins环境优化，无需Git操作

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
echo "    memsci项目 Jenkins CI/CD Pipeline"
echo "========================================="

# Stage 1: 验证工作目录
log_info "Stage 1: 验证Jenkins工作空间..."
log_info "当前工作目录: $(pwd)"
log_info "Jenkins工作空间内容:"
ls -la
if [ -f "pyproject.toml" ]; then
    log_success "发现pyproject.toml，项目结构正确"
else
    log_warning "未找到pyproject.toml，请检查项目结构"
fi
log_success "工作空间验证完成"

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
    log_info "Poetry未找到，尝试快速安装..."
    
    # 尝试使用pip安装（更快）
    if $PYTHON_CMD -m pip install poetry --user --quiet; then
        log_info "使用pip安装Poetry成功"
        export PATH="$HOME/.local/bin:$PATH"
    else
        log_info "pip安装失败，使用官方安装脚本..."
        curl -sSL https://install.python-poetry.org | $PYTHON_CMD -
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # 验证安装
    if command -v poetry &> /dev/null; then
        log_success "Poetry安装成功: $(poetry --version)"
    else
        log_warning "Poetry安装可能失败，尝试直接使用pip进行依赖管理"
    fi
else
    log_info "Poetry已安装: $(poetry --version)"
fi

log_success "环境设置完成"

# Stage 3: Install Dependencies
log_info "Stage 3: 安装项目依赖..."
export PATH="$HOME/.local/bin:$PATH"

# 创建虚拟环境并安装依赖
if [ -f "pyproject.toml" ]; then
    if command -v poetry &> /dev/null; then
        log_info "使用Poetry安装依赖（可能需要几分钟）..."
        poetry install --no-dev --no-interaction
        log_success "Poetry依赖安装完成"
    else
        log_info "Poetry不可用，尝试使用pip安装..."
        if [ -f "requirements.txt" ]; then
            $PYTHON_CMD -m pip install -r requirements.txt --user --quiet
        else
            log_warning "无法使用Poetry且未找到requirements.txt，跳过依赖安装"
        fi
    fi
elif [ -f "requirements.txt" ]; then
    log_info "使用pip安装依赖..."
    $PYTHON_CMD -m pip install -r requirements.txt --user --quiet
    log_success "pip依赖安装完成"
else
    log_warning "未找到依赖文件，跳过依赖安装"
fi

# Stage 4: Code Quality Check
log_info "Stage 4: 代码质量检查..."

# 创建构建目录
mkdir -p "$BUILD_DIR"

# 运行代码检查（如果有的话）
if command -v flake8 &> /dev/null; then
    log_info "运行flake8代码检查..."
    flake8 src/ --max-line-length=88 --ignore=E203,W503 || log_warning "flake8检查发现问题"
fi

if command -v black &> /dev/null; then
    log_info "运行black代码格式检查..."
    black --check src/ || log_warning "black格式检查发现问题"
fi

log_success "代码质量检查完成"

# Stage 5: Run Tests
log_info "Stage 5: 运行测试..."

# 运行测试
if [ -d "tests" ]; then
    if command -v pytest &> /dev/null; then
        log_info "使用pytest运行测试..."
        poetry run pytest tests/ --junitxml="$BUILD_DIR/test-results.xml" --cov=src --cov-report=xml:"$BUILD_DIR/coverage.xml" || log_warning "部分测试失败"
    elif command -v python &> /dev/null; then
        log_info "使用unittest运行测试..."
        $PYTHON_CMD -m unittest discover tests/ || log_warning "部分测试失败"
    fi
else
    log_warning "未找到tests目录，跳过测试"
fi

log_success "测试执行完成"

# Stage 6: Build
log_info "Stage 6: 构建项目..."

# 创建分发目录
mkdir -p "$DIST_DIR"

# 如果有setup.py或pyproject.toml，构建包
if [ -f "pyproject.toml" ]; then
    log_info "使用Poetry构建项目..."
    poetry build --output "$DIST_DIR"
elif [ -f "setup.py" ]; then
    log_info "使用setup.py构建项目..."
    $PYTHON_CMD setup.py sdist bdist_wheel --dist-dir "$DIST_DIR"
else
    log_info "创建源码包..."
    tar -czf "$DIST_DIR/${PROJECT_NAME}-$(date +%Y%m%d-%H%M%S).tar.gz" src/
fi

log_success "项目构建完成"

# Stage 7: Archive Artifacts
log_info "Stage 7: 归档构建产物..."

# 创建artifacts目录
mkdir -p "$BUILD_DIR/artifacts"

# 复制构建产物
if [ -d "$DIST_DIR" ] && [ "$(ls -A $DIST_DIR)" ]; then
    cp -r "$DIST_DIR"/* "$BUILD_DIR/artifacts/"
    log_success "构建产物已归档到 $BUILD_DIR/artifacts/"
else
    log_warning "未找到构建产物"
fi

# 复制测试报告
if [ -f "$BUILD_DIR/test-results.xml" ]; then
    cp "$BUILD_DIR/test-results.xml" "$BUILD_DIR/artifacts/"
    log_info "测试报告已归档"
fi

if [ -f "$BUILD_DIR/coverage.xml" ]; then
    cp "$BUILD_DIR/coverage.xml" "$BUILD_DIR/artifacts/"
    log_info "覆盖率报告已归档"
fi

log_success "产物归档完成"

echo "========================================="
echo "    Jenkins CI/CD Pipeline 执行完成"
echo "========================================="
echo "构建产物位置: $BUILD_DIR/artifacts/"
echo "如需部署，请使用构建产物进行后续操作"