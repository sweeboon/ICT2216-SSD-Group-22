pipeline {
    agent any

    environment {
        VENV_PATH = "react-flask-app/server/venv"
        DOCKER_IMAGE = 'custom-nginx'
        CONTAINER_NAME = 'nginx'
        MOUNTED_DIR = '/usr/src/app/react-flask-app'
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

        stage('Ensure Docker Container is Running') {
            steps {
                script {
                    sh '''
                        if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
                            if [ "$(docker ps -aq -f status=exited -f name=$CONTAINER_NAME)" ]; then
                                docker start $CONTAINER_NAME
                            else
                                docker run -d --name $CONTAINER_NAME --network jenkins-blueocean \
                                    -v /home/student24/fullchain.pem:/etc/ssl/certs/forteam221ct_fullchain.pem \
                                    -v /home/student24/privkey.pem:/etc/ssl/private/forteam221ct_privkey.pem \
                                    -v /home/student24/nginx/nginx.conf:/etc/nginx/nginx.conf \
                                    -v $WORKSPACE/react-flask-app:/usr/src/app/react-flask-app \
                                    -p 80:80 -p 443:443 \
                                    $DOCKER_IMAGE:$BUILD_ID
                            fi
                        fi
                    '''
                }
            }
        }

        stage('Update Code in Mounted Volume') {
            steps {
                script {
                    // Ensure the target directory exists
                    sh 'docker exec $CONTAINER_NAME mkdir -p $MOUNTED_DIR'
                    // Copy the entire react-flask-app directory to the container
                    sh 'docker cp $WORKSPACE/react-flask-app/. $CONTAINER_NAME:$MOUNTED_DIR'
                    // Copy the .env file to the server directory in the container
                    sh 'docker cp $WORKSPACE/react-flask-app/server/.env $CONTAINER_NAME:$MOUNTED_DIR/server/.env'
                }
            }
        }

        stage('Start Services') {
            steps {
                script {
                    sh '''
                        docker exec $CONTAINER_NAME /bin/bash -c '
                        service nginx start &&
                        cd /usr/src/app/react-flask-app/server &&
                        source venv/bin/activate &&
                        flask run --host=0.0.0.0 --port=5000 &
                        cd /usr/src/app/react-flask-app/src &&
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
