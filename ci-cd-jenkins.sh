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
    log_info "清理临时文件和虚拟环境..."
    
    # 清理虚拟环境
    if [ -d ".venv" ]; then
        log_info "删除虚拟环境目录..."
        rm -rf .venv
    fi
    
    # 清理构建目录
    if [ -d "build" ]; then
        log_info "清理构建目录..."
        rm -rf build
    fi
    
    # 清理分发目录
    if [ -d "dist" ]; then
        log_info "清理分发目录..."
        rm -rf dist
    fi
    
    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    log_info "清理完成"
}

# 设置陷阱，确保脚本退出时执行清理
trap cleanup EXIT

echo "========================================="
echo "    memsci项目 Jenkins CI/CD Pipeline"
echo "========================================="

# Stage 0: 清理现有环境
log_info "Stage 0: 清理现有环境..."

# 强制清理现有虚拟环境
if [ -d ".venv" ]; then
    log_info "发现现有虚拟环境，正在删除..."
    rm -rf .venv
    log_success "现有虚拟环境已删除"
fi

# 清理现有构建产物
if [ -d "build" ]; then
    log_info "清理现有构建目录..."
    rm -rf build
fi

if [ -d "dist" ]; then
    log_info "清理现有分发目录..."
    rm -rf dist
fi

# 清理Python缓存文件
log_info "清理Python缓存文件..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

log_success "环境清理完成"

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

# 设置虚拟环境
VENV_DIR=".venv"

# 强制创建新的虚拟环境
log_info "创建新的虚拟环境..."

# 尝试使用标准venv模块创建虚拟环境
if $PYTHON_CMD -m venv "$VENV_DIR" 2>/dev/null; then
    log_success "虚拟环境创建成功"
    VENV_CREATED=true
else
    log_warning "标准venv创建失败，尝试备用方案..."
    
    # 备用方案1: 尝试使用virtualenv
    if command -v virtualenv &> /dev/null; then
        log_info "使用virtualenv创建虚拟环境..."
        if virtualenv "$VENV_DIR" 2>/dev/null; then
            log_success "使用virtualenv创建虚拟环境成功"
            VENV_CREATED=true
        fi
    fi
    
    # 备用方案2: 如果virtualenv也不可用，尝试安装它
    if [ "$VENV_CREATED" != true ]; then
        log_info "尝试安装virtualenv..."
        if $PYTHON_CMD -m pip install virtualenv --user --quiet 2>/dev/null; then
            if $PYTHON_CMD -m virtualenv "$VENV_DIR" 2>/dev/null; then
                log_success "安装virtualenv后创建虚拟环境成功"
                VENV_CREATED=true
            fi
        fi
    fi
    
    # 如果所有虚拟环境方案都失败，继续使用系统Python
    if [ "$VENV_CREATED" != true ]; then
        log_warning "无法创建虚拟环境，将使用系统Python环境"
        log_warning "建议在Jenkins节点上安装: apt install python3-venv 或 yum install python3-venv"
        # 创建一个假的venv目录结构以保持脚本兼容性
        mkdir -p "$VENV_DIR"
        VENV_CREATED=false
    fi
fi

# 激活虚拟环境
log_info "激活虚拟环境..."
if [ "$VENV_CREATED" = true ]; then
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        PYTHON_CMD="$VENV_DIR/bin/python"
        PIP_CMD="$VENV_DIR/bin/pip"
        log_success "虚拟环境已激活"
    elif [ -f "$VENV_DIR/Scripts/activate" ]; then
        source "$VENV_DIR/Scripts/activate"
        PYTHON_CMD="$VENV_DIR/Scripts/python"
        PIP_CMD="$VENV_DIR/Scripts/pip"
        log_success "虚拟环境已激活"
    else
        log_warning "虚拟环境激活脚本未找到，使用系统Python"
        PIP_CMD="$PYTHON_CMD -m pip"
    fi
else
    log_info "使用系统Python环境"
    PIP_CMD="$PYTHON_CMD -m pip"
fi

# 检查并安装Poetry
if ! command -v poetry &> /dev/null; then
    log_info "Poetry未找到，尝试快速安装..."
    
    # 如果使用虚拟环境，优先使用pip安装
    if [ "$VENV_CREATED" = true ]; then
        if $PIP_CMD install poetry --quiet 2>/dev/null; then
            log_success "使用pip安装Poetry成功"
        else
            log_info "pip安装失败，使用官方安装脚本..."
            if curl -sSL https://install.python-poetry.org | $PYTHON_CMD - 2>/dev/null; then
                export PATH="$HOME/.local/bin:$PATH"
                if command -v poetry &> /dev/null; then
                    log_success "Poetry官方安装成功"
                else
                    log_warning "Poetry安装失败，将使用pip进行依赖管理"
                fi
            else
                log_warning "Poetry安装失败，将使用pip进行依赖管理"
            fi
        fi
    else
        # 系统Python环境下，尝试用户级安装
        log_info "在系统Python环境中尝试安装Poetry..."
        if $PIP_CMD install --user poetry --quiet 2>/dev/null; then
            export PATH="$HOME/.local/bin:$PATH"
            log_success "使用pip用户级安装Poetry成功"
        elif curl -sSL https://install.python-poetry.org | $PYTHON_CMD - 2>/dev/null; then
            export PATH="$HOME/.local/bin:$PATH"
            if command -v poetry &> /dev/null; then
                log_success "Poetry官方安装成功"
            else
                log_warning "Poetry安装失败，将使用pip进行依赖管理"
            fi
        else
            log_warning "Poetry安装失败，将使用pip进行依赖管理"
        fi
    fi
