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
                echo '🔍 Verifying build environment...'
                sh '''
                    echo "=== Workspace Files ==="
                    ls -la
                    
                    echo ""
                    echo "=== Required Files Check ==="
                    [ -f "tests.py" ] && echo "✅ Test file found" || echo "❌ Test file NOT found"
                    [ -f "Dockerfile" ] && echo "✅ Dockerfile found" || echo "❌ Dockerfile NOT found"
                    [ -f "requirements.txt" ] && echo "✅ Requirements found" || echo "❌ Requirements NOT found"
                    
                    echo ""
                    echo "=== Docker Verification ==="
                    if command -v docker > /dev/null 2>&1; then
                        echo "✅ Docker CLI found"
                        docker --version
                        docker info | head -n 5 || echo "Docker daemon check failed"
                    else
                        echo "❌ Docker CLI not found"
                        exit 1
                    fi
                    
                    echo ""
                    echo "=== SonarQube Connection Test ==="
                    if curl -s http://sonarqube:9000/api/system/status > /dev/null 2>&1; then
                        echo "✅ SonarQube is reachable"
                    else
                        echo "⚠️ SonarQube not reachable (will skip analysis)"
                    fi
                '''
            }
        }
        
        stage('SonarQube Analysis') {
            steps {
                script {
                    echo '🔍 Running SonarQube code analysis...'
                    
                    // Check if SonarQube is reachable before attempting analysis
                    def sonarAvailable = sh(
                        script: 'curl -s -o /dev/null -w "%{http_code}" http://sonarqube:9000/api/system/status',
                        returnStdout: true
                    ).trim()
                    
                    if (sonarAvailable == '200') {
                        try {
                            def scannerHome = tool name: 'SonarScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                            
                            withSonarQubeEnv('sonarqube') {
                                sh """
                                ${scannerHome}/bin/sonar-scanner \
                                -Dsonar.projectKey=demoqa-tests \
                                -Dsonar.projectName="DemoQA Selenium Tests" \
                                -Dsonar.projectVersion=1.0 \
                                -Dsonar.sources=. \
                                -Dsonar.python.version=3 \
                                -Dsonar.sourceEncoding=UTF-8 \
                                -Dsonar.exclusions=**/*.png,**/*.jpg,**/screenshots/**,**/docker-compose.yml
                                """
                            }
                            echo '✅ SonarQube analysis completed successfully'
                        } catch (Exception e) {
                            echo "⚠️ SonarQube analysis failed (likely authentication issue)"
                            echo "Error: ${e.message}"
                            echo "💡 To fix: Add SonarQube token to Jenkins credentials"
                            echo "Pipeline will continue without SonarQube analysis"
                            currentBuild.result = 'UNSTABLE'
                        }
                    } else {
                        echo "⚠️ SonarQube server not reachable (HTTP $sonarAvailable)"
                        echo "Skipping SonarQube analysis"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            when {
                expression { 
                    currentBuild.result == null || currentBuild.result == 'SUCCESS' 
                }
            }
            steps {
                script {
                    echo '🚦 Waiting for Quality Gate result...'
                    try {
                        timeout(time: 3, unit: 'MINUTES') {
                            def qg = waitForQualityGate()
                            if (qg.status != 'OK') {
                                echo "⚠️ Quality Gate status: ${qg.status}"
                                currentBuild.result = 'UNSTABLE'
                            } else {
                                echo '✅ Quality Gate PASSED'
                            }
                        }
                    } catch (Exception e) {
                        echo "⚠️ Quality Gate check timed out or failed"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image for Selenium tests...'
                sh """
                    docker build -t ${DOCKER_IMAGE} .
                    echo "✅ Docker image built successfully"
                    docker images | grep demoqa-tests
                """
            }
        }
        
        stage('Run Selenium Tests') {
            steps {
                script {
                    echo '🧪 Running Selenium tests in Docker container...'
                    try {
                        sh """
                            # Remove old container if exists
                            docker rm -f demoqa-tests 2>/dev/null || true
                            
                            # Run tests
                            echo "Starting test execution..."
                            docker run --name demoqa-tests ${DOCKER_IMAGE}
                            
                            echo "✅ Test execution completed"
                        """
                    } catch (Exception e) {
                        echo "⚠️ Tests completed with failures"
                        echo "Error: ${e.message}"
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
        }
        
        stage('Extract Test Results') {
            steps {
                echo '📤 Extracting test results and screenshots...'
                sh '''
                    # Create directory for artifacts
                    mkdir -p test_screenshots
                    
                    # Copy screenshots from container
                    echo "Copying screenshots..."
                    docker cp demoqa-tests:/app/test_screenshots/. ./test_screenshots/ 2>/dev/null || \
                    echo "⚠️ No screenshots found or container not available"
                    
                    # Display results
                    echo ""
                    echo "=== Test Artifacts ==="
                    if [ -d "test_screenshots" ] && [ "$(ls -A test_screenshots 2>/dev/null)" ]; then
                        echo "✅ Screenshots extracted successfully:"
                        ls -lh test_screenshots/
                        echo ""
                        echo "Total screenshots: $(ls test_screenshots/*.png 2>/dev/null | wc -l)"
                    else
                        echo "ℹ️ No test failures - no screenshots generated"
                    fi
                '''
            }
        }
        
        stage('Cleanup') {
            steps {
                echo '🧹 Cleaning up Docker resources...'
                sh '''
                    docker rm -f demoqa-tests 2>/dev/null || true
                    echo "✅ Cleanup completed"
                '''
            }
        }
    }
    
    post {
        always {
            script {
                echo '📊 Archiving build artifacts...'
                
                // Archive screenshots
                try {
                    archiveArtifacts artifacts: 'test_screenshots/**/*.png', allowEmptyArchive: true, fingerprint: true
                    echo '✅ Artifacts archived successfully'
                } catch (Exception e) {
                    echo 'ℹ️ No artifacts to archive'
                }
                
                // Docker system cleanup
                try {
                    sh 'docker system prune -f 2>/dev/null || true'
                } catch (Exception e) {
                    echo 'ℹ️ Docker cleanup skipped'
                }
            }
        }
        success {
            echo '''
            ╔═══════════════════════════════════════╗
            ║  ✅ PIPELINE COMPLETED SUCCESSFULLY  ║
            ╚═══════════════════════════════════════╝
            '''
        }
        unstable {
            echo '''
            ╔═══════════════════════════════════════╗
            ║  ⚠️  PIPELINE UNSTABLE                ║
            ║  Some stages had warnings             ║
            ╚═══════════════════════════════════════╝
            '''
        }
        failure {
            echo '''
            ╔═══════════════════════════════════════╗
            ║  ❌ PIPELINE FAILED                   ║
            ║  Check logs for error details         ║
            ╚═══════════════════════════════════════╝
            '''
        }
    }
}
