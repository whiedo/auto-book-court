pipeline {
    agent { docker { image 'python:3.11.1-bullseye' } }
    stages {
        stage('build') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        stage('test') {
            steps {
                sh 'python test.py'
            }
            post {
                always {
                    junit 'test-reports/*.xml'
                }
            }
    }
}