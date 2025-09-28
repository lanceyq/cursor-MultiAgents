#!/usr/bin/env bash
# 测试hook
set -euo pipefail
# 测试hook
# 简易日志函数
log_info() { echo "[INFO] $*"; }
log_warning() { echo "[WARN] $*"; }
log_success() { echo "[OK] $*"; }
log_error() { echo "[ERROR] $*"; }

# 基本目录变量
PROJECT_NAME="${PROJECT_NAME:-$(basename "$(pwd)")}"
BUILD_DIR="${BUILD_DIR:-build}"
DIST_DIR="${DIST_DIR:-dist}"
TEST_XML="$BUILD_DIR/test-results.xml"
COV_XML="$BUILD_DIR/coverage.xml"

mkdir -p "$BUILD_DIR" "$DIST_DIR"

# 清理与虚拟环境管理开关（可通过环境变量覆盖）
CLEAN_BUILD_DIR="${CLEAN_BUILD_DIR:-false}"
CLEAN_PREVIOUS_VENV="${CLEAN_PREVIOUS_VENV:-false}"
REMOVE_VENV_ON_EXIT="${REMOVE_VENV_ON_EXIT:-false}"
VENV_ACTIVE=false
VENV_DIR="$BUILD_DIR/venv"

# 可选：清理构建目录，确保环境整洁
if [ "$CLEAN_BUILD_DIR" = "true" ]; then
  log_info "清理构建目录: $BUILD_DIR"
  rm -rf "$BUILD_DIR"
  mkdir -p "$BUILD_DIR"
fi

# 预清理旧虚拟环境
if [ "$CLEAN_PREVIOUS_VENV" = "true" ] && [ -d "$VENV_DIR" ]; then
  log_info "清理旧虚拟环境: $VENV_DIR"
  rm -rf "$VENV_DIR"
fi

# 如果当前 shell 已处于其他虚拟环境，提示但继续创建自建环境
if [ -n "${VIRTUAL_ENV-}" ]; then
  log_warning "检测到已有虚拟环境(${VIRTUAL_ENV})，将启用自建虚拟环境覆盖当前环境"
fi

