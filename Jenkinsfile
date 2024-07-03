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
                    // Print the current workspace directory
                    sh 'echo "Current workspace: ${WORKSPACE}"'
                    // List the contents of the workspace directory
                    sh 'ls -l ${WORKSPACE}'
                    // List the contents of the react-flask-app directory
                    sh 'ls -l ${WORKSPACE}/react-flask-app'
                }
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    // Create the virtual environment if it doesn't exist
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
                    // Install any dependencies listed in requirements.txt
                    sh 'bash -c "source ${WORKSPACE}/${VENV_PATH}/bin/activate && pip install -r ${WORKSPACE}/react-flask-app/server/requirements.txt"'
                }
            }
        }

        stage('Install Node.js Dependencies') {
            steps {
                script {
                    // Install Node.js dependencies
                    sh 'bash -c "cd ${WORKSPACE}/react-flask-app/src && yarn install"'
                }
            }
        }

        stage('Ensure Docker Container is Running') {
            steps {
                script {
                    // Ensure Docker container is running
                    sh """
                        if [ ! "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
                            if [ "$(docker ps -aq -f status=exited -f name=${CONTAINER_NAME})" ]; then
                                docker start ${CONTAINER_NAME}
                            else
                                docker run -d --name ${CONTAINER_NAME} --network my_network \
                                    -v /home/student24/fullchain.pem:/etc/ssl/certs/forteam221ct_fullchain.pem \
                                    -v /home/student24/privkey.pem:/etc/ssl/private/forteam221ct_privkey.pem \
                                    -v /home/student24/fullchain.pem:/etc/ssl/certs/fullchain.pem \
                                    -v /home/student24/privkey.pem:/etc/ssl/private/privkey.pem \
                                    -v /home/student24/nginx/nginx.conf:/etc/nginx/nginx.conf \
                                    -v ${WORKSPACE}/react-flask-app:/usr/src/app \
                                    -p 80:80 -p 443:443 \
                                    ${DOCKER_IMAGE}
                            fi
                        fi
                    """
                }
            }
        }

        stage('Update Code in Mounted Volume') {
            steps {
                script {
                    // Copy the updated code to the mounted volume in the running Docker container
                    sh 'rsync -av --delete ${WORKSPACE}/react-flask-app/ ${MOUNTED_DIR}/'
                }
            }
        }
    }

    post {
        always {
            // Optionally clean the workspace after the build
            cleanWs()
        }
    }
}
