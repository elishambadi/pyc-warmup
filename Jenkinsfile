pipeline {
    agent any

    environment {
        COMPOSE_FILE = "docker-compose.yml"
    }

    stages {
        stage('Pull Latest Code') {
            steps {
                git branch: 'master', url: 'https://github.com/elishambadi/pyc-warmup.git'
            }
        }

        stage('Stop & Remove Old Containers') {
            steps {
                sh 'docker compose down'
            }
        }

        stage('Rebuild & Start Containers') {
            steps {
                sh 'docker compose up -d --build'
            }
        }

        stage('Notify Slack') {
            steps {
                slackSend channel: '#deployments', message: "Deployment successful for ${env.JOB_NAME} - ${env.BUILD_NUMBER}"
            }
        }
    }
}
