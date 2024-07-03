pipeline {
    agent any

    environment {
        VENV_PATH = "react-flask-app/server/venv"
        DOCKER_IMAGE = 'nginx'
        CONTAINER_NAME = 'nginx'
        MOUNTED_DIR = '/usr/src/app'
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

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t ${DOCKER_IMAGE}:${env.BUILD_ID} ${WORKSPACE}'
                }
            }
        }

        stage('Ensure Docker Container is Running') {
            steps {
                script {
                    sh """
                        if [ ! "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
                            if [ "$(docker ps -aq -f status=exited -f name=${CONTAINER_NAME})" ]; then
                                docker rm ${CONTAINER_NAME}
                            fi
                            docker run -d --name ${CONTAINER_NAME} --network jenkins-blueocean \
                                -v /home/student24/fullchain.pem:/etc/ssl/certs/forteam221ct_fullchain.pem \
                                -v /home/student24/privkey.pem:/etc/ssl/private/forteam221ct_privkey.pem \
                                -v /home/student24/fullchain.pem:/etc/ssl/certs/fullchain.pem \
                                -v /home/student24/privkey.pem:/etc/ssl/private/privkey.pem \
                                -v /home/student24/nginx/nginx.conf:/etc/nginx/nginx.conf \
                                -v ${WORKSPACE}/react-flask-app:/usr/src/app \
                                -p 80:80 -p 443:443 \
                                ${DOCKER_IMAGE}:${env.BUILD_ID}
                        fi
                    """
                }
            }
        }

        stage('Copy .env File and Start Services') {
            steps {
                script {
                    withCredentials([file(credentialsId: '9e9add6b-9983-4371-81af-33e9987d85a0', variable: 'SECRET_ENV_FILE')]) {
                        sh 'docker cp $SECRET_ENV_FILE ${CONTAINER_NAME}:${MOUNTED_DIR}/react-flask-app/server/.env'
                        sh 'docker exec ${CONTAINER_NAME} bash -c "source ${MOUNTED_DIR}/react-flask-app/server/venv/bin/activate && \
                            cd ${MOUNTED_DIR}/react-flask-app/server && flask db migrate && yarn start"'
                    }
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
