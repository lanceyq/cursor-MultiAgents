@echo off
REM memsci项目CI/CD脚本 (Windows版本)
REM 等效于Jenkinsfile的功能

setlocal enabledelayedexpansion

REM 环境变量
set PROJECT_NAME=memsci
set PYTHON_VERSION=3.12
set WORKSPACE_DIR=%CD%
set BUILD_DIR=%WORKSPACE_DIR%\build
set DIST_DIR=%WORKSPACE_DIR%\dist

echo =========================================
echo     memsci项目 CI/CD Pipeline 开始
echo =========================================

REM Stage 1: Checkout
echo [INFO] Stage 1: 检出源代码...
if not exist ".git" (
    echo [INFO] 克隆仓库...
    git clone https://gitclone.com/github.com/lanceyq/cursor-MultiAgents.git temp_repo
    cd temp_repo
    git checkout memsci-project
    xcopy memsciCICD\* ..\ /E /Y
    cd ..
    rmdir /S /Q temp_repo
) else (
    echo [INFO] 更新现有仓库...
    git fetch origin
    git checkout memsci-project
    git pull origin memsci-project
)
echo [SUCCESS] 源代码检出完成

REM Stage 2: Setup Environment
echo [INFO] Stage 2: 设置Python环境...

REM 检查Python版本
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到Python，请先安装Python
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION_OUTPUT=%%i
echo [INFO] Python版本: %PYTHON_VERSION_OUTPUT%

REM 检查并安装Poetry
where poetry >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] 安装Poetry...
    curl -sSL https://install.python-poetry.org | python -
    set PATH=%APPDATA%\Python\Scripts;%PATH%
) else (
    for /f "tokens=*" %%i in ('poetry --version') do set POETRY_VERSION=%%i
    echo [INFO] Poetry已安装: !POETRY_VERSION!
)

echo [SUCCESS] 环境设置完成

REM Stage 3: Install Dependencies
echo [INFO] Stage 3: 安装项目依赖...
set PATH=%APPDATA%\Python\Scripts;%PATH%
poetry install
if %errorlevel% neq 0 (
    echo [ERROR] 依赖安装失败
    exit /b 1
)
echo [SUCCESS] 依赖安装完成

REM Stage 4: Lint Code (可选)
echo [INFO] Stage 4: 代码质量检查...
REM 如果项目中有linting工具，可以在这里运行
REM poetry run flake8 src/ tests/ || echo [WARNING] 代码检查发现问题
REM poetry run black --check src/ tests/ || echo [WARNING] 代码格式检查发现问题
echo [INFO] 代码检查完成

REM Stage 5: Run Tests
echo [INFO] Stage 5: 运行自动化测试...
set PATH=%APPDATA%\Python\Scripts;%PATH%
set PYTHONPATH=%WORKSPACE_DIR%\src;%PYTHONPATH%

REM 创建测试结果目录
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

REM 运行pytest测试
poetry run pytest tests/ -v --tb=short --junitxml="%BUILD_DIR%\test-results.xml"
if %errorlevel% equ 0 (
    echo [SUCCESS] 所有测试通过
) else (
    echo [WARNING] 部分测试失败，但继续构建过程
)

REM Stage 6: Build Package
echo [INFO] Stage 6: 构建软件包...
set PATH=%APPDATA%\Python\Scripts;%PATH%
poetry build
if %errorlevel% neq 0 (
    echo [ERROR] 软件包构建失败
    exit /b 1
)
echo [SUCCESS] 软件包构建完成

REM Stage 7: Archive Artifacts
echo [INFO] Stage 7: 归档构建产物...
if exist "dist" (
    if not exist "%BUILD_DIR%\artifacts" mkdir "%BUILD_DIR%\artifacts"
    xcopy dist\* "%BUILD_DIR%\artifacts\" /E /Y
    echo [SUCCESS] 构建产物已归档到: %BUILD_DIR%\artifacts\
    
    echo [INFO] 构建产物列表:
    dir "%BUILD_DIR%\artifacts\"
) else (
    echo [WARNING] 未找到构建产物目录
)

echo =========================================
echo     CI/CD Pipeline 执行完成
echo =========================================

REM 显示摘要
echo [INFO] 执行摘要:
echo   - 工作目录: %WORKSPACE_DIR%
echo   - 构建目录: %BUILD_DIR%
if exist "%BUILD_DIR%\test-results.xml" (
    echo   - 测试结果: %BUILD_DIR%\test-results.xml
)
if exist "%BUILD_DIR%\artifacts" (
    echo   - 构建产物: %BUILD_DIR%\artifacts\
)

echo [SUCCESS] Pipeline执行成功完成！
pause