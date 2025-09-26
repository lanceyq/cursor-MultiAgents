# 安装依赖（支持虚拟环境和系统Python环境）
# 测试github上传效果
if [ -f "pyproject.toml" ]; then
if command -v poetry &> /dev/null; then
        log_info "使用Poetry安装依赖（可能需要几分钟）..."
        if poetry install --no-dev --no-interaction 2>/dev/null; then
        log_info "使用Poetry安装依赖（包括测试依赖，可能需要几分钟）..."
        if poetry install --no-interaction 2>/dev/null; then
log_success "Poetry依赖安装完成"
else
log_warning "Poetry安装失败，尝试pip安装..."
@@ -257,6 +257,14 @@
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
@@ -270,6 +278,14 @@
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
@@ -279,8 +295,24 @@
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
@@ -307,67 +339,80 @@

# 运行测试
if [ -d "tests" ]; then
    if command -v pytest &> /dev/null; then
    # 检查pytest是否可用
    if command -v pytest &> /dev/null || $PYTHON_CMD -m pytest --version &> /dev/null; then
log_info "使用pytest运行测试..."
        poetry run pytest tests/ --junitxml="$BUILD_DIR/test-results.xml" --cov=src --cov-report=xml:"$BUILD_DIR/coverage.xml" || log_warning "部分测试失败"
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
        log_info "使用unittest运行测试..."
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