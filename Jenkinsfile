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
                    sh '''
                        DOCKER_IMAGE=${DOCKER_IMAGE}
                        BUILD_ID=${env.BUILD_ID}
                        WORKSPACE=${WORKSPACE}
                        docker build -t $DOCKER_IMAGE:$BUILD_ID -f $WORKSPACE/react-flask-app/Dockerfile $WORKSPACE/react-flask-app
                    '''
                }
            }
        }

        stage('Ensure Docker Container is Running') {
            steps {
                script {
                    sh '''
                        CONTAINER_NAME=${CONTAINER_NAME}
                        WORKSPACE=${WORKSPACE}
                        MOUNTED_DIR=${MOUNTED_DIR}
                        if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
                            if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
                                docker start $CONTAINER_NAME
                            else
                                docker run -d --name $CONTAINER_NAME --network jenkins-blueocean \
                                    -v /home/student24/fullchain.pem:/etc/ssl/certs/forteam221ct_fullchain.pem \
                                    -v /home/student24/privkey.pem:/etc/ssl/private/forteam221ct_privkey.pem \
                                    -v /home/student24/fullchain.pem:/etc/ssl/certs/fullchain.pem \
                                    -v /home/student24/privkey.pem:/etc/ssl/private/privkey.pem \
                                    -v /home/student24/nginx/nginx.conf:/etc/nginx/nginx.conf \
                                    -v $WORKSPACE/react-flask-app:/usr/src/app \
                                    -p 80:80 -p 443:443 \
                                    ${DOCKER_IMAGE}:${env.BUILD_ID}
                            fi
                        fi
                    '''
                }
            }
        }

        stage('Update Code in Mounted Volume') {
            steps {
                script {
                    sh '''
                        CONTAINER_NAME=${CONTAINER_NAME}
                        MOUNTED_DIR=${MOUNTED_DIR}
                        WORKSPACE=${WORKSPACE}
                        docker exec $CONTAINER_NAME mkdir -p $MOUNTED_DIR
                        docker cp $WORKSPACE/react-flask-app/. $CONTAINER_NAME:$MOUNTED_DIR/
                        docker cp $WORKSPACE/react-flask-app/server/.env $CONTAINER_NAME:$MOUNTED_DIR/react-flask-app/server/.env
                    '''
                }
            }
        }

        stage('Start Services') {
            steps {
                script {
                    sh '''
                        CONTAINER_NAME=${CONTAINER_NAME}
                        docker exec $CONTAINER_NAME /bin/bash -c '
                        service nginx start &&
                        cd /usr/src/app/react-flask-app/server &&
                        source venv/bin/activate 
                        yarn start
                        '
                    '''
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
