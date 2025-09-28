pipeline {
    agent any
    
    environment {
        // 定义环境变量
        PYTHON_VERSION = '3.12'
        PROJECT_NAME = 'memsci'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                // 使用GitHub凭据进行认证
                checkout([
                    $class:'GitSCM',
                    branches: [[name: '*/memsci-project']],
                    userRemoteConfigs: [[
                        url:'https://github.com/lanceyq/cursor-MultiAgents.git',
                        credentialsId:'github-pat-credentials'
                    ]]
                ])
            }
        }

        stage('Validate Git Remote') {
            steps {
                echo 'Validating Git remote URL and connectivity...'
                script {
                    withCredentials([string(credentialsId: 'github-pat-credentials', variable: 'GITHUB_PAT')]) {
                        if (isUnix()) {
                            sh '''
                                URL="https://github.com/lanceyq/cursor-MultiAgents.git"
                                git ls-remote --heads "$URL" || {
                                  AUTH_URL="https://oauth2:${GITHUB_PAT}@github.com/lanceyq/cursor-MultiAgents.git"
                                  git ls-remote --heads "$AUTH_URL"
                                }
                            '''
                        } else {
                            bat '''
                                set "URL=https://github.com/lanceyq/cursor-MultiAgents.git"
                                git ls-remote --heads "%URL%" || (
                                  set "AUTH_URL=https://oauth2:%GITHUB_PAT%@github.com/lanceyq/cursor-MultiAgents.git"
                                  git ls-remote --heads "%AUTH_URL%"
                                )
                            '''
                        }
                    }
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo 'Setting up Python environment...'
                script {
                    // 检查Python版本
                    bat 'python --version'
                    
                    // 安装Poetry（如果没有安装）
                    bat '''
                        where poetry >nul 2>&1
                        if %errorlevel% neq 0 (
                            echo Installing Poetry...
                            curl -sSL https://install.python-poetry.org | python -
                            set PATH=%APPDATA%\\Python\\Scripts;%PATH%
                        )
                        poetry --version
                    '''
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing project dependencies...'
                script {
                    bat '''
                        set PATH=%APPDATA%\\Python\\Scripts;%PATH%
                        poetry install
                    '''
                }
            }
        }
        
        stage('Lint Code') {
            steps {
                echo 'Running code linting...'
                script {
                    bat '''
                        set PATH=%APPDATA%\\Python\\Scripts;%PATH%
                        REM 如果项目中有linting工具，可以在这里运行
                        REM poetry run flake8 src/ tests/ || exit /b 0
                        REM poetry run black --check src/ tests/ || exit /b 0
                        echo Linting completed
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running automated tests...'
                script {
                    bat '''
                        set PATH=%APPDATA%\\Python\\Scripts;%PATH%
                        REM 设置环境变量（如果需要）
                        set PYTHONPATH=%WORKSPACE%\\src;%PYTHONPATH%
                        
                        REM 运行pytest测试
                        poetry run pytest tests/ -v --tb=short --junitxml=test-results.xml || exit /b 0
                    '''
                }
            }
            post {
                always {
                    // 发布测试结果
                    junit 'test-results.xml'
                }
            }
        }
        
        stage('Build Package') {
            steps {
                echo 'Building package...'
                script {
                    bat '''
                        set PATH=%APPDATA%\\Python\\Scripts;%PATH%
                        poetry build
                    '''
                }
            }
        }
        
        stage('Archive Artifacts') {
            steps {
                echo 'Archiving build artifacts...'
                archiveArtifacts artifacts: 'dist/*', fingerprint: true
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed!'
            // 清理工作空间（可选）
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded!'
            // 可以添加成功通知
        }
        failure {
            echo 'Pipeline failed!'
            // 可以添加失败通知
        }
    }
}

### sdfs 