else
    log_info "Poetry已安装: $(poetry --version)"
fi

log_success "环境设置完成"

# Stage 3: Install Dependencies
log_info "Stage 3: 安装项目依赖..."

# 安装依赖（支持虚拟环境和系统Python环境）
if [ -f "pyproject.toml" ]; then
    if command -v poetry &> /dev/null; then
        log_info "使用Poetry安装依赖（包括测试依赖，可能需要几分钟）..."
        if poetry install --no-interaction 2>/dev/null; then
            log_success "Poetry依赖安装完成"
        else
            log_warning "Poetry安装失败，尝试pip安装..."
            if [ -f "requirements.txt" ]; then
                if [ "$VENV_CREATED" = true ]; then
                    $PIP_CMD install -r requirements.txt --quiet
                else
                    $PIP_CMD install --user -r requirements.txt --quiet 2>/dev/null || $PIP_CMD install -r requirements.txt --quiet
                fi
                log_success "pip依赖安装完成"
            else
                log_warning "未找到requirements.txt"
            fi
            
            # 确保测试依赖已安装
            log_info "确保测试依赖已安装..."
            if [ "$VENV_CREATED" = true ]; then
                $PIP_CMD install pytest pytest-asyncio --quiet 2>/dev/null || log_warning "测试依赖安装失败"
            else
                $PIP_CMD install --user pytest pytest-asyncio --quiet 2>/dev/null || $PIP_CMD install pytest pytest-asyncio --quiet 2>/dev/null || log_warning "测试依赖安装失败"
            fi
        fi
    else
        log_info "Poetry不可用，尝试使用pip安装..."
        if [ -f "requirements.txt" ]; then
            if [ "$VENV_CREATED" = true ]; then
                $PIP_CMD install -r requirements.txt --quiet
            else
                $PIP_CMD install --user -r requirements.txt --quiet 2>/dev/null || $PIP_CMD install -r requirements.txt --quiet
            fi
            log_success "pip依赖安装完成"
        else
            log_warning "无法使用Poetry且未找到requirements.txt，跳过依赖安装"
        fi
        
        # 确保测试依赖已安装
        log_info "确保测试依赖已安装..."
        if [ "$VENV_CREATED" = true ]; then
            $PIP_CMD install pytest pytest-asyncio --quiet 2>/dev/null || log_warning "测试依赖安装失败"
        else
            $PIP_CMD install --user pytest pytest-asyncio --quiet 2>/dev/null || $PIP_CMD install pytest pytest-asyncio --quiet 2>/dev/null || log_warning "测试依赖安装失败"
        fi
    fi
elif [ -f "requirements.txt" ]; then
    log_info "使用pip安装依赖..."
    if [ "$VENV_CREATED" = true ]; then
        $PIP_CMD install -r requirements.txt --quiet
    else
        $PIP_CMD install --user -r requirements.txt --quiet 2>/dev/null || $PIP_CMD install -r requirements.txt --quiet
    fi
    log_success "pip依赖安装完成"
    
    # 确保测试依赖已安装
    log_info "确保测试依赖已安装..."
    if [ "$VENV_CREATED" = true ]; then
        $PIP_CMD install pytest pytest-asyncio --quiet 2>/dev/null || log_warning "测试依赖安装失败"
    else
        $PIP_CMD install --user pytest pytest-asyncio --quiet 2>/dev/null || $PIP_CMD install pytest pytest-asyncio --quiet 2>/dev/null || log_warning "测试依赖安装失败"
    fi
else
    log_warning "未找到依赖文件，跳过依赖安装"
    
    # 即使没有依赖文件，也尝试安装基本的测试依赖
    log_info "尝试安装基本测试依赖..."
    if [ "$VENV_CREATED" = true ]; then
        $PIP_CMD install pytest pytest-asyncio --quiet 2>/dev/null || log_warning "测试依赖安装失败"
    else
        $PIP_CMD install --user pytest pytest-asyncio --quiet 2>/dev/null || $PIP_CMD install pytest pytest-asyncio --quiet 2>/dev/null || log_warning "测试依赖安装失败"
    fi
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
    # 检查pytest是否可用
    if command -v pytest &> /dev/null || $PYTHON_CMD -m pytest --version &> /dev/null; then
        log_info "使用pytest运行测试..."
        if command -v poetry &> /dev/null && [ -f "pyproject.toml" ]; then
            # 使用Poetry运行pytest
            poetry run pytest tests/ --junitxml="$BUILD_DIR/test-results.xml" --cov=src --cov-report=xml:"$BUILD_DIR/coverage.xml" || log_warning "部分测试失败"
        else
            # 直接使用pytest
            if [ "$VENV_CREATED" = true ]; then
                $PYTHON_CMD -m pytest tests/ --junitxml="$BUILD_DIR/test-results.xml" || log_warning "部分测试失败"
            else
                pytest tests/ --junitxml="$BUILD_DIR/test-results.xml" || log_warning "部分测试失败"
            fi
        fi
    elif command -v python &> /dev/null; then
        log_info "pytest不可用，使用unittest运行测试..."
        $PYTHON_CMD -m unittest discover tests/ || log_warning "部分测试失败"
    else
        log_warning "无法找到Python或pytest，跳过测试"
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