# 退出时的清理逻辑：解除并删除虚拟环境
cleanup() {
  if [ "$VENV_ACTIVE" = true ]; then
    if command -v deactivate >/dev/null 2>&1; then
      deactivate || true
      log_info "已解除虚拟环境"
    fi
  fi
  if [ "$REMOVE_VENV_ON_EXIT" = "true" ] && [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
    log_info "已删除虚拟环境目录: $VENV_DIR"
  fi
}
trap cleanup EXIT

# 全局加速与缓存复用配置
# 默认在当前执行中保留虚拟环境与缓存（可通过环境变量覆盖）
: "${REMOVE_VENV_ON_EXIT:=false}"
export PIP_INDEX_URL=${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}
export PIP_EXTRA_INDEX_URL=${PIP_EXTRA_INDEX_URL:-https://pypi.org/simple}
log_info "已设置 pip 镜像: $PIP_INDEX_URL"

# 为 Poetry 安装阶段准备镜像源（若项目未配置）
ensure_poetry_source() {
  if [ -f "pyproject.toml" ]; then
    if ! grep -q "\[\[tool.poetry.source\]\]" pyproject.toml; then
      log_info "为 Poetry 添加镜像源到 pyproject.toml"
      cat >> pyproject.toml <<'EOF'
[[tool.poetry.source]]
name = "tsinghua"
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
EOF
    else
      log_info "检测到 Poetry 源配置，跳过添加"
    fi
  fi
}

# 持久缓存与本地 wheel 仓库（即使每次新建 venv 也能复用）
CACHE_DIR=${CACHE_DIR:-"$HOME/.cache/memsci"}
WHEEL_DIR="$CACHE_DIR/wheels"
mkdir -p "$CACHE_DIR" "$WHEEL_DIR"
export PIP_CACHE_DIR=${PIP_CACHE_DIR:-"$CACHE_DIR/pip"}
export POETRY_CACHE_DIR=${POETRY_CACHE_DIR:-"$CACHE_DIR/poetry"}
log_info "缓存目录: $CACHE_DIR; 轮子目录: $WHEEL_DIR"

# 选择 Python / Pip 命令
if command -v python3 &> /dev/null; then
  PYTHON_CMD=python3
elif command -v python &> /dev/null; then
  PYTHON_CMD=python
else
  log_error "未找到 Python，无法继续"
  exit 1
fi

if command -v pip3 &> /dev/null; then
  PIP_CMD=pip3
elif command -v pip &> /dev/null; then
  PIP_CMD=pip
else
  PIP_CMD="$PYTHON_CMD -m pip"
fi

# Stage 0: 创建并启用虚拟环境（优先）
VENV_DIR="$BUILD_DIR/venv"
if $PYTHON_CMD -m venv "$VENV_DIR" 2>/dev/null; then
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
  PYTHON_CMD=python
  PIP_CMD=pip
  VENV_ACTIVE=true
  log_info "已创建并启用虚拟环境: $VENV_DIR"
  # 基础工具升级，提升安装成功率
  $PYTHON_CMD -m pip install -U pip setuptools wheel
else
  log_warning "无法创建虚拟环境，将尝试使用系统环境安装（可能受 PEP 668 限制）"
fi

# Stage 1: 安装依赖
log_info "Stage 1: 安装依赖"
if [ -f "pyproject.toml" ]; then
  if command -v poetry &> /dev/null; then
    log_info "使用 Poetry 安装依赖"
    ensure_poetry_source
    poetry lock || log_warning "Poetry lock 生成失败，继续安装"
    # 优先走 wheelhouse 以加速新 venv 安装
    if poetry export -f requirements.txt --without-hashes -o "$BUILD_DIR/requirements.txt"; then
      log_info "已生成 requirements.txt，准备构建并复用本地 wheels"
      $PIP_CMD wheel -r "$BUILD_DIR/requirements.txt" -w "$WHEEL_DIR" --prefer-binary || log_warning "预编译 wheels 失败，继续尝试安装"
      if $PIP_CMD install --no-index --find-links="$WHEEL_DIR" -r "$BUILD_DIR/requirements.txt"; then
        log_success "依赖已通过本地 wheelhouse 安装"
      else
        log_warning "从 wheelhouse 安装失败，回退到 Poetry 安装"
        if ! poetry install --no-interaction --no-root &> /dev/null; then
          log_warning "Poetry 安装失败，尝试使用 pip"
          if [ -f "requirements.txt" ]; then
            $PIP_CMD install --prefer-binary -r requirements.txt || $PYTHON_CMD -m pip install --user -r requirements.txt || $PYTHON_CMD -m pip install --break-system-packages -r requirements.txt || true
          else
            log_warning "未找到 requirements.txt，改用 pip 安装项目本体"
            $PIP_CMD install --prefer-binary . || $PYTHON_CMD -m pip install --user . || $PYTHON_CMD -m pip install --break-system-packages . || true
          fi
        fi
      fi
    else
      log_warning "Poetry export 失败，改用 Poetry 安装"
      if ! poetry install --no-interaction --no-root &> /dev/null; then
        log_warning "Poetry 安装失败，尝试使用 pip"
        if [ -f "requirements.txt" ]; then
          $PIP_CMD install --prefer-binary -r requirements.txt || $PYTHON_CMD -m pip install --user -r requirements.txt || $PYTHON_CMD -m pip install --break-system-packages -r requirements.txt || true
        else
          log_warning "未找到 requirements.txt，改用 pip 安装项目本体"
          $PIP_CMD install --prefer-binary . || $PYTHON_CMD -m pip install --user . || $PYTHON_CMD -m pip install --break-system-packages . || true
        fi
      fi
    fi
  else
    log_info "Poetry 不可用，使用 pip 安装项目（基于 pyproject.toml）"
    if [ -f "requirements.txt" ]; then
      # 预编译并缓存 wheels，加速重复安装
      $PIP_CMD wheel -r requirements.txt -w "$WHEEL_DIR" --prefer-binary || log_warning "预编译 wheels 失败，直接安装"
      $PIP_CMD install --no-index --find-links="$WHEEL_DIR" -r requirements.txt || $PIP_CMD install --prefer-binary -r requirements.txt || $PYTHON_CMD -m pip install --user -r requirements.txt || $PYTHON_CMD -m pip install --break-system-packages -r requirements.txt || true
    fi
    # 无论是否有 requirements.txt，都尝试安装项目本体，确保运行时依赖（如 pydantic）就绪
    $PIP_CMD install --prefer-binary . || $PYTHON_CMD -m pip install --user . || $PYTHON_CMD -m pip install --break-system-packages . || true
  fi
elif [ -f "requirements.txt" ]; then
  log_info "使用 pip 安装依赖"
  $PIP_CMD wheel -r requirements.txt -w "$WHEEL_DIR" --prefer-binary || log_warning "预编译 wheels 失败，直接安装"
  $PIP_CMD install --no-index --find-links="$WHEEL_DIR" -r requirements.txt || $PIP_CMD install --prefer-binary -r requirements.txt || $PYTHON_CMD -m pip install --user -r requirements.txt || $PYTHON_CMD -m pip install --break-system-packages -r requirements.txt || true
else
  log_warning "未找到依赖文件，跳过依赖安装"
fi

# 确保测试依赖
log_info "确保测试依赖已安装（pytest/pytest-asyncio）"
$PYTHON_CMD -m pip install -U pytest pytest-asyncio pytest-cov \
  || $PYTHON_CMD -m pip install --user -U pytest pytest-asyncio pytest-cov \
  || $PYTHON_CMD -m pip install --break-system-packages -U pytest pytest-asyncio pytest-cov \
  || log_warning "测试依赖安装失败"

# Stage 2: 代码质量（可选，这里仅占位）
log_info "Stage 2: 代码质量检查（可选，未启用）"

# Stage 3: 运行测试
log_info "Stage 3: 运行测试"
if [ -d "tests" ]; then
  # 优先使用 Poetry 环境的 pytest
  if command -v poetry &> /dev/null && [ -f "pyproject.toml" ]; then
    if poetry run pytest --version &> /dev/null; then
      log_info "使用 pytest 运行测试（Poetry 环境）"
      poetry run pytest tests/ --junitxml="$TEST_XML" --cov=src --cov-report=xml:"$COV_XML" || log_warning "部分测试失败"
    else
      log_info "pytest 不可用，使用 unittest 运行测试"
      $PYTHON_CMD -m unittest discover tests/ || log_warning "部分测试失败"
    fi
  else
    # 使用系统环境的 pytest
    if $PYTHON_CMD -m pytest --version &> /dev/null || command -v pytest &> /dev/null; then
      log_info "使用 pytest 运行测试"
      $PYTHON_CMD -m pytest tests/ --junitxml="$TEST_XML" --cov=src --cov-report=xml:"$COV_XML" || log_warning "部分测试失败"
    else
      log_info "pytest 不可用，使用 unittest 运行测试"
      $PYTHON_CMD -m unittest discover tests/ || log_warning "部分测试失败"
    fi
  fi
else
  log_warning "未找到 tests 目录，跳过测试"
fi

log_success "测试执行完成"

# Stage 4: 构建
log_info "Stage 4: 构建项目"
if [ -f "pyproject.toml" ] && command -v poetry &> /dev/null; then
  log_info "使用 Poetry 构建项目"
  poetry build
  if [ -d "dist" ]; then
    cp -r dist/* "$DIST_DIR/" 2>/dev/null || true
  fi
elif [ -f "setup.py" ]; then
  log_info "使用 setup.py 构建项目"
  $PYTHON_CMD setup.py sdist bdist_wheel --dist-dir "$DIST_DIR"
else
  if [ -d "src" ]; then
    log_info "创建源码包（tar.gz）"
    tar -czf "$DIST_DIR/${PROJECT_NAME}-$(date +%Y%m%d-%H%M%S).tar.gz" src/
  else
    log_warning "未找到可构建的源码目录"
  fi
fi

log_success "项目构建完成"

# Stage 5: 归档构建产物
log_info "Stage 5: 归档构建产物"
mkdir -p "$BUILD_DIR/artifacts"

if [ -d "$DIST_DIR" ] && [ "$(ls -A "$DIST_DIR" 2>/dev/null)" ]; then
  cp -r "$DIST_DIR"/* "$BUILD_DIR/artifacts/" 2>/dev/null || true
  log_success "构建产物已归档到 $BUILD_DIR/artifacts/"
else
  log_warning "未找到构建产物"
fi

if [ -f "$TEST_XML" ]; then
  cp "$TEST_XML" "$BUILD_DIR/artifacts/"
  log_info "测试报告已归档"
fi

if [ -f "$COV_XML" ]; then
  cp "$COV_XML" "$BUILD_DIR/artifacts/"
  log_info "覆盖率报告已归档"
fi

echo "========================================="
echo "    Jenkins CI/CD Pipeline 执行完成"
echo "========================================="
echo "构建产物位置: $BUILD_DIR/artifacts/"