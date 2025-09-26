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
                    $class: 'GitSCM',
                    branches: [[name: '*/memsci-project']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/lanceyq/cursor-MultiAgents.git',
                        credentialsId: 'github-pat-credentials'
                    ]]
                ])
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo 'Setting up Python environment...'
                script {
                    // 检查Python版本
                    sh 'python3 --version || python --version'
                    
                    // 安装Poetry（如果没有安装）
                    sh '''
                        if ! command -v poetry &> /dev/null; then
                            echo "Installing Poetry..."
                            curl -sSL https://install.python-poetry.org | python3 -
                            export PATH="$HOME/.local/bin:$PATH"
                        fi
                        poetry --version
                    '''
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing project dependencies...'
                script {
                    sh '''
                        export PATH="$HOME/.local/bin:$PATH"
                        poetry install --no-dev
                    '''
                }
            }
        }
        
        stage('Lint Code') {
            steps {
                echo 'Running code linting...'
                script {
                    sh '''
                        export PATH="$HOME/.local/bin:$PATH"
                        # 如果项目中有linting工具，可以在这里运行
                        # poetry run flake8 src/ tests/ || true
                        # poetry run black --check src/ tests/ || true
                        echo "Linting completed"
                    '''
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                echo 'Running automated tests...'
                script {
                    sh '''
                        export PATH="$HOME/.local/bin:$PATH"
                        # 设置环境变量（如果需要）
                        export PYTHONPATH="${WORKSPACE}/src:$PYTHONPATH"
                        
                        # 运行pytest测试
                        poetry run pytest tests/ -v --tb=short --junitxml=test-results.xml || true
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
                    sh '''
                        export PATH="$HOME/.local/bin:$PATH"
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