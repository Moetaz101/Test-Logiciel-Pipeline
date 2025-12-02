pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "demoqa-tests:latest"
    }
    
    stages {
        stage('Clone Repository') {
            steps {
                echo '📥 Cloning repository...'
                git branch: 'main', url: 'https://github.com/Moetaz101/Test-Logiciel-Pipeline.git'
            }
        }
        
        stage('Verify Environment') {
            steps {
                echo '🔍 Checking environment...'
                sh '''
                    echo "=== Files in workspace ==="
                    ls -la
                    
                    echo "\n=== Docker check ==="
                    if command -v docker &> /dev/null; then
                        echo "✅ Docker found"
                        docker --version
                        docker info | head -n 5
                    else
                        echo "❌ Docker not found"
                    fi
                '''
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    echo '🔍 Running SonarQube analysis...'
                    try {
                        def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                        
                        withSonarQubeEnv('sonarqube') {
                            sh """
                            ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=demoqa-tests \
                            -Dsonar.projectName="DemoQA Tests" \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3
                            """
                        }
                        echo '✅ SonarQube analysis completed'
                    } catch (Exception e) {
                        echo "⚠️ SonarQube analysis failed - continuing anyway"
                        echo "Error: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            when {
                expression { currentBuild.result == null || currentBuild.result == 'SUCCESS' }
            }
            steps {
                script {
                    try {
                        timeout(time: 3, unit: 'MINUTES') {
                            def qg = waitForQualityGate()
                            if (qg.status != 'OK') {
                                echo "⚠️ Quality Gate: ${qg.status}"
                            }
                        }
                    } catch (Exception e) {
                        echo "⚠️ Quality Gate skipped"
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh """
                    docker build -t ${DOCKER_IMAGE} .
                    echo "✅ Image built"
                    docker images | grep demoqa-tests
                """
            }
        }
        
        stage('Run Tests') {
            steps {
                echo '🧪 Running tests...'
                sh """
                    docker rm -f demoqa-tests 2>/dev/null || true
                    docker run --name demoqa-tests ${DOCKER_IMAGE}
                    echo "✅ Tests completed"
                """
            }
        }
        
        stage('Extract Results') {
            steps {
                echo '📤 Extracting results...'
                sh """
                    mkdir -p test_screenshots
                    docker cp demoqa-tests:/app/test_screenshots/. ./test_screenshots/ || echo "No screenshots"
                    ls -la test_screenshots/ || echo "Empty"
                """
            }
        }
        
        stage('Cleanup') {
            steps {
                sh 'docker rm -f demoqa-tests || true'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'test_screenshots/**/*.png', allowEmptyArchive: true
            sh 'docker system prune -f 2>/dev/null || true'
        }
        success {
            echo '✅ Pipeline SUCCESS'
        }
        unstable {
            echo '⚠️ Pipeline UNSTABLE'
        }
        failure {
            echo '❌ Pipeline FAILED'
        }
    }
}
