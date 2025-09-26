pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'memsci'
        PYTHON_VERSION = '3.12'
    }
    
    stages {
        stage('Execute CI/CD Script') {
            steps {
                echo 'Running CI/CD script directly...'
                script {
                    // 根据操作系统选择执行不同的脚本
                    if (isUnix()) {
                        // Linux/Unix系统 - 使用bash直接执行，避免权限问题
                        sh 'bash ci-cd.sh'
                    } else {
                        // Windows系统
                        bat '''
                            ci-cd.bat
                        '''
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed!'
            
            // 发布测试结果（如果存在）
            script {
                if (fileExists('build/test-results.xml')) {
                    junit 'build/test-results.xml'
                }
            }
            
            // 归档构建产物（如果存在）
            script {
                if (fileExists('build/artifacts')) {
                    archiveArtifacts artifacts: 'build/artifacts/*', fingerprint: true
                }
            }
        }
        success {
            echo 'Pipeline succeeded!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}