pipeline {
    agent any
    environment {
        VENV_PATH = "react-flask-app/server/venv"
        DOCKER_IMAGE = 'custom-nginx'
        CONTAINER_NAME = 'react-flask-app'
    }
    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
            }
        }
        stage('Verify Checkout') {
            steps {
                script {
                    sh 'echo "Current workspace: $WORKSPACE"'
                    sh 'ls -l $WORKSPACE'
                    sh 'ls -l $WORKSPACE/react-flask-app'
                }
            }
        }
        stage('Setup Virtual Environment') {
            steps {
                script {
                    sh '''
                        if [ ! -d "$WORKSPACE/$VENV_PATH" ]; then
                            python3 -m venv $WORKSPACE/$VENV_PATH
                        fi
                    '''
                }
            }
        }
        stage('Install Python Dependencies') {
            steps {
                script {
                    sh 'bash -c "source $WORKSPACE/$VENV_PATH/bin/activate && pip install -r $WORKSPACE/react-flask-app/server/requirements.txt"'
                }
            }
        }
        stage('Install Node.js Dependencies') {
            steps {
                script {
                    sh 'bash -c "cd $WORKSPACE/react-flask-app/src && yarn install"'
                }
            }
        }
        stage('Copy .env File') {
            steps {
                script {
                    withCredentials([file(credentialsId: '9e9add6b-9983-4371-81af-33e9987d85a0', variable: 'SECRET_ENV_FILE')]) {
                        sh 'cp $SECRET_ENV_FILE $WORKSPACE/react-flask-app/server/.env'
                    }
                }
            }
        }
        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $DOCKER_IMAGE:$BUILD_ID -f $WORKSPACE/react-flask-app/Dockerfile $WORKSPACE/react-flask-app'
                }
            }
        }
        stage('Deploy Application') {
            agent {
                docker {
                    image 'docker:git'
                    args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
                }
            }
            steps {
                script {
                    sh 'curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose'
                    sh 'chmod +x /usr/local/bin/docker-compose'
                    sh 'ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose'
                    sh 'docker-compose -f $WORKSPACE/react-flask-app/docker-compose.yml up -d'
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
