pipeline {
    agent any

    environment {
        VENV_PATH = "react-flask-app/server/venv"
        WORKSPACE_DIR = "${env.WORKSPACE}"
        DOCKER_IMAGE = 'nginx'
        CONTAINER_NAME = 'nginx'
    }

    stages {
        stage('Clean Workspace') {
            steps {
                script {
                    // Clean the workspace directory
                    sh 'rm -rf ${WORKSPACE_DIR}/*'
                }
            }
        }

        stage('Checkout') {
            steps {
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    // Ensure the directory for virtual environment exists
                    sh 'mkdir -p ${WORKSPACE_DIR}/${VENV_PATH}'
                    // Create the virtual environment
                    sh 'bash -c "python3 -m venv ${WORKSPACE_DIR}/${VENV_PATH}"'
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                script {
                    // Install any dependencies listed in requirements.txt
                    sh 'bash -c "source ${WORKSPACE_DIR}/${VENV_PATH}/bin/activate && pip install -r ${WORKSPACE_DIR}/react-flask-app/server/requirements.txt"'
                }
            }
        }

        stage('Install Node.js Dependencies') {
            steps {
                script {
                    // Install Node.js dependencies
                    sh 'bash -c "cd ${WORKSPACE_DIR}/react-flask-app/src && yarn install"'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh "docker build -t ${DOCKER_IMAGE}:${env.BUILD_ID} -f ${WORKSPACE_DIR}/react-flask-app/Dockerfile ${WORKSPACE_DIR}/react-flask-app"
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
