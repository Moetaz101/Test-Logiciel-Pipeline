pipeline {
    agent any

    environment {
        SONARQUBE = 'sonarqube'
        DOCKER_IMAGE = "demoqa-tests:latest"
    }

    tools {
        sonarScanner 'SonarScanner'
    }

    stages {

        stage('Clone Repository') {
            steps {
                git branch: 'main', url: 'https://github.com/YOUR_USERNAME/YOUR_REPO.git'
            }
        }

        stage('SonarQube Code Analysis') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    sh '''
                    sonar-scanner \
                    -Dsonar.projectKey=demoqa-tests \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://localhost:9000
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t demoqa-tests .
                '''
            }
        }

        stage('Run Docker Container') {
            steps {
                sh '''
                docker rm -f demoqa-tests || true
                docker run --name demoqa-tests demoqa-tests
                '''
            }
        }
    }
}
