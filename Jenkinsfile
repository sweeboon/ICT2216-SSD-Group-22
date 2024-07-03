pipeline {
    agent any

    environment {
        VENV_PATH = "react-flask-app/server/venv"
        DOCKER_IMAGE = 'myapp'
        CONTAINER_NAME = 'myapp-container'
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
                    sh 'echo "Current workspace: ${WORKSPACE}"'
                    sh 'ls -l ${WORKSPACE}'
                    sh 'ls -l ${WORKSPACE}/react-flask-app'
                }
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    sh '''
                        if [ ! -d "${WORKSPACE}/${VENV_PATH}" ]; then
                            python3 -m venv ${WORKSPACE}/${VENV_PATH}
                        fi
                    '''
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                script {
                    sh 'bash -c "source ${WORKSPACE}/${VENV_PATH}/bin/activate && pip install -r ${WORKSPACE}/react-flask-app/server/requirements.txt"'
                }
            }
        }

        stage('Install Node.js Dependencies') {
            steps {
                script {
                    sh 'bash -c "cd ${WORKSPACE}/react-flask-app/src && yarn install"'
                }
            }
        }

        stage('Copy .env File') {
            steps {
                script {
                    withCredentials([file(credentialsId: '9e9add6b-9983-4371-81af-33e9987d85a0', variable: 'SECRET_ENV_FILE')]) {
                        sh 'cp $SECRET_ENV_FILE ${WORKSPACE}/react-flask-app/server/.env'
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t ${DOCKER_IMAGE}:${env.BUILD_ID} ${WORKSPACE}/react-flask-app'
                }
            }
        }

        stage('Deploy Docker Image') {
            steps {
                script {
                    sh """
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true
                        docker run -d --name ${CONTAINER_NAME} --network my_network \
                        -v /home/student24/fullchain.pem:/etc/ssl/certs/forteam221ct_fullchain.pem \
                        -v /home/student24/privkey.pem:/etc/ssl/private/forteam221ct_privkey.pem \
                        -v /home/student24/fullchain.pem:/etc/ssl/certs/fullchain.pem \
                        -v /home/student24/privkey.pem:/etc/ssl/private/privkey.pem \
                        -v /home/student24/nginx/nginx.conf:/etc/nginx/nginx.conf \
                        -p 80:80 -p 443:443 \
                        ${DOCKER_IMAGE}:${env.BUILD_ID}
                    """
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
