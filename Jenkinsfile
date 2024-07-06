pipeline {
    agent any
    environment {
        CUSTOM_WORKSPACE = '/var/jenkins_home/workspace/ICT2216'
    }

    options {
        customWorkspace("${env.CUSTOM_WORKSPACE}")
    }

    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }
        stage('Checkout') {
            steps {
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
            }
        }
        stage('Verify Checkout') {
            steps {
                script {
                    sh 'echo "Current workspace: $CUSTOM_WORKSPACE"'
                    sh 'ls -l $CUSTOM_WORKSPACE'
                    sh 'ls -l $CUSTOM_WORKSPACE/react-flask-app'
                }
            }
        }
        stage('Copy .env File') {
            steps {
                script {
                    withCredentials([file(credentialsId: '9e9add6b-9983-4371-81af-33e9987d85a0', variable: 'SECRET_ENV_FILE')]) {
                        sh 'cp $SECRET_ENV_FILE $CUSTOM_WORKSPACE/react-flask-app/server/.env'
                        sh 'ls -l $CUSTOM_WORKSPACE/react-flask-app/server/.env'  // Verify the .env file is copied
                    }
                }
            }
        }
        stage('Clean Up') {
            agent {
                docker {
                    image 'docker/compose:latest'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    sh 'docker system prune -af'
                    sh 'docker volume prune -f'
                }
            }
        }
        stage('Stop and Remove Existing Containers') {
            agent {
                docker {
                    image 'docker/compose:latest'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    sh 'docker-compose -f $CUSTOM_WORKSPACE/react-flask-app/docker-compose.yml down'
                }
            }
        }
        stage('Deploy Application') {
            agent {
                docker {
                    image 'docker/compose:latest'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    sh 'echo "Current workspace during deploy: $CUSTOM_WORKSPACE"'
                    sh 'ls -l $CUSTOM_WORKSPACE/react-flask-app/server/.env'  // Ensure .env file is present before build
                    sh 'docker-compose -f $CUSTOM_WORKSPACE/react-flask-app/docker-compose.yml up -d --build'
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
