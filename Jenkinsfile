pipeline {
    agent any

    environment {
        VENV_PATH = '/var/lib/jenkins/workspace/ICT2216/venv'
        DOCKER_IMAGE = 'nginx'
        CONTAINER_NAME = 'nginx-container'
    }

    stages {
        stage('Checkout') {
            steps {
                git url: 'https://github.com/sweeboon/ICT2216-SSD-Group-22.git', branch: 'main', credentialsId: '92db66e9-d356-45db-af30-b8897191973c'
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    // Create the virtual environment if it doesn't exist
                    sh "python3 -m venv ${VENV_PATH}"
                }
            }
        }

        stage('Install Python Dependencies') {
            steps {
                // Install any dependencies listed in requirements.txt
                sh "bash -c 'source ${VENV_PATH}/bin/activate && pip install -r /var/lib/jenkins/workspace/ICT2216/react-flask-app/server/requirements.txt'"
            }
        }

        stage('Install Node.js Dependencies') {
            steps {
                // Install Node.js dependencies
                sh 'bash -c "cd /var/lib/jenkins/workspace/ICT2216/react-flask-app/src && yarn install"'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image
                    sh "docker build -t ${DOCKER_IMAGE}:${env.BUILD_ID} -f /var/lib/jenkins/workspace/ICT2216/react-flask-app/Dockerfile /var/lib/jenkins/workspace/ICT2216/react-flask-app"
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
