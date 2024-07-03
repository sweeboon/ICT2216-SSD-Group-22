pipeline {
    agent any

    environment {
        VENV_PATH = "react-flask-app/server/venv"
        DOCKER_IMAGE = 'nginx'
        CONTAINER_NAME = 'nginx'
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
                    // Read the .env file and pass the variables as build arguments
                    def envVars = readFile('/var/jenkins_home/.env').split('\n').collect { line -> 
                        return "--build-arg ${line.replace('=', '="')}\"" 
                    }.join(' ')
                    
                    // Verify Docker is accessible
                    sh 'docker --version'
                    sh 'docker ps'
                    
                    // Build the Docker image
                    sh "docker build ${envVars} -t ${DOCKER_IMAGE}:${env.BUILD_ID} -f ${WORKSPACE}/react-flask-app/Dockerfile ${WORKSPACE}/react-flask-app"
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
