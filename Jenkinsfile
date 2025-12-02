pipeline {
    agent any
    
    environment {
        SONARQUBE = 'sonarqube'
        DOCKER_IMAGE = "demoqa-tests:latest"
    }
    
    tools {
        // Fixed: Use the full class name for SonarQube Scanner
        hudson.plugins.sonar.SonarRunnerInstallation 'SonarScanner'
    }
    
    stages {
        stage('Clone Repository') {
            steps {
                // Update with your actual GitHub username and repository
                git branch: 'main', url: 'https://github.com/Moetaz101/Test-Logiciel-Pipeline.git'
            }
        }
        
        stage('SonarQube Code Analysis') {
            steps {
                script {
                    // Get the SonarScanner tool path
                    def scannerHome = tool 'SonarScanner'
                    
                    withSonarQubeEnv('sonarqube') {
                        sh """
                        ${scannerHome}/bin/sonar-scanner \
                        -Dsonar.projectKey=demoqa-tests \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.python.version=3
                        """
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh """
                docker build -t ${DOCKER_IMAGE} .
                """
            }
        }
        
        stage('Run Docker Container') {
            steps {
                sh """
                docker rm -f demoqa-tests || true
                docker run --name demoqa-tests ${DOCKER_IMAGE}
                """
            }
        }
        
        stage('Extract Test Results') {
            steps {
                sh """
                docker cp demoqa-tests:/app/test_screenshots ./test_screenshots || true
                """
            }
        }
        
        stage('Cleanup') {
            steps {
                sh """
                docker rm -f demoqa-tests || true
                """
            }
        }
    }
    
    post {
        always {
            // Archive test screenshots if they exist
            archiveArtifacts artifacts: 'test_screenshots/*.png', allowEmptyArchive: true
            
            // Clean up Docker images to save space
            sh 'docker system prune -f || true'
        }
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs above.'
        }
    }
}
