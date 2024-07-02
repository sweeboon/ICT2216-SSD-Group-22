pipeline {
    agent any

    environment {
        VENV_PATH = "react-flask-app/server/venv"
        DOCKER_IMAGE = 'nginx'
        CONTAINER_NAME = 'nginx'
        HOME_DIR = "/home/yourusername"
    }

    stages {
        stage('Clean Workspace') {
            steps {
                script {
                    // Clean the workspace directory
                    sh 'rm -rf ${WORKSPACE}/*'
                }
            }
        }

        stage('Checkout') {
            steps {
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
            }
        }

        stage('Copy .env File') {
            steps {
                script {
                    // Copy the .env file from the home directory to the workspace
                    sh 'cp ${HOME_DIR}/.env ${WORKSPACE}/react-flask-app/.env'
                }
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
                    // Create the virtual environment
                    sh 'bash -c "python3 -m venv ${WORKSPACE}/${VENV_PATH}"'
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

        stage('Build Docker Image') {
            steps {
                script {
                    // Verify Docker is accessible
                    sh 'docker --version'
                    sh 'docker ps'
                    // Build the Docker image
                    sh "docker build -t ${DOCKER_IMAGE}:${env.BUILD_ID} -f ${WORKSPACE}/react-flask-app/Dockerfile ${WORKSPACE}/react-flask-app"
                }
            }
        }

        stage('Deploy Docker Image') {
            steps {
                script {
                    sh """
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true
                        docker run -d -p 80:80 --name ${CONTAINER_NAME} ${DOCKER_IMAGE}:${env.BUILD_ID}
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
